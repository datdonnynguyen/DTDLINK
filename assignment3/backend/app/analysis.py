"""Offline, rule-based explanations. These never change or explain model weights."""
import re
from urllib.parse import unquote

import idna
from dtdlink_ml.feature_extraction import BRANDS, CONFUSABLE, SUSPICIOUS_TERMS, WORD_RE


def snippet(value, limit=180):
    return value if len(value) <= limit else value[:limit] + "…"


def matches(text, vocabulary):
    words = set(WORD_RE.findall(unquote(text).lower()))
    return [word for word in vocabulary if word in words]


def split_display_parts(url):
    """Keep every input character, including case, IPv6 brackets and empty ?/#."""
    match = re.fullmatch(r"(https?://)([^/?#]*)([^?#]*)(\?[^#]*)?(#.*)?", url, re.I)
    if not match:
        raise ValueError("Display breakdown requires a validated HTTP(S) URL.")
    protocol, authority, path, query, fragment = match.groups()
    parts = [{"kind": "protocol", "text": protocol}]
    if "@" in authority:
        userinfo, _, authority = authority.rpartition("@")
        parts.append({"kind": "userinfo", "text": userinfo + "@"})
    if authority.startswith("["):
        end = authority.index("]") + 1
        host, port = authority[:end], authority[end:]
    elif ":" in authority:
        host, _, port = authority.rpartition(":")
        port = ":" + port
    else:
        host, port = authority, ""
    parts.append({"kind": "host", "text": host})
    for kind, text in (("port", port), ("path", path), ("query", query), ("fragment", fragment)):
        if text:
            parts.append({"kind": kind, "text": text})
    assert "".join(part["text"] for part in parts) == url
    return parts


def get_signals(features, parsed):
    """Observed patterns plus exact evidence and a practical next step, not SHAP."""
    signals = []

    def add(id_, title, severity, present, detail, evidence, action):
        signals.append(dict(id=id_, title=title, severity=severity, present=bool(present),
                            detail=detail, evidence=[dict(label=k, value=snippet(str(v))) for k, v in evidence]
                            if present else [], action=action if present else ""))

    add("userinfo", "Hidden destination", "high", features["has_userinfo"],
        "Text before @ is not the real destination host. It is the URL's sign-in information; a familiar name here does not mean you are visiting that site.",
        [("Before @", parsed.userinfo + "@"), ("Actual host", parsed.host)],
        "Compare the actual host with the site you intended to visit. If they differ, use a known bookmark instead of this link.")
    add("ip", "IP address as host", "medium", features["has_ip_host"],
        "This link uses a numeric IP address instead of a named website. That makes the organisation behind it harder to recognise; legitimate services can also use IP addresses.",
        [("Numeric host", parsed.host)],
        "Confirm the address with the sender through a separate, trusted channel before entering personal information.")
    add("brand", "Brand in a subdomain", "high", features["brand_in_subdomain"],
        "A familiar brand appears in the prefix of the hostname. That prefix does not establish ownership by the brand; check the base domain and the complete host.",
        [("Brand words", ", ".join(matches(parsed.subdomain, BRANDS))), ("Subdomain", parsed.subdomain), ("Base domain", parsed.registrable_domain)],
        "Compare this domain with an address obtained independently from the organisation. A brand name in the prefix is not verification.")
    chars = list(dict.fromkeys(c for c in parsed.analysis_url if c in CONFUSABLE))
    add("unicode", "Look-alike characters", "high", features["has_confusable_unicode"],
        "Some characters resemble Latin letters but have different Unicode values. They can be legitimate language characters, yet make an unfamiliar address look familiar. This check covers only a limited character list.",
        [("Characters found", ", ".join(f"{c} (U+{ord(c):04X})" for c in chars))],
        "Compare the exact hostname with a trusted address. If the spelling is unclear, navigate using your own bookmark.")
    encodings = list(dict.fromkeys(re.findall(r"(?:%[0-9a-fA-F]{2})+", parsed.analysis_url)))[:6]
    def readable(code):
        try:
            return repr(unquote(code, errors="strict"))
        except UnicodeDecodeError:
            return "[non-UTF-8 bytes]"
    encoded_evidence = [("Encoded characters", ", ".join(f"{code} → {readable(code)}" for code in encodings))] if encodings else []
    if features["host_has_punycode"]:
        encoded_evidence.append(("Internationalised host", parsed.host))
        try:
            encoded_evidence.append(("Unicode spelling", idna.decode(parsed.host, uts46=True)))
        except idna.IDNAError:
            pass
    add("encoding", "Encoded URL characters", "medium", features["has_percent_encoding"] or features["host_has_punycode"],
        "Percent codes represent characters, while xn-- marks an internationalised domain. Both are normal URL formats, but can make the address harder to read. Decoding shown here is for reading only; it does not change the destination or model input.",
        encoded_evidence,
        "Read the actual host first. Encoded text in a path or query does not replace the hostname, and encoding alone is not evidence of phishing.")
    term_evidence = []
    for label, value in (("Sign-in text", parsed.userinfo), ("Host", parsed.host), ("Path", parsed.path), ("Query", parsed.query), ("Fragment", parsed.fragment)):
        found = matches(value, SUSPICIOUS_TERMS)
        if found:
            term_evidence.append((label + " terms", ", ".join(found)))
    add("terms", "Account-related terms", "low", features["has_suspicious_term"],
        "Words about signing in, accounts or verification appear in the address. Real login pages use these words too; their presence does not prove that the site is malicious.",
        term_evidence,
        "If the message asks you to sign in or verify an account, open the organisation's known website yourself before providing credentials.")
    add("subdomains", "Many subdomains", "medium", features["subdomain_count"] >= 3,
        "Several labels precede the base domain. They can make a long hostname harder to recognise, though legitimate sites also use subdomains.",
        [("Subdomain labels", features["subdomain_count"]), ("Prefix", parsed.subdomain), ("Base domain", parsed.registrable_domain)],
        "Identify the base domain and then read the complete hostname. Do not assume the first familiar word is the website owner.")
    add("length", "Long URL", "low", features["url_length"] > 120,
        "This address is longer than the 120-character display rule. Long links can hide important parts, but search, sharing and tracking links are often long too.",
        [("URL length", f'{features["url_length"]} characters')],
        "Use the breakdown to inspect the host before reading the path and parameters. Length alone is not a reason to trust or reject a link.")
    add("transport", "HTTP without TLS", "low", not features["uses_https"],
        "The address starts with HTTP rather than HTTPS, so it does not request an encrypted HTTPS connection. We have not connected to the site or checked its certificate.",
        [("Protocol", parsed.scheme + "://")],
        "Avoid sending passwords or payment information over HTTP. HTTPS in an address also does not verify who owns the site.")
    add("port", "Unusual connection port", "medium", features["has_nonstandard_port"],
        "This URL names a port other than the usual HTTP port 80 or HTTPS port 443. Development tools and legitimate services can also use custom ports.",
        [("Explicit port", parsed.port), ("Usual port for this protocol", 443 if parsed.scheme == "https" else 80)],
        "Confirm that the organisation expects this specific port before using the link. A custom port alone does not prove abuse.")
    brand_locations = []
    for label, value in (("Path", parsed.path), ("Query", parsed.query)):
        found = matches(value, BRANDS)
        if found:
            brand_locations.append((label + " brand words", ", ".join(found)))
    add("brand_path", "Brand words outside the host", "low", features["brand_in_path_or_query"],
        "A familiar brand appears in the path or parameters. Those words do not determine which website receives the request; they can also occur in legitimate articles, search results and links.",
        brand_locations + [("Actual host", parsed.host)],
        "Use the actual hostname to identify the destination, rather than a brand name later in the URL.")
    return signals
