"""Tests for stable, label-independent DTDLINK URL features."""

import csv
import hashlib
import json
import math

import pytest

from dtdlink_ml.feature_extraction import (
    FEATURE_NAMES,
    OUTPUT_COLUMNS,
    extract_feature_dataset,
    extract_features,
    extract_url_record,
)


EXAMPLE_URL = (
    "https://paypal.com@security-check.example.net:8443/login/verify"
    "?account=123&next=%2Fhome#step2"
)

# More than the 30 normal, malformed, encoded, Unicode, IP-host, long and
# suspicious cases required by the Stage 3 completion plan.
ROBUSTNESS_INPUTS = [
    "https://example.com",
    "http://example.com/path",
    "example.com/path",
    "//example.com/path",
    "https://www.example.co.uk/a/b",
    "https://a.b.c.example.com",
    "https://user@example.com",
    "https://user:pass@example.com",
    "https://paypal.com@example.net/login",
    "http://127.0.0.1/admin",
    "http://192.168.1.5:8080/admin",
    "https://[2001:db8::1]/",
    "https://[2001:db8::1]:8443/login",
    "https://example.com:443/",
    "http://example.com:80/",
    "https://example.com:8443/",
    "https://example.com:wrong/",
    "https://example.com:70000/",
    "https://example.com/login?next=%2Fhome",
    "https://example.com/?a=1&b=&c=3",
    "https://example.com/path#fragment",
    "https://example.com/%40admin%2Flogin",
    "https://例子.测试/登录",
    "https://раypal.example/login",
    "https://xn--fsqu00a.xn--0zwm56d/",
    "https://localhost/login",
    "localhost:8000/login",
    "",
    "   ",
    "https://",
    "https:///only-path",
    "https://[2001:db8::1",
    "https:/example.com",
    "http:example.com",
    "javascript:alert(1)",
    "mailto:user@example.com",
    "data:text/plain,hello",
    "ftp://example.com/file",
    "https://example.com/path with space",
    "https://example.com/line\nbreak",
    "https://example.com/tab\tvalue",
    "https://example.com/null\x00value",
    "https://example.com/" + "a" * 5000,
    "https://999.999.999.999/login",
    "https://example.com./path",
    "https://a@b@example.com/path",
    "?query-only=true",
    "#fragment-only",
    None,
    12345,
]


def test_example_url_becomes_expected_numeric_evidence() -> None:
    features = extract_features(EXAMPLE_URL)

    assert features["url_length"] == 94
    assert features["host_length"] == 26
    assert features["path_length"] == 13
    assert features["query_length"] == 24
    assert features["subdomain_count"] == 1
    assert features["query_parameter_count"] == 2
    assert features["has_at_symbol"] == 1
    assert features["has_userinfo"] == 1
    assert features["brand_in_userinfo"] == 1
    assert features["has_ip_host"] == 0
    assert features["has_nonstandard_port"] == 1
    assert features["has_percent_encoding"] == 1
    assert features["parse_ok"] == 1


def test_feature_schema_order_is_stable_and_numeric() -> None:
    features = extract_features("https://example.com/login")

    assert tuple(features) == FEATURE_NAMES
    assert len(features) == 36
    assert all(isinstance(value, (int, float)) for value in features.values())
    assert all(
        not isinstance(value, float) or math.isfinite(value)
        for value in features.values()
    )


def test_brand_matching_uses_tokens_instead_of_substrings() -> None:
    false_positive = extract_features("https://pineapple.example.com/")
    true_positive = extract_features("https://apple.example.com/")

    assert false_positive["brand_in_subdomain"] == 0
    assert true_positive["brand_in_subdomain"] == 1


def test_unicode_confusable_and_general_unicode_are_separate_features() -> None:
    ordinary_unicode = extract_features("https://例子.测试/登录")
    confusable = extract_features("https://раypal.example/login")

    assert ordinary_unicode["has_unicode"] == 1
    assert confusable["has_unicode"] == 1
    assert confusable["has_confusable_unicode"] == 1


def test_ip_punycode_and_unknown_tld_signals() -> None:
    ip_features = extract_features("http://192.168.1.5/login")
    punycode_features = extract_features(
        "https://xn--fsqu00a.xn--0zwm56d/login"
    )

    assert ip_features["has_ip_host"] == 1
    assert ip_features["has_unknown_tld"] == 0
    assert punycode_features["host_has_punycode"] == 1
    assert punycode_features["has_unknown_tld"] == 1


def test_labels_are_metadata_and_do_not_change_features() -> None:
    benign = extract_url_record("https://example.com", "benign", "0")
    dangerous = extract_url_record("https://example.com", "phishing", "1")

    assert [benign[name] for name in FEATURE_NAMES] == [
        dangerous[name] for name in FEATURE_NAMES
    ]
    assert benign["type"] != dangerous["type"]
    assert benign["target"] != dangerous["target"]


@pytest.mark.parametrize("value", ROBUSTNESS_INPUTS)
def test_at_least_30_unusual_inputs_never_break_the_feature_schema(
    value: object,
) -> None:
    features = extract_features(value)

    assert tuple(features) == FEATURE_NAMES
    assert all(isinstance(item, (int, float)) for item in features.values())


def test_streaming_dataset_extraction_is_reproducible(tmp_path) -> None:
    input_path = tmp_path / "cleaned.csv"
    output_path = tmp_path / "features.csv"
    audit_path = tmp_path / "audit.json"
    input_path.write_text(
        "url,type,target\n"
        "https://example.com,benign,0\n"
        "example.net/login,phishing,1\n"
        "https://paypal.com@example.org/verify,malware,1\n",
        encoding="utf-8",
    )

    first_audit = extract_feature_dataset(input_path, output_path, audit_path)
    first_output_hash = hashlib.sha256(output_path.read_bytes()).hexdigest()
    first_audit_bytes = audit_path.read_bytes()
    second_audit = extract_feature_dataset(input_path, output_path, audit_path)

    assert hashlib.sha256(output_path.read_bytes()).hexdigest() == first_output_hash
    assert audit_path.read_bytes() == first_audit_bytes
    assert second_audit == first_audit
    assert first_audit["output"]["rows"] == 3
    assert first_audit["output"]["feature_count"] == len(FEATURE_NAMES)

    with output_path.open(encoding="utf-8", newline="") as stream:
        rows = list(csv.DictReader(stream))
    assert rows[0]["registrable_domain"] == "example.com"
    assert rows[1]["parse_issues"] == "missing_scheme"
    assert list(rows[0]) == list(OUTPUT_COLUMNS)


def test_dataset_extraction_rejects_wrong_schema(tmp_path) -> None:
    input_path = tmp_path / "wrong.csv"
    input_path.write_text("url,label\nexample.com,benign\n", encoding="utf-8")

    with pytest.raises(ValueError, match="Expected input columns"):
        extract_feature_dataset(
            input_path,
            tmp_path / "features.csv",
            tmp_path / "audit.json",
        )


def test_dataset_extraction_rejects_unknown_target(tmp_path) -> None:
    input_path = tmp_path / "wrong-target.csv"
    input_path.write_text(
        "url,type,target\nexample.com,benign,unknown\n",
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="Unexpected target"):
        extract_feature_dataset(
            input_path,
            tmp_path / "features.csv",
            tmp_path / "audit.json",
        )


def test_audit_is_valid_json_and_records_no_label_leakage(tmp_path) -> None:
    input_path = tmp_path / "cleaned.csv"
    output_path = tmp_path / "features.csv"
    audit_path = tmp_path / "audit.json"
    input_path.write_text(
        "url,type,target\nhttps://example.com,benign,0\n",
        encoding="utf-8",
    )

    extract_feature_dataset(input_path, output_path, audit_path)
    audit = json.loads(audit_path.read_text(encoding="utf-8"))

    assert audit["constraints"]["network_lookups"] is False
    assert audit["constraints"]["labels_used_to_calculate_features"] is False
    assert "training data only" in audit["constraints"]["tld_frequency_feature"]
