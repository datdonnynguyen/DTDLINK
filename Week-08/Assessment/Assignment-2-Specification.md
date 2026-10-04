# Assignment 2 — AI-based Project for Cybersecurity (AI4Cyber)

## Current AI-use guidance

AI tools are permitted under the current course clarification recorded on 9 September 2026. The prohibition still displayed in the older Canvas specification is legacy wording that has not yet been updated. See `../../AI_USAGE_NOTE.md`.

## Key details

- Weight: 40% (40 points)
- Team task: one student submits on behalf of the group
- Due: 4 October 2026 at 23:59 AEST (end of Week 8)
- Availability: from 31 August 2026 at 00:00
- Submission: Canvas file upload
- Late penalty: 5% of the available mark per calendar day or part thereof for up to seven days; more than seven days late receives zero and no feedback

## Purpose

Continue the Assignment 1 topic by building a reproducible cybersecurity machine-learning pipeline: raw-data collection, feature extraction, preprocessing, analysis, supervised classification, within-class unsupervised clustering, evaluation, interpretation, and reporting.

## Required deliverables

1. PDF report, up to 4,000 words excluding cover, contents, bibliography, and appendix:
   - title and group identities
   - motivation, intended users, and problem framing
   - data sources and collection
   - cleaning, transformation, joining, feature engineering, and rationale
   - analysis and visualisation
   - model choices, alternatives, and alignment with the problem
   - implementation and evaluation
   - findings, limitations, conclusion, future work, and Harvard bibliography
2. ZIP archive containing only final-project material:
   - processed dataset used by the final model in JSON/JSONL/CSV or similar format
   - README in PDF or Markdown explaining Conda environment setup, preprocessing, training, and prediction commands
   - all source code and final trained models
3. Weekly meeting minutes.
4. Signed contribution form.

## Mandatory modelling rules

- Implement at least classification and clustering.
- Classification is the core detection task.
- Perform clustering without labels and within a single class; report label composition only as a validity check.
- Describe clusters using feature differences from overall averages and real examples, not merely their majority label.
- Evaluate classification with suitable metrics such as accuracy, precision, recall, and F1; inspect false positives and false negatives.
- Implement feature extraction as reusable code from raw input rather than using an already extracted feature table.

Higher marks reward relevant additional data integrated through a justified transformation, research-backed feature extraction, justified models beyond those taught, and evaluation designed to expose failure modes. Ideas that materially change the baseline scope require tutor approval followed by written email confirmation.

The assignment page still contains a legacy prohibition on generative AI and a warning against posting reasoning or solution material publicly. Under the current clarification recorded above, the AI prohibition is outdated and AI use is permitted; the separate warning against public posting remains recorded as written.

## Course-provided base datasets

`Basic_Datasets.zip` contains four topic folders:

- AI-Generated Content Detection — `train_v2_drcat_02.csv` (`text`, `label`, prompt/source metadata)
- Phishing URL Detection — `malicious_phish.csv` (`url`, `type`)
- Prompt Injection Guardrail — `train-00000-of-00001.parquet`
- Log Anomaly Detection — `HDFS.log` plus `anomaly_label.csv` (`BlockId`, `Label`)

The 201 MB ZIP expands to more than 1.7 GB because the HDFS log is about 1.58 GB. It also contains non-learning macOS metadata files that should not be included in a final submission.

## Rubric (40 points)

- Report: data collection/processing explanation — 3
- Report: data analysis — 2
- Report: model-selection justification — 2
- Report: writing and logical structure — 1
- Report: Harvard referencing — 1
- Report: completeness — 1
- Core source-code functionality, required models, feature extraction, and clustering interpretation — 7
- Final dataset relevance, format, and organisation — 3
- Reproducible README — 1
- Code comments — 2
- Modular code structure — 2
- Innovation: additional data and transformation — 4
- Innovation: research-backed feature extraction — 4
- Innovation: models beyond the unit — 4
- Innovation: evaluation design and error analysis — 3

## External dataset sources not downloaded

- Prompt Injection Guardrail: https://huggingface.co/datasets/xTRam1/safe-guard-prompt-injection
- AI-Generated Content Detection: http://kaggle.com/datasets/thedrcat/daigt-v2-train-dataset
- Phishing URL Detection: https://www.kaggle.com/datasets/sid321axn/malicious-urls-dataset
- Log Anomaly Detection: https://zenodo.org/records/8196385

## Related resources

- `Basic_Datasets.zip` — base raw inputs and labels.
- `Group Assessment Contribution Form-1.docx` — updated contribution/signature template.
- `../../Week-04/Assessment/Meeting Minutes Example.docx` — reused weekly-minutes template.
- Weeks 4–5: data and feature pipeline; Weeks 6–7: clustering, classification, evaluation, and interpretation; Week 8 is the due week and begins the website phase.
