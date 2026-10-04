"""Reusable offline raw-URL inference and the saved Stage 7 model contract."""
from __future__ import annotations

import argparse
from dataclasses import dataclass
import json
from pathlib import Path
import platform
from typing import Sequence

import joblib
import numpy as np
import pandas as pd
import sklearn

from dtdlink_ml.feature_extraction import FEATURE_NAMES, extract_features, file_sha256
from dtdlink_ml.url_parser import parse_url

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_MODEL = ROOT / 'models/final_pipeline.joblib'
DEFAULT_METADATA = ROOT / 'models/model_metadata.json'
LABEL_MAPPING = {'benign': 0, 'phishing': 1, 'malware': 1, 'defacement': 1}


def implementation_hashes():
    """Detect changes to inference code, including rules and bundled PSL use."""
    directory = Path(__file__).resolve().parent
    return {name: file_sha256(directory / name)
            for name in ('url_parser.py', 'feature_extraction.py', 'predict.py')}


def runtime_versions():
    return {'python': platform.python_version(), 'numpy': np.__version__,
            'pandas': pd.__version__, 'scikit-learn': sklearn.__version__,
            'joblib': joblib.__version__}


@dataclass
class RawURLPipeline:
    """Classifier plus feature order, offline extractor contract and threshold.

    No additional scaler/lookup is required by the selected Random Forest.
    The Python parser/extractor must accompany the serialized artifact.
    """
    classifier: object
    feature_names: tuple = FEATURE_NAMES
    threshold: float = 0.5

    def validate_contract(self):
        if tuple(self.feature_names) != FEATURE_NAMES:
            raise ValueError('Saved feature schema differs from current extractor.')
        if not 0 < self.threshold < 1:
            raise ValueError('Invalid saved threshold.')
        if list(self.classifier.classes_) != [0, 1]:
            raise ValueError('Classifier must have classes [0, 1].')
        if tuple(self.classifier.feature_names_in_) != tuple(self.feature_names):
            raise ValueError('Classifier feature order differs from saved schema.')

    def probability_from_features(self, frame):
        """Strict schema check prevents silently swapped/extra feature columns."""
        self.validate_contract()
        if tuple(frame.columns) != tuple(self.feature_names):
            raise ValueError('Input feature columns/order differ from saved schema.')
        values = frame.to_numpy(dtype=float)
        if not np.isfinite(values).all() or (values < 0).any():
            raise ValueError('Features must be finite and nonnegative.')
        scores = self.classifier.predict_proba(frame)[:, 1]
        if not np.isfinite(scores).all() or ((scores < 0) | (scores > 1)).any():
            raise ValueError('Invalid classifier probabilities.')
        return scores

    def features_from_urls(self, urls: Sequence[str]):
        if isinstance(urls, (str, bytes)):
            raise ValueError('Pass a list of URL strings, not a single string.')
        urls = list(urls)
        if not urls or any(not isinstance(url, str) or not url.strip() for url in urls):
            raise ValueError('URLs must be nonempty strings.')
        return pd.DataFrame([extract_features(url) for url in urls], columns=self.feature_names)

    def predict_proba(self, urls):
        positive = self.probability_from_features(self.features_from_urls(urls))
        return np.column_stack([1 - positive, positive])

    def predict(self, urls):
        return (self.predict_proba(urls)[:, 1] >= self.threshold).astype(int)

    def predict_urls(self, urls):
        """Do not persist input URLs or present a negative result as safe."""
        urls = list(urls) if not isinstance(urls, (str, bytes)) else urls
        features = self.features_from_urls(urls)
        probabilities = self.probability_from_features(features)
        results = []
        for url, probability in zip(urls, probabilities):
            parsed = parse_url(url)
            positive = bool(probability >= self.threshold)
            results.append({'predicted_class': int(positive),
                'label': 'Potentially dangerous' if positive else 'No elevated signal detected; safety not guaranteed',
                'dangerous_probability': float(probability), 'threshold': self.threshold,
                'probability_calibrated': False, 'parse_ok': bool(parsed.parse_ok),
                'parse_issues': list(parsed.issues)})
        return results


def load_pipeline(model_path=DEFAULT_MODEL, metadata_path=DEFAULT_METADATA):
    """Load only the project's trusted artifact; verify bytes and environment first."""
    model_path, metadata_path = Path(model_path), Path(metadata_path)
    metadata = json.loads(metadata_path.read_text(encoding='utf-8'))
    if file_sha256(model_path) != metadata['model_sha256']:
        raise ValueError('Model hash differs from metadata.')
    if implementation_hashes() != metadata['implementation_sha256']:
        raise ValueError('Inference implementation changed since export.')
    if runtime_versions() != metadata['runtime_versions']:
        raise ValueError('Runtime versions differ from the exported environment.')
    pipeline = joblib.load(model_path)
    if not isinstance(pipeline, RawURLPipeline):
        raise ValueError('Unsupported pipeline artifact.')
    pipeline.validate_contract()
    if (metadata['feature_names'] != list(pipeline.feature_names)
            or metadata['threshold'] != pipeline.threshold
            or metadata['label_mapping'] != LABEL_MAPPING):
        raise ValueError('Metadata differs from saved pipeline contract.')
    return pipeline


def main():
    parser = argparse.ArgumentParser(description='Offline DTDLINK prediction; does not save URLs.')
    parser.add_argument('url', help='URL text; it is never visited')
    args = parser.parse_args()
    print(json.dumps(load_pipeline().predict_urls([args.url])[0], indent=2, ensure_ascii=True))


if __name__ == '__main__':
    main()
