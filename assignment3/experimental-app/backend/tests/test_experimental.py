"""Confirm the preview is independent and its actual model uses the fitted view."""
from pathlib import Path
import json
import pytest
from fastapi.testclient import TestClient
from app.config import BACKEND
from app.main import create_app
from app.service import MODEL_VERSION,load_model
from dtdlink_a3.pipeline import A3TextPipeline
from dtdlink_ml.feature_extraction import file_sha256


def test_preview_loads_actual_text_model_and_reports_correct_dimension():
    model=load_model()
    assert isinstance(model,A3TextPipeline)
    assert MODEL_VERSION.startswith('a3-preview-text-')
    with TestClient(create_app(model_loader=lambda:model)) as client:
        assert client.get('/model-info').json()['feature_count']==model.features_from_urls(['https://example.com/']).shape[1]==100036


@pytest.mark.parametrize('urls',[
    ['https://example.com/','http://example.com/','HTTPS://EXAMPLE.COM','https://example.com:443/'],
    ['https://example.com/login?x=1','HTTP://EXAMPLE.COM/login?x=1','https://example.com:443/login?x=1'],
])
def test_real_preview_model_is_consistent_for_documented_variants(urls):
    probabilities=load_model().predict_proba(urls)[:,1]
    assert max(probabilities)-min(probabilities)<1e-12


def test_preview_origin_is_separate_from_primary_frontend():
    with TestClient(create_app()) as client:
        assert client.get('/health',headers={'Origin':'http://127.0.0.1:5174'}).headers['access-control-allow-origin']=='http://127.0.0.1:5174'
        assert client.get('/health',headers={'Origin':'http://127.0.0.1:5173'}).status_code==403


def test_primary_runtime_artifact_retained_when_workspace_exists():
    primary=BACKEND.parents[1]/'backend/models/final_pipeline.joblib'
    if not primary.exists():pytest.skip('Independent preview ZIP has no primary workspace.')
    assert file_sha256(primary)=='d4aa8ff332ab82c36e3befce1a0e74c336b25a07a19ee9012e489c56239cb586'
