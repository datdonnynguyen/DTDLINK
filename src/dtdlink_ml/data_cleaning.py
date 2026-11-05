"""Clean URL records and record removed rows."""

import json
from pathlib import Path

import pandas as pd

from dtdlink_ml.feature_extraction import file_sha256

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "data/raw/malicious_phish.csv"
CLEANED = ROOT / "data/interim/malicious_phish_cleaned.csv"
CONFLICTS = ROOT / "reports/cleaning/conflicting_records.csv"
AUDIT = ROOT / "reports/cleaning/cleaning_audit.json"
EXPECTED_RAW_SHA256 = "d83ce942075dd63ed4d11560cfdcd9d512caa3d680e292f22cab484e8f074d01"
EXPECTED_COLUMNS = ["url", "type"]
TARGET_MAPPING = {"benign": 0, "phishing": 1, "malware": 1, "defacement": 1}


def count_values(col):
    counts = {}
    for value, count in col.value_counts().sort_index().items():
        counts[str(value)] = int(count)
    return counts


def check_raw_data(df):
    """Stop if the raw data has wrong columns, empty cells or unknown labels."""
    if list(df.columns) != EXPECTED_COLUMNS:
        raise ValueError(f"Expected columns {EXPECTED_COLUMNS}, received {list(df.columns)}.")
    for col in EXPECTED_COLUMNS:
        values = df[col].astype("string").fillna("").str.strip()
        blank = int((values == "").sum())
        if blank > 0:
            raise ValueError(f"Column '{col}' contains {blank} missing or blank values.")
    unknown = sorted(set(df["type"]) - set(TARGET_MAPPING))
    if unknown:
        raise ValueError(f"Unexpected type labels: {unknown}.")


def add_binary_target(df):
    """Add the 0/1 target column (benign = 0, everything else = 1)."""
    check_raw_data(df)
    df = df.copy()
    df["target"] = df["type"].map(TARGET_MAPPING).astype("int8")
    return df


def trim_url_edges(df):
    """Remove spaces at the start/end of each URL; returns the data and how many changed."""
    df = df.copy()
    stripped = df["url"].str.strip()
    changed = int((stripped != df["url"]).sum())
    df["url"] = stripped
    return df, changed


def separate_label_conflicts(df):
    """Take out every row of a URL that has two different labels."""
    n_labels = df.groupby("url")["type"].nunique()
    bad_urls = n_labels[n_labels > 1].index
    is_bad = df["url"].isin(bad_urls)
    return df[~is_bad].copy(), df[is_bad].copy(), len(bad_urls)


def remove_exact_duplicates(df):
    """Keep only the first copy of each identical (url, type) row."""
    duplicate_mask = df.duplicated(subset=["url", "type"], keep="first")
    return df[~duplicate_mask].copy(), int(duplicate_mask.sum())


def read_raw(path, expected_sha256=None):
    """Read the raw CSV as text, after checking its SHA-256 if one is given."""
    sha256 = file_sha256(path)
    if expected_sha256 is not None and sha256 != expected_sha256:
        raise ValueError("Raw CSV SHA-256 does not match the expected value.")
    # keep text like "NA" or "null" as it is
    df = pd.read_csv(path, dtype="string", keep_default_na=False, na_filter=False,
                     skip_blank_lines=False, encoding="utf-8")
    return df, sha256


def run_cleaning_pipeline(raw_path=RAW, cleaned_path=CLEANED, conflicts_path=CONFLICTS,
                          audit_path=AUDIT, expected_sha256=EXPECTED_RAW_SHA256):
    """Run the Stage 2 cleaning steps and save the cleaned CSV, conflicts and audit."""
    raw_path = Path(raw_path)
    cleaned_path = Path(cleaned_path)
    conflicts_path = Path(conflicts_path)
    audit_path = Path(audit_path)

    raw, raw_hash = read_raw(raw_path, expected_sha256)
    df = add_binary_target(raw)
    df.insert(0, "source_record_number", range(1, len(df) + 1))
    df, n_trimmed = trim_url_edges(df)
    no_conflicts, conflicts, conflict_count = separate_label_conflicts(df)
    unique_rows, duplicate_count = remove_exact_duplicates(no_conflicts)

    cleaned = unique_rows[["url", "type", "target"]].reset_index(drop=True)
    conflicts = conflicts[["source_record_number", "url", "type", "target"]].reset_index(drop=True)
    cleaned_path.parent.mkdir(parents=True, exist_ok=True)
    conflicts_path.parent.mkdir(parents=True, exist_ok=True)
    audit_path.parent.mkdir(parents=True, exist_ok=True)
    cleaned.to_csv(cleaned_path, index=False, lineterminator="\n")
    conflicts.to_csv(conflicts_path, index=False, lineterminator="\n")

    audit = {
        "input": {
            "path": str(raw_path),
            "sha256": raw_hash,
            "rows": len(raw),
            "type_counts": count_values(raw["type"]),
            "target_counts": count_values(df["target"]),
        },
        "rules": {
            "edge_whitespace": {"action": "trim", "urls_changed": n_trimmed},
            "label_conflicts": {
                "action": "remove all rows of the URL",
                "conflicting_urls": conflict_count,
                "rows_removed": len(conflicts),
                "rows_after": len(no_conflicts),
            },
            "exact_duplicates": {"action": "keep first", "rows_removed": duplicate_count,
                                 "rows_after": len(cleaned)},
        },
        "output": {
            "cleaned_path": str(cleaned_path),
            "cleaned_sha256": file_sha256(cleaned_path),
            "conflicts_path": str(conflicts_path),
            "rows": len(cleaned),
            "type_counts": count_values(cleaned["type"]),
            "target_counts": count_values(cleaned["target"]),
        },
    }
    audit_path.write_text(json.dumps(audit, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")
    return cleaned, audit


if __name__ == "__main__":
    _, audit = run_cleaning_pipeline()
    print(json.dumps(audit, indent=2, ensure_ascii=False, sort_keys=True))
