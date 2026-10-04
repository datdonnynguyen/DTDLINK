# DTDLINK Master Learning and Build Plan

> This is the execution plan for Assignment 2 and the bridge into Assignment 3. Future Codex sessions must read `PROJECT_CONTEXT.md` first, then this file, determine the current stage, teach the required weekly knowledge, and only then continue implementation.

## 1. Fixed project direction

- Project: **DTDLINK - Potentially Dangerous URL Detection** for Assignment 2;
  the submitted Assignment 1 title remains Phishing URL Detection
- Selected target: binary `benign` versus `potentially_dangerous`, mapping raw
  phishing, malware, and defacement labels to the positive class
- Raw input: a URL string
- Core Assignment 2 output: a reproducible pipeline that converts a raw URL into features, classifies it, performs within-class clustering, evaluates results, and saves the final model
- Assignment 3 continuation: React interface -> FastAPI -> Assignment 2 feature extractor and model
- Constraints inherited from Assignment 1:
  - prediction must not open the URL;
  - prediction must not use an online lookup;
  - submitted URLs must not be stored;
  - the interface must not promise that a URL is safe;
  - results must include cautious wording and understandable signals.

## 2. Overall product architecture

```text
                         DTDLINK
                            |
          +-----------------+-----------------+
          |                 |                 |
       DATA/ML           BACKEND           FRONTEND
    Assignment 2       Assignment 3       Assignment 3
          |                 |                 |
    raw URL data        FastAPI API       React interface
          |                 |                 |
    cleaning code           +------ calls ---+
          |
    URL parser
          |
    feature extractor
          |
    classification + clustering
          |
    evaluation + saved model
```

Assignment 2 builds the **DATA/ML** section. Assignment 3 must reuse it rather than reimplementing feature extraction differently.

## 3. Planned repository structure

The project should grow toward the following structure. Folders marked `A3 later` are planned now but should not distract from Assignment 2.

```text
dtdlink/
├── README.md
├── requirements.txt or environment.yml
├── data/
│   ├── raw/                  # untouched source data; not all raw data must be submitted
│   ├── interim/              # cleaned/split intermediate data
│   └── processed/            # final feature dataset used by the model
├── notebooks/
│   ├── 01_data_audit.ipynb
│   ├── 02_cleaning.ipynb
│   ├── 03_feature_exploration.ipynb
│   ├── 04_eda.ipynb
│   ├── 05_classification.ipynb
│   └── 06_clustering.ipynb
├── src/
│   └── dtdlink_ml/
│       ├── __init__.py
│       ├── config.py
│       ├── data_loading.py
│       ├── data_cleaning.py
│       ├── url_parser.py
│       ├── feature_extraction.py
│       ├── data_splitting.py
│       ├── train_classifier.py
│       ├── cluster_urls.py
│       ├── evaluate.py
│       └── predict.py
├── tests/
│   ├── test_url_parser.py
│   ├── test_feature_extraction.py
│   ├── test_data_splitting.py
│   └── test_prediction.py
├── models/
│   ├── final_pipeline.joblib
│   └── model_metadata.json
├── reports/
│   ├── figures/
│   ├── tables/
│   └── assignment2-report.pdf
├── docs/
│   ├── feature_dictionary.md
│   ├── decisions.md
│   ├── meeting_minutes/
│   └── contribution-form.docx
├── backend/                  # A3 later: FastAPI
└── frontend/                 # A3 later: React
```

Notebooks are for exploration and explanation. Reusable logic must be moved into `src/dtdlink_ml/`. The final website must call the same `predict.py` pipeline used in Assignment 2.

## 4. How Codex must work with the student

### Student learning and implementation preference

The student does **not** want to study programming syntax in depth or type most
of the code personally. The student remains the project owner and must
understand and approve the implementation before it is written. Codex is the
implementation assistant: it proposes and explains the work, waits for explicit
acceptance, then writes, runs, tests, and explains the approved code on the
student's behalf.

Codex should therefore:

- break every Stage into small, logically ordered implementation steps instead
  of completing the full Stage silently;
- treat the student as the person performing and owning the work, while Codex
  serves as the technical hands that type and run the approved implementation;
- before each substantial step, explain its goal, reason, input, planned method,
  expected output, effectiveness, risks, affected files, and success criterion;
- after each step, show the real result, teach the important code flow and usage,
  connect the result to the project, and check conceptual understanding;
- wait for `tiếp tục` before the next substantial step, in addition to the
  explicit `OK, hãy code` acceptance required before writing or changing code;
- teach the concepts needed to understand, explain, and adjust the current stage;
- explain the purpose, input, processing flow, output, important settings, and main risks of each code component;
- give a short walkthrough of important functions and code sections so the student can read the code later;
- explain unfamiliar syntax only where it affects understanding; avoid turning the work into a full programming course;
- do not require coding exercises, syntax drills, or asking the student to type implementation code;
- write, organise, and comment the project code;
- install and configure required environments and packages when authorised;
- run notebooks, scripts, tests, training, evaluation, and debugging;
- explain what will be installed and why in plain language, then perform the installation instead of asking the student to copy commands manually;
- ask the student only for decisions that materially affect scope, labels, model behaviour, interpretation, or submission;
- keep commonly adjusted choices in clear configuration or named constants where practical, such as paths, random seed, label mapping, feature list, model parameters, and threshold;
- use readable modules, descriptive names, comments, and docstrings so the student can navigate the implementation;
- before a material change, explain what will change and its expected effect; after implementation, explain what was built, what went in, what came out, what the main code sections do, what the student can safely adjust, and whether verification passed.

The student explicitly requires an approval gate for every coding unit. Before
creating or modifying implementation code, Codex must list all affected files,
including tests, notebooks, configuration, and scripts, and explain each file's
problem, purpose, input, planned logic, expected output, design choices, and
risks. Codex must then stop and wait for an explicit acceptance such as
`OK, hãy code`; silence is not approval. The approval covers only the named
files and behavior. A material new file, behavior, or design choice requires a
new explanation and acceptance, while routine fixes within the approved scope
remain authorized. After implementation, Codex must teach from the actual
code—not only summarize the result—using the
purpose/input/main-flow/output/adjustable-parts/verification format below and
pointing to important code sections where useful. A component is complete only
when the approved code is written, verified, and explained.

Assume only basic Python knowledge. Teach in layers: first the DTDLINK concept
and a concrete URL example, then a short data-flow/pseudocode view, then the
important blocks of the actual implementation. Translate unfamiliar syntax in
plain Vietnamese only where it affects comprehension, connect code blocks to
their outputs and modelling consequences, and finish with the few safe settings
the student can adjust. Avoid exhaustive line-by-line lectures unless requested.
Never require practice code, syntax drills, memorisation, or function
reproduction; conversational checks may test project reasoning only.

The student should be able to explain:

- what problem each component solves;
- what data goes into and comes out of it;
- why the team made the main data/model decisions;
- what the model results mean and what its limitations are;
- how Assignment 2's saved model connects to Assignment 3.
- where the main settings live and what changing each setting is likely to affect.

The student is not expected to memorise syntax, reproduce functions from memory, complete coding exercises, or perform package installation manually. Brief conversational understanding checks are allowed, but they must test project reasoning rather than require code writing. Operating-system or security approval may still require the student to click **Allow**; Codex must explain such approval briefly when it occurs.

Every stage uses four modes:

| Mode | What Codex does | File changes? |
|---|---|---|
| `LEARN` | Explain the concept and method in simple Vietnamese, including enough code structure for the student to read and adjust it; no coding exercise | No |
| `PRACTISE` | Codex demonstrates a small course example when useful and walks through the result; the student observes and asks questions rather than writing code | Only when useful |
| `BUILD` | Codex implements the component, installs/configures what is needed, verifies it, and gives a short code walkthrough | Yes |
| `REVIEW` | Check evidence, explain results, compare with rubric, and identify the next gap | No unless explicitly asked to repair |

At the end of a verified `BUILD` stage, Codex must update `PROJECT_CONTEXT.md` with:

- completion date;
- files created or changed;
- verification performed;
- important results or decisions;
- the next stage.

Codex must not:

- jump directly from raw data to a final model;
- use the held-out test set to choose features, models, parameters, or thresholds;
- mark work complete without file or command evidence;
- change the phishing/offline/privacy scope without recording a decision;
- create a separate feature implementation for Assignment 3.
- turn each stage into a broad programming course or require the student to type code that Codex can safely implement.
- hide the implementation behind a result summary without showing the student the main code flow and adjustable settings.

### Required explanation after each code change

After meaningful code is created or changed, Codex must explain it using this compact format:

1. **Purpose:** why this file/component exists.
2. **Input:** what data it receives.
3. **Main flow:** the important functions or steps, without unnecessary line-by-line detail.
4. **Output:** what it produces and where the output is stored.
5. **Adjustable parts:** settings the student may change and the expected effect.
6. **Verification:** what was run and whether it passed.

When useful, Codex should point to the relevant file and line, but the student is not required to edit it personally.

## 5. Stage-by-stage learning and build sequence

### Stage 0 - Understand the map and prepare the environment

**Purpose:** Make sure the student understands the project shape and can run the learning tools.

**Course knowledge:** Week 4 setup resources; Assignment 1 provides the scope.

**LEARN:**

- what Python, Jupyter, pandas, scikit-learn, a dataset, and a model are;
- difference between a notebook, Python source file, dataset, and saved model;
- basic URL structure.

**BUILD:**

- verify Python/Jupyter;
- create the planned project structure;
- define environment dependencies;
- confirm where the base dataset is located.

**Completion gate:** Python imports work, the folder structure is understood, and the student can explain where data, code, tests, models, and reports belong.

### Stage 1 - Inspect the raw dataset and define the target

**Purpose:** Understand the available evidence before changing it.

**Course knowledge:** Week 4 lecture and seminar.

**LEARN:**

- rows, columns, features, labels, classes, data types;
- missing values, duplicates, class balance;
- binary versus multiclass classification.

**PRACTISE:** Week 4 general preprocessing notebook with its small dataset.

**BUILD:**

- extract and inspect only `malicious_phish.csv`;
- report shape, schema, label counts, missingness, duplicates, and label conflicts;
- inspect representative examples;
- choose and document the target-label strategy.

**Required decision:** Choose one of:

1. benign versus phishing;
2. benign versus potentially dangerous;
3. four-class classification.

Selected on 15 September 2026: option 2, benign versus potentially dangerous.
The exact mapping and wording are recorded in `docs/decisions.md`. The raw CSV
must remain unchanged. Because this expands the Assignment 1 scope, group
acknowledgement and a named second reader must also be recorded.

**Completion gate:** A data-audit report exists and the target-label decision is recorded in meeting minutes/decisions and `PROJECT_CONTEXT.md`.

### Stage 2 - Build reproducible cleaning

**Purpose:** Produce trustworthy input without destroying security signals.

**Course knowledge:** Week 4 cleaning, missing values, outliers, regex, privacy; Week 5 ETL.

**LEARN:**

- cleaning versus feature extraction;
- when to remove, repair, or retain abnormal records;
- why raw data must remain unchanged;
- why every row-count change needs an explanation.

**PRACTISE:** Week 4 cybersecurity preprocessing notebook, then compare with the solution.

**BUILD:**

- implement `data_cleaning.py`;
- preserve raw data;
- produce a cleaned/interim dataset;
- log counts before and after each rule;
- document exclusions and limitations.

**Completion gate:** Cleaning can run from raw input to the same cleaned output twice, with a recorded audit trail.

**Issues inherited from Stage 1:**

- keep `data/raw/malicious_phish.csv` immutable;
- create target B reproducibly and retain the original `type` for subgroup checks;
- define and record how exact duplicates and the 6 conflicting URLs are handled;
- decide whether to trim the 7 URLs with edge whitespace, with before/after counts;
- do not automatically discard Unicode, control characters, long URLs, or parse
  issues because they may contain useful security signals;
- keep the format/class association visible for later evaluation, and preserve
  the information needed for the Stage 4 domain-aware split;
- do not split data, extract model features, or train a model during Stage 2.

### Stage 3 - Build the URL parser and feature extractor

**Purpose:** Convert any raw URL into the numeric evidence used by the model.

**Course knowledge:** Week 4 regex, privacy, preprocessing, feature engineering; Week 5 transformation.

**LEARN:**

- scheme, host, registrable domain, subdomain, TLD, port, path, query, fragment;
- feature, feature vector, numeric/categorical feature;
- fit-dependent features and leakage;
- why parsing must never visit the website.

**BUILD in this order:**

1. implement and test `url_parser.py`;
2. implement simple lexical features;
3. implement Assignment 1 committed security features;
4. write `feature_dictionary.md`;
5. create at least 30 normal, malformed, encoded, Unicode, IP-host, long, and suspicious URL tests;
6. run the extractor over the cleaned dataset.

**Initial feature families:**

- lengths: full URL, host, path, query;
- counts: dots, hyphens, digits, special characters, subdomains;
- booleans: has IP host, has `@`, has suspicious terms, has unusual characters;
- domain signals: brand in the wrong component, TLD information;
- any research-backed additions that remain offline at prediction time.

Any dataset-derived lookup such as TLD frequency must be fitted on training data only.

**Completion gate:** One reusable function accepts a raw URL and returns a stable, documented feature schema; all parser/feature tests pass.

### Stage 4 - Explore features and lock the data split

**Purpose:** Understand the feature table and create a fair experiment.

**Course knowledge:** Week 5 visualisation, transformations, joins, splitting, and leakage avoidance.

**LEARN:**

- distributions, mean, median, outliers, correlation;
- train/validation/test purposes;
- data leakage and grouped/domain-aware splitting;
- scaling and why it is fitted on training data only.

**PRACTISE:** Week 5 visualisation and splitting notebooks.

**BUILD:**

- create EDA figures that answer explicit questions;
- create grouped train/validation/test splits using registrable domain where practical;
- verify no domain overlap;
- preserve test data for one final evaluation;
- document class balance in each split.

**Completion gate:** The feature table is understood, splits are reproducible, leakage checks pass, and the held-out test set is locked.

### Stage 5 - Train and select classification models

**Purpose:** Build the core URL detection capability.

**Course knowledge:** Week 6 learning/overfitting/cross-validation foundations; Week 7 classification models and metrics.

**LEARN:**

- training versus prediction;
- baseline model, overfitting, cross-validation;
- Logistic Regression, Decision Tree, KNN, and optional Random Forest;
- probability, threshold, and class weight.

**PRACTISE:** Week 7 classification portion of the workshop.

**BUILD:**

1. train Logistic Regression baseline;
2. train Decision Tree baseline as committed in Assignment 1;
3. compare on validation data;
4. add at most one justified model beyond the basic pair if time permits;
5. tune using training/validation or cross-validation only;
6. choose and document the final classifier and threshold.

**Completion gate:** At least two models have comparable validation results, the final choice is justified, and the test set is still untouched.

### Stage 6 - Perform within-class clustering

**Purpose:** Discover different patterns inside one selected class.

**Course knowledge:** Week 6 K-means, inertia, silhouette, scaling, PCA and cluster profiling; Week 7 DBSCAN and noise.

**LEARN:**

- classification versus clustering;
- why labels must not enter clustering features;
- scaling, `k`, inertia, silhouette;
- DBSCAN `eps`, `min_samples`, and noise;
- how to describe clusters using feature differences and real examples.

**PRACTISE:** Week 6 K-means notebook and Week 7 DBSCAN portion.

**BUILD:**

- choose one class and document why;
- remove the label from clustering input;
- scale appropriate features;
- use K-means as the clear baseline;
- optionally compare DBSCAN;
- profile each cluster against the overall selected-class average;
- include representative URLs and a domain interpretation.

**Completion gate:** Clustering satisfies the one-class/no-label rule and every cluster has feature-based interpretation plus real examples.

### Stage 7 - Final evaluation, error analysis, and model export

**Purpose:** Test whether the final pipeline generalises and expose its failure modes.

**Course knowledge:** Week 7 accuracy, precision, recall, F1, confusion matrix, false positives, and false negatives.

**LEARN:**

- the four confusion-matrix outcomes;
- why accuracy can mislead under imbalance;
- precision/recall trade-off;
- why false negatives matter for DTDLINK;
- probability is not automatically a calibrated trust score.

**BUILD:**

- run the selected pipeline once on the locked test set;
- report accuracy, precision, recall, F1, confusion matrix, and class-specific results;
- inspect false positives and false negatives;
- identify recurring failure patterns and limitations;
- save feature schema, preprocessing, classifier, label mapping, and threshold;
- reload the saved pipeline and test predictions on new URLs without network access.

**Completion gate:** Final results are reproducible, errors are interpreted, and one saved pipeline handles raw URL-to-prediction consistently.

### Stage 8 - Complete the Assignment 2 submission

**Purpose:** Turn verified technical work into a reproducible assessed submission.

**Course knowledge:** Weeks 4-7 provide report evidence; Week 8 is the packaging/submission transition.

**BUILD:**

- write the report alongside evidence rather than inventing results later;
- create final figures and tables from saved outputs;
- write README commands for environment setup, preprocessing, training, evaluation, and prediction;
- include only the final processed dataset, final source code, and final trained model(s);
- complete weekly minutes and signed contribution form;
- run the README from a clean environment;
- remove caches, `.DS_Store`, temporary files, unused models, and unnecessary raw data;
- compare the final package against every rubric item.

**Completion gate:** A clean reviewer can reproduce the reported results and every required deliverable/rubric item has file evidence.

### Stage 9 - Reuse the pipeline in Assignment 3

**Purpose:** Turn Assignment 2's model into the DTDLINK product promised in Assignment 1.

**Course knowledge:**

- Week 8: React foundations;
- Week 9: UI/UX, Material UI, responsive design, and routing;
- Week 10: FastAPI and API contracts;
- Week 11: React-FastAPI-model integration and visualisation;
- Week 12: unit, integration, system, usability, and acceptance testing.

**BUILD:**

- FastAPI calls the saved Assignment 2 pipeline;
- React sends non-clickable URL text to the local API;
- API returns prediction, score/probability, and signals;
- interface communicates uncertainty and never guarantees safety;
- Insights uses real Assignment 2 data/model results;
- tests trace back to Assignment 1 acceptance criteria.

**Completion gate:** React -> FastAPI -> exact saved feature pipeline/model -> safe user-facing result works end-to-end and passes tests.

## 6. Week-to-structure map

| Course week | Knowledge contribution | Project structure produced or improved |
|---|---|---|
| Weeks 1-3 | Scope, requirements, risks, usability, prototype | `PROJECT_CONTEXT.md`, `docs/decisions.md`, UI requirements |
| Week 4 | Data quality, cleaning, regex, privacy, feature engineering, baseline | `data/`, `data_loading.py`, `data_cleaning.py`, first parser/features/tests |
| Week 5 | ETL, visualisation, joins, leakage-safe splitting | processed data, EDA notebook/figures, `data_splitting.py`, feature dictionary |
| Week 6 | Model learning, overfitting, cross-validation, scaling, K-means | clustering notebook/code, cluster profiles, model-validation logic |
| Week 7 | DBSCAN, classifiers, metrics, confusion matrix, error analysis | training/evaluation code, final model selection, error tables |
| Week 8 | React introduction and Assignment 2 completion | final report, model, README, submission ZIP; frontend begins later |
| Week 9 | UX/UI, MUI, routes | `frontend/` structure and accessible pages |
| Week 10 | FastAPI | `backend/` API around the saved pipeline |
| Week 11 | Full-stack AI integration and charts | end-to-end prediction flow and real Insights visualisation |
| Week 12 | Testing | unit/integration/system/acceptance evidence |

## 7. Dependency rules

```text
Dataset audit
    -> label decision
    -> cleaning
    -> parser/features
    -> EDA and locked split
    -> classification and clustering
    -> final evaluation/export
    -> report/package
    -> Assignment 3 integration
```

Parallel work is allowed only when inputs are stable:

- report drafting and meeting minutes run throughout;
- classification and clustering can run in parallel after the feature schema and split are locked;
- UI learning can begin, but real model integration waits for the saved pipeline contract;
- innovation work begins only after all mandatory Assignment 2 requirements run successfully.

## 8. Priority order

### Priority A - Must work

1. Raw URL -> reusable features.
2. Reproducible cleaning and safe split.
3. At least two classification models.
4. Within-class clustering without labels.
5. Correct evaluation and error analysis.
6. Saved model, processed data, source, README, report, minutes, contribution form.

### Priority B - Must be trustworthy

1. Domain leakage checks.
2. Parser/feature tests.
3. Training-only fitting of preprocessing/lookups.
4. Held-out final test.
5. Clean rerun from README.

### Priority C - Higher-mark innovation after A and B

1. Relevant additional data with justified transformation.
2. Research-backed URL features.
3. One justified model beyond the taught baseline.
4. Evaluation designed to expose failure modes.

## 9. Target calendar from 14 September 2026

Current recorded deadline: **4 October 2026 at 23:59 AEST**.

| Dates | Target stages |
|---|---|
| 14-15 Sep | Stage 0 and Week 4 foundations |
| 15-17 Sep | Stage 1 dataset audit and label decision |
| 17-20 Sep | Stage 2 cleaning |
| 18-23 Sep | Stage 3 parser, features, dictionary, and tests |
| 22-25 Sep | Stage 4 EDA and locked split |
| 24-28 Sep | Stage 5 classification |
| 26-29 Sep | Stage 6 clustering |
| 29 Sep-1 Oct | Stage 7 final evaluation and export |
| 18 Sep-2 Oct | Report/README/minutes updated continuously |
| 2-3 Oct | Stage 8 clean rerun, rubric audit, final packaging |
| 4 Oct | Submission buffer; do not plan core implementation for this day |

## 10. Current status

- [x] Assignment 1 completed and summarised.
- [x] Project topic, name, intended behaviour, roles, and constraints recorded.
- [x] Assignment 2 requirements reviewed.
- [x] Master learning/build structure defined in this file.
- [x] Stage 0 environment and learning-foundation check (verified 15 Sep 2026).
- [x] Stage 1 dataset audit and target-label decision — completion gate reviewed
  and passed 17 Sep 2026; option B is recorded. Scope-change governance review
  remains a separate open follow-up.
- [x] Stage 2 cleaning pipeline — completed and verified 18 Sep 2026; 641,113
  unique cleaned URLs, deterministic outputs, raw hash unchanged, and all row
  changes recorded in `reports/cleaning/cleaning_audit.json`.
- [x] Stage 3 URL parser, feature extractor, dictionary, and tests — completed
  and verified 19 Sep 2026; 36 numeric features for 641,113 URLs, 50 robustness
  inputs, deterministic full-data output, and all 98 project tests passed.
- [x] Stage 4 EDA and locked leakage-safe split — completed and verified 24 Sep
  2026; 60/20/20 grouped partition, zero group overlap, training-only EDA and
  locked test manifest.
- [x] Stage 5 classification models and selection — Random Forest with threshold
  0.5 selected and verified 2 Oct 2026; test set remains locked.
- [x] Stage 6 within-class clustering and interpretation — verified 2 Oct 2026; train dangerous only, K-means k=7, profiles/examples and reproducible outputs.
- [x] Stage 7 final evaluation, error analysis, and export — verified 3 Oct 2026; frozen Random Forest/0.5, held-out test metrics, error analysis and offline/reload checks.
- [ ] Stage 8 final Assignment 2 package.
- [ ] Stage 9 Assignment 3 integration.

Current handoff: Stages 0-7 complete; Stage 8 is next. Stage 7 fit only the
selected Random Forest on train with the frozen Stage 5 settings, reproduced
validation, then evaluated locked test. Accuracy 0.917888, precision 0.852199,
recall 0.915521, F1 0.882726; FN 3,620 / FP 6,804. Phishing recall 0.833555
must be discussed separately. Saved pipeline/metadata and error evidence are
available; 140 tests pass, reload probabilities match within 1e-12 with exact
labels, 120 raw test URL checks and 5 offline new-URL checks pass. The initial
bitwise reload assertion was repaired by resuming verification from saved
predictions/model; no test-based retuning or refit. Notebook cells were executed
sequentially and figure inspected. See `docs/checkpoints/stage-8-ready.md`.
Test is now used for final evaluation. Stage 8 needs report/package, a clean
rerun, meeting minutes and contribution form. Scope-change acknowledgement and
a named second reader remain a governance follow-up.

## 11. Standard prompt for future Codex sessions

The complete copy-ready prompt set for every Stage is maintained in `DTDLINK_PROMPT_PLAYBOOK.md`.

```text
Read PROJECT_CONTEXT.md and ASSIGNMENT2_MASTER_PLAN.md first. Identify the current incomplete stage and the required course-week knowledge. Teach me enough to understand the method, read the main code flow, explain the result, and know what settings I can adjust, but do not require me to complete coding exercises or study syntax in depth. You are responsible for environment setup, package installation, writing and organising code, running tests, debugging, training, and verification. After each code change, explain its purpose, input, main flow, output, adjustable parts, and verification. Ask me only for material project decisions or required approvals. Complete only the current stage and update PROJECT_CONTEXT.md only when there is evidence that the stage is complete. Do not jump ahead, use the final test set early, change the DTDLINK scope silently, or duplicate feature logic.
```

For a shorter request, the student can say:

```text
Continue DTDLINK from the master plan. Teach me enough to understand the method and read the important code, without giving me coding exercises. Then implement, test, show me what I can adjust, and update progress after verification.
```
