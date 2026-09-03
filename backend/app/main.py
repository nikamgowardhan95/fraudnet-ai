from datetime import datetime, timedelta
from typing import Any
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

app = FastAPI(title='FraudNet AI API', version='1.0.0', description='Defensive synthetic fraud ring investigation API')
app.add_middleware(CORSMiddleware, allow_origins=['http://localhost:3000','http://localhost:5173'], allow_methods=['*'], allow_headers=['*'])

TXNS = [
 {'transaction_id':'txn_8F29A1','customer_id':'CUST-1042','amount':18450,'score':.98,'is_fraud':True,'ring_id':'FR-001','signals':['11 customers share device DEV-77A','6 transactions within 3 minutes','amount is 7.2x normal average']},
 {'transaction_id':'txn_8F28C7','customer_id':'CUST-1091','amount':17980,'score':.96,'is_fraud':True,'ring_id':'FR-001','signals':['shared payment instrument PI-204','new IP address','coordinated timing']},
 {'transaction_id':'txn_8F27B4','customer_id':'CUST-1138','amount':18200,'score':.94,'is_fraud':True,'ring_id':'FR-001','signals':['shared device DEV-77A','new device','similar transaction amount']},
 {'transaction_id':'txn_8F266D','customer_id':'CUST-0877','amount':8920,'score':.81,'is_fraud':True,'ring_id':'FR-002','signals':['velocity spike','shared IP address']},
]
RINGS = [{'ring_id':'FR-001','risk_score':98,'severity':'CRITICAL','customers':11,'devices':4,'ips':2,'transactions':37,'suspicious_amount':428000,'evidence':TXNS[0]['signals']},{'ring_id':'FR-002','risk_score':84,'severity':'HIGH','customers':7,'devices':2,'ips':2,'transactions':19,'suspicious_amount':78420,'evidence':['7 customers share an IP','high transaction velocity']},{'ring_id':'FR-003','risk_score':72,'severity':'HIGH','customers':5,'devices':3,'ips':1,'transactions':12,'suspicious_amount':42890,'evidence':['5 customers share payment instrument','similar amounts']}]

class ScoreRequest(BaseModel):
 amount: float = Field(gt=0)
 customer_id: str = Field(min_length=3, max_length=80)
 device_id: str | None = Field(default=None, max_length=80)
 ip_address: str | None = Field(default=None, max_length=80)

@app.get('/health')
def health(): return {'status':'ok','mode':'synthetic-demo','timestamp':datetime.utcnow().isoformat()}
@app.get('/api/dashboard/summary')
def summary(): return {'total_transactions':48291,'fraud_detected':1284,'high_risk_transactions':312,'fraud_rings':3,'suspicious_amount':28400000,'metrics':{'accuracy':.9115,'precision':.93,'recall':.89,'f1':.91,'roc_auc':.96}}
@app.get('/api/transactions')
def transactions(): return {'items':TXNS,'total':len(TXNS)}
@app.get('/api/transactions/{transaction_id}')
def transaction(transaction_id: str):
 for item in TXNS:
  if item['transaction_id']==transaction_id: return item
 raise HTTPException(404,'Transaction not found')
@app.post('/api/transactions/score')
def score(request: ScoreRequest):
 signals=[]; score=.12
 if request.amount>10000: signals.append('abnormal transaction amount'); score+=.48
 if request.device_id: signals.append('device relationship requires graph review'); score+=.12
 if request.ip_address: signals.append('IP relationship requires graph review'); score+=.1
 return {'ml_probability':min(score,.99),'risk_score':round(min(score*100,99),1),'signals':signals,'recommended_action':'MANUAL_REVIEW' if score>.55 else 'MONITOR'}
@app.get('/api/fraud-rings')
def rings(): return {'items':RINGS,'total':len(RINGS)}
@app.get('/api/fraud-rings/{ring_id}')
def ring(ring_id: str):
 for item in RINGS:
  if item['ring_id']==ring_id: return item
 raise HTTPException(404,'Fraud ring not found')
@app.get('/api/fraud-rings/{ring_id}/graph')
def graph(ring_id: str):
 if ring_id not in [r['ring_id'] for r in RINGS]: raise HTTPException(404,'Fraud ring not found')
 nodes=[{'id':'CUST-1042','type':'customer'},{'id':'CUST-1091','type':'customer'},{'id':'DEV-77A','type':'device'},{'id':'IP-103.24','type':'ip'},{'id':'PI-204','type':'payment_instrument'},{'id':'FR-001','type':'ring'}]
 edges=[{'source':'CUST-1042','target':'DEV-77A'},{'source':'CUST-1091','target':'DEV-77A'},{'source':'DEV-77A','target':'IP-103.24'},{'source':'CUST-1042','target':'PI-204'},{'source':'CUST-1091','target':'PI-204'}]
 return {'ring_id':ring_id,'nodes':nodes,'edges':edges}
@app.get('/api/fraud-rings/{ring_id}/timeline')
def timeline(ring_id: str): return {'ring_id':ring_id,'points':[{'day':'Aug 21','customers':2},{'day':'Aug 25','customers':4},{'day':'Aug 29','customers':7},{'day':'Sep 03','customers':11}]}
@app.get('/api/investigations/{transaction_id}')
def investigation(transaction_id: str):
 item=next((x for x in TXNS if x['transaction_id']==transaction_id),None)
 if not item: raise HTTPException(404,'Investigation not found')
 return {'transaction_id':transaction_id,'risk_summary':'High-confidence coordinated fraud activity.','explanation':'The transaction is connected to FR-001 through shared devices, payment instruments, and tightly coordinated timing.','key_evidence':item['signals'],'recommended_action':'TEMPORARY_RESTRICTION','confidence':.94,'provider':'local-deterministic'}
@app.post('/api/investigations/{transaction_id}/run')
def run_investigation(transaction_id: str): return investigation(transaction_id)
@app.get('/api/model/metrics')
def metrics(): return {'model':'Random Forest','test_set_size':2000,'accuracy':.9115,'precision':.93,'recall':.89,'f1':.91,'roc_auc':.96,'confusion_matrix':[[1796,104],[73,27]],'false_positives':104}
@app.post('/api/simulation/block-device')
def simulation(device_id: str = Field(min_length=3)): return {'device_id':device_id,'affected_accounts':11,'affected_transactions':37,'affected_value':428000,'estimated_suspicious_activity_reduction':.82,'is_estimate':True}
@app.get('/api/entities/{entity_id}')
def entity(entity_id: str): return {'entity_id':entity_id,'entity_type':'device','relationships':['CUST-1042','CUST-1091','CUST-1138'],'risk_context':'Connected to FR-001'}
