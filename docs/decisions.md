# DTDLINK decision log

## D-001 — Assignment 2 target strategy

- Date recorded: 15 September 2026 (Australia/Melbourne)
- Completion review: 17 September 2026; the Stage 1 audit report, recorded
  mapping, independent counts, and unchanged raw-data hash were verified.
- Status: selected for the Assignment 2 data/ML pipeline; group change-control
  acknowledgement and second-reader review remain to be recorded.
- Decision owner recorded in this workspace: student/user confirmation in the
  Stage 1 review.

### Decision

Use binary classification with the target name `target` and these mappings:

| Raw `type` value | Target value | Meaning |
|---|---:|---|
| `benign` | 0 | `benign` |
| `phishing` | 1 | `potentially_dangerous` |
| `malware` | 1 | `potentially_dangerous` |
| `defacement` | 1 | `potentially_dangerous` |

The mapping is a documented modelling definition. It does not assert that the
three source classes are equivalent, and it must not be applied to the raw CSV.
The implementation belongs in the reproducible Stage 2 pipeline.

### Rationale

- It uses all four source labels while keeping the first classifier binary.
- The raw balance is 428,103 benign rows (65.74%) and 223,088 potentially
  dangerous rows (34.26%) before cleaning.
- It supports a broad warning-oriented product while remaining simpler to
  evaluate and explain than four-class classification.

### Consequences and wording

- Assignment 2 and Assignment 3 must describe the model as detecting a
  **potentially dangerous URL**, rather than claiming it specifically detects
  phishing.
- Suitable cautious outputs include `Potentially dangerous`, `Uncertain`, and
  `No strong danger signal detected`. The last output is not a safety guarantee.
- The model will not distinguish phishing, malware, and defacement at
  prediction time. Reports may still analyse the three source labels to expose
  subgroup performance and data-quality differences.
- Evaluation must report recall and false negatives for the combined positive
  class and, where possible, break results down by original source label.
- Known source risks remain: exact duplicates are concentrated in malware and
  URL formatting is strongly associated with defacement.

### Change control

This expands the submitted Assignment 1 scope from phishing-only detection to
potentially-dangerous URL detection. Under the team rule in
`PROJECT_CONTEXT.md`, the next group meeting must record approval and name a
second reader. Until that evidence is added, this is the selected technical
target but the scope-change governance checkpoint remains open.

## D-002 — Stage 2 cleaning rules

- Date recorded: 18 September 2026 (Australia/Melbourne)
- Status: implemented and verified
- Scope: cleaning only; no feature extraction, splitting, or modelling

### Decision

Apply the rules below in this fixed order:

1. Verify the raw CSV fingerprint, schema, required values, and allowed labels.
2. Trim whitespace only from the start and end of `url` values.
3. Quarantine every row for a URL that has more than one source `type`.
4. Remove exact duplicate `url`–`type` pairs, keeping the first source record.
5. Map the retained source labels to the binary `target` from D-001.
6. Retain Unicode, control characters, extreme-length URLs, and diagnostic
   parse problems for the Stage 3 parser instead of deleting them automatically.

### Rationale

- Edge whitespace is a limited formatting repair. It changes seven values and
  creates no new duplicate group in this dataset.
- A URL with both benign and phishing labels has no defensible single answer
  when the only input is its URL text. All 12 records from the six conflicting
  URLs are therefore quarantined instead of selecting or inventing a label.
- Exact duplicates give repeated samples extra weight and can leak across later
  splits. Keeping the first occurrence is deterministic and traceable.
- Unusual characters and malformed-looking URLs can be security signals. Stage
  2 does not have enough evidence to treat them as invalid records.

### Verified consequence

- Raw rows: 651,191.
- URLs trimmed: 7; no rows removed by trimming.
- Conflicts: 6 URLs and 12 rows quarantined.
- Exact duplicate rows removed: 10,066.
- Cleaned rows and unique URLs: 641,113.
- Cleaned target balance: 428,074 benign and 213,039 potentially dangerous.
- The raw CSV SHA-256 remained unchanged, and two pipeline runs produced the
  same cleaned, conflict, and audit hashes.

## D-003 — Stage 3 parser and feature-schema rules

- Date recorded: 19 September 2026 (Australia/Melbourne)
- Status: implemented and verified
- Scope: offline parsing and feature extraction only; no splitting or modelling

### Decision

1. Parse URL text locally and never open the destination, resolve DNS, or
   refresh the Public Suffix List during extraction.
2. Preserve the original URL. Trim edge whitespace only in the parser's
   analysis copy and record the issue.
3. Treat a missing scheme as recoverable when a host can be identified; retain
   `has_scheme` and `missing_scheme` as evidence.
4. Return a stable parser structure and issue codes rather than crashing on
   malformed, Unicode, encoded, IP-host, control-character, or extreme-length
   input.
5. Lock 36 numeric Stage 3 features in the order recorded by `FEATURE_NAMES`
   and `docs/feature_dictionary.md`.
6. Copy `type` and `target` to the processed table for later analysis, but do
   not read them while calculating any feature.
7. Retain `registrable_domain` as metadata for the Stage 4 grouped split.
8. Defer dataset-derived TLD frequency/rarity until after Stage 4 splitting so
   it can be fitted on training data only.

### Rationale

- One reusable parser/extractor must serve both Assignment 2 and the later
  FastAPI application; otherwise training and live predictions can disagree.
- URL structure and unusual text can carry security information, so malformed
  samples should remain inspectable unless a later, documented rule excludes
  them.
- A TLD-frequency lookup built on all rows would leak validation/test
  distribution information into preprocessing.
- Streaming extraction keeps memory use bounded while producing a deterministic
  CSV that can be audited independently.

### Verified consequence

- 641,113 cleaned rows produced 641,113 processed rows and 36 numeric features.
- 641,093 rows parsed without a fatal issue; 20 retained rows have fatal parse
  issues for later analysis.
- 50 robustness inputs cover normal, malformed, encoded, Unicode, IP-host,
  control-character, long, and suspicious forms.
- All 98 project tests passed.
- Two complete extraction runs produced identical processed CSV and audit JSON
  hashes.

## D-004 — Stage 4 grouped split and test-lock rules

- Date recorded: 24 September 2026 (Australia/Melbourne)
- Status: implemented and verified
- Scope: data-quality audit, train/validation/test partition and training-only
  EDA; no model fitting

### Decision

1. Use `registrable_domain` as the grouping key so every URL from one
   registrable domain belongs to exactly one split.
2. For the 14 rows without a registrable domain, use a unique SHA-256 URL key.
   Do not place unrelated malformed URLs into one artificial empty-domain
   group.
3. Create ten shuffled `StratifiedGroupKFold` base folds with seed 42, then
   deterministically select two test folds, two validation folds, and six
   training folds to minimize deviation from the 60/20/20 row targets and the
   overall target rate.
4. Permit target labels only to balance the partition. Target and source labels
   never enter the group key or feature calculations.
5. Use the full feature table only for structural/data-quality and
   split-feasibility checks. Perform feature-target comparisons, distributions,
   correlations and any later preprocessing fit on training rows only.
6. Lock the test assignment using the split-manifest SHA-256. Do not use test
   rows for feature selection, scaling, lookup fitting, model selection,
   hyperparameter tuning or threshold selection. The next allowed test use is
   the one-time Stage 7 final evaluation.
7. Preserve all 36 Stage 3 features for Stage 5. Correlation and constant-value
   findings are warnings for validation, not automatic deletion rules.

### Rationale

- 40,609 groups contain multiple URLs and the largest group contains 13,422
  rows. A random row split would expose the same domain to training and test.
- Ten base folds plus deterministic allocation produces closer row and class
  balance than treating one of five uneven grouped folds as each holdout.
- URL-hash fallback keys are stable and label-independent while avoiding a
  false relationship between unrelated malformed records.
- Training-only EDA protects the held-out evaluation from exploratory feature
  decisions.

### Verified consequence

- Train: 384,832 rows (60.03%), 93,405 groups, dangerous rate 33.07%.
- Validation: 129,332 rows (20.17%), 31,050 groups, dangerous rate 33.20%.
- Test: 126,949 rows (19.80%), 31,117 groups, dangerous rate 33.75%.
- Pairwise group overlap is zero and all 641,113 rows are assigned exactly once.
- Split-manifest SHA-256:
  `fbcbcf2ff68e26acfa2bb435b53c262645688a54a195ff64e283e7ff753ffc2f`.
- Repeated executions reproduced the same manifest and audit fingerprints.
- Source-format audit confirms a major limitation: explicit schemes occur in
  8.26% of benign, 100% of defacement, 94.88% of malware and 26.40% of phishing
  rows. `has_scheme` may therefore encode source collection differences.
- Training-only EDA found two constant-zero features
  (`brand_in_userinfo`, `has_confusable_unicode`) and three feature pairs with
  absolute Pearson correlation at least 0.85. No feature was removed.
- All 105 project tests passed.

## D-005 — Stage 5 classifier and threshold selection

- Classifier selected: 1 October 2026 (Australia/Melbourne)
- Threshold selected: 2 October 2026 (Australia/Melbourne)
- Decision owner: student/user, who explicitly selected Random Forest and 0.5
- Status: selected and verified for Stage 5
- Scope: Stage 5 validation comparison only; no test-set evaluation

### Decision and evidence

Select the 100-tree Random Forest candidate with alert threshold 0.5 as
DTDLINK's classifier. The candidate was fit on the 384,832-row training partition and compared with
Logistic Regression and Decision Tree on the same 129,332-row validation
partition. At the common 0.5 comparison threshold, Random Forest achieved
precision 0.8452, recall 0.9358 and F1 0.8882, with 2,758 missed dangerous URLs
and 7,357 false alarms. Decision Tree achieved recall 0.9393 but produced
10,195 false alarms and F1 0.8630. The complete threshold trade-off and source
subgroup counts are in `reports/classification/`.

### Threshold rationale and limitations

The student chose 0.5 after reviewing the trade-off. Validation results for
Random Forest at threshold 0.4 were 1,837 missed dangerous URLs and 10,172
false alarms; at 0.5 they were 2,758 and 7,357 respectively. The chosen
threshold reduces false alarms by 2,815 while missing 921 additional dangerous
URLs relative to 0.4. Stage 5 records this choice without using the locked
test set.

Validation was used to compare models and thresholds, so it is not an unbiased
final performance estimate. URL scheme formatting may reflect source collection
differences, and raw model probabilities are not calibrated trust scores.

## D-006 — Stage 6 within-class clustering

- Date: 2 October 2026 (Australia/Melbourne).
- Authorization: student requested full Stage 6 implementation after reviewing
  the proposed files, flow and class recommendation.
- Population: 127,256 true-label potentially_dangerous training URLs; not the
  classifier's predicted positives. The mixed dangerous class follows target B.
- Input: 34 nonconstant fixed-schema numeric features; exclude type, target,
  raw URL and other metadata. Remove only two class-population constants;
  keep correlated features as a baseline with an explicit limitation.
- Scale with StandardScaler fitted on that population. Use K-means k=2–8,
  n_init=10, seed=42; same random 2,000-row silhouette sample for every k.
- Label-free selection: sampled silhouette maximum, tie prefers smaller k.
  k=7: 0.292263 (k=6: 0.283951; k=8: 0.285758). No clear strong elbow;
  interpretation and stability limit the strength of this baseline choice.
- Seven sizes: 40,662 / 26,369 / 53 / 5,730 / 4,386 / 47,106 / 2,950.
  Profiles expose missing-scheme short URLs; query-heavy URLs; anomalous
  Unicode/control text; suspicious terms/brands; IP hosts; scheme/path URLs;
  and IP hosts with nonstandard ports. These are structural descriptions,
  not confirmed attack types or risk rankings.
- Rare group has 53 rows and one silhouette-sample point. Alternate-seed ARI:
  0.97749 (43), 0.60157 (44); do not claim a unique stable grouping. Source
  formatting, correlated features, rare-boolean scaling and repeated domains
  are limitations. PCA 2D explains only 24.28% of variance.
- Source-type composition is checked AFTER selection, never used as input or
  selection criterion. DBSCAN is optional and omitted from this baseline.
- Evidence: cluster report/tables/JSON and three inspected figures; 120 tests;
  repeated CSV/JSON hashes identical; fresh fit and profile means reconciled.
- Stage 5 classifier/threshold and Stage 4 test lock remain in effect.


## D-007 — Stage 7 frozen final evaluation and export

- Date: 3 October 2026 (Australia/Melbourne).
- Authorization: student approved the complete Stage 7 file plan and implementation.
- Keep D-005 Random Forest settings and threshold 0.5. Refit on train ONLY,
  verify validation matches D-005, then evaluate test. Do not merge validation
  into training or adjust the model/threshold after seeing test.
- Final test (126,949 rows): accuracy 0.917888, precision 0.852199,
  recall 0.915521, F1 0.882726; FP 6,804 / FN 3,620.
- Phishing recall 0.833555, malware 0.898710, defacement 0.993692.
  Source-label subgroup metrics accompany the binary aggregate.
- Export raw-URL pipeline plus metadata, retaining the existing 36-feature
  implementation. Random Forest uses no scaler/calibration or clustering.
  Package source files/environment with the model; verify compatibility at load.
- Error examples: five per available source/error combination, sorted by URL ID;
  descriptive feature comparisons are associations rather than causal attribution.
- Parallel RF accumulation varies at the last binary digits. Reload acceptance
  requires absolute probability difference <= 1e-12 AND exactly equal labels;
  observed maximum 3.33e-16 and no changed labels. The original test predictions
  were preserved when the bitwise assertion failed; verification resumed from
  saved files without refitting, retuning or a new test experiment.
- Subsequent evaluation calls verify/read saved artifacts. No implicit rerun.
- Limitations remain: false negatives (especially phishing), source-format bias,
  no temporal/external holdout, unverified source labels, uncalibrated probability.
  Test is now used; additional development needs independent future evaluation.
