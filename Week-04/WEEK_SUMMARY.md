# Week 4

## Current AI-use guidance

AI tools are permitted under the current course clarification recorded on 9 September 2026. Older contrary wording in downloaded materials is legacy content that has not yet been updated. See `../AI_USAGE_NOTE.md`.

## Topic

Machine-learning project lifecycle and cybersecurity problem framing; dataset sourcing and quality; Python data preprocessing, cleaning, missing values, outliers, regular expressions, privacy, feature engineering, scaling, class imbalance, and baseline modelling.

## What I should learn

- Translate the chosen cybersecurity topic into a supervised classification problem.
- Identify and justify a credible base dataset for Assignment 2.
- Understand CSV, text, and JSON data and assess dataset authority, coverage, sample size, and quality.
- Clean invalid or missing data, manage outliers, normalise timestamps and categories, and use regular expressions.
- Engineer security-oriented features while anonymising or redacting sensitive fields.
- Prepare train/test data, scale features, handle imbalance, and build a simple baseline model.

## Resources

### Week4_Lecture.pdf

- Type: PDF Lecture 1 slides (47 pages)
- Classification: MUST LEARN; ASSESSMENT RELATED
- Purpose: Connects each cybersecurity project option to a machine-learning classification task, identifies suggested base datasets, explains why domain knowledge matters, and introduces the ML lifecycle from problem definition through data preparation and later modelling/evaluation.
- Required or optional: Required
- Related files: `Week4_Seminar.pdf`; all Week 4 notebooks; Assignment 2
- Recommended order: 1

### Week4_Seminar.pdf

- Type: PDF Lecture 2 slides (27 pages)
- Classification: MUST LEARN; ASSESSMENT RELATED
- Purpose: Covers Python for data work, open-data sources, dataset-quality review, sample size, CSV/text/JSON structures, pandas, regular expressions, cleaning and preprocessing. The slides state that this material feeds the Assignment 2 data-processing section.
- Required or optional: Required
- Related files: `week4_workshop_general.ipynb`; `Cybersecurity_Preprocessing_Workshop.ipynb`; both CSV datasets
- Recommended order: 2

### Comprehensive Guide_ Installing Python, Setting Up VS Code, and Configuring the System Environment Path.pdf

- Type: PDF setup guide (23 pages)
- Classification: REFERENCE
- Purpose: Step-by-step Python and VS Code installation, Jupyter/Python extension setup, package installation, and Windows PATH troubleshooting; macOS users can skip the PATH section.
- Required or optional: Required if the Python/Jupyter environment is not ready; otherwise reference
- Related files: All `.ipynb` files
- Recommended order: Before practical work when setup is needed

### Python Environment Setup.pdf

- Type: PDF Conda setup guide (2 pages)
- Classification: OPTIONAL; REFERENCE
- Purpose: Optional alternative for managing isolated Python environments with Anaconda/Conda, including common create/activate/deactivate/list commands.
- Required or optional: Optional
- Related files: All `.ipynb` files
- Recommended order: Before practical work only if Conda environment control is desired

### Week 4 - workshop-4.docx.pdf

- Type: PDF workshop guide (4 pages)
- Classification: MUST DO; ASSESSMENT RELATED
- Purpose: Establishes the practical sequence: configure Python/Jupyter, learn basic `pip` use, then switch to the notebooks for cleaning, missing-data handling, and security feature preparation.
- Required or optional: Required
- Related files: Setup guides; all Week 4 notebooks
- Recommended order: 3

### week4_workshop_general.ipynb

- Type: Jupyter notebook
- Classification: MUST DO
- Purpose: General preprocessing practice covering quartiles and boxplots for outlier detection, mean/median imputation using `sales_data.csv`, and Python regular-expression operations.
- Required or optional: Required practice
- Related files: `sales_data-1.csv`
- Recommended order: 4

### sales_data-1.csv

- Type: CSV dataset (12 rows; columns: Month, Sales, Profit)
- Classification: MUST DO; DATASET
- Purpose: Small dataset with deliberately missing Sales and Profit values for the imputation exercise in `week4_workshop_general.ipynb`.
- Required or optional: Required by the general notebook
- Related files: `week4_workshop_general.ipynb`
- Recommended order: Keep beside the notebook before running it; the notebook refers to it as `sales_data.csv`.

### Cybersecurity_Preprocessing_Workshop.ipynb

- Type: Jupyter exercise notebook
- Classification: MUST DO; ASSESSMENT RELATED
- Purpose: Incomplete hands-on notebook for cleaning and UTC timestamp normalisation, removing invalid rows, hashing IPs, redacting email-like content, engineering URL/port/protocol features, log-transforming byte counts, scaling, stratified splitting, handling class imbalance, and fitting logistic regression.
- Required or optional: Required practice
- Related files: `synthetic_security_logs.csv`; `Solution-Cybersecurity_Preprocessing_Workshop.ipynb`
- Recommended order: 5

### synthetic_security_logs.csv

- Type: CSV dataset (800 rows; timestamps, source/destination IPs and ports, protocol, URL, user agent, bytes, label)
- Classification: MUST DO; DATASET
- Purpose: Synthetic labelled security-log data used by the cybersecurity preprocessing exercise and its solution.
- Required or optional: Required by the cybersecurity notebooks
- Related files: `Cybersecurity_Preprocessing_Workshop.ipynb`; `Solution-Cybersecurity_Preprocessing_Workshop.ipynb`
- Recommended order: Keep beside the notebook before running it

### Solution-Cybersecurity_Preprocessing_Workshop.ipynb

- Type: Jupyter solution notebook
- Classification: REFERENCE
- Purpose: Completed version of the cybersecurity preprocessing notebook, filling the cleaning, log transform, train/test split, scaling, and modelling gaps.
- Required or optional: Reference after attempting the exercise
- Related files: `Cybersecurity_Preprocessing_Workshop.ipynb`; `synthetic_security_logs.csv`
- Recommended order: 6, after attempting the exercise notebook

### Additional_MultiTopic_Workshop.ipynb

- Type: Jupyter example notebook
- Classification: OPTIONAL; REFERENCE
- Purpose: Modular simulated-data examples for text, malware/static features, vulnerable-code snippets, and traffic/log classification, including simple logistic-regression baselines. Its listed topic names reflect an older topic set and do not exactly match the current four project options, so treat it as technique inspiration only.
- Required or optional: Optional
- Related files: `Week4_Lecture.pdf`; the team's own dataset and topic
- Recommended order: 7, selectively after the core exercises

### Cross-week links displayed on the page

- `Week 3 - workshop.pdf` and `Week 3 - workshop solutions-1.pdf` are older React/MUI resources already stored under `Week-03/Workshop/`. They are unrelated to Week 4 preprocessing and were not duplicated here.
- Classification: OPTIONAL; CROSS-WEEK REFERENCE

### Assignment 1 resources

- `Assessment/Assignment-1-Specification.md` — ASSESSMENT RELATED; local record of the visible Canvas requirements, dates, deliverables, and 15-point rubric.
- `Assessment/Meeting Minutes Example.docx` — MUST DO; weekly meeting template with decisions, outcomes, owners, and timelines.
- `Assessment/Group Assessment Contribution Form.docx` — MUST DO; group task/evidence log, agreed contribution percentages, signatures, and contribution-based grading policy.
- Relationship: Weeks 1–3 theory -> project plan/prototype -> minutes and contribution evidence -> Assignment 1 submission.

## Recommended study order

1. Read `Week4_Lecture.pdf` and frame the chosen topic as a clear classification problem.
2. Read `Week4_Seminar.pdf` and identify the dataset-quality and preprocessing requirements for Assignment 2.
3. Configure Python/Jupyter using the setup guides if needed.
4. Read the workshop guide.
5. Run `week4_workshop_general.ipynb` with `sales_data-1.csv`.
6. Attempt `Cybersecurity_Preprocessing_Workshop.ipynb` with `synthetic_security_logs.csv`.
7. Compare the attempt with `Solution-Cybersecurity_Preprocessing_Workshop.ipynb`.
8. Consult `Additional_MultiTopic_Workshop.ipynb` only for techniques suitable for the team's current topic and dataset.
9. Apply the justified preprocessing pipeline to the Assignment 2 base dataset and document every decision.

## Resource relationships

`Week 4 - workshop-4.docx.pdf` -> `week4_workshop_general.ipynb` -> `sales_data-1.csv`

`Week4_Seminar.pdf` -> `Cybersecurity_Preprocessing_Workshop.ipynb` -> `synthetic_security_logs.csv` -> `Solution-Cybersecurity_Preprocessing_Workshop.ipynb`

`Week4_Lecture.pdf` -> project-specific dataset selection -> Assignment 2 preprocessing and baseline work

## Verification

All visible Week 4 links were checked. Eleven unique Week 4 learning files were downloaded; the two visible Week 3 links were verified as already-downloaded cross-week references. The Assignment 1 page was also inspected and its two downloadable templates were stored under `Assessment/`.
