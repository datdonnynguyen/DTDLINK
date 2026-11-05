"""Regression cases where a misleading explanation could change user judgement."""
import socket

import pytest
from app.service import get_signals, split_display_parts
from app.schemas import PredictRequest
from dtdlink_ml.feature_extraction import extract_features
from dtdlink_ml.url_parser import parse_url


def signals(url):
    return {s['id']: s for s in get_signals(extract_features(url), parse_url(url))}


@pytest.mark.parametrize('url', [
    'HTTPS://Example.COM.:00443/a%2Fb?next=https://other.example/#part',
    'http://user:pass@[2001:db8::1]:8080/a?x=1#section',
    'https://paypal.com@account-check.example/login',
    'https://@example.com/?#',
    'https://example.com/?redirect=https://paypal.com@other.example/',
    'https://example.com/a@b?x=@#@',
    'https://раypal.example/%D0%B0',
    'https://example.com/<svg/onload=alert(1)>?q=<script>',
])
def test_display_parts_reconstruct_exact_input_and_host_boundary(url):
    PredictRequest(url=url)
    parts = split_display_parts(url)
    assert ''.join(p['text'] for p in parts) == url
    assert sum(p['kind'] == 'host' for p in parts) == 1
    if url.startswith('https://example.com/'):
        assert next(p['text'] for p in parts if p['kind'] == 'host') == 'example.com'
        assert not any(p['kind'] == 'userinfo' for p in parts)


def test_userinfo_evidence_uses_real_host_and_preserves_brand_text():
    found = signals('https://paypal.com@account-check.example/login')
    s = found['userinfo']
    assert s['present'] and s['severity'] == 'high'
    assert s['evidence'] == [
        {'label': 'Before @', 'value': 'paypal.com@'},
        {'label': 'Actual host', 'value': 'account-check.example'},
    ]
    assert 'login' in str(found['terms']['evidence'])
    assert s['action']


def test_terms_have_word_boundaries_and_decoded_locations():
    found = signals('https://pineapple.example/blog/re%76erify?next=%6cogin')
    # "reverify" is not the vocabulary token "verify"; pineapple is not apple.
    assert not found['brand']['present']
    assert not found['brand_path']['present']
    assert found['terms']['evidence'] == [{'label': 'Query terms', 'value': 'login'}]


def test_nested_query_address_is_not_reported_as_actual_destination():
    url = 'https://example.com/?next=https://paypal.com@account-check.example/login'
    found = signals(url)
    assert not found['userinfo']['present']
    assert found['brand_path']['present']
    assert {'label': 'Actual host', 'value': 'example.com'} in found['brand_path']['evidence']


def test_encoding_is_readable_without_reinterpreting_authority():
    url = 'https://example.com/%40%2F?q=%D0%B0&space=%20'
    s = signals(url)['encoding']
    assert s['present']
    assert "%D0%B0 → 'а'" in str(s['evidence'])
    assert "%20 → ' '" in str(s['evidence'])
    assert 'not evidence of phishing' in s['action']
    assert not signals(url)['userinfo']['present']


def test_private_unicode_and_custom_port_explanations_are_cautious():
    found = signals('http://[::1]:8080/login')
    assert found['ip']['present'] and found['port']['present'] and found['transport']['present']
    assert not signals('https://example.com:443/')['port']['present']
    unicode = signals('https://раypal.example/login')['unicode']
    assert unicode['present'] and 'U+0440' in str(unicode['evidence'])
    punycode = signals('https://xn--pple-43d.com/')['encoding']
    assert any(item['label'] == 'Unicode spelling' for item in punycode['evidence'])


def test_absence_is_not_reported_as_evidence_and_long_values_are_bounded(monkeypatch):
    def forbidden(*args, **kwargs):
        raise AssertionError('Network access during explanation')
    monkeypatch.setattr(socket, 'getaddrinfo', forbidden)
    monkeypatch.setattr(socket.socket, 'connect', forbidden)
    clean = signals('https://example.com/')
    assert not any(s['present'] for s in clean.values())
    assert all(s['evidence'] == [] and s['action'] == '' for s in clean.values())
    long_url = 'https://' + 'a' * 180 + '@example.com/login'
    for s in signals(long_url).values():
        assert all(len(item['value']) <= 181 for item in s['evidence'])
