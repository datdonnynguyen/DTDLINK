"""Audit the raw CSV before cleaning."""

import hashlib
import json
import re
import zipfile
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlsplit

import pandas as pd

from dtdlink_ml.data_cleaning import read_raw

ROOT = Path(__file__).resolve().parents[2]
ARCHIVE = ROOT / "Week-08/Assessment/Basic_Datasets.zip"
MEMBER = "Basic_Datasets/Phishing URL Detection/malicious_phish.csv"
RAW = ROOT / "data/raw/malicious_phish.csv"
OUT = ROOT / "reports/audit"

MISSING_TOKENS = ["na", "n/a", "null", "none", "nan", "unknown", "?"]
SCHEME_PATTERN = r"^[A-Za-z][A-Za-z0-9+.-]*://"
ANOMALIES = ["any_whitespace", "control_character", "non_ascii", "length_over_2048", "diagnostic_parse_issue"]


def write_jsonl(name, records):
    with open(OUT / f"{name}.jsonl", "w", encoding="utf-8") as f:
        for record in records:
            f.write(json.dumps(record, ensure_ascii=True) + "\n")


def load_raw_dataset():
    """Copy the CSV out of the course ZIP (first run only) and load it."""
    with zipfile.ZipFile(ARCHIVE) as z:
        data = z.read(MEMBER)
    csv_sha = hashlib.sha256(data).hexdigest()
    if not RAW.exists():
        RAW.parent.mkdir(parents=True, exist_ok=True)
        RAW.write_bytes(data)
    # the copy in data/raw must be the same file as the one in the ZIP
    df, _ = read_raw(RAW, csv_sha)
    if list(df.columns) != ["url", "type"]:
        raise ValueError(f"Unexpected columns: {list(df.columns)}")
    source = {
        "archive": str(ARCHIVE.relative_to(ROOT)),
        "member": MEMBER,
        "raw": str(RAW.relative_to(ROOT)),
        "csv_sha256": csv_sha,
        "csv_bytes": len(data),
    }
    return df, source


def rough_hosts(urls):
    """Quick host check with urlsplit, only for the audit (the real parser is url_parser.py)."""
    hosts = []
    issues = []
    for url in urls:
        if not re.match(SCHEME_PATTERN, url) and not url.startswith("//"):
            url = "//" + url
        try:
            host = urlsplit(url).hostname or ""
            issue = "" if host else "no_hostname"
        except ValueError:
            host = ""
            issue = "urlsplit_value_error"
        hosts.append(host)
        issues.append(issue)
    return pd.Series(hosts, dtype="string"), pd.Series(issues, dtype="string")


def run_audit():
    """Run the Stage 1 audit (labels, duplicates, odd URLs) and save the result files."""
    OUT.mkdir(parents=True, exist_ok=True)
    df, source = load_raw_dataset()
    urls = df["url"]
    row_count = len(df)
    labels = df["type"].value_counts().sort_index()
    url_counts = urls.value_counts()
    pair_counts = df.groupby(["url", "type"]).size()
    n_labels = df.groupby("url")["type"].nunique()
    conflict_urls = n_labels[n_labels > 1].index
    is_conflict = urls.isin(conflict_urls)

    # labels seen for each URL that appears more than once
    repeated = df[urls.duplicated(keep=False)]
    labels_by_url = {}
    for url, types in repeated.groupby("url")["type"]:
        labels_by_url[url] = sorted(set(types))

    flags = {}
    flags["http_prefix"] = urls.str.match(r"(?i)^http://")
    flags["https_prefix"] = urls.str.match(r"(?i)^https://")
    flags["no_explicit_scheme"] = ~urls.str.match(SCHEME_PATTERN)
    flags["any_whitespace"] = urls.str.contains(r"\s")
    flags["control_character"] = urls.str.contains(r"[\x00-\x1f\x7f]")
    flags["non_ascii"] = urls.str.contains(r"[^\x00-\x7f]")
    flags["literal_at_symbol"] = urls.str.contains("@", regex=False)
    flags["length_over_2048"] = urls.str.len().gt(2048)
    hosts, issues = rough_hosts(urls)
    flags["diagnostic_parse_issue"] = issues.ne("")

    any_flag = pd.concat([flags[name] for name in ANOMALIES], axis=1).any(axis=1)
    records = []
    for i in df.index[any_flag]:
        names = [name for name in ANOMALIES if flags[name][i]]
        records.append({
            "record_number": int(i + 1),
            "url": str(df.at[i, "url"]),
            "label": str(df.at[i, "type"]),
            "flags": names,
            "parse_issue": str(issues[i]),
        })
    write_jsonl("anomaly_records", records)

    conflicts = df[is_conflict].copy()
    conflicts["record_number"] = conflicts.index + 1
    write_jsonl("conflict_records", conflicts.to_dict("records"))

    groups = []
    for url, count in url_counts.items():
        if count > 1:
            groups.append({"url": str(url), "rows": int(count), "labels": labels_by_url[url]})
    write_jsonl("duplicate_url_groups", groups)

    # 3 example URLs per class: length closest to Q1, median and Q3
    examples = []
    profiles = []
    for label in labels.index:
        in_class = df["type"].eq(label)
        lengths = urls[in_class].str.len()
        used = set()
        for q in [0.25, 0.5, 0.75]:
            dist = (lengths - lengths.quantile(q)).abs().sort_values(kind="stable")
            for idx in dist.index:
                if idx not in used:
                    break
            used.add(idx)
            examples.append({
                "record_number": int(idx + 1),
                "label": label,
                "length_quantile": q,
                "url": str(df.at[idx, "url"]),
                "length": int(lengths[idx]),
            })

        profile = {
            "label": label,
            "rows": int(in_class.sum()),
            "unique_urls": int(urls[in_class].nunique()),
            "exact_duplicate_excess": int(df[in_class].duplicated().sum()),
            "conflict_rows": int((in_class & is_conflict).sum()),
        }
        for name, mask in flags.items():
            profile[name] = int((mask & in_class).sum())
        profile["length"] = {str(q): float(lengths.quantile(q)) for q in [0, 0.25, 0.5, 0.75, 0.95, 1]}
        profiles.append(profile)
    write_jsonl("examples", examples)

    missing = {}
    for col in df:
        values = df[col]
        missing[col] = {
            "empty_string": int(values.eq("").sum()),
            "whitespace_only_nonempty": int((values.ne("") & values.str.fullmatch(r"\s*")).sum()),
            "na_like_token": int(values.str.strip().str.lower().isin(MISSING_TOKENS).sum()),
            "leading_or_trailing_whitespace": int(values.ne(values.str.strip()).sum()),
        }

    label_rows = []
    for label, count in labels.items():
        label_rows.append({"label": label, "rows": int(count), "percent": float(100 * count / row_count)})

    combos = Counter()
    for url in conflict_urls:
        combos["|".join(labels_by_url[url])] += 1

    known = hosts[hosts.ne("")]
    summary = {
        "audit_time_utc": datetime.now(timezone.utc).isoformat(),
        "source": source,
        "shape": {"rows": row_count, "columns": len(df.columns)},
        "labels": label_rows,
        "missingness": missing,
        "duplicates": {
            "unique_complete_rows": len(pair_counts),
            "exact_row_excess": int(df.duplicated().sum()),
            "exact_row_affected": int(df.duplicated(keep=False).sum()),
            "exact_row_groups": int((pair_counts > 1).sum()),
            "unique_urls": len(url_counts),
            "url_excess": int(urls.duplicated().sum()),
            "url_affected": int(urls.duplicated(keep=False).sum()),
            "url_groups": int((url_counts > 1).sum()),
            "additional_url_merges_if_trimmed": len(url_counts) - int(urls.str.strip().nunique()),
        },
        "conflicts": {
            "unique_urls": len(conflict_urls),
            "affected_rows": int(is_conflict.sum()),
            "label_combinations": dict(combos),
        },
        "by_class": profiles,
        "diagnostic_host": {
            "unique_nonempty_hosts": int(known.nunique()),
            "rows_in_repeated_hosts": int(known.duplicated(keep=False).sum()),
            "parse_issue_counts": {str(k): int(values) for k, values in issues.value_counts().items()},
            "largest_host_row_count": int(known.value_counts().max()),
        },
    }
    (OUT / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return summary


if __name__ == "__main__":
    print(json.dumps(run_audit(), ensure_ascii=False, indent=2))
