# Presenter C — Security, reproducibility and limitations

**Mốc bản ghép:** 08:45–14:15. Chỉ đọc blockquote. Dùng bản chính. Chuẩn bị
terminal ở `assignment3/`, README và các file có tên dưới đây. Đừng đọc số liệu
cũ như thể đó là kết quả của lệnh vừa chạy. Mốc thời gian cần tập lại bằng đồng hồ.

## C1 · 08:45–09:30 · Threat model and baseline controls

**Mở:** threat model trong README; chỉ `schemas.py`, `middleware.py` và cách
`URLAnalysis.jsx` render text nếu cần. Không mở mọi file quá lâu.

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

**Mở:** `scripts/dos_demo.py`, chỉ unprotected_app và hai case. Chạy:

```sh
backend/.venv/bin/python scripts/dos_demo.py
```

Lệnh ghi lại `evidence/dos-demo.json`. Có thể cắt bớt lúc chờ, giữ lệnh và output
cùng lần chạy. Không sửa số. Phải thấy health 200 và defended prediction_503 > 0
trước khi dùng lời kết luận. Không có số cố định trong narration này.

> First, application-level denial of service. Our test-only baseline runs synchronous
> inference inside an asynchronous endpoint. This blocks the event loop, delaying
> unrelated requests.
>
> The script compares that baseline with the production application factory using
> thirty-two concurrent predictions, repeated ten times, while measuring health
> request completion.

**Thao tác:** chỉ `burst` summary baseline/defended; các field
median_health_completion_ms, prediction_200 và prediction_503.

> Compare the baseline and defended health timings in the output. The defended
> case rejects excess work with status five oh three instead of accepting an
> unbounded workload. The health endpoint remains available.

**Mở:** `backend/app/main.py`, lifespan/predict_url: ThreadPoolExecutor,
max_concurrent, run_in_executor, done_callback, asyncio.shield. Chỉ 4 block này.

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

**Mở sẵn:** `docs/SECURITY_FINDINGS.md`, `evidence/zap-scan-before.json`,
`evidence/zap-scan.json`, `evidence/pip-audit-before.json`, `evidence/pip-audit.json`,
`evidence/npm-audit.json` và `frontend/vite.config.js`. Chỉ vài field liên quan;
đừng cuộn toàn bộ JSON. Scan đang nói là bằng chứng đã lưu ngày 5/11/2026.

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

**Demo trực tiếp:** lệnh này chỉ kết nối API localhost; evil.example là header.

```sh
curl -i -H 'Origin: http://evil.example' http://127.0.0.1:8000/health
```

**Chỉ:** 403 và JSON origin_not_allowed. Có thể chỉ CSP bằng Network headers
hoặc `curl -I http://127.0.0.1:5173/`. Header demo là minh họa hiện tại, không phải
khẳng định đã dựng exploit CSP trước/sau hay quét ZAP lại trong clip.

> This request rejects an unapproved Origin. We test only our own local application.
> These controls require dependency reviews and a policy permitting only necessary resources.

## C4 · 12:55–13:25 · Running the application and acknowledging assistance

**Mở:** README setup, backend/requirements.txt, frontend/package-lock.json,
README AI statement. Chỉ lệnh launcher, không cần chờ cài dependencies trong video.

> The README covers installation, pinned dependencies, startup, architecture and
> references. The included model needs no retraining. Our AI statement discloses
> assistance with implementation, testing and documentation.

## C5 · 13:25–14:15 · Honest limitations and next steps

**Màn hình:** How it works → Built on Assignment 2 / A prediction has limits.
Không chuyển sang preview hay mở các URL bên ngoài. Có thể chỉ Google diagnostic
đã lưu, nhưng không cần chạy thêm model thử nghiệm trong video.

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

## Hiểu trước khi quay

- DoS: công việc model chiếm tài nguyên; thread giữ event loop phản hồi, capacity
  giới hạn việc đang chạy và trả 503. Không phải per-user rate limiter.
- CORS chỉ là một lớp kiểm soát origin; client không phải browser có thể bỏ header.
- Scan before/after cho thấy các finding/fix trong phạm vi đã quét, không phải
  bằng chứng mọi exploit đều thất bại. Không gọi 53 informational là 53 lỗi nặng.
- Không khôi phục CSP yếu/pip cũ của app chính để quay trước/sau; dùng saved
  evidence đúng ngày. DoS baseline đã là lab riêng trong script.
- Hai defence thuộc mục 2.7; benchmark DoS không biến thành nghiên cứu mục 2.8.

**Cách đọc:** DoS = “denial of service”; CORS có thể đọc “cors”; CSP = “C S P”;
503 = “five oh three”; 403 = “four oh three”; nonce = “nons”.
