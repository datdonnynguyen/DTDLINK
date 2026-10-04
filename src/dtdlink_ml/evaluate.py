"""Stage 7: frozen train-only refit, one held-out evaluation, errors and export.

Existing completed runs are read back without refitting or rescoring test.
The saved predictions support report reproduction without another experiment.
"""
from __future__ import annotations

import json
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo

import joblib
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.metrics import classification_report, confusion_matrix
from threadpoolctl import threadpool_limits

from dtdlink_ml.feature_extraction import FEATURE_NAMES, file_sha256
from dtdlink_ml.predict import (RawURLPipeline, LABEL_MAPPING, implementation_hashes,
                               runtime_versions, load_pipeline)
from dtdlink_ml.train_classifier import (
    PROJECT_ROOT, FEATURE_INPUT, SPLIT_MANIFEST, FEATURE_SHA256, MANIFEST_SHA256,
    SELECTED_MODEL, SELECTED_THRESHOLD, _url_id, validate_manifest, make_models,
    load_allowed_data, score_predictions)

REPORT_DIR = PROJECT_ROOT / 'reports/evaluation'
MODEL_DIR = PROJECT_ROOT / 'models'
FIGURE_DIR = PROJECT_ROOT / 'reports/figures'
SELECTION_FILE = PROJECT_ROOT / 'reports/classification/validation_summary.json'


def load_final_test(feature_path=FEATURE_INPUT, manifest_path=SPLIT_MANIFEST,
                    feature_hash=FEATURE_SHA256, manifest_hash=MANIFEST_SHA256):
    """Load locked test only after the selected train-fit has been verified."""
    if file_sha256(feature_path) != feature_hash or file_sha256(manifest_path) != manifest_hash:
        raise ValueError('Locked data hash changed.')
    manifest = pd.read_csv(manifest_path, dtype='string', keep_default_na=False)
    counts = validate_manifest(manifest)
    rows, offset = [], 0
    for chunk in pd.read_csv(feature_path, usecols=['url', 'type', 'target', *FEATURE_NAMES],
                             keep_default_na=False, chunksize=50000):
        membership = manifest.iloc[offset:offset + len(chunk)]
        if len(chunk) != len(membership) or not np.array_equal(
                chunk.url.map(_url_id).to_numpy(), membership.url_id.to_numpy()):
            raise ValueError('Feature/manifest rows no longer align.')
        mask = membership['split'].eq('test').to_numpy()
        selected = chunk.loc[mask].copy()
        selected['url_id'] = membership.loc[mask, 'url_id'].to_numpy()
        rows.append(selected)
        offset += len(chunk)
    if offset != len(manifest):
        raise ValueError('Feature/manifest length differs.')
    test = pd.concat(rows, ignore_index=True)
    if len(test) != counts['test'] or test.url_id.duplicated().any():
        raise ValueError('Test membership/count differs.')
    if not test.type.isin(LABEL_MAPPING).all() or not test.target.eq(test.type.map(LABEL_MAPPING)).all():
        raise ValueError('Test label mapping differs.')
    return test


def build_prediction_table(test, probability, threshold=SELECTED_THRESHOLD):
    if not test.target.isin([0, 1]).all():
        raise ValueError('Invalid test labels.')
    # Reuse the independently tested metric validator before forming outcomes.
    score_predictions(test.target, probability, threshold)
    table = test[['url_id', 'url', 'type', 'target']].copy()
    table['probability'] = probability
    table['prediction'] = (table.probability >= threshold).astype(int)
    table['outcome'] = np.select([
        table.target.eq(1) & table.prediction.eq(1),
        table.target.eq(0) & table.prediction.eq(0),
        table.target.eq(0) & table.prediction.eq(1)], ['TP', 'TN', 'FP'], default='FN')
    return table


def subgroup_table(predictions):
    rows = []
    for source in LABEL_MAPPING:
        group = predictions.loc[predictions.type.eq(source)]
        if group.empty:
            continue
        errors = int(group.outcome.isin(['FP', 'FN']).sum())
        rows.append({'source_type': source, 'rows': len(group), 'correct': len(group) - errors,
            'correct_rate': 1 - errors / len(group),
            'missed_dangerous': int(group.outcome.eq('FN').sum()),
            'false_alarms': int(group.outcome.eq('FP').sum()),
            'dangerous_recall': (1 - errors / len(group)) if source != 'benign' else None,
            'benign_false_alarm_rate': errors / len(group) if source == 'benign' else None})
    return pd.DataFrame(rows)


def select_error_examples(test, predictions, per_group=5):
    """Deterministic coverage of error types/source labels, not cherry-picked extremes."""
    indices = []
    for outcome in ('FP', 'FN'):
        for source in LABEL_MAPPING:
            group = predictions.loc[predictions.outcome.eq(outcome) & predictions.type.eq(source)]
            indices.extend(group.sort_values('url_id').head(per_group).index.tolist())
    examples = predictions.loc[indices].copy()
    for name in ('url_length', 'has_scheme', 'uses_https', 'has_ip_host',
                 'has_suspicious_term', 'query_parameter_count', 'parse_ok'):
        examples[name] = test.loc[indices, name].to_numpy()
    return examples


def write_report(metrics, subgroups, test, predictions, examples, destination):
    lines = ['# Stage 7 — Đánh giá cuối và phân tích lỗi', '',
        'Random Forest 100 cây, threshold 0.5; fit chỉ trên train. Không điều chỉnh theo test.',
        'Positive = phishing/malware/defacement; negative = benign theo nhãn dataset.', '',
        '## Kết quả held-out test', '', f'Số URL test: {len(test):,}.', '',
        '| Metric | Giá trị |', '|---|---:|']
    for name in ('accuracy', 'precision', 'recall', 'f1'):
        lines.append(f'| {name} | {metrics[name]:.6f} |')
    for name in ('true_negative', 'false_positive', 'false_negative', 'true_positive'):
        lines.append(f'| {name} | {metrics[name]:,} |')
    lines += ['', '## Theo nhãn gốc', '', '| Loại | Số URL | Đúng | FN | FP | Tỷ lệ đúng |',
              '|---|---:|---:|---:|---:|---:|']
    for row in subgroups.to_dict('records'):
        lines.append(f"| {row['source_type']} | {row['rows']} | {row['correct']} | {row['missed_dangerous']} | {row['false_alarms']} | {row['correct_rate']:.4f} |")
    lines += ['', '## Mẫu lỗi quan sát được', '',
        'So sánh trong cùng nhãn thật: FP với TN; FN với TP. Các tỷ lệ sau chỉ là liên hệ mô tả, không chứng minh nguyên nhân hoặc đóng góp của từng feature.', '',
        '| Nhóm | n | Median URL length | Có scheme | HTTPS | Host IP | Từ nghi vấn |',
        '|---|---:|---:|---:|---:|---:|---:|']
    for outcome in ('TN', 'FP', 'TP', 'FN'):
        group = test.loc[predictions.outcome.eq(outcome)]
        if len(group):
            lines.append(f'| {outcome} | {len(group)} | {group.url_length.median():.1f} | {group.has_scheme.mean():.4f} | {group.uses_https.mean():.4f} | {group.has_ip_host.mean():.4f} | {group.has_suspicious_term.mean():.4f} |')
    fp = test.loc[predictions.outcome.eq('FP')]
    tn = test.loc[predictions.outcome.eq('TN')]
    fn = test.loc[predictions.outcome.eq('FN')]
    tp = test.loc[predictions.outcome.eq('TP')]
    for error_name, errors, correct_name, correct in [('FP', fp, 'TN', tn), ('FN', fn, 'TP', tp)]:
        if len(errors) and len(correct):
            lines += ['', f'{error_name}: median độ dài URL {errors.url_length.median():.1f} so với {correct_name} {correct.url_length.median():.1f}; tỷ lệ có scheme {errors.has_scheme.mean():.2%} so với {correct.has_scheme.mean():.2%}; tỷ lệ từ nghi vấn {errors.has_suspicious_term.mean():.2%} so với {correct.has_suspicious_term.mean():.2%}. Đây là dấu hiệu cần thảo luận về cấu trúc URL/định dạng nguồn, không đủ để quy kết lỗi cho một feature.']
    lines += ['', 'Ví dụ chọn theo URL ID tăng dần, tối đa 5 ví dụ cho mỗi cặp loại lỗi/nhãn gốc; không chọn chỉ các ví dụ gây ấn tượng. URL được escape trong khối văn bản và không truy cập.', '']
    for row in examples.to_dict('records'):
        lines += [f"- {row['outcome']}, type={row['type']}, p={row['probability']:.4f}, length={row['url_length']}, scheme={row['has_scheme']}, suspicious_term={row['has_suspicious_term']}",
                  '', '```text', json.dumps(row['url'], ensure_ascii=True), '```', '']
    lines += ['## Hạn chế và sử dụng', '',
        '- FN bỏ sót URL mang nhãn nguy hiểm; FP cảnh báo nhầm URL mang nhãn benign.',
        '- Nhãn gốc và thời điểm thu thập không được xác minh độc lập. Không mở URL để kiểm tra nhãn.',
        '- Domain-aware split giảm trùng miền; không phải temporal holdout hoặc bằng chứng hiệu quả trên mọi URL ngoài thực tế.',
        '- Định dạng scheme, nguồn dữ liệu, class imbalance và lexical-only features có thể ảnh hưởng kết quả.',
        '- Xác suất Random Forest chưa calibrated; không gọi là trust score hoặc bảo đảm an toàn.',
        '- Test đã được sử dụng cho đánh giá cuối. Mọi cải tiến sau đây cần validation và một holdout mới để đánh giá độc lập.',
        '- final_pipeline.joblib cần đi cùng source parser/features/predict.py và đúng environment. Không có scaler trong classifier này.',
        '- reload kiểm tra toàn bộ test probabilities khớp trong sai số tuyệt đối 1e-12 và nhãn giống hệt trước export và kiểm tra URL thô so với bảng features; không refit.',
        '- test_predictions.csv chứa URL dataset phục vụ kiểm toán; predict.py không lưu URL người dùng.', '']
    destination.write_text('\n'.join(lines), encoding='utf-8')


def verify_cached(report_dir):
    summary = json.loads((report_dir / 'test_metrics.json').read_text())
    if file_sha256(FEATURE_INPUT) != summary['feature_sha256'] or file_sha256(SPLIT_MANIFEST) != summary['manifest_sha256']:
        raise ValueError('Locked data changed since evaluation.')
    for relative, expected in summary['artifact_sha256'].items():
        if file_sha256(PROJECT_ROOT / relative) != expected:
            raise ValueError(f'Completed artifact changed: {relative}')
    load_pipeline()
    return summary


def finalize_export_checks(test, predictions, counts):
    """Verify exported inference against saved predictions without refitting.

    Parallel tree reduction can differ in the last binary digits. Require
    absolute probability error <= 1e-12 AND exactly equal class predictions.
    """
    probability = predictions.probability.to_numpy()
    metrics = score_predictions(test.target, probability, SELECTED_THRESHOLD)
    model_path = MODEL_DIR / 'final_pipeline.joblib'
    completed = REPORT_DIR / 'test_metrics.json'
    restored = load_pipeline()
    restored_probability = restored.probability_from_features(test.loc[:, FEATURE_NAMES])
    max_difference = float(np.max(np.abs(probability - restored_probability)))
    if (not np.allclose(probability, restored_probability, rtol=0, atol=1e-12)
            or not np.array_equal(restored_probability >= SELECTED_THRESHOLD, predictions.prediction.to_numpy())):
        raise ValueError('Reload changed probabilities beyond tolerance or changed labels.')
    # Coverage across source error groups and a deterministic spread of test rows.
    examples = select_error_examples(test, predictions)
    indices = sorted(set(examples.index.tolist() + np.linspace(0, len(test) - 1, 100, dtype=int).tolist()))
    raw_features = restored.features_from_urls(test.loc[indices, 'url'].tolist())
    if not np.array_equal(raw_features.to_numpy(), test.loc[indices, FEATURE_NAMES].to_numpy()):
        raise ValueError('Raw URL features differ from saved dataset.')
    if not np.allclose(restored.predict_proba(test.loc[indices, 'url'].tolist())[:, 1], probability[indices], rtol=0, atol=1e-12):
        raise ValueError('Raw URL predictions differ from table predictions.')
    new_urls = ['https://example.com/', 'http://192.0.2.1:8080/login?verify=1',
                'example.com/no-scheme', 'https://[broken', 'https://exаmple.com/%2Flogin']
    # Explicitly fail any attempted network operation during inference.
    import socket
    from unittest.mock import patch
    with patch.object(socket.socket, 'connect', side_effect=AssertionError('Network forbidden')), \
         patch.object(socket, 'getaddrinfo', side_effect=AssertionError('DNS forbidden')):
        offline_results = restored.predict_urls(new_urls)
    if len(offline_results) != len(new_urls):
        raise ValueError('Offline inference incomplete.')
    artifacts = [REPORT_DIR / name for name in ('test_predictions.csv', 'test_subgroups.csv',
        'classification_report.csv', 'error_examples.csv', 'stage-7-evaluation-report.md')]
    artifacts += [model_path, MODEL_DIR / 'model_metadata.json', FIGURE_DIR / 'test_confusion_matrix.png']
    summary = {**metrics, 'evaluated_at': datetime.now(ZoneInfo('Australia/Melbourne')).isoformat(),
        'model': SELECTED_MODEL, 'fit_split': 'train', 'evaluation_split': 'test',
        'split_counts': counts, 'feature_sha256': FEATURE_SHA256, 'manifest_sha256': MANIFEST_SHA256,
        'validation_refit_matches_selection': True, 'test_used_for_tuning': False,
        'reload_all_test_probabilities_match_tolerance': True, 'reload_all_test_labels_equal': True,
        'reload_probability_atol': 1e-12, 'reload_max_probability_difference': max_difference, 'raw_url_equivalence_checked': len(indices),
        'offline_new_urls_checked': len(new_urls), 'probability_calibrated': False,
        'artifact_sha256': {str(path.relative_to(PROJECT_ROOT)): file_sha256(path) for path in artifacts}}
    completed.write_text(json.dumps(summary, indent=2) + '\n')
    return summary

def run_stage7():
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    FIGURE_DIR.mkdir(parents=True, exist_ok=True)
    completed = REPORT_DIR / 'test_metrics.json'
    if completed.exists():
        print('Reading verified completed evaluation; no fit/test rescore.', flush=True)
        return verify_cached(REPORT_DIR)
    # A partial final run requires investigation instead of silently repeating test.
    if (REPORT_DIR / 'test_predictions.csv').exists():
        required = [MODEL_DIR / 'model_metadata.json', MODEL_DIR / 'final_pipeline.joblib',
                    REPORT_DIR / 'stage-7-evaluation-report.md', REPORT_DIR / 'test_subgroups.csv',
                    REPORT_DIR / 'classification_report.csv', REPORT_DIR / 'error_examples.csv',
                    FIGURE_DIR / 'test_confusion_matrix.png']
        if not all(path.exists() for path in required):
            raise RuntimeError('Partial test output exists; inspect/recover before another evaluation.')
        print('Recovering export checks from saved predictions; no refit or new test experiment.', flush=True)
        predictions = pd.read_csv(REPORT_DIR / 'test_predictions.csv', keep_default_na=False, float_precision='round_trip')
        test = load_final_test()
        if (not np.array_equal(predictions.url_id.to_numpy(), test.url_id.to_numpy())
                or not np.array_equal(predictions.target.to_numpy(), test.target.to_numpy())
                or not np.array_equal(predictions.prediction.to_numpy(), (predictions.probability >= SELECTED_THRESHOLD).astype(int).to_numpy())):
            raise ValueError('Saved predictions do not match locked test/threshold.')
        metadata = json.loads((MODEL_DIR / 'model_metadata.json').read_text())
        return finalize_export_checks(test, predictions, metadata['split_counts'])
    selection = json.loads(SELECTION_FILE.read_text())
    if (selection['selected_model'] != SELECTED_MODEL or selection['selected_threshold'] != SELECTED_THRESHOLD
            or selection['feature_names'] != list(FEATURE_NAMES)
            or selection['feature_sha256'] != FEATURE_SHA256 or selection['manifest_sha256'] != MANIFEST_SHA256):
        raise ValueError('Stage 5 selection contract differs.')
    print('Loading train/validation and refitting frozen Random Forest.', flush=True)
    train, validation, counts = load_allowed_data()
    for frame in (train, validation):
        if not frame.type.isin(LABEL_MAPPING).all() or not frame.target.eq(frame.type.map(LABEL_MAPPING)).all():
            raise ValueError('Train/validation label mapping differs.')
    if counts != selection['split_counts']:
        raise ValueError('Split counts differ from selection.')
    model = make_models()[SELECTED_MODEL]
    expected_settings = selection['model_settings'][SELECTED_MODEL]
    if any(model.get_params()[key] != value for key, value in expected_settings.items()):
        raise ValueError('Random Forest settings differ from recorded selection.')
    pipeline = RawURLPipeline(model, threshold=SELECTED_THRESHOLD)
    with threadpool_limits(limits=2):
        model.fit(train.loc[:, FEATURE_NAMES], train.target)
        validation_metrics = score_predictions(validation.target,
            pipeline.probability_from_features(validation.loc[:, FEATURE_NAMES]), SELECTED_THRESHOLD)
        for key, value in validation_metrics.items():
            if not np.isclose(value, selection['selected_validation_metrics'][key], atol=1e-12, rtol=0):
                raise ValueError(f'Refit validation result differs: {key}')
        print('Validation matches Stage 5. Evaluating locked test once.', flush=True)
        test = load_final_test()
        probability = pipeline.probability_from_features(test.loc[:, FEATURE_NAMES])
        predictions = build_prediction_table(test, probability)
        predictions.to_csv(REPORT_DIR / 'test_predictions.csv', index=False)
        metrics = score_predictions(test.target, probability, SELECTED_THRESHOLD)
        subgroups = subgroup_table(predictions)
        subgroups.to_csv(REPORT_DIR / 'test_subgroups.csv', index=False)
        class_report = classification_report(test.target, predictions.prediction,
            labels=[0, 1], target_names=['benign', 'potentially_dangerous'], output_dict=True, zero_division=0)
        pd.DataFrame(class_report).transpose().to_csv(REPORT_DIR / 'classification_report.csv', index_label='class_or_average')
        examples = select_error_examples(test, predictions)
        examples.to_csv(REPORT_DIR / 'error_examples.csv', index=False)
        write_report(metrics, subgroups, test, predictions, examples,
                     REPORT_DIR / 'stage-7-evaluation-report.md')
        matrix = confusion_matrix(test.target, predictions.prediction, labels=[0, 1])
        fig, ax = plt.subplots(figsize=(7, 5))
        ax.imshow(matrix, cmap='Blues')
        for (i, j), count in np.ndenumerate(matrix):
            ax.text(j, i, f'{count:,}', ha='center', va='center', fontsize=15,
                    color='white' if count > matrix.max() / 2 else 'black')
        ax.set(xticks=[0, 1], yticks=[0, 1], xticklabels=['Benign', 'Dangerous'],
               yticklabels=['Benign', 'Dangerous'], xlabel='Predicted label', ylabel='Actual label',
               title='Held-out test: Random Forest, threshold 0.5')
        fig.tight_layout()
        fig.savefig(FIGURE_DIR / 'test_confusion_matrix.png', dpi=160)
        plt.close(fig)
        model_path = MODEL_DIR / 'final_pipeline.joblib'
        joblib.dump(pipeline, model_path, compress=3)
        metadata = {'model': SELECTED_MODEL, 'model_settings': model.get_params(),
            'threshold': SELECTED_THRESHOLD, 'feature_names': list(FEATURE_NAMES),
            'label_mapping': LABEL_MAPPING, 'fit_split': 'train', 'split_counts': counts,
            'preprocessing': 'Existing offline parser/extractor; no fitted scaler or lookup',
            'probability_calibrated': False, 'feature_sha256': FEATURE_SHA256,
            'manifest_sha256': MANIFEST_SHA256, 'implementation_sha256': implementation_hashes(),
            'runtime_versions': runtime_versions(), 'model_sha256': file_sha256(model_path)}
        (MODEL_DIR / 'model_metadata.json').write_text(json.dumps(metadata, indent=2) + '\n')
    return finalize_export_checks(test, predictions, counts)


if __name__ == '__main__':
    print(json.dumps(run_stage7(), indent=2))
