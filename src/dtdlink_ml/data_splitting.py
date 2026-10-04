"""Stage 4 data audit, grouped splitting and training-only EDA for DTDLINK.

The module treats the Stage 3 feature table as an immutable input.  It groups
rows by registrable domain, assigns each group to exactly one split, and keeps
all model-directed exploration inside the training split.
"""

from __future__ import annotations

from collections import Counter
from itertools import combinations
import hashlib
import json
import math
from pathlib import Path
from typing import Any, Dict, Iterable, Mapping, Sequence, Tuple

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from sklearn.model_selection import StratifiedGroupKFold

from dtdlink_ml.feature_extraction import FEATURE_NAMES, OUTPUT_COLUMNS, file_sha256


PROJECT_ROOT = Path(__file__).resolve().parents[2]
FEATURE_INPUT = PROJECT_ROOT / "data" / "processed" / "url_features.csv"
FEATURE_AUDIT = (
    PROJECT_ROOT / "reports" / "features" / "feature_extraction_audit.json"
)
SPLIT_MANIFEST = PROJECT_ROOT / "data" / "processed" / "split_manifest.csv"
PRE_SPLIT_PROFILE = PROJECT_ROOT / "reports" / "eda" / "pre_split_profile.json"
PREPROCESSING_PLAN = PROJECT_ROOT / "reports" / "eda" / "preprocessing_plan.json"
SPLIT_AUDIT = PROJECT_ROOT / "reports" / "splitting" / "split_audit.json"
DOMAIN_PROFILE = PROJECT_ROOT / "reports" / "tables" / "domain_group_profile.csv"
TRAIN_FEATURE_SUMMARY = (
    PROJECT_ROOT / "reports" / "tables" / "train_feature_summary.csv"
)
TRAIN_CLASS_COMPARISON = (
    PROJECT_ROOT / "reports" / "tables" / "train_feature_class_comparison.csv"
)
BINARY_FEATURE_RATES = (
    PROJECT_ROOT / "reports" / "tables" / "binary_feature_rates_by_class.csv"
)
HIGH_CORRELATION_PAIRS = (
    PROJECT_ROOT / "reports" / "tables" / "high_correlation_pairs.csv"
)
SOURCE_QUALITY_PROFILE = (
    PROJECT_ROOT / "reports" / "tables" / "source_quality_profile.csv"
)
FIGURE_DIR = PROJECT_ROOT / "reports" / "figures"

METADATA_COLUMNS: Tuple[str, ...] = (
    "url",
    "type",
    "target",
    "registrable_domain",
    "tld",
    "parse_issues",
)
COUNT_FEATURES: Tuple[str, ...] = FEATURE_NAMES[:17]
BOOLEAN_FEATURES: Tuple[str, ...] = FEATURE_NAMES[17:]
ALLOWED_TYPES = frozenset({"benign", "defacement", "malware", "phishing"})
SPLIT_NAMES: Tuple[str, ...] = ("train", "validation", "test")
SPLIT_RATIOS: Mapping[str, float] = {
    "train": 0.60,
    "validation": 0.20,
    "test": 0.20,
}
DEFAULT_SEED = 42
N_BASE_FOLDS = 10
CORRELATION_THRESHOLD = 0.85
EDA_SAMPLE_SIZE = 50_000
PROFILE_FEATURES: Tuple[str, ...] = (
    "url_length",
    "host_length",
    "path_length",
    "digit_count",
    "subdomain_count",
    "query_parameter_count",
)


def _json_ready(value: Any) -> Any:
    """Convert NumPy and pandas scalars into JSON-safe Python values."""

    if isinstance(value, dict):
        return {str(key): _json_ready(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_ready(item) for item in value]
    if isinstance(value, (np.integer,)):
        return int(value)
    if isinstance(value, (np.floating,)):
        return None if not math.isfinite(float(value)) else float(value)
    if pd.isna(value):
        return None
    return value


def _write_json(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as stream:
        json.dump(
            _json_ready(dict(payload)),
            stream,
            indent=2,
            ensure_ascii=False,
            sort_keys=True,
        )
        stream.write("\n")


def _sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8", errors="surrogatepass")).hexdigest()


def load_feature_table(
    feature_path: Path = FEATURE_INPUT,
) -> pd.DataFrame:
    """Load the fixed Stage 3 schema with memory-conscious dtypes."""

    dtypes: Dict[str, str] = {
        "url": "string",
        "type": "string",
        "target": "int8",
        "registrable_domain": "string",
        "tld": "string",
        "parse_issues": "string",
    }
    dtypes.update({name: "int32" for name in COUNT_FEATURES})
    dtypes.update({name: "int8" for name in BOOLEAN_FEATURES})
    frame = pd.read_csv(feature_path, dtype=dtypes, keep_default_na=True)
    if list(frame.columns) != list(OUTPUT_COLUMNS):
        raise ValueError(
            "Stage 3 feature schema mismatch: expected "
            f"{list(OUTPUT_COLUMNS)}, received {list(frame.columns)}."
        )
    return frame


def validate_feature_contract(
    frame: pd.DataFrame,
    feature_path: Path = FEATURE_INPUT,
    feature_audit_path: Path = FEATURE_AUDIT,
) -> Dict[str, Any]:
    """Verify the Stage 3 table before any grouping or EDA decisions."""

    audit = json.loads(feature_audit_path.read_text(encoding="utf-8"))
    actual_hash = file_sha256(feature_path)
    missing_counts = frame.isna().sum()
    numeric = frame.loc[:, FEATURE_NAMES]
    numeric_array = numeric.to_numpy(dtype=np.float64, copy=False)
    non_finite_count = int((~np.isfinite(numeric_array)).sum())
    negative_count = int((numeric_array < 0).sum())
    invalid_boolean_counts = {
        feature: int((~frame[feature].isin([0, 1])).sum())
        for feature in BOOLEAN_FEATURES
    }
    failed_boolean_features = {
        feature: count
        for feature, count in invalid_boolean_counts.items()
        if count
    }
    unexpected_types = sorted(set(frame["type"].dropna()) - ALLOWED_TYPES)
    unexpected_targets = sorted(set(frame["target"].dropna()) - {0, 1})

    checks = {
        "columns_match_stage3_schema": list(frame.columns) == list(OUTPUT_COLUMNS),
        "feature_names_match_audit": audit["output"]["feature_names"]
        == list(FEATURE_NAMES),
        "feature_file_hash_matches_audit": actual_hash
        == audit["output"]["sha256"],
        "row_count_matches_audit": len(frame) == audit["output"]["rows"],
        "url_is_complete": int(frame["url"].isna().sum()) == 0,
        "url_is_unique": not frame["url"].duplicated().any(),
        "metadata_labels_are_complete": int(frame[["type", "target"]].isna().sum().sum())
        == 0,
        "types_are_allowed": not unexpected_types,
        "targets_are_binary": not unexpected_targets,
        "numeric_features_are_complete": int(missing_counts[list(FEATURE_NAMES)].sum())
        == 0,
        "numeric_features_are_finite": non_finite_count == 0,
        "numeric_features_are_non_negative": negative_count == 0,
        "boolean_features_are_binary": not failed_boolean_features,
    }
    return {
        "passed": all(checks.values()),
        "checks": checks,
        "evidence": {
            "rows": len(frame),
            "columns": len(frame.columns),
            "feature_count": len(FEATURE_NAMES),
            "feature_file_sha256": actual_hash,
            "missing_cells_by_column": {
                key: int(value)
                for key, value in missing_counts.items()
                if int(value) > 0
            },
            "non_finite_numeric_cells": non_finite_count,
            "negative_numeric_cells": negative_count,
            "invalid_boolean_values": failed_boolean_features,
            "unexpected_types": unexpected_types,
            "unexpected_targets": unexpected_targets,
            "duplicate_url_rows": int(frame["url"].duplicated().sum()),
        },
    }


def create_group_keys(frame: pd.DataFrame) -> Tuple[pd.Series, pd.Series]:
    """Return stable URL ids and label-independent domain grouping keys."""

    url_ids = frame["url"].map(_sha256_text).astype("string")
    domains = frame["registrable_domain"].fillna("").str.strip().str.lower()
    group_keys = ("domain:" + domains).astype("string")
    missing_domain = domains.eq("")
    group_keys = group_keys.mask(missing_domain, "url:" + url_ids)
    return url_ids, group_keys


def build_domain_profile(
    frame: pd.DataFrame,
    group_keys: pd.Series,
) -> pd.DataFrame:
    """Create one compact row per group for split feasibility inspection."""

    working = pd.DataFrame(
        {
            "group_key": group_keys,
            "registrable_domain": frame["registrable_domain"].fillna(""),
            "target": frame["target"].astype("int8"),
            "type": frame["type"],
        }
    )
    target_counts = pd.crosstab(working["group_key"], working["target"])
    type_counts = pd.crosstab(working["group_key"], working["type"])
    for value in (0, 1):
        if value not in target_counts:
            target_counts[value] = 0
    for value in sorted(ALLOWED_TYPES):
        if value not in type_counts:
            type_counts[value] = 0

    profile = (
        working.groupby("group_key", sort=True)
        .agg(
            registrable_domain=("registrable_domain", "first"),
            row_count=("target", "size"),
        )
        .join(target_counts[[0, 1]])
        .join(type_counts[sorted(ALLOWED_TYPES)])
        .reset_index()
        .rename(
            columns={
                0: "benign_count",
                1: "dangerous_count",
                "benign": "source_benign_count",
                "defacement": "source_defacement_count",
                "malware": "source_malware_count",
                "phishing": "source_phishing_count",
            }
        )
    )
    profile.insert(
        1,
        "group_kind",
        np.where(profile["group_key"].str.startswith("domain:"), "domain", "url_fallback"),
    )
    profile["dangerous_rate"] = (
        profile["dangerous_count"] / profile["row_count"]
    ).round(8)
    return profile.sort_values(
        ["row_count", "group_key"], ascending=[False, True], ignore_index=True
    )


def build_pre_split_profile(
    frame: pd.DataFrame,
    contract: Mapping[str, Any],
    domain_profile: pd.DataFrame,
) -> Dict[str, Any]:
    """Summarize only the checks needed to design a fair grouped split."""

    domains = frame["registrable_domain"].fillna("").str.strip()
    missing_domain = domains.eq("")
    group_sizes = domain_profile["row_count"]
    missing_issue_counts: Counter[str] = Counter()
    for issues in frame.loc[missing_domain, "parse_issues"].fillna(""):
        missing_issue_counts.update(issue for issue in issues.split("|") if issue)

    top_groups = domain_profile.head(20)[
        [
            "group_key",
            "group_kind",
            "row_count",
            "benign_count",
            "dangerous_count",
            "dangerous_rate",
        ]
    ].to_dict(orient="records")

    return {
        "scope": {
            "stage": "Stage 4.1 pre-split structural audit",
            "intended_grain": "one unique cleaned URL per row",
            "model_directed_feature_selection_performed": False,
            "test_set_created_at_profile_time": False,
        },
        "contract": contract,
        "dataset": {
            "rows": len(frame),
            "columns": len(frame.columns),
            "feature_count": len(FEATURE_NAMES),
            "unique_urls": int(frame["url"].nunique(dropna=False)),
            "target_counts": {
                str(key): int(value)
                for key, value in frame["target"].value_counts().sort_index().items()
            },
            "source_type_counts": {
                str(key): int(value)
                for key, value in frame["type"].value_counts().sort_index().items()
            },
        },
        "grouping_feasibility": {
            "group_rule": (
                "registrable_domain when present; otherwise a unique SHA-256 URL id"
            ),
            "group_count": len(domain_profile),
            "registrable_domain_count": int(domains[~missing_domain].nunique()),
            "rows_without_registrable_domain": int(missing_domain.sum()),
            "fallback_group_count": int(
                domain_profile["group_kind"].eq("url_fallback").sum()
            ),
            "singleton_groups": int(group_sizes.eq(1).sum()),
            "repeated_groups": int(group_sizes.gt(1).sum()),
            "largest_group_rows": int(group_sizes.max()),
            "group_size_quantiles": {
                str(quantile): float(group_sizes.quantile(quantile))
                for quantile in (0.5, 0.9, 0.95, 0.99, 1.0)
            },
            "missing_domain_issue_counts": dict(sorted(missing_issue_counts.items())),
            "missing_domain_target_counts": {
                str(key): int(value)
                for key, value in frame.loc[missing_domain, "target"]
                .value_counts()
                .sort_index()
                .items()
            },
            "top_20_groups": top_groups,
        },
        "leakage_boundary": {
            "allowed_before_split": [
                "schema and data-quality checks",
                "group-size and split-feasibility checks",
                "label counts used only to balance the partition",
            ],
            "deferred_until_after_split": [
                "feature-target comparison",
                "correlation-based modelling decisions",
                "scaler fitting",
                "TLD-frequency fitting",
                "model training and threshold selection",
            ],
        },
    }


def build_source_quality_profile(frame: pd.DataFrame) -> pd.DataFrame:
    """Expose source-format associations needed to interpret later models."""

    rows = []
    for source_type, subset in frame.groupby("type", sort=True):
        rows.append(
            {
                "source_type": source_type,
                "rows": len(subset),
                "dangerous_rate": float(subset["target"].mean()),
                "has_scheme_rate": float(subset["has_scheme"].mean()),
                "uses_https_rate": float(subset["uses_https"].mean()),
                "parse_ok_rate": float(subset["parse_ok"].mean()),
                "unknown_tld_rate": float(subset["has_unknown_tld"].mean()),
                "ip_host_rate": float(subset["has_ip_host"].mean()),
                "control_character_rate": float(
                    subset["has_control_character"].mean()
                ),
            }
        )
    return pd.DataFrame(rows)


def _fold_statistics(
    fold_ids: np.ndarray,
    targets: np.ndarray,
) -> Dict[int, Tuple[int, int]]:
    return {
        fold: (
            int((fold_ids == fold).sum()),
            int(targets[fold_ids == fold].sum()),
        )
        for fold in range(N_BASE_FOLDS)
    }


def choose_fold_allocation(
    fold_ids: np.ndarray,
    targets: np.ndarray,
) -> Dict[str, Tuple[int, ...]]:
    """Choose two test and two validation folds closest to 60/20/20."""

    statistics = _fold_statistics(fold_ids, targets)
    total_rows = len(targets)
    overall_rate = float(targets.mean())
    best_score: float | None = None
    best: Dict[str, Tuple[int, ...]] | None = None

    for test_folds in combinations(range(N_BASE_FOLDS), 2):
        remaining = [fold for fold in range(N_BASE_FOLDS) if fold not in test_folds]
        for validation_folds in combinations(remaining, 2):
            train_folds = tuple(
                fold for fold in remaining if fold not in validation_folds
            )
            candidate = {
                "train": train_folds,
                "validation": tuple(validation_folds),
                "test": tuple(test_folds),
            }
            score = 0.0
            for split_name, selected_folds in candidate.items():
                rows = sum(statistics[fold][0] for fold in selected_folds)
                positives = sum(statistics[fold][1] for fold in selected_folds)
                row_share = rows / total_rows
                positive_rate = positives / rows
                score += 4.0 * abs(row_share - SPLIT_RATIOS[split_name])
                score += abs(positive_rate - overall_rate)
            if best_score is None or score < best_score:
                best_score = score
                best = candidate

    if best is None:
        raise RuntimeError("Unable to choose grouped fold allocation.")
    return best


def assign_grouped_splits(
    frame: pd.DataFrame,
    group_keys: pd.Series,
    seed: int = DEFAULT_SEED,
) -> Tuple[pd.Series, Dict[str, Any]]:
    """Assign every domain group to one deterministic train/validation/test set."""

    targets = frame["target"].to_numpy(dtype=np.int8, copy=False)
    fold_ids = np.full(len(frame), -1, dtype=np.int8)
    splitter = StratifiedGroupKFold(
        n_splits=N_BASE_FOLDS,
        shuffle=True,
        random_state=seed,
    )
    placeholder_features = np.zeros((len(frame), 1), dtype=np.int8)
    for fold, (_, held_out_indices) in enumerate(
        splitter.split(placeholder_features, targets, groups=group_keys)
    ):
        fold_ids[held_out_indices] = fold
    if (fold_ids < 0).any():
        raise RuntimeError("At least one row was not assigned to a base fold.")

    allocation = choose_fold_allocation(fold_ids, targets)
    splits = np.full(len(frame), "", dtype=object)
    for split_name, selected_folds in allocation.items():
        splits[np.isin(fold_ids, selected_folds)] = split_name
    if (splits == "").any():
        raise RuntimeError("At least one row was not assigned to a final split.")

    base_fold_details = {}
    for fold, (rows, positives) in _fold_statistics(fold_ids, targets).items():
        base_fold_details[str(fold)] = {
            "rows": rows,
            "row_share": rows / len(frame),
            "dangerous_count": positives,
            "dangerous_rate": positives / rows,
        }
    return pd.Series(splits, index=frame.index, dtype="string"), {
        "algorithm": "StratifiedGroupKFold plus deterministic fold-allocation search",
        "seed": seed,
        "base_fold_count": N_BASE_FOLDS,
        "selected_folds": {
            key: list(value) for key, value in allocation.items()
        },
        "base_fold_details": base_fold_details,
    }


def validate_split(
    frame: pd.DataFrame,
    url_ids: pd.Series,
    group_keys: pd.Series,
    splits: pd.Series,
) -> Dict[str, Any]:
    """Prove row coverage, URL uniqueness and zero group overlap."""

    split_sets = {
        name: set(group_keys[splits.eq(name)]) for name in SPLIT_NAMES
    }
    pairwise_overlap = {
        "train_validation": len(split_sets["train"] & split_sets["validation"]),
        "train_test": len(split_sets["train"] & split_sets["test"]),
        "validation_test": len(split_sets["validation"] & split_sets["test"]),
    }
    counts = splits.value_counts()
    details: Dict[str, Any] = {}
    for split_name in SPLIT_NAMES:
        mask = splits.eq(split_name)
        subset = frame.loc[mask]
        details[split_name] = {
            "rows": int(mask.sum()),
            "row_share": float(mask.mean()),
            "groups": int(group_keys[mask].nunique()),
            "target_counts": {
                str(key): int(value)
                for key, value in subset["target"].value_counts().sort_index().items()
            },
            "dangerous_rate": float(subset["target"].mean()),
            "source_type_counts": {
                str(key): int(value)
                for key, value in subset["type"].value_counts().sort_index().items()
            },
        }

    checks = {
        "all_rows_assigned_once": int(counts.sum()) == len(frame),
        "only_expected_split_names": set(counts.index) == set(SPLIT_NAMES),
        "url_ids_are_unique": not url_ids.duplicated().any(),
        "group_keys_are_complete": not group_keys.isna().any()
        and not group_keys.eq("").any(),
        "zero_group_overlap": all(value == 0 for value in pairwise_overlap.values()),
    }
    return {
        "passed": all(checks.values()),
        "checks": checks,
        "pairwise_group_overlap": pairwise_overlap,
        "splits": details,
    }


def create_training_tables(
    training: pd.DataFrame,
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Create bounded, full-training summaries without consulting test rows."""

    numeric = training.loc[:, FEATURE_NAMES]
    describe = numeric.describe(percentiles=[0.25, 0.5, 0.75, 0.95, 0.99]).T
    summary = describe.rename(
        columns={
            "count": "non_missing_count",
            "50%": "median",
            "25%": "p25",
            "75%": "p75",
            "95%": "p95",
            "99%": "p99",
        }
    )
    summary.insert(0, "feature", summary.index)
    summary["missing_count"] = numeric.isna().sum().to_numpy()
    summary["zero_rate"] = numeric.eq(0).mean().to_numpy()
    summary["unique_values"] = numeric.nunique().to_numpy()
    summary = summary.reset_index(drop=True)

    class_rows = []
    for feature in FEATURE_NAMES:
        benign = training.loc[training["target"].eq(0), feature]
        dangerous = training.loc[training["target"].eq(1), feature]
        pooled_variance = (
            ((len(benign) - 1) * benign.var(ddof=1))
            + ((len(dangerous) - 1) * dangerous.var(ddof=1))
        ) / max(len(benign) + len(dangerous) - 2, 1)
        pooled_sd = math.sqrt(max(float(pooled_variance), 0.0))
        mean_difference = float(dangerous.mean() - benign.mean())
        class_rows.append(
            {
                "feature": feature,
                "benign_mean": float(benign.mean()),
                "dangerous_mean": float(dangerous.mean()),
                "mean_difference_dangerous_minus_benign": mean_difference,
                "benign_median": float(benign.median()),
                "dangerous_median": float(dangerous.median()),
                "standardized_mean_difference": (
                    mean_difference / pooled_sd if pooled_sd else 0.0
                ),
            }
        )
    comparison = pd.DataFrame(class_rows)
    comparison["absolute_standardized_mean_difference"] = comparison[
        "standardized_mean_difference"
    ].abs()
    comparison = comparison.sort_values(
        ["absolute_standardized_mean_difference", "feature"],
        ascending=[False, True],
        ignore_index=True,
    )

    binary_rows = []
    for feature in BOOLEAN_FEATURES:
        benign_rate = float(training.loc[training["target"].eq(0), feature].mean())
        dangerous_rate = float(
            training.loc[training["target"].eq(1), feature].mean()
        )
        binary_rows.append(
            {
                "feature": feature,
                "benign_rate": benign_rate,
                "dangerous_rate": dangerous_rate,
                "rate_difference_dangerous_minus_benign": dangerous_rate
                - benign_rate,
            }
        )
    binary_rates = pd.DataFrame(binary_rows)
    binary_rates["absolute_rate_difference"] = binary_rates[
        "rate_difference_dangerous_minus_benign"
    ].abs()
    binary_rates = binary_rates.sort_values(
        ["absolute_rate_difference", "feature"],
        ascending=[False, True],
        ignore_index=True,
    )

    correlation = numeric.corr(method="pearson")
    pair_rows = []
    for left_index, left in enumerate(FEATURE_NAMES):
        for right in FEATURE_NAMES[left_index + 1 :]:
            value = correlation.loc[left, right]
            if pd.notna(value) and abs(float(value)) >= CORRELATION_THRESHOLD:
                pair_rows.append(
                    {
                        "feature_a": left,
                        "feature_b": right,
                        "pearson_correlation": float(value),
                        "absolute_correlation": abs(float(value)),
                    }
                )
    correlation_pairs = pd.DataFrame(
        pair_rows,
        columns=[
            "feature_a",
            "feature_b",
            "pearson_correlation",
            "absolute_correlation",
        ],
    ).sort_values(
        ["absolute_correlation", "feature_a", "feature_b"],
        ascending=[False, True, True],
        ignore_index=True,
    )
    return summary, comparison, binary_rates, correlation_pairs, correlation


def _sample_training(training: pd.DataFrame) -> pd.DataFrame:
    if len(training) <= EDA_SAMPLE_SIZE:
        return training.copy()
    fractions = training["target"].value_counts(normalize=True)
    samples = []
    for target, fraction in fractions.items():
        rows = max(1, round(EDA_SAMPLE_SIZE * float(fraction)))
        subset = training[training["target"].eq(target)]
        samples.append(subset.sample(n=min(rows, len(subset)), random_state=DEFAULT_SEED))
    return pd.concat(samples, ignore_index=True)


def _save_figure(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(path, dpi=160, bbox_inches="tight", facecolor="white")
    plt.close()


def create_training_figures(
    training: pd.DataFrame,
    group_keys: pd.Series,
    binary_rates: pd.DataFrame,
    correlation: pd.DataFrame,
) -> Dict[str, str]:
    """Create report-ready figures from training rows only."""

    sns.set_theme(style="whitegrid", context="notebook")
    colors = {0: "#2563C9", 1: "#B26B00"}
    labels = {0: "Benign", 1: "Potentially dangerous"}
    figure_paths: Dict[str, Path] = {
        "class_balance": FIGURE_DIR / "class_balance_train.png",
        "numeric_distributions": FIGURE_DIR / "numeric_feature_distributions.png",
        "class_boxplots": FIGURE_DIR / "feature_class_boxplots.png",
        "binary_rates": FIGURE_DIR / "binary_feature_rates.png",
        "domain_concentration": FIGURE_DIR / "domain_concentration.png",
        "correlation": FIGURE_DIR / "train_feature_correlation.png",
    }

    counts = training["target"].value_counts().reindex([0, 1], fill_value=0)
    plt.figure(figsize=(7.5, 4.8))
    bars = plt.bar(
        [labels[index] for index in counts.index],
        counts.values,
        color=[colors[index] for index in counts.index],
    )
    for bar, count in zip(bars, counts.values):
        plt.text(
            bar.get_x() + bar.get_width() / 2,
            count,
            f"{count:,}\n({count / len(training):.1%})",
            ha="center",
            va="bottom",
        )
    plt.ylim(0, float(counts.max()) * 1.14)
    plt.title("Training-set class balance")
    plt.ylabel("URLs")
    plt.xlabel("")
    _save_figure(figure_paths["class_balance"])

    sample = _sample_training(training)
    fig, axes = plt.subplots(2, 3, figsize=(15, 8.5))
    for axis, feature in zip(axes.flat, PROFILE_FEATURES):
        upper = max(float(training[feature].quantile(0.99)), 1.0)
        bins = np.linspace(0, upper, 31)
        for target in (0, 1):
            values = sample.loc[sample["target"].eq(target), feature].clip(upper=upper)
            axis.hist(
                values,
                bins=bins,
                histtype="step",
                linewidth=1.8,
                linestyle="-" if target == 0 else "--",
                color=colors[target],
                label=labels[target],
            )
        axis.set_title(feature)
        axis.set_xlabel(f"Value (clipped at training p99={upper:g})")
        axis.set_ylabel("Sampled URLs")
    axes.flat[0].legend(frameon=False)
    fig.suptitle("Training-only numeric feature distributions", y=1.02)
    fig.tight_layout()
    _save_figure(figure_paths["numeric_distributions"])

    fig, axes = plt.subplots(2, 3, figsize=(15, 8.5))
    for axis, feature in zip(axes.flat, PROFILE_FEATURES):
        upper = max(float(training[feature].quantile(0.99)), 1.0)
        plot_frame = sample[["target", feature]].copy()
        plot_frame[feature] = plot_frame[feature].clip(upper=upper)
        plot_frame["Class"] = plot_frame["target"].map(labels)
        sns.boxplot(
            data=plot_frame,
            x="Class",
            y=feature,
            hue="Class",
            palette={labels[key]: value for key, value in colors.items()},
            legend=False,
            showfliers=False,
            ax=axis,
        )
        axis.set_title(feature)
        axis.set_xlabel("")
        axis.set_ylabel(f"Value (clipped at p99={upper:g})")
    fig.suptitle("Training-only feature spread by class", y=1.02)
    fig.tight_layout()
    _save_figure(figure_paths["class_boxplots"])

    rate_plot = binary_rates.head(12).sort_values(
        "absolute_rate_difference", ascending=True
    )
    positions = np.arange(len(rate_plot))
    height = 0.38
    plt.figure(figsize=(10, 7))
    plt.barh(
        positions - height / 2,
        rate_plot["benign_rate"],
        height,
        color=colors[0],
        label=labels[0],
    )
    plt.barh(
        positions + height / 2,
        rate_plot["dangerous_rate"],
        height,
        color=colors[1],
        hatch="//",
        label=labels[1],
    )
    plt.yticks(positions, rate_plot["feature"])
    plt.xlabel("Share of training URLs")
    plt.title("Largest training-only binary-feature rate differences")
    plt.legend(frameon=False)
    _save_figure(figure_paths["binary_rates"])

    domain_counts = (
        group_keys.loc[training.index]
        .loc[lambda values: values.str.startswith("domain:")]
        .str.removeprefix("domain:")
        .value_counts()
        .head(15)
        .sort_values()
    )
    plt.figure(figsize=(10, 7))
    bars = plt.barh(domain_counts.index, domain_counts.values, color="#2563C9")
    for bar, count in zip(bars, domain_counts.values):
        plt.text(count, bar.get_y() + bar.get_height() / 2, f" {count:,}", va="center")
    plt.xlabel("Training URLs")
    plt.ylabel("Registrable domain")
    plt.title("Largest registrable-domain groups in training")
    _save_figure(figure_paths["domain_concentration"])

    plt.figure(figsize=(14, 12))
    mask = np.triu(np.ones_like(correlation, dtype=bool), k=1)
    sns.heatmap(
        correlation,
        mask=mask,
        cmap="vlag",
        center=0,
        vmin=-1,
        vmax=1,
        square=True,
        linewidths=0.15,
        cbar_kws={"label": "Pearson correlation", "shrink": 0.75},
    )
    plt.title("Training-only feature correlation")
    plt.xticks(rotation=55, ha="right", fontsize=7)
    plt.yticks(rotation=0, fontsize=7)
    _save_figure(figure_paths["correlation"])

    return {key: str(value) for key, value in figure_paths.items()}


def run_stage4_pipeline(
    feature_path: Path = FEATURE_INPUT,
    seed: int = DEFAULT_SEED,
) -> Dict[str, Any]:
    """Run the complete Stage 4 audit, split, training-only EDA and evidence write."""

    for path in (
        PRE_SPLIT_PROFILE,
        PREPROCESSING_PLAN,
        SPLIT_AUDIT,
        DOMAIN_PROFILE,
        TRAIN_FEATURE_SUMMARY,
        TRAIN_CLASS_COMPARISON,
        BINARY_FEATURE_RATES,
        HIGH_CORRELATION_PAIRS,
        SOURCE_QUALITY_PROFILE,
        SPLIT_MANIFEST,
    ):
        path.parent.mkdir(parents=True, exist_ok=True)

    frame = load_feature_table(feature_path)
    contract = validate_feature_contract(frame, feature_path)
    if not contract["passed"]:
        raise ValueError("Stage 3 feature contract failed; Stage 4 cannot continue.")

    url_ids, group_keys = create_group_keys(frame)
    domain_profile = build_domain_profile(frame, group_keys)
    source_quality_profile = build_source_quality_profile(frame)
    pre_split_profile = build_pre_split_profile(frame, contract, domain_profile)
    pre_split_profile["source_format_association"] = {
        "purpose": (
            "data-quality context for split interpretation, not feature selection"
        ),
        "table": str(SOURCE_QUALITY_PROFILE),
        "largest_has_scheme_rate_gap": float(
            source_quality_profile["has_scheme_rate"].max()
            - source_quality_profile["has_scheme_rate"].min()
        ),
    }
    domain_profile.to_csv(DOMAIN_PROFILE, index=False, lineterminator="\n")
    source_quality_profile.to_csv(
        SOURCE_QUALITY_PROFILE, index=False, lineterminator="\n"
    )
    _write_json(PRE_SPLIT_PROFILE, pre_split_profile)

    splits, method = assign_grouped_splits(frame, group_keys, seed=seed)
    validation = validate_split(frame, url_ids, group_keys, splits)
    if not validation["passed"]:
        raise RuntimeError("Leakage-safe split validation failed.")

    manifest = pd.DataFrame(
        {"url_id": url_ids, "group_key": group_keys, "split": splits}
    )
    manifest.to_csv(SPLIT_MANIFEST, index=False, lineterminator="\n")

    training = frame.loc[splits.eq("train")].copy()
    summary, comparison, binary_rates, correlation_pairs, correlation = (
        create_training_tables(training)
    )
    summary.to_csv(TRAIN_FEATURE_SUMMARY, index=False, lineterminator="\n")
    comparison.to_csv(TRAIN_CLASS_COMPARISON, index=False, lineterminator="\n")
    binary_rates.to_csv(BINARY_FEATURE_RATES, index=False, lineterminator="\n")
    correlation_pairs.to_csv(
        HIGH_CORRELATION_PAIRS, index=False, lineterminator="\n"
    )
    figure_paths = create_training_figures(
        training,
        group_keys,
        binary_rates,
        correlation,
    )

    constant_features = summary.loc[
        summary["unique_values"].eq(1), "feature"
    ].tolist()
    preprocessing_plan: Dict[str, Any] = {
        "feature_schema_unchanged": True,
        "model_input_features": list(FEATURE_NAMES),
        "metadata_excluded_from_numeric_model_input": list(METADATA_COLUMNS),
        "decisions": {
            "scaling": {
                "status": "required for scale-sensitive models",
                "fit_scope": "training rows only",
                "implementation_stage": "Stage 5 model pipeline",
            },
            "tld_frequency": {
                "status": "optional candidate; not created in Stage 4",
                "fit_scope": "training rows only if selected",
                "unknown_value_rule": "must be documented before implementation",
            },
            "feature_removal": {
                "status": "none in Stage 4",
                "reason": (
                    "correlation and class comparisons are diagnostic; removal "
                    "requires validation evidence in Stage 5"
                ),
            },
            "test_set": {
                "status": "locked",
                "allowed_next_use": "one final evaluation in Stage 7",
                "prohibited_uses": [
                    "feature selection",
                    "transformation fitting",
                    "model selection",
                    "hyperparameter tuning",
                    "threshold selection",
                ],
            },
        },
        "training_observations": {
            "constant_features": constant_features,
            "high_correlation_pair_count": len(correlation_pairs),
            "correlation_threshold": CORRELATION_THRESHOLD,
        },
    }
    _write_json(PREPROCESSING_PLAN, preprocessing_plan)

    split_audit: Dict[str, Any] = {
        "input": {
            "path": str(feature_path),
            "sha256": file_sha256(feature_path),
            "rows": len(frame),
        },
        "method": {
            **method,
            "group_key": (
                "registrable_domain; SHA-256 URL fallback for missing domains"
            ),
            "target_ratios": dict(SPLIT_RATIOS),
            "target_used_only_for_partition_balance": True,
        },
        "validation": validation,
        "manifest": {
            "path": str(SPLIT_MANIFEST),
            "sha256": file_sha256(SPLIT_MANIFEST),
            "rows": len(manifest),
            "columns": list(manifest.columns),
        },
        "test_lock": {
            "locked": True,
            "lock_identity": "split manifest SHA-256",
            "allowed_next_use": "Stage 7 final evaluation",
        },
        "eda": {
            "model_directed_scope": "training rows only",
            "training_rows": len(training),
            "tables": {
                "feature_summary": str(TRAIN_FEATURE_SUMMARY),
                "class_comparison": str(TRAIN_CLASS_COMPARISON),
                "binary_feature_rates": str(BINARY_FEATURE_RATES),
                "high_correlation_pairs": str(HIGH_CORRELATION_PAIRS),
            },
            "figures": figure_paths,
        },
    }
    _write_json(SPLIT_AUDIT, split_audit)
    return split_audit


def main() -> None:
    audit = run_stage4_pipeline()
    print(json.dumps(_json_ready(audit["validation"]), indent=2, ensure_ascii=False))
    print(f"Split manifest SHA-256: {audit['manifest']['sha256']}")


if __name__ == "__main__":
    main()
