"""Cluster dangerous training URLs using their numeric features."""

import json
from itertools import combinations

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.metrics import adjusted_rand_score, silhouette_score
from sklearn.preprocessing import StandardScaler
from threadpoolctl import threadpool_limits

from dtdlink_ml.feature_extraction import FEATURE_NAMES
from dtdlink_ml.train_classifier import (FEATURE_INPUT, FEATURE_SHA256, MANIFEST_SHA256, ROOT, SPLIT_MANIFEST,
                                         load_splits, select_allowed_rows)

SELECTED_TARGET = 1
K_VALUES = tuple(range(2, 9))
RANDOM_SEED = 42
N_INIT = 10
SILHOUETTE_SAMPLE_SIZE = 2000
REPRESENTATIVES_PER_CLUSTER = 3
REPORT_DIR = ROOT / "reports/clustering"
FIGURE_DIR = ROOT / "reports/figures"


def select_population(chunk, manifest_part, target=SELECTED_TARGET):
    """From one chunk, keep the train rows of the chosen class."""
    train = select_allowed_rows(chunk, manifest_part, ("train",))["train"]
    return train[train["target"] == target].copy()


def load_population(feature_path=FEATURE_INPUT, manifest_path=SPLIT_MANIFEST,
                    feature_hash=FEATURE_SHA256, manifest_hash=MANIFEST_SHA256):
    """Load the dangerous URLs of the train split (the rows we cluster)."""
    data, counts = load_splits(("train",), feature_path, manifest_path, feature_hash, manifest_hash)
    train = data["train"]
    df = train[train["target"] == SELECTED_TARGET].reset_index(drop=True)
    if len(df) == 0:
        raise ValueError("The selected class has no training rows.")
    return df, counts


def prepare_features(df):
    """Take the feature columns, drop constant ones and scale the rest."""
    X = df.loc[:, list(FEATURE_NAMES)].astype(float)
    if not np.isfinite(X.to_numpy()).all():
        raise ValueError("Features must be finite numbers.")
    removed = [col for col in X.columns if X[col].nunique() == 1]
    X = X.drop(columns=removed)
    if X.empty:
        raise ValueError("No varying numeric features.")
    scaler = StandardScaler()
    scaled = scaler.fit_transform(X)
    return X, scaled, scaler, removed


def make_kmeans(k, seed=RANDOM_SEED):
    return KMeans(n_clusters=k, n_init=N_INIT, random_state=seed, max_iter=300, algorithm="lloyd")


def fit_kmeans(scaled, k, seed=RANDOM_SEED):
    with np.errstate(over="ignore", divide="ignore", invalid="ignore"):
        return make_kmeans(k, seed).fit(scaled)


def random_sample(n, size):
    """Fixed random sample of row indexes (same seed every time)."""
    rng = np.random.default_rng(RANDOM_SEED)
    return np.sort(rng.choice(n, min(size, n), replace=False))


def compare_k(scaled, ks=K_VALUES, sample_size=SILHOUETTE_SAMPLE_SIZE):
    """Try each k and record inertia and silhouette (on a fixed sample, since the full data is too big)."""
    sample = random_sample(len(scaled), sample_size)
    rows = []
    models = {}
    for k in ks:
        km = fit_kmeans(scaled, k)
        labels = km.labels_[sample]
        n_found = len(np.unique(labels))
        sil = None
        if 1 < n_found < len(sample):
            with np.errstate(over="ignore", divide="ignore", invalid="ignore"):
                sil = float(silhouette_score(scaled[sample], labels))
        sizes = np.bincount(km.labels_, minlength=k)
        rows.append({
            "k": k,
            "inertia": float(km.inertia_),
            "silhouette": sil,
            "min_cluster_size": int(sizes.min()),
            "max_cluster_size": int(sizes.max()),
            "iterations": int(km.n_iter_),
        })
        models[k] = km
        print(f"k={k}: inertia={km.inertia_:.2f}, silhouette={sil}, sizes={sizes.tolist()}", flush=True)
    return pd.DataFrame(rows), models, sample


def choose_k(table):
    """Pick the k with the best silhouette (smaller k if tied)."""
    valid = table.dropna(subset=["silhouette"])
    if len(valid) == 0:
        raise ValueError("No valid silhouette score to choose k from.")
    valid = valid.sort_values(["silhouette", "k"], ascending=[False, True])
    return int(valid.iloc[0]["k"])


def build_profiles(df, X, scaled, km):
    """Describe each cluster: feature means, closest example URLs and label mix."""
    mean_all = X.mean()
    std_all = X.std(ddof=0)
    profiles = []
    examples = []
    composition = []
    for cluster_id in range(km.n_clusters):
        idx = np.flatnonzero(km.labels_ == cluster_id)
        members = X.iloc[idx]
        for col in X.columns:
            mean = float(members[col].mean())
            profiles.append({
                "cluster": cluster_id,
                "size": len(idx),
                "feature": col,
                "overall_mean": float(mean_all[col]),
                "cluster_mean": mean,
                "cluster_median": float(members[col].median()),
                "difference_in_std": float((mean - mean_all[col]) / std_all[col]),
            })

        distances = np.linalg.norm(scaled[idx] - km.cluster_centers_[cluster_id], axis=1)
        nearest = np.argsort(distances, kind="stable")[:REPRESENTATIVES_PER_CLUSTER]
        for rank, i in enumerate(nearest, start=1):
            row = df.iloc[idx[i]]
            examples.append({"cluster": cluster_id, "rank": rank, "url_id": row["url_id"], "url": row["url"],
                             "distance_to_center": float(distances[i])})

        # source labels are only looked at after clustering
        for source, count in df.iloc[idx]["type"].value_counts().sort_index().items():
            composition.append({"cluster": cluster_id, "source_type": source, "count": int(count),
                        "proportion": float(count / len(idx))})
    return pd.DataFrame(profiles), pd.DataFrame(examples), pd.DataFrame(composition)


def save_figures(table, profiles, km, folder=FIGURE_DIR):
    folder.mkdir(parents=True, exist_ok=True)
    n = km.n_clusters

    fig, axes = plt.subplots(1, 2, figsize=(10, 4))
    axes[0].plot(table.k, table.inertia, "o-")
    axes[0].set(xlabel="Number of clusters (k)", ylabel="Inertia (sum of squared distances)")
    axes[1].plot(table.k, table.silhouette, "o-")
    axes[1].set(xlabel="Number of clusters (k)", ylabel="Silhouette (2,000-row sample)")
    fig.tight_layout()
    fig.savefig(folder / "clustering_k_selection.png", dpi=160)
    plt.close(fig)

    # top 3 features of each cluster, so small clusters also show up
    top = []
    for _, group in profiles.groupby("cluster"):
        biggest = group["difference_in_std"].abs().nlargest(3).index
        for col in group.loc[biggest, "feature"]:
            if col not in top:
                top.append(col)
    matrix = profiles.pivot(index="feature", columns="cluster", values="difference_in_std").loc[top]
    fig, ax = plt.subplots(figsize=(10, 8))
    img = ax.imshow(matrix, cmap="coolwarm", vmin=-3, vmax=3, aspect="auto")
    ax.set_yticks(range(len(top)), top)
    ax.set_xticks(range(n), [f"Cluster {i}" for i in range(n)])
    for r in range(len(top)):
        for c in range(n):
            value = float(matrix.iloc[r, c])
            color = "white" if abs(value) >= 2 else "black"
            ax.text(c, r, f"{value:+.1f}", ha="center", va="center", fontsize=8, color=color)
    ax.set_title("Cluster mean minus overall mean, in standard deviations")
    fig.colorbar(img, ax=ax, label="Difference in SD (colour capped at +/-3)", extend="both")
    fig.tight_layout()
    fig.savefig(folder / "clustering_profiles.png", dpi=160)
    plt.close(fig)


def describe_cluster(g):
    """Describe the first matching feature pattern; these are not confirmed attack types."""
    means = g.set_index("feature").cluster_mean
    if means.get("has_control_character", 0) > .5:
        return "More than half of the URLs contain control characters."
    if means.get("has_nonstandard_port", 0) > .5:
        return "More than half of the URLs use non-standard ports."
    if means.get("has_ip_host", 0) > .5:
        return "More than half of the URLs have IP-address hosts."
    if means.get("has_suspicious_term", 0) > .5:
        return "More than half of the URLs contain terms from the suspicious-word list, such as login or verify."
    if means.get("query_parameter_count", 0) > 3:
        return "URLs have more than three query parameters on average."
    if means.get("has_scheme", 1) < .1:
        return "Fewer than 10% of the URLs have an explicit scheme."
    return "No summary rule matched; use the feature means below to interpret this cluster."


def write_report(summary, table, profiles, examples):
    lines = [
        "# Stage 6 - Clustering the dangerous URLs", "",
        f"Data: {summary['selected_rows']:,} potentially dangerous URLs from the train split.",
        f"{len(summary['removed_constant_features'])} constant features removed, "
        f"{len(summary['feature_names'])} features used. Labels, URL text and domain are not used as features.", "",
        "## Choosing k", "",
        f"Features scaled with StandardScaler. K-means with n_init={N_INIT} and seed={RANDOM_SEED}, "
        f"k from 2 to 8. Silhouette is computed on the same random sample of "
        f"{summary['silhouette_sample_size']:,} rows for every k, and the k with the highest silhouette is used.",
        f"Chosen: **k={summary['selected_k']}**, silhouette={summary['selected_silhouette']:.4f}.", "",
        "| k | Inertia | Silhouette | Smallest cluster | Largest cluster |", "|---|---:|---:|---:|---:|",
    ]
    for row in table.itertuples():
        lines.append(f"| {row.k} | {row.inertia:.1f} | {row.silhouette:.4f} | {row.min_cluster_size} | {row.max_cluster_size} |")
    lines += ["", "## Clusters", "",
              "Differences are in standard deviations from the mean of all selected URLs."]

    for cluster_id, group in profiles.groupby("cluster"):
        top = group.loc[group.difference_in_std.abs().nlargest(5).index]
        size = int(group.iloc[0]["size"])
        lines += ["", f"### Cluster {cluster_id} - {size:,} URLs ({size / summary['selected_rows']:.2%})", "",
                  describe_cluster(group), "",
                  "| Feature | Cluster mean | Overall mean | Difference / SD |", "|---|---:|---:|---:|"]
        for row in top.itertuples():
            lines.append(f"| {row.feature} | {row.cluster_mean:.4f} | {row.overall_mean:.4f} | {row.difference_in_std:+.2f} |")
        lines += ["", "URLs closest to the centre:", "", "```text"]
        for url in examples.loc[examples.cluster == cluster_id, "url"]:
            lines.append(json.dumps(url, ensure_ascii=True))
        lines.append("```")

    lines += [
        "", "## Stability and limitations", "",
        f"Adjusted Rand index between seed 42 and seeds 43/44: {summary['stability_ari']}.",
        f"Sample points per cluster in the silhouette sample: {summary['silhouette_sample_cluster_sizes']}. "
        "Very small clusters barely appear in the sample.",
        "- K-means puts every URL in some cluster, even unusual ones.",
        "- Big domains contribute many URLs, so a cluster is not the same as one campaign.",
        "- Only the dangerous URLs of the train split are clustered; the classifier is not changed.",
    ]
    (REPORT_DIR / "stage-6-clustering-report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def run():
    """Run Stage 6 end to end and save all tables, figures, summary and report."""
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    df, counts = load_population()
    X, scaled, scaler, removed = prepare_features(df)
    print(f"Selected {len(df):,} train URLs; {len(X.columns)} features; removed {removed}", flush=True)

    # Limit clustering to two CPU threads.
    with threadpool_limits(limits=2):
        table, models, sample = compare_k(scaled)
        k = choose_k(table)
        km = models[k]
        # same k, other seeds -> how similar are the clusters? (ARI 1 = identical)
        ari = {}
        for seed in (43, 44):
            other = fit_kmeans(scaled, k, seed)
            ari[str(seed)] = float(adjusted_rand_score(km.labels_, other.labels_))
        profiles, examples, composition = build_profiles(df, X, scaled, km)
        save_figures(table, profiles, km)

    assign = df[["url_id", "group_key"]].copy()
    assign["cluster"] = km.labels_
    concentration = {}
    for c, rows in assign.groupby("cluster"):
        groups = rows.group_key.value_counts()
        concentration[str(c)] = {
            "unique_groups": len(groups),
            "largest_group": str(groups.index[0]),
            "largest_group_rows": int(groups.iloc[0]),
            "largest_group_share": float(groups.iloc[0] / len(rows)),
        }

    corr = X.corr()
    pairs = []
    for a, b in combinations(X.columns, 2):
        if abs(corr.loc[a, b]) >= .85:
            pairs.append({"a": a, "b": b, "correlation": float(corr.loc[a, b])})

    summary = {
        "feature_sha256": FEATURE_SHA256,
        "manifest_sha256": MANIFEST_SHA256,
        "selected_target": SELECTED_TARGET,
        "selected_rows": len(df),
        "split_counts": counts,
        "feature_names": X.columns.tolist(),
        "removed_constant_features": removed,
        "high_correlation_pairs": pairs,
        "random_seed": RANDOM_SEED,
        "n_init": N_INIT,
        "k_values": list(K_VALUES),
        "selected_k": k,
        "selected_silhouette": float(table.loc[table.k == k, "silhouette"].iloc[0]),
        "silhouette_sample_size": len(sample),
        "silhouette_sample_cluster_sizes": {str(i): int((km.labels_[sample] == i).sum()) for i in range(k)},
        "stability_ari": ari,
        "cluster_sizes": {str(i): int((km.labels_ == i).sum()) for i in range(k)},
        "cluster_domain_concentration": concentration,
    }
    table.to_csv(REPORT_DIR / "k_comparison.csv", index=False)
    assign.to_csv(REPORT_DIR / "cluster_assignments.csv", index=False)
    profiles.to_csv(REPORT_DIR / "cluster_profiles.csv", index=False)
    examples.to_csv(REPORT_DIR / "representative_urls.csv", index=False)
    composition.to_csv(REPORT_DIR / "source_type_composition.csv", index=False)
    (REPORT_DIR / "clustering_summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    write_report(summary, table, profiles, examples)

    short = {key: summary[key] for key in ["selected_rows", "selected_k", "selected_silhouette",
                                          "cluster_sizes", "stability_ari"]}
    print(json.dumps(short, indent=2), flush=True)
    return summary


if __name__ == "__main__":
    run()
