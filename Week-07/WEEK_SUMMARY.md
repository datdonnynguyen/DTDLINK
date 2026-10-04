# Week 7

## Current AI-use guidance

AI tools are permitted under the current course clarification recorded on 9 September 2026. Older contrary wording in downloaded materials is legacy content that has not yet been updated. See `../AI_USAGE_NOTE.md`.

## Topic

Density-based clustering and supervised classification: DBSCAN, logistic regression, K-nearest neighbours, classification metrics, and optional decision-tree and random-forest extensions.

## What I should learn

- Distinguish clustering from classification and compare DBSCAN with K-means.
- Explain DBSCAN's `eps`, `min_samples`, core/border/noise points, strengths, and limitations.
- Standardise features before distance-based learning and select parameters with evidence.
- Train logistic-regression and KNN classifiers without leaking test information.
- Evaluate classification with accuracy, precision, recall, F1-score, confusion matrices, and classification reports.
- Interpret outliers and classification decisions in the team's cybersecurity project context.
- Recognise decision trees and random forests as optional alternative classifiers.

## Resources

### week7_lec.pdf

- Type: PDF lecture slides (42 pages; Canvas displayed the link label `week7_lec-preview.pptx`, but the supplied download is a PDF)
- Classification: MUST LEARN; ASSESSMENT RELATED
- Purpose: Introduces DBSCAN and its parameters, cluster/noise interpretation and validation, then develops the classification workflow and core models used in the workshop.
- Required or optional: Required
- Related files: `Week7_Seminar-1.pdf`; `Workshop_week7_stu.ipynb`
- Recommended order: 1

### Week7_Seminar-1.pdf

- Type: PDF seminar/type-along slides (37 pages)
- Classification: MUST LEARN; MUST DO; ASSESSMENT RELATED
- Purpose: Demonstrates DBSCAN with scaling, parameter selection and silhouette evaluation; then implements leakage-safe logistic regression and KNN classification and evaluates their predictions.
- Required or optional: Required
- Related files: `week7_lec.pdf`; `Workshop_week7_stu.ipynb`; scikit-learn datasets below
- Recommended order: 2

### Workshop_week7_stu.ipynb

- Type: Jupyter workshop notebook (33 cells)
- Classification: MUST DO; ASSESSMENT RELATED
- Purpose: Runnable practice on DBSCAN using synthetic moon-shaped data and logistic-regression/KNN classification using the Breast Cancer dataset. Includes project-transfer questions about features, security outliers, benign-versus-malicious classification, and optional decision-tree/random-forest examples.
- Required or optional: Required; the advanced tree models are optional
- Related files: Both Week 7 PDFs; scikit-learn `make_moons` and Breast Cancer datasets
- Recommended order: 3

### Workshop_week7_Solution.ipynb

- Type: Mentioned Jupyter solution notebook
- Classification: REFERENCE
- Purpose: Intended solution companion for the student workshop notebook.
- Required or optional: Reference
- Related files: `Workshop_week7_stu.ipynb`
- Recommended order: After attempting the student notebook
- Availability: The filename is visible on the Week 7 page, but no link or download control is provided. It could not be accessed or downloaded.

### Reused links displayed on the page

- Python/VS Code and Conda setup PDFs are already stored in `Week-04/Other/`.
- The older Week 3 React/MUI PDFs are already stored in `Week-03/Workshop/`.
- The older MySQL/FastAPI workshop PDF is already stored in `Week-06/Workshop/`.
- Classification: OPTIONAL or REFERENCE; CROSS-WEEK

## External resources not downloaded

- Title: Synthetic `make_moons` dataset
- URL: Generated locally by `sklearn.datasets.make_moons()`
- Purpose: Non-linearly separable sample data used to demonstrate DBSCAN clusters and noise.
- Week: 7
- Title: Breast Cancer Wisconsin diagnostic dataset
- URL: Bundled through `sklearn.datasets.load_breast_cancer()`
- Purpose: Binary-classification data used for logistic regression, KNN, and optional tree-based models.
- Week: 7

## Recommended study order

1. Read `week7_lec.pdf`, focusing on the modelling workflow and why DBSCAN differs from K-means.
2. Work through `Week7_Seminar-1.pdf` and reproduce its scaling, fitting, prediction, and evaluation steps.
3. Run `Workshop_week7_stu.ipynb` from top to bottom and answer the cybersecurity/project-transfer questions.
4. Compare logistic regression and KNN using all reported metrics, not accuracy alone.
5. Experiment with DBSCAN parameters and KNN's neighbour count, recording how results change.
6. Explore the decision-tree and random-forest section only after the required models are understood.

## Resource relationships

`week7_lec.pdf` -> `Week7_Seminar-1.pdf` -> `Workshop_week7_stu.ipynb`

`Workshop_week7_stu.ipynb` -> generated `make_moons` data -> DBSCAN -> silhouette/noise analysis

`Workshop_week7_stu.ipynb` -> built-in Breast Cancer data -> scaling -> logistic regression/KNN -> precision/recall/F1/confusion matrix

## Verification

Every visible Week 7 item was checked. Three current files were downloaded. The page mentions `Workshop_week7_Solution.ipynb`, but it is plain text without a link or download control, so it is recorded as inaccessible. Reused setup and legacy web-development resources were verified as already stored in earlier week folders.
