from fastapi.testclient import TestClient
from backend.app.main import app
client=TestClient(app)
def test_health(): assert client.get('/health').status_code==200
def test_score_validation(): assert client.post('/api/transactions/score',json={'amount':0,'customer_id':'x'}).status_code==422
def test_ring_graph():
 r=client.get('/api/fraud-rings/FR-001/graph'); assert r.status_code==200 and len(r.json()['nodes'])>=5
def test_investigation(): assert client.post('/api/investigations/txn_8F29A1/run').json()['provider']=='local-deterministic'
def test_simulation(): assert client.post('/api/simulation/block-device?device_id=DEV-77A').json()['is_estimate'] is True
