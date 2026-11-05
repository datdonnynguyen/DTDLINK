# Assignment 2 verification

Verified on 7 October 2026 on macOS arm64 with a freshly created Python 3.9.6
virtual environment. All pinned requirements were installed from package
distributions, rather than reusing the project's site-packages. `pip check`
reported no broken requirements. Conda is not installed on this machine;
`environment.yml` was parsed and checked, but a Conda installation was not run.

## Checks performed

- All 137 tests passed using a separate package copy in the fresh environment.
- Full feature extraction and grouped splitting were run from the supplied
  cleaned URL CSV. The regenerated feature table and split manifest were
  byte-identical to the submitted versions.
- All three classifiers were fitted on train and compared on validation with
  the recorded settings. Their saved metric/threshold tables matched.
- K-means k=2–8 and the seed stability checks were rerun on dangerous train
  only. Selected k=7, cluster sizes, silhouette and ARI values matched.
- The frozen final Random Forest was trained and evaluated in the reproduction
  copy. Final metrics and predictions matched the submitted results.
- Ten classifier/clustering/evaluation CSVs were compared. Numeric comparisons
  used relative tolerance 1e-12 and absolute tolerance 1e-10; fixed data
  fingerprints and identifiers required exact equality.
- All 126,949 stored test probabilities were also compared with the supplied
  loaded model, within absolute tolerance 1e-12 and with identical labels.
- 120 raw test URLs reproduced stored features/predictions with network and
  DNS access blocked. New and malformed inputs also ran offline.
- The project's original source, selected settings, saved model and processed
  datasets were not changed during packaging. Experiments ran in a separate copy.

## Recorded results

| Metric | Final test |
|---|---:|
| URLs | 126,949 |
| Accuracy | 0.9178882858470725 |
| Precision | 0.852199413489736 |
| Recall | 0.915521224708875 |
| F1 | 0.8827261886011295 |
| False positives | 6,804 |
| False negatives | 3,620 |

The source labels are not independently verified and probabilities are not
calibrated. These are dataset results, not guarantees about live websites.
The test set has already been used; future model changes need independent
evaluation. Reproduction used the fixed settings and did not select a new
model or threshold.

The large raw course archive is optional for reproducing raw auditing/cleaning
and is not in the submission ZIP. Fresh full-data reproduction here started
from the supplied prepared URL CSV, as explained in README. Real weekly
minutes and the signed contribution form are supplied separately by the team.
