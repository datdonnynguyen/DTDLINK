"""Scan only the two explicit loopback services owned by this project.

Usage: python scripts/zap_scan.py --java /path/to/java --zap /path/to/zap.jar
Requires an official OWASP ZAP distribution with standard add-ons. The scanner
uses a temporary profile and is stopped after results are saved.
"""
import argparse
import json
import os
import secrets
import subprocess
import tempfile
import time
import urllib.parse
import urllib.request
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
TARGETS=['http://127.0.0.1:5173','http://127.0.0.1:8000']


def main():
    parser=argparse.ArgumentParser(); parser.add_argument('--java',default='java'); parser.add_argument('--zap',required=True)
    parser.add_argument('--port',type=int,default=8090); parser.add_argument('--active',action='store_true',help='Run a bounded active scan against the local backend only.')
    args=parser.parse_args(); key=secrets.token_hex(20)
    evidence=ROOT/'evidence'; evidence.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='dtdlink-zap-') as folder:
        log=Path(folder)/'process.log'
        command=[args.java,'-Xmx512m','-jar',str(Path(args.zap).resolve()),'-daemon','-host','127.0.0.1','-port',str(args.port),
            '-dir',folder,'-config','api.key='+key,'-config','autoupdate.checkOnStart=false',
            '-config','autoupdate.downloadNewRelease=false','-config','connection.timeoutInSecs=10']
        process=subprocess.Popen(command,stdout=log.open('w'),stderr=subprocess.STDOUT,cwd=str(Path(args.zap).resolve().parent))
        opener=urllib.request.build_opener(urllib.request.ProxyHandler({}))
        def api(path,**parameters):
            query=urllib.parse.urlencode({'apikey':key,**parameters})
            with opener.open(f'http://127.0.0.1:{args.port}/JSON/{path}/?{query}',timeout=20) as response:
                return json.load(response)
        def wait_until(check,deadline=90):
            start=time.monotonic()
            while time.monotonic()-start<deadline:
                try:
                    if check(): return
                except Exception:
                    if process.poll() is not None: break
                time.sleep(.5)
            raise RuntimeError('ZAP did not finish this phase; inspect the saved local log.')
        try:
            wait_until(lambda:bool(api('core/view/version').get('version')))
            version=api('core/view/version')['version']
            api('context/action/newContext',contextName='DTDLINK-local-only')
            api('context/action/includeInContext',contextName='DTDLINK-local-only',regex=r'http://127\.0\.0\.1:(5173|8000)(/.*)?')
            api('context/action/setContextInScope',contextName='DTDLINK-local-only',booleanInScope='true')
            for target in TARGETS:
                for path in (['/','/insights','/how-it-works','/missing'] if target.endswith('5173') else ['/health','/model-info','/docs','/openapi.json','/missing']):
                    api('core/action/accessUrl',url=target+path,followRedirects='false')
            payload=json.dumps({'url':'https://example.com/'})
            request='POST http://127.0.0.1:8000/predict HTTP/1.1\r\nHost: 127.0.0.1:8000\r\nContent-Type: application/json\r\nContent-Length: '+str(len(payload))+'\r\n\r\n'+payload
            api('core/action/sendRequest',request=request,followRedirects='false')
            phases=['passive']
            if args.active:
                api('ascan/action/setOptionMaxScanDurationInMins',Integer=1)
                scan=api('ascan/action/scan',url='http://127.0.0.1:8000',recurse='true',inScopeOnly='true')['scan']
                wait_until(lambda:api('ascan/view/status',scanId=scan)['status']=='100',deadline=180)
                phases.append('bounded-active-backend')
            wait_until(lambda:api('pscan/view/recordsToScan')['recordsToScan']=='0')
            alerts=api('core/view/alerts',start=0,count=1000)['alerts']
            summary={'tool':'OWASP ZAP','version':version,'phases':phases,'targets':TARGETS,'alerts':alerts,
                     'scope_note':'Only explicit project loopback services; no destination URLs submitted to DTDLINK are fetched.'}
            (evidence/'zap-scan.json').write_text(json.dumps(summary,indent=2))
            print(json.dumps({'version':version,'phases':phases,'alerts':len(alerts),'risk_counts':{risk:sum(x['risk']==risk for x in alerts) for risk in ['High','Medium','Low','Informational']}},indent=2))
        finally:
            process.terminate()
            try: process.wait(timeout=10)
            except subprocess.TimeoutExpired: process.kill(); process.wait()
            # Remove the ephemeral scanner API key from the diagnostic log.
            (evidence/'zap-process.log').write_text(log.read_text(errors='replace').replace(key,'[REDACTED]'))

if __name__=='__main__': main()
