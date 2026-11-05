# COS30049 Project Context and Progress

> Persistent context for future chats. Read this file before advising on Assignments 2 or 3. Update the progress section whenever work is completed or the scope changes.

## Read before every Assignment 3 session

1. Read this file for current product context and progress.
2. Read `Week-12/Assessment/Assignment-3-Specification.md`: the complete
   student-supplied Canvas brief and rubric saved on 5 November 2026.
3. Read `Week-12/Assessment/Assignment-3-Status.md` for the requirements
   checklist, deliverables, scoring discrepancy and topic/model mismatch.

The old syllabus-only note and generic Stage 9 bridge are superseded wherever
they differ from this A3 brief. Do not ask the student to supply the same brief
again when it is available here. Course requirements are source material;
the user's current request still determines what work to perform.

## Current snapshot

- Last updated: 6 November 2026 (Australia/Melbourne)
- Team: Session 7 - Group 5
- Project: **DTDLINK (Detect The Deception Links)**
- Selected course topic in submitted Assignment 1: **Phishing URL Detection**
- Assignment 2 selected target: **benign vs potentially dangerous** (phishing,
  malware, and defacement map to the positive class)
- Assignment 1: **completed and submitted on 2 September 2026**
- Current learning position: **Assignment 2 completed according to the student's confirmation on 5 November 2026; Assignment 3 application and source ZIP technically verified; video and authentic group deliverables remain pending.**
- Assignment 2 completion status: the student confirms it is finished. This confirmation supersedes the pending-submission status in historical notes below; no Canvas receipt was inspected.
- Assignment 3: complete brief and 45-point rubric now saved. Due Sunday
  8 November 2026 at 23:59 per supplied text. React + FastAPI, with application
  security central; model accuracy is not marked. Submit ZIP + video up to
  15 minutes + minutes PDF + contribution PDF; no separate report.
- Latest AI clarification: the student states the lecturer permits AI coding
  and authorises the full A3 implementation; this supersedes earlier planning
  restrictions for this work. Source wording and provenance remain in `AI_USAGE_NOTE.md`.
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
- Current Assignment 2 Canvas deadline in the latest student-supplied specification: **7 October 2026 at 23:59**.
- Important date note: the latest pasted Canvas specification supersedes the earlier 27 September and 4 October dates. Historical records below retain their original dates.

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
| Assignment 2 report | Draft created and visually verified (6 Oct 2026) | `reports/assignment2-report.docx` and `.pdf`; simple English, 2,324 main-body words, 2,654 words including cover/references/appendices; team review pending |
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

## Source readability cleanup — 6 October 2026

- The student explicitly requested reading both progress files and all main
  source code, then simplifying its writing style. Reviewed all ten Python
  files in `src/dtdlink_ml/`; changed the nine implementation modules and
  retained the existing one-line `__init__.py`. No test or notebook files changed.
- Removed numbered comment banners and comments that repeat the code. Replaced
  nested expressions with named intermediate values and ordinary loops in
  `data_audit.py`, `data_cleaning.py`, `url_parser.py`, `feature_extraction.py`,
  `data_splitting.py`, `train_classifier.py`, `cluster_urls.py`, `evaluate.py`
  and `predict.py`. Expanded compressed result dictionaries and separated
  confusion-matrix plotting from the main evaluation flow.
- Preserved the feature names/order, URL parsing results, label mapping,
  domain-group rules, model parameters, threshold 0.5, offline behavior and
  cautious prediction wording. The saved model and data files were not changed.
- Before/after verification: all 140 existing tests passed; 2,598 parser/feature
  cases matched exactly, 2,594 raw-URL probabilities matched within 1e-12 with
  identical labels, and full cleaning outputs had identical hashes. All
  641,113 URL/group identities and full training summary tables matched.
- All 126,949 saved test predictions matched within 1e-12 with identical labels,
  without refitting or tuning. Test outcomes, subgroup tables, error examples,
  evaluation-report bytes and confusion-matrix PNG bytes matched. Raw-class
  profiles for all 651,191 source records matched. A fixed 496-row dangerous
  training sample reproduced clustering results/profiles/figure bytes; bounded
  train/validation samples reproduced all three classifiers' comparison tables.
  This does not claim a new full clustering or training run.
- Updated only inference-source fingerprints in `models/model_metadata.json`
  and its corresponding artifact hash in `reports/evaluation/test_metrics.json`
  after equivalence checks. Model, feature-table and split-manifest hashes,
  evaluation metrics and original evaluation timestamp remain unchanged.
  Default model loading and the cached Stage 7 command passed. Source compilation
  and `git diff --check` passed; the existing joblib CPU-detection warning remains.
- Assignment 2 remains at Stages 0–7 complete, with Stage 8 packaging next.
- Follow-up on the same date: the student requested a shorter version that
  remains simple. Reduced `src` from 3,622 to 3,279 physical lines (343 lines,
  about 9.5%). Reused one raw-CSV reader/hash check, the existing label-count
  helper and one classifier probability check. Added empty-field defaults to
  `ParsedURL`, removing repeated empty-result assignments. Kept short expressions,
  arguments and result fields together while retaining explicit error handling.
  Formatting-only edits were checked for identical Python syntax trees.
- Repeated before/after checks passed for parser/features, full cleaning output,
  URL/group identities, training tables, saved predictions, evaluation reports,
  fixed-sample clustering and bounded classifier comparisons. All 140 existing
  tests, source compilation, cached evaluation and default model loading passed.
  No test files or saved classifier bytes changed; source/metadata hashes were
  synchronized again after verification.
- Second simplification pass on the same date, at the student's request (simpler,
  more human-looking, shorter): `src` reduced from 3,279 to 2,480 lines. Removed
  one-line helper functions, merged the three locked-data readers into
  `train_classifier.load_locked_data`, reused `data_cleaning.read_raw` in the audit
  and the single `file_sha256`, and wrote feature/brand checks as plain set
  operations. Public names used by tests/notebooks are unchanged.
- Fixed a pre-existing bug: `python -m dtdlink_ml.predict URL` (README command)
  always raised "Unsupported pipeline artifact" because the class in `__main__`
  differed from the pickled class. The library call `load_pipeline()` was not affected.
- Verification: 140 tests passed; parser/features identical for all 641,113
  cleaned URLs plus edge cases; a full Stages 1-6 rerun in a scratch copy of the
  project reproduced all 47 compared files byte-for-byte (feature table
  `fe049dd9...`, manifest `fbcbcf2f...`, EDA tables/figures, classifier
  comparison, k=7 clustering), JSON compared after path substitution and audit
  timestamp removal. Stage 7 reports/figure were rebuilt byte-identically from the
  saved test probabilities, and the recovery check reloaded the model on all test
  rows (max difference 3.33e-16, identical labels) without refitting or new test
  scoring. Only the inference-source hashes in `models/model_metadata.json` and
  the matching artifact hash in `reports/evaluation/test_metrics.json` changed.
- Third pass on the same date (student request, readability for a second-year
  level; AI use is permitted per `AI_USAGE_NOTE.md`): rewrote `src` with short
  everyday variable names, explicit `for`/`if` instead of comprehensions,
  lambda and `np.select`, small private helpers folded into the main functions,
  and very few comments. `src` is now 2,720 lines (explicit loops are longer).
  Public names used by tests/notebooks unchanged. Verification repeated: 140
  tests passed; parser/features identical to the original git commit for
  641,180 inputs; a full Stages 1-6 rerun in a scratch copy reproduced all 47
  compared files; Stage 7 reports/figure rebuilt byte-identically from saved
  probabilities and the recovery reload check passed (max difference 3.33e-16)
  without refitting or new test scoring. Inference-source hashes re-synced.
- Fourth pass on the same date (student request): translated every Vietnamese
  string in `src` to English (cluster descriptions, Stage 6 and Stage 7 report
  text) and added a one-line docstring to every function/class. Regenerated
  `reports/clustering/stage-6-clustering-report.md` (from a scratch rerun whose
  other 46 compared outputs were byte-identical) and
  `reports/evaluation/stage-7-evaluation-report.md` (from the saved test
  probabilities; no refit or new test scoring); both reports are now in English
  with the same numbers. Updated the Stage 7 report hash and inference-source
  hashes in `reports/evaluation/test_metrics.json` / `models/model_metadata.json`.
  140 tests and the cached Stage 7 verification passed. Saved notebook outputs
  still show the old Vietnamese cluster descriptions until re-run.
- Figure reduction on the same date (student decision): removed four figures and
  their code: `train_feature_correlation.png`, `numeric_feature_distributions.png`,
  `domain_concentration.png` (Stage 4) and `clustering_pca.png` (Stage 6, including
  the PCA import/constant and the `pca_explained_variance_ratio` summary key).
  Six figures remain: class balance, feature box plots, binary feature rates,
  k selection, cluster profiles and test confusion matrix. A scratch rerun
  reproduced all other outputs byte-for-byte; only `split_audit.json` (figure
  list), `clustering_summary.json` (PCA key) and the Stage 6 report (PCA
  sentences) changed and were copied into `reports/`. Notebooks 03/05 and README
  updated. The report draft initially retained one sentence about the 24.28%
  PCA variance; the later report revision below removed it.
- `docs/technical-architecture*.html` still mention a few old private helper
  names (`_extract_features_from_parsed`, `_domain_parts`, `_split_for_analysis`,
  `build_summary`).

## Compact source style — 7 October 2026

- After reverting the longer readability rewrite, the student requested small,
  role-specific style changes without adding length. Updated the nine `src`
  implementation modules, keeping function signatures and ordinary Python.
  Features return a direct dictionary, cleaning retains pandas operations,
  audit uses a compact tuple of checks, parser retains explicit branches and
  model definitions sit together. Renamed only ambiguous local variables and
  removed redundant comments. No new helper functions or source files.
- Source length: 2,740 -> 2,716 lines. All 140 tests pass; compilation and
  `git diff --check` pass. Before/after checks match for 2,514 parser/feature
  inputs, sampled split/EDA/classifier/clustering/error results, and the full
  651,191-row audit/cleaning outputs written to temporary directories.
- Saved model bytes, tests and notebooks are unchanged. Reloading all 126,949
  saved test rows gives identical labels and probability differences at most
  3.33e-16 (tolerance 1e-12); no fitting or tuning. Source fingerprints and the
  metadata artifact hash were synchronized; CLI/cached evaluation pass.
  This pass changes readability, makes no authorship claim and does not change
  the Stage 8 report/package status. The existing joblib CPU warning remains.

- Follow-up: the student requested a less polished, casual presentation.
  Shortened the repeated module headers and a few docstrings, used short module
  comments in audit/training/features, and placed related length/count entries
  together in the feature dictionary. Source now has 2,690 lines. Executable
  syntax trees match the previous version after excluding documentation;
  140 tests, source compilation, default model loading, cached evaluation and
  `git diff --check` pass. Only required source/metadata fingerprints changed;
  saved model, metrics, tests and notebooks remain unchanged.

## Stage 8 report draft — 6 October 2026

- The student requested an Assignment 2 report, then specified simple English,
  a student writing style, less detail and fewer than 3,000 words.
- Created `reports/assignment2-report.docx` and `reports/assignment2-report.pdf`.
  Initial draft: 2,324 main-body words / 2,654 whole-document words, nine pages
  and two saved figures. Revised at the student's request after figure reduction:
  2,570 main-body words including tables and captions; whole document: 2,899
  words including cover, references and appendices. Twelve pages, of which nine
  contain the main report; all six remaining figures and compact evidence tables.
- Covers problem/users/scope, dataset and cleaning, reusable features, grouped
  split, training-only EDA, three-classifier comparison and threshold trade-off,
  final test metrics and subgroup/error analysis, within-class clustering,
  implementation/verification, limitations, future work and conclusion.
- Includes six Harvard-style references checked against research papers,
  official scikit-learn documentation and the course-linked dataset listing.
  Appendix gives one real representative example per cluster and evidence paths.
- Rechecked 13 current data/export/source fingerprints before authoring. Used
  saved metrics and charts; no training, test retuning, source/model/data changes
  or claims of a clean-environment run. Rendered the initial DOCX with the bundled
  compiler, inspected all nine page images, and checked PDF text/metrics.
- The six-figure revision rechecked the progress records, specification, source,
  notebooks and saved analysis outputs. Added feature class boxplots and binary
  rates to data analysis, and k selection and the cluster profile heatmap to
  clustering; kept class balance and test confusion matrix, renumbered Figures
  1–6, and removed the obsolete PCA sentence. Short captions explain the training
  sample/display clipping, rates versus feature importance, fixed silhouette
  sample and saturated heatmap colours. English remains simple and brief.
- Verified all six embedded image hashes against the remaining project PNGs,
  sequential figure captions, ten tables, current metrics, no PCA claim, and
  whole-document word count below 3,000. Inspected all twelve final page images
  and repaired pagination before exporting the PDF. No source, model, dataset,
  notebook, training or test-selection changes were made by this report revision.
- Report remains subject to student/team review. Stage 8 is NOT complete:
  README/Conda and preprocessing instructions, clean-environment verification,
  final ZIP, real weekly minutes, signed contribution form and scope-change
  acknowledgement/named second reader remain outstanding.

## Stage 8 technical package — 7 October 2026

- The student confirmed real weekly minutes and the contribution form are
  already available, and requested fixes to the remaining deliverables and an
  upload list. Those two administrative documents were not altered or inspected.
- Final report: simple English, 2,649 main-body words / 2,978 whole-document
  words, 13 pages, six current figures. Corrected the current test count to 137,
  clarified model metadata and implementation challenges, and added original
  label composition for every cluster alongside feature-based descriptions.
  Every page was visually checked and all embedded figures match current PNGs.
- Completed portable README instructions for Conda, prepared-data processing,
  training, prediction, fixed evaluation and optional raw cleaning. Added
  `environment.yml`, `VERIFICATION.md` and `reports/submission-checklist.md`.
- Installed pinned requirements in a fresh Python 3.9.6 virtual environment;
  `pip check` passed and all 137 tests passed. Conda YAML was parsed and checked;
  Conda is unavailable here, so no actual Conda run is claimed.
- Reproduced full Stages 3-7 in a separate copy using frozen settings. Feature
  table and split manifest were byte-identical; ten output CSVs, clustering
  selection/stability and final metrics matched within the recorded tolerances.
  Original project source, processed data and selected model were preserved.
- Deliverables are `submission/session-07-group-5-assignment-2-report.pdf` and
  `submission/session-07-group-5-assignment-2-code-data-models.zip`. The ZIP
  contains only relevant code, prepared data, model, evidence, documentation,
  notebooks and tests, plus a SHA-256 manifest. Unnecessary course files,
  environments, caches and duplicate report files are excluded.
- Initial verified ZIP: 80 files, 97,206,444 bytes. CRC and every manifest hash passed;
  extracted files match the workspace originals. All 137 tests, prediction
  and cached evaluation passed directly from the final extracted ZIP.
  `reports/submission-audit.json` records the release fingerprints and checks.
- The student later explicitly requested a smaller submission ZIP. Current
  release: 53 files, 80,569,494 bytes (76.84 MiB). Removed tests/notebooks,
  verification/manifest files, decision/cleaning notes, Stage Markdown reports,
  supplementary JSONL records, full test predictions and cluster assignments.
  Retained all runtime modules, three prepared CSVs, final model/metadata,
  feature dictionary, compact audits, result tables/examples and six figures.
  Edited README and requirements only inside the ZIP, removing notebook/test
  commands and their three dependency pins. The working project is preserved.
- Trimmed ZIP CRC passed; all retained files except README/requirements match
  the previous verified ZIP byte-for-byte. Every runtime module imports with
  pytest/JupyterLab/ipykernel blocked. Loaded every split and the clustering
  population; all 126,949 test probabilities and labels match the earlier
  export (max difference 4.44e-16), 120 raw URL checks and five unusual/new
  inputs work with network/DNS blocked, and cached/recomputed test metrics match.
  Report, model, data and runtime source were not changed by this trimming.
- Stage 8 technical work is complete; final team review and Canvas submission
  remain. One member uploads these two files plus the team's existing minutes
  PDF and signed contribution-form PDF. The latest supplied Canvas specification
  shows 7 October at 23:59. No Canvas upload or unprovided scope-change approval
  has been claimed.

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

## Approved source cleanup — 7 October 2026

- User approved the readability plan before implementation. Updated the nine
  implementation modules in `src/dtdlink_ml/`: shorter consistent module
  docstrings, clearer variable names, `any()`/`sum()` for simple URL checks,
  one combined empty-URL check and the result label `Predicted benign`.
- Removed the redundant post-cleaning duplicate assertion; kept manifest row
  counts, alignment, hashes, feature-order checks and the model reload check.
  Source decreased from 2,072 to 2,040 lines (32 fewer).
- Updated the existing threshold test in `tests/test_prediction.py` to check
  both result labels and the 0.5 boundary. All 137 tests pass; the existing
  joblib CPU-detection warning remains. Source compilation and diff checks pass.
- Before/after checks: 1,316 parser/feature cases match exactly; 1,312 URL
  predictions retain classes and probabilities within 1e-12; fixed 1,000-row
  EDA tables and domain assignments match. Eight temporary report/chart files
  match byte-for-byte. Model, processed features and manifest hashes match.
- A verification script accidentally regenerated two clustering PNGs in
  `reports/figures/`; they were replaced with verified default-style renders
  from the saved CSVs. No project model refit or full-data clustering run occurred.

## Latest submission review — 7 October 2026

- The student requested a final readiness check after assembling all files.
  Review details: `reports/submission-readiness-review.md`. Deliverables were
  inspected without modifying the submission PDFs/ZIP or administrative records.
- Four types are present, but current `submission/assignment2-report.pdf` is a
  12-page version with outdated verification claims and no cluster-composition
  table. The corrected verified 13-page PDF remains in `reports/`.
- Minutes currently supplied are a five-meeting reconstructed draft with
  assumed/unconfirmed details and no dated record for 28 Sep–4 Oct. Real team
  confirmation and complete weekly coverage remain necessary. Contribution
  form has typed names on signature lines; authorisation/consensus is unverified.
- ZIP is unchanged and passes hash/CRC checks. Group-prefixed PDF filenames,
  correct final report, confirmed minutes/form and final submission remain.

## Submission recheck after student edits — 7 October 2026

- Minutes now contains only meeting 1 (2 September), plus a blank page;
  remaining meetings from the previous export are absent. Header was cleaned,
  but assumed/verify/suggested details remain.
- Previously linked Google Doc has corrected 137 tests, clean-environment
  verification and cluster label-composition Table 9. Local submission PDF is
  still the outdated 12-page export. Google Doc retains an omitted tests/
  appendix reference and has lost the dataset author-date citation.
- ZIP remains unchanged/valid. Local contribution form remains unchanged.
  See updated reports/submission-readiness-review.md for remaining actions.

## Latest final recheck — 7 October 2026

- New minutes export `submission/DTDLINK_Meeting_Minutes.pdf` restores all five
  meetings in seven readable pages. Week 28 Sep–4 Oct is still unrepresented;
  some confirm/reconstructed-draft text remains.
- Local report and contribution PDF remain unchanged. The linked Google Doc
  contains technical report corrections, but final local PDF export and two
  small citation/omitted-test-reference corrections remain.
- ZIP hash/CRC passes unchanged. Group-prefixed PDF names and member
  signature/consensus confirmation remain. Latest details are in
  `reports/submission-readiness-review.md`; no submission file was edited.


## Uploaded report corrected — 7 October 2026

- Repaired the student's newly supplied Word report and exported the final
  group-prefixed report PDF into submission/. The old submission PDF was
  backed up and replaced. Editable source is reports/assignment2-report.docx.
- Final report: 2,682 main / 2,992 whole-document words, 13 visually verified
  pages, six figures, stronger cluster profiles and original-label Table 9.
  Test count, metadata, fresh-environment and appendix claims match evidence.
- ZIP/source/model/data remain unchanged. Stage 8 report and technical package
  are ready. Genuine weekly minutes coverage, confirmation of draft details,
  all-member signatures/consensus and final Canvas submission remain.
  See reports/submission-readiness-review.md for current administrative issues.

- Final filename cleanup: minutes and contribution form now have the Session 7
  Group 5 prefix. Their PDF contents are byte-identical; no administrative facts
  or signatures were changed. Four upload filenames now match the checklist.


## All-deliverable recheck — 7 October 2026

- Report and ZIP remain byte-identical to the verified final outputs; CRC passes.
- Latest minutes export DTDLINK_Meeting_Minutes (1) (1).pdf removed the
  reconstructed-draft sentence but retains confirm/draft-planning wording,
  the weekly gap 28 Sep–4 Oct, and a filename without the group prefix.
- Form content is unchanged; contribution total is 100%, typed signatures
  require actual member agreement/authorisation. Its final page is blank.
- No deliverable was edited. Stage 8 technical outputs are ready; minutes
  finalisation, group confirmation and actual Canvas submission remain.


## Final ZIP execution check requested by student — 7 October 2026

- Extracted the exact submission ZIP to a new temporary folder and created a
  fresh Python 3.9 venv. Installed all pinned requirements from cached wheels;
  pip check passed. Executed every Python pipeline command in the README,
  including optional raw audit/cleaning using the original course archive,
  prepared feature/split processing, classifier training, clustering, cached
  evaluation, explicit frozen refit evaluation and prediction before/after fit.
- Prepared CSV hashes match, 11 result tables match, all 126,949 test
  predictions match within 1e-12 (max probability difference 3.33e-16),
  120 raw URL feature checks and five offline new/malformed inputs pass.
  All six regenerated PNG files are valid. Submission ZIP bytes are unchanged.
- Conda is unavailable; its YAML was checked and the README venv alternative
  was executed. Direct Conda execution is not asserted. Complete run evidence
  is reports/zip-final-readme-test.json. No Canvas upload was performed.

## Assignment 3 transition — 5 November 2026

- Student confirms Assignment 2 is finished and wants to move to Assignment 3.
- Re-read the saved Assignment 3 status and Stage 9 plan. Known product plan:
  React interface -> local FastAPI -> existing Assignment 2 feature pipeline
  and saved model, with cautious results, URL signals, real-data insights and
  end-to-end tests. Preserve offline analysis and no URL storage/clickable links.
- The saved course snapshot contains only a syllabus-level Assignment 3 summary;
  no official detailed specification or rubric is present in the project.
  Its old statement about publication availability is not a live Canvas check.
  Obtain the current official brief before fixing submission formats, deadline,
  marking requirements or a final Assignment 3 execution plan.
- This turn reviewed context and recorded the transition only; no frontend,
  backend or model code was created or modified.


## Full Assignment 3 brief saved — 5 November 2026

- Saved the student's complete Canvas paste byte-for-byte as
  Week-12/Assessment/Assignment-3-Specification.md, including sections 1–5,
  the video requirements, Important notes and the full 45-point rubric.
- Source: /Users/okok/.codex/attachments/1f785667-71eb-441c-a562-e4364c9ad039/Pasted text.txt
- SHA256 of both attachment and archived source:
  b31761fc83c206c007eb84f950bbd2902deede81a2447f6aac58aaa02243b8fc
- Replaced the old syllabus-only Assignment-3-Status.md with a requirements
  summary, deliverable list, video evidence checklist, marking totals and
  unresolved planning issues. Added a read-first pointer at this file's top,
  the Stage 9 bridge, prompt playbook and Week 12 summary.
- Recorded the A3-specific AI wording separately from historical September
  guidance. Preserved the source's security-mark cap discrepancy and the
  A2 combined-dangerous versus A3 phishing-topic output issue without silently
  changing the assessment rules or model. Deadline: 8 November 2026 at 23:59.
- Current task is complete: archival and context documentation only. No
  application implementation, experiment selection or model change occurred.

## Assignment 3 implementation — 5 November 2026

- User approved the proposed model, labels, full HTTP(S) input, privacy scope,
  availability defence and dependency/configuration defence, then explicitly
  requested the entire application be coded. That current instruction supersedes
  earlier per-step implementation gates for this authorised scope.
- User reports lecturer permission for AI coding; source provenance is recorded
  in AI_USAGE_NOTE.md and the A3 README. No written tutor approval is fabricated.
- Isolated application: `assignment3/backend` and `assignment3/frontend`. Frozen
  A2 model and four inference modules copied byte-for-byte, not modified/refitted.
- UI labels: Potentially dangerous / Likely legitimate, with combined-class and
  no-safety-guarantee wording. Confidence corresponds to the predicted class.
- React pages: Check URL, Session insights, How it works; validation, states,
  404, error boundary, safe token highlighting, responsive layout and interactive
  current-signal/session-score charts. At most 20 anonymous entries in memory;
  no URL history, storage, external fonts or destination requests.
- FastAPI: Pydantic contracts, GET health/model-info and POST predict, uniform
  JSON errors, model lifespan loading, trusted pre-load hash, local Swagger UI.
- Security: 2,048-character URL limit, 16 KiB streamed body limit, 5-second body
  deadline, exact frontend CORS, same-origin Swagger support, hardened headers,
  bounded off-event-loop inference, cancellation-safe slot accounting and 503.
- New A3 Python 3.12 environment; A2 environment/source/data/model untouched.
  Pinned versions and independent npm lock. Pip vulnerabilities corrected by
  isolated upgrade to 26.3; npm/pip audit now have no known findings.
- OWASP ZAP 2.17.0 passive + bounded active local scan: CSP style-src tightened;
  final scan has 0 High/Medium/Low and 53 informational observations, interpreted
  in `assignment3/docs/SECURITY_FINDINGS.md`. No complete-security claim.
- DoS evidence uses repeated real inference bursts and a separately disclosed
  controlled slow-inference harness; no unprotected production switch.
- README, Vietnamese learning guide, video checklist, real team-deliverable
  checklist, tests, local launcher and source packaging script provided.
- Section 2.8 is NOT claimed complete. Video, authentic weekly minutes, member
  contribution/signatures and acceptance of the combined-class model by tutor
  remain group follow-ups. Final verification evidence and ZIP paths are recorded
  by the packaging completion entry below.

## Assignment 3 technical package verified — 5 November 2026

- Standalone source: `assignment3/`. Final group-prefixed source ZIP:
  `submission/session-07-group-5-assignment-3-source.zip`. No Canvas upload.
- Executed: 34 A3 backend tests in the working project; standalone fresh ZIP has
  33 passed and one expected skip (original-A2-source comparison unavailable).
  Frontend: 13 tests passed and production build passed. Dependency install and
  npm ci were performed in a fresh extracted copy; the documented launcher
  started both TCP services and live HTTP checks passed.
- Model unchanged: SHA-256 d4aa8ff332ab82c36e3befce1a0e74c336b25a07a19ee9012e489c56239cb586.
  All four copied inference modules equal A2 bytes. Across 1,600 raw test URLs,
  labels match and maximum probability difference is 3.33e-16, without refitting.
- Browser QA: desktop 1280 px and phone 375 px; real predictions for both labels,
  Enter submission, validation, chart filters/detail controls, clear session,
  phone menu, no horizontal overflow in checked views, 404, service outage and
  recovery, and real Swagger Try it out POST. Screenshots and verification JSON
  are in `assignment3/evidence/`. A 10-case optional Playwright suite was authored
  and discovered, but not executed; no complete accessibility/user study claimed.
- npm and pip audits: 0 known current findings. ZAP 2.17.0 passive + bounded
  active scan: 0 High/Medium/Low, 53 informational; all interpreted in security
  notes. Actual live HTTP bursts returned 503 for excess work while health stayed
  available. Controlled slow-model harness is explicitly described as instrumentation.
- Final code formatting and secondary text contrast improvements applied;
  final source rebuilt in the clean extraction. Local QA servers were stopped
  after verification. Start the installed workspace with:
  `cd assignment3 && backend/.venv/bin/python scripts/run.py`.
- `assignment3/docs/LEARNING_GUIDE_VI.md` explains actual code flow in Vietnamese.
  README documents setup, architecture, threat model, selected two defences,
  AI disclosure, Harvard references and limits. No section 2.8 claim is made.
- Remaining student/group work: record <=15-minute video, complete authentic
  weekly minutes and contribution/signatures, and confirm topic/model acceptance
  with tutor. These have not been invented or marked complete.

## Dataset/model Insights addition undone — 5 November 2026

- The student first requested extra A2 dataset/model statistics, then explicitly
  requested undo after deciding that the detail was unnecessary. This cancels
  that addition. Do not re-add it without a new request.
- Restored the 12 affected existing files byte-for-byte from the verified
  pre-addition source ZIP and removed the six addition-only implementation/data
  files. Insights is again the original session-comparison/current-signal page;
  labels, score wording, model and all earlier application features are unchanged.
- Every packaged source file matches the existing source ZIP manifest. The ZIP
  itself was already the pre-addition version and remains byte-identical.
- Verification after rollback: production frontend build, 13 frontend tests and
  34 backend tests passed. Reloaded the running backend to remove /insights data
  endpoint; the browser page /insights remains the original React page.

## UI UX Pro Max interface redesign — 5 November 2026

- The student explicitly requested a new AI-inspired interface using the public
  nextlevelbuilder/ui-ux-pro-max-skill repository. Read its SKILL.md and UX rules,
  ran local design-system/style/React searches at revision
  b7d5353e0130feb8c5574ef1251f8a1db1873ccb, and implemented a dark graphite/violet
  workspace with a centred URL composer and consistent chart/result surfaces.
- Changed frontend App branding, CheckPage markup, styles and chart colours only;
  no new runtime dependency or remote font/script. All 13 protected backend,
  inference and model files match pre-redesign SHA-256 values. The model, API,
  class labels, confidence interpretation and existing app behaviour are unchanged.
- Session Insights remains anonymous current-session charts; the previously
  cancelled historical dataset/model-statistics feature was not restored.
- Saved design decisions, attribution and MIT notice under
  assignment3/design-system/dtdlink/. README acknowledges the design source
  and actual AI assistance. Verification: production build, 13 frontend tests,
  34 backend tests; browser checks at measured 375/768/1024/1440 CSS px, real
  prediction, validation, signal detail/filter, session selection/clearing,
  phone menu and all three routes. No overflow observed at checked widths.
- Evidence: assignment3/evidence/ui-redesign-verification.json and ui-ai-*.jpg.
  Updated source ZIP generated and manifest/CRC verified. Previous ZIP and source
  are backed up under /private/tmp/dtdlink-before-ai-ui/. No Canvas submission.

## Interface simplification — 5 November 2026

- At the student's explicit screenshot-based request, removed the sidebar privacy
  card, course/group/student-project footer, topbar model-status badge, and home
  input card's Local analysis badge. Removed the now-unused frontend health state
  and startup health request. Prediction errors still appear beside the form.
- No backend/model changes. Production build and 13 frontend tests passed. Browser
  reload verified all requested elements absent; evidence/ui-ai-clean.jpg records
  the new appearance. Source ZIP regenerated with manifest/CRC verification.

## Readable URL analysis — 5 November 2026

- User requested more specific analysis that ordinary users can understand. Added
  backend/app/analysis.py as an offline presentation layer: exact ordered URL
  parts and 11 rule observations with evidence, plain-language meaning and action.
  Existing nine patterns enriched; added nonstandard port and brand words in
  path/query. service.py and response schemas now return url_parts plus per-signal
  evidence/action; regenerated the real Swagger response example.
- Frontend URLAnalysis.jsx emphasises the actual host, highlights exact userinfo
  and hostname boundaries, offers a native details breakdown and evidence/action
  cards. Three observations show first with remaining ones expandable. Handles
  model-dangerous/no-rule and model-benign/with-rule honestly. No causal model
  attribution, certificate checks, redirect following or website visits claimed.
- Model artifact, metadata and four A2 inference modules remain byte-identical to
  the pre-update ZIP. No training, threshold, confidence calculation, validation
  policy or dependency change. Session history still excludes URL evidence/parts.
- Verification: production build, 48 backend tests and 17 frontend tests passed.
  Real browser QA at 1728 and 375 CSS px; exact misleading destination, parts
  disclosure click/Enter, seven-observation expansion and no-pattern mismatch
  reviewed. No overflow observed. Evidence: url-analysis-verification.json and
  url-analysis-*.jpg. Optional browser test suite not executed; no new scan/clean
  install claimed. Source ZIP regenerated with CRC/manifest check.
- Backend restarted on 127.0.0.1:8000 with no access logging; frontend preview
  remains on 127.0.0.1:5173. Earlier removed sidebar/course/status badges remain
  removed. Previously cancelled dataset/model statistics feature stays cancelled.

## URL-format false-positive investigation — 5–6 November 2026

- User explicitly authorised isolated A3 code/experiments/training while freezing
  completed A2. Traced frontend -> API -> copied extractor -> artifact -> label:
  exact probabilities agree; missing-scheme input is rejected by API (422), not
  silently rewritten. Reproduced Google/GitHub formatting scores.
- Scheme audit: train benign 92.34% scheme-less vs defacement 100% HTTP; strongest
  RF impurity importance is parse_issue_count then has_scheme, not uses_https.
  Adding a scheme changes five coupled features. Source/format association is
  strong; actual collection causality/current site safety is not verified.
- A3 research at assignment3/experiments/url_format/: fixed shared neutral model
  view, four numeric RF trials, character TF-IDF+numeric logistic trials and
  convergence checks, root-specific RF routing, and character-only no-L2 view.
  No threshold changes (0.5), relabelling, whitelist, hand-added demos or test
  outcomes used. Train-only fit/scaler/vocabulary; validation-only development.
- 381,494 eligible train and 128,373 eligible validation records; exclusions
  match unchanged A3 validation. Original and IDNA wire-group split overlaps 0.
  Test group metadata and preservation checksums only; no test scoring/tuning.
- Text+numeric candidate: API-formatted validation FPR 88.00% -> 11.36%, dangerous
  recall 99.21% -> 92.13%. On native explicit URLs, FPR 35.67% -> 6.74%, recall
  98.84% -> 92.61%. However benign-homepage FPR remains 38.13%, including high
  scores for the user's diagnostic examples. Root specialists reduce homepage
  FPR to ~19% but recall falls to ~58%; final character-only trials also fail.
- Decision: NO experimental model promoted. Active A3 artifact/hash d4aa8ff3...,
  metadata/API example/frontend/threshold/security remain unchanged. Do not say
  the false-positive issue is fixed. No section 2.8 claim added.
- Preserved A2: 91 protected data/model/source/test/notebook/report/ZIP files
  checked unchanged. Research candidates/cache remain local A3 and excluded from
  source ZIP. Source scripts/plans/aggregates included. Findings in
  assignment3/docs/URL_FORMAT_FINDINGS_VI.md, promotion-decision.json and all
  per-candidate metrics; validation reused, not independent final-test accuracy.
- Verification: 61 backend tests, 17 frontend tests, production build; no new
  dependencies, external URL visits/DNS or analysis services. Only RFC syntax
  documentation was read online. No demo domain treated as proof of safety.

- Completed 6 November: retained active model after all scoped candidate families
  failed joint criteria. Actual localhost API still agrees with frozen model.
  Final source ZIP CRC/SHA manifest verified; fresh source extraction using the
  installed runtime passed 60 tests with one expected A2-source-comparison skip.
  This was not a fresh dependency installation.

## Separate experimental preview — 6 November 2026

- User asked whether to try a separate version with a new model after discussing
  further improvement. Created optional assignment3/experimental-app/ using the
  already trained A3 text+numeric candidate neutral_text_recall5_converged. This
  is a runnable research preview, NOT promotion to the primary submission app.
- Primary app 5173/API 8000 retains frozen A2 hash d4aa8ff3...; preview uses ports
  5174/API 8001, exact separate CORS/CSP, independent copied source/model/config,
  preview-labelled header/title/sidebar, accurate model info and response example.
  Local .venv/node_modules links share installed dependencies only.
- Preview model SHA256 f5a7b6fb18fa3c041ccac167436ddc9d3ea44f496842314c59070a7e36303290.
  Model is character TF-IDF + 36 numeric measurements, logistic regression,
  threshold .5; combined labels unchanged. Same train/inference view, raw URL
  evidence and all application security boundaries preserved.
- Known Google/GitHub examples still score high (99.71%/98.71%); no claim the
  homepage problem is fixed. Prior validation FPR 11.36%, recall 92.13%, homepage
  FPR 38.13%; no new accuracy evaluation. Separate preview allows comparison only.
- Verification: 65 backend tests passed, one expected original-source skip; 17
  frontend tests and build passed. Live checks confirmed primary a2-rf-d4aa8ff3
  vs preview a3-preview-text-f5a7b6fb. Browser real prediction and narrow layout
  checked, description matches actual classifier, no new scan/clean install.
- New separate ZIP: submission/session-07-group-5-assignment-3-experimental-preview.zip.
  Primary packaging explicitly excludes experimental-app/ to avoid mixing two
  apps/submission versions. Preview has its own README and package script.

## Component-role model trial — 6 November 2026

- User authorised trying field-aware URL modelling. New isolated experiment at
  assignment3/experiments/url_format/field_roles/ with pre-fit hashed PLAN.json,
  four train-only fitted character TF-IDF/logistic models, separate component
  vocabularies and optional learned homepage interactions. Shared inference code
  in backend/src/dtdlink_a3/fields.py is unused by either running app.
- Same 381,494 train / 128,373 validation, domain grouping unchanged, threshold
  0.5. No test outcomes, whitelist, injected demos, relabelling or external scans.
- Balanced model: FPR 6.59%, recall 86.04%, homepage FPR 20.01% / recall 77.12%.
  Context model: FPR 10.77%, recall 90.41%, homepage FPR 33.58% / recall 88.44%.
  Both other weight variants also failed unchanged joint gates. All converged,
  zero label flips on 9,277 valid-format pairs (encoding coverage remains sparse).
- Decision: NONE promoted; primary keeps d4aa8ff3..., preview keeps f5a7b6fb....
  Context model still gives Google 60.21% / GitHub 95.06% dangerous score after
  validation-based selection; do not claim false-positive issue fixed.
- Data limit: only two train userinfo rows, no usable userinfo vocabulary at
  min_df=3; flags still represent presence. Unknown suffix parser fallback uses
  entire hostname; empty query/fragment delimiters have no separate field feature.
  Do not infer model impossibility or label error merely from this failed trial.
- Saved-model verification recomputes every validation prediction and independent
  confusion counts, plus 1,000 fresh raw-URL inference rows per model. Evidence
  in field_roles/results/verification.json. Validation reused for development,
  not an independent final assessment. A2 preservation manifest still unchanged.
- Verification completed: 68 backend tests pass; all 91 protected A2 files and
  39 primary runtime files unchanged. Live localhost /model-info confirmed both
  existing versions; preview ZIP checksum unchanged. Primary source ZIP refreshed
  with experiment scripts, plans, aggregate evidence and contract tests only.

## GitHub source snapshot — 6 November 2026

- User requested uploading the complete project source to datdonnynguyen.
  Existing target: https://github.com/datdonnynguyen/DTDLINK, branch main.
- Snapshot includes current A2 source/notebooks/reports, primary A3 React/FastAPI
  application and pinned model, isolated preview, experiment scripts and evidence.
  Both running models and A2 artifacts are retained without retraining.
- Git excludes installed environments/packages (including preview symlinks),
  generated builds, local credentials, research caches/candidate artifacts and
  duplicate submission ZIPs/extracted submissions. These remain on the local
  machine; existing raw-data ignore rules and history are preserved.
- Automated approval review rejected publishing the updated per-URL test
  predictions to the public repo because the user requested source upload, not
  publication of potentially sensitive evaluation data. Updated per-URL
  predictions, error examples and the domain-level stability sample remain local
  and are excluded from this source snapshot. Source and aggregate evidence still
  upload; no A2 data file contents are edited or deleted locally.

## Continuation state audit — 6 November 2026

- Re-read the requested context, full A3 specification, status, AI note, model
  findings and both application/research READMEs. The student's current request
  reconfirms lecturer permission for AI coding; recorded in AI_USAGE_NOTE.md as
  student-reported guidance, without changing the supplied course wording.
- Process/socket checks and actual loopback HTTP requests confirm primary
  frontend/API 5173/8000 and preview 5174/8001 respond. API versions remain
  a2-rf-d4aa8ff3 and a3-preview-text-f5a7b6fb respectively. Both artifact hashes
  match metadata and threshold stays 0.5. No training process matching the
  project's experiment scripts was found at the process-check snapshot.
- Live primary Google/GitHub dangerous scores: 97.22%/95.43%; preview:
  99.71%/98.71%. Both APIs reject a missing-scheme Google input with 422.
  Requests went only to 127.0.0.1; destination sites were not opened.
- Newest modelling family is completed, not pending: field_roles/PLAN.json
  matches its execution receipt; all four artifacts, validation predictions
  and candidate results exist. Recomputed FPR/recall from saved confusion counts
  match the JSON. All four optimisers report convergence and all four fail at
  least one preregistered gate; decision.json selected remains null.
  Whole FPR/recall and homepage FPR/recall respectively:
  fields_balanced 6.59/86.04 and 20.01/77.12%; fields_recall3 9.06/88.81 and
  30.00/84.49%; fields_recall5 12.35/91.19 and 43.78/90.35%; fields_context5
  10.77/90.41 and 33.58/88.44%. No model promotion is justified.
- A newer field_roles/results/verification.json was found during inspection.
  It records reloaded-model reproduction of 128,373 validation predictions
  and 1,000 raw-URL predictions per candidate, with no promotion. Its script
  was inspected; this audit did not rerun training or that full verification.
  Userinfo vocabulary has zero features (only two nonempty train rows);
  structural flags remain. This limits the learned userinfo-text coverage.
- Rehashed all 91 protected A2 files against a2-protected-before.json:
  unchanged. No A2 test outcomes were used. Validation results remain reused
  development evidence, not an independent final test.
- Both A3 ZIPs pass CRC and every packaged manifest hash. At this snapshot the
  primary ZIP SHA-256 is ff7cf4a73e961e982670d7a53d782896d37dddfa3a767d71f6740591595075a2;
  its packaged files match the workspace but 14 newer field_roles source/test/
  plan/result files are absent. It is runnable but not the latest research
  snapshot. Preview ZIP matches its packaged source completely. Neither ZIP
  was overwritten by this audit.
- Local file inventory found no A3 presentation video or video-link file,
  A3 minutes PDF, or A3 contribution PDF. The submission PDFs are A2 files;
  docs/animation/dtdlink-data-flow.mp4 is not evidence of an A3 presentation.
  Group artifacts may exist elsewhere, but were not verified here. Section
  2.8 and tutor acceptance of the broader combined-dangerous target remain
  unconfirmed; no Canvas submission or authentic administrative facts invented.
- Recommended next work: retain primary/preview models, reconcile newest
  research documentation and package, then prioritise the <=15-minute video,
  genuine weekly minutes and agreed contribution form before the supplied
  8 November 2026 23:59 deadline (Canvas timezone still needs confirmation).
  Do not repeat completed RF/text/root/authority/field-role fits. Further model
  work needs a distinct data-quality hypothesis and independently sourced,
  domain-disjoint evaluation data rather than tuning familiar demo URLs.
- This continuation audit changed only context/AI guidance notes. No runtime
  code, UI, model, threshold, dataset, experiment output or ZIP was modified;
  no new clean install, security scan or full test-suite run is claimed.

## Three-presenter video preparation — 6 November 2026

- User requests A3 video guidance grounded in the actual submission. Confirmed
  preferences: English narration, three separate recordings edited together;
  divide by subject first and let the group choose presenters later.
- Created assignment3/docs/VIDEO_RECORDING_PLAN_VI.md and linked it from the
  existing VIDEO_CHECKLIST.md. Proposed final 14:15 timeline: presenter A 4:15
  product/live UI/states/charts, B 4:30 real request/code/API/model, C 5:30 threat
  model/two selected defences/setup/limits. Vietnamese directions, English
  speaking cues, exact project paths/commands and practical editing checklist.
- Use the primary A2-model application consistently. No model promotion,
  runtime change, new attack execution, recording, video export or submission
  occurred. Loading/network/render-error demonstrations and security commands
  still need rehearsal on the recording machine. Existing test scripts or saved
  scans are not represented as a newly recorded live demonstration.
