# Week 6

## Current AI-use guidance

AI tools are permitted under the current course clarification recorded on 9 September 2026. Older contrary wording in downloaded materials is legacy content that has not yet been updated. See `../AI_USAGE_NOTE.md`.

## Topic

How models learn, with regression and K-means clustering; loss and evaluation metrics; overfitting; cross-validation; scaling; cluster selection, validation, interpretation, and cybersecurity transfer.

## What I should learn

- Distinguish supervised regression from unsupervised clustering.
- Explain linear regression training, MSE/RMSE/MAE/R-squared, gradient descent, underfitting, and overfitting.
- Know when linear, polynomial, or ridge regression is appropriate.
- Use cross-validation instead of relying on one lucky split.
- Scale data before K-means, choose and justify `k`, and use inertia and silhouette scores critically.
- Describe clusters in domain terms and connect small or distant clusters to security investigation.
- Transfer the workflow to the regression/clustering requirements of Assignment 2.

## Resources

### Week6_Lecture.pdf

- Type: PDF Lecture 1 slides (30 pages)
- Classification: MUST LEARN; ASSESSMENT RELATED
- Purpose: Builds linear regression from first principles; explains errors, loss, gradient descent, metrics, model complexity and overfitting; then works through K-means clustering, scaling, cluster selection, and interpretation. Establishes the machinery beneath Week 7 classification.
- Required or optional: Required
- Related files: `Week6_Seminar.pdf`; `COS30049_Week6_live_demo.py`; `Week6_Workshop_student_version.ipynb`
- Recommended order: 1

### Week6_Seminar.pdf

- Type: PDF Lecture 2/seminar slides (23 pages)
- Classification: MUST LEARN; ASSESSMENT RELATED
- Purpose: Type-along scikit-learn workflow on red-wine data: audit and feature engineering, linear regression, four metrics, plotting residual behaviour, cross-validation, scaled K-means, inertia/silhouette comparison, cluster profiling, and PCA visualisation.
- Required or optional: Required
- Related files: `COS30049_Week6_live_demo.py`; external wine dataset below
- Recommended order: 2

### COS30049_Week6_live_demo.py

- Type: Python live-coding example
- Classification: MUST LEARN; ASSESSMENT RELATED; EXAMPLE
- Purpose: Runnable companion to the seminar. Demonstrates duplicate checks, a derived acid-ratio feature, train/test splitting, linear-regression fitting and evaluation, cross-validation, the effect of scaling on K-means, choosing `k`, describing cluster centers in standard deviations, and PCA for visual inspection.
- Required or optional: Required example
- Related files: `Week6_Seminar.pdf`; external wine dataset below
- Recommended order: 3

### Week6_Workshop_student_version.ipynb

- Type: Jupyter workshop notebook (47 cells)
- Classification: MUST DO; ASSESSMENT RELATED
- Purpose: Student-fill exercise for linear regression on California Housing and K-means on Iris, with blanks for splitting, fitting, prediction, and clustering parameters. Includes guided cybersecurity interpretation and Assignment 2 transfer questions. No solution notebook is provided; the page directs students to discuss solutions in class.
- Required or optional: Required
- Related files: Week 6 lecture/seminar; scikit-learn's California Housing and Iris datasets
- Recommended order: 4

### Week 6 - workshop - SE & CS.pdf

- Type: PDF legacy workshop guide (14 pages; labelled 2023)
- Classification: OPTIONAL; REFERENCE
- Purpose: Older material on MySQL installation and queries, connecting MySQL to FastAPI, Axios, and CORS. It is not part of the current regression/clustering workshop, but may be useful later as background for the web-development phase.
- Required or optional: Optional/reference
- Related files: Later FastAPI and front-end/back-end integration weeks
- Recommended order: After the current Week 6 materials, only if database-backed web work is needed

### Reused links displayed on the page

- Python/VS Code and Conda setup PDFs are already stored in `Week-04/Other/`.
- The older Week 3 React/MUI PDFs are already stored in `Week-03/Workshop/`.
- Classification: OPTIONAL or REFERENCE; CROSS-WEEK

## External resources not downloaded

- Title: Plotly red wine quality dataset
- URL: https://raw.githubusercontent.com/plotly/datasets/master/winequality-red.csv
- Purpose: Runtime dataset used by the Week 6 seminar and Python demo for regression, clustering, and cross-validation.
- Week: 6
- Title: California Housing dataset
- URL: Provided at runtime by `sklearn.datasets.fetch_california_housing()`
- Purpose: Regression exercise in the student notebook.
- Week: 6
- Title: Iris dataset
- URL: Bundled through `sklearn.datasets.load_iris()`
- Purpose: K-means exercise in the student notebook.
- Week: 6

## Recommended study order

1. Read `Week6_Lecture.pdf` and be able to explain each regression and clustering decision in plain language.
2. Type through `Week6_Seminar.pdf`.
3. Run and annotate `COS30049_Week6_live_demo.py`.
4. Complete every blank and discussion prompt in `Week6_Workshop_student_version.ipynb` before seeking the in-class solution.
5. Adapt the same evaluation and cluster-interpretation workflow to the team's Assignment 2 dataset.
6. Treat the 2023 MySQL/FastAPI PDF as optional future web-development reference.

## Resource relationships

`Week6_Lecture.pdf` -> `Week6_Seminar.pdf` -> `COS30049_Week6_live_demo.py`

`Week6_Workshop_student_version.ipynb` -> California Housing regression + Iris K-means -> security-domain interpretation -> Assignment 2

## Verification

All visible Week 6 items were checked. Five new files were downloaded; the setup and Week 3 links were verified as previously stored cross-week references. No current workshop solution file is available on the page.
