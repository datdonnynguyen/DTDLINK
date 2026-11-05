"""Post-selection, population-level check prompted by unresolved homepage scores."""
import json
from urllib.parse import urlsplit
import numpy as np
import pandas as pd
from diagnose import HERE, write_json, metrics


def main():
    cache=HERE/'cache';results=HERE/'results'
    output={'reason':'Overall selected model still scored the requested homepage examples very high. Audit all root paths, not just those domains; no demo-derived training records.'}
    for split in ['train','validation']:
        frame=pd.read_pickle(cache/f'{split}-eligible.pkl')
        parts=frame.api_url.map(urlsplit)
        root=np.array([p.path in ('','/') for p in parts]);homepage=np.array([p.path in ('','/') and not p.query for p in parts])
        flags=pd.DataFrame({'type':frame.type,'root_path':root,'homepage_no_query':homepage})
        counts=flags.groupby('type').agg(rows=('root_path','size'),root_paths=('root_path','sum'),homepages=('homepage_no_query','sum')).reset_index()
        counts.to_csv(results/f'{split}-root-distribution.csv',index=False)
        output[split]=counts.to_dict(orient='records')
        if split=='validation':
            from dtdlink_ml.predict import load_pipeline
            from diagnose import PROJECT,FEATURE_NAMES
            old=load_pipeline(PROJECT/'models/final_pipeline.joblib',PROJECT/'models/model_metadata.json')
            oldp=old.probability_from_features(pd.read_pickle(cache/'validation-api-X.pkl'))
            selected=json.loads((results/'decision-final.json').read_text())['selected']
            newp=np.load(cache/(selected+'-validation-prob.npy'))
            for name,mask in [('root_path',root),('homepage_no_query',homepage),('non_root',~root)]:
                output[name]={'a2_api':metrics(frame.target.values[mask],oldp[mask]),'selected_text':metrics(frame.target.values[mask],newp[mask])}
    write_json(results/'root-path-audit.json',output)
    print(json.dumps(output,indent=2))

if __name__=='__main__':main()
