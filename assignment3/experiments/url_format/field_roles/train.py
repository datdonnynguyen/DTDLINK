"""Fit URL-role features on train only; select on validation without test use."""
import json,sys,time,warnings
from pathlib import Path
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent))
from diagnose import PROJECT,BACKEND,write_json
from train_compare import performance,stability,variants
from dtdlink_ml.feature_extraction import file_sha256
from dtdlink_a3.fields import FieldAwarePipeline,field_record,encode_records,FIELD_NAMES,FLAG_NAMES
from app.schemas import validate_url
import joblib
import numpy as np
import pandas as pd
from scipy import sparse
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.exceptions import ConvergenceWarning
from threadpoolctl import threadpool_limits


def main():
    parent=HERE.parent;cache=HERE/'cache';results=HERE/'results';artifacts=HERE/'artifacts'
    for directory in (cache, results, artifacts):
        directory.mkdir(parents=True, exist_ok=True)
    plan=json.loads((HERE/'PLAN.json').read_text())
    write_json(results/'plan-receipt.json',{'sha256':file_sha256(HERE/'PLAN.json'),'started_utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime())})
    assert file_sha256(PROJECT/'data/processed/url_features.csv')=='fe049dd9f6b2c92570354b28b2885312f64c73b03b7053be06bc35cce5a591ff'
    assert file_sha256(PROJECT/'data/processed/split_manifest.csv')=='fbcbcf2ff68e26acfa2bb435b53c262645688a54a195ff64e283e7ff753ffc2f'
    audit=json.loads((parent/'results/eligibility-and-domain-audit.json').read_text());assert not any(audit['wire_domain_overlaps'].values())
    train=pd.read_pickle(parent/'cache/train-eligible.pkl');val=pd.read_pickle(parent/'cache/validation-eligible.pkl')
    assert len(train)==381494 and len(val)==128373
    assert set(train.group_key).isdisjoint(set(val.group_key))
    print('Extract train and validation URL roles',flush=True)
    train_records=[field_record(u) for u in train.api_url];val_records=[field_record(u) for u in val.api_url]
    joblib.dump((train_records,val_records),cache/'records.joblib',compress=3)
    vectorizers={};vocab_audit={}
    for name in FIELD_NAMES:
        cfg=plan['vectorizers'][name];values=[r[0][name] for r in train_records]
        print('FIT train vocabulary',name,flush=True)
        v=TfidfVectorizer(analyzer='char',ngram_range=tuple(cfg['ngrams']),max_features=cfg['max_features'],min_df=3,sublinear_tf=True,lowercase=False,norm='l2',dtype=np.float32)
        try:v.fit(values)
        except ValueError as exc:
            if 'empty vocabulary' not in str(exc) and 'After pruning' not in str(exc):raise
            v=None
        vectorizers[name]=v
        vocab_audit[name]={'nonempty_train_rows':sum(bool(s) for s in values),'features':len(v.vocabulary_) if v is not None else 0,'fit_scope':'train only'}
    write_json(results/'vocabulary-audit.json',vocab_audit);joblib.dump(vectorizers,cache/'vectorizers.joblib',compress=3)
    Xtrain=encode_records(train_records,vectorizers);Xval=encode_records(val_records,vectorizers)
    print('Sparse matrices',Xtrain.shape,'train nnz',Xtrain.nnz,flush=True)
    baseline=json.loads((parent/'results/baseline-cohorts.json').read_text())
    meta=pd.read_pickle(parent/'cache/pairs.pkl')
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
    pair_records=[field_record(u) for u in pair_urls];Xpairs=encode_records(pair_records,vectorizers)
    homepage=np.array([r[2] and not r[0]['query'] for r in val_records]);explicit=val.url.str.match(r'(?i)^https?://').values
    evaluations=[]
    for spec in plan['candidates']:
        name=spec['name'];weight=spec['class_weight']
        if isinstance(weight,dict):weight={int(k):v for k,v in weight.items()}
        print('FIT',name,flush=True);started=time.monotonic()
        if spec['root_context']:
            A=encode_records(train_records,vectorizers,True);B=encode_records(val_records,vectorizers,True);P=encode_records(pair_records,vectorizers,True)
        else:A,B,P=Xtrain,Xval,Xpairs
        classifier=LogisticRegression(C=1,solver='newton-cg',max_iter=100,tol=1e-4,random_state=42,class_weight=weight)
        with warnings.catch_warnings(record=True) as caught,threadpool_limits(limits=2):
            warnings.simplefilter('always',ConvergenceWarning);classifier.fit(A,train.target.values)
        converged=not any(issubclass(w.category,ConvergenceWarning) for w in caught) and int(classifier.n_iter_.max())<100
        model=FieldAwarePipeline(classifier=classifier,vectorizers=vectorizers,root_context=spec['root_context']);model.check_model()
        p=model.probability_from_features(B);score=performance(val,p);home=performance(val.loc[homepage],p[homepage]);st=stability(meta,model.probability_from_features(P))
        g=plan['acceptance'];gates={'whole_fpr':score['fpr']<=g['whole_fpr_max'],'dangerous_recall':score['recall']>=g['dangerous_recall_min'],'phishing_recall':score['subtypes']['phishing']['recall']>=g['phishing_recall_min'],'homepage_fpr':home['fpr']<=g['homepage_fpr_max'],'homepage_recall':home['recall']>=g['homepage_dangerous_recall_min'],'format_stability':st['valid_format_pool']['label_flip_rate']<=baseline['stability']['valid_format_pool']['label_flip_rate']*.25+1e-12,'domain_disjoint':True,'converged':converged}
        r={'name':name,'candidate':spec,'representation':model.representation,'feature_count':model.feature_count,'api_formatted':score,'native_explicit':performance(val.loc[explicit],p[explicit]),'homepage_no_query':home,'stability':st,'gates':gates,'passes':all(gates.values()),'solver_iterations':classifier.n_iter_.tolist(),'elapsed_s':round(time.monotonic()-started,2)}
        np.save(cache/(name+'-validation-prob.npy'),p);joblib.dump(model,artifacts/(name+'.joblib'),compress=3);write_json(results/(name+'.json'),r);evaluations.append(r)
        print('RESULT',json.dumps({'name':name,'fpr':score['fpr'],'recall':score['recall'],'phishing_recall':score['subtypes']['phishing']['recall'],'home_fpr':home['fpr'],'home_recall':home['recall'],'gates':gates,'seconds':r['elapsed_s']},indent=2),flush=True)
    passing=[r for r in evaluations if r['passes']]
    selected=min(passing,key=lambda r:(r['api_formatted']['fpr'],-r['api_formatted']['recall'])) if passing else None
    decision={'selected':selected['name'] if selected else None,'basis':'Fixed gates on full validation and homepages, no demo output or A2 test use.','threshold':.5,'candidates':[{'name':r['name'],'passes':r['passes'],'fpr':r['api_formatted']['fpr'],'recall':r['api_formatted']['recall'],'home_fpr':r['homepage_no_query']['fpr'],'home_recall':r['homepage_no_query']['recall']} for r in evaluations]}
    write_json(results/'decision.json',decision);print('DECISION',json.dumps(decision,indent=2),flush=True)
    if selected:
        model=joblib.load(artifacts/(selected['name']+'.joblib'))
        assert np.allclose(model.predict_proba(val.api_url.iloc[:1000].tolist())[:,1],np.load(cache/(selected['name']+'-validation-prob.npy'))[:1000],atol=1e-12,rtol=0)
    # Post-selection diagnostics are retained even on failure, never used to choose.
    demos=['https://www.google.com/','https://github.com/','https://www.python.org/doc/','https://en.wikipedia.org/wiki/Machine_learning','https://example.com/about.html','https://google.com@account-check.example/login','https://google.com.account-check.example/login']
    diagnostic={}
    for r in evaluations:
        m=joblib.load(artifacts/(r['name']+'.joblib'))
        diagnostic[r['name']]=[{'url':u,'probability':m.predict_urls([u])[0]['dangerous_probability']} for u in demos]
    write_json(results/'post-selection-diagnostics.json',diagnostic)

if __name__=='__main__':main()
