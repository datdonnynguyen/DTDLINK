# Video checklist — maximum 15 minutes

For the group's chosen English narration and separate recordings by three
presenters, see [the recording plan](VIDEO_RECORDING_PLAN.md).
It assigns a 14:15 timeline, screen actions, English speaking cues and rehearsals;
the group will choose who presents each part.

Complete English narration, screen directions and rehearsal notes are
in [the three-presenter script bundle](video-script/README.md).

Aim for 13–14 minutes so the final file stays within the limit. Demonstrate the
real application and explain code in your own words. This is a preparation guide,
not evidence that a video has been recorded or that everyone understands the code.

| Time | What to show | What to explain |
|---|---|---|
| 0:00–0:45 | Check URL page | Intended users, phishing-link problem, URL-text-only scope |
| 0:45–2:30 | Live prediction, actual-host breakdown and one evidence/action card; benign branch and invalid input | Labels, correct confidence, URL observations versus model decision, formatting bias |
| 2:30–3:30 | Phone layout, keyboard Enter, 404 and service error | Loading/success/error states and accessibility |
| 3:30–5:45 | Actual React handler, `/docs`, FastAPI endpoint, feature extractor and model call | Follow one real JSON request through validation, API, 36 features and response |
| 5:45–6:45 | Both charts: filter and select details | Different questions, observed signals versus model score, anonymous history |
| 6:45–7:30 | README threat model | Attacker, goals, capabilities and why there is no SSRF/SQL/upload/account attack surface |
| 7:30–10:00 | Run `scripts/dos_demo.py` and inspect `main.py` | Blocking baseline, responsive health, 503 for overload, cancellation-safe slot accounting and cost |
| 10:00–11:45 | npm audit, pip-audit before/after and ZAP findings | Actual findings, fixes, remaining limitations; why headers/escaping/CORS matter |
| 11:45–13:15 | README, source layout and fresh-start instructions | Pinned versions, model startup hash, no dataset needed, AI disclosure |
| 13:15–14:00 | Limitations and next steps | Combined target, tutor clarification, evasion weakness, no completed section 2.8 study |

Do not call the controlled repeated-inference case a discovered malicious URL.
Its 30 repeats are instrumentation in the test harness. The burst case uses
actual inference calls without this instrumentation. The ASGI benchmark is an
in-process application test, not a network load test.

To show unexpected-model errors without breaking the real application, use the
sanitised error test in `backend/tests/test_api.py`; frontend fallback behavior can
be reproduced with the optional Playwright route-interception test. Explain that
these are controlled faults. Do not leave broken code or defence-disabling flags
in the normal startup path.

Before submitting:

- Play the exported MP4/AVI from beginning to end; check text size and audio.
- Confirm duration <=15 minutes and include the group name in the filename.
- If using unlisted YouTube, test access from a signed-out browser and keep the
  link accessible until marking completes.
- Anything the team wants marked must appear in the video. A source feature or
  saved scan on its own does not satisfy the demonstration requirement.
- Do not claim tutor approval, a Windows run, user testing or member contribution
  that the team has not actually confirmed.
