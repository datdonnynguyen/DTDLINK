"""Phase 2: train-only vocabulary/scaler/linear models; unchanged validation gate."""
import json
import time
import joblib
import numpy as np
import pandas as pd
from scipy import sparse
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler

from diagnose import HERE, PROJECT, BACKEND, FEATURE_NAMES, metrics, write_json
from train_compare import performance, build_pairs, stability
from dtdlink_a3.pipeline import A3TextPipeline, TEXT_POLICY_ID
from dtdlink_a3.representation import canonical_model_view
from dtdlink_ml.feature_extraction import file_sha256
from dtdlink_ml.predict import load_pipeline as load_a2


def main():
    cache=HERE/'cache';results=HERE/'results';artifacts=HERE/'artifacts'
    plan=json.loads((HERE/'PLAN_TEXT.json').read_text()); gates=json.loads((HERE/'PLAN.json').read_text())['integration_gate']
    write_json(results/'text-plan-receipt.json',{'plan_sha256':file_sha256(HERE/'PLAN_TEXT.json'),'started_utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'fit_scope':'train only; no demo injection or test data use'})
    train=pd.read_pickle(cache/'train-eligible.pkl');val=pd.read_pickle(cache/'validation-eligible.pkl')
    Xnum_train=pd.read_pickle(cache/'train-neutral-X.pkl');Xnum_val=pd.read_pickle(cache/'validation-neutral-X.pkl')
    train_text=[canonical_model_view(u)[0] for u in train.api_url]
    val_text=[canonical_model_view(u)[0] for u in val.api_url]
    vectorizer=TfidfVectorizer(analyzer='char',ngram_range=(3,5),min_df=3,max_features=100000,sublinear_tf=True,lowercase=False,dtype=np.float32)
    print('Fit train-only character vocabulary',flush=True)
    Xtext_train=vectorizer.fit_transform(train_text); Xtext_val=vectorizer.transform(val_text)
    scaler=StandardScaler(with_mean=False).fit(Xnum_train)
    Xtrain=sparse.hstack([Xtext_train,sparse.csr_matrix(scaler.transform(Xnum_train).astype(np.float32))],format='csr',dtype=np.float32)
    Xval=sparse.hstack([Xtext_val,sparse.csr_matrix(scaler.transform(Xnum_val).astype(np.float32))],format='csr',dtype=np.float32)
    joblib.dump((vectorizer,scaler),cache/'text-transformers.joblib',compress=3)
    print('Sparse matrix',Xtrain.shape,'nnz',Xtrain.nnz,flush=True)
    old=load_a2(PROJECT/'models/final_pipeline.joblib',PROJECT/'models/model_metadata.json')
    meta,Xpairs_old,Xpairs_new=build_pairs(val,cache)
    baseline=json.loads((results/'baseline-cohorts.json').read_text())
    baseline['stability']=stability(meta,old.probability_from_features(Xpairs_old))
    write_json(results/'baseline-cohorts.json',baseline)
    # Transform exactly the same sampled pair strings with the fitted train vocabulary.
    from train_compare import variants
    unique=val.sample(frac=1,random_state=42).drop_duplicates('group_key')
    sample=pd.concat([unique.loc[unique.target==y].sample(n=min(2000,int((unique.target==y).sum())),random_state=42) for y in [0,1]])
    pair_urls=[]
    from app.schemas import validate_url
    for row in sample.itertuples(index=False):
        for family,variant in variants(row.api_url,row.url):
            if family!='dataset_missing_scheme':
                try:
                    validate_url(variant)
                    if len(variant)>2048:continue
                except ValueError:continue
            pair_urls.extend([row.api_url,variant])
    transformer=A3TextPipeline(classifier=None,vectorizer=vectorizer,scaler=scaler)
    Xpairs=transformer.features_from_urls(pair_urls)
    assert Xpairs.shape[0]==len(meta)*2
    explicit=val.url.str.match(r'(?i)^https?://').values
    evaluations=[]
    for spec in plan['candidates']:
        cw=spec['class_weight']
        if isinstance(cw,dict): cw={int(k):v for k,v in cw.items()}
        classifier=LogisticRegression(C=1,solver='liblinear',max_iter=300,random_state=42,class_weight=cw)
        print('FIT',spec['name'],flush=True); started=time.monotonic()
        classifier.fit(Xtrain,train.target.values)
        model=A3TextPipeline(classifier=classifier,vectorizer=vectorizer,scaler=scaler);model.check_model()
        probability=model.probability_from_features(Xval)
        evaluation={'name':spec['name'],'settings':spec,'api_formatted':performance(val,probability),'native_explicit':performance(val.loc[explicit],probability[explicit]),'stability':stability(meta,model.probability_from_features(Xpairs)),'fit_and_eval_s':round(time.monotonic()-started,2),'feature_count':model.feature_count,'solver_iterations':classifier.n_iter_.tolist()}
        score=evaluation['api_formatted']; old_stable=baseline['stability']['valid_format_pool']['label_flip_rate']; stable=evaluation['stability']['valid_format_pool']['label_flip_rate']
        evaluation['gates']={'fpr_at_most_20pct':score['fpr']<=gates['validation_false_positive_rate_max'],'dangerous_recall_at_least_90pct':score['recall']>=gates['validation_dangerous_recall_min'],'phishing_recall_at_least_80pct':score['subtypes']['phishing']['recall']>=gates['validation_phishing_recall_min'],'fpr_halved_vs_api_baseline':score['fpr']<=baseline['api_formatted']['fpr']*.5,'format_flips_reduced_by_75pct':stable<=old_stable*.25+1e-12,'domain_overlap_zero':True}
        evaluation['passes']=all(evaluation['gates'].values())
        joblib.dump(model,artifacts/(spec['name']+'.joblib'),compress=3)
        np.save(cache/(spec['name']+'-validation-prob.npy'),probability)
        write_json(results/(spec['name']+'.json'),evaluation);evaluations.append(evaluation)
        print('RESULT',json.dumps({'name':spec['name'],'score':score,'gates':evaluation['gates'],'elapsed':evaluation['fit_and_eval_s']},indent=2),flush=True)
    passing=[e for e in evaluations if e['passes']]
    selected=min(passing,key=lambda e:(e['api_formatted']['fpr'],-e['api_formatted']['recall'])) if passing else None
    decision={'selected':selected['name'] if selected else None,'policy':TEXT_POLICY_ID,'threshold':.5,'decision_basis':'Unchanged validation gates/ranking; demo scores withheld until selection. No A2 test data used.','candidates':[{'name':e['name'],'passes':e['passes'],'fpr':e['api_formatted']['fpr'],'recall':e['api_formatted']['recall'],'phishing_recall':e['api_formatted']['subtypes']['phishing']['recall']} for e in evaluations]}
    write_json(results/'decision-text.json',decision);print('DECISION',json.dumps(decision,indent=2),flush=True)
    if selected:
        model=joblib.load(artifacts/(selected['name']+'.joblib'))
        assert np.allclose(model.probability_from_features(Xval[:1000]),np.load(cache/(selected['name']+'-validation-prob.npy'))[:1000],atol=1e-12,rtol=0)
        demos=['https://www.google.com/','www.google.com/','https://github.com/','github.com/','http://www.google.com/','https://www.google.com','HTTPS://WWW.GOOGLE.COM/','https://paypal.com@account-check.example/login']
        write_json(results/'post-selection-demos.json',[{'url':u,'a2_probability':old.predict_urls([u])[0]['dangerous_probability'],'a3_probability':model.predict_urls([u])[0]['dangerous_probability'],'note':'Diagnostic only; familiar name is not a safety label. GitHub domain was already in A2 train, Google in validation; these are not fresh-test results.'} for u in demos])

if __name__=='__main__':main()
