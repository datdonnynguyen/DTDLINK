"""Parse URL text offline and record parsing issues."""

import ipaddress
import re
from dataclasses import asdict, dataclass
from typing import Optional, Tuple
from urllib.parse import urlsplit

import tldextract

WEB_SCHEMES = ["http", "https"]
OTHER_SCHEMES = ["data", "file", "javascript", "mailto", "tel"]
FATAL = ["invalid_port", "invalid_structure", "missing_host", "unsupported_scheme"]

SCHEME_RE = re.compile(r"^[A-Za-z][A-Za-z0-9+.-]*://")
BAD_HTTP_RE = re.compile(r"^https?:(?!//)", re.IGNORECASE)
CTRL_RE = re.compile(r"[\x00-\x1f\x7f]")

# offline: only the suffix list bundled with tldextract
extractor = tldextract.TLDExtract(suffix_list_urls=(), fallback_to_snapshot=True,
                                  include_psl_private_domains=False, cache_dir=None)


@dataclass(frozen=True)
class ParsedURL:
    """URL components and parsing issues."""
    raw_url: str
    analysis_url: str
    scheme: str = ""
    userinfo: str = ""
    username: str = ""
    password: str = ""
    host: str = ""
    port: Optional[int] = None
    path: str = ""
    query: str = ""
    fragment: str = ""
    registrable_domain: str = ""
    subdomain: str = ""
    tld: str = ""
    has_scheme: bool = False
    host_is_ip: bool = False
    parse_ok: bool = False
    issues: Tuple[str, ...] = ()

    def to_dict(self):
        return asdict(self)


def dedupe(items):
    """Remove repeated items but keep the original order."""
    unique = []
    for item in items:
        if item not in unique:
            unique.append(item)
    return tuple(unique)


def parse_url(value):
    """Parse a URL and return any problems in `issues`."""
    if not isinstance(value, str):
        return ParsedURL("", "", issues=("input_not_string",))
    url = value.strip()
    if url == "":
        return ParsedURL(value, url, issues=("empty_input",))

    issues = []
    if url != value:
        issues.append("edge_whitespace")
    if CTRL_RE.search(value):
        issues.append("control_character")

    bad_http = BAD_HTTP_RE.match(url) is not None
    has_scheme = bad_http
    if SCHEME_RE.match(url):
        has_scheme = True
    elif ":" in url and url.split(":", 1)[0].lower() in OTHER_SCHEMES:
        has_scheme = True
    if not has_scheme:
        issues.append("missing_scheme")
    if bad_http:
        issues.append("invalid_structure")

    text = url
    if not has_scheme and not url.startswith("//"):
        text = "//" + url  # Recover the host in scheme-less dataset URLs.
    try:
        parts = urlsplit(text)
    except ValueError:
        issues.append("invalid_structure")
        return ParsedURL(value, url, has_scheme=has_scheme, issues=dedupe(issues))

    scheme = parts.scheme.lower()
    host = parts.hostname or ""
    host = host.lower().rstrip(".")
    try:
        port = parts.port
    except ValueError:
        port = None
        issues.append("invalid_port")
    if host == "":
        issues.append("missing_host")
    if has_scheme and scheme not in WEB_SCHEMES:
        issues.append("unsupported_scheme")

    is_ip = False
    if host:
        try:
            ipaddress.ip_address(host)
            is_ip = True
        except ValueError:
            pass

    domain = ""
    sub = ""
    tld = ""
    if is_ip:
        domain = host
    elif host:
        domain_parts = extractor(host)
        domain = domain_parts.registered_domain
        if domain == "":
            domain = host
        sub = domain_parts.subdomain
        tld = domain_parts.suffix

    userinfo = ""
    if "@" in parts.netloc:
        userinfo = parts.netloc.rsplit("@", 1)[0]

    parse_ok = not any(issue in FATAL for issue in issues)

    return ParsedURL(
        raw_url=value,
        analysis_url=url,
        scheme=scheme,
        userinfo=userinfo,
        username=parts.username or "",
        password=parts.password or "",
        host=host,
        port=port,
        path=parts.path,
        query=parts.query,
        fragment=parts.fragment,
        registrable_domain=domain,
        subdomain=sub,
        tld=tld,
        has_scheme=has_scheme,
        host_is_ip=is_ip,
        parse_ok=parse_ok,
        issues=dedupe(issues),
    )
