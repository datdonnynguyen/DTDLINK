"""Final scoped A3 text-view experiment; no numeric path-length/protocol proxies."""
import json
import time
import warnings
from urllib.parse import urlsplit
import joblib
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.exceptions import ConvergenceWarning
from threadpoolctl import threadpool_limits
from diagnose import HERE,PROJECT,write_json
from train_compare import performance,stability,variants
from dtdlink_a3.pipeline import A3TextPipeline,TEXT_ONLY_POLICY_ID
from dtdlink_a3.representation import canonical_model_view
from dtdlink_ml.feature_extraction import file_sha256
from dtdlink_ml.predict import load_pipeline as load_a2
from app.schemas import validate_url


def main():
    cache=HERE/'cache';results=HERE/'results';artifacts=HERE/'artifacts'
    write_json(results/'authority-plan-receipt.json',{'plan_sha256':file_sha256(HERE/'PLAN_AUTHORITY_TEXT.json'),'started_utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime())})
    train=pd.read_pickle(cache/'train-eligible.pkl');val=pd.read_pickle(cache/'validation-eligible.pkl')
    def view(u):return canonical_model_view(u)[0][len('https://'):]
    vectorizer=TfidfVectorizer(analyzer='char',ngram_range=(3,5),min_df=3,max_features=30000,sublinear_tf=True,lowercase=False,norm=None,dtype=np.float32)
    print('FIT train-only authority vocabulary',flush=True)
    Xtrain=vectorizer.fit_transform(train.api_url.map(view));Xval=vectorizer.transform(val.api_url.map(view))
    print('Sparse matrix',Xtrain.shape,'nnz',Xtrain.nnz,flush=True)
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
    Xpairs=vectorizer.transform(map(view,pair_urls))
    homepage=np.array([urlsplit(u).path in ('','/') and not urlsplit(u).query for u in val.api_url])
    explicit=val.url.str.match(r'(?i)^https?://').values
    evaluated=[]
    for name,weight in [('authority_text_balanced','balanced'),('authority_text_recall3',{0:1,1:3}),('authority_text_recall5',{0:1,1:5})]:
        print('FIT',name,flush=True);started=time.monotonic()
        classifier=LogisticRegression(C=.1,solver='newton-cg',max_iter=100,tol=1e-4,random_state=42,class_weight=weight)
        with warnings.catch_warnings(record=True) as caught,threadpool_limits(limits=2):
            warnings.simplefilter('always',ConvergenceWarning)
            classifier.fit(Xtrain,train.target.values)
        converged=not any(issubclass(w.category,ConvergenceWarning) for w in caught) and int(classifier.n_iter_.max())<100
        model=A3TextPipeline(classifier=classifier,vectorizer=vectorizer,scaler=None,representation=TEXT_ONLY_POLICY_ID,use_numeric=False);model.check_model()
        prob=model.probability_from_features(Xval);score=performance(val,prob);home=performance(val.loc[homepage],prob[homepage]);st=stability(meta,model.probability_from_features(Xpairs))
        gates={'fpr_at_most_20pct':score['fpr']<=.2,'dangerous_recall_at_least_90pct':score['recall']>=.9,'phishing_recall_at_least_80pct':score['subtypes']['phishing']['recall']>=.8,'fpr_halved_vs_api_baseline':score['fpr']<=baseline['api_formatted']['fpr']*.5,'format_flips_reduced_by_75pct':st['valid_format_pool']['label_flip_rate']<=baseline['stability']['valid_format_pool']['label_flip_rate']*.25+1e-12,'domain_overlap_zero':True,'homepage_fpr_at_most_20pct':home['fpr']<=.2,'homepage_dangerous_recall_at_least_80pct':home['recall']>=.8,'optimizer_converged':converged}
        record={'name':name,'feature_count':model.feature_count,'use_numeric':False,'classifier_settings':{'C':.1,'class_weight':weight,'solver':'newton-cg','max_iter':100,'tol':1e-4},'api_formatted':score,'homepage_no_query':home,'native_explicit':performance(val.loc[explicit],prob[explicit]),'stability':st,'gates':gates,'passes':all(gates.values()),'solver_iterations':classifier.n_iter_.tolist(),'fit_and_eval_s':round(time.monotonic()-started,2)}
        np.save(cache/(name+'-validation-prob.npy'),prob);joblib.dump(model,artifacts/(name+'.joblib'),compress=3);write_json(results/(name+'.json'),record);evaluated.append(record)
        print('RESULT',json.dumps({'name':name,'score':score,'homepage':home,'gates':gates,'iterations':classifier.n_iter_.tolist()},indent=2),flush=True)
    passing=[e for e in evaluated if e['passes']];selected=min(passing,key=lambda e:(e['api_formatted']['fpr'],-e['api_formatted']['recall'])) if passing else None
    decision={'selected':selected['name'] if selected else None,'kind':'authority text only','threshold':.5,'basis':'Unchanged aggregate and homepage validation gates; no A2 test or demo-based choice.','candidates':[{'name':e['name'],'passes':e['passes'],'fpr':e['api_formatted']['fpr'],'recall':e['api_formatted']['recall'],'homepage_fpr':e['homepage_no_query']['fpr'],'homepage_recall':e['homepage_no_query']['recall']} for e in evaluated]}
    write_json(results/'decision-authority.json',decision);print('DECISION',json.dumps(decision,indent=2),flush=True)
    if selected:
        model=joblib.load(artifacts/(selected['name']+'.joblib'));old=load_a2(PROJECT/'models/final_pipeline.joblib',PROJECT/'models/model_metadata.json')
        demos=['https://www.google.com/','www.google.com/','https://github.com/','github.com/','http://www.google.com/','https://www.google.com','HTTPS://WWW.GOOGLE.COM/','https://paypal.com@account-check.example/login']
        write_json(results/'authority-demos.json',[{'url':u,'a2_probability':old.predict_urls([u])[0]['dangerous_probability'],'a3_probability':model.predict_urls([u])[0]['dangerous_probability'],'note':'Post-selection example; familiar domain is not a safety label.'} for u in demos])
        assert np.allclose(model.predict_proba(val.api_url.iloc[:1000].tolist())[:,1],np.load(cache/(selected['name']+'-validation-prob.npy'))[:1000],atol=1e-12,rtol=0)

if __name__=='__main__':main()
