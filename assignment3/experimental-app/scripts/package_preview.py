"""Create a distinct preview ZIP, without touching the primary submission."""
import hashlib,json,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
OUTPUT=(ROOT.parents[1] if ROOT.parent.name == 'assignment3' else ROOT.parent)/'submission/session-07-group-5-assignment-3-experimental-preview.zip'
SKIP={'.venv','node_modules','__pycache__','.pytest_cache','dist','test-results','playwright-report','.git'}

def main():
 files=[p for p in sorted(ROOT.rglob('*')) if p.is_file() and not any(part in SKIP for part in p.relative_to(ROOT).parts) and p.name not in {'.env','.DS_Store'} and p.suffix not in {'.pyc','.log','.zip'}]
 manifest={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
 OUTPUT.parent.mkdir(exist_ok=True)
 with zipfile.ZipFile(OUTPUT,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
  for p in files:z.write(p,Path('dtdlink-experimental-preview')/p.relative_to(ROOT))
  z.writestr('dtdlink-experimental-preview/SHA256SUMS.json',json.dumps(manifest,indent=2))
 with zipfile.ZipFile(OUTPUT) as z:
  assert z.testzip() is None
  for name,digest in manifest.items():assert hashlib.sha256(z.read('dtdlink-experimental-preview/'+name)).hexdigest()==digest
 print(json.dumps({'zip':str(OUTPUT),'files':len(manifest)+1,'bytes':OUTPUT.stat().st_size,'sha256':hashlib.sha256(OUTPUT.read_bytes()).hexdigest()},indent=2))

if __name__=='__main__':main()
