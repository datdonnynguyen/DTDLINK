# URL component-role trial — 6 November 2026

**Decision: no candidate promoted. Both existing applications retain their models.**
This follow-up tests the user's authorised proposal to separate actual domain,
subdomain, userinfo, path and query character patterns. It does not patch scores
for selected domains. `PLAN.json` was hashed before fitting (`plan-receipt.json`).

## Method and scope

Same eligible, domain-grouped population: 381,494 train / 128,373 validation.
All vocabularies, IDF weights and classifier coefficients fit train only; threshold
stays 0.5. No A2 test outcomes, injected demos, relabelling, threshold adjustment,
destination visits, DNS requests, reputation service or allowlist. The shared
`backend/src/dtdlink_a3/fields.py` supplies training and raw-URL inference features.
It is unused by both deployed applications.

Separate character TF-IDF blocks cover base domain, subdomain, path, query,
userinfo, fragment and port, plus nine bounded structural flags. Constant
protocol/prefix characters and global length counts are absent. An optional
train-learned homepage interaction adds masked domain/subdomain blocks. This
does not make HTTP/HTTPS identical resources or equally secure; raw URL warnings
remain an application responsibility.

The existing joint gates remain fixed: overall FPR ≤20%, dangerous recall ≥90%,
phishing recall ≥80%; homepage FPR ≤20%, dangerous recall ≥80%; converged fit,
zero audited domain overlap and ≥75% reduction in equivalent-format label flips
versus A2. These are development criteria, not a safety certification. The same
validation has been reused; these are not independent final-test results.

## Results

All rows below use the same API-formatted validation cohort. FPR means benign
rows incorrectly flagged / all benign rows. Recall means dangerous rows found /
all dangerous rows. Homepage = root path with no query (14,455 URLs, of which
8,497 benign and 5,958 dangerous). Full population: 85,656 benign / 42,717 dangerous.

| Model | Overall FPR | Dangerous recall | Homepage FPR | Homepage dangerous recall |
|---|---:|---:|---:|---:|
| Primary frozen A2 | 88.00% | 99.21% | 100.00% | 100.00% |
| Existing text preview | 11.36% | 92.13% | 38.13% | 90.80% |
| fields_balanced | 6.59% | 86.04% | 20.01% | 77.12% |
| fields_recall3 | 9.06% | 88.81% | 30.00% | 84.49% |
| fields_recall5 | 12.35% | 91.19% | 43.78% | 90.35% |
| fields_context5 | 10.77% | 90.41% | 33.58% | 88.44% |

All four optimisers converged. Each had zero label flips across the existing
9,277 valid-format pairs sampled from 4,000 validation domains, versus A2's 12.
The percent-hex family has only one pair; it cannot establish broad encoding
robustness. Case of path/query is deliberately preserved. Recomputed confusion
counts and stored predictions were checked after model deserialisation for
every validation row, plus fresh raw-URL inference on 1,000 seeded random rows
per model; see `results/verification.json` and its artifact hashes.

No candidate passed all gates. `fields_context5` reduces overall false positives
by 507 versus the existing preview (9,728 → 9,221), but adds 734 false negatives
(3,362 → 4,096). Its homepage FPR is still 33.58%, over the declared 20% ceiling.
`fields_balanced` reduces false positives further but misses 13.96% of dangerous
validation rows and 22.88% of dangerous homepages. Choosing it just to reduce
warnings would conceal this tradeoff.

## Diagnostic examples and limits

Demo scores were inspected only after all fits and the validation-based decision.
`fields_context5` gives Google root 60.21% and GitHub root 95.06% dangerous score;
both still cross 0.5. These are uncalibrated classifier scores. Familiar domains
are not certified benign labels, and these examples are not independent holdout
tests (GitHub occurs naturally in original train; Google in validation).

Only **two train URLs have nonempty userinfo**. At min_df=3 that block has no
vocabulary: flags can represent userinfo/brand presence, but this trial cannot
learn general userinfo text patterns. Other fitted vocabulary sizes are recorded
in `results/vocabulary-audit.json`. The original offline suffix parser retains
the entire hostname as a fallback when a suffix is unrecognised, rather than
establishing a registered-domain boundary. Empty query/fragment delimiters alone
do not create distinct field features. These are representation limitations.
No parser changes were made to A2.

This trial shows that field separation alone, under these settings and this
dataset, is insufficient. It does not prove every URL-only model must fail, or
that all source labels are incorrect. More representative, dated, independently
labelled benign/dangerous homepage and path data would support a more informative
next experiment. Further model selection needs an independent domain-disjoint
evaluation set; repeatedly tuning the same validation cannot supply that evidence.

## Reproduction

First run the parent preparation steps documented in `../README.md`; caches
and artifacts are intentionally excluded from submission ZIPs. From `assignment3/`:

```bash
backend/.venv/bin/python experiments/url_format/field_roles/train.py
backend/.venv/bin/python experiments/url_format/field_roles/verify.py
backend/.venv/bin/python experiments/url_format/check_preservation.py
cd backend
.venv/bin/python -m pytest -q
```

`train.py` writes its own `cache/`, `artifacts/` and `results/`. Aggregate evidence,
plans, scripts and contract tests ship in the main source ZIP; candidate models
and URL-level predictions remain local under this experiment. No frontend,
runtime hash, API example, security boundary or preview artifact was replaced.
