"""Security boundaries and integration tests for the real saved artifact."""
import asyncio
import socket
import threading

import httpx
import pytest
from fastapi.testclient import TestClient
from app.config import BACKEND, MODEL_SHA256, Settings
from app.main import create_app
from app.service import load_model, predict
from dtdlink_ml.feature_extraction import file_sha256

@pytest.fixture(scope="session")
def model():
    return load_model()

@pytest.fixture
def client(model):
    with TestClient(create_app(model_loader=lambda: model), raise_server_exceptions=False) as c:
        yield c


def assert_error(response, status, code=None):
    assert response.status_code == status
    data = response.json()
    assert set(data) == {"error", "request_id"}
    assert set(data["error"]) == {"code", "message", "fields"}
    assert len(data["request_id"]) == 32
    assert response.headers["x-request-id"] == data["request_id"]
    assert response.headers["cache-control"] == "no-store"
    assert response.headers["x-content-type-options"] == "nosniff"
    if code:
        assert data["error"]["code"] == code
    assert "Traceback" not in response.text
    return data


def test_real_prediction_matches_original_model(client, model):
    url = "https://paypal.com@account-check.example/login"
    response = client.post("/predict", json={"url": url})
    assert response.status_code == 200
    data = response.json(); expected = model.predict_urls([url])[0]
    assert data["dangerous_probability"] == pytest.approx(expected["dangerous_probability"], abs=1e-12)
    assert data["predicted_class"] == expected["predicted_class"]
    assert data["confidence"] == pytest.approx(expected["dangerous_probability"] if expected["predicted_class"] else 1-expected["dangerous_probability"])
    assert data["components"]["host"] == "account-check.example"
    assert any(s["id"] == "userinfo" and s["present"] for s in data["signals"])
    assert "url" not in data
    assert "".join(part["text"] for part in data["url_parts"]) == url
    hidden = next(s for s in data["signals"] if s["id"] == "userinfo")
    assert {"label": "Actual host", "value": "account-check.example"} in hidden["evidence"]
    assert hidden["action"]


@pytest.mark.parametrize("value", [None, 12, "", "example.com/", "javascript:alert(1)", "https://", "https://[broken",
    "https://example.com:99999/", "https://example.com:0/", "https://example.com/a b", "https://example.com/\n",
    "https://example.com/%00", "https://example.com/%250a", "https://example.com/%zz", "https://999.999.999.999/",
    "https://bad_host.example/", "https://example.com/" + "a" * 2048])
def test_invalid_input_rejected_before_model(client, value):
    assert_error(client.post("/predict", json={"url": value}), 422, "validation_error")


@pytest.mark.parametrize("url", ["https://[::1]/", "http://192.0.2.1:8080/login", "HTTPS://EXAMPLE.COM/", "https://раypal.example/login"])
def test_valid_edge_cases(client, url):
    assert client.post("/predict", json={"url": url}).status_code == 200


def test_error_formats(client):
    assert_error(client.post("/predict", content="{", headers={"content-type":"application/json"}), 422)
    assert_error(client.post("/predict", json={"url":"https://example.com/","extra":"secret"}), 422)
    assert_error(client.post("/predict", content="hello"), 415)
    assert_error(client.post("/predict", content="a" * 20000, headers={"content-type":"application/json"}), 413)
    assert_error(client.get("/missing"), 404)
    assert_error(client.get("/predict"), 405)


def test_exact_cors_and_preflight(client):
    origin="http://127.0.0.1:5174"
    assert client.get("/health",headers={"Origin":origin}).headers["access-control-allow-origin"]==origin
    rejected=client.get("/health",headers={"Origin":"http://evil.example"})
    assert_error(rejected,403,"origin_not_allowed")
    assert "access-control-allow-origin" not in rejected.headers
    response=client.options("/predict",headers={"Origin":origin,"Access-Control-Request-Method":"POST","Access-Control-Request-Headers":"Content-Type"})
    assert response.status_code==204
    assert_error(client.options("/predict",headers={"Origin":origin,"Access-Control-Request-Method":"DELETE"}),400)
    assert client.post("/predict",json={"url":"bad"},headers={"Origin":origin}).headers["access-control-allow-origin"]==origin
    docs_request=client.post('/predict',json={'url':'https://example.com/'},headers={'Origin':'http://127.0.0.1:8001'})
    assert docs_request.status_code==200
    assert 'access-control-allow-origin' not in docs_request.headers


def test_loads_only_once(model):
    calls=[]
    def loader():
        calls.append(True); return model
    with TestClient(create_app(model_loader=loader)) as c:
        for _ in range(3): assert c.post("/predict",json={"url":"https://example.com/"}).status_code==200
        assert c.get("/health").json()["model_loaded"]
    assert len(calls)==1


def test_unexpected_prediction_failure_is_sanitized(model):
    def broken(*args): raise RuntimeError("SECRET /private/internal/path")
    with TestClient(create_app(model_loader=lambda:model,predictor=broken),raise_server_exceptions=False) as c:
        response=c.post("/predict",json={"url":"https://example.com/"})
        assert_error(response,500,"prediction_failed")
        assert "SECRET" not in response.text and "private" not in response.text
        assert c.get('/health').json()['active_predictions']==0


def test_offline_model_and_hash(model, monkeypatch):
    def forbidden(*args,**kwargs): raise AssertionError("Network access during inference")
    monkeypatch.setattr(socket.socket,"connect",forbidden)
    monkeypatch.setattr(socket,"getaddrinfo",forbidden)
    assert 0 <= predict(model,"https://example.com/%69ndex.php","test")["dangerous_probability"] <= 1
    assert file_sha256(BACKEND/"models/final_pipeline.joblib")==MODEL_SHA256


def test_tampered_model_rejected_before_deserialization(tmp_path, monkeypatch):
    import app.service as service
    models=tmp_path/'models'; models.mkdir(); (models/'final_pipeline.joblib').write_bytes(b'untrusted')
    monkeypatch.setattr(service,'BACKEND',tmp_path)
    called=[]; monkeypatch.setattr(service,'load_pipeline',lambda *args:called.append(True))
    with pytest.raises(RuntimeError,match='integrity'): service.load_model()
    assert not called


def test_docs_and_openapi_contracts(client, model):
    schema=client.get('/openapi.json').json()
    assert schema['paths']['/predict']['post']['requestBody']
    assert '503' in schema['paths']['/predict']['post']['responses']
    assert schema['components']['schemas']['PredictRequest']['properties']['url']['maxLength']==2048
    assert client.get('/docs').status_code==200
    assert 'https://' not in client.get('/docs').text
    assert client.get('/model-info').json()['feature_count']==model.features_from_urls(['https://example.com/']).shape[1]


def test_busy_inference_keeps_health_responsive_and_excess_is_503(model):
    started=threading.Event(); release=threading.Event()
    def slow(*args):
        started.set(); assert release.wait(3); return predict(*args)
    async def scenario():
        app=create_app(settings=Settings(max_concurrent=1),model_loader=lambda:model,predictor=slow)
        async with app.app.router.lifespan_context(app.app):
            async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app),base_url='http://test') as c:
                task=asyncio.create_task(c.post('/predict',json={'url':'https://example.com/'}))
                try:
                    while not started.is_set(): await asyncio.sleep(.001)
                    health=await asyncio.wait_for(c.get('/health'),timeout=.3)
                    assert health.status_code==200 and health.json()['active_predictions']==1
                    assert_error(await c.post('/predict',json={'url':'https://example.com/'}),503,'server_busy')
                finally:
                    release.set(); assert (await task).status_code==200
                assert (await c.post('/predict',json={'url':'https://example.com/'})).status_code==200
    asyncio.run(scenario())


def test_cancellation_does_not_release_running_slot(model):
    started=threading.Event(); release=threading.Event()
    def slow(*args):
        started.set(); release.wait(3); return predict(*args)
    async def scenario():
        app=create_app(settings=Settings(max_concurrent=1),model_loader=lambda:model,predictor=slow)
        async with app.app.router.lifespan_context(app.app):
            async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app),base_url='http://test') as c:
                task=asyncio.create_task(c.post('/predict',json={'url':'https://example.com/'}))
                try:
                    while not started.is_set(): await asyncio.sleep(.001)
                    task.cancel()
                    with pytest.raises(asyncio.CancelledError): await task
                    assert_error(await c.post('/predict',json={'url':'https://example.com/'}),503)
                finally:
                    release.set()
                    while app.app.state.active: await asyncio.sleep(.005)
    asyncio.run(scenario())


def test_chunked_size_limit_and_slow_body(model):
    async def scenario():
        app=create_app(settings=Settings(body_timeout=.03),model_loader=lambda:model)
        async with app.app.router.lifespan_context(app.app):
            async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app),base_url='http://test') as c:
                async def oversized():
                    for _ in range(20): yield b'a'*1024
                assert_error(await c.post('/predict',content=oversized(),headers={'content-type':'application/json'}),413)
                async def slow():
                    yield b'{'; await asyncio.sleep(.1); yield b'}'
                assert_error(await c.post('/predict',content=slow(),headers={'content-type':'application/json'}),408)
    asyncio.run(scenario())


def test_unexpected_response_schema_failure_uses_shared_error(model):
    with TestClient(create_app(model_loader=lambda:model,predictor=lambda *args:{}),raise_server_exceptions=False) as c:
        assert_error(c.post('/predict',json={'url':'https://example.com/'}),500,'internal_error')
