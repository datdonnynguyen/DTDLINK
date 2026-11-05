"""Versioned, scheme-neutral feature view; never used for URL display or visits."""
import re
from urllib.parse import urlsplit

from dtdlink_ml.feature_extraction import extract_features

POLICY_ID = 'a3-scheme-neutral-v1'


def complete_http_url(value):
    """Dataset recovery only; public API still requires explicit HTTP(S)."""
    if not isinstance(value, str) or not value or value != value.strip():
        raise ValueError('Expected a nonempty URL without surrounding spaces.')
    if re.match(r'^[A-Za-z][A-Za-z0-9+.-]*://', value):
        if not value.lower().startswith(('http://', 'https://')):
            raise ValueError('Unsupported scheme.')
        return value
    if value.startswith('//'):
        return 'https:' + value
    if value.lower().startswith(('http:', 'https:')):
        raise ValueError('Malformed HTTP scheme.')
    return 'https://' + value


def canonical_model_view(value):
    """Normalise only the documented model view; retain security-bearing content.

    Protocol is deliberately neutral for classification, not asserted to be safe
    or equivalent transport. HTTPS/HTTP warnings are computed from the raw URL.
    Host case, empty root path and default ports have a consistent representation.
    www, userinfo, custom ports, path/query case, encoding and fragments stay.
    """
    complete = complete_http_url(value)
    parts = urlsplit(complete)
    scheme = parts.scheme.lower()
    if scheme not in ('http', 'https') or not parts.hostname:
        raise ValueError('Expected a complete HTTP(S) hostname.')
    host = parts.hostname.lower().rstrip('.')
    if ':' in host:
        host = '[' + host + ']'
    userinfo = parts.netloc.rsplit('@', 1)[0] + '@' if '@' in parts.netloc else ''
    port = parts.port
    usual = 80 if scheme == 'http' else 443
    custom_port = port is not None and port != usual
    authority = userinfo + host + (f':{port}' if custom_port else '')
    # Preserve even empty query/fragment markers, without decoding/reordering.
    suffix = ''
    if '?' in complete.split('#', 1)[0]:
        suffix += '?' + parts.query
    if '#' in complete:
        suffix += '#' + parts.fragment
    canonical = 'https://' + authority + (parts.path or '/') + suffix
    return canonical, custom_port


def model_features(value):
    canonical, custom_port = canonical_model_view(value)
    features = extract_features(canonical)
    # A custom HTTP :443 is still custom, despite the scheme-neutral view.
    features['has_nonstandard_port'] = int(custom_port)
    return features
