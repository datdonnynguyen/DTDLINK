"""Reproducible Stage 2 cleaning pipeline for DTDLINK.

The pipeline keeps the raw CSV unchanged, trims only URL edge whitespace,
quarantines conflicting labels, removes exact duplicates, and creates the
documented binary target.

Run from the project root:
    .venv/bin/python src/dtdlink_ml/data_cleaning.py
"""

import hashlib
import json
from pathlib import Path
from typing import Optional, Union

import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "data/raw/malicious_phish.csv"
CLEANED = ROOT / "data/interim/malicious_phish_cleaned.csv"
CONFLICTS = ROOT / "reports/cleaning/conflicting_records.csv"
AUDIT = ROOT / "reports/cleaning/cleaning_audit.json"
EXPECTED_RAW_SHA256 = (
    "d83ce942075dd63ed4d11560cfdcd9d512caa3d680e292f22cab484e8f074d01"
)
EXPECTED_COLUMNS = ["url", "type"]
TARGET_MAPPING = {
    "benign": 0,
    "phishing": 1,
    "malware": 1,
    "defacement": 1,
}


def file_sha256(path: Path) -> str:
    """Calculate a file fingerprint without changing the file."""

    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def validate_raw_contract(dataframe: pd.DataFrame) -> None:
    """Reject input that does not match the Stage 1 data contract."""

    actual_columns = list(dataframe.columns)
    if actual_columns != EXPECTED_COLUMNS:
        raise ValueError(
            f"Expected columns {EXPECTED_COLUMNS}, received {actual_columns}."
        )

    for column in EXPECTED_COLUMNS:
        missing_mask = dataframe[column].isna()
        blank_mask = dataframe[column].astype("string").str.strip().eq("")
        invalid_count = int((missing_mask | blank_mask.fillna(False)).sum())
        if invalid_count:
            raise ValueError(
                f"Column '{column}' contains {invalid_count} missing or blank values."
            )

    observed_labels = set(dataframe["type"].unique().tolist())
    unexpected_labels = sorted(observed_labels - set(TARGET_MAPPING))
    if unexpected_labels:
        raise ValueError(f"Unexpected type labels: {unexpected_labels}.")


def add_binary_target(dataframe: pd.DataFrame) -> pd.DataFrame:
    """Return a copy with the approved benign/dangerous target mapping."""

    validate_raw_contract(dataframe)
    working = dataframe.copy()
    working["target"] = working["type"].map(TARGET_MAPPING).astype("int8")
    return working


def trim_url_edges(dataframe: pd.DataFrame) -> tuple[pd.DataFrame, int]:
    """Trim whitespace only at the start and end of each URL."""

    trimmed = dataframe.copy()
    cleaned_urls = trimmed["url"].str.strip()
    changed_count = int((cleaned_urls != trimmed["url"]).sum())
    trimmed["url"] = cleaned_urls
    return trimmed, changed_count


def separate_label_conflicts(
    dataframe: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame, int]:
    """Quarantine every row whose URL has more than one source label."""

    label_counts = dataframe.groupby("url")["type"].nunique()
    conflict_urls = label_counts[label_counts > 1].index
    conflict_mask = dataframe["url"].isin(conflict_urls)

    conflicts = dataframe.loc[conflict_mask].copy()
    remaining = dataframe.loc[~conflict_mask].copy()
    return remaining, conflicts, int(len(conflict_urls))


def remove_exact_duplicates(
    dataframe: pd.DataFrame,
) -> tuple[pd.DataFrame, int]:
    """Keep the first occurrence of each identical URL-label pair."""

    duplicate_mask = dataframe.duplicated(subset=["url", "type"], keep="first")
    duplicate_count = int(duplicate_mask.sum())
    deduplicated = dataframe.loc[~duplicate_mask].copy()
    return deduplicated, duplicate_count


def count_values(series: pd.Series) -> dict:
    """Return deterministic JSON-friendly value counts."""

    return {
        str(value): int(count)
        for value, count in series.value_counts().sort_index().items()
    }


def load_and_prepare_dataset(
    raw_path: Union[str, Path] = RAW,
    expected_sha256: Optional[str] = EXPECTED_RAW_SHA256,
) -> tuple[pd.DataFrame, dict]:
    """Read raw strings, validate their contract, and add target in memory."""

    path = Path(raw_path)
    observed_sha256 = file_sha256(path)
    if expected_sha256 is not None and observed_sha256 != expected_sha256:
        raise ValueError(
            "Raw CSV SHA-256 does not match the Stage 1 fingerprint; "
            "refusing to continue."
        )

    raw = pd.read_csv(
        path,
        dtype="string",
        keep_default_na=False,
        na_filter=False,
        skip_blank_lines=False,
        encoding="utf-8",
    )
    working = add_binary_target(raw)

    summary = {
        "raw_path": str(path),
        "raw_sha256": observed_sha256,
        "rows_before": int(len(raw)),
        "rows_after": int(len(working)),
        "columns_before": list(raw.columns),
        "columns_after": list(working.columns),
        "type_counts": count_values(raw["type"]),
        "target_counts": count_values(working["target"]),
        "rows_removed": int(len(raw) - len(working)),
    }
    return working, summary


def run_cleaning_pipeline(
    raw_path: Union[str, Path] = RAW,
    cleaned_path: Union[str, Path] = CLEANED,
    conflicts_path: Union[str, Path] = CONFLICTS,
    audit_path: Union[str, Path] = AUDIT,
    expected_sha256: Optional[str] = EXPECTED_RAW_SHA256,
) -> tuple[pd.DataFrame, dict]:
    """Run all Stage 2 rules and save deterministic outputs."""

    raw_path = Path(raw_path)
    cleaned_path = Path(cleaned_path)
    conflicts_path = Path(conflicts_path)
    audit_path = Path(audit_path)

    raw_hash_before = file_sha256(raw_path)
    if expected_sha256 is not None and raw_hash_before != expected_sha256:
        raise ValueError(
            "Raw CSV SHA-256 does not match the Stage 1 fingerprint; "
            "refusing to continue."
        )

    raw = pd.read_csv(
        raw_path,
        dtype="string",
        keep_default_na=False,
        na_filter=False,
        skip_blank_lines=False,
        encoding="utf-8",
    )
    validate_raw_contract(raw)

    working = raw.copy()
    working.insert(0, "source_record_number", range(1, len(working) + 1))
    working, trimmed_url_count = trim_url_edges(working)
    working["target"] = working["type"].map(TARGET_MAPPING).astype("int8")

    after_conflicts, conflicts, conflict_url_count = separate_label_conflicts(
        working
    )
    deduplicated, duplicate_count = remove_exact_duplicates(after_conflicts)

    cleaned = deduplicated[["url", "type", "target"]].reset_index(drop=True)
    conflicts = conflicts[
        ["source_record_number", "url", "type", "target"]
    ].reset_index(drop=True)

    if cleaned["url"].duplicated().any():
        raise ValueError("Cleaned output still contains duplicate URLs.")
    if cleaned[["url", "type"]].duplicated().any():
        raise ValueError("Cleaned output still contains exact duplicates.")

    cleaned_path.parent.mkdir(parents=True, exist_ok=True)
    conflicts_path.parent.mkdir(parents=True, exist_ok=True)
    audit_path.parent.mkdir(parents=True, exist_ok=True)

    cleaned.to_csv(cleaned_path, index=False, lineterminator="\n")
    conflicts.to_csv(conflicts_path, index=False, lineterminator="\n")

    raw_hash_after = file_sha256(raw_path)
    if raw_hash_after != raw_hash_before:
        raise RuntimeError("Raw CSV changed while cleaning was running.")

    audit = {
        "input": {
            "path": str(raw_path),
            "sha256_before": raw_hash_before,
            "sha256_after": raw_hash_after,
            "rows": int(len(raw)),
            "columns": list(raw.columns),
            "type_counts": count_values(raw["type"]),
            "target_counts": count_values(raw["type"].map(TARGET_MAPPING)),
        },
        "rules": {
            "edge_whitespace": {
                "action": "trim",
                "urls_changed": trimmed_url_count,
                "rows_after": int(len(working)),
            },
            "label_conflicts": {
                "action": "quarantine_all_rows",
                "conflicting_urls": conflict_url_count,
                "rows_removed": int(len(conflicts)),
                "rows_after": int(len(after_conflicts)),
            },
            "exact_duplicates": {
                "action": "keep_first_url_type_pair",
                "rows_removed": duplicate_count,
                "rows_after": int(len(cleaned)),
            },
            "other_anomalies": {
                "action": "retain",
                "details": [
                    "Unicode",
                    "control characters",
                    "extreme length",
                    "diagnostic parse issues",
                ],
            },
        },
        "output": {
            "cleaned_path": str(cleaned_path),
            "cleaned_sha256": file_sha256(cleaned_path),
            "conflicts_path": str(conflicts_path),
            "conflicts_sha256": file_sha256(conflicts_path),
            "rows": int(len(cleaned)),
            "columns": list(cleaned.columns),
            "type_counts": count_values(cleaned["type"]),
            "target_counts": count_values(cleaned["target"]),
            "unique_urls": int(cleaned["url"].nunique()),
        },
    }

    with audit_path.open("w", encoding="utf-8") as stream:
        json.dump(audit, stream, indent=2, ensure_ascii=False, sort_keys=True)
        stream.write("\n")

    return cleaned, audit


def main() -> None:
    """Run the complete Stage 2 pipeline and print its audit summary."""

    _, audit = run_cleaning_pipeline()
    print(json.dumps(audit, indent=2, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
