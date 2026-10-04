# Week 5

## Current AI-use guidance

AI tools are permitted under the current course clarification recorded on 9 September 2026. Older contrary wording in downloaded materials is legacy content that has not yet been updated. See `../AI_USAGE_NOTE.md`.

## Topic

Deeper machine-learning data preprocessing and transformation with Python, plus exploratory visualisation and reproducible train/validation/test splitting.

## What I should learn

- Use the ETL model to explain a preprocessing pipeline.
- Manipulate, reshape, join, concatenate, clean, and engineer features with pandas.
- Normalise or standardise numeric features and avoid data leakage.
- Create plots that reveal class imbalance, distributions, class separability, feature correlation, spikes, and trends.
- Split data reproducibly into training, validation, and test sets.
- Connect preprocessing and visual evidence directly to Assignment 2 requirements and rubric criteria.

## Resources

### Week5_Lecture.pdf

- Type: PDF Lecture 1 slides (30 pages)
- Classification: MUST LEARN; ASSESSMENT RELATED
- Purpose: Extends Week 4 into ETL, dataset sources and licences, sorting/filtering, feature creation, distribution transforms, pivot/melt, joins, concatenation, data analysis, and visualisation. It explicitly links transformations, feature creation, and charts to Assignment 2.
- Required or optional: Required
- Related files: `Week5_Seminar.pdf`; transformation guide; demo script; both notebooks
- Recommended order: 1

### Week5_Seminar.pdf

- Type: PDF Lecture 2 slides (28 pages)
- Classification: MUST LEARN; ASSESSMENT RELATED
- Purpose: Practical introduction to pandas, scikit-learn, Matplotlib, and Seaborn, including DataFrames, reading/writing data, cleaning, train/test splitting, and common chart types. These named libraries are expected in Assignment 2.
- Required or optional: Required
- Related files: Both notebooks; `cicids_synthetic_dataset.csv`
- Recommended order: 2

### COS30049_Week5_guide.html

- Type: Offline HTML reference guide
- Classification: MUST LEARN; ASSESSMENT RELATED; REFERENCE
- Purpose: Detailed pandas guide covering inspection, selection, cleaning, vectorised string/regex work, feature creation, groupby/aggregation, pivot/melt, merge, concat, index handling, leakage-safe splitting/evaluation, and clustering. It explains Assignment 2 innovation criteria around joining an additional source and reconciling mismatched schemas.
- Required or optional: Required reference
- Related files: `COS30049_Week5_demo_data_processing.py`; `Week5_Lecture.pdf`
- Recommended order: 3

### COS30049_Week5_demo_data_processing.py

- Type: Python live-coding example
- Classification: MUST LEARN; ASSESSMENT RELATED; EXAMPLE
- Purpose: End-to-end transformation walkthrough on an SMS spam dataset: sorting, aggregation, pivot/melt, extracting a join key, leakage-safe lookup-table creation, left joins, unmatched-row treatment, demonstrating target leakage, schema-aligned concatenation, and extra-source integration.
- Required or optional: Required example
- Related files: `COS30049_Week5_guide.html`; external SMS dataset below
- Recommended order: 4

### week5_workshop-1.ipynb

- Type: Jupyter workshop notebook
- Classification: MUST DO
- Purpose: Uses the California Housing dataset to practise scatter plots, correlation heatmaps, and a reproducible 60/20/20 training/validation/test split.
- Required or optional: Required practice
- Related files: `Week5_Seminar.pdf`
- Recommended order: 5

### Data_visualization-1.ipynb

- Type: Jupyter workshop notebook
- Classification: MUST DO; ASSESSMENT RELATED
- Purpose: Security-data visualisation workflow: audit/clean the provided CSV; chart class balance; inspect distributions and class-wise boxplots; make feature scatterplots and correlation heatmaps; and plot per-minute totals, class-specific traffic, and rolling averages.
- Required or optional: Required practice
- Related files: `cicids_synthetic_dataset.csv`
- Recommended order: 6

### cicids_synthetic_dataset.csv

- Type: CSV dataset (10,000 rows; timestamp, five traffic measures, protocol, and label)
- Classification: MUST DO; DATASET
- Purpose: Synthetic CICIDS-style labelled network-flow data used by `Data_visualization-1.ipynb` for security-oriented exploratory analysis.
- Required or optional: Required by the visualisation notebook
- Related files: `Data_visualization-1.ipynb`
- Recommended order: Keep beside the notebook and update its `DATA_PATH` before running

### Reused links displayed on the page

- The Python/VS Code guide and `Python Environment Setup.pdf` are already stored in `Week-04/Other/` and remain setup references.
- `Additional_MultiTopic_Workshop.ipynb` is already stored in `Week-04/Examples/` and remains optional inspiration.
- The two older Week 3 React/MUI PDFs are already stored in `Week-03/Workshop/` and are unrelated to the Week 5 preprocessing sequence.
- Classification: OPTIONAL or REFERENCE; CROSS-WEEK

## External resource not downloaded

- Title: SMS Spam Collection mirror used by the Week 5 demo
- URL: https://raw.githubusercontent.com/justmarkham/pycon-2016-tutorial/master/data/sms.tsv
- Purpose: Runtime dataset loaded by `COS30049_Week5_demo_data_processing.py` for transformation, join, leakage, and concatenation examples.
- Week: 5

## Recommended study order

1. Read `Week5_Lecture.pdf` for the conceptual transformation and visualisation map.
2. Read `Week5_Seminar.pdf` for the Python libraries and splitting workflow.
3. Work through the offline HTML guide as a reference.
4. Read and run `COS30049_Week5_demo_data_processing.py`, paying special attention to leakage-safe joins and schema reconciliation.
5. Complete `week5_workshop-1.ipynb`.
6. Set `DATA_PATH` in `Data_visualization-1.ipynb` to `cicids_synthetic_dataset.csv` and complete the security visualisations.
7. Reuse the resulting preprocessing rationale and charts in Assignment 2 where they genuinely support the chosen dataset.

## Resource relationships

`Week5_Lecture.pdf` + `Week5_Seminar.pdf` -> `COS30049_Week5_guide.html` -> `COS30049_Week5_demo_data_processing.py`

`Data_visualization-1.ipynb` -> `cicids_synthetic_dataset.csv`

`week5_workshop-1.ipynb` -> California Housing dataset fetched by scikit-learn at runtime

## Verification

Every visible Week 5 item was checked. Seven new Week 5 files were downloaded; five reused links were verified against files already stored in Weeks 3-4. No additional visible Week 5 learning-resource links were present.
