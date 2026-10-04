"""Tests for the Stage 2 raw-data contract and target mapping."""

import hashlib

import pandas as pd
import pytest

from dtdlink_ml.data_cleaning import (
    add_binary_target,
    load_and_prepare_dataset,
    remove_exact_duplicates,
    run_cleaning_pipeline,
    separate_label_conflicts,
    trim_url_edges,
    validate_raw_contract,
)


def test_add_binary_target_keeps_rows_and_original_columns() -> None:
    raw = pd.DataFrame(
        {
            "url": ["example.test", "login.test", "file.test", "page.test"],
            "type": ["benign", "phishing", "malware", "defacement"],
        },
        dtype="string",
    )

    prepared = add_binary_target(raw)

    assert prepared["target"].tolist() == [0, 1, 1, 1]
    assert prepared[["url", "type"]].equals(raw)
    assert len(prepared) == len(raw)
    assert list(raw.columns) == ["url", "type"]


@pytest.mark.parametrize(
    "dataframe",
    [
        pd.DataFrame({"url": ["example.test"]}, dtype="string"),
        pd.DataFrame(
            {"type": ["benign"], "url": ["example.test"]}, dtype="string"
        ),
        pd.DataFrame(
            {
                "url": ["example.test"],
                "type": ["benign"],
                "extra": ["unexpected"],
            },
            dtype="string",
        ),
    ],
)
def test_validate_raw_contract_rejects_wrong_schema(
    dataframe: pd.DataFrame,
) -> None:
    with pytest.raises(ValueError, match="Expected columns"):
        validate_raw_contract(dataframe)


def test_validate_raw_contract_rejects_unknown_label() -> None:
    dataframe = pd.DataFrame(
        {"url": ["example.test"], "type": ["unknown"]}, dtype="string"
    )

    with pytest.raises(ValueError, match="Unexpected type labels"):
        validate_raw_contract(dataframe)


@pytest.mark.parametrize("invalid_url", ["", "   ", pd.NA])
def test_validate_raw_contract_rejects_missing_or_blank_url(
    invalid_url: object,
) -> None:
    dataframe = pd.DataFrame(
        {"url": [invalid_url], "type": ["benign"]}, dtype="string"
    )

    with pytest.raises(ValueError, match="missing or blank"):
        validate_raw_contract(dataframe)


def test_loader_rejects_a_changed_source_fingerprint(tmp_path) -> None:
    csv_path = tmp_path / "input.csv"
    csv_path.write_text("url,type\nexample.test,benign\n", encoding="utf-8")
    actual_hash = hashlib.sha256(csv_path.read_bytes()).hexdigest()

    with pytest.raises(ValueError, match="SHA-256"):
        load_and_prepare_dataset(csv_path, expected_sha256="0" * 64)

    _, summary = load_and_prepare_dataset(
        csv_path,
        expected_sha256=actual_hash,
    )
    assert summary["rows_before"] == summary["rows_after"] == 1
    assert summary["target_counts"] == {"0": 1}


def test_trim_url_edges_changes_only_the_edges() -> None:
    dataframe = pd.DataFrame(
        {
            "url": ["  example.test/path with space  ", "unchanged.test"],
            "type": ["benign", "phishing"],
        },
        dtype="string",
    )

    trimmed, changed_count = trim_url_edges(dataframe)

    assert trimmed["url"].tolist() == [
        "example.test/path with space",
        "unchanged.test",
    ]
    assert changed_count == 1
    assert dataframe.loc[0, "url"].startswith("  ")


def test_separate_label_conflicts_quarantines_every_conflicting_row() -> None:
    dataframe = pd.DataFrame(
        {
            "url": ["conflict.test", "conflict.test", "keep.test"],
            "type": ["benign", "phishing", "malware"],
        },
        dtype="string",
    )

    remaining, conflicts, conflict_url_count = separate_label_conflicts(dataframe)

    assert remaining["url"].tolist() == ["keep.test"]
    assert conflicts["url"].tolist() == ["conflict.test", "conflict.test"]
    assert conflict_url_count == 1


def test_remove_exact_duplicates_keeps_the_first_row() -> None:
    dataframe = pd.DataFrame(
        {
            "source_record_number": [10, 20, 30],
            "url": ["same.test", "same.test", "other.test"],
            "type": ["malware", "malware", "benign"],
        }
    )

    deduplicated, removed_count = remove_exact_duplicates(dataframe)

    assert deduplicated["source_record_number"].tolist() == [10, 30]
    assert removed_count == 1


def test_complete_pipeline_writes_reproducible_outputs(tmp_path) -> None:
    raw_path = tmp_path / "raw.csv"
    cleaned_path = tmp_path / "cleaned.csv"
    conflicts_path = tmp_path / "conflicts.csv"
    audit_path = tmp_path / "audit.json"
    raw_path.write_text(
        "url,type\n"
        "  trim.test  ,benign\n"
        "duplicate.test,malware\n"
        "duplicate.test,malware\n"
        "conflict.test,benign\n"
        "conflict.test,phishing\n",
        encoding="utf-8",
    )
    raw_hash = hashlib.sha256(raw_path.read_bytes()).hexdigest()

    first_cleaned, first_audit = run_cleaning_pipeline(
        raw_path,
        cleaned_path,
        conflicts_path,
        audit_path,
        expected_sha256=raw_hash,
    )
    first_cleaned_bytes = cleaned_path.read_bytes()
    first_audit_bytes = audit_path.read_bytes()

    second_cleaned, second_audit = run_cleaning_pipeline(
        raw_path,
        cleaned_path,
        conflicts_path,
        audit_path,
        expected_sha256=raw_hash,
    )

    assert first_cleaned["url"].tolist() == ["trim.test", "duplicate.test"]
    assert first_audit["rules"]["edge_whitespace"]["urls_changed"] == 1
    assert first_audit["rules"]["label_conflicts"]["rows_removed"] == 2
    assert first_audit["rules"]["exact_duplicates"]["rows_removed"] == 1
    assert cleaned_path.read_bytes() == first_cleaned_bytes
    assert audit_path.read_bytes() == first_audit_bytes
    assert second_cleaned.equals(first_cleaned)
    assert second_audit == first_audit
    assert hashlib.sha256(raw_path.read_bytes()).hexdigest() == raw_hash
