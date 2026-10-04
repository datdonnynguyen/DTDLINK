"""Stage 6: reproducible, offline clustering within dangerous TRAIN URLs.

Labels select the population; only documented numeric URL features enter
StandardScaler, KMeans, silhouette and PCA. Source types are inspected AFTER
selection, solely as a source-composition check.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.metrics import adjusted_rand_score, silhouette_score
from sklearn.preprocessing import StandardScaler
from threadpoolctl import threadpool_limits

from dtdlink_ml.feature_extraction import FEATURE_NAMES, file_sha256
from dtdlink_ml.train_classifier import (
    FEATURE_INPUT, SPLIT_MANIFEST, FEATURE_SHA256, MANIFEST_SHA256,
    PROJECT_ROOT, _url_id, validate_manifest,
)

# Adjustable settings. Changing them requires rerunning and reviewing the report.
SELECTED_TARGET = 1
K_VALUES = tuple(range(2, 9))
RANDOM_SEED = 42
N_INIT = 10
SILHOUETTE_SAMPLE_SIZE = 2000
PCA_SAMPLE_SIZE = 10000
REPRESENTATIVES_PER_CLUSTER = 3
REPORT_DIR = PROJECT_ROOT / "reports/clustering"
FIGURE_DIR = PROJECT_ROOT / "reports/figures"


def select_population(chunk, membership, target=SELECTED_TARGET):
    """Check identity, discard other splits, then filter the one true class."""
    if len(chunk) != len(membership):
        raise ValueError("Feature/manifest row counts differ.")
    if not np.array_equal(chunk["url"].map(_url_id).to_numpy(), membership["url_id"].to_numpy()):
        raise ValueError("Feature rows no longer align with locked manifest.")
    train = chunk.loc[membership["split"].eq("train").to_numpy()].copy()
    if not train["target"].isin([0, 1]).all():
        raise ValueError("Invalid training target.")
    train["url_id"] = membership.loc[membership["split"].eq("train"), "url_id"].to_numpy()
    train["group_key"] = membership.loc[membership["split"].eq("train"), "group_key"].to_numpy()
    return train.loc[train["target"].eq(target)].copy()


def load_population(feature_path=FEATURE_INPUT, manifest_path=SPLIT_MANIFEST,
                    expected_feature_hash=FEATURE_SHA256, expected_manifest_hash=MANIFEST_SHA256):
    if file_sha256(feature_path) != expected_feature_hash:
        raise ValueError("Locked feature hash changed.")
    if file_sha256(manifest_path) != expected_manifest_hash:
        raise ValueError("Locked manifest hash changed.")
    manifest = pd.read_csv(manifest_path, dtype="string", keep_default_na=False)
    counts = validate_manifest(manifest)
    retained, offset = [], 0
    for chunk in pd.read_csv(feature_path, usecols=["url", "type", "target", *FEATURE_NAMES],
                             keep_default_na=False, chunksize=50000):
        retained.append(select_population(chunk, manifest.iloc[offset:offset + len(chunk)]))
        offset += len(chunk)
    if offset != len(manifest):
        raise ValueError("Feature/manifest row counts differ.")
    frame = pd.concat(retained, ignore_index=True)
    if frame.empty or frame["url_id"].duplicated().any():
        raise ValueError("Empty population or duplicated IDs.")
    return frame, counts


def prepare_features(frame):
    """Whitelist inputs and remove only population-constant columns."""
    numeric = frame.loc[:, list(FEATURE_NAMES)].astype(float)
    if not np.isfinite(numeric.to_numpy()).all() or (numeric.to_numpy() < 0).any():
        raise ValueError("Features must be finite and nonnegative.")
    removed = numeric.columns[numeric.nunique().eq(1)].tolist()
    features = numeric.drop(columns=removed)
    if features.empty:
        raise ValueError("No varying numeric features.")
    scaler = StandardScaler()
    scaled = scaler.fit_transform(features)
    return features, scaled, scaler, removed


def make_kmeans(k, seed=RANDOM_SEED):
    return KMeans(n_clusters=k, n_init=N_INIT, random_state=seed,
                  max_iter=300, algorithm="lloyd")


def fit_checked(scaled, k, seed=RANDOM_SEED):
    """Verify BLAS results independently: macOS Accelerate may set stale FP flags.

    Suppress only floating-point status warnings around the library operation;
    reject nonfinite results and reconcile inertia with non-BLAS arithmetic.
    """
    with np.errstate(over="ignore", divide="ignore", invalid="ignore"):
        model = make_kmeans(k, seed).fit(scaled)
    residual = scaled - model.cluster_centers_[model.labels_]
    independent_inertia = float(np.einsum("ij,ij->", residual, residual, optimize=False))
    if (not np.isfinite(model.cluster_centers_).all()
            or not np.isfinite(model.inertia_)
            or not np.isclose(model.inertia_, independent_inertia, rtol=1e-9, atol=1e-6)):
        raise ValueError("K-means numerical result failed independent inertia check.")
    return model


def compare_k(scaled, ks=K_VALUES, sample_size=SILHOUETTE_SAMPLE_SIZE):
    """Use the SAME fixed sample for each k; fit each model on all selected rows."""
    sample = np.sort(np.random.default_rng(RANDOM_SEED).choice(
        len(scaled), min(sample_size, len(scaled)), replace=False))
    rows, models = [], {}
    for k in ks:
        model = fit_checked(scaled, k)
        labels = model.labels_
        sampled_labels = labels[sample]
        valid = 1 < len(np.unique(sampled_labels)) < len(sample)
        with np.errstate(over="ignore", divide="ignore", invalid="ignore"):
            silhouette = float(silhouette_score(scaled[sample], sampled_labels)) if valid else None
        if valid and (not np.isfinite(silhouette) or not -1 <= silhouette <= 1):
            raise ValueError("Invalid silhouette result.")
        sizes = np.bincount(labels, minlength=k)
        rows.append(dict(k=k, inertia=float(model.inertia_), silhouette=silhouette,
                         min_cluster_size=int(sizes.min()), max_cluster_size=int(sizes.max()),
                         iterations=int(model.n_iter_), sample_size=len(sample),
                         sampled_cluster_count=len(np.unique(sampled_labels))))
        models[k] = model
        print(f"k={k}: inertia={model.inertia_:.2f}, silhouette={silhouette}, sizes={sizes.tolist()}", flush=True)
    return pd.DataFrame(rows), models, sample


def choose_k(comparison):
    """Transparent label-free baseline rule; cluster profiles must still be reviewed."""
    valid = comparison.dropna(subset=["silhouette"])
    if valid.empty:
        raise ValueError("No valid silhouette comparison.")
    return int(valid.sort_values(["silhouette", "k"], ascending=[False, True]).iloc[0]["k"])


def build_profiles(frame, features, scaled, model):
    labels = model.labels_
    overall_mean, overall_std = features.mean(), features.std(ddof=0)
    profiles, examples, composition = [], [], []
    for cluster in range(model.n_clusters):
        indices = np.flatnonzero(labels == cluster)
        group = features.iloc[indices]
        for name in features.columns:
            profiles.append(dict(cluster=cluster, size=len(indices), feature=name,
                overall_mean=float(overall_mean[name]), cluster_mean=float(group[name].mean()),
                cluster_median=float(group[name].median()),
                difference_in_std=float((group[name].mean() - overall_mean[name]) / overall_std[name])))
        distances = np.linalg.norm(scaled[indices] - model.cluster_centers_[cluster], axis=1)
        nearest = np.argsort(distances, kind="stable")[:REPRESENTATIVES_PER_CLUSTER]
        for rank, local in enumerate(nearest, 1):
            row = frame.iloc[indices[local]]
            examples.append(dict(cluster=cluster, rank=rank, url_id=row["url_id"],
                                 url=row["url"], distance_to_center=float(distances[local])))
        # Source labels are read only here, after clustering and k selection.
        for source, count in frame.iloc[indices]["type"].value_counts().sort_index().items():
            composition.append(dict(cluster=cluster, source_type=source, count=int(count),
                                    proportion=float(count / len(indices))))
    return pd.DataFrame(profiles), pd.DataFrame(examples), pd.DataFrame(composition)


def save_figures(comparison, profiles, scaled, model, directory=FIGURE_DIR):
    directory.mkdir(parents=True, exist_ok=True)
    fig, axes = plt.subplots(1, 2, figsize=(10, 4))
    axes[0].plot(comparison.k, comparison.inertia, "o-")
    axes[0].set(xlabel="Number of clusters (k)", ylabel="Inertia (sum of squared distances)")
    axes[1].plot(comparison.k, comparison.silhouette, "o-")
    axes[1].set(xlabel="Number of clusters (k)", ylabel="Silhouette (fixed 2,000-row sample)")
    fig.tight_layout(); fig.savefig(directory / "clustering_k_selection.png", dpi=160); plt.close(fig)

    # Include signals from EVERY cluster; rare large z-scores otherwise hide
    # ordinary cluster differences. Color saturates at +/-3; annotations stay exact.
    top = list(dict.fromkeys(name for _, group in profiles.groupby("cluster")
                            for name in group.loc[group.difference_in_std.abs().nlargest(3).index, "feature"]))
    matrix = profiles.pivot(index="feature", columns="cluster", values="difference_in_std").loc[top]
    fig, ax = plt.subplots(figsize=(10, 8))
    limit = 3
    image = ax.imshow(matrix, cmap="coolwarm", vmin=-limit, vmax=limit, aspect="auto")
    ax.set_yticks(range(len(top)), top); ax.set_xticks(range(model.n_clusters), [f"Cluster {i}" for i in range(model.n_clusters)])
    for row in range(len(top)):
        for column in range(model.n_clusters):
            value = float(matrix.iloc[row, column])
            ax.text(column, row, f"{value:+.1f}", ha="center", va="center", fontsize=8,
                    color="white" if abs(value) >= 2 else "black")
    ax.set_title("Feature differences: numbers are SD; colors saturate at +/-3")
    fig.colorbar(image, ax=ax, label="Difference in population SD (color clipped)", extend="both")
    fig.tight_layout(); fig.savefig(directory / "clustering_profiles.png", dpi=160); plt.close(fig)

    pca = PCA(n_components=2, svd_solver="full").fit(scaled)
    sample = np.sort(np.random.default_rng(RANDOM_SEED).choice(len(scaled), min(PCA_SAMPLE_SIZE, len(scaled)), replace=False))
    projection = np.einsum("ij,kj->ik", scaled[sample] - pca.mean_, pca.components_, optimize=False)
    if not np.isfinite(projection).all():
        raise ValueError("Nonfinite PCA projection.")
    fig, ax = plt.subplots(figsize=(8, 5))
    for cluster in range(model.n_clusters):
        mask = model.labels_[sample] == cluster
        ax.scatter(projection[mask, 0], projection[mask, 1], s=5, alpha=.4, label=f"Cluster {cluster}")
    ax.set(xlabel=f"PC1 ({pca.explained_variance_ratio_[0]:.1%} variance)",
           ylabel=f"PC2 ({pca.explained_variance_ratio_[1]:.1%} variance)", title="PCA view: sampled training URLs only")
    ax.legend(markerscale=3); fig.tight_layout()
    fig.savefig(directory / "clustering_pca.png", dpi=160); plt.close(fig)
    return pca.explained_variance_ratio_.tolist()


def describe_cluster(group):
    """Translate observed means to cautious domain language, never attack labels."""
    values = group.set_index("feature").cluster_mean
    if values.get("has_control_character", 0) > .5:
        return "Nhóm văn bản bất thường: nhiều ký tự điều khiển/Unicode và lỗi parser. Có thể phản ánh dữ liệu hỏng hoặc cách mã hóa nguồn; không suy ra một loại tấn công."
    if values.get("has_nonstandard_port", 0) > .5:
        return "Nhóm host chủ yếu dạng IP với port không chuẩn; cần phân biệt cấu trúc địa chỉ với kết luận về hành vi máy chủ."
    if values.get("has_ip_host", 0) > .5:
        return "Nhóm host dạng IP, không có tên miền/TLD quen thuộc; ví dụ chỉ minh họa hình thức URL, không xác minh hoạt động đích."
    if values.get("has_suspicious_term", 0) > .5:
        return "Nhóm có từ khóa như login/signin/verify và tín hiệu thương hiệu ở nhiều vị trí; phù hợp để khảo sát cấu trúc dễ gây nhầm lẫn."
    if values.get("query_parameter_count", 0) > 3:
        return "Nhóm URL dài với nhiều tham số query, có thể gồm cấu trúc CMS lặp lại. Đây là mẫu hình văn bản, không đủ để xác nhận phishing."
    if values.get("has_scheme", 1) < .1:
        return "Nhóm URL ngắn, không ghi scheme; parse_issue_count thường phản ánh missing_scheme có thể phục hồi, không đồng nghĩa parser thất bại. Có thể bị chi phối bởi định dạng nguồn."
    return "Nhóm URL có scheme, đường dẫn tương đối nhiều đoạn và ít query hơn; đặc điểm cấu trúc khá phổ biến, không phải bằng chứng an toàn hoặc nguy hiểm riêng lẻ."


def write_report(summary, comparison, profiles, representatives):
    lines = ["# Stage 6 — Phân cụm URL trong một class", "",
        f"Dữ liệu thật: **{summary['selected_rows']:,} URL potentially_dangerous trong train**; không dùng validation/test.",
        f"Đầu vào: 36 features; loại {len(summary['removed_constant_features'])} features hằng số; còn {len(summary['feature_names'])} features.",
        "Nhãn chỉ lọc class; type/target/URL/domain không vào scaling, K-means, silhouette hoặc PCA.", "",
        "## Phương pháp và chọn k", "",
        "StandardScaler fit trên toàn tập đã chọn. Giữ features không hằng số, kể cả tương quan, để baseline minh bạch; chưa thêm biến đổi hoặc trọng số tùy ý.",
        f"K-means: n_init={N_INIT}, seed={RANDOM_SEED}; thử k=2–8 trên toàn tập. Silhouette dùng cùng mẫu ngẫu nhiên {summary['silhouette_sample_size']:,} dòng cho mọi k.",
        "Quy tắc baseline: chọn silhouette mẫu cao nhất; hòa chọn k nhỏ hơn. Không dùng type để chọn k.",
        f"Kết quả: **k={summary['selected_k']}**, silhouette={summary['selected_silhouette']:.4f}.", "",
        "| k | Inertia | Silhouette | Nhóm nhỏ nhất | Nhóm lớn nhất |", "|---|---:|---:|---:|---:|"]
    for row in comparison.itertuples():
        lines.append(f"| {row.k} | {row.inertia:.1f} | {row.silhouette:.4f} | {row.min_cluster_size} | {row.max_cluster_size} |")
    lines += ["", "## Hồ sơ từng cluster", "",
              "Giá trị trung bình/tỷ lệ đọc trên thang đo gốc; chênh lệch chuẩn hóa so với TOÀN class đã chọn. Cluster ID không là cấp độ nguy hiểm."]
    for cluster, group in profiles.groupby("cluster"):
        top = group.loc[group.difference_in_std.abs().nlargest(5).index]
        size = int(group.iloc[0]['size'])
        lines += ["", f"### Cluster {cluster} — {size:,} URL ({size / summary['selected_rows']:.2%})", "",
                  describe_cluster(group), "",
                  "| Feature | Trung bình nhóm | Trung bình class | Chênh lệch / SD |", "|---|---:|---:|---:|"]
        for row in top.itertuples():
            lines.append(f"| {row.feature} | {row.cluster_mean:.4f} | {row.overall_mean:.4f} | {row.difference_in_std:+.2f} |")
        higher = top.loc[top.difference_in_std > 0, "feature"].tolist()
        lower = top.loc[top.difference_in_std < 0, "feature"].tolist()
        lines += ["", "Diễn giải cấu trúc: " + ("cao hơn mức chung ở " + ", ".join(higher) if higher else "không nổi bật theo chiều tăng trong top features")
                  + ("; thấp hơn ở " + ", ".join(lower) if lower else "") + ". Đây là kiểu đặc điểm URL, không phải một loại tấn công được xác nhận.",
                  "", "URL thật gần tâm nhất (văn bản, không truy cập):", "", "```text"]
        lines += [json.dumps(url, ensure_ascii=True) for url in representatives.loc[representatives.cluster.eq(cluster), "url"]]
        lines += ["```"]
    lines += ["", "## Độ ổn định và hạn chế", "",
        f"ARI giữa lần chạy seed 42 và seed 43/44: {summary['stability_ari']}. ARI đo đồng thuận phân nhóm, không phải accuracy phát hiện URL.",
        "Kết quả thay đổi khi đổi seed; không khẳng định cấu trúc nhóm là duy nhất hoặc ổn định hoàn toàn. Kết quả chính dùng seed 42 cố định để tái lập.",
        f"Số điểm trong mẫu silhouette theo cluster cuối: {summary['silhouette_sample_cluster_sizes']}. Nhóm hiếm có thể không có trong mẫu, nên điểm mẫu không đại diện tốt cho nhóm đó.",
        "URL ví dụ được hiển thị dưới dạng chuỗi JSON đã escape; CSV giữ nguyên văn bản gốc để truy vết ký tự điều khiển.",
        "- Silhouette là ước lượng trên mẫu, không phải toàn dữ liệu; lựa chọn k có thể nhạy với mẫu và thang đo.",
        "- StandardScaler có thể khuếch đại tín hiệu boolean hiếm; outliers và features tương quan có thể chi phối khoảng cách.",
        "- Nhiều URL cùng domain tạo trọng số lớn cho domain đó; không mặc định clusters là các chiến dịch độc lập.",
        "- Scheme/encoding có thể phản ánh định dạng nguồn; bảng source_type_composition chỉ là kiểm tra sau phân cụm.",
        "- PCA chỉ là hình chiếu; xem tỷ lệ phương sai giải thích trong JSON. Điểm gần nhau trên hình chưa chắc gần nhau trong mọi features.",
        "- K-means luôn gán nhóm, kể cả URL bất thường. Không đánh giá độ nguy hiểm bằng cluster ID; không tạo classifier mới.",
        "- DBSCAN là tùy chọn và chưa chạy. Đây là phân tích trong class dangerous của train, không phải đánh giá tổng quát trên test.",
        "", "## Giá trị cho DTDLINK", "",
        "Profiles và URL ví dụ giúp giải thích sự đa dạng của tín hiệu URL, cung cấp bằng chứng cho báo cáo/Insights. Không thay đổi Random Forest hoặc threshold 0.5.",
        "", "## Kiểm tra", "",
        "Tổng kích thước nhóm bằng số URL đầu vào; ID duy nhất; nhãn không vào ma trận; hashes dữ liệu/split không đổi. Test set giữ cho Stage 7."]
    (REPORT_DIR / "stage-6-clustering-report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def run():
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    frame, counts = load_population()
    features, scaled, scaler, removed = prepare_features(frame)
    print(f"Selected {len(frame):,} train URLs; {len(features.columns)} features; removed {removed}", flush=True)
    with threadpool_limits(limits=2):
        comparison, models, sample = compare_k(scaled)
        k = choose_k(comparison)
        model = models[k]
        stability = {str(seed): float(adjusted_rand_score(model.labels_, fit_checked(scaled, k, seed).labels_))
                     for seed in (43, 44)}
        profiles, representatives, composition = build_profiles(frame, features, scaled, model)
        pca_variance = save_figures(comparison, profiles, scaled, model)
    assignments = frame[["url_id", "group_key"]].copy()
    assignments["cluster"] = model.labels_
    domain_concentration = {}
    for cluster, rows in assignments.groupby("cluster"):
        groups = rows.group_key.value_counts()
        domain_concentration[str(cluster)] = dict(unique_groups=len(groups), largest_group=str(groups.index[0]),
                                                  largest_group_rows=int(groups.iloc[0]), largest_group_share=float(groups.iloc[0] / len(rows)))
    assert len(assignments) == len(frame) and assignments.url_id.is_unique
    assert int(profiles.groupby("cluster").size().count()) == k
    assert int(profiles.groupby("cluster")["size"].first().sum()) == len(frame)
    correlation = features.corr()
    pairs = [{"a": a, "b": b, "correlation": float(correlation.loc[a, b])}
             for i, a in enumerate(features.columns) for b in features.columns[i+1:]
             if abs(correlation.loc[a, b]) >= .85]
    summary = dict(feature_sha256=FEATURE_SHA256, manifest_sha256=MANIFEST_SHA256,
        selected_class="potentially_dangerous", selected_target=SELECTED_TARGET, fit_split="train",
        selected_rows=len(frame), split_counts=counts, feature_names=features.columns.tolist(),
        removed_constant_features=removed, high_correlation_pairs=pairs,
        scaler="StandardScaler fit on selected-class train rows only", scaler_mean=scaler.mean_.tolist(),
        scaler_scale=scaler.scale_.tolist(), random_seed=RANDOM_SEED, n_init=N_INIT,
        k_values=list(K_VALUES), selected_k=k,
        selection_rule="maximum fixed-sample silhouette; tie chooses smaller k; no source labels",
        selected_silhouette=float(comparison.loc[comparison.k.eq(k), "silhouette"].iloc[0]),
        silhouette_sample_size=len(sample), silhouette_sample_index_sha256=hashlib.sha256(sample.tobytes()).hexdigest(),
        silhouette_sample_cluster_sizes={str(i): int((model.labels_[sample] == i).sum()) for i in range(k)},
        independent_inertia_checks_passed=True,
        stability_ari=stability, pca_explained_variance_ratio=pca_variance,
        cluster_sizes={str(i): int((model.labels_ == i).sum()) for i in range(k)},
        cluster_domain_concentration=domain_concentration,
        labels_used_as_features=False, validation_used=False, test_used_for_modelling_or_metrics=False,
        dbscan_run=False, max_iterations_reached=bool((comparison.iterations >= 300).any()))
    for name, table in [("k_comparison.csv", comparison), ("cluster_assignments.csv", assignments),
                        ("cluster_profiles.csv", profiles), ("representative_urls.csv", representatives),
                        ("source_type_composition.csv", composition)]:
        table.to_csv(REPORT_DIR / name, index=False)
    if file_sha256(FEATURE_INPUT) != FEATURE_SHA256 or file_sha256(SPLIT_MANIFEST) != MANIFEST_SHA256:
        raise ValueError("Input changed during clustering.")
    (REPORT_DIR / "clustering_summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    write_report(summary, comparison, profiles, representatives)
    print(json.dumps({key: summary[key] for key in ("selected_rows", "selected_k", "selected_silhouette", "cluster_sizes", "stability_ari")}, indent=2), flush=True)
    return summary


if __name__ == "__main__":
    run()
