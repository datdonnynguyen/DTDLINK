# Presenter C — Security, reproducibility and limitations

**Final-video timeline:** 08:45–14:15. Read only the blockquotes aloud. Use the primary app. Prepare a terminal in `assignment3/`, the README and the files listed below. Never describe old measurements as output from a command you have just run. Rehearse the timing with a stopwatch.

## C1 · 08:45–09:30 · Threat model and baseline controls

**Open:** The README threat model. Briefly point to `schemas.py`, `middleware.py` and the text rendering in `URLAnalysis.jsx` as needed. Keep file changes short.

> An attacker can bypass React, submit hostile input and send concurrent requests
> to mislead the model or exhaust the service.
>
> We enforce backend input and body limits, text-only rendering, exact CORS and
> security headers. CORS is not authentication.
>
> Without a database or outbound website requests, the prediction path does not
> expose SQL injection or server-side request forgery. Our selected defences address
> availability and configuration risks.

## C2 · 09:30–11:35 · Defence one: application-level denial of service

**Open:** `scripts/dos_demo.py`, showing `unprotected_app` and its two cases. Run from `assignment3/`:

```sh
backend/.venv/bin/python scripts/dos_demo.py
```

This overwrites `evidence/dos-demo.json`. Keep the command and output from the same execution together. You may cut waiting time, but do not change the measurements. Before using the conclusion, confirm health status is 200 and the defended case has `prediction_503 > 0`.

**While explaining the output:** Point to the `burst` baseline and defended summaries, especially `median_health_completion_ms`, `prediction_200` and `prediction_503`.

**Then open:** `backend/app/main.py`, at `lifespan` and `predict_url`. Point to `ThreadPoolExecutor`, `max_concurrent`, `run_in_executor`, the completion callback and `asyncio.shield`. Explain the controlled slow case separately. The narration deliberately contains no fixed latency values.

> First, application-level denial of service. Our test-only baseline runs synchronous
> inference inside an asynchronous endpoint. This blocks the event loop, delaying
> unrelated requests.
>
> The script compares that baseline with the production application factory using
> thirty-two concurrent predictions, repeated ten times, while measuring health
> request completion.
> Compare the baseline and defended health timings in the output. The defended
> case rejects excess work with status five oh three instead of accepting an
> unbounded workload. The health endpoint remains available.
> In main dot PY, a bounded thread pool moves inference away from the event loop.
> The default capacity is two jobs. The endpoint checks capacity before scheduling
> work, and returns five oh three with a retry header when it is full.
>
> Slots remain occupied until the actual work finishes, even if the client cancels.
>
> The separate slow-request case deliberately repeats inference thirty times to
> create controlled load. It is not a discovered URL exploit. These in-process
> measurements demonstrate scheduling, not protection against a distributed network attack.
>
> The trade-off is limited throughput: legitimate users may need to retry while
> all prediction slots are occupied.

## C3 · 11:35–12:55 · Defence two: configuration and dependencies

**Prepare these tabs:** `docs/SECURITY_FINDINGS.md`, `evidence/zap-scan-before.json`, `evidence/zap-scan.json`, `evidence/pip-audit-before.json`, `evidence/pip-audit.json`, `evidence/npm-audit.json` and `frontend/vite.config.js`. Point only to relevant findings and configuration. These are saved scans from 5 November 2026.

**Live demonstration:** Run the command below. It connects only to the local API; `evil.example` is an Origin header value, not a destination:

```sh
curl -i -H 'Origin: http://evil.example' http://127.0.0.1:8000/health
```

Point to status 403 and `origin_not_allowed`. You can show the current CSP in the browser Network headers or with `curl -I http://127.0.0.1:5173/`. This demonstrates current headers and origin handling; it does not establish that every CSP exploit was tested before and after, or that ZAP was rerun during the clip.

> Our second defence addresses misconfiguration and vulnerable dependencies.
> These saved audit results are from November fifth.
>
> ZAP identified an overly permissive inline-style policy. We tightened the content
> security policy, using self-hosted styles and a development nonce. The bounded
> scan after that fix recorded no high, medium or low alerts, with informational
> observations still documented.
>
> The dependency audit also identified issues in the environment's pip version.
> We upgraded it in the isolated Assignment Three environment. The saved pip and
> npm audits then reported no known findings. A clean scan is not proof of complete security.
> This request rejects an unapproved Origin. We test only our own local application.
> These controls require dependency reviews and a policy permitting only necessary resources.

## C4 · 12:55–13:25 · Running the application and acknowledging assistance

**Open:** README setup instructions, `backend/requirements.txt`, `frontend/package-lock.json` and the README AI statement. Point to the launcher command; there is no need to record the full dependency installation.

> The README covers installation, pinned dependencies, startup, architecture and
> references. The included model needs no retraining. Our AI statement discloses
> assistance with implementation, testing and documentation.

## C5 · 13:25–14:15 · Honest limitations and next steps

**Screen:** Open **How it works**, showing **Built on Assignment 2.** and **A prediction has limits.** Do not switch to the preview or visit submitted destinations. You may point to a saved diagnostic example, but do not run additional model experiments for this scene.

> Finally, the model still produces false positives and is sensitive to URL
> formatting. Its confidence is uncalibrated, and it cannot distinguish the three
> dangerous subtypes or inspect current website content.
>
> Separate Assignment Three experiments improved some validation metrics but did
> not meet all acceptance criteria, so the primary application retains the original
> model. We do not claim a completed advanced security study under section two point eight.
>
> Next steps include better-sourced data, independent evaluation and broader
> deployment testing. DTDLINK provides evidence to support cautious decisions,
> rather than a guarantee of safety. Thank you.

## Understand before recording

- Inference consumes resources. Threads keep the event loop available; the capacity budget bounds running work and rejects excess requests with 503. It is not a per-user rate limiter.
- CORS is an origin control; non-browser clients can omit Origin.
- Before/after scans show findings and fixes within their coverage. They do not prove every exploit fails. Informational observations are not high-severity vulnerabilities.
- Do not restore weak CSP settings or old pip versions in the main app to stage an attack. Use dated saved evidence. The DoS script already contains a separate lab baseline.
- Both selected defences belong to section 2.7. The DoS benchmark does not complete section 2.8.

**Pronunciation:** DoS = “denial of service”; CORS = “cors”; CSP = “C S P”; 503 = “five oh three”; 403 = “four oh three”; nonce = “nons”.
