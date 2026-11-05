"""Local-only comparison of blocking inference and the production capacity guard.

The burst uses actual model calls. The slow-request case deliberately repeats
inference inside a test-only predictor to control the workload; it is NOT a
claim that a particular submitted URL naturally causes that amount of work.
"""
import asyncio
import json
import statistics
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))
from app.config import Settings
from app.main import create_app
from app.schemas import PredictRequest
from app.service import load_model, predict
from fastapi import FastAPI
import httpx

URL = "https://example.com/" + "a" * 1800


def unprotected_app(model, predictor):
    app = FastAPI()
    @app.get('/health')
    async def health(): return {'status':'ready'}
    @app.post('/predict')
    async def analyse(payload: PredictRequest):
        return predictor(model, payload.url, 'local-lab')
    return app


async def measure(app, concurrent):
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app),base_url='http://local-lab',timeout=30) as client:
        started=time.perf_counter()
        requests=[asyncio.create_task(client.post('/predict',json={'url':URL})) for _ in range(concurrent)]
        probe=asyncio.create_task(client.get('/health'))
        health=await probe
        health_ms=(time.perf_counter()-started)*1000
        responses=await asyncio.gather(*requests)
        return {'health_status':health.status_code,'health_completion_ms':round(health_ms,2),
                'prediction_200':sum(r.status_code==200 for r in responses),'prediction_503':sum(r.status_code==503 for r in responses),
                'other_statuses':[r.status_code for r in responses if r.status_code not in (200,503)],
                'total_ms':round((time.perf_counter()-started)*1000,2)}


async def run():
    model=load_model()
    results={'scope':'Own in-process ASGI application only; no external target, no production defence switch.',
             'burst':{'concurrent_requests':32,'repetitions':10,'baseline':[],'defended':[]},
             'controlled_slow_request':{'inference_repeats':30,'repetitions':5,'baseline':[],'defended':[],
             'qualification':'Test-only predictor repeats real inference 30 times; not a discovered expensive-URL exploit.'}}
    def controlled_slow(model,url,request_id):
        output=None
        for _ in range(30): output=predict(model,url,request_id)
        return output
    for key,predictor,n,repeats in [('burst',predict,32,10),('controlled_slow_request',controlled_slow,1,5)]:
        baseline=unprotected_app(model,predictor)
        defended=create_app(settings=Settings(max_concurrent=2),model_loader=lambda:model,predictor=predictor)
        async with defended.app.router.lifespan_context(defended.app):
            for _ in range(repeats):
                results[key]['baseline'].append(await measure(baseline,n))
                results[key]['defended'].append(await measure(defended,n))
        for variant in ['baseline','defended']:
            measurements=results[key][variant]
            results[key][variant+'_summary']={
                'median_health_completion_ms':round(statistics.median(x['health_completion_ms'] for x in measurements),2),
                'maximum_health_completion_ms':max(x['health_completion_ms'] for x in measurements),
                'prediction_200':sum(x['prediction_200'] for x in measurements),
                'prediction_503':sum(x['prediction_503'] for x in measurements)}
        print(key,json.dumps({v:results[key][v+'_summary'] for v in ['baseline','defended']}),flush=True)
    path=ROOT/'evidence'/'dos-demo.json'; path.parent.mkdir(exist_ok=True)
    path.write_text(json.dumps(results,indent=2))
    assert all(not x['other_statuses'] and x['health_status']==200 for case in ['burst','controlled_slow_request'] for variant in ['baseline','defended'] for x in results[case][variant])
    assert results['burst']['defended_summary']['prediction_503']>0
    print('Saved',path)

if __name__=='__main__': asyncio.run(run())
