"""Position-aware A3 feature blocks; no reputation lookup or domain allowlist."""
from dataclasses import dataclass, field
import numpy as np
from scipy import sparse
from dtdlink_ml.predict import RawURLPipeline, check_urls
from dtdlink_ml.url_parser import parse_url
from dtdlink_ml.feature_extraction import get_features
from .representation import canonical_model_view

FIELD_POLICY_ID = 'a3-url-fields-v1'
FIELD_NAMES = ('base_domain','subdomain','path','query','userinfo','fragment','port')
FLAG_NAMES = ('has_userinfo','has_ip_host','has_confusable_unicode','brand_in_subdomain',
              'brand_in_userinfo','brand_in_path_or_query','has_nonstandard_port',
              'has_encoded_separator','host_has_punycode')


def field_record(url):
    """Split the same neutral model view, preserving component roles and content."""
    canonical, custom = canonical_model_view(url)
    parsed = parse_url(canonical)
    features = get_features(parsed)
    features['has_nonstandard_port'] = int(custom)
    fields = {'base_domain':parsed.registrable_domain,'subdomain':parsed.subdomain,
              'path':parsed.path,'query':parsed.query,'userinfo':parsed.userinfo,
              'fragment':parsed.fragment,'port':str(parsed.port) if parsed.port is not None else ''}
    flags = [features[name] for name in FLAG_NAMES]
    return fields, flags, parsed.path == '/'


def encode_records(records, vectorizers, root_context=False):
    blocks=[]; host_blocks=[]
    for name in FIELD_NAMES:
        vectorizer=vectorizers[name]
        block=(vectorizer.transform([r[0][name] for r in records]) if vectorizer is not None
               else sparse.csr_matrix((len(records),0),dtype=np.float32))
        blocks.append(block)
        if name in ('base_domain','subdomain'):host_blocks.append(block)
    blocks.append(sparse.csr_matrix(np.asarray([r[1] for r in records],dtype=np.float32)))
    if root_context:
        mask=np.asarray([r[2] for r in records],dtype=np.float32).reshape(-1,1)
        blocks.extend(block.multiply(mask) for block in host_blocks)
    return sparse.hstack(blocks,format='csr',dtype=np.float32)


@dataclass
class FieldAwarePipeline(RawURLPipeline):
    vectorizers: dict = field(default_factory=dict)
    root_context: bool = False
    representation: str = FIELD_POLICY_ID

    @property
    def feature_count(self):
        sizes={name:(len(v.vocabulary_) if v is not None else 0) for name,v in self.vectorizers.items()}
        return sum(sizes.values())+len(FLAG_NAMES)+(sum(sizes.get(n,0) for n in ('base_domain','subdomain')) if self.root_context else 0)

    def check_model(self):
        if (self.representation!=FIELD_POLICY_ID or tuple(self.vectorizers)!=FIELD_NAMES
                or self.threshold!=.5 or list(self.classifier.classes_)!=[0,1]
                or self.classifier.n_features_in_!=self.feature_count):
            raise ValueError('Field-aware model contract mismatch.')
        for vectorizer in self.vectorizers.values():
            if vectorizer is not None and (vectorizer.analyzer!='char' or vectorizer.lowercase or vectorizer.norm!='l2'):
                raise ValueError('Unexpected field vectorizer.')

    def features_from_urls(self, urls):
        return encode_records([field_record(u) for u in check_urls(urls)],self.vectorizers,self.root_context)

    def probability_from_features(self, X):
        if X.shape[1]!=self.feature_count or not np.isfinite(X.data).all():
            raise ValueError('Invalid field-aware feature matrix.')
        return self.classifier.predict_proba(X)[:,1]
