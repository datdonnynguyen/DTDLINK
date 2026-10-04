# Stage 8 ready checkpoint

- Date: 3 October 2026 (Australia/Melbourne).
- Stages 0–7 complete. Next: Assignment 2 report and reproducible package.
- Student authorized full Stage 7; evaluated only the frozen Random Forest on
  test after train-only refit and validation reproduction. Threshold 0.5.

## Evidence

- Code: `evaluate.py`, `predict.py`; tests: `test_evaluate.py`, `test_prediction.py`.
- Notebook: `notebooks/06_final_evaluation.ipynb`, four cells executed sequentially
  and saved using project Python; no normal-kernel claim.
- Evaluation: `reports/evaluation/`; test confusion matrix inspected.
- Export: `models/final_pipeline.joblib`, `models/model_metadata.json`.
- Test rows 126,949; accuracy 0.917888, precision 0.852199, recall 0.915521,
  F1 0.882726; TN 77,294 / FP 6,804 / FN 3,620 / TP 39,231.
- Phishing recall 0.833555 (3,122 FN), malware 0.898710 (369 FN),
  defacement 0.993692 (129 FN). Dangerous aggregate is not phishing-only recall.
- 20 source/error examples; FP/TN and FN/TP comparisons show associations only.
- 140 tests pass. Reload compares all test probabilities within 1e-12 with
  exact label equality (max difference 3.33e-16). 120 raw test URLs reproduce
  table features/predictions; 5 new URLs pass with network/DNS blocked.
- Initial bitwise reload assertion repaired through saved-result recovery;
  original test predictions/model preserved; no second fit or retuning.
- A repeat evaluation command verifies cached artifacts and performs no new fit
  or test experiment. Source/runtime/schema/model hashes checked at load.

## Boundaries and next action

Test is now used. Do not choose features, model or threshold using these results.
Probabilities are uncalibrated; do not guarantee safety. Prediction stays offline
and does not save user inputs. Package the reusable inference source and pinned
runtime with the model. Stage 8 needs report, README clean-environment check,
submission cleanup, weekly minutes and signed contribution form. Group
scope-change acknowledgement and a named second reader are still outstanding.
