"""Build A3-only eligible feature caches, retaining the frozen A2 split."""
import json
import sys
from collections import Counter
from pathlib import Path
import time

import idna
import numpy as np
import pandas as pd

from diagnose import HERE, PROJECT, BACKEND, FEATURE_NAMES, write_json
sys.path.insert(0,str(BACKEND/'src'))
from app.schemas import validate_url
from dtdlink_a3.representation import complete_http_url, model_features
from dtdlink_ml.feature_extraction import extract_features


def wire_group(key):
    if not key.startswith('domain:'):
        return key
    value = key[7:]
    try:
        return 'domain:' + idna.encode(value, uts46=True).decode('ascii').lower().rstrip('.')
    except idna.IDNAError:
        return key.lower()


def main():
    cache=HERE/'cache'; results=HERE/'results'
    manifest=pd.read_csv(PROJECT/'data/processed/split_manifest.csv',keep_default_na=False)
    manifest['wire_group']=manifest.group_key.map(wire_group)
    groups={s:set(manifest.loc[manifest['split']==s,'wire_group']) for s in ['train','validation','test']}
    overlaps={f'{a}_{b}':len(groups[a]&groups[b]) for a,b in [('train','validation'),('train','test'),('validation','test')]}
    # Do not reassign rows or tune against test. Fail closed on canonical-group overlap.
    if any(overlaps.values()):
        raise RuntimeError(f'Wire-domain split overlaps need resolution before training: {overlaps}')
    audit={'wire_domain_overlaps':overlaps,'test':'Only split group metadata inspected; no test URLs, labels or features retained/scored.'}
    for split in ['train','validation']:
        raw=pd.read_pickle(cache/f'{split}-raw.pkl')
        rows=[]; neutral=[]; api=[]; reasons=Counter(); excluded=Counter(); started=time.monotonic()
        for i,row in enumerate(raw.itertuples(index=False)):
            try:
                complete=complete_http_url(row.url)
                validate_url(complete)
                if len(complete)>2048:
                    raise ValueError('overlength')
            except ValueError as exc:
                reasons[str(exc)]+=1; excluded[row.type]+=1
                continue
            rows.append((i,complete))
            neutral.append(model_features(complete))
            api.append(extract_features(complete))
            if len(rows)%50000==0:
                print(split,len(rows),'eligible',round(time.monotonic()-started,1),'s',flush=True)
        indices=[i for i,_ in rows]
        frame=raw.iloc[indices].copy().reset_index(drop=True)
        frame['api_url']=[url for _,url in rows]
        frame.to_pickle(cache/f'{split}-eligible.pkl')
        pd.DataFrame(neutral,columns=FEATURE_NAMES).to_pickle(cache/f'{split}-neutral-X.pkl')
        pd.DataFrame(api,columns=FEATURE_NAMES).to_pickle(cache/f'{split}-api-X.pkl')
        audit[split]={'source_rows':len(raw),'eligible_rows':len(frame),'excluded_rows':len(raw)-len(frame),'exclusion_reasons':dict(reasons),'excluded_labels':dict(excluded),'eligible_labels':{str(k):int(v) for k,v in frame.type.value_counts().items()},'elapsed_s':round(time.monotonic()-started,2)}
        print(json.dumps({split:audit[split]},indent=2),flush=True)
    write_json(results/'eligibility-and-domain-audit.json',audit)

if __name__=='__main__': main()
