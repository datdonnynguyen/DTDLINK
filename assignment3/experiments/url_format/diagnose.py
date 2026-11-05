"""Read-only A2 lineage/data audit. Never train on or score A2 test rows."""
import hashlib
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
PROJECT = HERE.parents[2]
BACKEND = HERE.parents[1] / 'backend'
sys.path.insert(0, str(BACKEND))
sys.path.insert(0, str(BACKEND / 'src'))
from app.service import predict
from dtdlink_ml.predict import load_pipeline
from app.schemas import PredictRequest
from dtdlink_ml.feature_extraction import FEATURE_NAMES, file_sha256, url_id

FEATURE_HASH = 'fe049dd9f6b2c92570354b28b2885312f64c73b03b7053be06bc35cce5a591ff'
SPLIT_HASH = 'fbcbcf2ff68e26acfa2bb435b53c262645688a54a195ff64e283e7ff753ffc2f'


def write_json(path, value):
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + '\n')


def metrics(y, probability):
    y = np.asarray(y, dtype=int)
    p = np.asarray(probability) >= .5
    tn, fp = int(((y == 0) & ~p).sum()), int(((y == 0) & p).sum())
    fn, tp = int(((y == 1) & ~p).sum()), int(((y == 1) & p).sum())
    return dict(rows=len(y), benign=int((y == 0).sum()), dangerous=int((y == 1).sum()),
                tn=tn, fp=fp, fn=fn, tp=tp, fpr=fp/(tn+fp), recall=tp/(tp+fn),
                precision=tp/(tp+fp) if tp+fp else 0., accuracy=(tp+tn)/len(y))


def load_allowed():
    feature_path = PROJECT / 'data/processed/url_features.csv'
    split_path = PROJECT / 'data/processed/split_manifest.csv'
    assert file_sha256(feature_path) == FEATURE_HASH
    assert file_sha256(split_path) == SPLIT_HASH
    manifest = pd.read_csv(split_path, keep_default_na=False)
    assert not manifest.url_id.duplicated().any()
    assert manifest.groupby('group_key')['split'].nunique().max() == 1
    wanted = {s: [] for s in ['train', 'validation']}
    start = 0
    for chunk in pd.read_csv(feature_path, keep_default_na=False, chunksize=50000):
        part = manifest.iloc[start:start+len(chunk)]
        # Verify source-row alignment; labels/features of test rows are not retained or scored.
        assert np.array_equal(chunk.url.map(url_id).values, part.url_id.values)
        for split in wanted:
            mask = part['split'].values == split
            selected = chunk.loc[mask].copy()
            selected['url_id'] = part.url_id.values[mask]
            selected['group_key'] = part.group_key.values[mask]
            wanted[split].append(selected)
        start += len(chunk)
    assert start == len(manifest)
    return {key: pd.concat(parts, ignore_index=True) for key, parts in wanted.items()}, manifest


def main():
    results = HERE / 'results'
    cache = HERE / 'cache'
    results.mkdir(exist_ok=True); cache.mkdir(exist_ok=True)
    frozen = {}
    for directory in ['data', 'models', 'reports', 'src', 'tests', 'notebooks']:
        for path in sorted((PROJECT/directory).rglob('*')):
            if path.is_file() and '__pycache__' not in path.parts:
                frozen[str(path.relative_to(PROJECT))] = file_sha256(path)
    for path in (PROJECT/'submission').glob('*assignment-2*.zip'):
        frozen[str(path.relative_to(PROJECT))] = file_sha256(path)
    write_json(results/'a2-protected-before.json', frozen)
    data, manifest = load_allowed()
    for split, frame in data.items():
        frame.to_pickle(cache/f'{split}-raw.pkl')
        frame['scheme_format'] = np.select([frame.url.str.match(r'(?i)^https://'), frame.url.str.match(r'(?i)^http://'), frame.url.str.contains(r'^[A-Za-z][A-Za-z0-9+.-]*://', regex=True)], ['https','http','other'], default='none')
        distribution = frame.groupby(['type','target','scheme_format'], dropna=False).size().rename('rows').reset_index()
        distribution['within_label_pct'] = 100*distribution.rows/distribution.groupby('type').rows.transform('sum')
        distribution.to_csv(results/f'{split}-scheme-distribution.csv', index=False)
        binary = frame.groupby(['target','scheme_format']).size().rename('rows').reset_index()
        binary['within_class_pct'] = 100*binary.rows/binary.groupby('target').rows.transform('sum')
        binary.to_csv(results/f'{split}-scheme-by-target.csv', index=False)
        print(split, distribution.to_string(index=False), flush=True)
    model = load_pipeline(PROJECT/"models/final_pipeline.joblib", PROJECT/"models/model_metadata.json")
    val = data['validation']
    probability = model.probability_from_features(val.loc[:, list(FEATURE_NAMES)])
    write_json(results/'baseline-raw-validation.json', metrics(val.target, probability))
    importance = pd.DataFrame({'feature':FEATURE_NAMES, 'impurity_importance':model.classifier.feature_importances_}).sort_values('impurity_importance', ascending=False)
    importance.to_csv(results/'baseline-feature-importance.csv', index=False)
    demos = ['https://www.google.com/', 'www.google.com/', 'https://github.com/', 'github.com/', 'http://www.google.com/', 'https://www.google.com', 'https://google.com/', 'HTTPS://WWW.GOOGLE.COM/']
    trace = []
    from app.main import create_app
    from fastapi.testclient import TestClient
    with TestClient(create_app(model_loader=lambda:model)) as client:
        for url in demos:
            row = model.predict_urls([url])[0]
            response = client.post('/predict', json={'url':url})
            if response.status_code == 200:
                direct = predict(model, url, 'diagnostic')
                assert np.allclose([response.json()['dangerous_probability'],direct['dangerous_probability']],row['dangerous_probability'],atol=1e-12,rtol=0)
                assert ''.join(part['text'] for part in response.json()['url_parts']) == url
                assert response.json()['predicted_class'] == int(row['dangerous_probability'] >= .5)
            trace.append(dict(url=url, model_probability=row['dangerous_probability'], api_status=response.status_code,
                              group_membership=sorted(set(manifest.loc[manifest.group_key.isin(['domain:google.com' if 'google' in url.lower() else 'domain:github.com']), 'split']))))
    write_json(results/'baseline-application-trace.json', trace)
    from dtdlink_ml.feature_extraction import extract_features
    paired = []
    for bare in ['www.google.com/', 'github.com/']:
        before = extract_features(bare); after = extract_features('https://'+bare)
        changes = {key:{'no_scheme':before[key], 'https':after[key]} for key in FEATURE_NAMES if before[key] != after[key]}
        flips = {}
        X = model.features_from_urls(['https://'+bare])
        for key in changes:
            altered = X.copy(); altered.loc[0,key] = before[key]
            flips[key] = float(model.probability_from_features(altered)[0])
        paired.append(dict(bare=bare, feature_changes=changes, one_feature_reset_probabilities=flips,
                           note='Controlled feature interventions can be off-manifold; diagnostic, not a causal explanation or production fix.'))
    write_json(results/'baseline-format-feature-deltas.json', paired)
    print(json.dumps({'baseline':metrics(val.target, probability),'trace':trace},indent=2), flush=True)


if __name__ == '__main__':
    main()
