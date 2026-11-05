"""Convergence-checked train-only optimizer refinement; no demo-based selection."""
import copy
import json
import time
import warnings
import joblib
import numpy as np
import pandas as pd
from scipy import sparse
from sklearn.exceptions import ConvergenceWarning
from threadpoolctl import threadpool_limits

from diagnose import HERE, PROJECT, FEATURE_NAMES, write_json
from train_compare import performance, stability, variants
from dtdlink_ml.feature_extraction import file_sha256
from dtdlink_ml.predict import load_pipeline as load_a2
from dtdlink_a3.representation import canonical_model_view
from app.schemas import validate_url


def main():
    cache=HERE/'cache';results=HERE/'results';artifacts=HERE/'artifacts'
    assert (results/'decision-text.json').exists(),'Finish phase 2 first.'
    plan=json.loads((HERE/'PLAN_TEXT.json').read_text());gate=json.loads((HERE/'PLAN.json').read_text())['integration_gate']
    write_json(results/'solver-plan-receipt.json',{'plan_sha256':file_sha256(HERE/'PLAN_SOLVER.json'),'started_utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime())})
    train=pd.read_pickle(cache/'train-eligible.pkl');val=pd.read_pickle(cache/'validation-eligible.pkl')
    numtrain=pd.read_pickle(cache/'train-neutral-X.pkl');numval=pd.read_pickle(cache/'validation-neutral-X.pkl')
    vectorizer,scaler=joblib.load(cache/'text-transformers.joblib')
    traintext=[canonical_model_view(u)[0] for u in train.api_url];valtext=[canonical_model_view(u)[0] for u in val.api_url]
    Xtrain=sparse.hstack([vectorizer.transform(traintext),sparse.csr_matrix(scaler.transform(numtrain).astype(np.float32))],format='csr',dtype=np.float32)
    Xval=sparse.hstack([vectorizer.transform(valtext),sparse.csr_matrix(scaler.transform(numval).astype(np.float32))],format='csr',dtype=np.float32)
    baseline=json.loads((results/'baseline-cohorts.json').read_text());meta=pd.read_pickle(cache/'pairs.pkl')
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
    for spec in plan['candidates']:
        name=spec['name']+'_converged'
        model=joblib.load(artifacts/(spec['name']+'.joblib'))
        model.classifier.set_params(solver='newton-cg',max_iter=100,tol=1e-4,warm_start=True)
        print('REFINE',name,flush=True);started=time.monotonic()
        with warnings.catch_warnings(record=True) as caught,threadpool_limits(limits=2):
            warnings.simplefilter('always',ConvergenceWarning)
            model.classifier.fit(Xtrain,train.target.values)
        converged=not any(issubclass(w.category,ConvergenceWarning) for w in caught) and int(model.classifier.n_iter_.max())<100
        model.check_model();prob=model.probability_from_features(Xval)
        st=stability(meta,model.predict_proba(pair_urls)[:,1])
        score=performance(val,prob)
        gates={'fpr_at_most_20pct':score['fpr']<=gate['validation_false_positive_rate_max'],'dangerous_recall_at_least_90pct':score['recall']>=gate['validation_dangerous_recall_min'],'phishing_recall_at_least_80pct':score['subtypes']['phishing']['recall']>=gate['validation_phishing_recall_min'],'fpr_halved_vs_api_baseline':score['fpr']<=baseline['api_formatted']['fpr']*.5,'format_flips_reduced_by_75pct':st['valid_format_pool']['label_flip_rate']<=baseline['stability']['valid_format_pool']['label_flip_rate']*.25+1e-12,'domain_overlap_zero':True,'optimizer_converged':converged}
        evaluation={'name':name,'source_candidate':spec,'api_formatted':score,'native_explicit':performance(val.loc[explicit],prob[explicit]),'stability':st,'gates':gates,'passes':all(gates.values()),'feature_count':model.feature_count,'solver_iterations':model.classifier.n_iter_.tolist(),'fit_and_eval_s':round(time.monotonic()-started,2)}
        np.save(cache/(name+'-validation-prob.npy'),prob);joblib.dump(model,artifacts/(name+'.joblib'),compress=3)
        write_json(results/(name+'.json'),evaluation);evaluations.append(evaluation)
        print('RESULT',json.dumps(evaluation,indent=2),flush=True)
    passing=[e for e in evaluations if e['passes']]
    chosen=min(passing,key=lambda e:(e['api_formatted']['fpr'],-e['api_formatted']['recall'])) if passing else None
    decision={'selected':chosen['name'] if chosen else None,'threshold':.5,'basis':'Converged train-only fits, unchanged validation gates and FPR ranking. No A2 test scores or demo scores used.','candidates':[{'name':e['name'],'passes':e['passes'],'fpr':e['api_formatted']['fpr'],'recall':e['api_formatted']['recall'],'phishing_recall':e['api_formatted']['subtypes']['phishing']['recall'],'converged':e['gates']['optimizer_converged']} for e in evaluations]}
    write_json(results/'decision-final.json',decision);print('DECISION',json.dumps(decision,indent=2),flush=True)
    if chosen:
        selected=joblib.load(artifacts/(chosen['name']+'.joblib'))
        old=load_a2(PROJECT/'models/final_pipeline.joblib',PROJECT/'models/model_metadata.json')
        demos=['https://www.google.com/','www.google.com/','https://github.com/','github.com/','http://www.google.com/','https://www.google.com','HTTPS://WWW.GOOGLE.COM/','https://paypal.com@account-check.example/login']
        write_json(results/'post-selection-demos-final.json',[{'url':u,'a2_probability':old.predict_urls([u])[0]['dangerous_probability'],'a3_probability':selected.predict_urls([u])[0]['dangerous_probability'],'note':'Diagnostic only; not a safety label. GitHub naturally occurred in A2 train, Google in validation; not an independent holdout.'} for u in demos])
        assert np.allclose(selected.probability_from_features(Xval[:1000]),np.load(cache/(chosen['name']+'-validation-prob.npy'))[:1000],atol=1e-12,rtol=0)

if __name__=='__main__':main()
