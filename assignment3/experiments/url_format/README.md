# A3 URL-format investigation (separate from completed A2)

This is research/development evidence, not a new A2 evaluation or an accuracy
promise. All output is under this directory or the A3 runtime. A2 is read-only.
No submitted website is opened, DNS resolved or external analysis API queried.
The RFC reference concerns syntax documentation, not destination analysis.

## Inputs and boundaries

- Original feature table: `../../../data/processed/url_features.csv`, SHA-256
  `fe049dd9f6b2c92570354b28b2885312f64c73b03b7053be06bc35cce5a591ff`.
- Locked original manifest: `../../../data/processed/split_manifest.csv`, SHA-256
  `fbcbcf2ff68e26acfa2bb435b53c262645688a54a195ff64e283e7ff753ffc2f`.
- Frozen reference: `../../../models/final_pipeline.joblib`, SHA-256
  `d4aa8ff332ab82c36e3befce1a0e74c336b25a07a19ee9012e489c56239cb586`.
- Fitting uses **train only**. Validation selects candidates using the predeclared
  gates in `PLAN.json`, unchanged for `PLAN_TEXT.json`. Threshold stays 0.5.
- A2 test rows are filtered out before retaining features or labels for research.
  Test split-group metadata is used only for overlap checks; checksums protect
  all A2 files, including unparsed test artifacts. No A2 test metrics are computed.
- Wire-format (IDNA) domain group overlaps are checked, in addition to the original
  grouped split. Vocabulary, IDF and numeric scaling are fitted on train only.
- No hand-added demo records or domain whitelist. GitHub's domain already occurs
  naturally in A2 train, and Google's domain in validation. Demo predictions are
  therefore diagnostic examples, not independent held-out accuracy evidence.

## Reproduction

Use the installed A3 environment. From the original project root:

```sh
assignment3/backend/.venv/bin/python assignment3/experiments/url_format/diagnose.py
assignment3/backend/.venv/bin/python assignment3/experiments/url_format/prepare.py
assignment3/backend/.venv/bin/python assignment3/experiments/url_format/train_compare.py
assignment3/backend/.venv/bin/python assignment3/experiments/url_format/train_text.py
assignment3/backend/.venv/bin/python assignment3/experiments/url_format/refine_text.py
assignment3/backend/.venv/bin/python assignment3/experiments/url_format/root_audit.py
assignment3/backend/.venv/bin/python assignment3/experiments/url_format/train_root.py
assignment3/backend/.venv/bin/python assignment3/experiments/url_format/train_authority_text.py
assignment3/backend/.venv/bin/python assignment3/experiments/url_format/check_preservation.py
assignment3/backend/.venv/bin/python assignment3/experiments/url_format/summarise.py
```

A standalone A3 submission deliberately does not include training datasets.
To reproduce research, provide the unchanged A2 project inputs at the locations
above, with matching hashes. Runtime app startup does not run these scripts.
Local `cache/` and `artifacts/` are ignored/excluded from the submission ZIP;
source scripts, preregistered settings, aggregate results and selected runtime
model/metadata are retained. The scripts never rewrite A2 outputs.

## Comparison populations

1. **Raw A2 validation:** the original serialized strings and frozen features;
   checks the reference reproduces A2 validation results. Not a deployment metric.
2. **API-formatted validation:** the same eligible validation records as complete
   HTTP(S) inputs; a missing dataset scheme is completed with HTTPS. This models
   the required app-input format. It assumes source labels transfer to that
   serialization; it does not verify actual HTTP/HTTPS resources.
3. **Native explicit validation:** only already complete HTTP(S) records, without
   adding a scheme. This separate comparison makes the completion assumption
   visible rather than presenting synthetic completion as new ground truth.
4. **Format pairs:** one URL per validation domain, balanced by class (seed 42),
   then valid case/root-slash/default-port/hex-case variants. HTTP/HTTPS changes
   and dataset missing-scheme recovery are reported separately from equivalent
   format variants. Labels are inherited for analysis, not externally verified.

FPR = false positives / benign rows; dangerous recall = true positives /
dangerous rows. Counts and subtype recalls are saved. Domain-macro measures
average within-domain rates, rather than allowing large domains to dominate.
Validation has been reused for development and is not an unbiased final test.
Source labels may be stale or noisy; familiar names do not establish safety.

## Representation

`backend/src/dtdlink_a3/representation.py` supplies the exact same feature view
for fitting and inference: constant scheme for model features, lowercase host,
consistent empty root path, and omitted default port for the original protocol.
The original URL still controls display, parsing explanations and HTTP warnings.
Protocol neutrality is a deliberate modelling choice, **not** an assertion that
HTTP and HTTPS are equivalent resources or equally secure.

Preserve `www`, userinfo, custom ports (including custom HTTP port 443), path/query
case, parameter order, percent encodings, fragments and empty `?`/`#` markers.
No universal redirect resolution, Unicode/IDNA or encoded-path equivalence is
claimed. Percent-encoding-related sensitivities may remain.

The RF-only candidates keep the 36 measurements but remove format proxies. The
text candidates add train-fitted character 3–5-grams (at most 100,000) and a linear
classifier, since coarse numeric vectors can merge differently labelled URLs.
Original labels are not rewritten when feature vectors collide.

## Evidence

- `results/*scheme*.csv`: full train/validation scheme distributions by label.
- `results/baseline-application-trace.json`: model/service/API agreement for full
  inputs and 422 for missing schemes; original user examples reproduced.
- `results/baseline-format-feature-deltas.json`: coupled feature changes. One-
  feature interventions can be off-manifold and are not a causal explanation.
- `results/baseline-feature-importance.csv`: impurity importance, not causal proof.
- `results/eligibility-and-domain-audit.json`: exclusions and zero group overlap.
- `results/neutral_*.json`: all candidate results, including failed candidates.
- `results/decision*.json`: gate results; demos inspected only after selection.
- `results/post-selection-demos.json`: diagnostic outputs only if a candidate passes.
- `results/a2-protected-before.json`: A2 file preservation digest manifest.

Syntax reference: Berners-Lee, Fielding and Masinter (2005), RFC 3986, sections
6.2.2–6.2.3, https://www.rfc-editor.org/rfc/rfc3986#section-6.2.3. Case/default-port/
empty-path normalization follows those rules; scheme neutrality is our separate
modelling intervention. Reading documentation did not send any tested URL to it.

## Final decision

No candidate was promoted. The text-plus-measurements candidate passed the
initial aggregate gate but remained poor on the homepage population. The
additional population gate rejected it; root-expert and authority-text variants
also failed the joint criteria. The active A3 deployment retains the frozen A2
artifact, metadata and example. See `results/promotion-decision.json` and
`../../docs/URL_FORMAT_FINDINGS_VI.md`. The selected artifact in an intermediate
`decision-final.json` is a research-stage choice, **not** a deployment decision.

`PLAN_SOLVER.json` records a convergence check after the first balanced sparse
fit hit 300 iterations. The final recall-5 text fit had already converged at 285
iterations; a warm-start Newton-CG check required zero further iterations and
kept its validation classification counts. No unconverged model was deployed.

The final fixed-scope authority-text experiment removes constant protocol tokens
from its train/inference text view and tests no-L2 text features without numeric
length proxies; it also failed the joint aggregate/homepage criteria. All
failed candidates and optimiser checks are retained as local artifacts/evidence.
These are alternative experiments, not independent repeated validations.

## Component-role follow-up — 6 November 2026

Four additional, converged field-aware logistic models separate domain,
subdomain, path, query, userinfo, fragment and port patterns. None passed the
unchanged aggregate/homepage gates; neither the primary nor the optional preview
model was replaced. Reproduction, full comparisons, saved-artifact verification
and sparse-userinfo limitations are in [field_roles/README.md](field_roles/README.md).
