# DTDLINK — experimental A3 preview

**Review-only version. The primary A3 app and completed A2 remain unchanged.**
This preview uses the separately trained A3 character TF-IDF + numeric-feature
logistic classifier, not the primary A2 Random Forest. It is not the main
submission package and is not claimed to have fixed the homepage issue.

## Compare the versions

| Version | Frontend | API/docs | Model |
|---|---|---|---|
| Primary | http://127.0.0.1:5173/ | http://127.0.0.1:8000/docs | Frozen A2 RF |
| Experimental | http://127.0.0.1:5174/ | http://127.0.0.1:8001/docs | A3 text + 36 measurements |

The preview is labelled **EXPERIMENTAL A3** in the sidebar and **Preview** in the
header/title. Its backend has a distinct hash, metadata, response example and
model-version identifier. It keeps the same dark UI, URL evidence, session
charts, input validation, escaped text, bounded inference, exact CORS and headers.
No destination is opened, DNS resolved or external analysis service called.

## What this model improves, and what remains

On the same eligible API-formatted validation cohort (128,373 URLs), FPR changed
from 88.00% to 11.36%; dangerous recall from 99.21% to 92.13%. These are reused
validation measurements, not an unbiased final test or live safety probability.
Benign-homepage FPR remains 38.13%, which failed the stricter homepage criterion.
This is why this is a separate preview rather than a primary-model replacement.

Known diagnostics reproduced without overrides:

| Input | Primary score | Preview score |
|---|---:|---:|
| https://www.google.com/ | 97.22% | 99.71% |
| https://github.com/ | 95.43% | 98.71% |

These examples still score high. Familiar domain names are not ground truth of
current website safety; no whitelist or label manipulation is used. GitHub's
domain naturally occurred in A2 train and Google's in validation, so these are
not independent held-out demonstrations. A2 test outcomes were not used.

The candidate is `neutral_text_recall5_converged`: train-only vocabulary, IDF,
scaler and classifier, shared train/inference URL representation and threshold
0.5. No demo records were injected. Source research and full metrics remain in
the parent project's `experiments/url_format/`; relevant evidence is copied to
`docs/` in this independent preview package.

## Run in this existing workspace

From the original project root:

```sh
assignment3/backend/.venv/bin/python assignment3/experimental-app/scripts/run.py
```

Local dependency links reuse the already installed Python/npm dependencies.
Model and source are independent copies. These links are excluded from the ZIP.
Press Ctrl+C in the launcher terminal to stop its two children. The primary app
has separate ports/processes and is not stopped by this launcher.

## Run a fresh extracted preview ZIP

Python 3.12 and Node.js >=22.12 are required. From the extracted preview folder:

```sh
python3.12 -m venv backend/.venv
backend/.venv/bin/python -m pip install -r backend/requirements.txt
cd frontend
npm ci
npm run build
cd ..
backend/.venv/bin/python scripts/run.py
```

For PowerShell use `py -3.12`, `backend\.venv\Scripts\python.exe` and
`Set-Location` equivalents. Windows execution is not claimed verified.
The default ports are 5174/8001. Change all of launcher, frontend API base/CSP,
backend exact origin and package scripts together if ports are changed.

## Model integrity and interpretation

SHA-256: `f5a7b6fb18fa3c041ccac167436ddc9d3ea44f496842314c59070a7e36303290`.
Startup checks this code-pinned hash before joblib deserialization, then validates
the A3 text-pipeline metadata/feature contract. There are 100,000 character-pattern
features plus 36 numeric measurements. Observed URL rules use the raw input;
they are not causal explanations of the trained classifier. Confidence remains
uncalibrated. Class 1 still combines phishing, malware and defacement.

The model view uses a common scheme, host case/root/default-port representation
in both training and inference. `www`, userinfo, custom ports, path/query case,
encoding and fragments remain. Public API input still requires HTTP(S); the raw
URL is preserved for display, and HTTP warnings remain based on the actual input.

## Checks and AI assistance

`evidence/verification.json` records executed checks and limits. No fresh install,
new ZAP scan or new independent accuracy evaluation is claimed for this preview.
Research metrics copied in docs are measurements from the prior local study.
Codex assisted with the experimental training, integration, app copy, tests and
this documentation. The team remains responsible for reviewing and explaining
its work. This preview is optional research, not a replacement submission.
