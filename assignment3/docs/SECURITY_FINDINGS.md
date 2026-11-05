# Security findings and interpretation

Checks were run on the team's own loopback application on 5 November 2026.
They do not constitute a proof of complete security or a grade prediction.

## Dependency audit

- `evidence/npm-audit.json`: 0 known vulnerabilities in the locked frontend
  dependency tree at the time of the audit.
- `evidence/pip-audit-before.json`: pip 25.0.1 generated 12 vulnerability entries
  in the returned advisory data, including duplicate aliases/records. This is
  **not** a claim of 12 distinct vulnerable application packages or 12 unique CVEs.
- Fix: upgraded the isolated A3 environment's pip to **26.3**, included in the lock
  file and explicit bootstrap instructions. A2's environment was not upgraded.
- `evidence/pip-audit.json`: no known vulnerabilities after that change.
- The older scikit-learn/NumPy/pandas/tldextract versions preserve A2 model and
  suffix-snapshot compatibility. They were included in the audit. A clean audit
  does not mean future vulnerabilities cannot be discovered.

## ZAP configuration scan

Official OWASP ZAP 2.17.0 and an official Temurin Java 17 runtime were downloaded
to a temporary tools directory. They are not application dependencies or ZIP
contents. `scripts/zap_scan.py` scanned the frontend at 127.0.0.1:5173 and backend
at 127.0.0.1:8000; the active phase was restricted to the backend and configured
with a maximum duration of one minute. A fresh authenticated scanner profile was
used and stopped afterwards. The temporary API key was redacted from its log.

Before CSP tightening (`evidence/zap-scan-before.json`):

- Four Medium `CSP: style-src unsafe-inline` alerts, one per frontend route.
- Five Informational `Modern Web Application` alerts.

Fix: removed `unsafe-inline` from frontend style policy, retained self-hosted CSS
and a nonce for Vite's development style/refresh injection. User URL tokens are
rendered as React text nodes; no HTML-rendering bypass exists. The production
preview was rechecked after applying the stricter policy.

After the fix (`evidence/zap-scan.json`):

- High: **0**; Medium: **0**; Low: **0**.
- Informational: **53**, consisting of five `Modern Web Application` notices and
  48 `User Agent Fuzzer` observations.

Interpretation of each remaining type:

- **Modern Web Application:** expected React and Swagger JavaScript application
  detection. No fix is required; it also reminds us that a conventional scan does
  not exercise every client-side route/state.
- **User Agent Fuzzer:** response bodies differ because API errors include a fresh
  request ID; timing/active-count responses can also change. Application routing,
  validation and prediction do not branch on User-Agent. This is informational,
  not evidence of an access-control bypass. It is retained in the evidence.

Coverage limits: explicit route seeding and one JSON POST were scanned. Browser
JavaScript behavior, every possible input, network infrastructure and deployment
TLS are not exhaustively assessed. A separate browser walkthrough checked the
main UI workflow. There is intentionally no HSTS on local HTTP and no claim of
Internet production readiness. CSP and frame-denial headers reduce XSS/framing
risk but do not substitute for text escaping or validation.

## Availability experiment

`evidence/dos-demo.json` records ten repeated 32-request bursts using actual model
calls, and five controlled expensive-inference comparisons. The production app
factory uses two bounded inference slots; the intentionally blocking baseline is
only in the lab script and is never served by normal startup.

Observed burst totals: baseline accepted 320 requests; defended accepted 20 and
rejected 300 with 503. Median scheduled health completion was approximately
532 ms versus 31 ms. The separate repeated-inference case was approximately
484 ms versus 3 ms. Read the raw distributions rather than treating a single run
or these rounded numbers as a portable performance promise.

The slow-case predictor repeats inference 30 times to produce a controlled load.
It is a scheduling demonstration, not a naturally discovered expensive URL. The
burst uses no such multiplier. ASGI transport measures in-process scheduling;
TCP/network capacity and distributed denial of service are not tested. The cost
of the defence is rejection of excess legitimate work and bounded throughput.

## Other checks and known model limitations

- Backend tests cover body limits including chunked input, body-read deadlines,
  rejection of invalid input, exact CORS including /docs same-origin calls,
  sanitized unexpected errors, hash validation before deserialization, cancellation
  accounting and offline inference.
- A2 model hash and its four inference-source copies are preserved. A compatibility
  check on 1,600 raw test URLs reproduced labels exactly and probabilities within
  1e-12 after moving to the A3 Python environment.
- No dependency scan fixes the model's formatting bias or prediction evasion.
  Complete HTTP(S) input is required, but percent encoding may still change output.
- No section 2.8 before/after model-attack study is claimed.
