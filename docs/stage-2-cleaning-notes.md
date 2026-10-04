# Stage 2 — Ghi chú cleaning dữ liệu DTDLINK

## 1. Mục tiêu

Stage 2 tạo một bảng dữ liệu đáng tin cậy hơn để dùng cho parser, feature và mô
hình ở các Stage sau. Cleaning không cố gắng xác định URL có an toàn hay không.
Nó chỉ sửa những lỗi định dạng có căn cứ, xử lý mâu thuẫn và ngăn bản sao làm
sai lệch dữ liệu.

Kiến thức chính thuộc **Week 4** (cleaning, missing values, outliers và bảo toàn
dữ liệu) và **Week 5** (ETL, pipeline có thể chạy lại và chống leakage).

## 2. Luồng dữ liệu

```text
data/raw/malicious_phish.csv
        |
        v
kiểm tra hash + schema + label
        |
        v
trim khoảng trắng ở hai đầu URL
        |
        v
cách ly URL có nhãn mâu thuẫn
        |
        v
loại bản sao URL + type
        |
        v
thêm target 0/1
        |
        +--> data/interim/malicious_phish_cleaned.csv
        +--> reports/cleaning/conflicting_records.csv
        +--> reports/cleaning/cleaning_audit.json
```

File raw luôn được đọc, không bao giờ bị ghi đè.

## 3. Ý nghĩa từng quy tắc

### Kiểm tra đầu vào

Pipeline chỉ chấp nhận đúng hai cột `url`, `type` và bốn nhãn `benign`,
`phishing`, `malware`, `defacement`. SHA-256 phải giống Stage 1. Nếu nguồn thay
đổi, pipeline dừng để tránh tạo kết quả từ một dataset không còn giống báo cáo.

### Trim URL

`strip()` chỉ bỏ khoảng trắng ở đầu và cuối chuỗi. Nó không lowercase, không xóa
query, không giải mã URL và không sửa khoảng trắng bên trong. Có 7 URL được sửa
và không có hàng nào bị xóa.

### Cách ly mâu thuẫn

Sáu URL xuất hiện với cả nhãn benign và phishing. Vì cùng một chuỗi đầu vào
không thể có hai đáp án xác định, pipeline đưa toàn bộ 12 hàng vào file riêng.
“Cách ly” nghĩa là không dùng để học mô hình nhưng vẫn giữ lại để kiểm tra.

### Loại bản sao

Một bản sao chính xác có cùng `url` và `type`. Pipeline giữ bản ghi xuất hiện
đầu tiên và loại 10.066 lần lặp sau đó. Quy tắc này giảm việc một URL bị tính
trọng số nhiều lần và giảm nguy cơ cùng mẫu lọt vào nhiều tập dữ liệu.

### Giữ các bất thường khác

Unicode, ký tự điều khiển, URL rất dài và URL khó parse không tự động bị xóa.
Chúng có thể là tín hiệu bảo mật. Stage 3 sẽ xây parser có khả năng xử lý và kiểm
thử các trường hợp này.

## 4. Kết quả trước và sau

| Chỉ số | Raw | Cleaned |
|---|---:|---:|
| Tổng hàng | 651.191 | 641.113 |
| URL duy nhất | 641.119 | 641.113 |
| Benign / target 0 | 428.103 | 428.074 |
| Potentially dangerous / target 1 | 223.088 | 213.039 |
| URL mâu thuẫn | 6 | 0 |
| Bản sao chính xác dư | 10.066 | 0 |

Malware giảm mạnh từ 32.520 xuống 23.645 vì Stage 1 đã phát hiện bản sao tập
trung ở lớp này. Đây là thay đổi dữ liệu có lý do, không phải bằng chứng rằng
malware ít phổ biến trên Internet.

## 5. Cách đọc code

Code chính nằm trong `src/dtdlink_ml/data_cleaning.py`:

- `validate_raw_contract()` kiểm tra dữ liệu đầu vào.
- `trim_url_edges()` thực hiện một sửa đổi có giới hạn.
- `separate_label_conflicts()` tách các hàng không có đáp án rõ ràng.
- `remove_exact_duplicates()` giữ lần xuất hiện đầu tiên.
- `run_cleaning_pipeline()` gọi các bước theo đúng thứ tự và ghi output.

Các hàm nhận một bảng và trả lại bảng mới. Cách viết này tránh sửa âm thầm bảng
đầu vào và giúp từng quy tắc có thể được test riêng.

## 6. Cách chạy và kiểm tra

Từ thư mục dự án:

```bash
.venv/bin/python src/dtdlink_ml/data_cleaning.py
PYTHONPATH=src .venv/bin/python -m pytest -q
```

Pipeline đạt yêu cầu tái lập khi hai lần chạy cho cùng SHA-256 của cleaned CSV,
conflict CSV và audit JSON. Audit hiện lưu số hàng sau mỗi quy tắc để giải thích
mọi thay đổi.

## 7. Phần có thể điều chỉnh sau khi có lý do

- Cách xử lý conflict có thể thay đổi nếu xuất hiện nguồn nhãn đáng tin cậy hơn.
- Khóa dedup có thể mở rộng nếu dự án định nghĩa được canonical URL an toàn.
- Không nên lowercase, xóa query hoặc chuẩn hóa scheme nếu chưa đo ảnh hưởng;
  các thao tác đó có thể phá hủy tín hiệu bảo mật.

Stage 2 chưa chia train/test, chưa tạo feature và chưa train mô hình. Domain-aware
split vẫn thuộc Stage 4, còn URL parser và feature extractor thuộc Stage 3.
