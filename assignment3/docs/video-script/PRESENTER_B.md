# Presenter B — Follow one request through the actual code

**Final-video timeline:** 04:15–08:45. Read only the blockquotes aloud. Open the listed files beforehand with readable text. Use the same example as Presenter A: `https://paypal.com@account-check.example/login`.

## B1 · 04:15–04:40 · Architecture

**Screen:** Show the architecture diagram in `assignment3/README.md`, then move to the actual code.

> I will explain how the parts connect. React sends one URL to FastAPI. The
> backend validates it, extracts features, runs the saved model, and returns JSON.
> React then displays the result. We use POST for prediction and GET for readiness
> and model information, so both methods serve a practical purpose.

## B2 · 04:40–05:30 · Frontend input and request

**Open:** `frontend/src/App.jsx`, at `async function onSubmit`. Point to `validateURL(draft)`, `setLoading(true)`, `apiRequest`, `JSON.stringify` and `setResult` in that order. Then open `frontend/src/api.js` and point to `fetch`, `response.ok` and `AbortController`.

> In App dot JSX, onSubmit first validates the input. It then sets the loading
> state and sends the original string in a JSON object containing the URL field.
> It does not remove HTTPS or rewrite the input to improve the prediction.
>
> In api dot JS, fetch sends the request to slash predict. The response is parsed
> as JSON. Failed status codes become useful messages, and an AbortController
> handles the ten-second client timeout. Finally, the loading state is cleared.

## B3 · 05:30–06:35 · Pydantic, real /docs request and errors

**Open:** `backend/app/schemas.py`, at `PredictRequest` and `PredictResponse`. Point to the strict string, maximum length and `validate_url`.

**Live actions:** Open http://127.0.0.1:8000/docs, expand **POST /predict**, choose **Try it out**, enter the following request and click **Execute**:

```json
{"url":"https://paypal.com@account-check.example/login"}
```

Keep the successful response visible long enough to read its main fields. Then change the JSON URL to `example.com/` and execute again. Point to **Server response 422** and the `error`, `fields` and `request_id` fields while explaining validation.

> Frontend checks help users, but attackers can bypass the interface. In schemas
> dot PY, Pydantic requires a string with a maximum of two thousand and forty-eight
> characters, and our validator requires a complete HTTP or HTTPS URL.
>
> Here in slash docs, I submit the same example directly to the API. The successful
> response contains the label, dangerous probability, confidence, URL components
> and observations. These values come from the backend, rather than fixed interface text.
> Removing the scheme returns status four twenty-two. The error uses a consistent
> JSON structure with a code, message, field details and request identifier.
> Internal stack traces and filesystem paths are not returned.

## B4 · 06:35–07:40 · Startup and real model inference

**Open, in order:** `backend/app/main.py` at `lifespan` and `predict_url`; `backend/app/service.py` at `load_model` and `predict`; `backend/src/dtdlink_ml/predict.py` at `features_from_urls` and `probability_from_features`. Show only the blocks you are explaining; avoid scrolling through entire files.

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

**Open, in order:** `service.py` at probability, confidence and label construction; `Result.jsx` at `result.label` and `result.confidence`; `URLAnalysis.jsx` at its text/span rendering. Finish on the real result screen.

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

## Understand before recording

- The JSON request contains `url`; the response comes from the backend.
- The 36-feature order must match training. Do not remove HTTPS or change the threshold for the demo.
- `predict_proba` returns class estimates; `service.py` derives confidence for the selected class.
- Hash verification occurs before joblib loading. This existing integrity control is not a third selected defence; the selected two remain DoS and misconfiguration/dependencies.
- The model combines three dangerous categories. Do not call the output phishing-only probability. Startup loads the model; it does not train it.

**Pronunciation:** JSX = “J S X”; JSON = “jay-son”; Pydantic = “pie-dantic”; FastAPI = “Fast A P I”; HTTP = “H T T P”; 422 = “four twenty-two”.
