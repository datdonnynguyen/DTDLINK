"""FastAPI endpoints. All expensive inference runs outside the event loop."""
import asyncio
import json
from contextlib import asynccontextmanager
from concurrent.futures import ThreadPoolExecutor

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from starlette.exceptions import HTTPException

from .config import BACKEND, MAX_BODY_BYTES, MAX_URL_LENGTH, Settings
from .middleware import SecurityBoundary, error_response
from .schemas import ErrorResponse, HealthResponse, ModelInfo, PredictRequest, PredictResponse
from .service import MODEL_VERSION, load_model, predict

ERRORS = {status: {"model": ErrorResponse, "description": description} for status, description in {
    400: "Malformed request", 403: "Origin not allowed", 408: "Body read timeout", 413: "Request body too large",
    415: "JSON required", 422: "Input validation failed", 500: "Prediction failed", 503: "Inference capacity exhausted"}.items()}
ERRORS[200] = {"description": "A real model result; illustrative timing only.", "content": {"application/json": {
    "example": json.loads((BACKEND / "examples" / "prediction.json").read_text())}}}


def create_app(settings=None, model_loader=load_model, predictor=predict):
    settings = settings or Settings.from_env()

    @asynccontextmanager
    async def lifespan(api):
        api.state.model = model_loader()
        api.state.active = 0
        api.state.pool = ThreadPoolExecutor(max_workers=settings.max_concurrent, thread_name_prefix="dtdlink-inference")
        try:
            yield
        finally:
            api.state.pool.shutdown(wait=True, cancel_futures=True)
            api.state.model = None

    api = FastAPI(title="DTDLINK API", version="1.0.0", lifespan=lifespan, docs_url=None, redoc_url=None,
                  description="Offline URL-text classification using the frozen Assignment 2 Random Forest. No destination requests or URL storage.")

    @api.exception_handler(RequestValidationError)
    async def validation_error(request, exc):
        fields = []
        for issue in exc.errors():
            location = ".".join(str(x) for x in issue.get("loc", []) if x != "body") or "body"
            kind = issue.get("type", "")
            message = issue.get("msg", "Invalid input.")
            if kind == "json_invalid":
                message = "Send a valid JSON object."
            fields.append({"field": location, "message": message})
        return error_response("validation_error", "Check the submitted input.", request.state.request_id, 422, fields)

    @api.exception_handler(HTTPException)
    async def http_error(request, exc):
        messages = {404: ("not_found", "This API endpoint does not exist."), 405: ("method_not_allowed", "This HTTP method is not supported.")}
        code, message = messages.get(exc.status_code, ("http_error", "The request was rejected."))
        return error_response(code, message, request.state.request_id, exc.status_code, headers=exc.headers)

    @api.exception_handler(Exception)
    async def unexpected_error(request, exc):
        return error_response("internal_error", "The request could not be completed. Try again.", request.state.request_id, 500)

    @api.get("/health", response_model=HealthResponse, summary="Check service readiness",
             description="Checks that the model has loaded and reports current inference capacity. Does not run a prediction.",
             responses={200: {"content": {"application/json": {"example": {"status": "ready", "model_loaded": True,
             "model_version": MODEL_VERSION, "feature_count": 36, "max_concurrent": 2, "active_predictions": 0}}}}})
    async def health():
        return dict(status="ready", model_loaded=api.state.model is not None, model_version=MODEL_VERSION,
                    feature_count=36, max_concurrent=settings.max_concurrent, active_predictions=api.state.active)

    @api.get("/model-info", response_model=ModelInfo, summary="Read model scope and input limits",
             description="Example request: GET /model-info (no body). Public configuration; no filesystem paths or model bytes.",
             responses={200: {"content": {"application/json": {"example": {
                 "name": "Random Forest", "version": MODEL_VERSION, "feature_count": 36, "threshold": 0.5,
                 "labels": {"0": "Likely legitimate", "1": "Potentially dangerous"},
                 "limits": {"url_characters": 2048, "request_bytes": 16384},
                 "limitations": ["Combined class; not phishing-only.", "Uncalibrated probabilities."]}}}}})
    async def model_info():
        return dict(name="Random Forest", version=MODEL_VERSION, feature_count=36, threshold=0.5,
                    labels={"0": "Likely legitimate", "1": "Potentially dangerous"},
                    limits={"url_characters": MAX_URL_LENGTH, "request_bytes": MAX_BODY_BYTES},
                    limitations=["Combined phishing/malware/defacement class, not phishing-only.", "Probabilities are not calibrated.",
                                 "Predictions are sensitive to URL formatting and encoding.", "No website content, reputation or DNS is checked."])

    @api.post("/predict", response_model=PredictResponse, responses=ERRORS,
              summary="Analyse one URL without visiting it",
              description="Validates one HTTP(S) URL, applies the unchanged A2 36-feature extractor, and returns a real model result. Observed signals are not model feature attributions.")
    async def predict_url(payload: PredictRequest, request: Request):
        # Check and reserve with no await between them: atomic within this single event loop.
        if api.state.active >= settings.max_concurrent:
            return error_response("server_busy", "All analysis slots are busy. Try again shortly.", request.state.request_id,
                                  503, headers={"Retry-After": "1"})
        api.state.active += 1
        loop = asyncio.get_running_loop()
        try:
            work = loop.run_in_executor(api.state.pool, predictor, api.state.model, payload.url, request.state.request_id)
        except Exception:
            api.state.active -= 1
            raise
        # A client disconnect/cancellation must not release a slot while its thread is still running.
        work.add_done_callback(lambda _: setattr(api.state, "active", api.state.active - 1))
        try:
            return await asyncio.shield(work)
        except Exception:
            return error_response("prediction_failed", "The model could not analyse this URL. Try again.", request.state.request_id, 500)

    static_dir = BACKEND / "static"
    if static_dir.exists():
        api.mount("/static", StaticFiles(directory=static_dir), name="static")

    @api.get("/docs", response_class=HTMLResponse, include_in_schema=False)
    async def docs():
        return """<!doctype html><html lang="en"><head><meta charset="utf-8"><title>DTDLINK API documentation</title>
        <link rel="stylesheet" href="/static/swagger-ui.css"></head><body><div id="swagger-ui"></div>
        <script src="/static/swagger-ui-bundle.js"></script><script src="/static/docs.js"></script></body></html>"""

    return SecurityBoundary(api, settings)

app = create_app()
