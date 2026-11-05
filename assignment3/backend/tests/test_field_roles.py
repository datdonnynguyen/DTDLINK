"""Contract checks for the isolated, unpromoted component-role experiment."""
import socket

import numpy as np
import pytest
from sklearn.feature_extraction.text import TfidfVectorizer

from dtdlink_a3.fields import FIELD_NAMES, FLAG_NAMES, encode_records, field_record


def test_actual_domain_and_deceptive_text_have_distinct_roles(monkeypatch):
    def forbidden(*args, **kwargs):
        raise AssertionError('Unexpected network access')
    monkeypatch.setattr(socket, 'getaddrinfo', forbidden)
    monkeypatch.setattr(socket.socket, 'connect', forbidden)
    actual, _, _ = field_record('https://google.com/login')
    userinfo, flags, _ = field_record('https://google.com@account-check.example.net/login')
    subdomain, _, _ = field_record('https://google.com.account-check.example.net/login')
    assert actual['base_domain'] == 'google.com'
    assert userinfo['base_domain'] == subdomain['base_domain'] == 'example.net'
    assert userinfo['userinfo'] == 'google.com'
    assert subdomain['subdomain'] == 'google.com.account-check'
    assert flags[FLAG_NAMES.index('has_userinfo')] == 1


@pytest.mark.parametrize('urls', [
    ['https://example.com', 'HTTPS://EXAMPLE.COM:443/', 'example.com/'],
    ['http://www.example.com', 'https://www.example.com/', 'HTTP://WWW.EXAMPLE.COM:80/'],
])
def test_format_variants_share_field_records(urls):
    assert all(field_record(u) == field_record(urls[0]) for u in urls)


def test_sensitive_content_and_nonstandard_port_remain_visible():
    fields, flags, _ = field_record('http://www.example.com:443/A%2F?X=1&X=2#Section')
    assert fields == dict(base_domain='example.com', subdomain='www',
                          path='/A%2F', query='X=1&X=2', userinfo='',
                          fragment='Section', port='443')
    assert flags[FLAG_NAMES.index('has_nonstandard_port')] == 1
    assert field_record('https://example.com/A') != field_record('https://example.com/a')


def test_same_text_in_path_and_query_uses_different_matrix_blocks():
    # Tiny vocabulary fixture tests layout only; never used by an experiment fit.
    vectorizers = {name: TfidfVectorizer(analyzer='char', ngram_range=(1, 1),
                                        lowercase=False, dtype=np.float32).fit(['login'])
                   for name in FIELD_NAMES}
    rows = [field_record(u) for u in ['https://example.com/login', 'https://example.com/?login']]
    matrix = encode_records(rows, vectorizers)
    sizes = [len(v.vocabulary_) for v in vectorizers.values()]
    path_start, query_start = sum(sizes[:2]), sum(sizes[:3])
    assert matrix[0, path_start:query_start].nnz > 0
    assert matrix[1, path_start:query_start].nnz == 0
    assert matrix[0, query_start:sum(sizes[:4])].nnz == 0
    assert matrix[1, query_start:sum(sizes[:4])].nnz > 0
    vectorizers['userinfo'] = None  # Actual train population has no usable vocabulary.
    assert encode_records(rows, vectorizers).shape[1] == matrix.shape[1] - sizes[4]


def test_root_context_adds_host_blocks_only_to_root_paths():
    vectorizers = {name: None for name in FIELD_NAMES}
    vectorizers['base_domain'] = TfidfVectorizer(analyzer='char').fit(['example.com'])
    rows = [field_record(u) for u in ['https://example.com/', 'https://example.com/login']]
    basic = encode_records(rows, vectorizers)
    contextual = encode_records(rows, vectorizers, root_context=True)
    assert contextual[0, basic.shape[1]:].nnz > 0
    assert contextual[1, basic.shape[1]:].count_nonzero() == 0


def test_unknown_suffix_does_not_claim_a_known_registered_domain():
    fields, _, _ = field_record('https://google.com.account-check.example/login')
    # Original offline parser falls back to the whole hostname for unknown suffixes.
    assert fields['base_domain'] == 'google.com.account-check.example'
