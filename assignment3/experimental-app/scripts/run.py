"""Start the already-installed local application; Ctrl+C stops owned children."""
import argparse
import shutil
import signal
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser=argparse.ArgumentParser(); parser.add_argument('--dev',action='store_true'); args=parser.parse_args()
    def stop_owned_services(signum, frame):
        raise KeyboardInterrupt
    signal.signal(signal.SIGTERM, stop_owned_services)
    npm=shutil.which('npm')
    if not npm or not (ROOT/'frontend'/'node_modules').exists():
        raise SystemExit('Install Node.js, then run npm ci in frontend/ first.')
    if not args.dev and not (ROOT/'frontend'/'dist'/'index.html').exists():
        raise SystemExit('Run npm run build in frontend/ first, or use --dev.')
    backend=[sys.executable,'-m','uvicorn','app.main:app','--host','127.0.0.1','--port','8001','--no-access-log','--timeout-keep-alive','5']
    frontend=[npm,'run','dev' if args.dev else 'preview']
    children=[]
    try:
        for command,cwd in [(backend,ROOT/'backend'),(frontend,ROOT/'frontend')]:
            children.append(subprocess.Popen(command,cwd=cwd))
        print('DTDLINK: http://127.0.0.1:5174/ | API docs: http://127.0.0.1:8001/docs',flush=True)
        while all(child.poll() is None for child in children): time.sleep(.25)
        if any(child.returncode not in (None,0) for child in children):
            raise SystemExit('A service stopped. Read its error above; check that ports 5174 and 8001 are available.')
    except KeyboardInterrupt:
        pass
    finally:
        for child in children:
            if child.poll() is None: child.terminate()
        for child in children:
            try: child.wait(timeout=8)
            except subprocess.TimeoutExpired: child.kill(); child.wait()

if __name__=='__main__': main()
