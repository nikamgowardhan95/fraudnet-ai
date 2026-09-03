import json, csv
from pathlib import Path
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score, confusion_matrix
from joblib import dump
FEATURES=['amount','transaction_frequency','customer_age_days','previous_transaction_count','previous_fraud_count','is_new_device','is_new_ip']
def load():
 p=Path('data/raw/transactions.csv'); rows=list(csv.DictReader(p.open())); X=[[float(r[k]) if k not in ('is_new_device','is_new_ip') else int(r[k]=='True') for k in FEATURES] for r in rows]; y=[int(r['is_fraud']=='True') for r in rows]; return X,y
def train():
 X,y=load(); Xtr,Xtmp,ytr,ytmp=train_test_split(X,y,test_size=.3,random_state=42,stratify=y); Xv,Xte,yv,yte=train_test_split(Xtmp,ytmp,test_size=2/3,random_state=42,stratify=ytmp); model=RandomForestClassifier(n_estimators=120,random_state=42,class_weight='balanced'); model.fit(Xtr,ytr); pred=model.predict(Xte); proba=model.predict_proba(Xte)[:,1]; m={'model':'Random Forest','train_set_size':len(ytr),'validation_set_size':len(yv),'test_set_size':len(yte),'accuracy':accuracy_score(yte,pred),'precision':precision_score(yte,pred,zero_division=0),'recall':recall_score(yte,pred,zero_division=0),'f1':f1_score(yte,pred,zero_division=0),'roc_auc':roc_auc_score(yte,proba),'confusion_matrix':confusion_matrix(yte,pred).tolist(),'false_positives':int(((pred==1)&( __import__('numpy').array(yte)==0)).sum())}; Path('ml/artifacts').mkdir(exist_ok=True); dump(model,'ml/artifacts/fraud_model.joblib'); json.dump(m,open('ml/artifacts/metrics.json','w'),indent=2); return m
if __name__=='__main__': print(json.dumps(train(),indent=2))
