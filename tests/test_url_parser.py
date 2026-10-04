"""Tests for the offline and fault-tolerant DTDLINK URL parser."""

import socket

import pytest

from dtdlink_ml.url_parser import ParsedURL, parse_url


EXAMPLE_URL = (
    "https://paypal.com@security-check.example.net:8443/login/verify"
    "?account=123&next=%2Fhome#step2"
)


def test_parser_separates_the_real_host_from_misleading_userinfo() -> None:
    parsed = parse_url(EXAMPLE_URL)

    assert parsed.raw_url == EXAMPLE_URL
    assert parsed.scheme == "https"
    assert parsed.userinfo == "paypal.com"
    assert parsed.host == "security-check.example.net"
    assert parsed.registrable_domain == "example.net"
    assert parsed.subdomain == "security-check"
    assert parsed.tld == "net"
    assert parsed.port == 8443
    assert parsed.path == "/login/verify"
    assert parsed.query == "account=123&next=%2Fhome"
    assert parsed.fragment == "step2"
    assert parsed.parse_ok is True


def test_scheme_less_url_is_recovered_without_changing_the_original() -> None:
    parsed = parse_url("example.com/login")

    assert parsed.raw_url == "example.com/login"
    assert parsed.has_scheme is False
    assert parsed.scheme == ""
    assert parsed.host == "example.com"
    assert parsed.path == "/login"
    assert parsed.parse_ok is True
    assert parsed.issues == ("missing_scheme",)


def test_protocol_relative_url_is_parsed_as_a_host() -> None:
    parsed = parse_url("//www.example.co.uk/path")

    assert parsed.host == "www.example.co.uk"
    assert parsed.registrable_domain == "example.co.uk"
    assert parsed.subdomain == "www"
    assert parsed.tld == "co.uk"
    assert parsed.has_scheme is False


@pytest.mark.parametrize(
    ("url", "expected_host"),
    [
        ("http://192.168.1.5/admin", "192.168.1.5"),
        ("https://[2001:db8::1]/login", "2001:db8::1"),
    ],
)
def test_parser_recognises_ip_hosts(url: str, expected_host: str) -> None:
    parsed = parse_url(url)

    assert parsed.host == expected_host
    assert parsed.host_is_ip is True
    assert parsed.registrable_domain == expected_host
    assert parsed.tld == ""


def test_username_and_password_are_kept_as_structure_not_host() -> None:
    parsed = parse_url("https://alice:secret@example.com/private")

    assert parsed.username == "alice"
    assert parsed.password == "secret"
    assert parsed.userinfo == "alice:secret"
    assert parsed.host == "example.com"


@pytest.mark.parametrize(
    ("url", "issue"),
    [
        ("", "empty_input"),
        ("   ", "empty_input"),
        ("https://", "missing_host"),
        ("https://example.com:wrong", "invalid_port"),
        ("https://example.com:70000", "invalid_port"),
        ("https://[2001:db8::1", "invalid_structure"),
        ("https:/example.com", "invalid_structure"),
        ("http:example.com", "invalid_structure"),
        ("javascript:alert(1)", "unsupported_scheme"),
    ],
)
def test_malformed_inputs_return_issue_codes_instead_of_crashing(
    url: str,
    issue: str,
) -> None:
    parsed = parse_url(url)

    assert parsed.parse_ok is False
    assert issue in parsed.issues


@pytest.mark.parametrize("value", [None, 123, ["https://example.com"]])
def test_non_string_inputs_have_a_stable_invalid_result(value: object) -> None:
    parsed = parse_url(value)

    assert isinstance(parsed, ParsedURL)
    assert parsed.parse_ok is False
    assert parsed.issues == ("input_not_string",)


def test_unicode_and_punycode_hosts_remain_inspectable() -> None:
    unicode_result = parse_url("https://例子.测试/登录")
    punycode_result = parse_url("https://xn--fsqu00a.xn--0zwm56d/login")

    assert unicode_result.host == "例子.测试"
    assert unicode_result.path == "/登录"
    assert punycode_result.host.startswith("xn--")


def test_edge_whitespace_is_flagged_while_raw_input_is_preserved() -> None:
    parsed = parse_url("  https://example.com/path  ")

    assert parsed.raw_url.startswith("  ")
    assert parsed.analysis_url == "https://example.com/path"
    assert parsed.host == "example.com"
    assert "edge_whitespace" in parsed.issues
    assert parsed.parse_ok is True


def test_parser_makes_no_network_connection(monkeypatch: pytest.MonkeyPatch) -> None:
    def fail_if_called(*args: object, **kwargs: object) -> None:
        raise AssertionError("URL parsing attempted a network connection")

    monkeypatch.setattr(socket, "create_connection", fail_if_called)
    parsed = parse_url("https://www.example.com/path")

    assert parsed.registrable_domain == "example.com"
    assert parsed.parse_ok is True


def test_parser_output_schema_is_stable() -> None:
    expected_fields = {
        "raw_url",
        "analysis_url",
        "scheme",
        "userinfo",
        "username",
        "password",
        "host",
        "port",
        "path",
        "query",
        "fragment",
        "registrable_domain",
        "subdomain",
        "tld",
        "has_scheme",
        "host_is_ip",
        "parse_ok",
        "issues",
    }

    assert set(parse_url("https://example.com").to_dict()) == expected_fields
