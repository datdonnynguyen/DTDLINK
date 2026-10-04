"""Stage 5 checks for locked membership, train-only fitting and metrics."""

import hashlib

import numpy as np
import pandas as pd
import pytest

from dtdlink_ml.feature_extraction import FEATURE_NAMES, file_sha256
from dtdlink_ml.train_classifier import (
    load_allowed_data,
    make_models,
    score_predictions,
    select_allowed_rows,
    validate_manifest,
)


def _small_files(tmp_path):
    rows = []
    memberships = []
    examples = (
        ("https://safe.example/a", "benign", 0, "train", "example"),
        ("https://bad.example/b", "phishing", 1, "train", "example"),
        ("https://other.test/a", "benign", 0, "validation", "other.test"),
        ("https://danger.test/a", "malware", 1, "validation", "danger.test"),
        ("https://hidden.test/a", "phishing", 1, "test", "hidden.test"),
    )
    for url, source_type, target, split, group in examples:
        rows.append({"url": url, "type": source_type, "target": target, **{name: 0 for name in FEATURE_NAMES}})
        memberships.append(
            {
                "url_id": hashlib.sha256(url.encode()).hexdigest(),
                "group_key": f"domain:{group}",
                "split": split,
            }
        )
    feature_path = tmp_path / "features.csv"
    manifest_path = tmp_path / "manifest.csv"
    pd.DataFrame(rows).to_csv(feature_path, index=False)
    pd.DataFrame(memberships).to_csv(manifest_path, index=False)
    return feature_path, manifest_path


def test_loader_returns_only_train_and_validation(tmp_path):
    feature_path, manifest_path = _small_files(tmp_path)
    train, validation, counts = load_allowed_data(
        feature_path,
        manifest_path,
        file_sha256(feature_path),
        file_sha256(manifest_path),
        chunk_size=2,
    )
    assert counts == {"train": 2, "validation": 2, "test": 1}
    assert len(train) == len(validation) == 2
    assert not train["url"].str.contains("hidden").any()
    assert not validation["url"].str.contains("hidden").any()


def test_loader_rejects_changed_locked_hash(tmp_path):
    feature_path, manifest_path = _small_files(tmp_path)
    with pytest.raises(ValueError, match="manifest hash changed"):
        load_allowed_data(feature_path, manifest_path, file_sha256(feature_path), "wrong")


def test_loader_rejects_reordered_rows(tmp_path):
    feature_path, manifest_path = _small_files(tmp_path)
    frame = pd.read_csv(feature_path)
    frame.iloc[[1, 0, 2, 3, 4]].to_csv(feature_path, index=False)
    with pytest.raises(ValueError, match="no longer align"):
        load_allowed_data(
            feature_path,
            manifest_path,
            file_sha256(feature_path),
            file_sha256(manifest_path),
            chunk_size=2,
        )


def test_manifest_rejects_group_leakage(tmp_path):
    _, manifest_path = _small_files(tmp_path)
    manifest = pd.read_csv(manifest_path, dtype="string")
    manifest.loc[2, "group_key"] = "domain:example"
    with pytest.raises(ValueError, match="crosses split"):
        validate_manifest(manifest)


def test_selection_never_returns_test_rows(tmp_path):
    feature_path, manifest_path = _small_files(tmp_path)
    features = pd.read_csv(feature_path)
    manifest = pd.read_csv(manifest_path, dtype="string")
    selected = select_allowed_rows(features, manifest)
    assert set(selected) == {"train", "validation"}
    assert sum(len(frame) for frame in selected.values()) == 4


def test_metrics_count_false_alarms_and_missed_dangerous():
    result = score_predictions([0, 0, 1, 1], [0.1, 0.8, 0.3, 0.9], 0.5)
    assert (result["true_negative"], result["false_positive"], result["false_negative"], result["true_positive"]) == (1, 1, 1, 1)
    assert result["precision"] == result["recall"] == result["f1"] == 0.5


def test_two_baselines_and_optional_forest_are_defined():
    models = make_models()
    assert set(models) == {"logistic_regression", "decision_tree", "random_forest"}
    assert models["logistic_regression"].named_steps["scale"].__class__.__name__ == "StandardScaler"
    assert models["decision_tree"].max_depth == 12
    assert models["random_forest"].n_estimators == 100
    assert models["random_forest"].random_state == 42
