# Presenter A — Introduction and website demonstration

**Mốc bản ghép:** 00:00–04:15. Nhóm tự chọn người nói. Chỉ đọc các đoạn tiếng
Anh trong blockquote; tiếng Việt là chỉ dẫn quay. Mốc thời gian là mục tiêu,
cần bấm giờ khi tập. Dùng bản chính tại http://127.0.0.1:5173/.

## A1 · 00:00–00:30 · Introduction

**Màn hình:** trang Check URL, chưa có kết quả. Không cần slide dài.

> Hello, we are Session Seven, Group Five. Our project is DTDLINK, Detect The
> Deception Links. It helps people inspect a suspicious link before opening it.
> Our React interface connects to a FastAPI backend and a trained Random Forest.
> The application analyses URL text without visiting the destination website.

## A2 · 00:30–01:35 · A real prediction and readable URL evidence

**Thao tác:** bấm **A misleading address** rồi **Analyse link**. Nút mẫu chỉ điền
input, không tự submit. Chờ kết quả, chỉ label và confidence. Ví dụ hiện tại:
`https://paypal.com@account-check.example/login`; ngày 6/11 kiểm tra trên UI cho
97,3% confidence, nhãn Potentially dangerous. Không cần đọc số trong lời nói.

> I will select “A misleading address” and analyse it. The main result shows the
> model's prediction and its confidence. This estimate is not a guarantee of
> real-world harm or safety.

**Thao tác:** cuộn đến **THIS LINK POINTS TO**, mở **Understand the parts of
this URL**, rồi chỉ hai observation trong **READ THE SIGNS**.

> The actual host is account-check dot example. PayPal dot com appears before
> the at sign, so it is user information, not the destination hostname.
>
> The breakdown separates the connection type, user information, hostname and
> page path. “Hidden destination” explains the misleading structure and suggests
> checking a trusted address. “Account-related terms” shows words such as account
> and login. These are observations about the text, not the exact reasons for
> the model's decision.

## A3 · 01:35–02:40 · Loading, validation and error states

**Chuẩn bị riêng clip trạng thái trước khi quay:** dùng input không hợp lệ;
giữ loading đủ nhìn bằng làm chậm request có kiểm soát; mô phỏng request lỗi
và response sai cấu trúc bằng các test có sẵn. Có hướng dẫn trong README của
bộ script. Khôi phục kết nối trước clip kết quả tiếp theo. Không sửa model.

**Thao tác:** cho thấy **Analysing…** / **Reading the signs in your link…**, rồi
input `example.com/` nhận **Start the URL with http:// or https://.**

> During a request, the button shows “Analysing” and prevents repeated submission.
> We have slowed the response for this demonstration so the loading state is visible.
> An incomplete address receives a message beside the input.

**Thao tác:** cắt sang clip request bị chặn trong trình duyệt, rồi /unknown-page,
rồi fallback render. Chữ trên màn hình phải đúng clip tương ứng.

> Here, a deliberately interrupted request shows a service error. An unknown
> route shows our not-found page. A separate controlled rendering failure reaches
> the unexpected-error fallback, with a reload option. These are controlled faults
> to demonstrate recovery, rather than a normal prediction.

## A4 · 02:40–03:10 · Phone layout and keyboard access

**Thao tác:** viewport khoảng 375×812, menu mở/đóng, input và một result. Dùng
Tab để thấy focus và Enter để submit. Đây là giả lập kích thước, không nói thử
trên thiết bị thật. Trở về desktop trước cảnh biểu đồ.

> This is the phone-sized layout. The navigation collapses into a menu, and the
> result remains readable. Labels and visible keyboard focus support accessibility.
> Users can move through controls with Tab and submit with Enter.

## A5 · 03:10–04:15 · Two interactive visualisations

**Chuẩn bị:** ở cùng một phiên, chạy thật misleading example và simple example,
rồi quay lại misleading example để chart hiện Hidden destination. Không reload
trước khi quay Session insights. Các input không phải nhãn an toàn đã xác minh.

**Thao tác:** chart **What deserves a closer look?** → Show signals → High
attention → chọn Hidden destination. Mở **Session insights** → chọn Check # →
Filter checks; có thể chọn Likely legitimate và cho thấy empty state nếu không
có kết quả lớp này; trả về All results. Bấm Clear session sau cùng.

> The first chart groups observed signals by attention level. I can filter the
> categories and select “Hidden destination” for more detail.
>
> Session insights answers a different question: how do the model scores compare
> across checks? I can filter predictions and select a check to inspect its score
> and signal count. The dashed line marks the fifty-percent decision threshold.
>
> Only the latest twenty anonymous entries remain in memory. This comparison
> excludes URLs and hostnames. Clearing the session removes these entries.
>
> Next, we will follow a request through the actual frontend, API and model code.

## Hiểu trước khi quay

- Confidence thuộc nhãn model dự đoán; không phải độ an toàn thực tế.
- Host sau @ mới là hostname; tên quen thuộc trước @ không xác minh đích.
- Hai chart đo hai thứ: số pattern theo mức chú ý và điểm model theo lần kiểm tra.
- Phần loading/network/fallback là lỗi/độ trễ tạo có kiểm soát. Chỉ đọc lời đã
  quay được màn hình tương ứng. Chưa dựng được thì cần tập trước, không ghép
  screenshot/test result vào như dự đoán thật.

**Cách đọc:** URL = “you are ell”; API = “A P I”; @ = “at sign”. Không đọc cả
URL dài thành tiếng, dùng con trỏ chỉ phần đang giải thích.
