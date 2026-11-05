# DTDLINK — Assignment 2

> Assignment 3 application: see [assignment3/README.md](assignment3/README.md). The instructions below remain the frozen Assignment 2 workflow.

DTDLINK analyses URL text offline and predicts benign (0) or potentially
dangerous (1). Phishing, malware and defacement form the positive class.
Prediction never visits URLs, resolves DNS or stores submitted URLs.
Probabilities are not calibrated; a negative prediction does not guarantee
safety. The website belongs to Assignment 3.

## 1. Environment setup

Extract the ZIP and open a terminal in its `dtdlink-assignment2` directory.
With Miniconda or Anaconda installed, run:

```bash
conda env create -f environment.yml
conda activate dtdlink-a2
python -m pip check
```

Equivalent explicit Conda commands:

```bash
conda create -n dtdlink-a2 python=3.9 pip -y
conda activate dtdlink-a2
python -m pip install -r requirements.txt
```

Set the module search path once in that terminal:

```bash
# macOS / Linux
export PYTHONPATH="$PWD/src"
```

```powershell
# Windows PowerShell
$env:PYTHONPATH = Join-Path (Get-Location) "src"
```

Use the activated environment's `python` for all commands below. A Python
virtual environment is an alternative:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
export PYTHONPATH="$PWD/src"
```

Windows venv activation is `.venv\Scripts\Activate.ps1`. Python 3.9 and the
pinned packages match the project runtime. The parser uses the public-suffix
snapshot bundled with tldextract, with online refresh disabled.

## 2. Package and dataset

| Location | Contents |
|---|---|
| `src/dtdlink_ml/` | Reusable processing, features, models and prediction |
| `data/interim/malicious_phish_cleaned.csv` | Prepared URLs, original labels and binary targets |
| `data/processed/url_features.csv` | Same URLs, six label/analysis columns and 36 numeric features |
| `data/processed/split_manifest.csv` | Fixed domain-group split for every URL |
| `models/` | Final pipeline and metadata |
| `reports/` | Audits, comparisons, clustering, test results and six figures |
| `notebooks/` | Stage explanations and saved displays |
| `tests/` | Automated checks |
| `docs/feature_dictionary.md` | All 36 feature definitions and limitations |
| `docs/decisions.md` | Modelling decisions |

Only the selected URL dataset is included. It comes from the course
malicious_phish.csv, linked to Kaggle's Malicious URLs dataset. No extra
source was joined. Cleaning trimmed seven URL values, quarantined twelve
conflicting rows and removed 10,066 duplicates. The final 641,113 URLs include
428,074 benign and 213,039 dangerous records.

Train has 384,832 rows, validation 129,332 and test 126,949, with no domain
shared across partitions. These partitions were used for training, selection
or final evaluation. Labels and URL/domain metadata support analysis; the
classifier takes only the 36 columns in `FEATURE_NAMES`.

## 3. Use the supplied model and run tests

```bash
python -m dtdlink_ml.predict 'https://example.com/'
python -m pytest -q
```

Prediction needs no training. Its JSON includes predicted class, cautious
label, dangerous probability, threshold and parser issues. This URL is an
input demonstration, not an expected benign result. Keep source, joblib file
and metadata together because the saved object uses `dtdlink_ml.predict`.

The current version has 137 tests. They cover unusual URLs, feature order,
label exclusion, grouped splits, preprocessing, metrics, reload and offline
prediction. Tests use small temporary fixtures and do not retrain the supplied
model. A joblib physical-CPU detection warning may appear without failing tests.

## 4. Reprocess the prepared URLs

Use a second copy of the extracted project for reproduction, so the submitted
outputs remain available for comparison. The supplied cleaned CSV still
contains raw URL strings; rebuild their features and fixed split with:

```bash
python -m dtdlink_ml.feature_extraction
python -m dtdlink_ml.data_splitting
```

The first command writes the fixed 36-feature table and audit. The second
groups by registrable domain, assigns the seeded 60/20/20 split and creates
training-only EDA. Fourteen URLs without a domain use URL-hash groups.
Expected SHA-256 fingerprints:

```text
cleaned:  b717c3c8f3c802bbf975973cecabe82a703aeca7069389aacac579ff2aebe464
features: fe049dd9f6b2c92570354b28b2885312f64c73b03b7053be06bc35cce5a591ff
manifest: fbcbcf2ff68e26acfa2bb435b53c262645688a54a195ff64e283e7ff753ffc2f
```

Training and clustering check these locked inputs and row alignment. Test has
already been evaluated; keep the recorded settings for reproduction and use
independent data for future tuning.

### Optional raw audit and cleaning

The course archive is excluded because it contains three unrelated datasets.
To reproduce raw cleaning, obtain Basic_Datasets.zip from Canvas and put it
at `Week-08/Assessment/Basic_Datasets.zip` in the reproduction copy:

```bash
python -m dtdlink_ml.data_audit
python -m dtdlink_ml.data_cleaning
```

Audit extracts only the URL CSV into `data/raw/`. Cleaning trims whitespace,
quarantines all conflicting-label URLs, keeps the first exact duplicate and
adds the binary target. It writes the cleaned CSV and row-change evidence.
Then follow Sections 4–6. The raw CSV hash must be
`d83ce942075dd63ed4d11560cfdcd9d512caa3d680e292f22cab484e8f074d01`.
The supplied prepared data and model work without this optional archive.

## 5. Train classifiers and reproduce clustering

```bash
python -m dtdlink_ml.train_classifier
python -m dtdlink_ml.cluster_urls
```

Classification fits Logistic Regression, Decision Tree and Random Forest on
train and compares them on validation. Only Logistic Regression uses a
train-fitted StandardScaler. Random Forest uses 100 trees, depth 12, minimum
leaf size 100, square-root feature sampling, balanced subsample weights,
seed 42 and two workers. It was selected at threshold 0.5 for validation F1
0.888186. Results are saved under `reports/classification/`.

Clustering selects the 127,256 true-label dangerous TRAIN rows. Labels and
metadata are excluded from inputs. Two constant features are removed and
34 features are scaled on this population. K-means compares k=2–8 with ten
initialisations, seed 42 and a fixed 2,000-row silhouette sample. Selected
k=7 has sampled silhouette 0.292263. Cluster means, representative URLs,
original-label composition and two figures are saved under
`reports/clustering/` and `reports/figures/`. Cluster IDs are not danger levels.

## 6. Final evaluation and frozen reproduction

```bash
python -m dtdlink_ml.evaluate
```

In the supplied ZIP this reads the saved test_metrics.json without fitting.
Test accuracy is 0.917888, precision 0.852199, recall 0.915521 and F1 0.882726;
FP=6,804 and FN=3,620. Phishing recall is 0.833555, distinct from the combined
positive-class recall.

To reproduce the final fit in a separate project copy, rename the saved metrics:

```bash
python -c "from pathlib import Path; p=Path('reports/evaluation/test_metrics.json'); p.rename(p.with_name('test_metrics.original.json'))"
python -m dtdlink_ml.evaluate
```

Without the saved metrics, evaluation checks the selected model and threshold,
fits the fixed Random Forest on train only, evaluates locked test, exports the
model and checks reload probabilities. It overwrites the reproduction copy's
model and evaluation files. This repeats fixed settings; do not use it to tune
against the already-used test set.

## 7. Notebooks and verification

```bash
jupyter lab
```

Notebook 01 requires the optional course ZIP for its raw audit; notebook 02
requires the extracted raw CSV for cleaning. Other notebooks use the prepared
data or saved outputs. Some cells regenerate results, so Run All in a copy.
Notebook 05 reads saved outputs unless RUN_CLUSTERING=True.

Source-format bias, unverified labels, phishing misses, no temporal/external
holdout and uncalibrated probabilities limit the results. The ML core is ready
for later FastAPI/React integration; the website is not an Assignment 2 output.

See `VERIFICATION.md` for the actual environment/package checks. Submit the
PDF report, weekly meeting minutes and signed contribution form separately
alongside this ZIP.
