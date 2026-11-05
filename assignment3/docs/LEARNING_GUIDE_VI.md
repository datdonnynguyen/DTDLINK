# Hiểu DTDLINK A3 từng phần

## 1. Câu chuyện của ứng dụng

Người dùng nhận một liên kết và muốn kiểm tra trước khi mở. DTDLINK chỉ đọc các
ký tự trong liên kết. Nó không biết trang đích hiện đang chứa gì và không thể
bảo đảm an toàn. Model A2 gộp phishing, malware và defacement thành một lớp.

Có hai loại thông tin khác nhau:

- **Dự đoán model:** xác suất thuộc nhóm nguy hiểm, từ Random Forest.
- **Dấu hiệu quan sát:** quy tắc như có @, hostname là IP, ký tự trông giống nhau.
  Các quy tắc giúp đọc URL; chúng không giải thích chính xác model đã suy luận gì.

## 2. Theo dõi một yêu cầu thật

Ví dụ `https://paypal.com@account-check.example/login`:

1. `frontend/src/pages/CheckPage.jsx` hiển thị ô nhập và nút.
2. `frontend/src/App.jsx`, hàm `onSubmit`, kiểm tra đầu vào rồi gọi API.
3. `frontend/src/api.js` gửi JSON `{url: ...}` tới backend; xử lý timeout/lỗi mạng.
4. `backend/app/middleware.py` giới hạn toàn bộ body, thời gian nhận body, Origin
   và thêm header bảo mật. Kẻ tấn công có thể bỏ qua giao diện nên lớp này cần thiết.
5. `backend/app/schemas.py` kiểm tra trường url bằng Pydantic. Nếu không hợp lệ,
   FastAPI trả 422 với một cấu trúc JSON thống nhất.
6. `backend/app/main.py`, `predict_url`, giữ một chỗ trong giới hạn hai công việc.
   Nếu hết chỗ, trả 503 ngay. Nếu có chỗ, đưa suy luận sang thread riêng.
7. `backend/app/service.py`, `predict`, gọi model đã được nạp lúc khởi động.
8. `backend/src/dtdlink_ml/predict.py` trích 36 đặc trưng và gọi `predict_proba`.
   Bốn module này được sao chép nguyên từ A2; không huấn luyện lại.
9. `backend/app/analysis.py` tạo phần giải thích từ parser/feature A2: chia đúng
   từng đoạn URL, chỉ ra bằng chứng, ý nghĩa và bước tiếp theo cho 11 quy tắc.
   Model, thứ tự 36 feature và điểm dự đoán không đổi. Backend trả thêm
   `url_parts`, `signals[].evidence` và `signals[].action`; URL không ghi vào log.
10. `Result.jsx` và `URLAnalysis.jsx` hiển thị bằng văn bản React an toàn. Host
    thật được làm nổi bật; người dùng có thể mở giải thích từng phần. Mỗi dấu
    hiệu có bằng chứng, “What this means” và “Your next step”. Ba mục ưu tiên
    hiện trước, các mục còn lại mở thêm nếu cần.

Ở ví dụ trên, host thật là `account-check.example`, không phải `paypal.com`.
Ứng dụng không mở cả hai địa chỉ để kiểm tra.

## 3. Điểm và confidence khác nhau thế nào?

Nếu model trả nguy hiểm = 0,2:

- Điểm nguy hiểm: 20%.
- Nhãn: Likely legitimate, vì 0,2 < 0,5.
- Confidence của nhãn benign: 1 - 0,2 = 80%.

80% là ước lượng của model cho lớp dự đoán, không phải bảo đảm URL an toàn 80%.
Dải 40–60% chỉ bật thêm thông báo thận trọng; chưa được hiệu chỉnh thống kê.

## 4. Vì sao cần thread và giới hạn số việc?

`async` không tự làm phép tính model chạy nhanh hơn. Nếu gọi trực tiếp hàm chậm
trên event loop, các yêu cầu khác phải chờ. Thread giúp event loop tiếp tục nhận
và xử lý yêu cầu như `/health`. Giới hạn hai việc tránh tích lũy công việc vô hạn.
Nếu khách hủy kết nối, công việc thật có thể vẫn đang chạy, nên chưa được trả chỗ
trống cho người khác. Đây là lý do slot được trả trong callback khi việc hoàn tất.

Đánh đổi: khi quá tải, một số người dùng thật nhận 503 và phải thử lại. Cơ chế này
không ngăn được tấn công làm nghẽn cả đường truyền mạng.

## 5. Hai biểu đồ trả lời câu hỏi khác nhau

- **Current result:** loại dấu hiệu nào xuất hiện trong URL vừa kiểm tra? Lọc mức
  chú ý và bấm một dấu hiệu để xem ý nghĩa.
- **Session:** điểm model của các lần kiểm tra khác nhau ra sao? Lọc nhãn và chọn
  số thứ tự một lần kiểm tra để xem chi tiết.

Lịch sử chỉ giữ số thứ tự, nhãn, điểm, thời gian và số dấu hiệu; không giữ URL hoặc
hostname. Dữ liệu nằm trong RAM của React và biến mất khi tải lại/xóa phiên.

## 6. Phần nào có thể điều chỉnh?

- Màu, khoảng cách, bố cục: `frontend/src/styles.css`.
- Dòng giải thích giao diện: các page/component React.
- Số công việc đồng thời: biến môi trường `DTDLINK_MAX_CONCURRENT` (1–8).
- Origin frontend: `DTDLINK_FRONTEND_ORIGIN`; phải khớp địa chỉ trình duyệt.
- Không tùy tiện đổi thứ tự feature, threshold, model hash hoặc chuẩn hóa URL
  trước model; các việc này ảnh hưởng hợp đồng A2 và cần đánh giá riêng.

## 7. Giới hạn cần nói trung thực khi trình bày

Model nhạy với cách viết URL, xác suất chưa hiệu chỉnh, và không phân biệt ba loại
nguy hiểm. Kiểm tra đầu vào giảm lỗi ứng dụng nhưng không sửa hoàn toàn điểm yếu
model. Kết quả audit hoặc vài test thành công không chứng minh an toàn tuyệt đối.
Section 2.8 chưa được làm thành nghiên cứu phòng vệ trước/sau; đừng trình bày như
đã hoàn thành. Minutes, chữ ký, đóng góp và video phải do nhóm xác nhận thực tế.

## 8. Cách trình bày phần phân tích chi tiết

Dùng ví dụ `https://paypal.com@account-check.example/login`:

1. Model vẫn dự đoán như A2, không học lại.
2. Host thật là `account-check.example`. Phần `paypal.com@` là thông tin
   đăng nhập trong cấu trúc URL, không xác định website được truy cập.
3. Mục **Hidden destination** chỉ đúng hai phần này, giải thích vì sao dễ
   nhìn nhầm và khuyên đối chiếu với địa chỉ lấy từ nguồn đáng tin.
4. Mục **Account-related terms** chỉ rõ `account` nằm trong host, `login`
   nằm trong path. Các từ này cũng có trong URL bình thường.
5. Bấm **Understand the parts of this URL** để xem protocol, host, path và
   các phần khác nếu có. Phần query chứa một URL khác không tự biến URL đó
   thành host hiện tại; ứng dụng không theo redirect.
6. Có thể dùng `https://example.com/` để minh họa giới hạn: model A2 có thể
   báo nguy hiểm dù 11 quy tắc không tìm thấy dấu hiệu. Giao diện nói rõ sự
   khác biệt này. Không được gọi các quy tắc là lý do thực sự của model.

Các đoạn decode chỉ giúp đọc ký tự mã hóa. Model luôn nhận chuỗi gốc. Base
domain chỉ là nhóm tên theo suffix list có sẵn, không phải xác nhận chủ sở hữu.
