"""Tests for the Stage 4 grouped split and training-only evidence."""

import hashlib

import numpy as np
import pandas as pd

from dtdlink_ml.data_splitting import (
    BOOLEAN_FEATURES,
    SPLIT_NAMES,
    assign_grouped_splits,
    build_domain_profile,
    build_source_quality_profile,
    create_group_keys,
    validate_split,
)
from dtdlink_ml.feature_extraction import FEATURE_NAMES


def _feature_frame() -> pd.DataFrame:
    rows = []
    for domain_index in range(50):
        target = domain_index % 2
        source_type = "benign" if target == 0 else "phishing"
        for url_index in range(2 + domain_index % 3):
            row = {
                "url": f"https://s{url_index}.example{domain_index}.com/path",
                "type": source_type,
                "target": target,
                "registrable_domain": f"example{domain_index}.com",
                "tld": "com",
                "parse_issues": "",
            }
            for feature in FEATURE_NAMES:
                row[feature] = 0
            rows.append(row)
    missing = rows[0].copy()
    missing["url"] = "not a parseable host"
    missing["registrable_domain"] = pd.NA
    missing["target"] = 1
    missing["type"] = "phishing"
    missing["parse_ok"] = 0
    rows.append(missing)
    frame = pd.DataFrame(rows)
    for feature in BOOLEAN_FEATURES:
        frame[feature] = frame[feature].astype("int8")
    return frame


def test_group_key_uses_domain_and_hashed_url_fallback() -> None:
    frame = _feature_frame().iloc[[0, 1, -1]].copy()
    url_ids, group_keys = create_group_keys(frame)

    assert group_keys.iloc[0] == group_keys.iloc[1]
    assert group_keys.iloc[0].startswith("domain:")
    assert group_keys.iloc[2].startswith("url:")
    assert group_keys.iloc[2].endswith(url_ids.iloc[2])


def test_domain_profile_reconciles_rows_and_targets() -> None:
    frame = _feature_frame()
    _, group_keys = create_group_keys(frame)
    profile = build_domain_profile(frame, group_keys)

    assert profile["row_count"].sum() == len(frame)
    assert profile["benign_count"].sum() == int(frame["target"].eq(0).sum())
    assert profile["dangerous_count"].sum() == int(frame["target"].eq(1).sum())
    assert profile["group_key"].is_unique


def test_source_quality_profile_keeps_original_label_groups() -> None:
    frame = _feature_frame()
    profile = build_source_quality_profile(frame)

    assert set(profile["source_type"]) == {"benign", "phishing"}
    assert profile["rows"].sum() == len(frame)
    assert profile.loc[profile["source_type"].eq("benign"), "dangerous_rate"].item() == 0
    assert profile.loc[profile["source_type"].eq("phishing"), "dangerous_rate"].item() == 1


def test_grouped_split_is_reproducible_and_has_zero_domain_overlap() -> None:
    frame = _feature_frame()
    url_ids, group_keys = create_group_keys(frame)

    first, first_method = assign_grouped_splits(frame, group_keys, seed=42)
    second, second_method = assign_grouped_splits(frame, group_keys, seed=42)
    validation = validate_split(frame, url_ids, group_keys, first)

    assert first.equals(second)
    assert first_method == second_method
    assert set(first.unique()) == set(SPLIT_NAMES)
    assert validation["passed"] is True
    assert validation["pairwise_group_overlap"] == {
        "train_validation": 0,
        "train_test": 0,
        "validation_test": 0,
    }

    assignment_counts = (
        pd.DataFrame({"group": group_keys, "split": first})
        .groupby("group")["split"]
        .nunique()
    )
    assert assignment_counts.max() == 1


def test_group_key_does_not_change_when_labels_change() -> None:
    frame = _feature_frame()
    first_url_ids, first_groups = create_group_keys(frame)
    changed = frame.copy()
    changed["target"] = 1 - changed["target"]
    changed["type"] = "malware"
    second_url_ids, second_groups = create_group_keys(changed)

    assert first_url_ids.equals(second_url_ids)
    assert first_groups.equals(second_groups)


def test_url_ids_are_full_sha256_values() -> None:
    frame = _feature_frame().iloc[:3]
    url_ids, _ = create_group_keys(frame)

    assert url_ids.str.fullmatch(r"[0-9a-f]{64}").all()
    assert url_ids.iloc[0] == hashlib.sha256(
        frame.iloc[0]["url"].encode("utf-8")
    ).hexdigest()


def test_split_balance_stays_close_on_representative_groups() -> None:
    frame = _feature_frame()
    _, group_keys = create_group_keys(frame)
    splits, _ = assign_grouped_splits(frame, group_keys, seed=42)

    shares = splits.value_counts(normalize=True)
    assert np.isclose(shares["train"], 0.60, atol=0.12)
    assert np.isclose(shares["validation"], 0.20, atol=0.08)
    assert np.isclose(shares["test"], 0.20, atol=0.08)
