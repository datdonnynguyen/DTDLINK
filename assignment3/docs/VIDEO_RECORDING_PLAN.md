# DTDLINK A3 — three-person recording plan

Prepared on 6 November 2026. The group will present in English, record separately and edit the sections into one video. Presenter A/B/C assignments are for the group to choose and do not establish individual contributions.

Use the [complete script bundle](video-script/README.md), including full narration and scene instructions. The [combined English script](video-script/FULL_SCRIPT_EN.md) contains only the speaking text and scene headings.

## 1. Requirements and application version

This plan follows section 3.1 and Video rubric criteria 1–4 of the locally saved Assignment 3 specification, checked against the application README, React/FastAPI code and security evidence.

Show a real workflow, follow a request through actual code and /docs, explain implementation and design reasons, demonstrate security, and discuss limitations and next steps. Anything the group wants assessed must appear in the video. The saved brief does not require every member to present or explicitly require webcams or an uninterrupted take.

Use the primary app at http://127.0.0.1:5173/ and API documentation at http://127.0.0.1:8000/docs. Its model is the frozen A2 Random Forest: 36 features, threshold 0.5, version `a2-rf-d4aa8ff3`. Keep this version consistent across recordings. Discuss experimental models briefly under limitations.

## 2. Division and timeline

| Presenter | Final-video timeline | Duration | Responsibility |
|---|---|---|---|
| A | 00:00–04:15 | 4:15 | Users, website workflow, states, phone layout and charts |
| B | 04:15–08:45 | 4:30 | A real request through React, FastAPI, the model and the response |
| C | 08:45–14:15 | 5:30 | Threat model, two defences, evidence, setup and limitations |

Presenter C has more time because two defences need demonstration. Record short scene clips rather than requiring a perfect single take. The 14:15 total is a target; rehearse and keep the exported video within 15 minutes including titles and credits.

## 3. Presenter A — website demonstration

Follow [Presenter A’s script](video-script/PRESENTER_A.md).

- **00:00–00:30:** Introduce the project, intended users and URL-text-only scope on Check URL.
- **00:30–01:35:** Select A misleading address and submit. Show the prediction, confidence, actual host, URL breakdown and evidence/action cards.
- **01:35–02:40:** Show loading, invalid input, an interrupted request, the not-found page and the controlled rendering fallback.
- **02:40–03:10:** Show a phone-sized viewport and keyboard navigation.
- **03:10–04:15:** Demonstrate both chart filters and selection controls, then clear the session and hand over to B.

Use `https://paypal.com@account-check.example/login` as text inside the app. Its actual host is `account-check.example`. Do not navigate to the destination. Explain that observations help interpret URL structure and are not the exact reasons for the model decision.

Prepare controlled states using the existing tests and rehearsal instructions. Show the matching state before using its narration. Create real results in the same normal browser tab before showing Session insights; reloading clears that session. If a filter has no matching results, demonstrate the honest empty state rather than inventing a prediction.

## 4. Presenter B — code and integration

Follow [Presenter B’s script](video-script/PRESENTER_B.md).

- **04:15–04:40:** Briefly show the README architecture diagram and explain GET versus POST.
- **04:40–05:30:** Show `App.jsx` onSubmit and `api.js`: validation, loading, JSON request, response and timeout handling.
- **05:30–06:35:** Show Pydantic schemas and submit the same example through /docs. Demonstrate a 200 response and a missing-scheme 422 response.
- **06:35–07:40:** Show lifespan startup loading, the service and the saved model’s feature extraction and predict_proba call.
- **07:40–08:45:** Explain labels, threshold and predicted-class confidence. Show the response rendered as escaped text and explain the local-analysis design.

Use actual code rather than only diagrams. Explain each important block’s input, processing, output and design reason. Preserve A2 feature logic. Do not call the combined dangerous output phishing-only probability or a calibrated safety estimate. Let C explain concurrency protection in detail.

## 5. Presenter C — security and limitations

Follow [Presenter C’s script](video-script/PRESENTER_C.md).

- **08:45–09:30:** Explain attackers, goals, capabilities, trust boundaries and applicable controls. Explain why database injection and outbound-request SSRF do not apply to the prediction path.
- **09:30–11:35:** Demonstrate the DoS script, compare baseline/defended output, and show the bounded thread pool, capacity check, 503 response and cancellation-safe slot accounting.
- **11:35–12:55:** Present dated dependency/ZAP findings and fixes, show the CSP configuration, and demonstrate local rejection of an unapproved Origin.
- **12:55–13:25:** Show setup instructions, pinned dependencies, the included model, references and AI disclosure.
- **13:25–14:15:** Finish on How it works with model limitations and next steps.

Run the DoS demonstration from `assignment3/`:

```sh
backend/.venv/bin/python scripts/dos_demo.py
```

The baseline is test-only; it does not disable production defences. The controlled slow case repeats inference 30 times and must be identified as instrumentation, not a naturally discovered expensive URL. The ASGI experiment measures scheduling, not network DDoS resilience. Discuss the cost: bounded throughput and legitimate retries.

The second selected defence uses saved scans from 5 November 2026. Present the original findings, fixes and bounded coverage. Do not restore weak configuration in the main app to stage an attack. Saved scans are not a demonstration of every exploit. For the live Origin example, run:

```sh
curl -i -H 'Origin: http://evil.example' http://127.0.0.1:8000/health
```

Only localhost is contacted. CORS is not authentication. Section 2.8 remains incomplete and must not be claimed from the DoS benchmark or selected URL examples.

## 6. Record separately and edit consistently

1. Confirm that all three machines use the same primary model/source version. No presenter needs to retrain it.
2. Agree on landscape framing, a common resolution if supported, readable code text and clear microphone audio. Record a 20-second test clip and review it.
3. Close private tabs and mute notifications. Keep the pointer easy to follow.
4. Record screen and narration together. Leave approximately two seconds at each clip boundary. Avoid reintroducing the whole project in B and C.
5. Keep real input-to-result actions continuous. You may trim installation or scan waiting time, but do not substitute another result as if it belongs to the same request.
6. Label scene files clearly, such as A1_intro, A2_workflow, B1_request and C2_dos. One person combines the clips and balances the audio.
7. Use brief section titles. Webcam or effects should not cover code, results or evidence. They are not explicitly required by the saved brief.
8. Export MP4/AVI within 15 minutes, including all titles and credits, and watch the complete final file. Use the group name in the filename. For an unlisted-video submission, verify signed-out access and retain the link until marking is complete.

## 7. Final rehearsal checks

- The same main example works in the app and /docs and displays genuine model output.
- Loading, connection failure and rendering fallback have been prepared as controlled scenes; 404 is a separate state.
- The phone-sized view, keyboard interaction and both chart demonstrations are readable.
- The security commands work on C’s recording machine. Spoken measurements match the shown run; historical scans are labelled with their actual date.
- Each presenter can explain input, processing, output, design reason and limitation in their own words.

This is a recording plan, not evidence that the video, rehearsals, new scans or final submission have been completed.
