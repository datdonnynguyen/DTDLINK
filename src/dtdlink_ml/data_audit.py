"""Read-only Stage 1 audit. No cleaning, target mapping, splitting or training.

Run from the project root:
    .venv/bin/python src/dtdlink_ml/data_audit.py
"""

import csv
import hashlib
import json
import platform
import re
import zipfile
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlsplit

import pandas as pd


# ============================================================================
# SECTION 1 - AUDIT PATHS AND SETTINGS
#
# Uppercase values are shared settings. Keeping them here makes adjustable
# values easy to find without searching through the functions below.
# ============================================================================
ROOT = Path(__file__).resolve().parents[2]
ARCHIVE = ROOT / "Week-08/Assessment/Basic_Datasets.zip"
MEMBER = "Basic_Datasets/Phishing URL Detection/malicious_phish.csv"
RAW = ROOT / "data/raw/malicious_phish.csv"
OUT = ROOT / "reports/audit"

EXPECTED_COLUMNS = ["url", "type"]
MISSING_TOKENS = ["na", "n/a", "null", "none", "nan", "unknown", "?"]
SCHEME_PATTERN = r"^[A-Za-z][A-Za-z0-9+.-]*://"
LONG_URL_THRESHOLD = 2048
LENGTH_QUANTILES = [0, 0.25, 0.5, 0.75, 0.95, 1]
EXAMPLE_QUANTILES = [0.25, 0.5, 0.75]
ANOMALY_NAMES = [
    "any_whitespace",
    "control_character",
    "non_ascii",
    "length_over_2048",
    "diagnostic_parse_issue",
]


# ============================================================================
# SECTION 2 - LOAD AND PROTECT THE RAW DATA
#
# Purpose: read the correct CSV from the archive, verify its SHA-256 fingerprint,
# and preserve empty strings and missing-like tokens exactly as supplied.
# ============================================================================
def sha256(data: bytes) -> str:
    """Return the SHA-256 fingerprint of some bytes."""

    return hashlib.sha256(data).hexdigest()


def load_raw_dataset() -> tuple[pd.DataFrame, dict]:
    """Read the course CSV without changing its bytes or text values."""

    archive_bytes = ARCHIVE.read_bytes()
    archive_hash = sha256(archive_bytes)

    with zipfile.ZipFile(ARCHIVE) as archive:
        csv_bytes = archive.read(MEMBER)  # Reading also checks the ZIP CRC.

    csv_hash = sha256(csv_bytes)
    if RAW.exists():
        if sha256(RAW.read_bytes()) != csv_hash:
            raise ValueError(
                "Existing raw CSV differs from archive; refusing overwrite."
            )
    else:
        RAW.parent.mkdir(parents=True, exist_ok=True)
        RAW.write_bytes(csv_bytes)

    # Keep empty strings and NA-like text literal so the audit can count them.
    dataframe = pd.read_csv(
        RAW,
        dtype="string",
        keep_default_na=False,
        na_filter=False,
        skip_blank_lines=False,
        encoding="utf-8",
    )
    assert list(dataframe.columns) == EXPECTED_COLUMNS, (
        "Unexpected schema: review before proceeding."
    )

    source_info = {
        "archive": str(ARCHIVE.relative_to(ROOT)),
        "member": MEMBER,
        "raw": str(RAW.relative_to(ROOT)),
        "archive_sha256": archive_hash,
        "csv_sha256": csv_hash,
        "csv_bytes": len(csv_bytes),
    }
    return dataframe, source_info


# ============================================================================
# SECTION 3 - CHECK DUPLICATES AND LABEL CONFLICTS
#
# A duplicate is a repeated URL or row. A label conflict is one URL assigned to
# multiple labels. This section only detects and counts; it removes nothing.
# ============================================================================
def analyse_duplicates_and_conflicts(dataframe: pd.DataFrame) -> dict:
    """Locate repeated rows, repeated URLs, and URLs with multiple labels."""

    urls = dataframe["url"]
    url_counts = urls.value_counts()
    # Group by both URL and label to find completely duplicated rows.
    pair_counts = dataframe.groupby(["url", "type"], dropna=False).size()
    # Count distinct labels for each URL to find label conflicts.
    labels_per_url = dataframe.groupby("url")["type"].nunique()
    conflict_urls = labels_per_url[labels_per_url > 1].index

    return {
        "urls": urls,
        "url_counts": url_counts,
        "pair_counts": pair_counts,
        "conflict_urls": conflict_urls,
        "conflict_mask": urls.isin(conflict_urls),
    }


def verify_with_csv_reader(
    dataframe: pd.DataFrame,
    labels: pd.Series,
    duplicate_info: dict,
) -> tuple[Counter, dict]:
    """Independently verify key pandas counts with Python's CSV reader."""

    pairs = Counter()
    widths = Counter()

    with RAW.open(encoding="utf-8", newline="") as stream:
        reader = csv.reader(stream)
        assert next(reader) == EXPECTED_COLUMNS
        for row in reader:
            widths[len(row)] += 1
            if len(row) != 2:
                raise ValueError("CSV record does not have two fields.")
            pairs[tuple(row)] += 1

    csv_labels = Counter()
    csv_urls = Counter()
    csv_classes = {}
    for (url, label), count in pairs.items():
        csv_labels[label] += count
        csv_urls[url] += count
        csv_classes.setdefault(url, set()).add(label)

    row_count = len(dataframe)
    assert sum(pairs.values()) == row_count
    assert dict(csv_labels) == {key: int(value) for key, value in labels.items()}
    assert row_count - len(pairs) == int(dataframe.duplicated().sum())
    assert row_count - len(csv_urls) == int(dataframe["url"].duplicated().sum())
    assert sum(len(values) > 1 for values in csv_classes.values()) == len(
        duplicate_info["conflict_urls"]
    )

    return widths, csv_classes


# ============================================================================
# SECTION 4 - CHECK MISSING VALUES
#
# Check several forms of missing-like data without changing any cell.
# ============================================================================
def analyse_missing_values(dataframe: pd.DataFrame) -> dict:
    """Count several forms of missing-like data without modifying any cells."""

    missingness = {}
    for column in dataframe:
        values = dataframe[column]
        missingness[column] = {
            "null": int(values.isna().sum()),
            "empty_string": int(values.eq("").sum()),
            "whitespace_only_nonempty": int(
                (values.ne("") & values.str.fullmatch(r"\s*")).sum()
            ),
            "na_like_token": int(
                values.str.strip().str.lower().isin(MISSING_TOKENS).sum()
            ),
            "leading_or_trailing_whitespace": int(
                values.ne(values.str.strip()).sum()
            ),
        }
    return missingness


# ============================================================================
# SECTION 5 - CHECK URL FORMAT AND PARSING
#
# These checks are diagnostic. Unicode, whitespace, or unusual length does not
# automatically make a URL dangerous or cause it to be removed.
# ============================================================================
def prepare_url_for_parsing(url: str) -> str:
    """Temporarily add // when needed so urlsplit can inspect a hostname."""

    has_scheme = re.match(SCHEME_PATTERN, url)
    if has_scheme or url.startswith("//"):
        return url
    return "//" + url


def analyse_url_format(urls: pd.Series) -> dict:
    """Measure URL text patterns and perform a diagnostic hostname parse."""

    # Each mask is a True/False series showing whether each URL has that signal.
    masks = {
        "http_prefix": urls.str.match(r"(?i)^http://"),
        "https_prefix": urls.str.match(r"(?i)^https://"),
        "no_explicit_scheme": ~urls.str.match(SCHEME_PATTERN),
        "any_whitespace": urls.str.contains(r"\s", regex=True),
        "control_character": urls.str.contains(
            r"[\x00-\x1f\x7f]", regex=True
        ),
        "non_ascii": urls.str.contains(r"[^\x00-\x7f]", regex=True),
        "literal_at_symbol": urls.str.contains("@", regex=False),
        "length_over_2048": urls.str.len().gt(LONG_URL_THRESHOLD),
    }

    hosts = []
    parse_issues = []
    for url in urls:
        try:
            parsed = urlsplit(prepare_url_for_parsing(url))
            hosts.append(parsed.hostname or "")
            parse_issues.append("" if parsed.hostname else "no_hostname")
        except ValueError:
            hosts.append("")
            parse_issues.append("urlsplit_value_error")

    host_series = pd.Series(hosts, dtype="string")
    issue_series = pd.Series(parse_issues, dtype="string")
    masks["diagnostic_parse_issue"] = issue_series.ne("")

    return {
        "masks": masks,
        "host_series": host_series,
        "issue_series": issue_series,
    }


def write_anomaly_records(dataframe: pd.DataFrame, url_info: dict) -> None:
    """Write every record that matches at least one anomaly diagnostic."""

    masks = url_info["masks"]
    anomaly_mask = pd.concat(
        [masks[name] for name in ANOMALY_NAMES], axis=1
    ).any(axis=1)

    records = []
    for index in dataframe.index[anomaly_mask]:
        records.append(
            {
                "record_number": int(index + 1),
                "url": str(dataframe.at[index, "url"]),
                "label": str(dataframe.at[index, "type"]),
                "flags": [
                    name for name in ANOMALY_NAMES if masks[name][index]
                ],
                "parse_issue": str(url_info["issue_series"][index]),
            }
        )
    write_jsonl("anomaly_records", records)


# ============================================================================
# SECTION 6 - PROFILE EACH CLASS AND SELECT EXAMPLES
#
# Separate benign, phishing, malware, and defacement results to reveal where
# each issue is concentrated. Examples use quantiles instead of manual choice.
# ============================================================================
def profile_each_class(
    dataframe: pd.DataFrame,
    labels: pd.Series,
    duplicate_info: dict,
    masks: dict,
) -> list[dict]:
    """Build duplicate, format, and length diagnostics for each source class."""

    urls = duplicate_info["urls"]
    class_profiles = []

    for label in labels.index:
        group_mask = dataframe["type"].eq(label)
        profile = {
            "label": label,
            "rows": int(group_mask.sum()),
            "unique_urls": int(urls[group_mask].nunique()),
            "exact_duplicate_excess": int(dataframe[group_mask].duplicated().sum()),
            "conflict_rows": int(
                (group_mask & duplicate_info["conflict_mask"]).sum()
            ),
        }
        profile.update(
            {
                name: int((mask & group_mask).sum())
                for name, mask in masks.items()
            }
        )

        lengths = urls[group_mask].str.len()
        profile["length"] = {
            str(quantile): float(lengths.quantile(quantile))
            for quantile in LENGTH_QUANTILES
        }
        class_profiles.append(profile)

    return class_profiles


def select_representative_examples(
    dataframe: pd.DataFrame,
    labels: pd.Series,
) -> list[dict]:
    """Select deterministic URL examples near Q1, median, and Q3 per class."""

    examples = []
    for label in labels.index:
        class_rows = dataframe[dataframe["type"].eq(label)]
        lengths = class_rows["url"].str.len()
        chosen_indexes = set()

        for quantile in EXAMPLE_QUANTILES:
            target_length = lengths.quantile(quantile)
            distances = (lengths - target_length).abs().sort_values(kind="stable")
            index = next(
                value for value in distances.index if value not in chosen_indexes
            )
            chosen_indexes.add(index)
            examples.append(
                {
                    "record_number": int(index + 1),
                    "label": label,
                    "length_quantile": quantile,
                    "url": str(dataframe.at[index, "url"]),
                    "length": int(lengths[index]),
                }
            )

    return examples


# ============================================================================
# SECTION 7 - WRITE EVIDENCE AND BUILD THE SUMMARY
#
# JSONL stores detailed records; summary.json stores the aggregate values used
# by the Stage 1 report. build_summary combines results and does not clean data.
# ============================================================================
def write_jsonl(name: str, records: list[dict]) -> None:
    """Write evidence records as one JSON object per line."""

    with (OUT / f"{name}.jsonl").open("w", encoding="utf-8") as stream:
        for record in records:
            stream.write(json.dumps(record, ensure_ascii=True) + "\n")


def build_summary(
    dataframe: pd.DataFrame,
    source_info: dict,
    labels: pd.Series,
    missingness: dict,
    duplicate_info: dict,
    csv_classes: dict,
    csv_widths: Counter,
    url_info: dict,
    class_profiles: list[dict],
) -> dict:
    """Assemble the stable summary structure consumed by the report."""

    row_count = len(dataframe)
    urls = duplicate_info["urls"]
    url_counts = duplicate_info["url_counts"]
    pair_counts = duplicate_info["pair_counts"]
    conflict_urls = duplicate_info["conflict_urls"]
    host_series = url_info["host_series"]
    issue_series = url_info["issue_series"]

    stripped_unique_urls = int(urls.str.strip().nunique())
    valid_hosts = host_series[host_series.ne("")]
    host_counts = valid_hosts.value_counts()

    return {
        "audit_time_utc": datetime.now(timezone.utc).isoformat(),
        "source": source_info,
        "environment": {
            "python": platform.python_version(),
            "pandas": pd.__version__,
        },
        "shape": {"rows": row_count, "columns": len(dataframe.columns)},
        "schema": [
            {
                "column": column,
                "pandas_dtype": str(dataframe[column].dtype),
                "semantic_type": (
                    "URL text" if column == "url" else "categorical label"
                ),
            }
            for column in dataframe
        ],
        "labels": [
            {
                "label": label,
                "rows": int(count),
                "percent": float(100 * count / row_count),
            }
            for label, count in labels.items()
        ],
        "missingness": missingness,
        "duplicates": {
            "unique_complete_rows": int(len(pair_counts)),
            "exact_row_excess": int(dataframe.duplicated().sum()),
            "exact_row_affected": int(dataframe.duplicated(keep=False).sum()),
            "exact_row_groups": int((pair_counts > 1).sum()),
            "unique_urls": int(len(url_counts)),
            "url_excess": int(urls.duplicated().sum()),
            "url_affected": int(urls.duplicated(keep=False).sum()),
            "url_groups": int((url_counts > 1).sum()),
            "additional_url_merges_if_trimmed": int(
                len(url_counts) - stripped_unique_urls
            ),
        },
        "conflicts": {
            "unique_urls": len(conflict_urls),
            "affected_rows": int(duplicate_info["conflict_mask"].sum()),
            "label_combinations": dict(
                Counter(
                    "|".join(sorted(csv_classes[url])) for url in conflict_urls
                )
            ),
        },
        "by_class": class_profiles,
        "diagnostic_host": {
            "unique_nonempty_hosts": int(valid_hosts.nunique()),
            "rows_in_repeated_hosts": int(
                valid_hosts.duplicated(keep=False).sum()
            ),
            "parse_issue_counts": {
                str(key): int(value)
                for key, value in issue_series.value_counts().items()
            },
            "largest_host_row_count": int(host_counts.max()),
        },
        "verification": {
            "independent_csv_checks_passed": True,
            "csv_record_widths": {
                str(key): int(value) for key, value in csv_widths.items()
            },
            "raw_hash_unchanged": sha256(RAW.read_bytes())
            == source_info["csv_sha256"],
            "archive_hash_unchanged": sha256(ARCHIVE.read_bytes())
            == source_info["archive_sha256"],
        },
        "limitations": [
            "No website visited or label independently verified.",
            "No collection dates, label provenance or historical snapshots in these two columns.",
            "Host inspection is diagnostic, not registrable-domain grouping or strict URL validation.",
            "No canonicalization, cleaning, exclusions, relabeling, split or training performed.",
            "Missingness preserves literal strings; null-like tokens counted separately.",
            "Examples illustrate length quartiles, not statistically representative or verified class membership.",
        ],
    }


# ============================================================================
# SECTION 8 - ORCHESTRATE THE COMPLETE AUDIT
#
# run_audit() calls the sections above in order. It is the main entry point used
# by the notebook and terminal command to reproduce Stage 1.
# ============================================================================
def run_audit() -> dict:
    """Run every read-only Stage 1 audit step and return the summary."""

    # Step 1: Prepare the output directory, load data, and verify the source.
    OUT.mkdir(parents=True, exist_ok=True)
    dataframe, source_info = load_raw_dataset()
    labels = dataframe["type"].value_counts().sort_index()

    # Step 2: Check duplicates/conflicts and verify them with csv.reader.
    duplicate_info = analyse_duplicates_and_conflicts(dataframe)
    csv_widths, csv_classes = verify_with_csv_reader(
        dataframe, labels, duplicate_info
    )

    # Step 3: Check missing values and URL formatting signals.
    missingness = analyse_missing_values(dataframe)
    url_info = analyse_url_format(duplicate_info["urls"])

    # Step 4: Create detailed evidence and per-class profiles.
    write_anomaly_records(dataframe, url_info)
    class_profiles = profile_each_class(
        dataframe,
        labels,
        duplicate_info,
        url_info["masks"],
    )
    examples = select_representative_examples(dataframe, labels)

    # Step 5: Write conflict, duplicate, and example records.
    conflict_records = (
        dataframe.loc[duplicate_info["conflict_mask"]]
        .assign(record_number=lambda rows: rows.index + 1)
        .to_dict("records")
    )
    duplicate_url_groups = [
        {
            "url": str(url),
            "rows": int(count),
            "labels": sorted(csv_classes[url]),
        }
        for url, count in duplicate_info["url_counts"].items()
        if count > 1
    ]
    write_jsonl("conflict_records", conflict_records)
    write_jsonl("duplicate_url_groups", duplicate_url_groups)
    write_jsonl("examples", examples)

    # Step 6: Build the summary, verify source integrity, and save the result.
    summary = build_summary(
        dataframe=dataframe,
        source_info=source_info,
        labels=labels,
        missingness=missingness,
        duplicate_info=duplicate_info,
        csv_classes=csv_classes,
        csv_widths=csv_widths,
        url_info=url_info,
        class_profiles=class_profiles,
    )
    assert all(
        summary["verification"][key]
        for key in [
            "independent_csv_checks_passed",
            "raw_hash_unchanged",
            "archive_hash_unchanged",
        ]
    )

    summary_path = OUT / "summary.json"
    summary_path.write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return summary


if __name__ == "__main__":
    print(json.dumps(run_audit(), ensure_ascii=False, indent=2))
