"""Build a small reproducible source ZIP without secrets, caches or environments."""
import hashlib
import json
import zipfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
OUTPUT=ROOT.parent/'submission'/'session-07-group-5-assignment-3-source.zip'
SKIP_DIRS={'.venv','node_modules','__pycache__','.pytest_cache','dist','test-results','playwright-report','.git','.tools','cache','artifacts','experimental-app'}


def main():
    OUTPUT.parent.mkdir(exist_ok=True)
    files=[]
    for path in sorted(ROOT.rglob('*')):
        relative=path.relative_to(ROOT)
        if not path.is_file() or any(part in SKIP_DIRS for part in relative.parts): continue
        if path.name in {'.env','.DS_Store'} or path.suffix in {'.pyc','.log'}: continue
        if path.name.endswith('.zip'): continue
        files.append(path)
    manifest={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
    with zipfile.ZipFile(OUTPUT,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as archive:
        for path in files: archive.write(path,Path('dtdlink-assignment3')/path.relative_to(ROOT))
        archive.writestr('dtdlink-assignment3/SHA256SUMS.json',json.dumps(manifest,indent=2))
    with zipfile.ZipFile(OUTPUT) as archive:
        assert archive.testzip() is None
        for filename,digest in manifest.items():
            assert hashlib.sha256(archive.read('dtdlink-assignment3/'+filename)).hexdigest()==digest
    print(json.dumps({'zip':str(OUTPUT),'files':len(files)+1,'bytes':OUTPUT.stat().st_size,
                      'sha256':hashlib.sha256(OUTPUT.read_bytes()).hexdigest()},indent=2))

if __name__=='__main__': main()
