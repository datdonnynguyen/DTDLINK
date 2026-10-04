# Stage 5 ready checkpoint

- Date: 24 September 2026 (Australia/Melbourne)
- Acceptance review: re-verified independently on 24 September 2026; all
  641,113 URL hashes and assignments reconciled, pairwise group overlap remained
  zero, the locked manifest hash matched, and all 105 tests passed
- Previous stages: Stages 0, 1, 2, 3, and 4 complete
- Current task: Stage 5 — train and select classification models
- Stage 5 status: ready to begin; no classifier has been trained yet

## Evidence that closed Stage 4

- Reusable audit/split/EDA pipeline: `src/dtdlink_ml/data_splitting.py`
- Automated tests: `tests/test_data_splitting.py`
- Reviewable notebook: `notebooks/03_eda_and_splitting.ipynb`
- Split manifest: `data/processed/split_manifest.csv`
- Pre-split audit: `reports/eda/pre_split_profile.json`
- Leakage and split audit: `reports/splitting/split_audit.json`
- Preprocessing plan: `reports/eda/preprocessing_plan.json`
- Tables: `reports/tables/`
- Training-only figures: `reports/figures/`
- Decision record: `docs/decisions.md`, decision D-004

## Final Stage 4 result

- Input: 641,113 unique URLs with the fixed 36-feature Stage 3 schema.
- Grouping: 155,558 registrable domains plus 14 unique URL-hash fallback
  groups; 155,572 groups in total.
- Repeated groups: 40,609; largest group: 13,422 rows.
- Train: 384,832 rows (60.03%), 93,405 groups, dangerous rate 33.07%.
- Validation: 129,332 rows (20.17%), 31,050 groups, dangerous rate 33.20%.
- Test: 126,949 rows (19.80%), 31,117 groups, dangerous rate 33.75%.
- Train/validation/test group overlap: zero for every pair.
- Split-manifest SHA-256:
  `fbcbcf2ff68e26acfa2bb435b53c262645688a54a195ff64e283e7ff753ffc2f`.
- Two pipeline reruns and a sequential execution of all nine notebook code
  cells reproduced the same split-manifest hash.
- Full automated suite: 105 tests passed.

## EDA findings carried into Stage 5

1. The training set remains moderately imbalanced: 257,576 benign (66.93%) and
   127,256 potentially dangerous (33.07%). Accuracy alone is not sufficient.
2. `has_scheme` and `parse_issue_count` have correlation -0.9994 because a
   missing scheme is a recoverable parser issue in this dataset.
3. `has_explicit_port` and `has_nonstandard_port` have correlation 0.9972;
   almost every explicit port in training is non-standard.
4. `suspicious_term_count` and `has_suspicious_term` have correlation 0.9187.
5. `brand_in_userinfo` and `has_confusable_unicode` are constant zero in
   training. They remain in the schema until validation evidence justifies a
   documented change.
6. Explicit scheme formatting is strongly associated with source label:
   benign 8.26%, defacement 100%, malware 94.88%, phishing 26.40%. Model results
   must be interpreted as partly exposed to source-format association.
7. Large repeated domain groups make domain-aware validation essential; random
   row splitting is not acceptable for reported results.

## Test-set lock

- The test assignment is identified by the manifest hash above.
- Stage 5 may use training data for fitting and validation data for comparing
  models, hyperparameters and thresholds.
- Stage 5 must not inspect test feature distributions or test model metrics.
- Scaling and any optional TLD-frequency lookup must be fit on training rows
  only and then applied unchanged to validation/test/new URLs.
- The next permitted test-set evaluation is Stage 7 after the final classifier
  and threshold have been selected.

## Notebook validation limitation

The sandbox blocked a normal Jupyter kernel because it could not bind local
sockets. All nine code cells were therefore executed sequentially with the
project Python environment, the notebook structure was validated with
`nbformat`, and its HTML shell plus all six saved PNG figures were inspected.
The pipeline itself was executed repeatedly outside the notebook and produced
stable hashes. A normal local Jupyter session can rerun the notebook without
this sandbox limitation.

## Next action

Teach the Week 6/7 concepts needed for classification: training versus
prediction, baselines, overfitting, validation, Logistic Regression, Decision
Tree, class weights, probabilities and thresholds. Then implement Stage 5
using train for fitting and validation for comparison while leaving test locked.
