"""Offline, fault-tolerant URL parsing for DTDLINK.

This module separates URL text into structured parts without visiting the
destination or making network requests.
"""

from dataclasses import asdict, dataclass
import ipaddress
import re
from typing import Any, Dict, Optional, Tuple
from urllib.parse import SplitResult, urlsplit

import tldextract


# =============================================================================
# SECTION 1 - PARSER SETTINGS
# Supported schemes, malformed-input patterns and offline domain parsing.
# =============================================================================
WEB_SCHEMES = frozenset({"http", "https"})
NON_HIERARCHICAL_SCHEMES = frozenset(
    {"data", "file", "javascript", "mailto", "tel"}
)
SCHEME_WITH_SLASHES_RE = re.compile(
    r"^(?P<scheme>[A-Za-z][A-Za-z0-9+.-]*):/{2}"
)
MALFORMED_WEB_SCHEME_RE = re.compile(r"^https?:(?!//)", re.IGNORECASE)
CONTROL_CHARACTER_RE = re.compile(r"[\x00-\x1f\x7f]")

# Use the bundled Public Suffix List without network or cache access.
DOMAIN_EXTRACTOR = tldextract.TLDExtract(
    suffix_list_urls=(),
    fallback_to_snapshot=True,
    include_psl_private_domains=False,
    cache_dir=None,
)


# =============================================================================
# SECTION 2 - PARSED URL RESULT
# Stable structured output returned for every input.
# =============================================================================
@dataclass(frozen=True)
class ParsedURL:
    """Store parsed URL parts and parser issue codes."""

    raw_url: str
    analysis_url: str
    scheme: str
    userinfo: str
    username: str
    password: str
    host: str
    port: Optional[int]
    path: str
    query: str
    fragment: str
    registrable_domain: str
    subdomain: str
    tld: str
    has_scheme: bool
    host_is_ip: bool
    parse_ok: bool
    issues: Tuple[str, ...]

    def to_dict(self) -> Dict[str, Any]:
        """Return a plain dictionary suitable for notebooks and APIs."""

        return asdict(self)


# =============================================================================
# SECTION 3 - PARSER HELPERS
# Small functions used by the main parser.
# =============================================================================
def _empty_result(raw_url: str, analysis_url: str, issue: str) -> ParsedURL:
    """Return the same schema even when the input is empty or unusable."""

    return ParsedURL(
        raw_url=raw_url,
        analysis_url=analysis_url,
        scheme="",
        userinfo="",
        username="",
        password="",
        host="",
        port=None,
        path="",
        query="",
        fragment="",
        registrable_domain="",
        subdomain="",
        tld="",
        has_scheme=False,
        host_is_ip=False,
        parse_ok=False,
        issues=(issue,),
    )


def _has_explicit_scheme(url: str) -> bool:
    """Check whether the input contains an explicit URL scheme."""

    if SCHEME_WITH_SLASHES_RE.match(url):
        return True
    scheme_candidate = url.partition(":")[0].lower()
    return (
        ":" in url
        and scheme_candidate in NON_HIERARCHICAL_SCHEMES
    )


def _split_for_analysis(url: str, has_scheme: bool) -> SplitResult:
    """Add temporary // so a scheme-less URL exposes its host."""

    if has_scheme or url.startswith("//"):
        return urlsplit(url, allow_fragments=True)
    return urlsplit(f"//{url}", allow_fragments=True)


def _domain_parts(host: str, host_is_ip: bool) -> Tuple[str, str, str]:
    """Separate registrable domain, subdomain and TLD fully offline."""

    if not host:
        return "", "", ""
    if host_is_ip:
        return host, "", ""

    clean_host = host.rstrip(".")
    extracted = DOMAIN_EXTRACTOR(clean_host)
    registrable_domain = extracted.registered_domain or clean_host
    return registrable_domain, extracted.subdomain, extracted.suffix


# =============================================================================
# SECTION 4 - MAIN URL PARSER
# Convert one raw URL into structured parts and issue codes.
# =============================================================================
def parse_url(value: object) -> ParsedURL:
    """Parse one URL-like value without network access or uncaught errors."""

    # Validate input while keeping a stable output schema.
    if not isinstance(value, str):
        return _empty_result("", "", "input_not_string")

    raw_url = value
    analysis_url = raw_url.strip()
    if not analysis_url:
        return _empty_result(raw_url, analysis_url, "empty_input")

    # Record unusual input without changing raw_url.
    issues = []
    if raw_url != analysis_url:
        issues.append("edge_whitespace")
    if CONTROL_CHARACTER_RE.search(raw_url):
        issues.append("control_character")

    # A missing scheme is recoverable; a malformed web scheme is fatal.
    malformed_web_scheme = bool(MALFORMED_WEB_SCHEME_RE.match(analysis_url))
    has_scheme = _has_explicit_scheme(analysis_url) or malformed_web_scheme
    if not has_scheme:
        issues.append("missing_scheme")
    if malformed_web_scheme:
        issues.append("invalid_structure")

    # Split authority, path, query and fragment.
    try:
        split = _split_for_analysis(analysis_url, has_scheme)
    except (TypeError, ValueError):
        return ParsedURL(
            **{
                **_empty_result(raw_url, analysis_url, "invalid_structure").to_dict(),
                "has_scheme": has_scheme,
                "issues": tuple(dict.fromkeys(issues + ["invalid_structure"])),
            }
        )

    scheme = split.scheme.lower()
    host = (split.hostname or "").lower().rstrip(".")

    # Invalid text or out-of-range ports raise ValueError.
    try:
        port = split.port
    except ValueError:
        port = None
        issues.append("invalid_port")

    if not host:
        issues.append("missing_host")
    if has_scheme and scheme not in WEB_SCHEMES:
        issues.append("unsupported_scheme")

    try:
        host_is_ip = bool(host) and ipaddress.ip_address(host) is not None
    except ValueError:
        host_is_ip = False

    # Extract domain parts for features and the Stage 4 grouped split.
    registrable_domain, subdomain, tld = _domain_parts(host, host_is_ip)

    # The real host follows the final @; preceding text is user-info.
    userinfo = split.netloc.rsplit("@", 1)[0] if "@" in split.netloc else ""

    fatal_issues = {
        "invalid_port",
        "invalid_structure",
        "missing_host",
        "unsupported_scheme",
    }
    # Fatal issues set parse_ok=False, but the record remains available.
    parse_ok = not any(issue in fatal_issues for issue in issues)

    return ParsedURL(
        raw_url=raw_url,
        analysis_url=analysis_url,
        scheme=scheme,
        userinfo=userinfo,
        username=split.username or "",
        password=split.password or "",
        host=host,
        port=port,
        path=split.path,
        query=split.query,
        fragment=split.fragment,
        registrable_domain=registrable_domain,
        subdomain=subdomain,
        tld=tld,
        has_scheme=has_scheme,
        host_is_ip=host_is_ip,
        parse_ok=parse_ok,
        issues=tuple(dict.fromkeys(issues)),
    )
