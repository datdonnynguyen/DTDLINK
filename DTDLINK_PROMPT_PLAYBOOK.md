# DTDLINK Prompt Playbook

> Bộ prompt ngắn để học và thực hiện từng Stage. Chi tiết kỹ thuật, thứ tự công việc và điều kiện hoàn thành nằm trong `ASSIGNMENT2_MASTER_PLAN.md`.

## Cách sử dụng

Mỗi Stage dùng một task riêng và đi theo thứ tự:

1. **Prompt A — Học lý thuyết:** hiểu kiến thức và vị trí của Stage.
2. **Prompt B — Vừa học vừa làm:** thực hiện dự án từng bước; Codex thao tác code thay bạn.
3. **Prompt C — Hiểu kết quả:** nhìn lại code, kết quả và ý nghĩa.
4. **Prompt D — Tổng kết:** kiểm tra hoàn thành, cập nhật tiến độ và tạo checkpoint.

Bạn là người thực hiện, hiểu và quyết định dự án. Codex thay bạn viết/chạy code, kiểm tra và sửa lỗi. Trước khi thay đổi code, Codex phải giải thích và chờ bạn nói **“OK, hãy code”**. Trước bước lớn tiếp theo, Codex chờ bạn nói **“tiếp tục”**.

---

# Stage 0 — Chuẩn bị môi trường và hiểu cấu trúc dự án

**Tên task:** `DTDLINK 00 – Setup và nền tảng Week 4`  
**Kiến thức:** Week 4.

## Prompt A — Học lý thuyết

```text
Hãy đọc PROJECT_CONTEXT.md và ASSIGNMENT2_MASTER_PLAN.md. Chúng ta bắt đầu Stage 0.

Hãy giải thích dễ hiểu kiến thức cần biết, kiến thức thuộc Week nào, Stage 0 dùng để làm gì và nằm ở đâu trong DTDLINK. Dùng ví dụ đơn giản và chưa viết code.
```

## Prompt B — Vừa học vừa làm dự án

```text
Bây giờ hãy cùng tôi thực hiện Stage 0 theo Master Plan.

Chia công việc thành các bước nhỏ. Trước mỗi bước, giải thích việc sắp làm, lý do, input, output và file liên quan. Chờ tôi nói “OK, hãy code”, sau đó bạn thay tôi thực hiện phần kỹ thuật, giải thích kết quả và chờ tôi nói “tiếp tục”.
```

## Prompt C — Hiểu kết quả

```text
Hãy giúp tôi nhìn lại Stage 0: chúng ta đã chuẩn bị những gì, mỗi thành phần dùng để làm gì, cấu trúc dự án hoạt động ra sao, kết quả kiểm tra thế nào và phần nào tôi có thể điều chỉnh. Không cần giải thích từng dòng code.
```

## Prompt D — Tổng kết và checkpoint

```text
Hãy kiểm tra Stage 0 đã đạt completion gate trong Master Plan chưa. Nếu đã đạt, hãy tổng kết kết quả, file thay đổi, kiểm tra đã chạy, hạn chế còn lại, cập nhật tiến độ và tạo checkpoint cho Stage 1. Không đánh dấu hoàn thành nếu chưa có bằng chứng.
```

---

# Stage 1 — Kiểm tra dataset và xác định target

**Tên task:** `DTDLINK 01 – Dataset Audit và Labels`  
**Kiến thức:** Week 4.

## Prompt A — Học lý thuyết

```text
Hãy đọc PROJECT_CONTEXT.md và ASSIGNMENT2_MASTER_PLAN.md, kiểm tra Stage 0 và bắt đầu Stage 1.

Hãy giải thích dễ hiểu kiến thức cần biết, kiến thức thuộc Week nào, Stage 1 dùng để làm gì và ảnh hưởng thế nào đến DTDLINK. Dùng ví dụ phishing URL và chưa viết code.
```

## Prompt B — Vừa học vừa làm dự án

```text
Bây giờ hãy cùng tôi thực hiện Stage 1 theo Master Plan.

Chia việc kiểm tra dataset và lựa chọn target thành các bước nhỏ. Trước mỗi bước, giải thích câu hỏi đang kiểm tra, lý do, input và kết quả có thể xuất hiện. Chờ tôi nói “OK, hãy code”, sau đó bạn thay tôi chạy phần kỹ thuật, cùng tôi đọc kết quả và chờ tôi nói “tiếp tục”. Không tự quyết định target thay tôi.
```

## Prompt C — Hiểu kết quả

```text
Hãy giúp tôi nhìn lại Stage 1: dataset có đặc điểm và vấn đề gì, chúng ta đã kiểm tra bằng cách nào, kết quả có ý nghĩa gì, target được chọn ra sao và quyết định này ảnh hưởng thế nào đến các Stage sau. Chỉ giải thích luồng code chính.
```

## Prompt D — Tổng kết và checkpoint

```text
Hãy kiểm tra Stage 1 đã đạt completion gate trong Master Plan chưa. Nếu đã đạt, hãy tổng kết audit, quyết định target, file và bằng chứng, cập nhật tiến độ và tạo checkpoint cho Stage 2. Không đánh dấu hoàn thành nếu quyết định quan trọng chưa được ghi lại.
```

---

# Stage 2 — Làm sạch dữ liệu

**Tên task:** `DTDLINK 02 – Data Cleaning`  
**Kiến thức:** Week 4 và Week 5.

## Prompt A — Học lý thuyết

```text
Hãy đọc hai file tiến độ, kiểm tra Stage 1 và bắt đầu Stage 2.

Hãy giải thích dễ hiểu kiến thức cần biết, kiến thức thuộc Week nào, cleaning giải quyết vấn đề gì và tại sao nó phải được thực hiện trước các bước mô hình. Liên hệ với kết quả Stage 1 và chưa viết code.
```

## Prompt B — Vừa học vừa làm dự án

```text
Bây giờ hãy cùng tôi thực hiện Stage 2 theo Master Plan.

Chia cleaning pipeline thành các bước nhỏ. Trước mỗi bước, giải thích dữ liệu nào sẽ được xử lý, lý do, ảnh hưởng và cách kiểm tra. Chờ tôi nói “OK, hãy code”, sau đó bạn thay tôi viết/chạy code, cho tôi xem kết quả trước và sau rồi chờ tôi nói “tiếp tục”.
```

## Prompt C — Hiểu kết quả

```text
Hãy giúp tôi nhìn lại Stage 2: dữ liệu đã được làm sạch như thế nào, tại sao dùng các quy tắc đó, số liệu thay đổi ra sao, code chạy theo luồng nào, output nằm ở đâu và quy tắc nào tôi có thể điều chỉnh.
```

## Prompt D — Tổng kết và checkpoint

```text
Hãy kiểm tra Stage 2 đã đạt completion gate trong Master Plan chưa. Nếu đã đạt, hãy tổng kết quy tắc cleaning, số liệu trước/sau, file, test, hạn chế, cập nhật tiến độ và tạo checkpoint cho Stage 3. Không đánh dấu hoàn thành nếu raw data bị thay đổi hoặc kết quả chưa tái tạo được.
```

---

# Stage 3 — URL parser và feature extractor

**Tên task:** `DTDLINK 03 – URL Parser và Features`  
**Kiến thức:** Week 4 và Week 5.

## Prompt A — Học lý thuyết

```text
Hãy đọc hai file tiến độ, kiểm tra Stage 2 và bắt đầu Stage 3.

Hãy giải thích dễ hiểu kiến thức cần biết, kiến thức thuộc Week nào, URL parser và feature extractor dùng để làm gì, và chúng biến một URL thành dữ liệu cho model như thế nào. Dùng một URL ví dụ và chưa viết code.
```

## Prompt B — Vừa học vừa làm dự án

```text
Bây giờ hãy cùng tôi thực hiện Stage 3 theo Master Plan.

Chia parser, features, feature dictionary và tests thành các bước nhỏ. Trước mỗi bước, giải thích input, cách xử lý, output, hiệu quả và trường hợp lỗi. Chờ tôi nói “OK, hãy code”, sau đó bạn thay tôi viết/chạy code, giải thích kết quả rồi chờ tôi nói “tiếp tục”.
```

## Prompt C — Hiểu kết quả

```text
Hãy giúp tôi nhìn lại Stage 3 bằng một URL ví dụ: URL được tách và biến thành features như thế nào, code chính nằm ở đâu, từng nhóm feature giúp gì, tests chứng minh điều gì và phần nào tôi có thể điều chỉnh.
```

## Prompt D — Tổng kết và checkpoint

```text
Hãy kiểm tra Stage 3 đã đạt completion gate trong Master Plan chưa. Nếu đã đạt, hãy tổng kết parser, feature extractor, feature dictionary, tests và limitations, cập nhật tiến độ và tạo checkpoint cho Stage 4. Không đánh dấu hoàn thành nếu feature schema chưa ổn định hoặc test chưa đạt.
```

---

# Stage 4 — EDA và chia dữ liệu an toàn

**Tên task:** `DTDLINK 04 – EDA và Safe Splitting`  
**Kiến thức:** Week 5.

## Prompt A — Học lý thuyết

```text
Hãy đọc hai file tiến độ, kiểm tra Stage 3 và bắt đầu Stage 4.

Hãy giải thích dễ hiểu kiến thức cần biết, kiến thức thuộc Week nào, EDA và train/validation/test split dùng để làm gì, và data leakage có thể làm kết quả sai lệch như thế nào. Chưa viết code.
```

## Prompt B — Vừa học vừa làm dự án

```text
Bây giờ hãy cùng tôi thực hiện Stage 4 theo Master Plan.

Chia EDA và việc chia dữ liệu thành các bước nhỏ. Trước mỗi bước, giải thích câu hỏi cần trả lời, dữ liệu sử dụng, output và nguy cơ leakage. Chờ tôi nói “OK, hãy code”, sau đó bạn thay tôi viết/chạy code, cùng tôi đọc biểu đồ hoặc kết quả rồi chờ tôi nói “tiếp tục”.
```

## Prompt C — Hiểu kết quả

```text
Hãy giúp tôi nhìn lại Stage 4: các biểu đồ cho biết điều gì, dữ liệu được chia như thế nào, cách chia hiện tại giảm leakage ra sao, test set được bảo vệ thế nào và setting nào tôi có thể điều chỉnh.
```

## Prompt D — Tổng kết và checkpoint

```text
Hãy kiểm tra Stage 4 đã đạt completion gate trong Master Plan chưa. Nếu đã đạt, hãy tổng kết insights, cách chia dữ liệu, leakage checks, files và bằng chứng, cập nhật tiến độ và tạo checkpoint cho Stage 5. Không đánh dấu hoàn thành nếu test set chưa được khóa hoặc leakage chưa được kiểm tra.
```

---

# Stage 5 — Classification models

**Tên task:** `DTDLINK 05 – Classification Models`  
**Kiến thức:** Week 6 và Week 7.

## Prompt A — Học lý thuyết

```text
Hãy đọc hai file tiến độ, kiểm tra Stage 4 và bắt đầu Stage 5.

Hãy giải thích dễ hiểu kiến thức cần biết, kiến thức thuộc Week nào, classification model học và dự đoán như thế nào, và chúng ta sẽ chọn model công bằng ra sao. Dùng ví dụ DTDLINK và chưa viết code.
```

## Prompt B — Vừa học vừa làm dự án

```text
Bây giờ hãy cùng tôi thực hiện Stage 5 theo Master Plan.

Chia training, validation và lựa chọn model thành các bước nhỏ. Trước mỗi bước, giải thích model hoặc quyết định sắp làm, input, setting, output và cách đánh giá. Chờ tôi nói “OK, hãy code”, sau đó bạn thay tôi viết/chạy code, cùng tôi đọc validation result rồi chờ tôi nói “tiếp tục”. Không tự chọn final model thay tôi và không dùng test set.
```

## Prompt C — Hiểu kết quả

```text
Hãy giúp tôi nhìn lại Stage 5: các model đã học như thế nào, được so sánh bằng gì, kết quả validation có ý nghĩa gì, vì sao chọn model/threshold hiện tại, code chính hoạt động ra sao và setting nào tôi có thể điều chỉnh.
```

## Prompt D — Tổng kết và checkpoint

```text
Hãy kiểm tra Stage 5 đã đạt completion gate trong Master Plan chưa. Nếu đã đạt, hãy tổng kết model comparison, quyết định model/threshold, file, bằng chứng và limitations, cập nhật tiến độ và tạo checkpoint cho Stage 6. Xác nhận test set vẫn chưa được sử dụng.
```

---

# Stage 6 — Clustering

**Tên task:** `DTDLINK 06 – Clustering`  
**Kiến thức:** Week 6 và Week 7.

## Prompt A — Học lý thuyết

```text
Hãy đọc hai file tiến độ, kiểm tra Stage 5 và bắt đầu Stage 6.

Hãy giải thích dễ hiểu kiến thức cần biết, kiến thức thuộc Week nào, clustering khác classification thế nào và clustering giúp hiểu các nhóm URL trong một class ra sao. Chưa viết code.
```

## Prompt B — Vừa học vừa làm dự án

```text
Bây giờ hãy cùng tôi thực hiện Stage 6 theo Master Plan.

Chia việc chọn class, chuẩn bị features, chạy clustering và diễn giải clusters thành các bước nhỏ. Trước mỗi bước, giải thích input, setting, output, cách đánh giá và giới hạn. Chờ tôi nói “OK, hãy code”, sau đó bạn thay tôi viết/chạy code, cùng tôi hiểu kết quả rồi chờ tôi nói “tiếp tục”.
```

## Prompt C — Hiểu kết quả

```text
Hãy giúp tôi nhìn lại Stage 6: class và features được chọn ra sao, thuật toán tạo clusters như thế nào, mỗi cluster có đặc điểm gì, kết quả có ý nghĩa gì đối với DTDLINK và setting nào tôi có thể điều chỉnh.
```

## Prompt D — Tổng kết và checkpoint

```text
Hãy kiểm tra Stage 6 đã đạt completion gate trong Master Plan chưa. Nếu đã đạt, hãy tổng kết phương pháp, cluster profiles, URL đại diện, files, bằng chứng và limitations, cập nhật tiến độ và tạo checkpoint cho Stage 7. Không đánh dấu hoàn thành nếu label bị dùng làm clustering input hoặc clusters chưa được diễn giải.
```

---

# Stage 7 — Đánh giá cuối cùng và lưu model

**Tên task:** `DTDLINK 07 – Final Evaluation`  
**Kiến thức:** Week 7.

## Prompt A — Học lý thuyết

```text
Hãy đọc hai file tiến độ, kiểm tra các Stage trước và bắt đầu Stage 7.

Hãy giải thích dễ hiểu kiến thức cần biết, kiến thức thuộc Week nào, các evaluation metrics và confusion matrix nói lên điều gì, và vì sao error analysis quan trọng với DTDLINK. Chưa chạy final test.
```

## Prompt B — Vừa học vừa làm dự án

```text
Bây giờ hãy cùng tôi thực hiện Stage 7 theo Master Plan.

Chia final evaluation, error analysis và model export thành các bước nhỏ. Trước mỗi bước, giải thích metric hoặc kiểm tra sắp làm, input, output và điều có thể kết luận. Chờ tôi nói “OK, hãy code”, sau đó bạn thay tôi chạy phần kỹ thuật, cùng tôi đọc kết quả rồi chờ tôi nói “tiếp tục”. Không điều chỉnh model dựa trên test result.
```

## Prompt C — Hiểu kết quả

```text
Hãy giúp tôi nhìn lại Stage 7: final metrics có ý nghĩa gì, model thường sai ở đâu, false negatives ảnh hưởng thế nào, limitations là gì, saved pipeline gồm những gì và một raw URL đi đến prediction như thế nào.
```

## Prompt D — Tổng kết và checkpoint

```text
Hãy kiểm tra Stage 7 đã đạt completion gate trong Master Plan chưa. Nếu đã đạt, hãy tổng kết final metrics, error analysis, saved model, offline/reload tests, files và limitations, cập nhật tiến độ và tạo checkpoint cho Stage 8.
```

---

# Stage 8 — Báo cáo và nộp Assignment 2

**Tên task:** `DTDLINK 08 – Report và Submission`  
**Kiến thức:** Tổng hợp Weeks 4–7 và bước chuyển tiếp Week 8.

## Prompt A — Học lý thuyết

```text
Hãy đọc hai file tiến độ, kiểm tra bằng chứng của Stages 0–7 và bắt đầu Stage 8.

Hãy giải thích dễ hiểu Assignment 2 cần nộp những gì, mỗi phần báo cáo lấy bằng chứng từ Stage nào, reproducibility nghĩa là gì và rubric sẽ được kiểm tra ra sao. Chưa chỉnh sửa bài nộp.
```

## Prompt B — Vừa học vừa hoàn thiện dự án

```text
Bây giờ hãy cùng tôi thực hiện Stage 8 theo Master Plan và rubric.

Chia report, README, evidence và package thành các phần nhỏ. Trước mỗi phần, giải thích yêu cầu, bằng chứng, file liên quan và tiêu chí đạt. Chờ tôi nói “OK, hãy code”, sau đó bạn thay tôi chỉnh sửa hoặc kiểm tra, cho tôi xem kết quả rồi chờ tôi nói “tiếp tục”. Không tạo số liệu không có bằng chứng.
```

## Prompt C — Hiểu kết quả

```text
Hãy giúp tôi nhìn lại Stage 8 và toàn bộ Assignment 2: câu chuyện từ raw data đến saved model, mỗi deliverable chứng minh điều gì, cách người chấm tái tạo kết quả, mục rubric nào đã đạt và phần nào còn cần nhóm xác nhận.
```

## Prompt D — Tổng kết và checkpoint

```text
Hãy kiểm tra Stage 8 và toàn bộ Assignment 2 đã hoàn thành chưa. Nếu đã đạt, hãy tổng kết deliverables, rubric evidence, clean rerun, việc còn cần con người thực hiện, cập nhật tiến độ và tạo checkpoint kết thúc Assignment 2. Không đánh dấu hoàn thành nếu còn yêu cầu bắt buộc chưa có bằng chứng.
```

---

# Stage 9 — Tích hợp Assignment 3

> Chỉ bắt đầu sau khi Assignment 2 hoàn thành.

**Tên task:** `DTDLINK 09 – Assignment 3 Integration`  
**Kiến thức:** Weeks 8–12.

## Prompt A — Học lý thuyết

```text
Hãy đọc hai file tiến độ, xác nhận Assignment 2 đã hoàn thành và bắt đầu Stage 9.

Hãy giải thích dễ hiểu kiến thức cần biết, kiến thức thuộc Week nào, React, FastAPI và saved ML pipeline kết nối với nhau thế nào, và Stage này biến model thành sản phẩm DTDLINK ra sao. Chưa viết code.
```

## Prompt B — Vừa học vừa làm dự án

```text
Bây giờ hãy cùng tôi thực hiện Stage 9 theo Master Plan.

Chia việc tích hợp frontend, backend, model và testing thành các bước nhỏ. Trước mỗi bước, giải thích vị trí trong hệ thống, input, output, file liên quan và cách test. Chờ tôi nói “OK, hãy code”, sau đó bạn thay tôi viết/chạy code, cùng tôi đọc kết quả rồi chờ tôi nói “tiếp tục”.
```

## Prompt C — Hiểu kết quả

```text
Hãy giúp tôi nhìn lại Stage 9 bằng một URL ví dụ: dữ liệu đi từ React qua FastAPI đến model và quay lại giao diện như thế nào, code chính nằm ở đâu, kết quả được sử dụng ra sao và phần nào tôi có thể điều chỉnh.
```

## Prompt D — Tổng kết và checkpoint

```text
Hãy kiểm tra Stage 9 đã đạt completion gate trong Master Plan và acceptance criteria chưa. Nếu đã đạt, hãy tổng kết luồng end-to-end, files, tests, limitations, cập nhật tiến độ và tạo checkpoint cho bước tiếp theo của Assignment 3.
```

---

# Khi phải dừng giữa Stage

```text
Hãy tạo checkpoint giữa Stage: ghi phần đã làm, bằng chứng, file thay đổi, phần đang dở, lỗi hoặc quyết định còn chờ và đúng một bước tiếp theo. Cập nhật tiến độ thực tế nhưng không đánh dấu cả Stage hoàn thành.
```

# Khi mở task mới hoặc mất context

```text
Hãy đọc PROJECT_CONTEXT.md và ASSIGNMENT2_MASTER_PLAN.md, kiểm tra file và bằng chứng để xác định trạng thái thật. Cho tôi biết Stage hiện tại, phần đã xong, phần đang dở và bước tiếp theo. Không làm lại phần đã hoàn thành; sau đó tiếp tục bằng Prompt phù hợp A, B, C hoặc D.
```
