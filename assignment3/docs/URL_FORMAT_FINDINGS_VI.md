# Kiểm tra lỗi nhạy định dạng URL — DTDLINK A3

Hoàn tất kiểm chứng ngày 6/11/2026 (Australia/Melbourne).

**Kết luận: chưa thay model đang chạy.** Đã kiểm chứng nguyên nhân, tạo quy tắc
biểu diễn nhất quán và huấn luyện các model A3 riêng. Có bản cải thiện mạnh chỉ
số tổng, nhưng chưa bản nào đạt đồng thời yêu cầu về URL trang chủ và recall.
Không dùng whitelist, không đổi nhãn, không tăng threshold, không làm đẹp demo.

## 1. Đây là lỗi ở đâu?

Luồng React → JSON → FastAPI → trích feature → model → nhãn hoạt động đúng.
React gửi nguyên `draft`; `new URL()` chỉ kiểm tra định dạng, không sửa chuỗi.
API, service và model trả cùng xác suất cho URL đầy đủ. Nhãn 1 vẫn là nhóm gộp
phishing/malware/defacement. Confidence là p hoặc 1-p đúng theo lớp dự đoán.
URL thiếu scheme nhận 422 ở API; các điểm 18,66%/5,82% là kiểm tra trực tiếp model,
không phải đầu vào đã được API chấp nhận.

Tái lập ví dụ: `https://www.google.com/` 97.22%,
`www.google.com/` 18.66%; `https://github.com/`
95.43%, `github.com/` 5.82%.
Tên quen thuộc không chứng minh tình trạng an toàn của URL hiện tại.

## 2. Nguyên nhân tìm được

Train có **92,34% benign không có scheme**, trong khi defacement **100% có
HTTP**, malware 95,24% có HTTP(S), phishing khoảng 26,74% có HTTP(S). Validation
cũng lệch: benign 88,72% không có scheme; defacement vẫn 100% HTTP. HTTPS chỉ có
0,43% benign train và 0,31% benign validation.

Thêm scheme làm đổi đồng thời `has_scheme`, `parse_issue_count`, `uses_https`,
`url_length` và `special_character_count`. Hai importance lớn nhất của RF là
`parse_issue_count` 21,01% và `has_scheme` 17,96%; đây là importance theo impurity,
không phải chứng minh nhân quả. Các can thiệp một feature và phép so sánh định
dạng củng cố việc model dùng tín hiệu định dạng. Không thể quy hết cho HTTPS.

Ngoài scheme, root path và thông tin quá thô vẫn là vấn đề. Model RF dùng 36
con số; **6.570 vector feature train chứa cả hai nhãn**. Theo bản biểu diễn trung
lập scheme, train có 2,793 định danh
URL chứa cả hai nhãn. Điều này không tự chứng minh nhãn sai: HTTP/HTTPS cũng có
thể là tài nguyên khác nhau. Không có nhãn nào bị xoá/đổi để làm đẹp phép đo.
Không có thông tin thời điểm/nguồn thu thập đủ để xác minh toàn bộ nhãn hiện tại.

## 3. Cách xử lý đã thực hiện trong thử nghiệm

Một hàm dùng chung cho train và suy luận tạo **bản phụ cho model**: thống nhất
scheme, host chữ thường, root path rỗng thành `/`, bỏ cổng mặc định theo protocol
gốc. Giữ `www`, thông tin trước `@`, cổng riêng, path/query phân biệt hoa thường,
thứ tự tham số, encoding, fragment và dấu `?`/`#` rỗng. Raw URL và cảnh báo HTTP
vẫn dùng nguyên chuỗi người dùng. Đây không phải bỏ scheme trước model A2 cũ.

Đã thử RF với biểu diễn mới; TF-IDF ký tự + logistic regression + 36 phép đo;
kiểm tra hội tụ; RF riêng cho root path; và text-only không chuẩn hoá L2 để giảm
proxy độ dài. Hướng cuối loại prefix protocol hằng số khỏi **text view** ở cả
train và suy luận, không sửa URL hiển thị. Toàn bộ các hướng đều nằm riêng A3.

## 4. So sánh trước/sau trên cùng tập validation

Cùng **128.373 URL hợp lệ theo chính sách A3**, gồm 85.656 benign và 42.717
dangerous. URL thiếu scheme trong dataset được hoàn thiện để mô phỏng dạng API.
Đây là giả định chuyển nhãn giữa cách ghi, không phải kiểm tra website thực tế.
Nhóm trang chủ không query có 14.455 URL: 8.497 benign và 5.958 dangerous.

| Bản kiểm tra | FPR toàn tập | Recall dangerous | FPR trang chủ | Recall dangerous trang chủ |
|---|---:|---:|---:|---:|
| A2 đang chạy, URL dạng API | 88.00% | 99.21% | 100.00% | 100.00% |
| A3 text + 36 phép đo | 11.36% | 92.13% | 38.13% | 90.80% |
| A3 chuyên gia riêng cho root path | 9.43% | 87.45% | 19.30% | 57.74% |
| A3 text-only, không L2 | 12.64% | 87.33% | 36.54% | 83.59% |

FPR = số benign bị báo dangerous / tổng benign. Recall dangerous = số dangerous
nhận ra / tổng dangerous. Bản text giảm FP từ 75,373 xuống
9,728, nhưng FN tăng từ 338 lên
3,362. Đây là đánh đổi thật, không được giấu.

Kiểm tra riêng **38.432 URL vốn đã có HTTP(S)**, không thêm scheme:
A2 FPR 35.67%, recall 98.84%; bản text FPR
6.74%, recall 92.61%.
Do đó cải thiện tổng không chỉ do cách tạo URL hoàn thiện.

Để đối chiếu, A2 trên **chuỗi gốc** của cùng tập đủ điều kiện có FPR
8.36%, recall 93.86%. Đây là định dạng dataset, không phải
định dạng nhập đầy đủ mà ứng dụng yêu cầu. Không trộn hai baseline này.

## 5. Độ ổn định và chống rò rỉ

Trên 9.277 cặp biến thể định dạng từ mẫu một URL/domain validation (4.000 domain,
cân bằng hai lớp), A2 đổi nhãn 12 cặp; bản text đổi 0 cặp. Thay cách ghi
không-scheme/đầy đủ làm A2 đổi 2.015/3.366 cặp, bản text đổi 0. HTTP/HTTPS là phép
thử transport riêng, không khẳng định cùng tài nguyên. Mẫu hex-case chỉ có một
cặp nên không thể kết luận rộng cho mọi kiểu encoding.

Chỉ train được dùng để học: 381.494 URL hợp lệ; 3.338 URL bị chính sách A3 loại.
Validation còn 128.373/129.332 URL, loại 959 URL và ghi rõ lý do. Vocabulary, IDF,
scaler đều chỉ fit train. Giao domain giữa train/validation/test bằng 0, kể cả
chuẩn IDNA trong group metadata. Không chèn demo vào train. GitHub vốn ở train,
Google vốn ở validation; các demo không phải holdout độc lập.

Không dùng outcome test A2 để train, điều chỉnh, chọn hoặc đánh giá model A3.
Chỉ đọc checksum để bảo vệ file A2 và group metadata để kiểm tra rò rỉ.
Validation đã tái sử dụng để phát triển nên số liệu trên không phải đánh giá
cuối độc lập hoặc bảo đảm kết quả ngoài đời.

## 6. Quyết định và giới hạn

**Giữ nguyên A2 trong ứng dụng.** Bản text qua tiêu chí tổng ban đầu nhưng vẫn
báo sai 38,13% benign trang chủ và vẫn cho điểm cao ở hai ví dụ người dùng.
Các thử nghiệm nhắm vào nhóm này chưa đạt đồng thời FPR≤20% và recall≥80%
trên trang chủ, cùng recall≥90% toàn tập. Không quảng bá lỗi đã được sửa xong.

Không thay hash/metadata/API example của model chạy vì không có promotion.
Giao diện hiện tại, giải thích URL và các biện pháp bảo mật giữ nguyên. ZIP bổ
sung code/evidence nghiên cứu; cache dữ liệu và model ứng viên không đóng gói.
Các model ứng viên vẫn giữ trong thư mục `experiments/url_format/artifacts/`.

Muốn tiến tiếp có cơ sở cần dữ liệu URL đầy đủ, nhãn có nguồn gốc/thời điểm đáng
tin, bao phủ cả benign và dangerous root/path, và đánh giá theo domain trên một
tập mới độc lập. Không thể lấy tên miền phổ biến hoặc vài demo làm nhãn an toàn.
Không có website đích nào được mở, DNS tra cứu hay dịch vụ phân tích ngoài được gọi.
Đọc RFC là đọc tài liệu cú pháp, không phải gửi URL kiểm tra ra ngoài.

## 7. Tệp để kiểm chứng và học lại

- `experiments/url_format/README.md`: lệnh tái lập và định nghĩa population.
- `results/*scheme*.csv`: phân bố train/validation theo nhãn.
- `results/candidate-comparison.csv`: mọi lượt thử, gồm các bản không đạt.
- `results/promotion-decision.json`: quyết định không tích hợp.
- `results/a2-preservation-after.json`: checksum các file A2 được bảo vệ.
- `results/baseline-application-trace.json`, `frontend-trace.json`: kiểm tra luồng.
- `results/eligibility-and-domain-audit.json`: loại trừ và domain.
- `results/root-path-audit.json`, `canonical-identity-audit.json`: kiểm tra bổ sung.

Quy tắc hoa/thường, root path và cổng mặc định tham khảo RFC 3986 §6.2.2–6.2.3:
https://www.rfc-editor.org/rfc/rfc3986#section-6.2.3. Trung lập protocol là lựa chọn
mô hình riêng, không phải khẳng định HTTP/HTTPS tương đương về bảo mật/tài nguyên.

## 8. Thử model đọc riêng từng phần URL — 6/11/2026

Đã huấn luyện thêm **4 model** với các nhóm đặc trưng riêng cho domain,
subdomain, phần trước `@`, path, query, fragment và port. Cùng một chữ nằm ở
domain thật và ở query được đưa vào hai nhóm khác nhau. Dùng chung cách tạo
feature khi train và khi dự đoán; threshold vẫn 0,5. Không thêm whitelist,
chèn demo vào train, đổi nhãn hoặc dùng kết quả test A2.

| Model | FPR toàn validation | Recall dangerous | FPR trang chủ | Recall dangerous trang chủ |
|---|---:|---:|---:|---:|
| Preview text hiện tại | 11,36% | 92,13% | 38,13% | 90,80% |
| Tách phần, balanced | 6,59% | 86,04% | 20,01% | 77,12% |
| Tách phần, trọng số dangerous 3 | 9,06% | 88,81% | 30,00% | 84,49% |
| Tách phần, trọng số dangerous 5 | 12,35% | 91,19% | 43,78% | 90,35% |
| Tách phần + ngữ cảnh trang chủ | 10,77% | 90,41% | 33,58% | 88,44% |

Cùng 128.373 URL validation, trong đó 85.656 benign và 42.717 dangerous.
Nhóm trang chủ có 8.497 benign, 5.958 dangerous. FPR là tỷ lệ benign báo nhầm;
recall là tỷ lệ dangerous nhận ra. Các nhóm có sẵn scheme cũng được lưu riêng
trong JSON kết quả, không trộn với baseline chuỗi gốc A2.

**Không thay model của cả ứng dụng chính lẫn preview.** Bản balanced giảm báo
nhầm nhưng bỏ sót 13,96% dangerous toàn tập; bản có ngữ cảnh vẫn báo nhầm 33,58%
benign trang chủ, vượt mức 20% đã đặt trước. So với preview, bản ngữ cảnh giảm
507 báo nhầm nhưng tăng 734 dangerous bị bỏ sót. Các tiêu chí là điều kiện
thử nghiệm của dự án, không phải tiêu chuẩn chứng nhận an toàn.

Sau khi quyết định theo validation, mới kiểm tra demo: bản ngữ cảnh cho Google
60,21%, GitHub 95,06% điểm dangerous, nên vẫn báo Potentially dangerous. Các
điểm này chưa được hiệu chuẩn, không phải xác suất website thực sự gây hại.
Tách vị trí chữ chưa đủ để giải quyết hai ví dụ này.

Giới hạn cụ thể: chỉ **2 URL train chứa phần trước `@`** nên không học được bộ
từ cho phần đó; chỉ còn các cờ cấu trúc. Parser offline dùng toàn hostname làm
fallback nếu không nhận ra đuôi domain; dấu `?`/`#` rỗng riêng lẻ không tạo
feature khác biệt trong bản tách phần. Không sửa parser A2. Cả bốn model hội tụ,
đều không đổi nhãn trên 9.277 cặp định dạng, nhưng mẫu hex-case chỉ có một cặp.

Đã nạp lại các artifact, tính lại dự đoán cho toàn bộ validation và so với số
đã lưu; thêm 1.000 URL ngẫu nhiên/model qua giao diện dự đoán raw URL, cùng
kiểm tra confusion counts độc lập. Code, hash và kết quả ở
`experiments/url_format/field_roles/`. Validation đã được dùng nhiều lần để
phát triển, nên chưa thể coi đây là số đo cuối độc lập.

Hướng tiếp theo có cơ sở hơn là cải thiện dữ liệu và nhãn: đủ URL đầy đủ của
cả benign/dangerous, trang chủ/path, nguồn và thời điểm rõ ràng; sau đó đánh giá
trên domain mới độc lập. Thử nghiệm này không chứng minh mọi model URL-only
đều không thể cải thiện. Tuy nhiên, chưa có bằng chứng để thay model đang chạy
hoặc khẳng định đã sửa xong lỗi báo nhầm.
