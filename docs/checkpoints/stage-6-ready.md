# Stage 6 ready checkpoint

- Date: 2 October 2026 (Australia/Melbourne)
- Previous stages: Stages 0–5 complete
- Current task: Stage 6 — within-class clustering
- Stage 6 status: ready to begin; no clustering model has been fitted

## Stage 5 decision

The student selected the 100-tree Random Forest classifier on 1 October 2026
and alert threshold **0.5** on 2 October 2026. Decision D-005 in
`docs/decisions.md` records the rationale and the 0.4-versus-0.5 trade-off.
The selected settings are constants in `src/dtdlink_ml/train_classifier.py`
and appear in `reports/classification/validation_summary.json`.

## Stage 5 evidence

- Input: the fixed Stage 3 table of 641,113 URLs and 36 numeric features.
- Stage 4 split: 384,832 train; 129,332 validation; 126,949 locked test.
- All three candidates trained on train and compared on the same validation
  partition: Logistic Regression, Decision Tree and Random Forest.
- Selected Random Forest at threshold 0.5 on validation: accuracy 0.9218,
  precision 0.8452, recall 0.9358, F1 0.8882, 2,758 false negatives and
  7,357 false positives.
- The alternate Random Forest threshold 0.4 would have yielded 1,837 false
  negatives and 10,172 false positives on validation. The student selected
  0.5 after reviewing this trade-off.
- Reusable pipeline: `src/dtdlink_ml/train_classifier.py`.
- Automated checks: `tests/test_train_classifier.py`; full suite 112 passed.
- Reviewable notebook: `notebooks/04_classification.ipynb`; all four code
  cells executed sequentially, outputs saved and chart inspected. A normal
  Jupyter kernel could not bind local sockets in the sandbox.
- Tables and metadata: `reports/classification/`.
- README documents the Stage 5 reproduction command.

## Test lock and limits

- Feature-table SHA-256:
  `fe049dd9f6b2c92570354b28b2885312f64c73b03b7053be06bc35cce5a591ff`.
- Split-manifest SHA-256:
  `fbcbcf2ff68e26acfa2bb435b53c262645688a54a195ff64e283e7ff753ffc2f`.
- Test membership was read to exclude test rows. Test features were not profiled
  and no test model metrics or threshold decisions were calculated. The first
  final test evaluation remains Stage 7.
- Validation was used for model and threshold selection, so its metrics may
  be optimistic. URL scheme formatting may partly reveal source collection
  practices. Model probabilities are not calibrated trust scores.
- The selected classifier has not yet been exported; saving the final pipeline
  is part of Stage 7 after final evaluation.

## Next action

Teach the Week 6/7 clustering concepts, select one class using training data,
and perform within-class clustering without using the class label as a feature.
Describe clusters through feature differences and representative URLs.
