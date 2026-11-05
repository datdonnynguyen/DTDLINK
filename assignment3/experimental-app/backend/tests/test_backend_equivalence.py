"""Ensure the deployable copy stays byte-identical to the frozen A2 inference source."""
from pathlib import Path
import pytest
from app.config import BACKEND
from app.service import load_model


def test_a2_inference_source_is_unchanged_when_parent_project_is_available():
    parent = BACKEND.parents[1]
    original = parent / 'src' / 'dtdlink_ml'
    if not original.exists():
        pytest.skip('Standalone submission: original A2 workspace is intentionally absent.')
    for name in ['__init__.py', 'predict.py', 'url_parser.py', 'feature_extraction.py']:
        assert (BACKEND/'src'/'dtdlink_ml'/name).read_bytes() == (original/name).read_bytes()
