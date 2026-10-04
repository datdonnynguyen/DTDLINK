"""Train and compare DTDLINK classifiers without using the locked test set.

Stage 5 fits on train rows and reports validation results. The student-selected
classifier and alert threshold are recorded without evaluating the test set.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Tuple

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, confusion_matrix, f1_score, precision_score, recall_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.tree import DecisionTreeClassifier

from dtdlink_ml.feature_extraction import FEATURE_NAMES, file_sha256


PROJECT_ROOT = Path(__file__).resolve().parents[2]
FEATURE_INPUT = PROJECT_ROOT / "data" / "processed" / "url_features.csv"
SPLIT_MANIFEST = PROJECT_ROOT / "data" / "processed" / "split_manifest.csv"
REPORT_DIR = PROJECT_ROOT / "reports" / "classification"
FEATURE_SHA256 = "fe049dd9f6b2c92570354b28b2885312f64c73b03b7053be06bc35cce5a591ff"
MANIFEST_SHA256 = "fbcbcf2ff68e26acfa2bb435b53c262645688a54a195ff64e283e7ff753ffc2f"
RANDOM_SEED = 42
CHUNK_SIZE = 50_000
THRESHOLDS = (0.20, 0.30, 0.40, 0.50, 0.60, 0.70, 0.80)
MODEL_NAMES = ("logistic_regression", "decision_tree", "random_forest")
SELECTED_MODEL = "random_forest"
SELECTED_THRESHOLD = 0.50


def _url_id(url: str) -> str:
    return hashlib.sha256(url.encode("utf-8", errors="surrogatepass")).hexdigest()


def validate_manifest(manifest: pd.DataFrame) -> Dict[str, int]:
    """Check membership and grouping, without reading any test model values."""
    if list(manifest.columns) != ["url_id", "group_key", "split"]:
        raise ValueError("Split manifest columns differ from the locked Stage 4 schema.")
    if manifest.isna().any().any() or manifest["url_id"].duplicated().any():
        raise ValueError("Split manifest has missing values or duplicate URL ids.")
    if not manifest["split"].isin(("train", "validation", "test")).all():
        raise ValueError("Split manifest contains an unknown split.")
    if set(manifest["split"]) != {"train", "validation", "test"}:
        raise ValueError("Split manifest must contain all three splits.")
    if manifest.groupby("group_key", sort=False)["split"].nunique().max() != 1:
        raise ValueError("A registrable-domain group crosses split boundaries.")
    return {name: int(manifest["split"].eq(name).sum()) for name in ("train", "validation", "test")}


def select_allowed_rows(
    feature_chunk: pd.DataFrame, manifest_chunk: pd.DataFrame
) -> Dict[str, pd.DataFrame]:
    """Verify row identity and discard test rows before accessing model values."""
    if len(feature_chunk) != len(manifest_chunk):
        raise ValueError("Feature table and split manifest have different row counts.")
    actual_ids = feature_chunk["url"].map(_url_id).to_numpy()
    if not np.array_equal(actual_ids, manifest_chunk["url_id"].to_numpy()):
        raise ValueError("Feature rows no longer align with the locked split manifest.")
    return {
        name: feature_chunk.loc[manifest_chunk["split"].eq(name).to_numpy()].copy()
        for name in ("train", "validation")
    }


def load_allowed_data(
    feature_path: Path = FEATURE_INPUT,
    manifest_path: Path = SPLIT_MANIFEST,
    expected_feature_sha256: str = FEATURE_SHA256,
    expected_manifest_sha256: str = MANIFEST_SHA256,
    chunk_size: int = CHUNK_SIZE,
) -> Tuple[pd.DataFrame, pd.DataFrame, Dict[str, int]]:
    """Load only train/validation rows into the modelling frames."""
    if file_sha256(feature_path) != expected_feature_sha256:
        raise ValueError("Stage 3 feature table hash changed; stop before modelling.")
    if file_sha256(manifest_path) != expected_manifest_sha256:
        raise ValueError("Locked Stage 4 manifest hash changed; stop before modelling.")
    manifest = pd.read_csv(manifest_path, dtype="string", keep_default_na=False)
    split_counts = validate_manifest(manifest)
    usecols = ["url", "type", "target", *FEATURE_NAMES]
    feature_chunks = pd.read_csv(feature_path, usecols=usecols, chunksize=chunk_size)
    retained: Dict[str, List[pd.DataFrame]] = {"train": [], "validation": []}
    offset = 0
    for chunk in feature_chunks:
        membership = manifest.iloc[offset : offset + len(chunk)]
        selected = select_allowed_rows(chunk, membership)
        for name in retained:
            retained[name].append(selected[name])
        offset += len(chunk)
    if offset != len(manifest):
        raise ValueError("Feature table and split manifest have different row counts.")
    train = pd.concat(retained["train"], ignore_index=True)
    validation = pd.concat(retained["validation"], ignore_index=True)
    if len(train) != split_counts["train"] or len(validation) != split_counts["validation"]:
        raise ValueError("Selected train/validation counts differ from the manifest.")
    for name, frame in (("train", train), ("validation", validation)):
        if frame["target"].isna().any() or not frame["target"].isin((0, 1)).all():
            raise ValueError(f"{name} contains invalid target values.")
        values = frame.loc[:, FEATURE_NAMES].to_numpy(dtype=np.float64)
        if not np.isfinite(values).all() or (values < 0).any():
            raise ValueError(f"{name} contains invalid numeric features.")
    return train, validation, split_counts


def make_models() -> Mapping[str, Any]:
    """Define comparable, fixed baselines; no test-informed tuning."""
    return {
        "logistic_regression": Pipeline(
            [
                ("scale", StandardScaler()),
                ("classifier", LogisticRegression(solver="liblinear", max_iter=500, class_weight="balanced", random_state=RANDOM_SEED)),
            ]
        ),
        "decision_tree": DecisionTreeClassifier(
            max_depth=12,
            min_samples_leaf=100,
            class_weight="balanced",
            random_state=RANDOM_SEED,
        ),
        "random_forest": RandomForestClassifier(
            n_estimators=100,
            max_depth=12,
            min_samples_leaf=100,
            max_features="sqrt",
            class_weight="balanced_subsample",
            random_state=RANDOM_SEED,
            n_jobs=2,
        ),
    }


def score_predictions(y_true: Iterable[int], probability: Iterable[float], threshold: float) -> Dict[str, Any]:
    """Return positive-class metrics and explicit error counts."""
    if not 0 < threshold < 1:
        raise ValueError("Threshold must lie strictly between 0 and 1.")
    actual = np.asarray(list(y_true), dtype=np.int8)
    scores = np.asarray(list(probability), dtype=np.float64)
    if len(actual) != len(scores) or not np.isfinite(scores).all() or ((scores < 0) | (scores > 1)).any():
        raise ValueError("Labels and model probabilities are inconsistent.")
    predicted = (scores >= threshold).astype(np.int8)
    tn, fp, fn, tp = confusion_matrix(actual, predicted, labels=[0, 1]).ravel()
    return {
        "threshold": float(threshold),
        "accuracy": float(accuracy_score(actual, predicted)),
        "precision": float(precision_score(actual, predicted, zero_division=0)),
        "recall": float(recall_score(actual, predicted, zero_division=0)),
        "f1": float(f1_score(actual, predicted, zero_division=0)),
        "true_negative": int(tn),
        "false_positive": int(fp),
        "false_negative": int(fn),
        "true_positive": int(tp),
    }


def compare_models(train: pd.DataFrame, validation: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Fit on train, then compare validation predictions under shared rules."""
    x_train = train.loc[:, FEATURE_NAMES]
    y_train = train["target"].to_numpy(dtype=np.int8)
    x_validation = validation.loc[:, FEATURE_NAMES]
    y_validation = validation["target"].to_numpy(dtype=np.int8)
    metrics_rows = []
    train_rows = []
    threshold_rows = []
    subgroup_rows = []
    for name, model in make_models().items():
        model.fit(x_train, y_train)
        with np.errstate(over="ignore", divide="ignore", invalid="ignore"):
            train_probability = model.predict_proba(x_train)[:, 1]
        if not np.isfinite(train_probability).all() or ((train_probability < 0) | (train_probability > 1)).any():
            raise ValueError(f"{name} produced invalid training probabilities.")
        train_rows.append({"model": name, **score_predictions(y_train, train_probability, 0.50)})
        # Some macOS BLAS builds warn during this matmul despite finite outputs.
        # Validate every returned probability instead of trusting that warning.
        with np.errstate(over="ignore", divide="ignore", invalid="ignore"):
            probability = model.predict_proba(x_validation)[:, 1]
        if not np.isfinite(probability).all() or ((probability < 0) | (probability > 1)).any():
            raise ValueError(f"{name} produced invalid validation probabilities.")
        metrics_rows.append({"model": name, **score_predictions(y_validation, probability, 0.50)})
        for threshold in THRESHOLDS:
            threshold_rows.append({"model": name, **score_predictions(y_validation, probability, threshold)})
        predictions = probability >= 0.50
        for source_type in ("benign", "phishing", "malware", "defacement"):
            mask = validation["type"].eq(source_type).to_numpy()
            if not mask.any():
                continue
            subgroup_rows.append(
                {
                    "model": name,
                    "source_type": source_type,
                    "rows": int(mask.sum()),
                    "correct": int((predictions[mask] == y_validation[mask]).sum()),
                    "missed_dangerous": int(((y_validation[mask] == 1) & ~predictions[mask]).sum()),
                    "false_alarms": int(((y_validation[mask] == 0) & predictions[mask]).sum()),
                }
            )
    return pd.DataFrame(train_rows), pd.DataFrame(metrics_rows), pd.DataFrame(threshold_rows), pd.DataFrame(subgroup_rows)


def run_stage5(report_dir: Path = REPORT_DIR) -> Dict[str, Any]:
    """Write validation evidence and the student's selected model/threshold."""
    train, validation, split_counts = load_allowed_data()
    train_metrics, metrics, thresholds, subgroups = compare_models(train, validation)
    report_dir.mkdir(parents=True, exist_ok=True)
    train_metrics.to_csv(report_dir / "train_metrics.csv", index=False)
    metrics.to_csv(report_dir / "validation_metrics.csv", index=False)
    thresholds.to_csv(report_dir / "threshold_tradeoffs.csv", index=False)
    subgroups.to_csv(report_dir / "validation_subgroups.csv", index=False)
    selected_rows = thresholds.loc[
        thresholds["model"].eq(SELECTED_MODEL)
        & thresholds["threshold"].eq(SELECTED_THRESHOLD)
    ]
    if len(selected_rows) != 1:
        raise ValueError("Selected classifier and threshold are absent from validation results.")
    selected_metrics = selected_rows.iloc[0].to_dict()
    summary = {
        "feature_sha256": FEATURE_SHA256,
        "manifest_sha256": MANIFEST_SHA256,
        "feature_names": list(FEATURE_NAMES),
        "split_counts": split_counts,
        "fit_split": "train",
        "comparison_split": "validation",
        "test_used_for_modelling_or_metrics": False,
        "models": list(MODEL_NAMES),
        "model_settings": {
            "logistic_regression": {"scaler": "StandardScaler fit on train", "solver": "liblinear", "max_iter": 500},
            "decision_tree": {"max_depth": 12, "min_samples_leaf": 100, "random_state": RANDOM_SEED},
            "random_forest": {
                "n_estimators": 100,
                "max_depth": 12,
                "min_samples_leaf": 100,
                "max_features": "sqrt",
                "class_weight": "balanced_subsample",
                "random_state": RANDOM_SEED,
                "n_jobs": 2,
            },
        },
        "class_weight": "balanced for logistic regression/decision tree; balanced_subsample for random forest",
        "default_threshold": 0.50,
        "thresholds_reviewed": list(THRESHOLDS),
        "final_model_selected": True,
        "final_threshold_selected": True,
        "selected_model": SELECTED_MODEL,
        "selected_threshold": SELECTED_THRESHOLD,
        "selected_validation_metrics": selected_metrics,
    }
    (report_dir / "validation_summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    return summary


if __name__ == "__main__":
    result = run_stage5()
    print(json.dumps(result, indent=2, ensure_ascii=False))
