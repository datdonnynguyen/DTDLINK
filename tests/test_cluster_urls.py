"""Stage 6 population isolation, label exclusion and numerical evidence checks."""
import numpy as np
import pandas as pd
import pytest
from threadpoolctl import threadpool_limits

from dtdlink_ml.cluster_urls import (
    select_population, load_population, prepare_features, compare_k, choose_k,
    build_profiles, make_kmeans, fit_checked,
)
from dtdlink_ml.feature_extraction import FEATURE_NAMES, file_sha256
from dtdlink_ml.train_classifier import _url_id


def population():
    rng = np.random.default_rng(7)
    frame = pd.DataFrame(0., index=range(40), columns=FEATURE_NAMES)
    frame["url_length"] = np.r_[rng.uniform(10, 15, 20), rng.uniform(100, 105, 20)]
    frame["host_length"] = np.r_[rng.uniform(2, 4, 20), rng.uniform(20, 24, 20)]
    frame["url"] = [f"https://d{i}.example/x" for i in range(40)]
    frame["url_id"] = frame.url.map(_url_id)
    frame["group_key"] = [f"domain:d{i}.example" for i in range(40)]
    frame["target"] = 1
    frame["type"] = "phishing"
    return frame


def test_filter_excludes_benign_validation_and_test():
    frame = population().iloc[:4].copy()
    frame.loc[1, "target"] = 0
    membership = frame[["url_id", "group_key"]].copy()
    membership["split"] = ["train", "train", "validation", "test"]
    # Values outside train must never affect feature selection or scaling.
    frame.loc[2:, "url_length"] = np.nan
    selected = select_population(frame, membership)
    assert selected.url_id.tolist() == [frame.iloc[0].url_id]
    assert selected.target.eq(1).all()


def test_filter_rejects_row_reordering():
    frame = population()
    membership = frame[["url_id", "group_key"]].copy()
    membership["split"] = "train"
    with pytest.raises(ValueError, match="align"):
        select_population(frame.iloc[::-1], membership)


def test_loader_checks_hashes_and_only_returns_class_train(tmp_path):
    frame = population().iloc[:4].copy()
    membership = frame[["url_id", "group_key"]].copy()
    membership["split"] = ["train", "train", "validation", "test"]
    frame.loc[1, "target"] = 0
    a, b = tmp_path / "features.csv", tmp_path / "manifest.csv"
    frame.to_csv(a, index=False); membership.to_csv(b, index=False)
    selected, counts = load_population(a, b, file_sha256(a), file_sha256(b))
    assert len(selected) == 1 and counts == {"train": 2, "validation": 1, "test": 1}
    with pytest.raises(ValueError, match="manifest hash"):
        load_population(a, b, file_sha256(a), "incorrect")


def test_whitelist_removes_constants_and_metadata_is_invariant():
    frame = population()
    features, scaled, _, removed = prepare_features(frame)
    assert features.columns.tolist() == ["url_length", "host_length"]
    assert len(removed) == 34
    frame["type"] = "arbitrary label"
    frame["target"] = 999
    frame["extra_numeric_label"] = np.arange(len(frame))
    changed = prepare_features(frame)[1]
    np.testing.assert_array_equal(scaled, changed)
    np.testing.assert_allclose(scaled.mean(axis=0), 0, atol=1e-12)


def test_nonfinite_features_and_all_constants_are_rejected():
    frame = population()
    frame.loc[0, "url_length"] = np.inf
    with pytest.raises(ValueError, match="finite"):
        prepare_features(frame)
    frame.loc[:, list(FEATURE_NAMES)] = 0
    with pytest.raises(ValueError, match="varying"):
        prepare_features(frame)


def test_k_selection_ignores_invalid_scores_and_breaks_ties_smallest():
    table = pd.DataFrame({"k": [4, 3, 2], "silhouette": [np.nan, .6, .6]})
    assert choose_k(table) == 2
    with pytest.raises(ValueError, match="valid silhouette"):
        choose_k(table.iloc[:1])


def test_real_clusters_are_reproducible_and_profiles_reconcile():
    frame = population()
    features, scaled, _, _ = prepare_features(frame)
    with threadpool_limits(limits=1):
        table, models, sample = compare_k(scaled, ks=(2, 3), sample_size=40)
        assert choose_k(table) == 2
        model = models[2]
        np.testing.assert_array_equal(model.labels_, make_kmeans(2).fit_predict(scaled))
    assert len(sample) == 40
    assert len(set(model.labels_[:20])) == len(set(model.labels_[20:])) == 1
    assert model.labels_[0] != model.labels_[20]
    profiles, examples, composition = build_profiles(frame, features, scaled, model)
    assert profiles.groupby("cluster")["size"].first().sum() == 40
    assert len(examples) == 6 and composition["count"].sum() == 40
    for name in features:
        rows = profiles.loc[profiles.feature.eq(name)]
        assert np.average(rows.cluster_mean, weights=rows["size"]) == pytest.approx(features[name].mean())


def test_independent_inertia_check_rejects_bad_library_result(monkeypatch):
    import dtdlink_ml.cluster_urls as module
    scaled = prepare_features(population())[1]
    with threadpool_limits(limits=1):
        model = make_kmeans(2).fit(scaled)
    model.inertia_ = float("nan")
    class BadModel:
        def fit(self, data):
            return model
    monkeypatch.setattr(module, "make_kmeans", lambda k, seed: BadModel())
    with pytest.raises(ValueError, match="numerical"):
        fit_checked(scaled, 2)
