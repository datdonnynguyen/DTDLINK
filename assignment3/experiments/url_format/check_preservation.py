"""Verify A2 data/code/models/results remain unchanged after A3 research."""
import json
from pathlib import Path
from diagnose import HERE, PROJECT, write_json
from dtdlink_ml.feature_extraction import file_sha256


def main():
    expected=json.loads((HERE/'results/a2-protected-before.json').read_text())
    changed=[name for name,digest in expected.items() if not (PROJECT/name).is_file() or file_sha256(PROJECT/name)!=digest]
    result={'protected_files':len(expected),'changed_files':changed,'passed':not changed,
            'scope':'Original A2 data, models, reports, source, tests, notebooks and A2 source ZIP. Hash reads only; no test metrics calculated.'}
    write_json(HERE/'results/a2-preservation-after.json',result)
    assert not changed,changed
    print(json.dumps(result,indent=2))

if __name__=='__main__': main()
