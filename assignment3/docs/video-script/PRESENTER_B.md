# Presenter B — Follow one request through the actual code

**Mốc bản ghép:** 04:15–08:45. Chỉ đọc blockquote tiếng Anh. Mở sẵn các file
bên dưới, cỡ chữ dễ đọc. Giữ nguyên ví dụ của A:
`https://paypal.com@account-check.example/login`.

## B1 · 04:15–04:40 · Architecture

**Màn hình:** sơ đồ trong `assignment3/README.md`, sau đó chuyển sang code.

> I will explain how the parts connect. React sends one URL to FastAPI. The
> backend validates it, extracts features, runs the saved model, and returns JSON.
> React then displays the result. We use POST for prediction and GET for readiness
> and model information, so both methods serve a practical purpose.

## B2 · 04:40–05:30 · Frontend input and request

**Mở:** `frontend/src/App.jsx`, tìm `async function onSubmit`. Chỉ lần lượt
`validateURL(draft)`, `setLoading(true)`, `apiRequest`, JSON.stringify và setResult.
Mở `frontend/src/api.js`, chỉ fetch/response.ok/AbortController.

> In App dot JSX, onSubmit first validates the input. It then sets the loading
> state and sends the original string in a JSON object containing the URL field.
> It does not remove HTTPS or rewrite the input to improve the prediction.
>
> In api dot JS, fetch sends the request to slash predict. The response is parsed
> as JSON. Failed status codes become useful messages, and an AbortController
> handles the ten-second client timeout. Finally, the loading state is cleared.

## B3 · 05:30–06:35 · Pydantic, real /docs request and errors

**Mở:** `backend/app/schemas.py` tại PredictRequest/PredictResponse; chỉ strict
string/max length và validate_url. Mở http://127.0.0.1:8000/docs → POST /predict
→ Try it out → thay body bằng JSON bên dưới → Execute.

```json
{"url":"https://paypal.com@account-check.example/login"}
```

> Frontend checks help users, but attackers can bypass the interface. In schemas
> dot PY, Pydantic requires a string with a maximum of two thousand and forty-eight
> characters, and our validator requires a complete HTTP or HTTPS URL.
>
> Here in slash docs, I submit the same example directly to the API. The successful
> response contains the label, dangerous probability, confidence, URL components
> and observations. These values come from the backend, rather than fixed interface text.

**Thao tác:** giữ cảnh successful response đủ đọc, sau đó input `example.com/`
trong JSON và Execute. Chỉ **Server response 422**, error/fields/request_id.

> Removing the scheme returns status four twenty-two. The error uses a consistent
> JSON structure with a code, message, field details and request identifier.
> Internal stack traces and filesystem paths are not returned.

## B4 · 06:35–07:40 · Startup and real model inference

**Mở:** `backend/app/main.py` → lifespan, predict_url; `backend/app/service.py`
→ load_model/predict; `backend/src/dtdlink_ml/predict.py` → features_from_urls,
probability_from_features. Khi chuyển file, chỉ block đang nói, không cuộn cả file.

> In main dot PY, the lifespan function loads the model once when the server
> starts. The service checks its trusted hash before loading the joblib file.
>
> The prediction service calls the saved URL pipeline. Features from URLs applies
> the unchanged Assignment Two extractor and builds a table in the required
> feature order. The classifier then calls predict proba.
>
> This is a Random Forest using thirty-six numeric features, including URL length,
> user information and hostname structure. We preserve the training-time feature
> logic instead of introducing different preprocessing at prediction time.

## B5 · 07:40–08:45 · Meaning of the response and design choices

**Mở:** `service.py` → probability/confidence/label; `Result.jsx` → result.label,
result.confidence; `URLAnalysis.jsx` → span/text rendering; cuối cùng result UI.

> Class zero is benign. Class one combines phishing, malware and defacement,
> so the application does not claim to identify a particular attack type.
>
> At a dangerous probability of at least zero point five, the label is “Potentially
> dangerous”. Below that threshold, it is “Likely legitimate”. Confidence is the
> probability of the predicted class: either p or one minus p.
>
> Result dot JSX displays these returned values. URLAnalysis displays the address
> and observations as escaped React text, without making the destination clickable.
> The observations are a separate explanation layer, not learned feature contributions.
>
> We chose local text analysis to avoid fetching untrusted destinations and sending
> submitted links to outside services. Next, we will demonstrate the application's
> security controls and their limitations.

## Hiểu trước khi quay

- JSON request có field `url`; response là dữ liệu thật từ backend.
- Thứ tự 36 feature phải khớp model đã học; không tự bỏ HTTPS hay đổi threshold.
- Hàm `predict_proba` trả điểm lớp; `service.py` tính confidence theo lớp được chọn.
- Hash check xảy ra trước joblib load. Đây là hygiene có sẵn; hai defence chọn
  chấm trong README vẫn là DoS và misconfiguration/dependencies.
- Model không phân biệt subtype, không xác minh website, không được gọi là
  “phishing probability” riêng. Model startup không phải train lại model.

**Cách đọc:** JSX = “J S X”; JSON = “jay-son”; Pydantic = “pie-dantic”;
FastAPI = “Fast A P I”; HTTP = “H T T P”; 422 = “four twenty-two”.
