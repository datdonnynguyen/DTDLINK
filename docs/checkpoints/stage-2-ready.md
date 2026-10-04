# Stage 2 ready checkpoint

- Date: 17 September 2026 (Australia/Melbourne)
- Previous stages: Stage 0 complete; Stage 1 complete
- Current task: Stage 2 — reproducible cleaning
- Stage 2 status: ready to begin; no cleaning code or cleaned dataset yet

## Evidence that closed Stage 1

- Audit report: `reports/audit/stage-1-data-audit.md`
- Machine-readable evidence: `reports/audit/summary.json` and the accompanying
  JSONL files
- Reproducible audit code: `src/dtdlink_ml/data_audit.py`
- Executed companion notebook: `notebooks/01_data_audit.ipynb`
- Target decision: `docs/decisions.md`, decision D-001
- Completion review: the required report sections, all four label mappings,
  independent counts, and the unchanged raw CSV hash were verified on
  17 September 2026

Key evidence: 651,191 rows and 2 string columns; benign 428,103, defacement
96,457, malware 32,520, phishing 94,111; 10,066 exact-row duplicate excess;
10,072 URL duplicate excess; 6 conflicting URLs affecting 12 rows; no null,
empty, whitespace-only, or checked missing-like cells.

## Locked target decision for the Stage 2 plan

Use binary target B and retain the original `type` column:

| Raw `type` | `target` | Meaning |
|---|---:|---|
| `benign` | 0 | benign |
| `phishing` | 1 | potentially_dangerous |
| `malware` | 1 | potentially_dangerous |
| `defacement` | 1 | potentially_dangerous |

The raw counts before cleaning are 428,103 versus 223,088. This mapping must be
created by the reproducible cleaning pipeline and must never be written into the
raw CSV. Product and report wording must remain cautious: `Potentially
dangerous`, `Uncertain`, and `No strong danger signal detected`.

The choice broadens the submitted Assignment 1 phishing-only scope. Group
acknowledgement and a named second reader remain a separate governance follow-up.

## Issues Stage 2 must address

1. Keep `data/raw/malicious_phish.csv` byte-for-byte unchanged.
2. Apply target B reproducibly while retaining raw `type` for later subgroup
   evaluation.
3. Define a documented exact-duplicate rule. Duplicates are concentrated in
   malware, so the class distribution will change after deduplication.
4. Define a documented rule for the 6 URLs with benign/phishing conflicts. Do
   not choose the first label or relabel them without evidence.
5. Decide whether to trim the 7 URLs with leading/trailing whitespace and record
   its effect. The Stage 1 audit found that trimming creates no new duplicate
   groups.
6. Do not automatically delete URLs with Unicode, control characters, extreme
   length, or diagnostic parse problems. They may be security-relevant; any
   removal or repair requires an explicit reason and count.
7. Record the number of rows before and after every cleaning rule and make the
   run deterministic.
8. Carry the format/class association forward as a modelling risk. Cleaning
   alone cannot prove or remove source bias.
9. Preserve the information needed for the domain-aware split in Stage 4. Do
   not perform splitting, feature extraction, or training in Stage 2.

## Instructions for the next task

1. Read `PROJECT_CONTEXT.md`, `ASSIGNMENT2_MASTER_PLAN.md`,
   `docs/decisions.md`, and `reports/audit/stage-1-data-audit.md`.
2. Do not repeat Stage 0 or Stage 1.
3. First teach, in plain Vietnamese, the difference between cleaning and feature
   extraction; remove, repair, and retain; raw-data immutability; and the need
   for a row-count audit trail.
4. Then propose one small Stage 2 step. Name every implementation file that
   would be created or changed and explain its purpose, input, planned flow,
   output, adjustable decisions, and risks.
5. Do not create or edit implementation code until the student explicitly says
   the plan is accepted, for example `OK, hãy code`.
6. After an approved step, explain the actual code and real output, check the
   student's conceptual understanding, and wait for `tiếp tục` before the next
   substantial step.

## Stage 2 completion gate

Stage 2 is complete only when the pipeline produces the same cleaned output on
two runs, every row-count change has a recorded reason, the raw hash remains
unchanged, and the implemented code and results have been explained to the
student.
