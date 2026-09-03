from sqlalchemy import Boolean, Column, DateTime, Float, Integer, String, Text
from ..database import Base

class Customer(Base):
    __tablename__='customers'; id=Column(String, primary_key=True); age_days=Column(Integer, default=0); previous_count=Column(Integer, default=0); previous_fraud_count=Column(Integer, default=0)
class Merchant(Base):
    __tablename__='merchants'; id=Column(String, primary_key=True); name=Column(String); risk_score=Column(Float, default=0)
class Device(Base):
    __tablename__='devices'; id=Column(String, primary_key=True)
class IPAddress(Base):
    __tablename__='ip_addresses'; id=Column(String, primary_key=True)
class PaymentInstrument(Base):
    __tablename__='payment_instruments'; id=Column(String, primary_key=True)
class Transaction(Base):
    __tablename__='transactions'; id=Column(String, primary_key=True); customer_id=Column(String); merchant_id=Column(String); amount=Column(Float); timestamp=Column(DateTime); device_id=Column(String); ip_address=Column(String); payment_method=Column(String); location=Column(String); transaction_frequency=Column(Float); customer_age_days=Column(Integer); previous_transaction_count=Column(Integer); previous_fraud_count=Column(Integer); is_new_device=Column(Boolean); is_new_ip=Column(Boolean); is_fraud=Column(Boolean); ml_probability=Column(Float, default=0); ring_id=Column(String, nullable=True)
class FraudRing(Base):
    __tablename__='fraud_rings'; id=Column(String, primary_key=True); risk_score=Column(Float); severity=Column(String); evidence=Column(Text); created_at=Column(DateTime)
class FraudEvidence(Base):
    __tablename__='fraud_evidence'; id=Column(Integer, primary_key=True); ring_id=Column(String); transaction_id=Column(String); text=Column(Text); weight=Column(Float)
class Investigation(Base):
    __tablename__='investigations'; id=Column(String, primary_key=True); transaction_id=Column(String); summary=Column(Text); explanation=Column(Text); action=Column(String); confidence=Column(Float); provider=Column(String)
