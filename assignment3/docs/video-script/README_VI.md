# Script quay video DTDLINK A3 — đọc tệp này trước

**Đã thống nhất:** ba người nói tiếng Anh, quay riêng rồi ghép; nhóm tự phân công
A/B/C. Bộ script dựa trên ứng dụng chính và yêu cầu A3, không phải preview.
Lời nói hoàn chỉnh nằm trong blockquote ở từng tệp; phần tiếng Việt hướng dẫn
thao tác. Có thêm FULL_SCRIPT_EN.md chỉ gồm lời tiếng Anh cho cả nhóm tập đọc.

| Người | Phần bản cuối | Lời nói tiếng Anh | Tệp |
|---|---|---:|---|
| A | 00:00–04:15 | 351 từ | PRESENTER_A.md |
| B | 04:15–08:45 | 443 từ | PRESENTER_B.md |
| C | 08:45–14:15 | 483 từ | PRESENTER_C.md |

Tổng 1.277 từ; khoảng 11 phút 37 giây ở 110 từ/phút, còn khoảng 2 phút 38 giây
cho thao tác/dừng trong mục tiêu 14:15. Đây là ước tính, không phải thời lượng
đã thu âm. Mỗi người bấm giờ khi tập; đoạn B cần mở sẵn file để chuyển nhanh.
Video cuối phải <=15 phút gồm cả title/credits. Không tăng tốc đến khó nghe.

## 1. Chốt cùng phiên bản

- Frontend chính: http://127.0.0.1:5173/.
- API chính: http://127.0.0.1:8000/docs.
- GET /model-info phải cho version `a2-rf-d4aa8ff3`, 36 features, threshold 0.5.
- Cả nhóm dùng cùng bản chính. Nghiên cứu A3 chỉ được nhắc ở giới hạn, không
  chuyển app sang preview giữa các clip.
- Từ thư mục `assignment3/`, môi trường đã cài dùng
  `backend/.venv/bin/python scripts/run.py`. Nếu dịch vụ đã chạy, dùng dịch vụ đó;
  không mở launcher thứ hai trên cùng cổng. Máy mới làm theo README setup trước.

## 2. Các input và chữ cần thấy trên website

| Cảnh | Input/thao tác | Màn hình hoặc ý nghĩa |
|---|---|---|
| Demo chính A và B | A misleading address → Analyse link | Potentially dangerous; actual host `account-check.example` |
| URL demo chính | `https://paypal.com@account-check.example/login` | Hidden destination; Account-related terms |
| Invalid input frontend | `example.com/` | Start the URL with http:// or https://. |
| Invalid input API | JSON có url `example.com/` | Server response 422; error JSON |
| 404 | http://127.0.0.1:5173/unknown-page | This page isn’t here.; Back to Check URL |
| Lỗi mạng có kiểm soát | Abort request /predict trong test | Cannot reach the analysis service... |
| Render fallback có kiểm soát | Test thay response bằng `{}` | Something unexpected happened.; Reload DTDLINK |
| Current chart | Show signals → High attention → Hidden destination | What deserves a closer look? |
| Session chart | Chọn Check #, lọc, rồi Clear session | How do your checks compare? |

Ngày 6/11 đã kiểm tra demo chính trên browser thật: nhãn Potentially dangerous,
confidence hiển thị 97,3%, đúng host và hai observation trên. Script không đọc số
đó để tránh lệch với bản quay. Kết quả là đầu ra model, không xác minh website
đích. A simple address chỉ điền `https://example.com/`; không hứa nhãn benign.

## 3. Chuẩn bị cảnh loading/network/fallback cho A

Ba cảnh này đã có tình huống trong `frontend/tests/app.spec.js`:

- `loading is visible and duplicate submissions are disabled`: giữ response
  bằng gate, cho nhìn nút và loading rồi tiếp tục request thật.
- `backend outage is shown as a useful error`: abort request trong trình duyệt.
- `unexpected render failure reaches the error boundary`: response kiểm thử `{}`.

Đây là **kiểm thử có kiểm soát**, không phải response model bình thường. Có thể
quay cửa sổ ứng dụng dưới test, giữ cảnh đủ đọc và nói rõ như narration đã viết.
Không chỉnh code/model hoặc dừng backend đang dùng để tạo lỗi.

Một cách tập với test có sẵn là dùng Playwright Inspector. Từ `assignment3/frontend/`:

```sh
npm run test:e2e -- --project=desktop --debug --grep "loading is visible"
npm run test:e2e -- --project=desktop --debug --grep "backend outage"
npm run test:e2e -- --project=desktop --debug --grep "unexpected render failure"
```

Mỗi lần chỉ chạy một lệnh, dùng thao tác Step over trong Inspector và dừng khi
trang đang hiện trạng thái cần quay; đọc test để biết request đang được giữ,
abort hay trả dữ liệu lỗi. Tập trước khi quay, vì thời điểm dừng phụ thuộc runner.
Nếu môi trường chưa có Chromium cho Playwright, cần cài browser theo hướng dẫn
của công cụ trước; không đồng nghĩa browser bạn dùng hằng ngày đã có runtime test.
Các flag CLI trên đã được đối chiếu với phiên bản Playwright cài trong dự án.
Trong lượt soạn script này chưa chạy các test/cảnh lỗi hoặc cài browser mới.

Sau cảnh lỗi, đóng cửa sổ test và dùng lại tab ứng dụng bình thường cho các demo
thật. Để quay Session insights, tạo vài kết quả thật trong cùng tab, không refresh
giữa các lần kiểm tra; clear session sau khi đã demo chart.

## 4. Chuẩn bị cho C

Lệnh DoS trong narration dùng hai case như source hiện tại. Chạy lại sẽ ghi
`evidence/dos-demo.json`. Nếu muốn giữ bản scan/benchmark cũ, sao lưu riêng bằng
tên rõ trước. Đọc output thật rồi quay; narration không ấn định latency/số 503.
Không chạy nghiên cứu training hoặc dùng dữ liệu test A2 để chuẩn bị video.

Kết quả dependency/ZAP trong narration được xác định rõ là scan **5/11/2026**.
Không cần quét lại để có thể trình bày bằng chứng lịch sử đúng phạm vi. Chỉ
demo request Origin ngay trên localhost; không gửi request kiểm thử đến website
ngoài. Đọc `docs/SECURITY_FINDINGS.md` để hiểu informational và giới hạn scan.
Saved scan là bằng chứng finding/fix, không phải demo mọi exploit trước/sau.
Nếu quay audit mới, thay lời mô tả ngày/kết quả cho đúng thay vì dùng lời lịch sử.

## 5. Cách mỗi người tập và gửi clip

1. Đọc mục “Hiểu trước khi quay” của phần mình.
2. Mở sẵn trang/file cần chỉ; tìm function bằng tên để tránh cuộn tìm khi quay.
3. Tập nói với thao tác; dùng câu tiếng Anh như bản nháp, chỉnh sang lời mình
   hiểu nhưng giữ đúng ý kỹ thuật và phạm vi đã kiểm chứng.
4. Quay clip ngắn theo từng cảnh; chừa hai giây đầu/cuối, tiếng mic rõ, chữ lớn.
5. Khi nói về request hoặc kết quả, màn hình phải hiện đúng request/kết quả đó.
   Có thể cắt thời gian chờ, không gắn response khác vào như cùng lần kiểm tra.
6. Một người ghép theo A → B → C, cân âm lượng và kiểm tra độ dài, đọc được code,
   hiển thị đủ hai defence và playback cuối. Không gán vai trò thuyết trình thành
   xác nhận về tỷ lệ đóng góp của thành viên.

## 6. Đối chiếu yêu cầu A3

| Yêu cầu video | Cảnh |
|---|---|
| Intended users/problem | A1 |
| Live workflow, input validation, loading/errors, phone | A2–A4 |
| Two useful interactive visualisations | A5 |
| One request through actual code and /docs | B1–B5 |
| How implementation works and why it was designed this way | B2–B5, C1–C3 |
| Threat model, hostile input, selected defences | C1–C3 |
| Reproducibility, references and AI disclosure | C4 |
| Limitations and next steps | C5 |

Section 2.8 chưa có nghiên cứu trước/sau hoàn chỉnh và không được script nhận
là đã hoàn thành. Các mốc quay, mô phỏng lỗi và benchmark cần được tập thật;
tệp script không phải bằng chứng nhóm đã quay, hiểu hết hoặc nộp video.
