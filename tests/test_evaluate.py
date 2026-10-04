"""Independent final metrics, locked test selection and frozen-fit checks."""
import json
import numpy as np
import pandas as pd
import pytest

from dtdlink_ml.feature_extraction import FEATURE_NAMES, file_sha256
from dtdlink_ml.train_classifier import _url_id
from dtdlink_ml.evaluate import (load_final_test, build_prediction_table,
    subgroup_table, select_error_examples, run_stage7)
import dtdlink_ml.evaluate as evaluation


def test_final_loader_selects_only_locked_test_and_checks_identity(tmp_path):
    rows, membership = [], []
    for i, split in enumerate(['train', 'validation', 'test', 'test']):
        url = f'https://domain{i}.com/'
        rows.append({'url': url, 'type': 'phishing', 'target': 1,
                     **{name: i for name in FEATURE_NAMES}})
        membership.append({'url_id': _url_id(url), 'group_key': f'domain:domain{i}.com', 'split': split})
    feature, manifest = tmp_path / 'features.csv', tmp_path / 'manifest.csv'
    pd.DataFrame(rows).to_csv(feature, index=False)
    pd.DataFrame(membership).to_csv(manifest, index=False)
    selected = load_final_test(feature, manifest, file_sha256(feature), file_sha256(manifest))
    assert selected.url.tolist() == [rows[2]['url'], rows[3]['url']]
    with pytest.raises(ValueError, match='hash'):
        load_final_test(feature, manifest, 'wrong', file_sha256(manifest))
    pd.DataFrame(rows[::-1]).to_csv(feature, index=False)
    with pytest.raises(ValueError, match='align'):
        load_final_test(feature, manifest, file_sha256(feature), file_sha256(manifest))


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


def test_completed_run_does_not_load_train_or_test(tmp_path, monkeypatch):
    monkeypatch.setattr(evaluation, 'REPORT_DIR', tmp_path)
    monkeypatch.setattr(evaluation, 'MODEL_DIR', tmp_path)
    monkeypatch.setattr(evaluation, 'FIGURE_DIR', tmp_path)
    (tmp_path / 'test_metrics.json').write_text('{}')
    monkeypatch.setattr(evaluation, 'verify_cached', lambda directory: {'cached': True})
    def forbidden():
        raise AssertionError('Completed run must not load/fit/rescore')
    monkeypatch.setattr(evaluation, 'load_allowed_data', forbidden)
    monkeypatch.setattr(evaluation, 'load_final_test', forbidden)
    assert run_stage7() == {'cached': True}


def test_partial_run_blocks_automatic_repeat(tmp_path, monkeypatch):
    for name in ('REPORT_DIR', 'MODEL_DIR', 'FIGURE_DIR'):
        monkeypatch.setattr(evaluation, name, tmp_path)
    (tmp_path / 'test_predictions.csv').write_text('partial')
    with pytest.raises(RuntimeError, match='Partial'):
        run_stage7()


def test_fit_sees_train_only_before_test_unlock(tmp_path, monkeypatch):
    from dtdlink_ml.train_classifier import make_models, SELECTED_MODEL, SELECTED_THRESHOLD, FEATURE_SHA256, MANIFEST_SHA256
    for name in ('REPORT_DIR', 'MODEL_DIR', 'FIGURE_DIR'):
        monkeypatch.setattr(evaluation, name, tmp_path)
    model = make_models()[SELECTED_MODEL]
    settings = {key: model.get_params()[key] for key in ['n_estimators', 'max_depth', 'random_state']}
    selection = {'selected_model': SELECTED_MODEL, 'selected_threshold': SELECTED_THRESHOLD,
        'feature_names': list(FEATURE_NAMES), 'feature_sha256': FEATURE_SHA256,
        'manifest_sha256': MANIFEST_SHA256, 'split_counts': {'train': 2, 'validation': 1, 'test': 1},
        'model_settings': {SELECTED_MODEL: settings}, 'selected_validation_metrics': {'accuracy': 1}}
    path = tmp_path / 'selection.json'
    path.write_text(json.dumps(selection))
    monkeypatch.setattr(evaluation, 'SELECTION_FILE', path)
    train = pd.DataFrame(0., index=[0, 1], columns=FEATURE_NAMES)
    train['target'] = [0, 1]
    train['type'] = ['benign', 'phishing']
    validation = pd.DataFrame(999., index=[0], columns=FEATURE_NAMES)
    validation['target'] = [1]
    validation['type'] = ['malware']
    monkeypatch.setattr(evaluation, 'load_allowed_data', lambda: (train, validation, selection['split_counts']))
    fit_called = []
    def checked_fit(x, y):
        assert len(x) == 2 and x.to_numpy().max() == 0
        assert y.tolist() == [0, 1]
        fit_called.append(True)
    monkeypatch.setattr(model, 'fit', checked_fit)
    monkeypatch.setattr(evaluation, 'make_models', lambda: {SELECTED_MODEL: model})
    monkeypatch.setattr(evaluation.RawURLPipeline, 'probability_from_features', lambda self, x: np.ones(len(x)))
    monkeypatch.setattr(evaluation, 'score_predictions', lambda *args: {'accuracy': 1})
    def stop_after_unlock():
        assert fit_called == [True]
        raise RuntimeError('Verified fit; stop before fake test')
    monkeypatch.setattr(evaluation, 'load_final_test', stop_after_unlock)
    with pytest.raises(RuntimeError, match='Verified fit'):
        run_stage7()
