# Rà soát tính đầy đủ của sơ đồ kiến trúc

Ngày rà soát: 24/09/2026. Phạm vi: tài liệu kiến trúc đích cho cả Assignment 2 và Assignment 3, không triển khai thêm ứng dụng.

## Kết luận

Bản trước có `data_loading.py` trong danh mục và quan hệ phụ nhưng không có node trong luồng sau train/validation/test CSV. Việc rút gọn tương tự khiến preprocessing, export, model metadata và explanation trông như bị bỏ qua. Đây là thiếu sót của cách thể hiện sơ đồ, không phải bằng chứng rằng các module tương lai đã tồn tại trong source.

Đã đưa các khâu trung gian quan trọng thành node, nối nguồn → xử lý → nơi sử dụng, đồng thời đồng bộ lại danh mục quan hệ hai chiều.

## Cơ sở đã đối chiếu

- `src/dtdlink_ml/data_audit.py:60`: đọc member trong ZIP, tạo/kiểm tra raw CSV; `run_audit()` ở dòng 477 ghi summary và các bằng chứng JSONL. Audit dùng `urllib.parse.urlsplit` nội bộ, không import `url_parser.py` của Stage 3.
- `src/dtdlink_ml/data_cleaning.py:161`: pipeline tự đọc raw, kiểm tra hash/schema, trim, mapping target, cách ly conflict, deduplicate và ghi cleaned/conflicts/audit. `load_and_prepare_dataset()` ở dòng 123 là helper trong file này, không phải module `data_loading.py` của kiến trúc đích; pipeline đầy đủ không gọi helper đó.
- `src/dtdlink_ml/feature_extraction.py:19`: import `ParsedURL, parse_url`; dòng 86 và 126 khai báo 36 features và 6 metadata. Dòng 273 mô tả single-URL extraction; dòng 303 đọc cleaned CSV, ghi feature table và audit. Labels được copy, không dùng để tính features.
- `src/dtdlink_ml/url_parser.py:31`: dùng public-suffix snapshot offline; `parse_url()` ở dòng 139 trả cấu trúc URL và issues, không truy cập website.
- Đọc code cells trong `notebooks/01_data_audit.ipynb` và `02_cleaning.ipynb`: chúng gọi đúng module tương ứng; không có training ngầm trong các notebook này.
- Đối chiếu inventory của `src/`, `tests/`, `notebooks/`, `data/`, `reports/`, `models/`, cùng import/entry point của tests. Bỏ qua cache, logs và thư viện phụ thuộc không cần cho kiến trúc sản phẩm.
- `ASSIGNMENT2_MASTER_PLAN.md:69`: có tên `data_loading.py` trong cấu trúc dự kiến. Stages 4–7 ở dòng 340–442 quy định EDA/split, training/validation, within-class clustering, final test, export/reload. Stage 9 ở dòng 463–484 mô tả React → FastAPI → pipeline A2.
- `PROJECT_CONTEXT.md`: scope offline, không mở URL, không lưu submitted URL/account/database; frontend React và backend FastAPI thuộc A3.
- `Week-12/Assessment/Assignment-3-Status.md`: workspace chưa có đầy đủ specification/rubric A3; không suy diễn rằng các tên route/module được đề xuất là yêu cầu chính thức.

## Bố cục hiện tại — 4 phần đã thống nhất

Theo yêu cầu giảm chia nhỏ, tài liệu hiện có đúng 4 sơ đồ liên tục:

1. Tổng quan: A2 tạo model → A3 dùng model.
2. A2: nguồn → audit → cleaning → features → EDA/split → từng CSV qua loader → preprocessing/training → final test → export. Clustering và Insights export là các nhánh cùng sơ đồ.
3. A3: mở website → navigation → form/hook → API → ML → response → UI. Startup và Insights ở hai bên, không cần chuyển qua sơ đồ khác.
4. Kiểm thử và bàn giao: test nối thành phần được kiểm tra; metrics/profiles nối report; README/deployment và hồ sơ nhóm phục vụ tái lập/bàn giao.

Danh mục 102 file/nhóm file được thu gọn, mở khi cần tra hoặc bấm node. Giữ nhãn nguồn CODE/PLAN/DESIGN; không thay đổi code ứng dụng. Số bước biểu thị thứ tự đọc, không phải trạng thái tiến độ. Các file phụ trợ vẫn được tra cứu qua quan hệ hai chiều; không ép tất cả thành bước runtime.

Đã bổ sung giải thích bằng lời ngay phía trên cả 4 sơ đồ, theo đúng số bước/file: đầu vào, xử lý, đầu ra và mục đích của từng đoạn. Phần chữ phân biệt loader với trainer, fit với transform, startup với request, và Insights với scan history. Có 20 liên kết từ đoạn giải thích đến node tương ứng, cùng liên kết quay lại phần đọc. Đã kiểm tra vị trí các phần giải thích, đích liên kết, render desktop và không tràn ngang nội dung chữ ở 390px; sơ đồ và danh mục giữ nguyên số lượng.

Lần chỉnh cách diễn đạt tiếp theo: giải thích công việc bằng tiếng Việt thông dụng trước, đưa tên file xuống dòng “Đối chiếu file”; dùng ví dụ học/bài luyện/bài thi để phân biệt train/validation/test. Giữ các điều kiện quan trọng: không học từ test, không huấn luyện lại mỗi request, clustering là nhánh riêng, Insights không phải scan history. Phân biệt test.csv chấm model với các file test kiểm tra chương trình. Không thay đổi sơ đồ hoặc source ứng dụng.

Theo yêu cầu mới nhất, cách diễn đạt trên được thay bằng danh sách đánh số khớp node: tên file được nêu ngay trong câu giải thích công việc và đầu ra, không còn dòng “Đối chiếu file” cuối đoạn. Hiện có 97 mục có liên kết đến node, gồm các nhánh A/B/C, S và I. Đã kiểm tra cả 97 đích tồn tại, thao tác nhảy đến bước 9 của A2 và bố cục chữ ở 390px. Vẫn giữ 4 sơ đồ chính; không đổi logic hay source ứng dụng.

## Lịch sử rà soát các đoạn nối (mã mục của bố cục cũ)

| Đoạn | Liên kết được làm rõ |
|---|---|
| 2A | ZIP → audit → raw → cleaning → cleaned; ghi riêng conflict quarantine và audit JSONL |
| 2B–2B2 | Feature table → loader → EDA notebook → split; không fit preprocessing trên toàn bảng EDA |
| 2C | Mỗi train/validation/test CSV → một lần gọi loader riêng → trainer hoặc final evaluator; không concat ba tập, không nạp test để chọn model |
| 2D | Loader → preprocessing → classification → selected pipeline và selection/policy JSON |
| 2E | Selected pipeline + test do loader trả + policy khóa → evaluate → metrics và error analysis |
| 2F | Train → loader → chọn một class/bỏ nhãn khỏi X → preprocessing riêng → clustering → profiles và clustering model |
| 2G | Selected pipeline + policy → export_model → final_pipeline.joblib và model_metadata.json; nối sang startup/reload tests |
| 3A–3D | index.html → React → router → AppShell → page; form → hook → validation → API hoặc ErrorNotice |
| 4A–4B | Startup qua bundle loader đọc cả model và metadata; route có schema và dependency lấy service đã nạp |
| 4C1–4C2 | Gọi parser/features và thực thi fitted pipeline là hai góc nhìn; explicit prediction → explain qua service → ghép response |
| 4D | Service → route → api.js → hook → ResultPanel theo chiều response, không phải request mới |
| 5A–5B | Metrics + profiles + audit → analytics export → JSON → insights service → route → api.js → page → charts |

## Cách hiểu các mũi tên

- `import / call`: bên gọi → module được gọi. Chẳng hạn trainer gọi loader và preprocessing.
- `data flow / return`: nơi tạo dữ liệu → nơi nhận dữ liệu. CSV → loader → preprocessing → trainer mô tả dữ liệu, không nói rằng CSV thực thi Python hoặc preprocessing tự gọi trainer.
- `read/write file`: đọc/ghi artifact theo nhãn. Khi đọc theo chiều dữ liệu, file có thể là đầu nguồn; một sơ đồ call có thể vẽ caller hướng tới file được đọc.
- Các sơ đồ con lặp lại cùng file theo vai trò/ngữ cảnh; không phải tạo thêm bản sao module hay train nhiều lần.
- Đánh giá dùng `transform/predict` của pipeline đã fit; không fit lại `preprocessing.py` bằng test. Runtime cũng không đọc CSV nghiên cứu hoặc train lại model.

## Phân biệt bằng chứng và thiết kế

`CODE` xác nhận file/code hoặc artifact đã đối chiếu. `PLAN` xác nhận tên nằm trong kế hoạch, không xác nhận implementation. `DESIGN` là module/contract đề xuất để hoàn thiện kiến trúc. Quan hệ của các phần tương lai là thiết kế đích, không phải import đã quan sát được.

Tại lần kiểm tra này, package hiện hữu gồm `__init__.py`, `data_audit.py`, `data_cleaning.py`, `url_parser.py`, `feature_extraction.py`. `data_loading.py` chưa tồn tại; `preprocessing.py`, `export_model.py`, `explain.py` và các file A3 là thiết kế tương lai. Không tạo những module đó trong lần chỉnh tài liệu này.

Các file cấu hình, manifests, notebook bổ trợ, README và tài liệu vẫn có trong danh mục/quan hệ. Không buộc chúng vào chuỗi xử lý một URL vì điều đó sẽ tạo thứ tự chạy không có thật. Danh mục có liên kết quay lại sơ đồ chứa file để người đọc tìm tiếp.

## Kiểm chứng tài liệu

- Inventory: không bỏ sót file Python/notebook hiện hữu trong các thư mục source/tests/notebooks; các đường dẫn CODE cụ thể đều tồn tại. Nhóm bốn audit JSONL được đối chiếu với inventory và hàm ghi trong source.
- Browser QA cho bố cục mới: 4 sơ đồ, 105 node hiển thị (có lặp file theo ngữ cảnh), 100 mũi tên có nhãn; danh mục 102 file/nhóm file.
- Kiểm tra tự động các node trung gian quan trọng và các cặp nối thiết yếu: CSV→loader; loader→preprocessing/caller; export→model/metadata; schema/dependency; UI validation; Insights.
- Kiểm tra riêng nhánh TEST, bước 11C: loader chỉ nối xuống final evaluator, không xuống trainer.
- Không lỗi JavaScript, liên kết hash bị thiếu, chữ vượt ô/SVG, chữ đè nhau hoặc cạnh xuyên ô không liên quan. Filter và click node mở đúng hàng trong danh mục.
- Kiểm tra ở 390px: không tràn ngang toàn trang; các sơ đồ rộng có vùng cuộn riêng để giữ chữ đọc được.
- Đã xem ảnh render của các sơ đồ quan trọng, gồm split/loader, preprocessing/training và inference/explanation.

Các kiểm tra này xác nhận tài liệu và quan hệ thiết kế, không thay thế unit/integration tests cho code chưa triển khai. Không chạy lại dataset lớn, huấn luyện model hoặc tuyên bố một backend/frontend đã hoạt động.
