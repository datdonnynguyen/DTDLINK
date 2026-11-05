# DTDLINK A3 — three-presenter video script

The group will record separately in English, then combine the clips into one video. Choose who presents A, B and C; these labels do not establish individual contributions.

Read the blockquotes aloud. All other text gives screen actions, preparation notes and explanations. Use [FULL_SCRIPT_EN.md](FULL_SCRIPT_EN.md) for the combined spoken script.

| Presenter | Final-video timeline | Spoken words | Recording guide |
|---|---|---:|---|
| A | 00:00–04:15 | 351 | [Website demonstration](PRESENTER_A.md) |
| B | 04:15–08:45 | 443 | [Code, API and model integration](PRESENTER_B.md) |
| C | 08:45–14:15 | 483 | [Security and limitations](PRESENTER_C.md) |

The 1,277 spoken words take approximately 11 minutes 37 seconds at 110 words per minute, leaving about 2 minutes 38 seconds for actions within the 14:15 target. This is an estimate, not a recorded duration. Rehearse with a stopwatch. Include titles and credits within the 15-minute maximum. Presenter B should prepare file tabs in advance.

## 1. Use the same application version

- Primary frontend: http://127.0.0.1:5173/.
- Primary API documentation: http://127.0.0.1:8000/docs.
- GET /model-info should return version `a2-rf-d4aa8ff3`, 36 features and threshold 0.5.
- Use the primary app throughout. Mention experimental research only when discussing limitations.
- From an installed `assignment3/` folder, use `backend/.venv/bin/python scripts/run.py`. If the services are already running, use them rather than starting another launcher on the same ports. A new machine must follow the application README first.

## 2. Inputs and expected screen content

| Scene | Input or action | Screen content |
|---|---|---|
| Main example for A and B | A misleading address → Analyse link | Potentially dangerous; actual host `account-check.example` |
| Main example URL | `https://paypal.com@account-check.example/login` | Hidden destination; Account-related terms |
| Frontend validation | `example.com/` | Start the URL with http:// or https://. |
| API validation | JSON containing URL `example.com/` | Server response 422 and error JSON |
| Not-found page | http://127.0.0.1:5173/unknown-page | This page isn’t here.; Back to Check URL |
| Controlled connection failure | Abort /predict in the browser test | Cannot reach the analysis service... |
| Controlled rendering failure | Test response `{}` | Something unexpected happened.; Reload DTDLINK |
| Current-result chart | Show signals → High attention → Hidden destination | What deserves a closer look? |
| Session chart | Select Check #, filter, then Clear session | How do your checks compare? |

The primary example was checked in the browser on 6 November 2026: Potentially dangerous, 97.3% displayed confidence, the stated actual host and both observations. The spoken script avoids quoting that confidence value. The output is a model estimate, not a verification of the destination. A simple address fills `https://example.com/`; it does not promise a benign prediction.

## 3. Prepare controlled-state clips for Presenter A

The existing `frontend/tests/app.spec.js` includes these scenarios:

- `loading is visible and duplicate submissions are disabled`: holds the response with a gate, then continues the real request.
- `backend outage is shown as a useful error`: aborts the request in the browser.
- `unexpected render failure reaches the error boundary`: supplies an invalid `{}` response.

These are controlled tests. Record the application window under test and identify the faults as controlled, as the script does. Do not modify the model or stop the shared backend to create these scenes.

One rehearsal option is Playwright Inspector. From `assignment3/frontend/`, run one command at a time:

```sh
npm run test:e2e -- --project=desktop --debug --grep "loading is visible"
npm run test:e2e -- --project=desktop --debug --grep "backend outage"
npm run test:e2e -- --project=desktop --debug --grep "unexpected render failure"
```

Use Step over and pause when the application displays the required state. Read the corresponding test to understand whether it holds, aborts or replaces a response. Rehearse the pause point before recording. Playwright may require its Chromium runtime to be installed; a normal browser installation does not establish that the test runtime is available. The flags were checked against the installed CLI. These error scenes have not been newly executed as part of script preparation.

After the error scenes, close the test window and return to the normal app for genuine predictions. Create several real results in the same tab before recording Session insights. Do not refresh between those checks. Clear the session after demonstrating the chart.

## 4. Prepare the security demonstration

The DoS command uses the two cases in the current source and overwrites `evidence/dos-demo.json`. Keep a separately named backup if you want to preserve the historical measurement. Inspect the real output before recording; the narration does not prescribe latency or rejection counts. Do not run training experiments or use A2 test outcomes to prepare the video.

The scan narration explicitly describes saved evidence from 5 November 2026. Present its date and scope accurately. The Origin demonstration connects only to the local API. Saved scans demonstrate findings and fixes within their coverage, not that every exploit has been tested. Read `docs/SECURITY_FINDINGS.md` before presenting. If you perform a new scan, update the narration to match its date and results.

## 5. Rehearse and combine the recordings

1. Read the “Understand before recording” notes in your presenter file.
2. Open the required pages and source files beforehand. Find the named functions so you can switch quickly.
3. Rehearse speaking and clicking together. Adapt the wording to your understanding while retaining the technical meaning.
4. Record short scene clips with readable text, clear microphone audio and approximately two seconds of space at each end.
5. Keep the screen aligned with the request or result being discussed. You may cut waiting time; do not splice in a different response as if it came from the same request.
6. Have one person combine A → B → C, balance audio, check coverage and verify playback. Presenter assignments are not contribution percentages.
7. Export MP4 or AVI, for example `session-07-group-5-assignment-3-video.mp4`. Keep the complete file under 15 minutes. If using the permitted unlisted-video option, verify signed-out access and retain the link until marking is complete.

## 6. Coverage against the brief

| Video requirement | Scenes |
|---|---|
| Intended users and problem | A1 |
| Live workflow, validation, loading, errors and phone layout | A2–A4 |
| Two useful interactive visualisations | A5 |
| One request through actual code and /docs | B1–B5 |
| Implementation and design reasons | B2–B5, C1–C3 |
| Threat model, hostile input and selected defences | C1–C3 |
| Reproducibility, references and AI disclosure | C4 |
| Limitations and next steps | C5 |

The script does not claim a completed section 2.8 study. The recordings, controlled faults and benchmark still require rehearsal on the recording machine. These files are preparation materials, not evidence that the group has recorded or submitted its video.
