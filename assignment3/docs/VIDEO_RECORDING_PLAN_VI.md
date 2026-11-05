# Kế hoạch quay video A3 cho 3 người — DTDLINK

Ngày chuẩn bị: 6/11/2026. Nhóm chọn nói tiếng Anh, mỗi người quay riêng rồi ghép.
Người A/B/C dưới đây là phân đoạn đề xuất; nhóm tự chọn người, không phải xác
nhận về đóng góp thực tế. Mục tiêu bản cuối: **14 phút 15 giây**, tối đa 15 phút.

## 1. Căn cứ và bản ứng dụng dùng quay

Đọc `Week-12/Assessment/Assignment-3-Specification.md`, mục 3.1 và rubric Video
1–4; đối chiếu README, code React/FastAPI, VIDEO_CHECKLIST.md và SECURITY_FINDINGS.md.
Đề yêu cầu demo chạy thật, theo một request qua code và /docs, giải thích cách
làm/lý do thiết kế, threat model, minh họa bảo mật, giới hạn và hướng tiếp theo.
Những gì muốn được chấm phải xuất hiện trong video. Không phải mọi thành viên
đều phải xuất hiện theo bản đề đã lưu; nhóm chọn ba người cùng thuyết trình.
Bản đề đã lưu không nêu yêu cầu bắt buộc bật webcam hay quay một mạch.

Quay bản chính `assignment3/`, frontend `http://127.0.0.1:5173/`, API/docs
`http://127.0.0.1:8000/docs`. Model: Random Forest A2, 36 features, threshold 0.5,
version `a2-rf-d4aa8ff3`. Không chuyển sang preview giữa các đoạn. Nghiên cứu A3
chỉ nhắc ngắn ở giới hạn; không biến video này thành báo cáo huấn luyện model.

## 2. Chia ba phần

| Người | Mốc trong bản ghép | Thời lượng | Phần chịu trách nhiệm trình bày |
|---|---|---|---|
| A | 00:00–04:15 | 4:15 | Người dùng, thao tác ứng dụng, trạng thái lỗi, điện thoại, hai biểu đồ |
| B | 04:15–08:45 | 4:30 | Theo một request qua React → FastAPI → model → kết quả; code và /docs |
| C | 08:45–14:15 | 5:30 | Threat model, hai defence, bằng chứng trước/sau, cách chạy và giới hạn |

Không cần chia đều đúng số giây. Phần C có hai defence cần minh họa nên dài hơn.
Mỗi người nên quay thành 2–3 clip nhỏ; ghép theo thứ tự dưới đây, không cần quay
cả phần hoàn hảo trong một lần. Không đọc nguyên code hoặc tên mọi file.

## 3. Người A — ứng dụng và trải nghiệm người dùng

### A1 — 00:00–00:35: giới thiệu

Màn hình: trang Check URL, thêm tên DTDLINK và Session 7 Group 5 khi dựng nếu cần.
Nói ai dùng ứng dụng, giải quyết gì, giới hạn chỉ đọc văn bản URL.

Gợi ý tiếng Anh:
> DTDLINK helps users inspect a suspicious link before opening it. Our application
> analyses the URL text using a trained model and shows readable observations.
> It does not visit the destination website or guarantee that a link is safe.

### A2 — 00:35–01:45: một lần kiểm tra thật

Dán `https://paypal.com@account-check.example/login` **vào ô nhập ứng dụng**, bấm
Analyse link/Enter. Chỉ model mới quyết định nhãn; không thay kết quả để khớp lời nói.
Chỉ label, confidence, actual host, một observation có evidence/action và mở
Understand the parts of this URL. Host là `account-check.example`, không phải
`paypal.com`. Không mở URL trong thanh địa chỉ trình duyệt.

> The text before the at sign is user information. The actual destination host
> is account-check.example. These observations help us read the address; they
> are not the exact reasons behind the model's prediction.

### A3 — 01:45–02:50: loading và lỗi

Quay loading thật. Nếu quá nhanh, dùng công cụ làm chậm/block request của trình
duyệt hoặc bài kiểm thử có sẵn khi tập quay; nói rõ đó là mô phỏng nếu dùng.
Thử input trống hoặc `example.com/` để hiện lỗi cạnh ô nhập. Mở
`http://127.0.0.1:5173/unknown-page` để quay trang 404 và nút quay về.
Quay thêm lỗi mạng và fallback bất ngờ trong một clip kiểm thử có kiểm soát:
`frontend/tests/app.spec.js` đã có tình huống abort request và response `{}`.
Phải tập dựng tình huống và nhìn thấy đúng màn hình trước khi ghi hình; việc
có test trong source chưa chứng minh clip này đã quay được. Không sửa model thật
hoặc để ứng dụng hỏng nhằm trình bày lỗi.

> Invalid input is rejected with a message beside the field. We also provide
> a not-found page and controlled error handling so failures do not leave a blank screen.

### A4 — 02:50–03:20: phone và bàn phím

Dùng viewport khoảng 375 px, thể hiện menu, ô nhập, result không tràn ngang.
Dùng Tab/Enter để chứng minh thao tác bàn phím. Nói đây là phone-sized viewport
nếu quay bằng chế độ giả lập, không gọi là thử trên điện thoại thật.

### A5 — 03:20–04:15: hai biểu đồ có tương tác

Current-result signals: lọc mức chú ý, chọn một signal để xem chi tiết.
Session insights: chạy vài lần kiểm tra thật trước đó, lọc nhãn và chọn Check #.
Không reload trước khi quay phần session vì dữ liệu chỉ nằm trong RAM.
Nói hai câu hỏi khác nhau: URL hiện tại có dấu hiệu gì; các lần kiểm tra trong
phiên có điểm model khác nhau ra sao. Lịch sử không lưu URL/hostname.

Chuyển phần:
> Next, we will follow this input through the actual frontend, API and model code.

## 4. Người B — kết nối và code

### B1 — 04:15–04:40: bức tranh tổng thể

Mở sơ đồ architecture trong README, chỉ một vòng đi và về. Không dành toàn bộ
phần này cho sơ đồ: rubric yêu cầu code thật. Nhắc GET /health và POST /predict
có mục đích khác nhau, không chỉ thêm method cho đủ yêu cầu.

### B2 — 04:40–05:35: React gửi gì?

Mở `frontend/src/App.jsx`, hàm `onSubmit`: validateURL → loading → apiRequest →
JSON.stringify({url: submittedURL}) → setResult → finally tắt loading.
Mở nhanh `frontend/src/api.js`: fetch POST, đọc response, xử lý status/lỗi mạng
và timeout. Có thể chỉ payload/status của request thật trong Network tab.

> The frontend validates the input for usability, sets a loading state, and sends
> the original URL as JSON. Backend validation is still necessary because an
> attacker can bypass the interface.

### B3 — 05:35–06:35: API và /docs

Mở `backend/app/schemas.py`: PredictRequest/PredictResponse, HTTP(S), giới hạn URL.
Mở /docs và thực hiện POST /predict bằng **cùng URL đã demo ở phần A**.
Chỉ request, HTTP 200 và vài trường response quan trọng. Thử URL thiếu scheme
để hiện 422 và JSON error thống nhất. Mở `main.py`, endpoint `predict_url`, chỉ
nơi gọi công việc inference. Để người C giải thích sâu capacity/thread.

### B4 — 06:35–07:40: model thật và xử lý đầu vào

Mở `backend/app/main.py`, lifespan: model chỉ nạp lúc startup.
Mở `backend/app/service.py`, load_model/predict; rồi
`backend/src/dtdlink_ml/predict.py`, `predict_urls`/`predict_proba` và điểm gọi
trích feature. Chỉ ví dụ vài feature, không đọc cả 36. Bản chính giữ nguyên
logic A2 ở training/inference, không âm thầm bỏ HTTPS. Bảo vệ hash có sẵn có thể
nhắc rất ngắn; hai defence xin chấm vẫn là DoS và misconfiguration/dependencies.

> We reuse the frozen Assignment 2 Random Forest and the same 36-feature
> extraction logic. The model is loaded once at startup. Class one combines
> phishing, malware and defacement; it does not identify a specific attack type.

### B5 — 07:40–08:45: response, confidence và thiết kế

Mở `service.py`: probability p, threshold 0.5, confidence p hoặc 1-p.
Mở `Result.jsx`/`URLAnalysis.jsx` và chỉ nơi hiển thị result. Giải thích model
score khác quan sát URL; model không biết nội dung trang đích. Trả lời vì sao
không fetch website: giữ phạm vi URL-text và tránh thêm bề mặt outbound requests.

> Confidence is the model's estimate for its predicted class. It is not a
> calibrated probability of real-world safety. The separate URL observations
> are rendered as escaped text and do not change the prediction.

Chuyển phần:
> We will now show how the backend handles hostile input and excessive workload.

## 5. Người C — bảo mật, chạy lại và giới hạn

### C1 — 08:45–09:25: threat model và hygiene

Mở threat model README. Attacker có thể bỏ qua React, gửi input tùy ý và nhiều
request. Mục tiêu: đánh lừa kết quả hoặc làm cạn tài nguyên. Chỉ source minh họa
Pydantic/body limits, React text escaping, exact CORS và security headers.
Không có database, upload, accounts hoặc outbound URL fetching; giải thích vì
sao SQL injection/SSRF tương ứng không phải attack surface của prediction path.
Không gọi CORS là authentication hoặc cơ chế chặn mọi client trực tiếp.

### C2 — 09:25–11:35: defence 1 — application-level DoS

Mở `scripts/dos_demo.py`: baseline cố ý gọi model đồng bộ trong async endpoint;
defended dùng factory app thật. Đây là test riêng, không tắt defence production.
Chạy từ thư mục `assignment3/` khi tập và khi quay:

```sh
backend/.venv/bin/python scripts/dos_demo.py
```

Script ghi lại `evidence/dos-demo.json`; số đo mới có thể khác số cũ. Hiện script
in summary cho hai case. Giải thích baseline/defended, health latency và số 503.
Mở `main.py`: bounded ThreadPoolExecutor, run_in_executor, capacity, 503 và slot
được giữ đến khi công việc thật kết thúc. Đánh đổi: người dùng thật có thể bị
từ chối khi bận, throughput bị giới hạn. Có thể thêm clip live TCP bằng
`backend/.venv/bin/python scripts/live_smoke.py`; script ghi `evidence/live-http.json`.

> The baseline blocks unrelated requests while inference runs. Our defence moves
> inference away from the event loop and limits concurrent work. Excess requests
> receive 503 rather than entering an unbounded queue. The cost is that legitimate
> users may need to retry when the service is busy.

Case slow_request lặp inference 30 lần để tạo tải kiểm soát; **không phải** URL
được phát hiện có khả năng tự gây 30 lần inference. ASGI benchmark không đo DDoS
hoặc sức chịu tải đường truyền. Không hứa chính xác latency cũ khi quay lại.

### C3 — 11:35–12:55: defence 2 — misconfiguration/dependencies

Mở SECURITY_FINDINGS.md và file trước/sau tương ứng. Chỉ rõ CSP unsafe-inline đã
được phát hiện, chính sách đã sửa trong `frontend/vite.config.js`; cho thấy header
thật của app hiện tại. Chỉ pip-audit trước/sau và npm audit, cùng phạm vi ZAP.
Minh họa Origin không được phép bằng request tới **API localhost của nhóm**:

```sh
curl -i -H 'Origin: http://evil.example' http://127.0.0.1:8000/health
```

Lệnh chỉ kết nối 127.0.0.1; evil.example là chuỗi header, không phải đích truy cập.
Nếu phát lại audit thật, chuẩn bị tool/mạng khi tập. Nếu trình bày scan đã lưu,
nêu đúng ngày và phạm vi, không gọi là scan đang chạy trực tiếp. Không phục hồi
dependency yếu hay nới CSP của ứng dụng chính để tạo màn tấn công. Nếu cần thêm
demo exploit trước/sau, chuẩn bị bản lab tách riêng; hiện không khẳng định đã có.
Saved scans là bằng chứng quét/fix; không tự chứng minh mọi exploit đã bị chặn.

> Our scans identified an overly permissive style policy, which we tightened.
> The saved results show the findings before and after the fix. These checks
> cover a bounded local scan, not proof that the application has no vulnerabilities.

### C4 — 12:55–13:25: chạy lại từ source

Mở README setup và cấu trúc frontend/backend/models, pinned requirements và npm
lock. Chỉ lệnh launcher `backend/.venv/bin/python scripts/run.py`. Không cần quay
toàn bộ cài đặt dependency nhiều phút. Nhắc README có architecture, threat model,
references và AI disclosure; không tuyên bố chạy Windows nếu chưa kiểm chứng.

### C5 — 13:25–14:15: giới hạn và tiếp theo

Nói model còn false positives/format bias, nhãn gộp, confidence chưa calibrated,
không xác minh website hiện tại. Thử nghiệm mới chưa đạt joint gates nên giữ
model chính; không cần đọc bảng mọi model. Section 2.8 chưa hoàn thành.
Hướng tiếp theo: dữ liệu có nguồn gốc tốt hơn, đánh giá độc lập, kiểm thử triển
khai rộng hơn. Ghi nhận AI đúng README; không mô tả toàn bộ code là tự viết nếu
không đúng. Kết thúc rõ, không kéo dài quá 15 phút.

## 6. Cách ba người quay riêng cho dễ ghép

1. Cả nhóm chốt cùng source/model trước khi quay. Nếu dùng máy khác, chạy cùng
   ZIP chính và kiểm tra /model-info. Người chỉ trình bày không cần train model.
2. Thống nhất hình ngang, ví dụ 1920×1080 nếu máy hỗ trợ, cỡ code đọc được,
   ngôn ngữ giao diện và cách phát âm DTDLINK. Ưu tiên tiếng mic rõ hơn webcam.
3. Mỗi người thử clip 20 giây, nghe lại và xem code có đọc được ở kích thước bình
   thường. Tắt thông báo, đóng tab cá nhân, tránh lộ thông tin tài khoản.
4. Quay màn hình và giọng cùng lúc. Mỗi clip chừa khoảng 2 giây yên ở đầu/cuối.
   Giới thiệu cá nhân một lần nếu muốn; người B/C không giới thiệu lại cả dự án.
5. Giữ thao tác input → response liên tục để thấy kết quả thật. Có thể cắt thời
   gian cài đặt/chờ quét, nhưng không ghép kết quả khác vào như cùng một request.
6. Gửi clip gốc cho một người ghép; đặt A1_intro, A2_workflow, B1_request,
   C1_threat, C2_dos... và cho biết thứ tự. Tên phần không phải tên đóng góp.
7. Người ghép cân âm lượng ba giọng, giữ cursor dễ thấy, thêm tiêu đề chuyển
   phần thật ngắn. Webcam, nhạc nền và hiệu ứng không được đề yêu cầu; dùng nếu
   giúp hiểu hơn và không che code/result. Không tăng tốc giọng đến khó nghe.
8. Xuất MP4/AVI, tên gợi ý `session-07-group-5-assignment-3-video.mp4`, tổng thời
   gian dưới 15 phút gồm title/credits. Mở file cuối và xem từ đầu đến cuối.
   Nếu quá giới hạn upload Canvas, đề cho phép YouTube unlisted + file link;
   kiểm tra truy cập khi đăng xuất, giữ link hoạt động đến khi chấm xong.

## 7. Những cảnh cần tập trước khi nhóm quay thật

- Cùng URL demo chạy được trong app và /docs, nhãn/confidence đúng model thật.
- Loading, lỗi API và unexpected fallback được tạo đúng bằng cách có kiểm soát;
  hiện chưa thực hiện buổi tập quay này. Không nhầm lỗi 404 với fallback render.
- Phone viewport, bàn phím và hai biểu đồ đều nhìn rõ. Nếu cần quay cả hai nhãn,
  chọn input được model thực sự trả ra nhãn đó sau khi kiểm tra; không tự gọi
  Google/example.com là demo benign, không bỏ scheme để ép kết quả.
- DoS script và công cụ audit có sẵn trên máy người C. Đọc kết quả mới trước khi
  viết câu có số liệu; ghi scan lịch sử đúng là scan lịch sử.
- Cả ba hiểu phần mình: input → xử lý → output → vì sao chọn cách đó → giới hạn.
  Các câu tiếng Anh ở đây là gợi ý; diễn đạt lại theo điều người trình bày hiểu.

Đây là kế hoạch quay, không xác nhận video đã được ghi hoặc các kiểm thử mới
đã chạy. Không có thay đổi runtime, model hoặc dữ liệu từ việc tạo tài liệu này.
