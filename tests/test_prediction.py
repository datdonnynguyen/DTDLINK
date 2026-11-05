"""Tests for loading the saved model and predicting raw URLs."""
import json
import socket

import joblib
import numpy as np
import pytest
from sklearn.ensemble import RandomForestClassifier

from dtdlink_ml.feature_extraction import FEATURE_NAMES, file_sha256
from dtdlink_ml.predict import RawURLPipeline, load_pipeline


@pytest.fixture
def pipeline():
    result = RawURLPipeline(RandomForestClassifier(n_estimators=5, random_state=42))
    urls = ['https://example.com/', 'http://192.0.2.1/login',
            'https://example.org/a', 'http://192.0.2.2/verify']
    result.classifier.fit(result.features_from_urls(urls), [0, 1, 0, 1])
    return result


def save(pipeline, tmp_path):
    model, metadata = tmp_path / 'model.joblib', tmp_path / 'metadata.json'
    joblib.dump(pipeline, model)
    metadata.write_text(json.dumps({'model_sha256': file_sha256(model),
        'feature_names': list(FEATURE_NAMES), 'threshold': pipeline.threshold}))
    return model, metadata


def test_reload_preserves_raw_predictions_and_probability(pipeline, tmp_path):
    urls = ['https://example.com/', 'http://192.0.2.99/verify', 'https://[broken']
    restored = load_pipeline(*save(pipeline, tmp_path))
    np.testing.assert_array_equal(pipeline.predict_proba(urls), restored.predict_proba(urls))
    assert restored.predict_urls(urls) == pipeline.predict_urls(urls)


def test_prediction_cannot_connect_or_resolve_dns(pipeline, monkeypatch):
    def forbidden(*args, **kwargs):
        raise AssertionError('Network forbidden')
    monkeypatch.setattr(socket.socket, 'connect', forbidden)
    monkeypatch.setattr(socket, 'getaddrinfo', forbidden)
    urls = ['missing.example/login', 'https://[broken', 'http://192.0.2.1:99999',
            'https://exаmple.com/%2Flogin', 'https://example.com/' + 'a' * 10000]
    results = pipeline.predict_urls(urls)
    assert len(results) == 5
    assert results[1]['parse_ok'] is False
    assert all(0 <= row['dangerous_probability'] <= 1 for row in results)
    assert not any('url' in row for row in results)


@pytest.mark.parametrize('urls', [[], [''], ['  '], [None], [123], 'https://example.com'])
def test_reject_empty_or_wrong_input(pipeline, urls):
    with pytest.raises(ValueError):
        pipeline.predict_urls(urls)


def test_rejects_feature_order_and_nonfinite_data(pipeline):
    features = pipeline.features_from_urls(['https://example.com'])
    with pytest.raises(ValueError, match='columns/order'):
        pipeline.probability_from_features(features.iloc[:, ::-1])
    features.iloc[0, 0] = np.nan
    with pytest.raises(ValueError, match='finite'):
        pipeline.probability_from_features(features)


@pytest.mark.parametrize('probability, expected_class, label', [
    (0.499, 0, 'Predicted benign'),
    (0.5, 1, 'Potentially dangerous'),
])
def test_threshold_boundary_and_result_labels(pipeline, monkeypatch, probability, expected_class, label):
    monkeypatch.setattr(pipeline.classifier, 'predict_proba',
                        lambda frame: np.array([[1 - probability, probability]]))
    assert pipeline.predict(['https://example.com']).tolist() == [expected_class]
    result = pipeline.predict_urls(['https://example.com'])[0]
    assert result['predicted_class'] == expected_class
    assert result['label'] == label


@pytest.mark.parametrize('change', ['bytes', 'threshold', 'schema'])
def test_rejects_changed_artifact_contract(pipeline, tmp_path, change):
    model, metadata_path = save(pipeline, tmp_path)
    metadata = json.loads(metadata_path.read_text())
    if change == 'bytes':
        model.write_bytes(model.read_bytes() + b'changed')
    elif change == 'threshold':
        metadata['threshold'] = 0.4
    else:
        metadata['feature_names'] = list(reversed(FEATURE_NAMES))
    metadata_path.write_text(json.dumps(metadata))
    with pytest.raises(ValueError):
        load_pipeline(model, metadata_path)
