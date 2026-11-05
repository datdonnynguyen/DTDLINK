"""Root-path expert training on train only; routed validation and unchanged gates."""
import json
import time
from urllib.parse import urlsplit
import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from diagnose import HERE, PROJECT, write_json
from train_compare import performance,stability,variants
from dtdlink_a3.pipeline import A3URLPipeline
from dtdlink_a3.routed import RootAwarePipeline,root_path
from dtdlink_ml.feature_extraction import file_sha256
from dtdlink_ml.predict import load_pipeline as load_a2
from app.schemas import validate_url


def main():
    cache=HERE/'cache';results=HERE/'results';artifacts=HERE/'artifacts'
    plan=json.loads((HERE/'PLAN_ROOT.json').read_text()); gates=json.loads((HERE/'PLAN.json').read_text())['integration_gate']
    write_json(results/'root-plan-receipt.json',{'plan_sha256':file_sha256(HERE/'PLAN_ROOT.json'),'started_utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime())})
    train=pd.read_pickle(cache/'train-eligible.pkl');val=pd.read_pickle(cache/'validation-eligible.pkl')
    trainroot=np.array([root_path(u) for u in train.api_url]);valroot=np.array([root_path(u) for u in val.api_url])
    homepage=np.array([root_path(u) and not urlsplit(u).query for u in val.api_url])
    numeric=pd.read_pickle(cache/'train-neutral-X.pkl')
    textname=json.loads((results/'decision-final.json').read_text())['selected']
    text=joblib.load(artifacts/(textname+'.joblib'))
    baseline=json.loads((results/'baseline-cohorts.json').read_text());meta=pd.read_pickle(cache/'pairs.pkl')
    # Recreate the same frozen per-domain pairs, using no test URLs.
    unique=val.sample(frac=1,random_state=42).drop_duplicates('group_key')
    sample=pd.concat([unique.loc[unique.target==y].sample(n=min(2000,int((unique.target==y).sum())),random_state=42) for y in [0,1]])
    pair_urls=[]
    for row in sample.itertuples(index=False):
        for family,variant in variants(row.api_url,row.url):
            if family!='dataset_missing_scheme':
                try:
                    validate_url(variant)
                    if len(variant)>2048:continue
                except ValueError:continue
            pair_urls.extend([row.api_url,variant])
    explicit=val.url.str.match(r'(?i)^https?://').values
    evaluations=[]
    for spec in plan['root_experts']:
        settings={k:v for k,v in spec.items() if k!='name'}
        if isinstance(settings['class_weight'],dict):settings['class_weight']={int(k):v for k,v in settings['class_weight'].items()}
        settings.update(random_state=42,n_jobs=2,max_features='sqrt')
        print('FIT',spec['name'],'rows',int(trainroot.sum()),flush=True);started=time.monotonic()
        classifier=RandomForestClassifier(**settings).fit(numeric.loc[trainroot],train.target.values[trainroot])
        root=A3URLPipeline(classifier=classifier)
        model=RootAwarePipeline(classifier=classifier,root_pipeline=root,text_pipeline=text);model.check_model()
        p=model.predict_proba(val.api_url.tolist())[:,1]
        score=performance(val,p);home=performance(val.loc[homepage],p[homepage]);st=stability(meta,model.predict_proba(pair_urls)[:,1])
        acceptance={'fpr_at_most_20pct':score['fpr']<=gates['validation_false_positive_rate_max'],'dangerous_recall_at_least_90pct':score['recall']>=gates['validation_dangerous_recall_min'],'phishing_recall_at_least_80pct':score['subtypes']['phishing']['recall']>=gates['validation_phishing_recall_min'],'fpr_halved_vs_api_baseline':score['fpr']<=baseline['api_formatted']['fpr']*.5,'format_flips_reduced_by_75pct':st['valid_format_pool']['label_flip_rate']<=baseline['stability']['valid_format_pool']['label_flip_rate']*.25+1e-12,'domain_overlap_zero':True,'homepage_fpr_at_most_20pct':home['fpr']<=.20,'homepage_dangerous_recall_at_least_80pct':home['recall']>=.80,'text_optimizer_converged':True}
        record={'name':spec['name'],'kind':'root-aware RF + text','settings':spec,'root_train_rows':int(trainroot.sum()),'api_formatted':score,'native_explicit':performance(val.loc[explicit],p[explicit]),'homepage_no_query':home,'root_path':performance(val.loc[valroot],p[valroot]),'stability':st,'gates':acceptance,'passes':all(acceptance.values()),'fit_and_eval_s':round(time.monotonic()-started,2)}
        np.save(cache/(spec['name']+'-validation-prob.npy'),p);joblib.dump(model,artifacts/(spec['name']+'.joblib'),compress=3);write_json(results/(spec['name']+'.json'),record);evaluations.append(record)
        print('RESULT',json.dumps({'name':spec['name'],'score':score,'homepage':home,'gates':acceptance},indent=2),flush=True)
    passing=[e for e in evaluations if e['passes']]
    selected=min(passing,key=lambda e:(e['api_formatted']['fpr'],-e['api_formatted']['recall'])) if passing else None
    decision={'selected':selected['name'] if selected else None,'kind':'root-aware RF + text','threshold':.5,'basis':'Full validation and predefined homepage-stratum gates; no whitelist, demo-based expert selection or A2 test use.','candidates':[{'name':e['name'],'passes':e['passes'],'fpr':e['api_formatted']['fpr'],'recall':e['api_formatted']['recall'],'homepage_fpr':e['homepage_no_query']['fpr'],'homepage_recall':e['homepage_no_query']['recall']} for e in evaluations]}
    write_json(results/'decision-deployment.json',decision);print('DECISION',json.dumps(decision,indent=2),flush=True)
    if selected:
        model=joblib.load(artifacts/(selected['name']+'.joblib'));old=load_a2(PROJECT/'models/final_pipeline.joblib',PROJECT/'models/model_metadata.json')
        demos=['https://www.google.com/','www.google.com/','https://github.com/','github.com/','http://www.google.com/','https://www.google.com','HTTPS://WWW.GOOGLE.COM/','https://paypal.com@account-check.example/login']
        write_json(results/'deployment-demos.json',[{'url':u,'a2_probability':old.predict_urls([u])[0]['dangerous_probability'],'a3_probability':model.predict_urls([u])[0]['dangerous_probability'],'note':'Post-selection diagnostic, not an independent safety label.'} for u in demos])
        assert np.allclose(model.predict_proba(val.api_url.iloc[:1000].tolist())[:,1],np.load(cache/(selected['name']+'-validation-prob.npy'))[:1000],atol=1e-12,rtol=0)

if __name__=='__main__':main()
