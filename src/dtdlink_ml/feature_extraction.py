"""Deterministic Stage 3 URL feature extraction for DTDLINK.

Calculate URL features locally without using source labels as inputs.

Run from the project root:
    .venv/bin/python src/dtdlink_ml/feature_extraction.py
"""

import csv
from collections import Counter
import hashlib
import json
import math
from pathlib import Path
import re
from typing import Any, Dict, Iterable, Mapping, Sequence, Tuple, Union
from urllib.parse import parse_qsl, unquote

from dtdlink_ml.url_parser import ParsedURL, parse_url


# =============================================================================
# SECTION 1 - PATHS AND PATTERNS
# Input, output and reusable text patterns.
# =============================================================================
ROOT = Path(__file__).resolve().parents[2]
CLEANED_INPUT = ROOT / "data/interim/malicious_phish_cleaned.csv"
FEATURE_OUTPUT = ROOT / "data/processed/url_features.csv"
FEATURE_AUDIT = ROOT / "reports/features/feature_extraction_audit.json"
EXPECTED_INPUT_COLUMNS = ["url", "type", "target"]

PERCENT_ENCODING_RE = re.compile(r"%[0-9A-Fa-f]{2}")
CONTROL_CHARACTER_RE = re.compile(r"[\x00-\x1f\x7f]")
TOKEN_RE = re.compile(r"[a-z0-9]+")


# =============================================================================
# SECTION 2 - FEATURE SETTINGS
# Adjustable suspicious terms, brands and Unicode look-alikes.
# =============================================================================
# These terms are signals only; they do not determine the target label.
SUSPICIOUS_TERMS: Tuple[str, ...] = (
    "account",
    "auth",
    "confirm",
    "credential",
    "login",
    "password",
    "secure",
    "signin",
    "update",
    "verify",
    "wallet",
)

# Match complete tokens: "pineapple" must not match the brand "apple".
BRAND_TOKENS: Tuple[str, ...] = (
    "adobe",
    "amazon",
    "apple",
    "facebook",
    "google",
    "instagram",
    "linkedin",
    "microsoft",
    "netflix",
    "office",
    "outlook",
    "paypal",
    "whatsapp",
)

# Bounded Greek/Cyrillic look-alike heuristic, not full Unicode UTS #39.
CONFUSABLE_UNICODE_CHARACTERS = frozenset(
    "\u0430\u0435\u043e\u0440\u0441\u0445\u0443\u0456\u0458\u04bb"
    "\u0391\u0392\u0395\u0397\u0399\u039a\u039c\u039d\u039f\u03a1\u03a4\u03a7\u03a5\u0396"
    "\u03b1\u03b5\u03b9\u03ba\u03bd\u03bf\u03c1\u03c4\u03c5\u03c7"
)


# =============================================================================
# SECTION 3 - FEATURE SCHEMA
# Fixed feature names and processed CSV column order.
# =============================================================================
# Names and order form the model input contract.
FEATURE_NAMES: Tuple[str, ...] = (
    "url_length",
    "host_length",
    "path_length",
    "query_length",
    "fragment_length",
    "tld_length",
    "dot_count",
    "hyphen_count",
    "digit_count",
    "special_character_count",
    "subdomain_count",
    "path_segment_count",
    "query_parameter_count",
    "suspicious_term_count",
    "brand_token_count",
    "non_ascii_count",
    "parse_issue_count",
    "has_scheme",
    "uses_https",
    "has_explicit_port",
    "has_nonstandard_port",
    "has_ip_host",
    "has_at_symbol",
    "has_userinfo",
    "has_suspicious_term",
    "brand_in_subdomain",
    "brand_in_userinfo",
    "brand_in_path_or_query",
    "has_unicode",
    "has_confusable_unicode",
    "has_percent_encoding",
    "has_encoded_separator",
    "has_control_character",
    "host_has_punycode",
    "has_unknown_tld",
    "parse_ok",
)

# The first six columns are metadata; FEATURE_NAMES are numeric model inputs.
OUTPUT_COLUMNS: Tuple[str, ...] = (
    "url",
    "type",
    "target",
    "registrable_domain",
    "tld",
    "parse_issues",
) + FEATURE_NAMES


# =============================================================================
# SECTION 4 - SMALL FEATURE HELPERS
# File hashing, token, count, path, query and port calculations.
# =============================================================================
def file_sha256(path: Path) -> str:
    """Calculate a deterministic file fingerprint."""

    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _tokens(text: str) -> Tuple[str, ...]:
    """Decode percent encoding and create lowercase alphanumeric tokens."""

    return tuple(TOKEN_RE.findall(unquote(text).lower()))


def _count_matching_terms(tokens: Sequence[str], terms: Iterable[str]) -> int:
    """Count distinct configured terms without counting repeated terms."""

    token_set = set(tokens)
    return sum(term in token_set for term in terms)


def _subdomain_count(parsed: ParsedURL) -> int:
    return len([label for label in parsed.subdomain.split(".") if label])


def _path_segment_count(path: str) -> int:
    return len([segment for segment in path.split("/") if segment])


def _query_parameter_count(query: str) -> int:
    try:
        return len(parse_qsl(query, keep_blank_values=True, strict_parsing=False))
    except (TypeError, ValueError):
        return 0


def _is_nonstandard_port(parsed: ParsedURL) -> bool:
    if parsed.port is None:
        return False
    expected = {"http": 80, "https": 443}.get(parsed.scheme)
    return expected is None or parsed.port != expected


def _extract_features_from_parsed(
    parsed: ParsedURL,
) -> Dict[str, Union[int, float]]:
    """Calculate 36 numeric features from one parsed URL."""

    url = parsed.analysis_url
    decoded_tokens = _tokens(url)
    subdomain_tokens = _tokens(parsed.subdomain)
    userinfo_tokens = _tokens(parsed.userinfo)
    path_query_tokens = _tokens(f"{parsed.path}?{parsed.query}")

    suspicious_term_count = _count_matching_terms(
        decoded_tokens, SUSPICIOUS_TERMS
    )
    brand_token_count = _count_matching_terms(decoded_tokens, BRAND_TOKENS)
    lower_url = url.lower()

    # Calculate lengths, counts and boolean signals without reading labels.
    features: Dict[str, Union[int, float]] = {
        "url_length": len(url),
        "host_length": len(parsed.host),
        "path_length": len(parsed.path),
        "query_length": len(parsed.query),
        "fragment_length": len(parsed.fragment),
        "tld_length": len(parsed.tld),
        "dot_count": url.count("."),
        "hyphen_count": url.count("-"),
        "digit_count": sum(character.isdigit() for character in url),
        "special_character_count": sum(
            not character.isalnum() for character in url
        ),
        "subdomain_count": _subdomain_count(parsed),
        "path_segment_count": _path_segment_count(parsed.path),
        "query_parameter_count": _query_parameter_count(parsed.query),
        "suspicious_term_count": suspicious_term_count,
        "brand_token_count": brand_token_count,
        "non_ascii_count": sum(ord(character) > 127 for character in url),
        "parse_issue_count": len(parsed.issues),
        "has_scheme": int(parsed.has_scheme),
        "uses_https": int(parsed.scheme == "https"),
        "has_explicit_port": int(parsed.port is not None),
        "has_nonstandard_port": int(_is_nonstandard_port(parsed)),
        "has_ip_host": int(parsed.host_is_ip),
        "has_at_symbol": int("@" in url),
        "has_userinfo": int(bool(parsed.userinfo)),
        "has_suspicious_term": int(suspicious_term_count > 0),
        "brand_in_subdomain": int(
            _count_matching_terms(subdomain_tokens, BRAND_TOKENS) > 0
        ),
        "brand_in_userinfo": int(
            _count_matching_terms(userinfo_tokens, BRAND_TOKENS) > 0
        ),
        "brand_in_path_or_query": int(
            _count_matching_terms(path_query_tokens, BRAND_TOKENS) > 0
        ),
        "has_unicode": int(any(ord(character) > 127 for character in url)),
        "has_confusable_unicode": int(
            any(character in CONFUSABLE_UNICODE_CHARACTERS for character in url)
        ),
        "has_percent_encoding": int(bool(PERCENT_ENCODING_RE.search(url))),
        "has_encoded_separator": int(
            any(code in lower_url for code in ("%2f", "%3a", "%40", "%5c"))
        ),
        "has_control_character": int(bool(CONTROL_CHARACTER_RE.search(url))),
        "host_has_punycode": int(
            any(label.startswith("xn--") for label in parsed.host.split("."))
        ),
        "has_unknown_tld": int(
            bool(parsed.host) and not parsed.host_is_ip and not parsed.tld
        ),
        "parse_ok": int(parsed.parse_ok),
    }

    # Stop if a feature is added, removed or reordered by mistake.
    if tuple(features) != FEATURE_NAMES:
        raise RuntimeError("Feature output no longer matches FEATURE_NAMES order.")
    if any(
        isinstance(value, float) and not math.isfinite(value)
        for value in features.values()
    ):
        raise ValueError("Feature output contains a non-finite value.")
    return features


# =============================================================================
# SECTION 5 - SINGLE URL FEATURE EXTRACTION
# Convert one raw URL into metadata and 36 numeric features.
# =============================================================================
def extract_features(value: object) -> Dict[str, Union[int, float]]:
    """Main single-URL flow: raw URL -> parser -> 36 numeric features."""

    return _extract_features_from_parsed(parse_url(value))


def extract_url_record(
    url: object,
    source_type: str,
    target: str,
) -> Dict[str, Any]:
    """Combine audit metadata and numeric features into one processed row."""

    parsed = parse_url(url)
    features = _extract_features_from_parsed(parsed)
    return {
        "url": parsed.raw_url,
        "type": source_type,
        "target": target,
        "registrable_domain": parsed.registrable_domain,
        "tld": parsed.tld,
        "parse_issues": "|".join(parsed.issues),
        **features,
    }


# =============================================================================
# SECTION 6 - FULL DATASET EXTRACTION
# Stream the cleaned CSV and write features plus audit evidence.
# =============================================================================
def extract_feature_dataset(
    input_path: Union[str, Path] = CLEANED_INPUT,
    output_path: Union[str, Path] = FEATURE_OUTPUT,
    audit_path: Union[str, Path] = FEATURE_AUDIT,
) -> Mapping[str, Any]:
    """Stream the cleaned CSV into a deterministic feature table."""

    input_path = Path(input_path)
    output_path = Path(output_path)
    audit_path = Path(audit_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    audit_path.parent.mkdir(parents=True, exist_ok=True)
    temporary_output = output_path.with_suffix(output_path.suffix + ".tmp")

    row_count = 0
    parse_ok_count = 0
    issue_counts: Counter = Counter()
    target_counts: Counter = Counter()
    type_counts: Counter = Counter()

    # Validate the Stage 2 schema, then process one record at a time.
    try:
        with input_path.open("r", encoding="utf-8", newline="") as source, \
                temporary_output.open("w", encoding="utf-8", newline="") as target_file:
            reader = csv.DictReader(source)
            if reader.fieldnames != EXPECTED_INPUT_COLUMNS:
                raise ValueError(
                    f"Expected input columns {EXPECTED_INPUT_COLUMNS}, "
                    f"received {reader.fieldnames}."
                )

            writer = csv.DictWriter(
                target_file,
                fieldnames=list(OUTPUT_COLUMNS),
                lineterminator="\n",
            )
            writer.writeheader()

            for source_row in reader:
                # Target is validated and copied, never used as a feature input.
                if source_row["target"] not in {"0", "1"}:
                    raise ValueError(
                        f"Unexpected target value at row {row_count + 2}: "
                        f"{source_row['target']!r}."
                    )
                record = extract_url_record(
                    source_row["url"],
                    source_row["type"],
                    source_row["target"],
                )
                writer.writerow(record)
                row_count += 1
                parse_ok_count += int(record["parse_ok"])
                target_counts[source_row["target"]] += 1
                type_counts[source_row["type"]] += 1
                if record["parse_issues"]:
                    issue_counts.update(record["parse_issues"].split("|"))

        # Replace the main output only after every row succeeds.
        temporary_output.replace(output_path)
    finally:
        if temporary_output.exists():
            temporary_output.unlink()

    # Record hashes, row counts, schema and parser issues.
    audit: Dict[str, Any] = {
        "input": {
            "path": str(input_path),
            "sha256": file_sha256(input_path),
            "columns": EXPECTED_INPUT_COLUMNS,
        },
        "output": {
            "path": str(output_path),
            "sha256": file_sha256(output_path),
            "rows": row_count,
            "columns": list(OUTPUT_COLUMNS),
            "feature_count": len(FEATURE_NAMES),
            "feature_names": list(FEATURE_NAMES),
            "parse_ok_rows": parse_ok_count,
            "parse_problem_rows": row_count - parse_ok_count,
            "issue_counts": dict(sorted(issue_counts.items())),
            "target_counts": dict(sorted(target_counts.items())),
            "type_counts": dict(sorted(type_counts.items())),
        },
        "constraints": {
            "network_lookups": False,
            "labels_used_to_calculate_features": False,
            "tld_frequency_feature": (
                "deferred until Stage 4; fit on training data only"
            ),
            "unicode_confusable_check": (
                "bounded documented heuristic, not complete Unicode UTS #39"
            ),
        },
    }
    with audit_path.open("w", encoding="utf-8") as stream:
        json.dump(audit, stream, indent=2, ensure_ascii=False, sort_keys=True)
        stream.write("\n")
    return audit


# =============================================================================
# SECTION 7 - COMMAND-LINE ENTRY POINT
# Run the full extraction only when this file is executed directly.
# =============================================================================
def main() -> None:
    audit = extract_feature_dataset()
    print(json.dumps(audit["output"], indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
