"""Fit classifiers on train and compare them on validation."""

import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, confusion_matrix, f1_score, precision_score, recall_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.tree import DecisionTreeClassifier

from dtdlink_ml.feature_extraction import FEATURE_NAMES, file_sha256, url_id

ROOT = Path(__file__).resolve().parents[2]
FEATURE_INPUT = ROOT / "data/processed/url_features.csv"
SPLIT_MANIFEST = ROOT / "data/processed/split_manifest.csv"
REPORT_DIR = ROOT / "reports/classification"
# hashes of the feature table and manifest from Stage 4, so we know the split hasn't changed
FEATURE_SHA256 = "fe049dd9f6b2c92570354b28b2885312f64c73b03b7053be06bc35cce5a591ff"
MANIFEST_SHA256 = "fbcbcf2ff68e26acfa2bb435b53c262645688a54a195ff64e283e7ff753ffc2f"
RANDOM_SEED = 42
CHUNK_SIZE = 50_000
THRESHOLDS = (0.20, 0.30, 0.40, 0.50, 0.60, 0.70, 0.80)
SELECTED_MODEL = "random_forest"
SELECTED_THRESHOLD = 0.50
FOREST_SETTINGS = {
    "n_estimators": 100,
    "max_depth": 12,
    "min_samples_leaf": 100,
    "max_features": "sqrt",
    "class_weight": "balanced_subsample",
    "random_state": RANDOM_SEED,
    "n_jobs": 2,
}


def validate_manifest(manifest):
    """Check the split manifest and return how many rows each split has."""
    if list(manifest.columns) != ["url_id", "group_key", "split"]:
        raise ValueError(f"Unexpected manifest columns: {list(manifest.columns)}")
    if manifest.isna().any().any() or manifest["url_id"].duplicated().any():
        raise ValueError("Split manifest has missing values or duplicate URL ids.")
    if set(manifest["split"]) != {"train", "validation", "test"}:
        raise ValueError("Split manifest must contain train, validation and test.")
    if manifest.groupby("group_key")["split"].nunique().max() != 1:
        raise ValueError("A domain group crosses split boundaries.")
    return {name: int((manifest["split"] == name).sum()) for name in ["train", "validation", "test"]}


def select_allowed_rows(chunk, manifest_part, splits=("train", "validation")):
    """Check a chunk lines up with the manifest, then keep only the wanted splits."""
    if len(chunk) != len(manifest_part):
        raise ValueError("Feature table and split manifest have different row counts.")
    ids = chunk["url"].map(url_id).to_numpy()
    if not np.array_equal(ids, manifest_part["url_id"].to_numpy()):
        raise ValueError("Feature rows no longer align with the split manifest.")
    selected = {}
    for name in splits:
        mask = (manifest_part["split"] == name).to_numpy()
        rows = chunk[mask].copy()
        rows["url_id"] = ids[mask]
        rows["group_key"] = manifest_part["group_key"].to_numpy()[mask]
        selected[name] = rows
    return selected


def load_splits(splits, feature_path=FEATURE_INPUT, manifest_path=SPLIT_MANIFEST,
                feature_sha256=FEATURE_SHA256, manifest_sha256=MANIFEST_SHA256, chunk_size=CHUNK_SIZE):
    """Read the feature table in chunks and keep only the requested splits."""
    if file_sha256(feature_path) != feature_sha256:
        raise ValueError("Feature table hash changed since the split was made.")
    if file_sha256(manifest_path) != manifest_sha256:
        raise ValueError("Split manifest hash changed since the split was made.")
    manifest = pd.read_csv(manifest_path, dtype="string", keep_default_na=False)
    counts = validate_manifest(manifest)

    parts = {name: [] for name in splits}
    start = 0
    cols = ["url", "type", "target"] + list(FEATURE_NAMES)
    for chunk in pd.read_csv(feature_path, usecols=cols, keep_default_na=False, chunksize=chunk_size):
        picked = select_allowed_rows(chunk, manifest.iloc[start:start + len(chunk)], splits)
        for name in splits:
            parts[name].append(picked[name])
        start += len(chunk)
    if start != len(manifest):
        raise ValueError("Feature table and split manifest have different row counts.")

    selected = {}
    for name in splits:
        selected[name] = pd.concat(parts[name], ignore_index=True)
        if len(selected[name]) != counts[name]:
            raise ValueError(f"{name} row count differs from the manifest.")
    return selected, counts


def load_train_val(feature_path=FEATURE_INPUT, manifest_path=SPLIT_MANIFEST,
                   feature_sha256=FEATURE_SHA256, manifest_sha256=MANIFEST_SHA256, chunk_size=CHUNK_SIZE):
    """Load train and validation only (test rows are skipped)."""
    data, counts = load_splits(("train", "validation"), feature_path, manifest_path,
                               feature_sha256, manifest_sha256, chunk_size)
    return data["train"], data["validation"], counts


def make_models():
    return {
        "logistic_regression": Pipeline([
            ("scale", StandardScaler()),
            ("classifier", LogisticRegression(solver="liblinear", max_iter=500,
                class_weight="balanced", random_state=RANDOM_SEED)),
        ]),
        "decision_tree": DecisionTreeClassifier(max_depth=12, min_samples_leaf=100,
            class_weight="balanced", random_state=RANDOM_SEED),
        "random_forest": RandomForestClassifier(**FOREST_SETTINGS),
    }


def score_predictions(y_true, prob, threshold):
    """Accuracy, precision, recall, F1 and TN/FP/FN/TP for a given threshold."""
    labels = np.asarray(list(y_true), dtype=np.int8)
    probabilities = np.asarray(list(prob), dtype=np.float64)
    if len(labels) != len(probabilities) or not np.isfinite(probabilities).all():
        raise ValueError("Labels and probabilities don't match up.")
    pred = (probabilities >= threshold).astype(np.int8)
    tn, fp, fn, tp = confusion_matrix(labels, pred, labels=[0, 1]).ravel()
    return {
        "threshold": float(threshold),
        "accuracy": float(accuracy_score(labels, pred)),
        "precision": float(precision_score(labels, pred, zero_division=0)),
        "recall": float(recall_score(labels, pred, zero_division=0)),
        "f1": float(f1_score(labels, pred, zero_division=0)),
        "true_negative": int(tn),
        "false_positive": int(fp),
        "false_negative": int(fn),
        "true_positive": int(tp),
    }


def get_prob(model, X):
    """Probability of 'dangerous' from a fitted model."""
    # score_predictions checks the returned probabilities.
    with np.errstate(over="ignore", divide="ignore", invalid="ignore"):
        return model.predict_proba(X)[:, 1]


def compare_models(train, val):
    """Train each model on train and score it on validation (overall, per threshold, per label)."""
    X_train = train.loc[:, FEATURE_NAMES]
    y_train = train["target"].to_numpy(dtype=np.int8)
    X_val = val.loc[:, FEATURE_NAMES]
    y_val = val["target"].to_numpy(dtype=np.int8)

    train_rows = []
    val_rows = []
    threshold_rows = []
    group_rows = []
    for name, model in make_models().items():
        model.fit(X_train, y_train)
        scores = score_predictions(y_train, get_prob(model, X_train), 0.50)
        train_rows.append({"model": name, **scores})

        probabilities = get_prob(model, X_val)
        val_rows.append({"model": name, **score_predictions(y_val, probabilities, 0.50)})
        for threshold in THRESHOLDS:
            threshold_rows.append({"model": name, **score_predictions(y_val, probabilities, threshold)})

        pred = probabilities >= 0.50
        for source in ["benign", "phishing", "malware", "defacement"]:
            mask = (val["type"] == source).to_numpy()
            if not mask.any():
                continue
            actual = y_val[mask]
            guess = pred[mask]
            group_rows.append({
                "model": name,
                "source_type": source,
                "rows": int(mask.sum()),
                "correct": int((guess == actual).sum()),
                "missed_dangerous": int(((actual == 1) & ~guess).sum()),
                "false_alarms": int(((actual == 0) & guess).sum()),
            })
    return pd.DataFrame(train_rows), pd.DataFrame(val_rows), pd.DataFrame(threshold_rows), pd.DataFrame(group_rows)


def run_stage5(report_dir=REPORT_DIR):
    """Run Stage 5 and save the comparison tables and the chosen model/threshold."""
    train, val, counts = load_train_val()
    train_res, val_res, thr_res, group_res = compare_models(train, val)
    report_dir.mkdir(parents=True, exist_ok=True)
    train_res.to_csv(report_dir / "train_metrics.csv", index=False)
    val_res.to_csv(report_dir / "validation_metrics.csv", index=False)
    thr_res.to_csv(report_dir / "threshold_tradeoffs.csv", index=False)
    group_res.to_csv(report_dir / "validation_subgroups.csv", index=False)

    chosen = thr_res[(thr_res["model"] == SELECTED_MODEL) & (thr_res["threshold"] == SELECTED_THRESHOLD)]
    summary = {
        "feature_names": list(FEATURE_NAMES),
        "split_counts": counts,
        "models": list(make_models()),
        "random_forest_settings": FOREST_SETTINGS,
        "thresholds_reviewed": list(THRESHOLDS),
        "selected_model": SELECTED_MODEL,
        "selected_threshold": SELECTED_THRESHOLD,
        "selected_validation_metrics": chosen.iloc[0].to_dict(),
    }
    text = json.dumps(summary, indent=2, ensure_ascii=False)
    (report_dir / "validation_summary.json").write_text(text + "\n", encoding="utf-8")
    return summary


if __name__ == "__main__":
    print(json.dumps(run_stage5(), indent=2, ensure_ascii=False))
