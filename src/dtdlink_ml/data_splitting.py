"""Split URLs by domain and explore the training rows."""

import json
import math
from collections import Counter
from itertools import combinations
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from sklearn.model_selection import StratifiedGroupKFold

from dtdlink_ml.data_cleaning import count_values
from dtdlink_ml.feature_extraction import FEATURE_NAMES, OUTPUT_COLUMNS, file_sha256, url_id

ROOT = Path(__file__).resolve().parents[2]
FEATURE_INPUT = ROOT / "data/processed/url_features.csv"
SPLIT_MANIFEST = ROOT / "data/processed/split_manifest.csv"
PRE_SPLIT_PROFILE = ROOT / "reports/eda/pre_split_profile.json"
SPLIT_AUDIT = ROOT / "reports/splitting/split_audit.json"
TABLE_DIR = ROOT / "reports/tables"
FIGURE_DIR = ROOT / "reports/figures"

METADATA_COLUMNS = ("url", "type", "target", "registrable_domain", "tld", "parse_issues")
COUNT_FEATURES = FEATURE_NAMES[:17]
BOOLEAN_FEATURES = FEATURE_NAMES[17:]
ALLOWED_TYPES = ["benign", "defacement", "malware", "phishing"]
SPLIT_NAMES = ("train", "validation", "test")
SPLIT_RATIOS = {"train": 0.6, "validation": 0.2, "test": 0.2}
DEFAULT_SEED = 42
N_BASE_FOLDS = 10
CORRELATION_THRESHOLD = 0.85
EDA_SAMPLE_SIZE = 50_000
PROFILE_FEATURES = ["url_length", "host_length", "path_length", "digit_count",
                    "subdomain_count", "query_parameter_count"]
COLORS = {0: "#2563C9", 1: "#B26B00"}
NAMES = {0: "Benign", 1: "Potentially dangerous"}


def to_json(x):
    """Convert NumPy/pandas values for JSON output."""
    if isinstance(x, dict):
        return {str(k): to_json(v) for k, v in x.items()}
    if isinstance(x, (list, tuple)):
        return [to_json(v) for v in x]
    if isinstance(x, np.integer):
        return int(x)
    if isinstance(x, np.floating):
        return float(x) if math.isfinite(x) else None
    if pd.isna(x):
        return None
    return x


def write_json(path, data):
    """Save a dict as a sorted, indented JSON file."""
    path.parent.mkdir(parents=True, exist_ok=True)
    text = json.dumps(to_json(data), indent=2, ensure_ascii=False, sort_keys=True)
    path.write_text(text + "\n", encoding="utf-8")


def save_csv(df, path):
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False, lineterminator="\n")


def load_feature_table(feature_path=FEATURE_INPUT):
    """Load the Stage 3 feature table with fixed column types."""
    dtypes = {col: "string" for col in METADATA_COLUMNS}
    dtypes["target"] = "int8"
    for col in COUNT_FEATURES:
        dtypes[col] = "int32"
    for col in BOOLEAN_FEATURES:
        dtypes[col] = "int8"
    df = pd.read_csv(feature_path, dtype=dtypes)
    if list(df.columns) != list(OUTPUT_COLUMNS):
        raise ValueError(f"Feature table columns are not what Stage 3 writes: {list(df.columns)}")
    return df


def check_feature_table(df):
    """Basic checks before splitting: no missing values, unique URLs, valid labels and features."""
    # registrable_domain/tld can be empty, the other columns can't
    needed = ["url", "type", "target"] + list(FEATURE_NAMES)
    if df[needed].isna().any().any():
        raise ValueError("Feature table has missing values.")
    if df["url"].duplicated().any():
        raise ValueError("Feature table has duplicate URLs.")
    if not df["type"].isin(ALLOWED_TYPES).all() or not df["target"].isin([0, 1]).all():
        raise ValueError("Feature table has unknown labels.")
    if (df.loc[:, FEATURE_NAMES] < 0).any().any():
        raise ValueError("Features must not be negative.")
    for col in BOOLEAN_FEATURES:
        if not df[col].isin([0, 1]).all():
            raise ValueError(f"{col} should only contain 0 or 1.")


def create_group_keys(df):
    """Give every URL a group: its registrable domain, or its own id if it has no domain."""
    ids = df["url"].map(url_id).astype("string")
    domains = df["registrable_domain"].fillna("").str.strip().str.lower()
    keys = ("domain:" + domains).astype("string")
    keys = keys.mask(domains.eq(""), "url:" + ids)
    return ids, keys


def build_domain_profile(df, keys):
    """One row per domain group with its size and label counts."""
    data = pd.DataFrame({
        "group_key": keys,
        "registrable_domain": df["registrable_domain"].fillna(""),
        "target": df["target"].astype("int8"),
        "type": df["type"],
    })
    by_target = pd.crosstab(data["group_key"], data["target"]).reindex(columns=[0, 1], fill_value=0)
    by_type = pd.crosstab(data["group_key"], data["type"]).reindex(columns=ALLOWED_TYPES, fill_value=0)
    profile = data.groupby("group_key", sort=True).agg(registrable_domain=("registrable_domain", "first"),
                                                     row_count=("target", "size"))
    profile = profile.join(by_target).join(by_type).reset_index()
    profile = profile.rename(columns={
        0: "benign_count",
        1: "dangerous_count",
        "benign": "source_benign_count",
        "defacement": "source_defacement_count",
        "malware": "source_malware_count",
        "phishing": "source_phishing_count",
    })
    kind = np.where(profile["group_key"].str.startswith("domain:"), "domain", "url_fallback")
    profile.insert(1, "group_kind", kind)
    profile["dangerous_rate"] = (profile["dangerous_count"] / profile["row_count"]).round(8)
    return profile.sort_values(["row_count", "group_key"], ascending=[False, True], ignore_index=True)


def build_pre_split_profile(df, prof):
    """Summary of the data and the domain groups, saved before the split is made."""
    domains = df["registrable_domain"].fillna("").str.strip()
    no_domain = domains.eq("")
    sizes = prof["row_count"]

    issue_counts = Counter()
    for text in df.loc[no_domain, "parse_issues"].fillna(""):
        for issue in text.split("|"):
            if issue:
                issue_counts[issue] += 1
    top_cols = ["group_key", "group_kind", "row_count", "benign_count", "dangerous_count", "dangerous_rate"]

    return {
        "dataset": {
            "rows": len(df),
            "feature_count": len(FEATURE_NAMES),
            "unique_urls": int(df["url"].nunique()),
            "target_counts": count_values(df["target"]),
            "source_type_counts": count_values(df["type"]),
        },
        "grouping_feasibility": {
            "group_count": len(prof),
            "registrable_domain_count": int(domains[~no_domain].nunique()),
            "rows_without_registrable_domain": int(no_domain.sum()),
            "singleton_groups": int(sizes.eq(1).sum()),
            "repeated_groups": int(sizes.gt(1).sum()),
            "largest_group_rows": int(sizes.max()),
            "group_size_quantiles": {str(q): float(sizes.quantile(q)) for q in (0.5, 0.9, 0.95, 0.99, 1.0)},
            "missing_domain_issue_counts": dict(sorted(issue_counts.items())),
            "missing_domain_target_counts": count_values(df.loc[no_domain, "target"]),
            "top_20_groups": prof.head(20)[top_cols].to_dict(orient="records"),
        },
    }


def build_source_quality_profile(df):
    """For each original label, how often URLs have a scheme, https, an IP host, etc."""
    rows = []
    for source, group in df.groupby("type", sort=True):
        rows.append({
            "source_type": source,
            "rows": len(group),
            "dangerous_rate": float(group["target"].mean()),
            "has_scheme_rate": float(group["has_scheme"].mean()),
            "uses_https_rate": float(group["uses_https"].mean()),
            "parse_ok_rate": float(group["parse_ok"].mean()),
            "unknown_tld_rate": float(group["has_unknown_tld"].mean()),
            "ip_host_rate": float(group["has_ip_host"].mean()),
            "control_character_rate": float(group["has_control_character"].mean()),
        })
    return pd.DataFrame(rows)


def fold_sizes(folds, y):
    """Number of rows and dangerous rows in each of the 10 base folds."""
    sizes = {}
    for fold in range(N_BASE_FOLDS):
        mask = folds == fold
        sizes[fold] = (int(mask.sum()), int(y[mask].sum()))
    return sizes


def choose_fold_allocation(folds, y):
    """Allocate 6/2/2 folds with row ratios and class balance close to the targets."""
    sizes = fold_sizes(folds, y)
    rate = float(y.mean())
    best = None
    best_score = math.inf
    for test in combinations(range(N_BASE_FOLDS), 2):
        rest = [f for f in range(N_BASE_FOLDS) if f not in test]
        for validation in combinations(rest, 2):
            train = tuple(f for f in rest if f not in validation)
            option = {"train": train, "validation": validation, "test": test}
            score = 0.0
            for name, chosen in option.items():
                rows = sum(sizes[f][0] for f in chosen)
                pos = sum(sizes[f][1] for f in chosen)
                # Give row ratios more weight than class balance.
                score += 4.0 * abs(rows / len(y) - SPLIT_RATIOS[name])
                score += abs(pos / rows - rate)
            if score < best_score:
                best = option
                best_score = score
    return best


def assign_grouped_splits(df, keys, seed=DEFAULT_SEED):
    """Split the data into train/validation/test so a domain is only ever in one split."""
    y = df["target"].to_numpy(dtype=np.int8)
    folds = np.full(len(df), -1, dtype=np.int8)
    kfold = StratifiedGroupKFold(n_splits=N_BASE_FOLDS, shuffle=True, random_state=seed)
    dummy = np.zeros((len(df), 1), dtype=np.int8)
    for fold, (_, idx) in enumerate(kfold.split(dummy, y, groups=keys)):
        folds[idx] = fold

    alloc = choose_fold_allocation(folds, y)
    splits = np.full(len(df), "", dtype=object)
    for name, chosen in alloc.items():
        splits[np.isin(folds, chosen)] = name

    method = {
        "algorithm": "StratifiedGroupKFold (10 folds), then whole folds given to each split",
        "seed": seed,
        "selected_folds": {name: list(chosen) for name, chosen in alloc.items()},
    }
    return pd.Series(splits, index=df.index, dtype="string"), method


def validate_split(df, ids, keys, splits):
    """Check that no domain group is in two splits; return row/label counts per split."""
    groups = {name: set(keys[splits.eq(name)]) for name in SPLIT_NAMES}
    overlap = {
        "train_validation": len(groups["train"] & groups["validation"]),
        "train_test": len(groups["train"] & groups["test"]),
        "validation_test": len(groups["validation"] & groups["test"]),
    }
    if sum(overlap.values()) > 0:
        raise ValueError(f"Domain groups appear in more than one split: {overlap}")
    if set(splits) != set(SPLIT_NAMES) or ids.duplicated().any():
        raise ValueError("Every row needs exactly one of train/validation/test and a unique id.")

    details = {}
    for name in SPLIT_NAMES:
        mask = splits.eq(name)
        part = df[mask]
        details[name] = {
            "rows": int(mask.sum()),
            "row_share": float(mask.mean()),
            "groups": int(keys[mask].nunique()),
            "target_counts": count_values(part["target"]),
            "dangerous_rate": float(part["target"].mean()),
            "source_type_counts": count_values(part["type"]),
        }
    return {"pairwise_group_overlap": overlap, "splits": details}


def create_training_tables(train):
    """EDA tables from training rows only: summary, class comparison, correlations."""
    X = train.loc[:, FEATURE_NAMES]
    summary = X.describe(percentiles=[0.25, 0.5, 0.75, 0.95, 0.99]).transpose()
    summary = summary.rename(columns={"count": "non_missing_count", "50%": "median", "25%": "p25",
                                      "75%": "p75", "95%": "p95", "99%": "p99"})
    summary.insert(0, "feature", summary.index)
    summary["missing_count"] = X.isna().sum().to_numpy()
    summary["zero_rate"] = X.eq(0).mean().to_numpy()
    summary["unique_values"] = X.nunique().to_numpy()
    summary = summary.reset_index(drop=True)

    benign = train[train["target"].eq(0)]
    dangerous = train[train["target"].eq(1)]
    rows = []
    for col in FEATURE_NAMES:
        benign_values = benign[col]
        dangerous_values = dangerous[col]
        # pooled standard deviation of the two classes
        variance = ((len(benign) - 1) * benign_values.var() +
                    (len(dangerous) - 1) * dangerous_values.var()) / max(len(benign) + len(dangerous) - 2, 1)
        pooled_sd = math.sqrt(max(float(variance), 0.0))
        difference = float(dangerous_values.mean() - benign_values.mean())
        rows.append({
            "feature": col,
            "benign_mean": float(benign_values.mean()),
            "dangerous_mean": float(dangerous_values.mean()),
            "mean_difference_dangerous_minus_benign": difference,
            "benign_median": float(benign_values.median()),
            "dangerous_median": float(dangerous_values.median()),
            "standardized_mean_difference": difference / pooled_sd if pooled_sd else 0.0,
        })
    comparison = pd.DataFrame(rows)
    comparison["absolute_standardized_mean_difference"] = comparison["standardized_mean_difference"].abs()
    comparison = comparison.sort_values(["absolute_standardized_mean_difference", "feature"],
                                        ascending=[False, True], ignore_index=True)

    rows = []
    for col in BOOLEAN_FEATURES:
        benign_rate = float(benign[col].mean())
        dangerous_rate = float(dangerous[col].mean())
        rows.append({"feature": col, "benign_rate": benign_rate, "dangerous_rate": dangerous_rate,
                     "rate_difference_dangerous_minus_benign": dangerous_rate - benign_rate})
    rates = pd.DataFrame(rows)
    rates["absolute_rate_difference"] = rates["rate_difference_dangerous_minus_benign"].abs()
    rates = rates.sort_values(["absolute_rate_difference", "feature"], ascending=[False, True], ignore_index=True)

    corr = X.corr()
    rows = []
    for feature_a, feature_b in combinations(FEATURE_NAMES, 2):
        correlation = corr.loc[feature_a, feature_b]
        if pd.notna(correlation) and abs(float(correlation)) >= CORRELATION_THRESHOLD:
            rows.append({"feature_a": feature_a, "feature_b": feature_b, "pearson_correlation": float(correlation),
                         "absolute_correlation": abs(float(correlation))})
    pairs = pd.DataFrame(rows, columns=["feature_a", "feature_b", "pearson_correlation", "absolute_correlation"])
    pairs = pairs.sort_values(["absolute_correlation", "feature_a", "feature_b"],
                              ascending=[False, True, True], ignore_index=True)
    return summary, comparison, rates, pairs


def save_fig(path):
    path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(path, dpi=160, bbox_inches="tight", facecolor="white")
    plt.close()


def create_training_figures(train, rates):
    """Draw the three EDA charts from training rows only."""
    sns.set_theme(style="whitegrid", context="notebook")
    paths = {
        "class_balance": FIGURE_DIR / "class_balance_train.png",
        "class_boxplots": FIGURE_DIR / "feature_class_boxplots.png",
        "binary_rates": FIGURE_DIR / "binary_feature_rates.png",
    }

    counts = train["target"].value_counts().reindex([0, 1], fill_value=0)
    plt.figure(figsize=(7.5, 4.8))
    bars = plt.bar([NAMES[0], NAMES[1]], counts.values, color=[COLORS[0], COLORS[1]])
    for bar, count in zip(bars, counts.values):
        plt.text(bar.get_x() + bar.get_width() / 2, count, f"{count:,}\n({count / len(train):.1%})",
                 ha="center", va="bottom")
    plt.ylim(0, float(counts.max()) * 1.14)
    plt.title("Training-set class balance")
    plt.ylabel("URLs")
    save_fig(paths["class_balance"])

    # ~50k stratified sample so the box plots are quick
    sample = train
    if len(train) > EDA_SAMPLE_SIZE:
        parts = []
        for target, frac in train["target"].value_counts(normalize=True).items():
            n = max(1, round(EDA_SAMPLE_SIZE * float(frac)))
            class_rows = train[train["target"].eq(target)]
            parts.append(class_rows.sample(n=min(n, len(class_rows)), random_state=DEFAULT_SEED))
        sample = pd.concat(parts, ignore_index=True)

    fig, axes = plt.subplots(2, 3, figsize=(15, 8.5))
    for ax, col in zip(axes.flat, PROFILE_FEATURES):
        top = max(float(train[col].quantile(0.99)), 1.0)
        data = sample[["target", col]].copy()
        data[col] = data[col].clip(upper=top)
        data["Class"] = data["target"].map(NAMES)
        sns.boxplot(data=data, x="Class", y=col, hue="Class", palette={NAMES[0]: COLORS[0], NAMES[1]: COLORS[1]},
                    legend=False, showfliers=False, ax=ax)
        ax.set_title(col)
        ax.set_xlabel("")
        ax.set_ylabel(f"Value (clipped at p99={top:g})")
    fig.suptitle("Training-only feature spread by class", y=1.02)
    fig.tight_layout()
    save_fig(paths["class_boxplots"])

    top12 = rates.head(12).sort_values("absolute_rate_difference", ascending=True)
    pos = np.arange(len(top12))
    plt.figure(figsize=(10, 7))
    plt.barh(pos - 0.19, top12["benign_rate"], 0.38, color=COLORS[0], label=NAMES[0])
    plt.barh(pos + 0.19, top12["dangerous_rate"], 0.38, color=COLORS[1], hatch="//", label=NAMES[1])
    plt.yticks(pos, top12["feature"])
    plt.xlabel("Share of training URLs")
    plt.title("Largest training-only binary-feature rate differences")
    plt.legend(frameon=False)
    save_fig(paths["binary_rates"])

    return {name: str(path) for name, path in paths.items()}


def run_stage4_pipeline(feature_path=FEATURE_INPUT, seed=DEFAULT_SEED):
    """Run Stage 4: check the data, split by domain, save the manifest, then do EDA on train."""
    df = load_feature_table(feature_path)
    check_feature_table(df)

    ids, keys = create_group_keys(df)
    domain_prof = build_domain_profile(df, keys)
    save_csv(domain_prof, TABLE_DIR / "domain_group_profile.csv")
    save_csv(build_source_quality_profile(df), TABLE_DIR / "source_quality_profile.csv")
    write_json(PRE_SPLIT_PROFILE, build_pre_split_profile(df, domain_prof))

    splits, method = assign_grouped_splits(df, keys, seed=seed)
    check = validate_split(df, ids, keys, splits)
    manifest = pd.DataFrame({"url_id": ids, "group_key": keys, "split": splits})
    save_csv(manifest, SPLIT_MANIFEST)

    # EDA uses train rows only
    train = df[splits.eq("train")].copy()
    summary, comparison, rates, pairs = create_training_tables(train)
    tables = {
        "feature_summary": TABLE_DIR / "train_feature_summary.csv",
        "class_comparison": TABLE_DIR / "train_feature_class_comparison.csv",
        "binary_feature_rates": TABLE_DIR / "binary_feature_rates_by_class.csv",
        "high_correlation_pairs": TABLE_DIR / "high_correlation_pairs.csv",
    }
    save_csv(summary, tables["feature_summary"])
    save_csv(comparison, tables["class_comparison"])
    save_csv(rates, tables["binary_feature_rates"])
    save_csv(pairs, tables["high_correlation_pairs"])
    figures = create_training_figures(train, rates)

    split_audit = {
        "input": {"path": str(feature_path), "sha256": file_sha256(feature_path), "rows": len(df)},
        "method": method,
        "validation": check,
        "manifest": {"path": str(SPLIT_MANIFEST), "sha256": file_sha256(SPLIT_MANIFEST), "rows": len(manifest)},
        "eda": {
            "training_rows": len(train),
            "tables": {name: str(path) for name, path in tables.items()},
            "figures": figures,
        },
    }
    write_json(SPLIT_AUDIT, split_audit)
    return split_audit


if __name__ == "__main__":
    res = run_stage4_pipeline()
    print(json.dumps(to_json(res["validation"]), indent=2, ensure_ascii=False))
    print(f"Split manifest SHA-256: {res['manifest']['sha256']}")
