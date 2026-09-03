import csv, sys
from datetime import datetime
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from backend.app.database import Base, SessionLocal, engine
from backend.app.models.entities import Customer, Merchant, Device, IPAddress, PaymentInstrument, Transaction

Base.metadata.create_all(bind=engine)
def seed():
    db=SessionLocal()
    try:
        rows=list(csv.DictReader(open('data/raw/transactions.csv')))
        customers=set(); merchants=set(); devices=set(); ips=set(); instruments=set()
        for r in rows:
            if r['customer_id'] not in customers: db.add(Customer(id=r['customer_id'],age_days=int(r['customer_age_days']),previous_count=int(r['previous_transaction_count']),previous_fraud_count=int(r['previous_fraud_count']))); customers.add(r['customer_id'])
            if r['merchant_id'] not in merchants: db.add(Merchant(id=r['merchant_id'],name=r['merchant_id'])); merchants.add(r['merchant_id'])
            if r['device_id'] not in devices: db.add(Device(id=r['device_id'])); devices.add(r['device_id'])
            if r['ip_address'] not in ips: db.add(IPAddress(id=r['ip_address'])); ips.add(r['ip_address'])
            if r['payment_method'] not in instruments: db.add(PaymentInstrument(id=r['payment_method'])); instruments.add(r['payment_method'])
            db.merge(Transaction(id=r['transaction_id'],customer_id=r['customer_id'],merchant_id=r['merchant_id'],amount=float(r['amount']),timestamp=datetime.fromisoformat(r['timestamp']),device_id=r['device_id'],ip_address=r['ip_address'],payment_method=r['payment_method'],location=r['location'],transaction_frequency=float(r['transaction_frequency']),customer_age_days=int(r['customer_age_days']),previous_transaction_count=int(r['previous_transaction_count']),previous_fraud_count=int(r['previous_fraud_count']),is_new_device=r['is_new_device']=='True',is_new_ip=r['is_new_ip']=='True',is_fraud=r['is_fraud']=='True',ring_id='FR-001' if r['device_id']=='DEV-77A' else None))
        db.commit(); print(f'Seeded {len(rows)} transactions')
    finally: db.close()
if __name__=='__main__': seed()
