# Assignment 3 requirements and current status

## Source and reading order

The student supplied the complete Canvas brief and rubric on 5 November 2026.
The full pasted text is preserved byte-for-byte in
`Assignment-3-Specification.md`. This summary is a navigation aid; consult the
full specification for exact requirements. The previous syllabus-only note is
superseded. No live Canvas verification was performed.

For future Assignment 3 work, read these in order:

1. `../../PROJECT_CONTEXT.md` for the product, prior evidence and current progress.
2. `Assignment-3-Specification.md` for the supplied assignment rules and rubric.
3. This file for the checklist and unresolved interpretation issues.
4. The Stage 9 bridge in `../../ASSIGNMENT2_MASTER_PLAN.md` and the relevant
   Weeks 8–12 materials. The old bridge is not a complete A3 implementation plan.

## Assessment and deadline

- Title: Full-Stack Web Development for a Secure AI Application.
- Weight and rubric total: 45% / 45 points. Group assignment.
- Due: Sunday 8 November 2026 at 23:59, as stated in the supplied brief.
  The new text does not specify a timezone; use the actual Canvas timezone
  rather than importing AEST from the old syllabus note.
- Model accuracy is not marked. An existing Assignment 2 model or another
  topic-appropriate model may be used. Application integration, usability,
  error handling, security and explanation are assessed.
- One member submits all files through Canvas, each named with the group name.
- 9–11 November: late, no deduction. 12/13/14/15 November: respectively
  5/10/15/20% deduction of available marks. More than seven calendar days late
  is not accepted. Video changes after the due date also count as late;
  the brief forbids all video changes after 15 November 2026 at 23:59.
- The earlier syllabus records the course hurdle as at least 40% in each
  assignment and at least 50% overall; this is background from that syllabus,
  not a requirement newly stated in the supplied A3 text.

## Four submission items

1. One source ZIP: separate React frontend and FastAPI backend folders,
   README in Markdown or PDF, and the model in the backend folder (or a
   download script if too large). Exclude `node_modules`.
2. Video: MP4 or AVI, at most 15 minutes. If over the Canvas file-size limit,
   an unlisted YouTube URL may instead be submitted in
   `group-name-video-link.txt`; keep it accessible until marking completes.
3. Meeting minutes PDF: at least one meeting each week since team formation.
4. Contribution form PDF: completed group form.

There is **no separate written report**. README and generated API documentation
belong with the application; they are not additional independent upload items.

## Required application baseline

### React frontend

- Validate input before sending it; put useful messages beside the field.
- Show the real model result and confidence prominently.
- Loading, success and error states; a not-found page and an unexpected-error
  fallback so failures never leave a blank screen.
- At least two visualisations answering different questions about results,
  with clear titles, labels, legends and tooltips at minimum. For a single-input
  app, current-result and session-comparison views are suggested options.
  Useful filtering, selection or zooming can earn more than tooltips alone.
  More charts alone do not earn more marks.
- Consistent visual design, desktop and phone layouts, labelled inputs,
  readable contrast and keyboard access to every function.

### FastAPI backend

- Constrained Pydantic request and response models.
- At least two HTTP methods, each serving a genuine purpose.
- Correct HTTP status codes and one consistent JSON error format for all
  errors, including unexpected model failures; no stack traces/internal details.
- Load the model once at startup. Apply the same preprocessing as training.
- `/docs`: a description and example request/response for every endpoint.
- Pinned dependencies; README alone starts both applications on a clean machine.

### Security hygiene and threat model

- Never render untrusted input as HTML; do not bypass React escaping.
- Enforce sensible input and, if applicable, upload size limits on the backend.
- CORS permits only the application's own exact frontend origin(s).
- No passwords, keys or other secrets in source code or repository history.
- README threat model (about half a page): attacker, goals and capabilities;
  identify applicable risks and briefly explain why other listed risks do not
  apply. Frontend validation is usability; backend validation is security.
- Test attacks only against the team's own application on its own machine.

## Innovation and advanced security

Section 2.7: name at most two selected defences in README. They must address
risks actually exposed by the design. Demonstrate the attacks and defences
in the video, preferably attacks succeeding without the defence and failing
with it; cover obvious variations and explain the defence's cost.

- Basic: model hash validation before unsafe joblib/pickle loading; command
  injection where system commands are used; rate limiting.
- Intermediate: SQL injection where a database exists; secure uploads where
  files are accepted; misconfiguration and vulnerable dependencies, with
  `pip-audit`, `npm audit`, OWASP ZAP and fixes or explanations of findings.
- Advanced: application-level denial of service, SSRF where outbound requests
  exist, broken access control where accounts exist.
- A DoS demonstration must show an expensive request does not block unrelated
  requests and excess concurrent work receives 503 instead of freezing.
- If rate limiting and DoS are both selected, use different mechanisms.
- DTDLINK planning inference: avoid adding accounts, a database or outbound
  requests merely to claim a risk the existing offline design does not expose.
  This follows the brief's applicability rule, not a new explicit course rule.

Section 2.8: choose and name at most one advanced attack/defence study, from
side channels, membership inference, model extraction or detection evasion.
Implement and measure the attack before and after the defence, repeat enough
to support the conclusion, interpret honestly and explain costs. This only
counts after the baseline security hygiene requirements are met. Examples
in the brief are teaching examples, not measurements of DTDLINK.

## README and video evidence

README must cover setup/run commands, an architecture diagram, pinned
versions, threat model, Harvard references, generative AI usage, the up-to-two
selected defences and the one advanced study if attempted.

The video must include intended users/problem; live input-to-result workflow;
invalid input, error pages and phone layout; one real request followed through
actual React code, FastAPI, `/docs`, model and response; key implementation
and design choices in the team's own words; threat model and demonstrated
security; limitations and next steps. Anything to be marked must appear in
the video. Not every team member has to present. Check video playback/access.

## Rubric totals

| Area | Points |
|---|---:|
| Video: connections, implementation/design, security, clarity | 10 |
| Frontend: states, visualisations, design/responsiveness/accessibility | 10 |
| Backend: API/docs, errors, model integration | 7 |
| Source: README execution, code quality and README content | 4 |
| Security hygiene and threat model | 3 |
| Innovation: section 2.7 defences | 7 |
| Innovation: section 2.8 advanced security | 4 |
| Total | 45 |

## Specific issues to resolve in planning

1. The brief's phishing topic minimum says phishing/legitimate with confidence.
   The existing A2 model instead distinguishes benign from a combined
   phishing/malware/defacement class. Do not relabel that probability as phishing
   confidence or assume it diagnoses an attack subtype. Resolve this mismatch
   explicitly before fixing the UI/API contract. No model change is authorised
   merely by saving the brief.
2. Section 2.7 prose says the two defences are capped at 8 points, but the
   attached rubric allocates 7 points to that section and sums to 45 overall.
   Preserve both statements and flag the discrepancy; do not invent a revised
   scoring scheme or promise a grade.
3. The A3-specific AI wording below differs from the September course-wide
   guidance. Use the newly supplied assignment-specific wording as the current
   planning reference unless newer written course clarification supersedes it.

## Assignment-specific generative AI wording

The supplied A3 brief says AI may be used for learning, ideas and debugging,
but not to generate assignment content. Students must understand, write and
explain the application's core logic, avoid copying functions/components
without understanding, and disclose all AI use in README. This records an
assessment requirement from the source, not a new user instruction to create
or restrict files. See `../../AI_USAGE_NOTE.md` for the supersession record.

## Related teaching weeks

- Week 8: web architecture, Node.js, React, JSX and state.
- Week 9: UX/UI, responsive Material UI and React Router.
- Week 10: HTTP, FastAPI, validation, middleware and API testing.
- Week 11: React/FastAPI/model integration, visualisation and debugging.
- Week 12: risk-based planning; unit/integration/system/acceptance testing.

## Implementation status — 5 November 2026

The user explicitly authorised the whole application after approving the proposed
labels, input scope and two section 2.7 defences. React/FastAPI implementation is
in `../../assignment3/`; model and four A2 inference modules are preserved. See
its README and evidence/verification.json for executed checks and current limits.

The user also reports that the lecturer permits AI coding and the restrictive
wording is legacy. This is recorded as student-reported clarification in
AI_USAGE_NOTE.md; no independent written announcement was inspected. The full
brief remains unchanged. Actual AI use is disclosed in the A3 README.

Remaining: tutor acceptance of combined-dangerous model scope, group recording of
the video, authentic complete weekly minutes and agreed contribution form.
Section 2.8 has not been implemented/claimed; no final Canvas submission is claimed.


### Verified technical handoff

Source ZIP is `../../submission/session-07-group-5-assignment-3-source.zip`.
Working application and README are in `../../assignment3/`. Executed checks:
34 backend tests, 13 frontend tests, fresh install/build/launcher and real-browser
walkthrough at desktop and phone sizes. Standalone ZIP: 33 backend tests pass,
one expected source-comparison skip. npm/pip audits have no known findings;
ZAP has no High/Medium/Low findings in the bounded scan. See evidence and
security notes for scope; optional browser-test suite is not claimed executed.
No video/minutes/contribution signatures or Canvas submission are claimed.
