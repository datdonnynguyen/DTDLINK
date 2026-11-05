"""A3-only model-view consistency without hiding raw URL security information."""
import socket

import pytest
from app.analysis import get_signals, split_display_parts
from app.schemas import PredictRequest
from dtdlink_a3.representation import canonical_model_view, model_features
from dtdlink_ml.feature_extraction import extract_features
from dtdlink_ml.url_parser import parse_url


@pytest.mark.parametrize('variants',[
    ['https://example.com','HTTPS://EXAMPLE.COM/','https://example.com:443/'],
    ['http://example.com','HTTP://EXAMPLE.COM:80/','http://example.com/'],
    ['https://example.com/','http://example.com/','example.com/'],
    ['http://[2001:db8::1]/','HTTP://[2001:DB8::1]:80/'],
])
def test_documented_variants_share_numeric_model_features(variants):
    first=model_features(variants[0])
    assert all(model_features(url)==first for url in variants)


@pytest.mark.parametrize('url',[
    'https://paypal.com@account-check.example/login',
    'https://example.com/%2F?next=%40#login',
    'https://example.com/Path?A=1&A=2#Section',
    'https://www.example.com/',
    'https://example.com/?#',
])
def test_security_bearing_parts_are_retained(url):
    canonical,_=canonical_model_view(url)
    assert canonical==url
    assert ''.join(p['text'] for p in split_display_parts(url))==url


def test_custom_ports_keep_meaning_for_original_transport():
    text,custom=canonical_model_view('http://example.com:443/')
    assert text=='https://example.com:443/' and custom
    assert model_features('http://example.com:443/')['has_nonstandard_port']==1
    assert model_features('https://example.com:443/')['has_explicit_port']==0
    assert model_features('http://example.com:8080/')['has_nonstandard_port']==1


def test_host_prefixes_and_path_case_are_not_collapsed():
    assert canonical_model_view('https://www.example.com/A')[0]!=canonical_model_view('https://example.com/A')[0]
    assert canonical_model_view('https://example.com/A')[0]!=canonical_model_view('https://example.com/a')[0]


def test_protocol_still_explained_from_raw_input_and_bare_input_rejected_by_api():
    url='http://example.com/'
    found=get_signals(extract_features(url),parse_url(url))
    assert next(s for s in found if s['id']=='transport')['present']
    assert model_features(url)['uses_https']==1  # intentionally neutral model view
    with pytest.raises(ValueError):
        PredictRequest(url='example.com/')


def test_representation_is_offline(monkeypatch):
    def forbidden(*args,**kwargs): raise AssertionError('Outbound request')
    monkeypatch.setattr(socket,'getaddrinfo',forbidden)
    monkeypatch.setattr(socket.socket,'connect',forbidden)
    assert model_features('https://раypal.example/login')['has_confusable_unicode']==1
