"""Tests for the Stage 7 evaluation."""
import json
import numpy as np
import pandas as pd
import pytest

from dtdlink_ml.feature_extraction import FEATURE_NAMES, file_sha256, url_id
from dtdlink_ml.evaluate import (load_test, build_prediction_table,
    subgroup_table, select_error_examples, run_stage7)
import dtdlink_ml.evaluate as evaluation


def test_load_test_returns_only_test_rows_and_checks_hashes(tmp_path):
    rows, membership = [], []
    for i, split in enumerate(['train', 'validation', 'test', 'test']):
        url = f'https://domain{i}.com/'
        rows.append({'url': url, 'type': 'phishing', 'target': 1,
                     **{name: i for name in FEATURE_NAMES}})
        membership.append({'url_id': url_id(url), 'group_key': f'domain:domain{i}.com', 'split': split})
    feature, manifest = tmp_path / 'features.csv', tmp_path / 'manifest.csv'
    pd.DataFrame(rows).to_csv(feature, index=False)
    pd.DataFrame(membership).to_csv(manifest, index=False)
    selected = load_test(feature, manifest, file_sha256(feature), file_sha256(manifest))
    assert selected.url.tolist() == [rows[2]['url'], rows[3]['url']]
    with pytest.raises(ValueError, match='hash'):
        load_test(feature, manifest, 'wrong', file_sha256(manifest))
    pd.DataFrame(rows[::-1]).to_csv(feature, index=False)
    with pytest.raises(ValueError, match='align'):
        load_test(feature, manifest, file_sha256(feature), file_sha256(manifest))


def test_outcomes_and_subgroups_match_hand_calculation():
    frame = pd.DataFrame({'url_id': list('abcde'), 'url': ['x'] * 5,
        'type': ['benign', 'benign', 'phishing', 'malware', 'defacement'], 'target': [0, 0, 1, 1, 1],
        **{name: [0] * 5 for name in FEATURE_NAMES}})
    result = build_prediction_table(frame, [.1, .8, .2, .5, .9])
    assert result.outcome.tolist() == ['TN', 'FP', 'FN', 'TP', 'TP']
    subgroups = subgroup_table(result).set_index('source_type')
    assert subgroups.loc['benign', 'benign_false_alarm_rate'] == .5
    assert subgroups.loc['phishing', 'dangerous_recall'] == 0
    assert subgroups.loc['malware', 'dangerous_recall'] == 1
    examples = select_error_examples(frame, result)
    assert set(examples.url_id) == {'b', 'c'}
    with pytest.raises(ValueError):
        build_prediction_table(frame, [float('nan')] * 5)


def test_finished_run_is_not_repeated(tmp_path, monkeypatch):
    for name in ('REPORT_DIR', 'MODEL_DIR', 'FIGURE_DIR'):
        monkeypatch.setattr(evaluation, name, tmp_path)
    (tmp_path / 'test_metrics.json').write_text('{"f1": 0.9}')
    def forbidden():
        raise AssertionError('should not load data again')
    monkeypatch.setattr(evaluation, 'load_train_val', forbidden)
    monkeypatch.setattr(evaluation, 'load_test', forbidden)
    assert run_stage7() == {'f1': 0.9}


def test_model_is_fitted_on_train_before_test_is_loaded(tmp_path, monkeypatch):
    from dtdlink_ml.train_classifier import make_models, SELECTED_MODEL, SELECTED_THRESHOLD
    for name in ('REPORT_DIR', 'MODEL_DIR', 'FIGURE_DIR'):
        monkeypatch.setattr(evaluation, name, tmp_path)
    path = tmp_path / 'selection.json'
    path.write_text(json.dumps({'selected_model': SELECTED_MODEL, 'selected_threshold': SELECTED_THRESHOLD}))
    monkeypatch.setattr(evaluation, 'SELECTION_FILE', path)
    train = pd.DataFrame(0., index=[0, 1], columns=FEATURE_NAMES)
    train['target'] = [0, 1]
    validation = pd.DataFrame(999., index=[0], columns=FEATURE_NAMES)
    validation['target'] = [1]
    monkeypatch.setattr(evaluation, 'load_train_val', lambda: (train, validation, {}))
    model = make_models()[SELECTED_MODEL]
    fit_called = []
    def checked_fit(x, y):
        # only the train rows, never the validation rows
        assert len(x) == 2 and x.to_numpy().max() == 0
        fit_called.append(True)
    monkeypatch.setattr(model, 'fit', checked_fit)
    monkeypatch.setattr(evaluation, 'make_models', lambda: {SELECTED_MODEL: model})
    def stop():
        assert fit_called == [True]
        raise RuntimeError('fit happened first')
    monkeypatch.setattr(evaluation, 'load_test', stop)
    with pytest.raises(RuntimeError, match='fit happened first'):
        run_stage7()
