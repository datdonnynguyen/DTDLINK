# COS30049 Project Context and Progress

> Persistent context for future chats. Read this file before advising on Assignments 2 or 3. Update the progress section whenever work is completed or the scope changes.

## Current snapshot

- Last updated: 3 October 2026 (Australia/Melbourne)
- Team: Session 7 - Group 5
- Project: **DTDLINK (Detect The Deception Links)**
- Selected course topic in submitted Assignment 1: **Phishing URL Detection**
- Assignment 2 selected target: **benign vs potentially dangerous** (phishing,
  malware, and defacement map to the positive class)
- Assignment 1: **completed and submitted on 2 September 2026**
- Current learning position: **Stage 7 complete using Week 7 evaluation concepts; Stage 8 report/package is next**
- Assignment 2: Stages 0-7 complete. The student selected Random Forest on
  1 October 2026 and threshold 0.5 on 2 October 2026 after comparing three
  classifiers on validation; frozen final test evaluation/export completed on 3 October 2026.
- Master execution plan: `ASSIGNMENT2_MASTER_PLAN.md` created; future work should follow its learning -> practice -> build -> review stages
- Prompt playbook: `DTDLINK_PROMPT_PLAYBOOK.md` contains concise copy-ready A (theory), B (guided learning/build), C (understand results), and D (completion/checkpoint) prompts for Stages 0-9, plus interrupted-session and context-recovery prompts. Technical detail stays in the master plan instead of being repeated in every prompt.
- Student working preference: the student owns the project, decisions, and
  understanding; Codex acts as the implementation assistant who writes code on
  the student's behalf. The student needs enough concepts and code structure to
  understand the method, read the implementation, explain results, and adjust
  important settings without doing coding exercises or memorising syntax.
  Codex handles authorized environment setup, installation, implementation,
  execution, testing, and debugging only after the approval gate below. Each
  Stage must be divided into small guided steps: explain before the step, obtain
  acceptance, perform the technical work, review the real result and code with
  the student, check conceptual understanding, then wait for `tiếp tục` before
  the next substantial step.
- Current Assignment 2 deadline recorded in the course materials: **4 October 2026 at 23:59 AEST**
- Important date note: the Assignment 1 schedule says 27 September, but the newer Assignment 2 specification says 4 October. Use 4 October unless a newer live Canvas notice supersedes it.

## Authoritative Assignment 1 source

- Original PDF: `/Users/okok/Downloads/session-07-group-5-Assignment1.pdf`
- Document title: *Phishing URL Detection - Project Management Plan and Front-End Prototype*
- Length: 21 pages
- Tutor: Dr Ricky Dong

## Team and agreed roles

| Member | Student ID | Role | Main responsibility |
|---|---:|---|---|
| SOKNA DAVID HEANG | 105962079 | Project Manager | Schedule, meetings/minutes, risks, change control, report |
| DUONG DANH DAT NGUYEN | 105928000 | Data and ML Lead | Data cleaning, feature code, model training and testing |
| SOTHEARITH KUY | 105069886 | Developer and UI/UX | Figma prototype, React frontend, FastAPI backend, charts |

Team rules:

1. Update tasks before the weekly meeting.
2. Report blockers immediately.
3. Push all work to the repository; work left on one laptop is not considered complete.
4. Scope/design changes require a group decision and a second reader before completion.

## Product vision

DTDLINK is planned as a learning-focused web application that assesses a URL using only the URL text. It must not open the destination and must not send the URL to an external service. The intended output is:

- a 0-100 trust/risk-style score;
- a cautious label such as `Potentially dangerous` or `Uncertain`;
- a list of human-readable URL signals contributing to the result;
- highlighting of suspicious URL parts;
- guidance telling the user what to do next.

The application must never claim that a URL is definitively safe.

## Project objectives selected in Assignment 1

1. Parse a URL into scheme, host, path, and query without visiting it.
2. Write reusable code that converts a raw URL into measurable features.
3. Train and compare at least two classification models.
4. Show an understandable score and explanation.
5. Provide a simple interface suitable for laptops and phones.
6. Maintain documentation, meeting minutes, and test evidence.

## Scope decisions

### In scope

- Course phishing URL dataset plus justified extra datasets.
- Cleaning, deduplication, and leakage-safe splitting.
- Custom feature extraction from raw URL text.
- At least two classification models and comparison.
- Accuracy, precision, recall, F1, confusion matrix, and missed-dangerous-URL
  analysis, with original-label subgroup checks where practical.
- Required Assignment 2 clustering within one class, even though this was not detailed in the Assignment 1 scope table.
- React interface, FastAPI model service, and charts in Assignment 3.
- Functional, offline, usability, accessibility, and reproducibility testing.
- Documentation, minutes, change tracking, and version control.

### Out of scope

- Opening or downloading a submitted website.
- Network lookups during prediction.
- Browser extension or production security product.
- Guaranteeing that a URL is safe.
- Saving submitted URLs or creating user accounts.
- Analysing email bodies, attachments, or QR codes.
- A database; FastAPI is intended only to serve the model.

## Planned raw input, target, and output

- Raw input: a URL string.
- Course base dataset: `malicious_phish.csv` from `Week-08/Assessment/Basic_Datasets.zip`.
- Dataset fields documented by the course: `url` and `type`.
- ML task: binary classification of `benign` versus `potentially_dangerous`.
- Target mapping: benign -> 0; phishing, malware, and defacement -> 1. This is
  applied reproducibly after the raw-data boundary, never by editing the raw CSV.
- Application output: prediction/probability transformed into cautious
  potentially-dangerous/uncertain wording and supporting signal explanations.
- Privacy constraint: URLs must not be stored or transmitted during analysis.

## URL features already committed to in Assignment 1

| Signal | Planned calculation | Rationale |
|---|---|---|
| URL/address length | Character count | Long URLs can obscure the real domain |
| Host is an IP address | Parse/test the host as an IP | Numeric hosts provide no familiar domain identity |
| Subdomain count | Count labels before the registrable domain | Excess labels can place trusted words before the real domain |
| Brand name in subdomain | Compare subdomain tokens with a documented brand list | A brand outside the registrable domain is suspicious |
| Look-alike/confusable characters | Unicode UTS #39-style confusable check | Different characters can look visually identical |
| Unusual top-level domain | Derive frequency from training data or a justified external source | Some TLDs may be disproportionately represented in phishing data |
| `@` in the URL | Detect `@` in the authority/address | Text before `@` can mislead users about the true host |

Assignment 2 must turn these ideas into a documented feature dictionary and reusable feature extraction code. Any feature learned from data, such as TLD frequency, must be fitted using training data only to prevent leakage.

## Data and modelling decisions already planned

- Inspect dataset size, labels, class balance, and duplicates.
- Normalise URL text only where the transformation does not destroy security-relevant information.
- Deduplicate before splitting.
- Split data by registrable domain where practical to prevent near-identical domains appearing in both training and test sets.
- Build a safe URL parser that handles malformed, encoded, and unusual URLs.
- Create unit tests for at least 30 unusual/negative URL cases.
- Assignment 1 proposed Logistic Regression and Decision Tree as baseline models.
- Tune and select a final model using validation data.
- Evaluate the selected model once on a held-out test set.
- Prioritise missed potentially dangerous links and recall rather than
  optimising accuracy alone; inspect performance by original dangerous subtype
  where practical.
- Assignment 2 additionally requires unsupervised clustering without labels within a single class, followed by feature-based cluster interpretation.

## Main functional requirements

The agreed Must requirements are:

1. Enter/paste one URL.
2. Validate empty, malformed, or excessively long input and explain errors.
3. Split the URL into scheme, host, path, and query.
4. Calculate features locally from URL text.
5. Return a potentially-dangerous-URL prediction/probability.
6. Present a 0-100 score with a cautious label.
7. Explain strong, medium, and weak signals.
8. Highlight the suspicious parts of the URL.
9. Label middle scores as uncertain.
10. Render the URL as non-clickable text.

The Insights page, interactive charts, and How It Works page were prioritised as Should requirements.

## Main non-functional requirements

- Offline: zero analysis-related network requests during ten checks.
- Speed: 95% of checks should finish in under two seconds.
- Usability: at least four of five first-time testers complete the task unaided.
- Accessibility: target WCAG 2.2 AA, keyboard operation, visible focus, and at least 4.5:1 contrast.
- Safe wording: never state that a link is safe.
- Privacy: do not save submitted URLs.
- Robustness: pass 30 negative/strange-input cases without crashing.
- Reproducibility: documented commands reproduce reported results within +/-0.01.
- Responsive design: main flow works at 375 px width.

## Acceptance criteria that affect Assignment 2

- A valid URL produces a score, label, and detected signals.
- Analysis works without opening the URL or sending it online.
- The result includes an explanation and highlights relevant URL portions.
- Scores between 40 and 60 are presented as uncertain, subject to later evidence-based calibration.
- Invalid input produces an explanation and does not crash.
- Submitted URLs are never clickable.
- Final held-out evaluation reports precision, recall, F1, confusion matrix, and missed-phishing count.
- A documented clean run reproduces metrics within +/-0.01.

## Identified high-priority risks

1. Similar URLs/domains in training and test data inflate performance.
2. Incorrect labels or severe class imbalance distort training/evaluation.
3. Accuracy-focused tuning causes the model to miss phishing URLs.
4. Malformed or encoded URLs crash feature extraction.
5. Online enrichment breaks the offline/privacy product promise.
6. React/FastAPI delays reduce testing time.
7. Uneven contribution or work remaining on individual laptops reduces team visibility.

## Prototype and UI decisions

- Product name: DTDLINK.
- Figma prototype: `https://www.figma.com/design/LJTZcDytGPsvlYEVvlmW5K/DTDLINK-%E2%80%93-Phishing-Link-Detector-Prototype?node-id=0-1&t=RLYJJYybsddFHu59-1`
- Planned pages: Check URL, Insights, and How It Works.
- Five main prototype frames: initial check screen, result, insights, bad-input/uncertain states, and How It Works.
- Core UX principle: communicate uncertainty and evidence without encouraging over-trust.
- Colours: navy `#0F2743`, action blue `#2563C9`, background `#F4F6FA`, high-risk red `#B3261E`, and medium-risk amber `#B26B00`.
- Risk meaning must never depend on colour alone.

## Current Assignment 2 progress tracker

| Work item | Current status as of 3 Oct 2026 | Evidence/next action |
|---|---|---|
| Assignment 1 project plan | Complete | Submitted PDF reviewed and summarised here |
| Topic and product scope | Assignment 2 expansion selected; governance review pending | DTDLINK now targets benign vs potentially dangerous; record group approval and second reader because Assignment 1 was phishing-only |
| Figma prototype | Complete for Assignment 1 | Reuse and revise later with real Assignment 2 metrics |
| Assignment 2 requirements overview | Reviewed | Course specification and Weeks 4-7 map available locally |
| Assignment 2 master structure and sequence | Complete | `ASSIGNMENT2_MASTER_PLAN.md`; Stage 7 complete and Stage 8 next |
| Python/Jupyter environment | Complete (15 Sep 2026) | Project-local `.venv`; Python 3.9.6, JupyterLab 4.3.5; pinned dependencies in `requirements.txt`; `pip check` clean and 3 Stage 0 smoke tests passed |
| Base phishing dataset extraction/inspection | Stage 1 complete (reviewed 17 Sep 2026) | `reports/audit/stage-1-data-audit.md`, `notebooks/01_data_audit.ipynb`, `docs/decisions.md`; option B selected; no cleaning/training |
| Cleaning and deduplication pipeline | Stage 2 complete (18 Sep 2026) | `src/dtdlink_ml/data_cleaning.py`, `notebooks/02_cleaning.ipynb`, `reports/cleaning/`, `docs/stage-2-cleaning-notes.md`; 641,113 unique cleaned URLs; repeat hashes match |
| Registrable-domain-aware split | Stage 4 complete (24 Sep 2026) | `src/dtdlink_ml/data_splitting.py`; reproducible 60/20/20 grouped split, zero overlap, locked manifest hash |
| URL parser | Stage 3 complete (19 Sep 2026) | `src/dtdlink_ml/url_parser.py`; offline, missing-scheme and malformed-input handling verified |
| Feature dictionary and extraction code | Stage 3 complete (19 Sep 2026) | `src/dtdlink_ml/feature_extraction.py`, `docs/feature_dictionary.md`; 36 numeric features and deterministic full-data output |
| Feature unit tests | Stage 3 complete (19 Sep 2026) | `tests/test_url_parser.py`, `tests/test_feature_extraction.py`; 50 robustness inputs; all 98 project tests passed |
| Exploratory analysis and charts | Stage 4 complete (24 Sep 2026) | `notebooks/03_eda_and_splitting.ipynb`, `reports/figures/`, `reports/tables/`; model-directed EDA uses training only |
| Classification baseline | Stage 5 complete (2 Oct 2026) | Logistic Regression and Decision Tree compared on validation in `reports/classification/` |
| Alternative/tuned classifier | Random Forest at threshold 0.5 selected (2 Oct 2026) | Three-model comparison in `notebooks/04_classification.ipynb`, decision D-005; test metrics unused |
| Within-class clustering | Stage 6 complete (2 Oct 2026) | Train dangerous only: 127,256 URLs, 34 features, K-means k=7; profiles/examples, 120 tests and repeat-output hashes verified; see reports/clustering/ |
| Error analysis | Stage 7 complete (3 Oct 2026) | `reports/evaluation/`; test metrics, subtype recalls, 20 FP/FN examples and feature comparisons |
| Final model export | Stage 7 complete (3 Oct 2026) | `models/final_pipeline.joblib`, metadata and reusable `predict.py`; offline/reload checks passed |
| Assignment 2 report | Not started/evidenced | Build sections alongside experiments rather than at the end |
| Reproducible README | Not started/evidenced | Document environment, preprocessing, training, evaluation, and prediction commands |
| Weekly Assignment 2 meeting minutes | Must continue | Update every week and record decisions/change approvals |
| Assignment 2 contribution form | Pending | Complete and sign before submission |

## Stage 0 completion record — 15 September 2026

- Created the Assignment 2 structure: `data/raw/`, `data/interim/`,
  `data/processed/`, `notebooks/`, `src/dtdlink_ml/`, `tests/`, `models/`,
  `reports/figures/`, `reports/tables/`, and `docs/meeting_minutes/`.
- Created a project-local `.venv` so Assignment 2 packages do not modify the
  macOS system Python.
- Created `requirements.txt` with Python 3.9-compatible pinned versions for
  JupyterLab, data processing, modelling, visualisation, URL/domain handling,
  and testing. Compatibility pins were added for the Xcode Python runtime's
  LibreSSL and the selected Matplotlib version.
- Created/updated `README.md`, `.gitignore`, `src/dtdlink_ml/__init__.py`, and
  `tests/test_environment.py`.
- Verification: Python 3.9.6; JupyterLab 4.3.5; `pip check` reported no broken
  requirements; all 3 environment smoke tests passed.
- Dataset source confirmed without extraction or analysis:
  `Week-08/Assessment/Basic_Datasets.zip`, member
  `Basic_Datasets/Phishing URL Detection/malicious_phish.csv`; the member passed
  the ZIP integrity check.
- Durable handoff checkpoint: `docs/checkpoints/stage-0-complete.md`.
- At the time Stage 0 was completed, the next stage was Stage 1 data audit and
  target-label decision. That historical handoff has now been superseded by the
  Stage 1 checkpoint below.

## Stage 1 completion record — completed 15 September, reviewed 17 September 2026

- Raw member extracted byte-for-byte to `data/raw/malicious_phish.csv`; CSV SHA-256: `d83ce942075dd63ed4d11560cfdcd9d512caa3d680e292f22cab484e8f074d01`.
- Reproducible audit: `src/dtdlink_ml/data_audit.py`; companion notebook: `notebooks/01_data_audit.ipynb`; Vietnamese report and JSON/JSONL evidence: `reports/audit/`.
- Shape: 651,191 rows × 2 columns (`url`, `type`, explicitly loaded as strings).
- Raw labels: benign 428,103; defacement 96,457; malware 32,520; phishing 94,111.
- No empty/whitespace-only cells or checked missing-value tokens. Exact duplicate excess: 10,066 rows; URL duplicate excess: 10,072. Six URLs have conflicting benign/phishing labels (12 records).
- Main risks: duplicate concentration in malware, class imbalance, label-format association (all defacement starts http://), repeated hosts, unusual URL characters, unavailable collection dates and label provenance.
- Verification: pandas and independent csv.reader checks agree; source hashes unchanged; repeat execution matched all summary fields except audit timestamp. Notebook cells executed sequentially with project Python and stdout captured; actual Jupyter kernel launch was blocked by sandbox local socket restrictions. No Stage 0 rerun.
- No cleaning, filtering, target mapping, feature pipeline, splitting or training performed.
- Target selected by the student: option B, `benign` versus
  `potentially_dangerous`; phishing, malware, and defacement map to the positive
  class. Raw counts before cleaning are 428,103 versus 223,088.
- Decision, rationale, mapping, wording, and limitations are recorded in
  `docs/decisions.md`. No target column has been created yet.
- Stage 1 completion gate is satisfied: the audit report exists, the target
  decision is recorded in `docs/decisions.md` and this file, independent counts
  match the report, and the raw CSV hash remains unchanged.
- Because B expands the submitted
  Assignment 1 scope, group acknowledgement and a named second reader still
  need to be recorded under the team's change-control rule. This is a separate
  governance follow-up and does not change the recorded Stage 1 technical result.
- Stage 2 must address these inherited issues: preserve the raw CSV; apply the
  B mapping reproducibly while retaining raw `type`; define documented rules
  for exact duplicates, 6 conflicting URLs, and 7 URLs with edge whitespace;
  retain or explicitly justify handling Unicode, control characters, very long
  URLs, and parse issues; record row counts before and after every rule; keep
  format/class association and repeated-host leakage visible for later feature
  and split work rather than hiding them through cleaning.
- Next implementation stage: Stage 2 reproducible cleaning. Begin with a plain
  language explanation and a named-file plan, then wait for explicit approval
  before changing implementation code. Do not edit the raw CSV or train models.
- Durable handoff checkpoint: `docs/checkpoints/stage-2-ready.md`.

## Stage 2 completion record — 18 September 2026

- Implemented the reusable pipeline in `src/dtdlink_ml/data_cleaning.py` and
  its automated checks in `tests/test_data_cleaning.py`.
- The pipeline verifies the Stage 1 raw fingerprint and data contract, trims
  edge whitespace from 7 URLs, quarantines all 12 rows from 6 conflicting URLs,
  removes 10,066 exact duplicate URL-label rows, retains other unusual URL
  forms, and applies target B while preserving the original `type`.
- Output: `data/interim/malicious_phish_cleaned.csv`, containing 641,113 rows,
  641,113 unique URLs, and columns `url`, `type`, `target`.
- Cleaned source-label counts: benign 428,074; defacement 95,308; malware
  23,645; phishing 94,086. Binary counts: target 0 = 428,074 and target 1 =
  213,039.
- Conflicting records remain inspectable in
  `reports/cleaning/conflicting_records.csv`; every row-count change and output
  fingerprint is recorded in `reports/cleaning/cleaning_audit.json`.
- The pipeline ran twice with identical cleaned, conflict, and audit hashes.
  The raw hash remained
  `d83ce942075dd63ed4d11560cfdcd9d512caa3d680e292f22cab484e8f074d01`.
- All 16 project tests passed. `notebooks/02_cleaning.ipynb` executed all five
  code cells without error, and its saved HTML rendering was checked.
- Plain-language learning notes: `docs/stage-2-cleaning-notes.md`; durable
  handoff: `docs/checkpoints/stage-3-ready.md`.
- Remaining risks carried forward: source-format/class association, unavailable
  label provenance and collection dates, unusual/malformed inputs for parser
  tests, and domain repetition for the Stage 4 leakage-safe split.
- Next implementation stage: Stage 3 URL parser, feature extractor, feature
  dictionary, and unusual-input tests. No feature extraction, splitting, or
  modelling occurred in Stage 2.

## Stage 3 completion record — 19 September 2026

- Implemented a reusable offline parser in `src/dtdlink_ml/url_parser.py`. It
  preserves original URL text, recovers host/path structure when a scheme is
  absent, identifies the real host after user-info, parses IPs/ports/domain
  components, and returns stable issue codes instead of crashing.
- Public-suffix parsing uses the bundled snapshot with network refresh and
  cache writes disabled. Prediction still makes no online lookup or destination
  request.
- Implemented `src/dtdlink_ml/feature_extraction.py` with 36 numeric lexical,
  structural, domain, brand-position, encoding, Unicode and parser-health
  features. Feature calculations do not read `type` or `target`.
- The fixed schema, exact calculations, limitations, vocabularies and Assignment
  1 signal mapping are documented in `docs/feature_dictionary.md`; decision
  D-003 is recorded in `docs/decisions.md`.
- Added `tests/test_url_parser.py` and `tests/test_feature_extraction.py`. The
  suite includes 50 normal, malformed, encoded, Unicode, IP-host,
  control-character, long and suspicious robustness inputs. All 98 project
  tests passed.
- Streaming extraction produced `data/processed/url_features.csv`: 641,113
  input rows, 641,113 output rows and 36 numeric features. The processed CSV
  SHA-256 is
  `fe049dd9f6b2c92570354b28b2885312f64c73b03b7053be06bc35cce5a591ff`.
- 641,093 rows parse without a fatal issue; 20 retained rows have fatal parse
  issues. Missing scheme occurs in 463,157 rows and is recoverable, while 88
  rows contain control characters.
- Two complete extraction runs produced identical processed CSV and audit JSON
  hashes. Raw and cleaned fingerprints remained unchanged. Evidence is stored
  in `reports/features/feature_extraction_audit.json`.
- Completion gate re-verified on 20 September 2026 after comment-only cleanup:
  all 98 tests passed; the 36 feature names are unique; the single-URL output,
  processed CSV header, audit schema, and feature dictionary all match the same
  fixed feature schema; output hashes remain unchanged.
- Dataset-derived TLD frequency was deliberately deferred. If selected later,
  it must be fitted only on Stage 4 training data to prevent leakage.
- Durable handoff: `docs/checkpoints/stage-4-ready.md`.
- Next implementation stage: Stage 4 feature exploration and a locked
  registrable-domain-aware train/validation/test split. No model was trained and
  no held-out test set was created or used during Stage 3.

## Stage 4 completion record — 24 September 2026

- Implemented `src/dtdlink_ml/data_splitting.py` and
  `tests/test_data_splitting.py` for the pre-split data contract, stable group
  keys, deterministic grouped partition, leakage checks, training-only EDA,
  figures, tables and audit evidence.
- Verified the 641,113-row Stage 3 table: fixed 36-feature schema, unique URLs,
  allowed labels, complete finite non-negative numeric values and binary
  boolean features.
- Identified 155,558 registrable domains. Fourteen rows without a domain receive
  separate label-independent SHA-256 URL fallback groups. There are 40,609
  repeated groups; the largest has 13,422 URLs.
- Used ten `StratifiedGroupKFold` base folds with seed 42 and a deterministic
  allocation search. Final split: train 384,832 rows, validation 129,332 rows,
  and test 126,949 rows. All 155,572 groups occur in exactly one split and all
  pairwise group overlaps are zero.
- Locked the test assignment with split-manifest SHA-256
  `fbcbcf2ff68e26acfa2bb435b53c262645688a54a195ff64e283e7ff753ffc2f`.
  It must not be used for model or threshold selection and is next permitted in
  the one-time Stage 7 final evaluation.
- Generated training-only distributions, class comparisons, binary-feature
  rates, domain concentration and correlation evidence. No feature was removed.
- Main caution: explicit schemes are strongly associated with original source
  labels (benign 8.26%, defacement 100%, malware 94.88%, phishing 26.40%), so
  model performance may partly reflect source formatting.
- Training-only checks found two constant-zero features and three feature pairs
  with absolute Pearson correlation at least 0.85. Scaling and any optional
  TLD-frequency lookup are reserved for training-only fit in Stage 5.
- All 105 project tests passed. The pipeline reproduced the same manifest hash
  across repeated runs. All nine notebook code cells passed sequential
  execution; normal kernel execution was blocked only by sandbox socket rules.
- The Stage 4 acceptance review independently recomputed all 641,113 URL ids,
  split counts, target rates, high-correlation values and group intersections
  directly from the feature table and manifest; every recorded value reconciled.
- Durable handoff: `docs/checkpoints/stage-5-ready.md`.
- Next implementation stage: Stage 5 classification model training and
  validation. No model has been trained and the test set remains unused.

## Stage 5 completion record — 2 October 2026

- Implemented `src/dtdlink_ml/train_classifier.py` and
  `tests/test_train_classifier.py` to verify the locked Stage 4 input hashes,
  exclude test rows from fitting and comparison, and evaluate three classifiers
  on the same validation partition.
- Compared Logistic Regression, Decision Tree and Random Forest. The student
  selected Random Forest on 1 October and threshold 0.5 on 2 October; decision
  D-005 records the validation trade-off.
- Selected Random Forest validation results: accuracy 92.18%, precision 84.52%,
  recall 93.58%, F1 88.82%, 2,758 missed dangerous URLs and 7,357 false alarms.
  These are selection results, not final test estimates.
- Saved reproducible tables and selection metadata in `reports/classification/`,
  updated `notebooks/04_classification.ipynb` and the Stage 5 README command.
  Notebook code cells executed sequentially and the saved chart was inspected;
  a normal kernel was blocked by sandbox socket restrictions.
- All 112 project tests passed. Feature-table and split-manifest SHA-256 hashes
  match the Stage 4 records. The final test set was not used for model metrics,
  tuning or threshold selection and remains reserved for Stage 7.
- Limitations: validation selection optimism, source-format association and
  uncalibrated model probabilities. The final model pipeline has not yet been
  exported; that belongs to Stage 7.
- Durable handoff: `docs/checkpoints/stage-6-ready.md`.
- Next implementation stage: Stage 6 within-class clustering using Week 6/7
  concepts and no class label as a clustering feature.

## Stage 6 completion record — 2 October 2026

- User authorized full Stage 6 implementation after the file plan and numeric
  flow explanation. Implemented `src/dtdlink_ml/cluster_urls.py` and
  `tests/test_cluster_urls.py`; notebook `notebooks/05_clustering.ipynb` calls
  the reusable module and reads saved evidence.
- Selected only true-label `potentially_dangerous` (`target=1`) TRAIN rows:
  127,256 URLs. No validation/test distributions, fitting or metrics were used.
  Membership and file hashes are checked; raw URL IDs are verified in chunks.
- Labels/metadata are excluded through the fixed numeric-feature whitelist.
  Removed two population-constant features (`brand_in_userinfo`,
  `has_confusable_unicode`); retained 34 nonconstant features, including
  correlated ones, as a documented baseline. StandardScaler fits on the
  selected population only.
- Fit K-means for k=2–8, n_init=10, seed=42. Selected k=7 by maximum
  silhouette on the SAME fixed random 2,000-row sample: 0.292263.
  Sizes in cluster-ID order: 40,662; 26,369; 53; 5,730; 4,386; 47,106; 2,950.
- Each cluster has original-scale means/medians, standardized differences
  relative to the selected-class mean, cautious domain interpretation and
  three real representative URLs (21 total). Source-type composition is
  calculated only after k selection as a validity/source check.
- Outputs: five CSV tables, `clustering_summary.json` and Vietnamese
  `stage-6-clustering-report.md` under `reports/clustering/`; three PNG figures
  under `reports/figures/`. README reproduction command and decision D-006
  record method and limitations. No classification settings were changed.
- Verification: full suite 120 passed; repeat execution produced identical
  hashes for all five CSVs and summary JSON; independent fresh fit labels and
  raw profile means reconcile. K-means inertia is also checked independently
  with non-BLAS arithmetic. Input hashes remain the Stage 3/4 locked hashes.
  All five notebook code cells executed sequentially with project Python;
  outputs and figures saved. This does not claim a normal Jupyter kernel run.
  All three figures visually inspected, profile chart repaired for rare-signal
  contrast and re-inspected.
- Limitations: silhouette 0.292 is modest; the rare 53-row abnormal-text group
  has only one point in the silhouette sample. ARI under seed 43/44 is
  0.97749/0.60157, so grouping is not fully stable across initialization.
  PCA's first two axes explain only 24.28% of variance. Scaling of rare
  booleans, correlation, source formatting and repeated domains can influence
  results. DBSCAN remains optional and was not run.
- Stage 6 completion gate satisfied: one-class/no-label input, interpreted
  clusters with real examples, numerical/repeat checks and preserved test lock.
- Durable handoff: `docs/checkpoints/stage-7-ready.md`.
- Next stage: Stage 7 final test evaluation, error analysis and model export.

## Stage 7 completion record — 3 October 2026

- Student authorized full Stage 7 after reviewing the file plan. Created
  `src/dtdlink_ml/evaluate.py`, `src/dtdlink_ml/predict.py`,
  `tests/test_evaluate.py`, `tests/test_prediction.py` and
  `notebooks/06_final_evaluation.ipynb`; updated README and decisions.
- Verified locked feature/manifest hashes, label mapping and Stage 5 selection.
  Refit only the frozen 100-tree Random Forest on 384,832 train rows with
  seed 42 and the exact selected settings; validation metrics reproduced Stage 5
  before unlocking 126,949 test rows. Threshold remains 0.5. No train+validation
  merge, test tuning, calibration or clustering scaler was added.
- Test: accuracy 0.9178882858, precision 0.8521994135, recall 0.9155212247,
  F1 0.8827261886; TN 77,294, FP 6,804, FN 3,620, TP 39,231.
- Original-label recalls: phishing 0.833555 (3,122 FN / 18,757 rows),
  malware 0.898710 (369 FN / 3,643), defacement 0.993692 (129 FN / 20,451).
  Benign false-alarm rate 0.080906 (6,804 / 84,098). Do not substitute binary
  dangerous recall for phishing recall.
- Saved six evaluation artifacts in `reports/evaluation/`, confusion matrix in
  `reports/figures/`, final pipeline and metadata in `models/`. Error analysis
  compares FP/TN and FN/TP and includes 20 deterministic source/error examples.
  Missed dangerous URLs have shorter median length and fewer scheme/suspicious
  term signals than TP; these are associations, not causal explanations.
- Export bundles feature order, classifier and threshold. Existing offline
  parser/extractor source accompanies the artifact; source/runtime/schema/hash
  checks reject incompatible loading. No additional fitted preprocessing is
  required for this Random Forest. User inference does not persist URLs.
- Verification: full suite 140 passed; reload matches probabilities for all
  test rows within 1e-12 and all labels exactly. Observed maximum difference
  3.33e-16 reflects parallel summation, so bitwise probability equality is not
  claimed. 120 raw test URLs reproduce the feature table and predictions;
  5 new URLs work with network/DNS blocked. Output metrics/counts reconcile
  with saved predictions; a repeat command verifies cached artifacts without
  refitting or another test experiment.
- The initial bitwise reload assertion was too strict. Investigation preserved
  the original test predictions/model; export checks resumed from these files
  after establishing tiny numerical differences and zero changed labels.
  No retraining or model/threshold change resulted from test inspection.
- Four notebook cells executed sequentially with project Python, outputs saved;
  not a normal Jupyter kernel-run claim. Confusion matrix visually inspected.
- Limitations: phishing misses, uncalibrated probabilities, source/format bias,
  unverified source labels, lexical-only features, and no temporal/external
  holdout. Test is now used; future improvements require independent evaluation.
- Stage 7 completion gate satisfied. Next: Stage 8 report, reproducible package,
  clean-environment check, minutes and contribution form. Group scope-change
  acknowledgement/named second reader remain an open governance follow-up.
- Handoff: `docs/checkpoints/stage-8-ready.md`.

## How future chats should use this file

- Read `ASSIGNMENT2_MASTER_PLAN.md` after this file and follow its current incomplete stage.
- Use `DTDLINK_PROMPT_PLAYBOOK.md` when the student wants a copy-ready prompt for starting, learning, building, reviewing, checkpointing, or resuming a Stage.
- Keep teaching concise but sufficient for code literacy: purpose, input, processing flow, output, important functions, adjustable settings, result, and limitation. Explain unfamiliar syntax only when it affects understanding.
- Codex is the implementation assistant and performs approved setup,
  installation, coding, execution, testing, and debugging on the student's
  behalf. The explanation-and-acceptance gate below applies before code changes;
  operating-system approval may also be required separately.
- Never assign coding exercises or require the student to type code. After meaningful changes, provide a short walkthrough of the main code flow and show what can be safely adjusted.
- Do not silently complete a whole Stage. Treat the student as the person doing
  the project and Codex as the technical hands: before each substantial step,
  explain the goal, reason, input, method, expected output, effectiveness,
  risks, files affected, and success check; after execution, review the actual
  evidence and its meaning together.
- Treat the following as a mandatory communication sequence whenever code will
  be written or changed:
  1. **Explain before coding:** list every implementation file that will be
     created or changed, including tests, notebooks, configuration, and scripts.
     For each file, explain the problem, purpose, input, main planned logic,
     expected output, important design choices, and any risks in plain Vietnamese.
  2. **Wait for explicit acceptance:** do not create or modify implementation
     code until the student clearly says the plan is understood and approved,
     for example `OK, hãy code`. Silence or continued discussion is not approval.
     Read-only inspection and explanation may continue while waiting.
  3. **Implement the approved scope:** approval covers only the named files and
     planned behavior. If implementation reveals a material new file, behavior,
     or design choice, explain it and obtain fresh acceptance before coding it.
     Routine debugging inside the already approved files and behavior is covered.
  4. **During substantial work:** give concise progress updates when a finding
     changes the planned implementation.
  5. **After coding:** use the actual code to explain its purpose, input, main
     functions/flow, output, important lines or sections, adjustable settings,
     verification result, and limitations.
  6. Explain unfamiliar syntax only when it helps the student understand the
     project logic. Never hide the implementation behind a result summary.
- Teach code for a student who knows only basic Python. The goal is project
  understanding, not independent implementation or syntax mastery. Use this
  layered explanation:
  1. Start with the real DTDLINK problem in plain Vietnamese and a small URL
     example.
  2. Show the data flow or short pseudocode before discussing Python details.
  3. Walk through only the important blocks of the actual code: named settings,
     main functions, decisions, and error handling. Do not explain every line
     unless the student asks.
  4. Translate unfamiliar expressions immediately into plain language, for
     example, explain that `df['type']` means selecting the `type` column.
  5. Connect each code block to its observed output, why it matters to the
     model, and what could go wrong.
  6. Finish with the small set of settings the student may safely change and
     the expected consequence of each change.
- Do not assign coding exercises, syntax drills, memorisation, or require the
  student to reproduce functions. Optional understanding checks must concern
  project reasoning and may be answered conversationally without writing code.
- Treat the student as doing the project through informed decisions and
  explanations; Codex supplies the typing and technical execution. A component
  is complete only after the approved code is written, verified, and explained
  back through the actual implementation and results.
- Treat the Assignment 1 decisions above as the current baseline, not as generic suggestions.
- Do not switch to another cybersecurity topic unless the user explicitly approves a scope change.
- Preserve the offline, privacy-first, non-clickable-URL, and cautious-wording constraints.
- Do not claim an Assignment 2 task is complete without new evidence in the workspace or explicit confirmation from the user.
- When work is completed, update the tracker with the date, result, and relevant file path.
- If course instructions conflict, prioritise the newest dated Canvas/course instruction and record the change here.
