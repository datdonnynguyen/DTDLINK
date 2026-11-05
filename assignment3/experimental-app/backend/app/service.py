"""Load the separate experimental A3 artifact once; retain raw URL explanations."""
import sys
import time

from .config import BACKEND, MODEL_SHA256

sys.path.insert(0, str(BACKEND / "src"))
from dtdlink_ml.feature_extraction import extract_features, file_sha256
from dtdlink_a3.pipeline import load_pipeline
from dtdlink_ml.url_parser import parse_url
from .analysis import get_signals, split_display_parts

MODEL_VERSION = "a3-preview-text-f5a7b6fb"
MODEL_NAME = "Experimental URL text classifier"
MODEL_FEATURE_COUNT = 100036
DISCLAIMER = "Experimental A3 preview. DTDLINK analyses URL text only. It does not visit the website. A benign prediction does not guarantee safety."


def load_model():
    artifact = BACKEND / "models" / "final_pipeline.joblib"
    if file_sha256(artifact) != MODEL_SHA256:
        raise RuntimeError("Model integrity verification failed; refusing to load.")
    return load_pipeline(artifact, BACKEND / "models" / "model_metadata.json")


def predict(model, url, request_id):
    started = time.perf_counter()
    result = model.predict_urls([url])[0]
    parsed = parse_url(url)
    features = extract_features(url)
    dangerous = result["predicted_class"] == 1
    probability = result["dangerous_probability"]
    return {
        "request_id": request_id,
        "predicted_class": result["predicted_class"],
        "label": "Potentially dangerous" if dangerous else "Likely legitimate",
        "explanation": ("The model predicts the combined risk class: phishing, malware or defacement. It cannot identify the subtype."
                        if dangerous else "The model predicts the benign class. This does not guarantee that the URL is safe."),
        "dangerous_probability": probability,
        "confidence": probability if dangerous else 1 - probability,
        "threshold": result["threshold"],
        "uncertain": 0.4 <= probability <= 0.6,
        "signals": get_signals(features, parsed),
        "url_parts": split_display_parts(url),
        "components": dict(scheme=parsed.scheme, host=parsed.host, registrable_domain=parsed.registrable_domain,
                           port=parsed.port, path_length=features["path_length"], query_parameter_count=features["query_parameter_count"]),
        "analysis_ms": round((time.perf_counter() - started) * 1000, 2),
        "model_version": MODEL_VERSION,
        "disclaimer": DISCLAIMER,
    }
