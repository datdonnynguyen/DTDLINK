"""A3 model routes by URL structure, never by domain names or an allowlist."""
from dataclasses import dataclass
from urllib.parse import urlsplit
import numpy as np
import pandas as pd
from dtdlink_ml.feature_extraction import FEATURE_NAMES
from dtdlink_ml.predict import RawURLPipeline, check_urls
from .representation import canonical_model_view, model_features

ROUTED_POLICY_ID='a3-scheme-neutral-v1-root-rf-page-text-v1'


def root_path(url):
    return urlsplit(canonical_model_view(url)[0]).path == '/'


@dataclass
class RoutedFeatures:
    text: object
    numeric: object
    root: object

    @property
    def shape(self):
        return self.text.shape


@dataclass
class RootAwarePipeline(RawURLPipeline):
    root_pipeline: object = None
    text_pipeline: object = None
    representation: str = ROUTED_POLICY_ID

    @property
    def feature_count(self):
        return self.text_pipeline.feature_count

    def check_model(self):
        self.root_pipeline.check_model();self.text_pipeline.check_model()
        if (self.representation != ROUTED_POLICY_ID or tuple(self.feature_names) != FEATURE_NAMES
                or self.threshold != .5 or self.root_pipeline.threshold != .5 or self.text_pipeline.threshold != .5):
            raise ValueError('Routed A3 model contract differs.')

    def features_from_urls(self, urls):
        urls=check_urls(urls)
        return RoutedFeatures(self.text_pipeline.features_from_urls(urls),
                              pd.DataFrame([model_features(u) for u in urls],columns=FEATURE_NAMES),
                              np.array([root_path(u) for u in urls],dtype=bool))

    def probability_from_features(self, X):
        if not isinstance(X,RoutedFeatures) or X.shape[1] != self.feature_count:
            raise ValueError('Expected versioned routed URL features.')
        p=self.text_pipeline.probability_from_features(X.text)
        if X.root.any():
            p[X.root]=self.root_pipeline.probability_from_features(X.numeric.loc[X.root])
        return p
