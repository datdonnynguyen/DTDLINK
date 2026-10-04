# Stage 4 ready checkpoint

- Date: 19 September 2026 (Australia/Melbourne)
- Re-verified: 20 September 2026; 98 tests passed, all schema checks matched,
  and processed/audit hashes remained unchanged after comment-only cleanup
- Previous stages: Stages 0, 1, 2, and 3 complete
- Current task: Stage 4 — feature exploration and leakage-safe split
- Stage 4 status: ready to begin; no train/validation/test split or model yet

## Evidence that closed Stage 3

- Offline parser: `src/dtdlink_ml/url_parser.py`
- Feature extractor and streaming dataset pipeline:
  `src/dtdlink_ml/feature_extraction.py`
- Parser tests: `tests/test_url_parser.py`
- Feature and integration tests: `tests/test_feature_extraction.py`
- Feature definitions: `docs/feature_dictionary.md`
- Decision record: `docs/decisions.md`, decision D-003
- Processed data: `data/processed/url_features.csv`
- Machine-readable audit: `reports/features/feature_extraction_audit.json`

## Final Stage 3 result

- Input rows: 641,113
- Output rows: 641,113
- Numeric feature count: 36
- Parse OK: 641,093 rows
- Fatal parse problems retained: 20 rows
- Robustness inputs in automated tests: 50
- Full project test result: 98 passed
- Processed CSV SHA-256:
  `fe049dd9f6b2c92570354b28b2885312f64c73b03b7053be06bc35cce5a591ff`
- Feature audit SHA-256:
  `989f65cbfb7b096fb2d933a851d6487f8420a05b3e8ff6d2d6db96d7a14d3025`

Two full extraction runs produced the same processed CSV and audit hashes. The
raw and cleaned data fingerprints remained unchanged.

## Important findings carried into Stage 4

- 463,157 rows have no explicit scheme. This is strongly represented in the
  source and must be examined for class/source association before modelling.
- 88 rows contain control characters, but this is not automatically fatal.
- Fatal issues comprise 13 invalid structures, 4 invalid ports, 2 unsupported
  FTP schemes, and 1 missing host.
- 12,215 rows have no recognised TLD; this means “not in the bundled snapshot”
  or not applicable, not automatically dangerous.
- Dataset-derived TLD frequency remains intentionally unimplemented. If used,
  it must be fitted on training rows only after splitting.
- Brand and Unicode-confusable signals use transparent bounded vocabularies;
  their coverage and class relationship require exploration.

## Stage 4 constraints

- Use `registrable_domain` to create grouped train/validation/test splits where
  practical and verify zero domain overlap.
- Do not use the held-out test set to choose features, transformations, model
  parameters, thresholds, or charts that influence modelling decisions.
- Investigate feature distributions, class/source-label associations, parse
  failures, unknown TLDs and repeated domains before locking the split.
- Fit scalers and any lookup learned from data on training rows only.
- Preserve the exact Stage 3 feature schema unless a documented decision and
  updated tests justify a change.

## Next action

Teach the Week 5 ideas of distributions, class comparison, leakage and grouped
splitting. Then propose the first small Stage 4 EDA step and its named files
before requesting approval to code.
