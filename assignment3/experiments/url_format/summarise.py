"""Produce the user-facing findings from recorded measurements, without new fits."""
import json
from pathlib import Path
import pandas as pd
from diagnose import HERE,PROJECT,BACKEND,write_json
from dtdlink_ml.feature_extraction import file_sha256


def pct(x):return f'{100*x:.2f}%'


def main():
    results=HERE/'results'
    baseline=json.loads((results/'baseline-cohorts.json').read_text())
    root=json.loads((results/'root-path-audit.json').read_text())
    identity=json.loads((results/'canonical-identity-audit.json').read_text())
    candidate_rows=[]
    for p in sorted(results.glob('*.json')):
        r=json.loads(p.read_text())
        if 'api_formatted' in r and 'gates' in r:
            score=r['api_formatted'];home=r.get('homepage_no_query',{})
            candidate_rows.append({'name':r['name'],'fpr':score['fpr'],'dangerous_recall':score['recall'],'phishing_recall':score['subtypes']['phishing']['recall'],'homepage_fpr':home.get('fpr'),'homepage_recall':home.get('recall'),'stage_gate_passes':r['passes']})
    pd.DataFrame(candidate_rows).to_csv(results/'candidate-comparison.csv',index=False)
    artifacts=[]
    for p in sorted((HERE/'artifacts').glob('*.joblib')):
        artifacts.append({'name':p.stem,'sha256':file_sha256(p),'bytes':p.stat().st_size,'local_path':str(p.relative_to(BACKEND.parent)),'bundled_in_zip':False})
    write_json(results/'candidate-artifacts.json',artifacts)
    decision={'integrated':False,'active_model_sha256':file_sha256(BACKEND/'models/final_pipeline.joblib'),'active_threshold':.5,
              'reason':'No candidate passed both whole-validation and homepage-stratum criteria. Aggregate text-model improvement did not resolve the requested homepage behaviour; numeric-root alternatives sacrificed too much dangerous recall. Retain the running A2 artifact, not a whitelist or threshold workaround.',
              'candidate_stage_selected':'neutral_text_recall5_converged (aggregate only, NOT deployed)',
              'homepage_gate':{'fpr_max':.20,'dangerous_recall_min':.80},
              'a2_test_use':'No test outcomes used for fitting, tuning, scoring or selection. Only preservation hashes and disjoint split-group metadata checked.',
              'ui_backend_security':'Active UI, model, model metadata, API example, validation and security code remain unchanged; research scripts/results added in A3 only.'}
    write_json(results/'promotion-decision.json',decision)
    a=baseline['api_formatted'];native=baseline['native_explicit'];raw=baseline['raw_eligible']
    text=json.loads((results/'neutral_text_recall5_converged.json').read_text())
    rf=json.loads((results/'root_rf_richer.json').read_text())
    auth=json.loads((results/'authority_text_recall5.json').read_text())
    rows=[('A2 đang chạy, URL dạng API',a,root['homepage_no_query']['a2_api']),
          ('A3 text + 36 phép đo',text['api_formatted'],root['homepage_no_query']['selected_text']),
          ('A3 chuyên gia riêng cho root path',rf['api_formatted'],rf['homepage_no_query']),
          ('A3 text-only, không L2',auth['api_formatted'],auth['homepage_no_query'])]
    table='\n'.join(f'| {name} | {pct(s["fpr"])} | {pct(s["recall"])} | {pct(h["fpr"])} | {pct(h["recall"])} |' for name,s,h in rows)
    report=f'''# Kiểm tra lỗi nhạy định dạng URL — DTDLINK A3

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

Tái lập ví dụ: `https://www.google.com/` {pct(.972174377884553)},
`www.google.com/` {pct(.18655881540261557)}; `https://github.com/`
{pct(.9543263549005231)}, `github.com/` {pct(.05823079257896131)}.
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
lập scheme, train có {identity['train']['canonical_urls_with_both_labels']:,} định danh
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
{table}

FPR = số benign bị báo dangerous / tổng benign. Recall dangerous = số dangerous
nhận ra / tổng dangerous. Bản text giảm FP từ {a['fp']:,} xuống
{text['api_formatted']['fp']:,}, nhưng FN tăng từ {a['fn']:,} lên
{text['api_formatted']['fn']:,}. Đây là đánh đổi thật, không được giấu.

Kiểm tra riêng **38.432 URL vốn đã có HTTP(S)**, không thêm scheme:
A2 FPR {pct(native['fpr'])}, recall {pct(native['recall'])}; bản text FPR
{pct(text['native_explicit']['fpr'])}, recall {pct(text['native_explicit']['recall'])}.
Do đó cải thiện tổng không chỉ do cách tạo URL hoàn thiện.

Để đối chiếu, A2 trên **chuỗi gốc** của cùng tập đủ điều kiện có FPR
{pct(raw['fpr'])}, recall {pct(raw['recall'])}. Đây là định dạng dataset, không phải
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
'''
    (BACKEND.parent/'docs/URL_FORMAT_FINDINGS_VI.md').write_text(report)
    print(json.dumps(decision,indent=2))

if __name__=='__main__':main()
