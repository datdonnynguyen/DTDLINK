"""Extract 36 numeric features from URL text offline."""

import csv
import hashlib
import json
import re
from collections import Counter
from pathlib import Path
from urllib.parse import parse_qsl, unquote

from dtdlink_ml.url_parser import parse_url

ROOT = Path(__file__).resolve().parents[2]
CLEANED_INPUT = ROOT / "data/interim/malicious_phish_cleaned.csv"
FEATURE_OUTPUT = ROOT / "data/processed/url_features.csv"
FEATURE_AUDIT = ROOT / "reports/features/feature_extraction_audit.json"
INPUT_COLUMNS = ["url", "type", "target"]

PCT_RE = re.compile(r"%[0-9A-Fa-f]{2}")
CTRL_RE = re.compile(r"[\x00-\x1f\x7f]")
WORD_RE = re.compile(r"[a-z0-9]+")

SUSPICIOUS_TERMS = ["account", "auth", "confirm", "credential", "login", "password",
                    "secure", "signin", "update", "verify", "wallet"]
BRANDS = ["adobe", "amazon", "apple", "facebook", "google", "instagram", "linkedin",
          "microsoft", "netflix", "office", "outlook", "paypal", "whatsapp"]
# cyrillic / greek letters that look like latin ones
CONFUSABLE = ("аеорсхуіјһ"
              "ΑΒΕΗΙΚΜΝΟΡΤΧΥΖ"
              "αεικνορτυχ")

# the model needs these columns in exactly this order
FEATURE_NAMES = (
    "url_length", "host_length", "path_length", "query_length", "fragment_length",
    "tld_length", "dot_count", "hyphen_count", "digit_count", "special_character_count",
    "subdomain_count", "path_segment_count", "query_parameter_count",
    "suspicious_term_count", "brand_token_count", "non_ascii_count", "parse_issue_count",
    "has_scheme", "uses_https", "has_explicit_port", "has_nonstandard_port",
    "has_ip_host", "has_at_symbol", "has_userinfo", "has_suspicious_term",
    "brand_in_subdomain", "brand_in_userinfo", "brand_in_path_or_query",
    "has_unicode", "has_confusable_unicode", "has_percent_encoding",
    "has_encoded_separator", "has_control_character", "host_has_punycode",
    "has_unknown_tld", "parse_ok",
)
OUTPUT_COLUMNS = ("url", "type", "target", "registrable_domain", "tld", "parse_issues") + FEATURE_NAMES


def file_sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while True:
            block = f.read(1024 * 1024)
            if not block:
                break
            h.update(block)
    return h.hexdigest()


def url_id(url):
    """SHA-256 of the URL text, used as a row id in the split manifest."""
    return hashlib.sha256(url.encode("utf-8", errors="surrogatepass")).hexdigest()


def count_terms(text, terms):
    """Count distinct matching terms after percent-decoding, using ASCII word tokens."""
    # "pineapple" must not count as the brand "apple".
    words = set(WORD_RE.findall(unquote(text).lower()))
    count = 0
    for term in terms:
        if term in words:
            count += 1
    return count


def get_features(parsed):
    """Calculate the 36 numeric features from an already parsed URL."""
    url = parsed.analysis_url

    digits = 0
    special = 0
    non_ascii = 0
    confusable = False
    for char in url:
        if char.isdigit():
            digits += 1
        if not char.isalnum():
            special += 1
        if ord(char) > 127:
            non_ascii += 1
        if char in CONFUSABLE:
            confusable = True

    sub_count = sum(bool(part) for part in parsed.subdomain.split("."))
    path_count = sum(bool(part) for part in parsed.path.split("/"))
    punycode = any(label.startswith("xn--") for label in parsed.host.split("."))
    encoded_sep = any(code in url.lower() for code in ("%2f", "%3a", "%40", "%5c"))

    nonstandard_port = False
    if parsed.port is not None:
        if parsed.scheme == "http":
            nonstandard_port = parsed.port != 80
        elif parsed.scheme == "https":
            nonstandard_port = parsed.port != 443
        else:
            nonstandard_port = True

    suspicious = count_terms(url, SUSPICIOUS_TERMS)

    return {
        "url_length": len(url), "host_length": len(parsed.host),
        "path_length": len(parsed.path), "query_length": len(parsed.query),
        "fragment_length": len(parsed.fragment), "tld_length": len(parsed.tld),
        "dot_count": url.count("."), "hyphen_count": url.count("-"),
        "digit_count": digits,
        "special_character_count": special,
        "subdomain_count": sub_count,
        "path_segment_count": path_count,
        "query_parameter_count": len(parse_qsl(parsed.query, keep_blank_values=True)),
        "suspicious_term_count": suspicious,
        "brand_token_count": count_terms(url, BRANDS),
        "non_ascii_count": non_ascii,
        "parse_issue_count": len(parsed.issues),
        "has_scheme": int(parsed.has_scheme),
        "uses_https": int(parsed.scheme == "https"),
        "has_explicit_port": int(parsed.port is not None),
        "has_nonstandard_port": int(nonstandard_port),
        "has_ip_host": int(parsed.host_is_ip),
        "has_at_symbol": int("@" in url),
        "has_userinfo": int(parsed.userinfo != ""),
        "has_suspicious_term": int(suspicious > 0),
        "brand_in_subdomain": int(count_terms(parsed.subdomain, BRANDS) > 0),
        "brand_in_userinfo": int(count_terms(parsed.userinfo, BRANDS) > 0),
        "brand_in_path_or_query": int(count_terms(parsed.path + "?" + parsed.query, BRANDS) > 0),
        "has_unicode": int(non_ascii > 0),
        "has_confusable_unicode": int(confusable),
        "has_percent_encoding": int(PCT_RE.search(url) is not None),
        "has_encoded_separator": int(encoded_sep),
        "has_control_character": int(CTRL_RE.search(url) is not None),
        "host_has_punycode": int(punycode),
        "has_unknown_tld": int(parsed.host != "" and not parsed.host_is_ip and parsed.tld == ""),
        "parse_ok": int(parsed.parse_ok),
    }


def extract_features(url):
    return get_features(parse_url(url))


def extract_url_record(url, source_type, target):
    """One row of the processed CSV: url, label, domain info and the 36 features."""
    parsed = parse_url(url)
    row = {
        "url": parsed.raw_url,
        "type": source_type,
        "target": target,
        "registrable_domain": parsed.registrable_domain,
        "tld": parsed.tld,
        "parse_issues": "|".join(parsed.issues),
    }
    row.update(get_features(parsed))
    return row


def extract_feature_dataset(input_path=CLEANED_INPUT, output_path=FEATURE_OUTPUT, audit_path=FEATURE_AUDIT):
    """Read the cleaned CSV row by row, write the feature table and an audit JSON."""
    input_path = Path(input_path)
    output_path = Path(output_path)
    audit_path = Path(audit_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    audit_path.parent.mkdir(parents=True, exist_ok=True)
    tmp = output_path.with_suffix(output_path.suffix + ".tmp")

    row_count = 0
    parsed_count = 0
    issue_counts = Counter()
    target_counts = Counter()
    type_counts = Counter()
    try:
        with open(input_path, encoding="utf-8", newline="") as src, \
                open(tmp, "w", encoding="utf-8", newline="") as out:
            reader = csv.DictReader(src)
            if reader.fieldnames != INPUT_COLUMNS:
                raise ValueError(f"Expected input columns {INPUT_COLUMNS}, received {reader.fieldnames}.")
            writer = csv.DictWriter(out, fieldnames=OUTPUT_COLUMNS, lineterminator="\n")
            writer.writeheader()
            for line in reader:
                if line["target"] not in ("0", "1"):
                    raise ValueError(f"Unexpected target value at row {row_count + 2}: {line['target']!r}.")
                row = extract_url_record(line["url"], line["type"], line["target"])
                writer.writerow(row)
                row_count += 1
                parsed_count += row["parse_ok"]
                target_counts[line["target"]] += 1
                type_counts[line["type"]] += 1
                if row["parse_issues"]:
                    issue_counts.update(row["parse_issues"].split("|"))
        tmp.replace(output_path)
    finally:
        if tmp.exists():
            tmp.unlink()

    audit = {
        "input": {"path": str(input_path), "sha256": file_sha256(input_path), "columns": INPUT_COLUMNS},
        "output": {
            "path": str(output_path),
            "sha256": file_sha256(output_path),
            "rows": row_count,
            "columns": list(OUTPUT_COLUMNS),
            "feature_count": len(FEATURE_NAMES),
            "feature_names": list(FEATURE_NAMES),
            "parse_ok_rows": parsed_count,
            "parse_problem_rows": row_count - parsed_count,
            "issue_counts": dict(sorted(issue_counts.items())),
            "target_counts": dict(sorted(target_counts.items())),
            "type_counts": dict(sorted(type_counts.items())),
        },
    }
    audit_path.write_text(json.dumps(audit, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")
    return audit


if __name__ == "__main__":
    res = extract_feature_dataset()
    print(json.dumps(res["output"], indent=2, ensure_ascii=False))
