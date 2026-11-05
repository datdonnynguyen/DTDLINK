"""Classify URL text offline using the saved model."""

import argparse
import json
from dataclasses import dataclass
from pathlib import Path

import joblib
import numpy as np
import pandas as pd

from dtdlink_ml.feature_extraction import FEATURE_NAMES, extract_features, file_sha256
from dtdlink_ml.url_parser import parse_url

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_MODEL = ROOT / "models/final_pipeline.joblib"
DEFAULT_METADATA = ROOT / "models/model_metadata.json"


def check_urls(urls):
    if isinstance(urls, (str, bytes)):
        raise ValueError("Pass a list of URL strings, not a single string.")
    urls = list(urls)
    if not urls or any(not isinstance(url, str) or not url.strip() for url in urls):
        raise ValueError("URLs must be nonempty strings.")
    return urls


@dataclass
class RawURLPipeline:
    """The saved model: classifier + feature order + threshold."""
    classifier: object
    feature_names: tuple = FEATURE_NAMES
    threshold: float = 0.5

    def check_model(self):
        """The classifier must use the same features (in the same order) as the extractor."""
        if tuple(self.feature_names) != FEATURE_NAMES:
            raise ValueError("Saved feature list differs from the current extractor.")
        if tuple(self.classifier.feature_names_in_) != FEATURE_NAMES:
            raise ValueError("Classifier was trained with a different feature order.")
        if list(self.classifier.classes_) != [0, 1]:
            raise ValueError("Classifier must have classes [0, 1].")

    def features_from_urls(self, urls):
        rows = [extract_features(url) for url in check_urls(urls)]
        return pd.DataFrame(rows, columns=self.feature_names)

    def probability_from_features(self, X):
        """Probability of 'dangerous' for each row of a feature table."""
        if tuple(X.columns) != tuple(self.feature_names):
            raise ValueError("Input feature columns/order differ from the model.")
        if not np.isfinite(X.to_numpy(dtype=float)).all():
            raise ValueError("Features must be finite numbers.")
        return self.classifier.predict_proba(X)[:, 1]

    def predict_proba(self, urls):
        """[benign, dangerous] probabilities for each URL."""
        probabilities = self.probability_from_features(self.features_from_urls(urls))
        return np.column_stack([1 - probabilities, probabilities])

    def predict(self, urls):
        return (self.predict_proba(urls)[:, 1] >= self.threshold).astype(int)

    def predict_urls(self, urls):
        """Readable result for each URL (the URL itself is not included in the output)."""
        urls = check_urls(urls)
        probabilities = self.probability_from_features(self.features_from_urls(urls))
        results = []
        for url, probability in zip(urls, probabilities):
            parsed = parse_url(url)
            dangerous = bool(probability >= self.threshold)
            if dangerous:
                label = "Potentially dangerous"
            else:
                label = "Predicted benign"
            results.append({
                "predicted_class": int(dangerous),
                "label": label,
                "dangerous_probability": float(probability),
                "threshold": self.threshold,
                "parse_ok": bool(parsed.parse_ok),
                "parse_issues": list(parsed.issues),
            })
        return results


def load_pipeline(model_path=DEFAULT_MODEL, metadata_path=DEFAULT_METADATA):
    """Load the saved model and check it against model_metadata.json."""
    meta = json.loads(Path(metadata_path).read_text(encoding="utf-8"))
    if file_sha256(model_path) != meta["model_sha256"]:
        raise ValueError("Model file does not match the hash in the metadata.")
    model = joblib.load(model_path)
    if not isinstance(model, RawURLPipeline):
        raise ValueError("Model file does not contain a RawURLPipeline.")
    model.check_model()
    if meta["feature_names"] != list(model.feature_names) or meta["threshold"] != model.threshold:
        raise ValueError("Metadata does not match the saved model.")
    return model


if __name__ == "__main__":
    # import by name, because the saved model points to dtdlink_ml.predict, not __main__
    from dtdlink_ml import predict

    parser = argparse.ArgumentParser(description="Offline DTDLINK URL check.")
    parser.add_argument("url", help="URL text (it is not visited)")
    args = parser.parse_args()
    res = predict.load_pipeline().predict_urls([args.url])[0]
    print(json.dumps(res, indent=2, ensure_ascii=True))
