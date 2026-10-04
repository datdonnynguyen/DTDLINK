# Stage 7 ready checkpoint

- Date: 2 October 2026 (Australia/Melbourne).
- Stages 0–6 complete; next: final evaluation, error analysis and export.
- Stage 5 selected Random Forest (100 trees) and threshold 0.5; D-005 remains
  authoritative. Do not retune against test results.

## Stage 6 evidence

- Pipeline: `src/dtdlink_ml/cluster_urls.py`; tests: `tests/test_cluster_urls.py`.
- Notebook: `notebooks/05_clustering.ipynb`, five code cells executed
  sequentially with project Python, outputs saved (not a kernel-run claim).
- Population: 127,256 dangerous TRAIN URLs; 34 nonconstant features, no labels
  or metadata in clustering input. StandardScaler fitted on this population.
- K-means k=7, n_init=10, seed=42; fixed 2,000-row silhouette sample 0.292263.
- Sizes: 40,662; 26,369; 53; 5,730; 4,386; 47,106; 2,950.
- Five CSVs/JSON/report in `reports/clustering/`; each cluster has profiles,
  cautious domain interpretation and three real examples; three inspected
  figures in `reports/figures/`.
- 120 tests passed; repeated CSV/JSON hashes identical; independent fresh-fit
  assignments and feature means reconcile; inertia checked without BLAS.
- Limits: initialization ARI 0.97749/0.60157; rare 53-row group has only one
  silhouette sample point; PCA 2D variance 24.28%; scaling/source/domain bias.
  Clusters do not establish attack categories or risk rankings. DBSCAN omitted.

## Test lock

- Feature SHA-256: `fe049dd9f6b2c92570354b28b2885312f64c73b03b7053be06bc35cce5a591ff`.
- Manifest SHA-256: `fbcbcf2ff68e26acfa2bb435b53c262645688a54a195ff64e283e7ff753ffc2f`.
- No test distributions, model metrics or selection used. Membership/bytes
  were read only for exclusion and integrity; first final evaluation is Stage 7.

## Next action

Explain the Stage 7 file plan, final held-out evaluation, error analysis and
export/reload checks to the student before implementing that new stage.
Do not start Stage 7 merely because Stage 6 is complete.
