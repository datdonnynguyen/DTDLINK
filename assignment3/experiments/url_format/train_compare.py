"""Predeclared train-only fits; validation-only selection; no A2 test scoring."""
import json
import sys
import time
from pathlib import Path
from urllib.parse import urlsplit
import re

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier

from diagnose import HERE, PROJECT, BACKEND, FEATURE_NAMES, metrics, write_json
from dtdlink_ml.predict import load_pipeline as load_a2
from dtdlink_ml.feature_extraction import extract_features, file_sha256
from dtdlink_a3.pipeline import A3URLPipeline
from dtdlink_a3.representation import model_features, POLICY_ID
from app.schemas import validate_url


def performance(frame, probabilities):
    output=metrics(frame.target,probabilities)
    output['subtypes']={}
    for label in ['phishing','malware','defacement']:
        mask=(frame.type==label).values
        output['subtypes'][label]={'rows':int(mask.sum()),'recall':float((probabilities[mask]>=.5).mean()) if mask.any() else None}
    grouped=pd.DataFrame({'group':frame.group_key.values,'y':frame.target.values,'alert':probabilities>=.5}).groupby(['group','y']).alert.mean().reset_index()
    output['domain_macro_fpr']=float(grouped.loc[grouped.y==0,'alert'].mean())
    output['domain_macro_recall']=float(grouped.loc[grouped.y==1,'alert'].mean())
    return output


def variants(url, source):
    parts=urlsplit(url)
    authority=parts.netloc
    userinfo,sep,host_port=authority.rpartition('@')
    if not sep: userinfo,host_port='',authority
    else: userinfo+='@'
    values=[('host_scheme_case',parts.scheme.upper()+'://'+userinfo+host_port.upper()+url[len(parts.scheme)+3+len(authority):])]
    if parts.path in ('','/'):
        end = len(parts.scheme)+3+len(authority)
        values.append(('empty_root_slash',url[:end]+('' if parts.path=='/' else '/')+url[end+len(parts.path):]))
    if parts.port is None:
        port=80 if parts.scheme.lower()=='http' else 443
        values.append(('default_port',url[:len(parts.scheme)+3]+authority+f':{port}'+url[len(parts.scheme)+3+len(authority):]))
        # This is a transport stress test, not a claim of resource equivalence.
        values.append(('http_https_transport',('http' if parts.scheme.lower()=='https' else 'https')+url[len(parts.scheme):]))
    if source != url:
        values.append(('dataset_missing_scheme',source))
    if re.search(r'%[0-9a-fA-F]{2}',url):
        values.append(('percent_hex_case',re.sub(r'%[0-9a-fA-F]{2}',lambda m:m.group().upper(),url)))
    return [(name,value) for name,value in values if value!=url]


def build_pairs(frame,cache):
    # One URL per group, then equal class sample; membership frozen before fits.
    unique=frame.sample(frac=1,random_state=42).drop_duplicates('group_key')
    sample=pd.concat([unique.loc[unique.target==y].sample(n=min(2000,int((unique.target==y).sum())),random_state=42) for y in [0,1]])
    sample[['url_id','group_key','target']].to_csv(HERE/'results/stability-sample.csv',index=False)
    records=[]; old=[]; new=[]
    for row in sample.itertuples(index=False):
        for family,variant in variants(row.api_url,row.url):
            if family!='dataset_missing_scheme':
                try:
                    validate_url(variant)
                    if len(variant)>2048: continue
                except ValueError:
                    continue
            records.append({'family':family,'url_id':row.url_id,'group_key':row.group_key,'target':row.target})
            old.extend([extract_features(row.api_url),extract_features(variant)])
            new.extend([model_features(row.api_url),model_features(variant)])
    meta=pd.DataFrame(records)
    meta.to_pickle(cache/'pairs.pkl')
    Xold=pd.DataFrame(old,columns=FEATURE_NAMES); Xnew=pd.DataFrame(new,columns=FEATURE_NAMES)
    Xold.to_pickle(cache/'pairs-api-X.pkl');Xnew.to_pickle(cache/'pairs-neutral-X.pkl')
    return meta,Xold,Xnew


def stability(meta,probabilities):
    pair=np.asarray(probabilities).reshape(-1,2)
    flip=(pair[:,0]>=.5)!=(pair[:,1]>=.5)
    delta=np.abs(pair[:,0]-pair[:,1])
    out={}
    for family in sorted(meta.family.unique()):
        mask=meta.family.values==family
        out[family]={'pairs':int(mask.sum()),'label_flips':int(flip[mask].sum()),'label_flip_rate':float(flip[mask].mean()),'mean_score_change':float(delta[mask].mean()),'p95_score_change':float(np.quantile(delta[mask],.95)),'max_score_change':float(delta[mask].max())}
    equiv=meta.family.isin(['host_scheme_case','empty_root_slash','default_port','percent_hex_case']).values
    out['valid_format_pool']={'pairs':int(equiv.sum()),'label_flips':int(flip[equiv].sum()),'label_flip_rate':float(flip[equiv].mean()),'max_score_change':float(delta[equiv].max())}
    return out


def main():
    plan=json.loads((HERE/'PLAN.json').read_text())
    cache=HERE/'cache';results=HERE/'results';artifacts=HERE/'artifacts';artifacts.mkdir(exist_ok=True)
    write_json(results/'training-plan-receipt.json',{'plan_sha256':file_sha256(HERE/'PLAN.json'),'training_started_utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'threshold':.5,'no_test_use':True})
    train=pd.read_pickle(cache/'train-eligible.pkl');val=pd.read_pickle(cache/'validation-eligible.pkl')
    Xtrain=pd.read_pickle(cache/'train-neutral-X.pkl');Xval=pd.read_pickle(cache/'validation-neutral-X.pkl');Xapi=pd.read_pickle(cache/'validation-api-X.pkl')
    assert len(train)==len(Xtrain) and len(val)==len(Xval)
    assert set(train.group_key).isdisjoint(set(val.group_key))
    # Explicitly audit canonical feature/label collisions; never relabel or duplicate demos.
    key=pd.util.hash_pandas_object(Xtrain,index=False)
    collision=pd.DataFrame({'feature_key':key,'label':train.target.values}).groupby('feature_key').label.nunique()
    write_json(results/'feature-collision-audit.json',{'feature_vectors_with_both_labels':int((collision>1).sum()),'note':'Different URLs can share the 36 coarse features; original labels retained.'})
    for i in [0,len(train)//2,len(train)-1]:
        assert Xtrain.iloc[i].to_dict()==model_features(train.iloc[i].api_url)
    meta,Xpairs_old,Xpairs_new=build_pairs(val,cache)
    old=load_a2(PROJECT/'models/final_pipeline.joblib',PROJECT/'models/model_metadata.json')
    old_prob=old.probability_from_features(Xapi)
    raw_prob=old.probability_from_features(val.loc[:,list(FEATURE_NAMES)])
    explicit=val.url.str.match(r'(?i)^https?://').values
    baseline={'api_formatted':performance(val,old_prob),'raw_eligible':performance(val,raw_prob),'native_explicit':performance(val.loc[explicit],old_prob[explicit]),'stability':stability(meta,old.probability_from_features(Xpairs_old))}
    write_json(results/'baseline-cohorts.json',baseline)
    print('BASELINE',json.dumps({'api':baseline['api_formatted'],'raw':baseline['raw_eligible'],'format':baseline['stability']['valid_format_pool']},indent=2),flush=True)
    evaluations=[]
    for spec in plan['candidates']:
        started=time.monotonic()
        settings={k:v for k,v in spec.items() if k!='name'}
        if isinstance(settings['class_weight'],dict):
            settings['class_weight']={int(k):v for k,v in settings['class_weight'].items()}
        settings.update(max_features='sqrt',random_state=42,n_jobs=2)
        classifier=RandomForestClassifier(**settings)
        print('FIT',spec['name'],flush=True)
        classifier.fit(Xtrain,train.target.values)
        model=A3URLPipeline(classifier=classifier)
        model.check_model()
        prob=model.probability_from_features(Xval)
        evaluation={'name':spec['name'],'settings':spec,'api_formatted':performance(val,prob),'native_explicit':performance(val.loc[explicit],prob[explicit]),'stability':stability(meta,model.probability_from_features(Xpairs_new)),'fit_and_eval_s':round(time.monotonic()-started,2)}
        gate=plan['integration_gate']; score=evaluation['api_formatted']; stable=evaluation['stability']['valid_format_pool']['label_flip_rate'];old_stable=baseline['stability']['valid_format_pool']['label_flip_rate']
        evaluation['gates']={
            'fpr_at_most_20pct':score['fpr']<=gate['validation_false_positive_rate_max'],
            'dangerous_recall_at_least_90pct':score['recall']>=gate['validation_dangerous_recall_min'],
            'phishing_recall_at_least_80pct':score['subtypes']['phishing']['recall']>=gate['validation_phishing_recall_min'],
            'fpr_halved_vs_api_baseline':score['fpr']<=baseline['api_formatted']['fpr']*(1-gate['relative_false_positive_reduction_vs_api_formatted_a2_min']),
            'format_flips_reduced_by_75pct':stable<=old_stable*(1-gate['paired_format_label_flip_reduction_min'])+1e-12,
            'domain_overlap_zero':True,
        }
        evaluation['passes']=all(evaluation['gates'].values())
        joblib.dump(model,artifacts/(spec['name']+'.joblib'),compress=3)
        np.save(cache/(spec['name']+'-validation-prob.npy'),prob)
        write_json(results/(spec['name']+'.json'),evaluation)
        evaluations.append(evaluation)
        print('RESULT',json.dumps({'name':spec['name'],'score':score,'gates':evaluation['gates'],'elapsed':evaluation['fit_and_eval_s']},indent=2),flush=True)
    passing=[e for e in evaluations if e['passes']]
    chosen=min(passing,key=lambda e:(e['api_formatted']['fpr'],-e['api_formatted']['recall'],e['settings']['max_depth'])) if passing else None
    decision={'selected':chosen['name'] if chosen else None,'policy':POLICY_ID,'threshold':.5,'decision_basis':'Predeclared validation gates; demo scores not consulted. No test outcomes used.','candidates':[{'name':e['name'],'passes':e['passes'],'fpr':e['api_formatted']['fpr'],'recall':e['api_formatted']['recall'],'phishing_recall':e['api_formatted']['subtypes']['phishing']['recall']} for e in evaluations]}
    write_json(results/'decision.json',decision)
    print('DECISION',json.dumps(decision,indent=2),flush=True)
    if chosen:
        selected=joblib.load(artifacts/(chosen['name']+'.joblib'))
        # Only now inspect the user's diagnostic URLs; no labels/allowlist are attached.
        demos=['https://www.google.com/','www.google.com/','https://github.com/','github.com/','http://www.google.com/','https://www.google.com','HTTPS://WWW.GOOGLE.COM/','https://paypal.com@account-check.example/login']
        write_json(results/'post-selection-demos.json',[{'url':u,'a2_probability':old.predict_urls([u])[0]['dangerous_probability'],'a3_probability':selected.predict_urls([u])[0]['dangerous_probability'],'note':'Diagnostic only; familiarity is not a safety label.'} for u in demos])
        reloaded=selected.probability_from_features(Xval.iloc[:1000])
        assert np.allclose(reloaded,np.load(cache/(chosen['name']+'-validation-prob.npy'))[:1000],atol=1e-12,rtol=0)

if __name__=='__main__': main()
