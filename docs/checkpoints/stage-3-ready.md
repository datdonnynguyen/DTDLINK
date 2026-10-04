# Stage 3 ready checkpoint

- Date: 18 September 2026 (Australia/Melbourne)
- Previous stages: Stages 0, 1, and 2 complete
- Current task: Stage 3 — URL parser and feature extractor
- Stage 3 status: ready to begin; no parser or model features implemented yet

## Evidence that closed Stage 2

- Pipeline: `src/dtdlink_ml/data_cleaning.py`
- Tests: `tests/test_data_cleaning.py`; all 16 project tests passed
- Executed notebook: `notebooks/02_cleaning.ipynb`; 5/5 code cells ran without
  error and the notebook rendered successfully to HTML for inspection
- Learning notes: `docs/stage-2-cleaning-notes.md`
- Cleaning decision: `docs/decisions.md`, decision D-002
- Machine-readable audit: `reports/cleaning/cleaning_audit.json`
- Cleaned data: `data/interim/malicious_phish_cleaned.csv`
- Quarantined conflicts: `reports/cleaning/conflicting_records.csv`

## Final Stage 2 rules and results

1. The raw SHA-256 and input contract are checked before any transformation.
2. Edge whitespace was trimmed from 7 URLs; no row was removed by this repair.
3. All 12 rows from 6 conflicting benign/phishing URLs were quarantined.
4. 10,066 exact duplicate URL-label rows were removed, keeping the first.
5. The original `type` was retained and target B was created reproducibly.
6. Unicode, control characters, extreme length, and parse issues were retained.

The cleaned output has 641,113 rows and 641,113 unique URLs. Its SHA-256 is
`b717c3c8f3c802bbf975973cecabe82a703aeca7069389aacac579ff2aebe464`.
Two complete runs produced the same cleaned, conflict, and audit hashes. The
raw hash remained unchanged.

## Stage 3 constraints inherited from the project

- Parse URL text locally without opening the destination or making lookups.
- Handle missing schemes, malformed inputs, Unicode, encoding, control
  characters, IP hosts, and extreme lengths without crashing.
- Begin with the seven signals committed in Assignment 1 and document every
  feature in `docs/feature_dictionary.md`.
- Keep data-learned feature state, such as TLD frequency, out of the full-data
  parser; it must later be fitted on training data only.
- Add at least 30 unusual and negative input cases.
- Do not split data, train models, or use a final test set during Stage 3.

## Next action

Teach the Week 4–5 distinction between parsing and feature extraction, then
propose the first small Stage 3 implementation step with all files and tests
named before requesting approval to code.
