import csv, random
from datetime import datetime, timedelta
from pathlib import Path

def generate(n=1200, seed=42):
    random.seed(seed); out=Path('data/raw/transactions.csv'); out.parent.mkdir(parents=True, exist_ok=True)
    rows=[]; start=datetime(2026,8,21)
    for i in range(n):
        ring=i<120; fraud=ring or random.random()<.08
        customer=f'CUST-{1042+i%180:04d}'; device='DEV-77A' if ring and i%3 else f'DEV-{random.randint(1,80):03d}'
        ip='IP-103.24' if ring and i%4 else f'IP-{random.randint(1,30):03d}'
        amount=18000+random.randint(-700,700) if ring else (random.randint(500,5000) if not fraud else random.randint(7000,16000))
        rows.append({'transaction_id':f'txn_{i:06d}','customer_id':customer,'merchant_id':f'M-{random.randint(1,20):03d}','amount':amount,'timestamp':(start+timedelta(minutes=i*11)).isoformat(),'device_id':device,'ip_address':ip,'payment_method':f'PI-{random.randint(1,90):03d}','location':random.choice(['Mumbai','Delhi','Bengaluru']),'transaction_frequency':random.randint(1,14) if fraud else random.randint(1,4),'customer_age_days':random.randint(30,900),'previous_transaction_count':random.randint(1,80),'previous_fraud_count':random.randint(1,4) if fraud else 0,'is_new_device':device.startswith('DEV-0'),'is_new_ip':ip.startswith('IP-0'),'is_fraud':fraud})
    with out.open('w', newline='') as f: w=csv.DictWriter(f, fieldnames=rows[0].keys()); w.writeheader(); w.writerows(rows)
    return out
if __name__=='__main__': print(generate())
