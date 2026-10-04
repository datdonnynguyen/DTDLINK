# DTDLINK — Báo cáo audit dữ liệu gốc (Stage 1)

Ngày: 15/09/2026 (Australia/Melbourne). Phạm vi: toàn bộ malicious_phish.csv, không lấy mẫu để tính số liệu.

**Kết luận:** Dữ liệu đủ để xác định target, nhưng chưa sẵn sàng training. Có mất cân bằng lớp, bản sao dư tập trung ở malware, 6 URL xung đột nhãn và khác biệt định dạng rất mạnh giữa các lớp. Sau audit, người dùng đã chọn phương án B: `benign` đối lập với `potentially_dangerous`.

## 1. Nguồn và cách kiểm tra lại

- Archive: `Week-08/Assessment/Basic_Datasets.zip`.
- Chỉ giải nén member: `Basic_Datasets/Phishing URL Detection/malicious_phish.csv`.
- Bản sao nguyên byte: `data/raw/malicious_phish.csv` (45,664,439 bytes).
- SHA-256 CSV: `d83ce942075dd63ed4d11560cfdcd9d512caa3d680e292f22cab484e8f074d01`.
- SHA-256 archive: `ed776a8d00acbd33970ed0b425286466786c4b35006d348a621ec64f9b62206e`.
- Thời điểm chạy UTC được lưu trong `summary.json`; đây không phải ngày thu thập URL.
- Môi trường: Python 3.9.6, pandas 2.2.3.
- Script: `src/dtdlink_ml/data_audit.py`; notebook: `notebooks/01_data_audit.ipynb`.
- Chạy lại từ thư mục dự án: `.venv/bin/python src/dtdlink_ml/data_audit.py`.
- Script chỉ tạo/cập nhật bằng chứng audit, kiểm tra hash trước khi dùng raw hiện có; nếu raw khác archive thì dừng, không ghi đè.

Không truy cập website, không tra cứu mạng, không xóa/sửa hàng, không gộp nhãn, không chia tập và không training. Các phép trim/parse là phép đo tạm thời; không tạo dataset đã cleaning.

## 2. Kích thước, schema và đơn vị quan sát

**651,191 hàng dữ liệu × 2 cột**, không tính header. Mỗi hàng là một bản ghi URL kèm nhãn do dataset cung cấp; không có khóa định danh duy nhất.

| Cột | Kiểu được nạp | Ý nghĩa |
|---|---|---|
| url | pandas string | Chuỗi URL đầu vào; chưa phải bảng feature số |
| type | pandas string | Nhãn phân loại dạng categorical về mặt ý nghĩa |

CSV không chứa khai báo kiểu dữ liệu. Script chủ động đọc cả hai cột dưới dạng string, giữ nguyên chuỗi rỗng và các token như NA thay vì tự đổi thành null. Tất cả 651,191 bản ghi được csv.reader xác nhận có đúng 2 trường.

## 3. Label và cân bằng lớp

| Label | Số hàng gốc | Tỷ lệ | Ý nghĩa theo tên nhãn |
|---|---:|---:|---|
| benign | 428,103 | 65.74% | Được nguồn gán là lành tính; không phải bảo đảm an toàn |
| defacement | 96,457 | 14.81% | Liên quan website bị thay đổi nội dung trái phép |
| malware | 32,520 | 4.99% | Liên quan phần mềm độc hại |
| phishing | 94,111 | 14.45% | Lừa đảo nhằm lấy thông tin |

Đây là phân bố hàng gốc, có tính các bản sao. Không coi tỷ lệ này là tỷ lệ URL nguy hiểm trên Internet. Benign nhiều hơn malware khoảng 13,16 lần. Nếu chỉ luôn đoán benign, accuracy trên bảng bốn lớp này đã là 65,74%; không thể dùng accuracy riêng để chứng minh phát hiện phishing tốt.

## 4. Dữ liệu thiếu

Cả hai cột đều có **0 null, 0 chuỗi rỗng, 0 ô chỉ chứa khoảng trắng**, và 0 token giống dữ liệu thiếu trong danh sách kiểm tra (`na`, `n/a`, `null`, `none`, `nan`, `unknown`, `?`, so sánh sau trim và lowercase tạm thời).

Có **7 URL có khoảng trắng đầu/cuối**, không có label dạng này. Nếu chỉ trim tạm để so sánh thì không xuất hiện nhóm URL trùng mới. Không thiếu ô không có nghĩa mọi URL đều hợp lệ hay label đều đúng.

## 5. Dòng trùng và URL trùng

So sánh **chuỗi chính xác**, có phân biệt chữ hoa/thường, giao thức, path và query. Chưa canonicalize URL.

| Phép kiểm tra | Số nhóm trùng | Tổng hàng nằm trong nhóm trùng | Bản sao dư sau lần xuất hiện đầu |
|---|---:|---:|---:|
| Cả hàng (url + type) | 2,201 | 12,267 (1.88%) | 10,066 (1.55%) |
| Chỉ url | 2,207 | 12,279 (1.89%) | 10,072 (1.55%) |

Có 641,125 cặp URL–label khác nhau và 641,119 chuỗi URL khác nhau. Ví dụ một nhóm xuất hiện 3 lần thì có 3 hàng bị ảnh hưởng nhưng chỉ 2 bản sao dư. Đây là phép đếm, chưa loại hàng nào.

| Class | Bản sao dư của cả hàng | Tỷ lệ trong class |
|---|---:|---:|
| benign | 23 | 0.01% |
| defacement | 1,149 | 1.19% |
| malware | 8,875 | 27.29% |
| phishing | 19 | 0.02% |

Malware chiếm 8.875/10.066 bản sao dư (88,17%). Vì vậy deduplication sau này sẽ làm thay đổi phân bố lớp đáng kể, đặc biệt ở malware. Không cộng số dòng trùng và URL trùng vì hai phép đếm chồng lấp.

## 6. URL mâu thuẫn label

**6 URL, 12 hàng** (0,00184% tổng hàng); mỗi URL có một hàng benign và một hàng phishing. Danh sách đầy đủ:

| URL nguyên văn (không phải link) | Bản ghi benign | Bản ghi phishing |
|---|---:|---:|
| `memory.loc.gov/ammem/ccmphtml/colahome.html` | 181227 | 609890 |
| `routesinternational.com/air.htm` | 208440 | 612942 |
| `en.wikipedia.org/wiki/E-book` | 213052 | 616867 |
| `en.wikipedia.org/wiki/Desktop_publishing` | 259610 | 616833 |
| `groups.yahoo.com/group/Band-in-a-Box/` | 275789 | 625974 |
| `ebookstore.sony.com/reader/` | 328666 | 616943 |

Số bản ghi bắt đầu từ 1 sau header. Không đồng nhất số này với dòng vật lý của file vì CSV có thể chứa ký tự xuống dòng bên trong một trường.

Tỷ lệ nhỏ nhưng cùng đầu vào không thể có hai đáp án xác định trong mô hình chỉ đọc URL. Không thể kết luận nhãn nào đúng từ tên miền. Có thể do nguồn gán nhãn hoặc thời điểm khác nhau, nhưng file không có bằng chứng xác định nguyên nhân. Cần thống nhất quy tắc xử lý tại Stage 2; chưa tự giữ hàng đầu, bỏ xung đột hoặc đổi nhãn.

## 7. Ví dụ minh họa từng class

Chọn xác định được: trong mỗi lớp, lấy URL có độ dài gần Q1, median, Q3 nhất; nếu bằng nhau chọn bản ghi xuất hiện trước, không lặp bản ghi. Đây là minh họa độ dài thường gặp, không phải mẫu ngẫu nhiên đại diện toàn bộ nội dung lớp. Nhãn được trích nguyên từ nguồn, chưa được xác thực độc lập.

| Class | Bản ghi | Độ dài | Vị trí độ dài | URL nguyên văn, không truy cập |
|---|---:|---:|---|---|
| benign | 3 | 31 | Q1 | `bopsecrets.org/rexroth/cr/1.htm` |
| benign | 8 | 46 | Q2 | `yourbittorrent.com/?q=anthony-hamilton-soulife` |
| benign | 221 | 71 | Q3 | `elliscountydivorcelawyer.com/ellis-county-post-divorce-modification.htm` |
| defacement | 69 | 55 | Q1 | `http://www.musimagen.com/lista_socios.php?letra=\303%91` |
| defacement | 138 | 81 | Q2 | `http://www.paoarapanui.cl/index.php?option=com_contact&view=contact&id=1&Itemid=6` |
| defacement | 1616 | 105 | Q3 | `http://gbcmonroe.org/index.php?option=com_jevents&task=week.listevents&year=2013&month=02&day=3&Itemid=67` |
| malware | 102868 | 33 | Q1 | `magedecorland.mediadevstaging.com` |
| malware | 1529 | 49 | Q2 | `socialsocietyedu.com/components/com_wa/config.bin` |
| malware | 441 | 76 | Q3 | `http://grasslandhotel.com.vn/index.php/component/djcatalog2/items/6-services` |
| phishing | 503 | 25 | Q1 | `ammmmazonm.temp.swtest.ru` |
| phishing | 1304 | 35 | Q2 | `prosdyuqnsdwxm.intend-incredible.ru` |
| phishing | 875 | 49 | Q3 | `account-security-centre20181712.000webhostapp.com` |

## 8. Định dạng URL và rủi ro học sai dấu hiệu

| Class | Không có scheme dạng :// | Bắt đầu http:// | Bắt đầu https:// | Trung vị độ dài |
|---|---:|---:|---:|---:|
| benign | 392,725 (91.74%) | 33,428 (7.81%) | 1,950 (0.46%) | 46 |
| defacement | 0 (0.00%) | 96,457 (100.00%) | 0 (0.00%) | 81 |
| malware | 1,210 (3.72%) | 24,546 (75.48%) | 6,764 (20.80%) | 49 |
| phishing | 69,257 (73.59%) | 17,886 (19.01%) | 6,966 (7.40%) | 35 |

Phishing có 2 URL dùng scheme dạng :// khác http/https. Các cột trên không phải phép kiểm tra URL hợp lệ đầy đủ.

**Rủi ro cao:** 100% defacement có http://, trong khi 91,74% benign không ghi scheme. Mô hình có thể học cách nguồn dữ liệu định dạng URL. Chưa thể khẳng định nguyên nhân là nguồn thu thập vì không có metadata. Sau này cần kiểm tra độ nhạy với định dạng và lựa chọn feature; không tự xóa giao thức trong audit.

Một kết quả đáng chú ý khác: trung vị độ dài phishing là 35 ký tự, thấp hơn benign (46). Giả định “URL dài hơn chắc chắn phishing” không được dữ liệu này hỗ trợ; độ dài chỉ là một tín hiệu kết hợp.

| Dấu hiệu cần xem xét | Số hàng (các mục có thể chồng lấp) |
|---|---:|
| Có bất kỳ khoảng trắng | 308 (0.05%) |
| Có ký tự điều khiển | 88 (0.01%) |
| Có ký tự ngoài ASCII | 921 (0.14%) |
| Dài hơn 2.048 ký tự | 2 (0.00%) |
| Lỗi/thiếu hostname trong phép parse chẩn đoán | 14 (0.00%) |

Parse chẩn đoán sử dụng urllib.parse.urlsplit, tạm thêm // khi chuỗi thiếu scheme; có 13 ValueError và 1 trường hợp không có hostname, đều thuộc phishing. Không coi tất cả URL còn lại là hợp lệ: parser này không xác thực đầy đủ cú pháp hoặc khả năng truy cập. Không coi Unicode hoặc URL dài là lỗi mặc định. Các bằng chứng chi tiết ở `anomaly_records.jsonl`, với ký tự điều khiển được JSON escape để đọc an toàn.

Có 196.520 hostname không rỗng theo phép parse chẩn đoán; 499.836 hàng có hostname xuất hiện nhiều lần. Host lớn nhất có 13.206 hàng. Đây là dấu hiệu rủi ro leakage nếu chia ngẫu nhiên từng hàng. Chưa tính registrable domain; không phải kết quả kiểm tra domain leakage chính thức và chưa có train/test split.

## 9. Đánh giá chất lượng và hành động đề xuất (chưa thực hiện)

| Vấn đề | Mức độ | Độ chắc chắn và hệ quả | Bước xử lý sau khi chốt target |
|---|---|---|---|
| Định dạng gắn chặt với class | Cao | Chắc chắn về số đếm; nguồn gây lệch chưa rõ. Có thể tăng điểm giả tạo và giảm khả năng dùng ngoài dataset. | Kiểm tra định dạng/feature và khả năng khái quát hóa. |
| Dòng trùng, nhất là malware | Cao | Đã đối chiếu độc lập. Tăng trọng số một số mẫu; có thể rò rỉ qua tập kiểm tra. | Quy tắc dedup trước split, ghi số hàng trước/sau. |
| 6 URL mâu thuẫn nhãn | Vừa | Chắc chắn về mâu thuẫn; chưa biết nhãn đúng. Tạo đáp án bất nhất. | Quyết định xử lý có tài liệu, không tùy tiện lấy hàng đầu. |
| Mất cân bằng lớp | Cao đối với đánh giá | Số liệu chắc chắn; mức khó học chỉ biết sau thử nghiệm. | Theo dõi recall/F1 của target, các URL potentially dangerous bị bỏ sót, và kết quả theo raw `type`. |
| Host lặp nhiều | Cao nếu split ngẫu nhiên | Chẩn đoán sơ bộ, chưa dùng registrable domain. Có thể học thuộc host. | Xây grouping và kiểm tra leakage tại Stage 4. |
| URL có ký tự lạ/lỗi parse | Vừa | Các dấu hiệu chắc chắn, không đồng nghĩa tất cả là dữ liệu sai. | Parser có kiểm thử và quy tắc cleaning bảo toàn tín hiệu. |
| Không có ngày thu thập, nguồn/độ tin cậy nhãn | Giới hạn quan trọng | Hai cột không cho xác định độ mới, drift theo thời gian hay tính đúng của nhãn. | Tìm provenance được cung cấp trong tài liệu trước khi đưa tuyên bố về dữ liệu hiện tại. |

Không có lịch sử để kiểm tra thay đổi phân bố hoặc bất thường theo thời gian. Ngày file/archive và ngày audit không được dùng thay cho ngày thu thập.

## 10. Các lựa chọn target và quyết định đã ghi nhận

Tất cả số dưới đây tính trên hàng gốc, chưa xử lý trùng/xung đột.

| Lựa chọn | Quy mô | Ưu điểm | Hạn chế và ý nghĩa đầu ra |
|---|---|---|---|
| A — benign vs phishing | 522.214 hàng: 428.103 benign và 94.111 phishing; 128.977 hàng thuộc hai loại khác nằm ngoài phạm vi đề xuất | Khớp tên Phishing URL Detection, câu hỏi và UI đã cam kết; dễ giải thích | Không học nhận diện malware/defacement; benign chiếm 81,98%, phishing 18,02%; không được diễn giải kết quả như phát hiện mọi nguy hiểm |
| B — benign vs potentially dangerous | 651.191 hàng: 428.103 benign vs 223.088 thuộc ba loại còn lại | Bao quát ba nhóm nguy hiểm, vẫn chỉ có hai lớp | Không phân biệt phishing với malware/defacement; phải điều chỉnh cách diễn đạt đầu ra và ghi nhận thay đổi phạm vi với nhóm |
| C — bốn lớp | 651.191 hàng; giữ bốn nhãn gốc | Giữ thông tin, chỉ rõ loại dự đoán | Khó đánh giá/giải thích hơn, malware ít và nhiều bản sao; defacement/malware có thể khó suy ra chỉ từ URL; cần thống nhất UI và phạm vi |

**Quyết định sau audit:** người dùng chọn B làm target chính. Mapping dự kiến là
`benign -> 0` và `phishing|malware|defacement -> 1`
(`potentially_dangerous`). Quyết định này không thay đổi các số liệu audit phía
trên và chưa được áp dụng vào CSV. Chi tiết tại `docs/decisions.md`.

Vì đây là mở rộng phạm vi phishing-only của Assignment 1, nhóm còn phải ghi
nhận phê duyệt và người đọc thứ hai theo quy tắc quản lý thay đổi. Nhãn benign
không phải bảo đảm URL an toàn.

## 11. Bằng chứng và kiểm chứng

- `summary.json`: số đếm, tỷ lệ, schema, phân lớp các chẩn đoán, hash và giới hạn.
- `duplicate_url_groups.jsonl`: toàn bộ 2.207 nhóm URL lặp, số lần và các label.
- `conflict_records.jsonl`: toàn bộ 12 bản ghi mâu thuẫn, với số bản ghi gốc.
- `anomaly_records.jsonl`: tất cả bản ghi khớp ít nhất một dấu hiệu bất thường được liệt kê trong script.
- `examples.jsonl`: 12 ví dụ xác định được như mục 7.
- `run.log`: kết quả chạy script ở dạng JSON.
- Các code cell notebook đã được chạy tuần tự trực tiếp bằng Python dự án (ghi stdout vào notebook); Jupyter kernel không khởi động được do sandbox chặn mở socket cục bộ. Các cell chạy lại audit và kiểm tra độc lập shape, label counts, duplicates, conflicts; đầu ra được lưu trong notebook.

CSV reader chuẩn và pandas cho cùng tổng hàng, số nhãn, số bản sao dư và số URL xung đột. SHA-256 raw và archive không thay đổi sau audit. Notebook còn kiểm tra kết quả chạy lại khớp báo cáo số liệu trước đó, ngoại trừ thời điểm chạy.

## 12. Cách đọc phần code

- **Mục đích:** data_audit.py thu thập bằng chứng chất lượng trước khi chọn target.
- **Input:** đúng một CSV từ archive khóa học; raw hiện có phải trùng hash.
- **Luồng chính:** xác nhận byte nguồn → đọc nguyên chuỗi → đếm schema/nhãn/thiếu/trùng/xung đột → chẩn đoán URL → ghi bằng chứng → kiểm tra nguồn không đổi.
- **Output:** reports/audit; không ghi data/interim, data/processed hoặc models.
- **Có thể điều chỉnh sau khi thảo luận:** ngưỡng độ dài chẩn đoán 2.048, danh sách token thiếu, cách chọn ví dụ. Đây là lựa chọn đo lường, không phải quy tắc tự xóa dữ liệu.
- **Verification:** các đối chiếu và assert kể trên; không chạy lại Stage 0.
