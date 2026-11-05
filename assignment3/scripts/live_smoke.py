"""Exercise only the running project's two fixed loopback services."""
import asyncio
import json
import time
from pathlib import Path
import httpx

ROOT = Path(__file__).resolve().parents[1]


async def main():
    result = {'scope': 'Live HTTP checks of own loopback application; no destination websites contacted.', 'bursts': []}
    async with httpx.AsyncClient(base_url='http://127.0.0.1:8000', timeout=15, trust_env=False) as client:
        health = await client.get('/health')
        assert health.status_code == 200
        result['health'] = health.json()
        prediction = await client.post('/predict', json={'url': 'https://example.com/'})
        assert prediction.status_code == 200
        result['prediction'] = {k: prediction.json()[k] for k in ['label', 'model_version', 'dangerous_probability']}
        assert (await client.post('/predict', json={'url': 'https://example.com/'}, headers={'Origin': 'http://127.0.0.1:8000'})).status_code == 200
        assert (await client.post('/predict', json={'url': 'bad'})).status_code == 422
        assert (await client.get('/health', headers={'Origin': 'http://evil.example'})).status_code == 403
        assert (await client.get('/static/swagger-ui-bundle.js')).status_code == 200
        assert 'https://' not in (await client.get('/docs')).text
        for _ in range(5):
            started = time.perf_counter()
            requests = [asyncio.create_task(client.post('/predict', json={'url': 'https://example.com/'})) for _ in range(32)]
            health = await client.get('/health')
            health_ms = (time.perf_counter() - started) * 1000
            responses = await asyncio.gather(*requests)
            statuses = [r.status_code for r in responses]
            assert health.status_code == 200 and set(statuses) <= {200, 503}
            result['bursts'].append({'requests': 32, 'health_completion_ms': round(health_ms, 2), 'accepted': statuses.count(200), 'busy_503': statuses.count(503)})
        result['busy_503_total'] = sum(x['busy_503'] for x in result['bursts'])
        assert result['busy_503_total'] > 0
    async with httpx.AsyncClient(trust_env=False) as client:
        frontend = await client.get('http://127.0.0.1:5173/')
        assert frontend.status_code == 200
        policy = frontend.headers['content-security-policy']
        assert "'unsafe-inline'" not in policy and 'frame-ancestors' in policy
        result['frontend'] = {'http_status': 200, 'csp_has_no_unsafe_inline': True}
    (ROOT / 'evidence' / 'live-http.json').write_text(json.dumps(result, indent=2))
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    asyncio.run(main())
