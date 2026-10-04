# DTDLINK — Detect The Deception Links

DTDLINK is a privacy-first phishing URL detection project. Assignment 2 builds
the reproducible data and machine-learning pipeline; Assignment 3 will reuse
that same pipeline through a FastAPI backend and React frontend.

The prediction pipeline must analyse URL text locally. It must not open the
submitted URL, perform an online lookup during prediction, store submitted
URLs, or claim that a URL is definitively safe.

## Local environment

The project uses a local virtual environment so its packages do not modify the
macOS system Python.

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Start JupyterLab with:

```bash
jupyter lab
```

Run the Stage 0 environment check with:

```bash
python -m pytest tests/test_environment.py
```

Dataset inspection begins in Stage 1 and is intentionally not part of the
Stage 0 environment check.

## Stage 1 raw-data audit

Report: [Vietnamese audit](reports/audit/stage-1-data-audit.md).
Notebook: [01_data_audit.ipynb](notebooks/01_data_audit.ipynb).

Run with the existing project environment:

```bash
.venv/bin/python src/dtdlink_ml/data_audit.py
```

The audit reads only the course phishing CSV member, preserves source bytes,
and writes evidence to `reports/audit/`. It does not clean, relabel, split or
train. Option B is selected for Assignment 2: `benign` versus
`potentially_dangerous`; see `docs/decisions.md`. The mapping will be created by
the reproducible Stage 2 pipeline, not by editing the raw CSV.
The notebook's cells were verified by sequential execution with project Python;
a Jupyter kernel could not bind local sockets inside the execution sandbox.

## Stage 3 URL parser and feature extraction

Feature definitions: [Stage 3 feature dictionary](docs/feature_dictionary.md).

Run the offline parser/feature tests and create the processed feature table:

```bash
PYTHONPATH=src .venv/bin/python -m pytest -q
PYTHONPATH=src .venv/bin/python src/dtdlink_ml/feature_extraction.py
```

The extractor reads `data/interim/malicious_phish_cleaned.csv` and writes
`data/processed/url_features.csv` plus
`reports/features/feature_extraction_audit.json`. It streams rows to avoid
holding the full processed table in memory. Labels are copied for later
modelling but are never used to calculate URL features. Parsing uses the
bundled public-suffix snapshot and performs no online lookup.

## Stage 4 EDA and leakage-safe split

Notebook: [03_eda_and_splitting.ipynb](notebooks/03_eda_and_splitting.ipynb).

Run the complete grouped split and training-only EDA with:

```bash
PYTHONPATH=src .venv/bin/python src/dtdlink_ml/data_splitting.py
```

The pipeline validates the immutable Stage 3 feature table, groups URLs by
registrable domain, and uses a SHA-256 URL fallback for the 14 rows without a
domain. It writes `data/processed/split_manifest.csv` and audit evidence under
`reports/eda/`, `reports/splitting/`, `reports/tables/`, and
`reports/figures/`. The split is approximately 60/20/20, has zero group
overlap, and is reproducible with seed 42. Model-directed EDA reads training
rows only. The test assignment is locked by the split-manifest SHA-256 and must
not be used until the one-time Stage 7 final evaluation.

## Stage 5 classification and validation

Notebook: [04_classification.ipynb](notebooks/04_classification.ipynb).

Run the three-model comparison with:

```bash
PYTHONPATH=src .venv/bin/python src/dtdlink_ml/train_classifier.py
```

The command verifies the feature-table and split-manifest hashes, fits Logistic
Regression, Decision Tree and Random Forest on training rows, and writes
validation comparisons to `reports/classification/`. The student selected
Random Forest with alert threshold 0.5. These settings are recorded in
`src/dtdlink_ml/train_classifier.py` and
`reports/classification/validation_summary.json`. Stage 5 did not evaluate test. Stage 7 has now completed the frozen held-out
evaluation and exported the final model; see the next section.

Run all automated tests with:

```bash
PYTHONPATH=src .venv/bin/python -m pytest -q
```

## Stage 6 within-class clustering

Notebook: [05_clustering.ipynb](notebooks/05_clustering.ipynb).
Interpretation: [Vietnamese cluster report](reports/clustering/stage-6-clustering-report.md).

```bash
PYTHONPATH=src .venv/bin/python src/dtdlink_ml/cluster_urls.py
PYTHONPATH=src .venv/bin/python -m pytest -q
```

The command verifies locked input hashes, selects only true-label dangerous
TRAIN URLs, excludes metadata/labels from model inputs, removes class-constant
features and fits StandardScaler. It compares K-means k=2–8 using the same
2,000-row silhouette sample, then creates profiles, three representative URLs
per cluster, source-composition checks and PCA figures. CPU parallelism is
limited to two threads. Existing dependencies suffice; no downloads/lookups.

Outputs: five CSVs, a JSON settings/audit summary and a Vietnamese report in
`reports/clustering/`; three `clustering_*.png` images in `reports/figures/`.
The notebook reads these saved outputs by default; set `RUN_CLUSTERING=True`
to regenerate them. URL examples are escaped text, not clickable links.

Verified baseline: 127,256 rows, 34 features, k=7, sampled silhouette 0.292263.
Clustering is exploratory: a 53-row abnormal-text group, modest silhouette,
seed sensitivity and source-format effects limit interpretation. Cluster IDs
are not danger levels. See decision D-006; no validation/test modelling or
metrics, DBSCAN or classifier export occurs in this command.


## Stage 7 final evaluation and offline prediction

Notebook: [06_final_evaluation.ipynb](notebooks/06_final_evaluation.ipynb).
Results and limitations: [Vietnamese final evaluation report](reports/evaluation/stage-7-evaluation-report.md).

```bash
MPLCONFIGDIR=/private/tmp/dtdlink-stage7-mpl PYTHONPATH=src .venv/bin/python -m dtdlink_ml.evaluate
PYTHONPATH=src .venv/bin/python -m dtdlink_ml.predict 'https://example.com/'
PYTHONPATH=src .venv/bin/python -m pytest -q
```

The evaluation command first verifies input hashes and the Stage 5 selection,
refits ONLY the selected 100-tree Random Forest on train, and confirms its
validation results reproduce Stage 5 before unlocking test. It keeps threshold
0.5. No scaler, clustering step, calibration or test-informed tuning is added.
On a clean output directory it creates test predictions, class/subgroup tables,
20 error examples, a confusion-matrix figure and `models/final_pipeline.joblib`
plus `models/model_metadata.json`. Existing completed results are checked and
read back without another fit or test experiment. Partial export checks can
resume from saved predictions/model; incomplete earlier outputs stop the run.
Do not delete saved evidence to try other thresholds/models against test.

Verified test (126,949 URLs): accuracy 0.917888, precision 0.852199,
recall 0.915521, F1 0.882726; TN 77,294 / FP 6,804 / FN 3,620 / TP 39,231.
Phishing recall is 0.833555, malware 0.898710, defacement 0.993692.
The binary aggregate must not be described as phishing-only performance.

The saved pipeline combines the classifier, feature order and threshold with
the existing offline parser/extractor. Keep `src/dtdlink_ml/`, dependencies,
model and metadata together; a joblib file alone is not a standalone program.
Only load this project's trusted joblib artifact. Loading verifies artifact
hash, inference source hashes, exact recorded runtime versions and schema.
Metadata changes or source edits require a deliberate compatibility review.

Reload checks cover all test probabilities with absolute tolerance 1e-12 and
exact class equality (observed maximum difference 3.33e-16 from parallel tree
summation). 120 raw test URLs reproduce the stored features/probabilities;
5 new URLs pass while socket connections/DNS are blocked. Unit tests also
cover malformed, Unicode, IP/port and long inputs. Prediction returns parser
issues and cautious labels, does not visit URLs and does not save user inputs.
Probabilities are uncalibrated, and a negative prediction never guarantees safety.

The notebook reads saved outputs and demonstrates inference; its four code
cells were executed sequentially and saved using project Python, rather than
claiming a Jupyter kernel session. The test figure was visually inspected.
Stage 8 packaging, clean-environment reproduction, minutes/contribution form
and group scope-change acknowledgement remain outstanding.
