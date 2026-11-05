"""A3-only RF adapter: the same representation is used for training/inference."""
import json
from dataclasses import dataclass
from pathlib import Path

import joblib
import pandas as pd
from dtdlink_ml.feature_extraction import FEATURE_NAMES, file_sha256
from dtdlink_ml.predict import RawURLPipeline, check_urls
from .representation import POLICY_ID, model_features


@dataclass
class A3URLPipeline(RawURLPipeline):
    representation: str = POLICY_ID

    def check_model(self):
        super().check_model()
        if self.representation != POLICY_ID:
            raise ValueError('Unsupported A3 input representation.')

    def features_from_urls(self, urls):
        return pd.DataFrame([model_features(url) for url in check_urls(urls)], columns=FEATURE_NAMES)


def load_pipeline(model_path, metadata_path):
    metadata=json.loads(Path(metadata_path).read_text())
    if file_sha256(model_path) != metadata['model_sha256']:
        raise ValueError('Model file does not match metadata.')
    model=joblib.load(model_path)
    if not isinstance(model,A3TextPipeline):
        raise ValueError('Expected the experimental A3 text pipeline.')
    model.check_model()
    if (metadata['feature_names'] != list(model.feature_names) or metadata['threshold'] != model.threshold
            or metadata['representation']['id'] != model.representation
            or metadata['feature_count'] != model.feature_count):
        raise ValueError('Model and representation metadata differ.')
    return model


TEXT_POLICY_ID = POLICY_ID + '-char3to5-numeric36-v1'
TEXT_ONLY_POLICY_ID = POLICY_ID + '-authority-char3to5-no-l2-v1'


@dataclass
class A3TextPipeline(RawURLPipeline):
    """Sparse URL character patterns plus the 36 neutral numeric measurements."""
    vectorizer: object = None
    scaler: object = None
    representation: str = TEXT_POLICY_ID
    use_numeric: bool = True

    @property
    def feature_count(self):
        return len(self.vectorizer.vocabulary_) + (len(self.feature_names) if self.use_numeric else 0)

    def check_model(self):
        if (self.representation != (TEXT_POLICY_ID if self.use_numeric else TEXT_ONLY_POLICY_ID) or tuple(self.feature_names) != FEATURE_NAMES
                or list(self.classifier.classes_) != [0, 1]
                or (self.use_numeric and self.scaler.n_features_in_ != len(FEATURE_NAMES))
                or (not self.use_numeric and self.vectorizer.norm is not None)
                or self.classifier.n_features_in_ != self.feature_count
                or self.vectorizer.analyzer != 'char'
                or self.vectorizer.ngram_range != (3, 5)
                or self.vectorizer.lowercase is not False):
            raise ValueError('A3 text pipeline and its feature contract differ.')

    def features_from_urls(self, urls):
        import numpy as np
        from scipy import sparse
        from .representation import canonical_model_view
        urls=check_urls(urls)
        text=[canonical_model_view(url)[0] for url in urls]
        if not self.use_numeric:
            return self.vectorizer.transform([value[len('https://'):] for value in text])
        numeric=pd.DataFrame([model_features(url) for url in urls],columns=FEATURE_NAMES)
        return sparse.hstack([self.vectorizer.transform(text),
                              sparse.csr_matrix(self.scaler.transform(numeric).astype(np.float32))],format='csr',dtype=np.float32)

    def probability_from_features(self, X):
        import numpy as np
        if X.shape[1] != self.feature_count or not np.isfinite(X.data).all():
            raise ValueError('A3 text feature matrix differs from its trained contract.')
        return self.classifier.predict_proba(X)[:, 1]
