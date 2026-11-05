"""Independently recompute decisions and check saved/raw inference agreement."""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
from diagnose import BACKEND, write_json
from dtdlink_a3.fields import encode_records
from dtdlink_ml.feature_extraction import file_sha256
import joblib
import numpy as np
import pandas as pd


def main():
    plan = json.loads((HERE / 'PLAN.json').read_text())
    receipt = json.loads((HERE / 'results/plan-receipt.json').read_text())
    assert receipt['sha256'] == file_sha256(HERE / 'PLAN.json')
    val = pd.read_pickle(HERE.parent / 'cache/validation-eligible.pkl')
    _, records = joblib.load(HERE / 'cache/records.joblib')
    y = val.target.to_numpy()
    home = np.array([r[2] and not r[0]['query'] for r in records])
    selection = json.loads((HERE / 'results/decision.json').read_text())
    checked = []
    sample = np.random.default_rng(20261106).choice(len(val), 1000, replace=False)
    for spec in plan['candidates']:
        name = spec['name']
        artifact = HERE / 'artifacts' / (name + '.joblib')
        m = joblib.load(artifact)
        m.check_model()
        p = np.load(HERE / 'cache' / (name + '-validation-prob.npy'))
        assert p.shape == y.shape and np.isfinite(p).all()
        assert ((0 <= p) & (p <= 1)).all()
        r = json.loads((HERE / 'results' / (name + '.json')).read_text())
        # Re-transform every validation record through the deserialised model.
        reproduced = m.probability_from_features(encode_records(records, m.vectorizers, m.root_context))
        np.testing.assert_allclose(reproduced, p, atol=1e-7, rtol=0)
        # Additionally exercise the public raw-URL interface after reloading.
        raw = m.predict_proba(val.api_url.iloc[sample].tolist())[:, 1]
        np.testing.assert_allclose(raw, p[sample], atol=1e-7, rtol=0)
        for mask, key in [(np.ones(len(y), dtype=bool), 'api_formatted'), (home, 'homepage_no_query')]:
            actual, pred = y[mask], p[mask] >= .5
            counts = {'tn': int(((actual == 0) & ~pred).sum()),
                      'fp': int(((actual == 0) & pred).sum()),
                      'fn': int(((actual == 1) & ~pred).sum()),
                      'tp': int(((actual == 1) & pred).sum())}
            assert all(r[key][k] == v for k, v in counts.items())
            assert abs(r[key]['fpr'] - counts['fp'] / (counts['fp'] + counts['tn'])) < 1e-12
            assert abs(r[key]['recall'] - counts['tp'] / (counts['tp'] + counts['fn'])) < 1e-12
        g = plan['acceptance']
        independently_passes = (r['api_formatted']['fpr'] <= g['whole_fpr_max']
                               and r['api_formatted']['recall'] >= g['dangerous_recall_min']
                               and r['homepage_no_query']['fpr'] <= g['homepage_fpr_max']
                               and r['homepage_no_query']['recall'] >= g['homepage_dangerous_recall_min']
                               and r['api_formatted']['subtypes']['phishing']['recall'] >= g['phishing_recall_min']
                               and all(r['gates'].values()))
        assert independently_passes == r['passes']
        checked.append({'name': name, 'sha256': file_sha256(artifact),
                        'full_validation_predictions_reproduced': len(p),
                        'fresh_raw_url_predictions_reproduced': len(sample),
                        'passes': independently_passes})
        print(name, 'verified', flush=True)
    assert not any(r['passes'] for r in checked) and selection['selected'] is None
    assert file_sha256(BACKEND / 'models/final_pipeline.joblib') == 'd4aa8ff332ab82c36e3befce1a0e74c336b25a07a19ee9012e489c56239cb586'
    assert file_sha256(BACKEND.parent / 'experimental-app/backend/models/final_pipeline.joblib') == 'f5a7b6fb18fa3c041ccac167436ddc9d3ea44f496842314c59070a7e36303290'
    write_json(HERE / 'results/verification.json', {
        'passed': True, 'candidates': checked, 'threshold': .5,
        'primary_model_sha256': file_sha256(BACKEND / 'models/final_pipeline.joblib'),
        'preview_model_sha256': file_sha256(BACKEND.parent / 'experimental-app/backend/models/final_pipeline.joblib'),
        'decision': 'No promotion; retain both existing applications.'})


if __name__ == '__main__':
    main()
