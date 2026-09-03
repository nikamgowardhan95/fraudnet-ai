from datetime import datetime
from pathlib import Path
import json
import os

from fastapi import FastAPI, HTTPException, Query  # pyright: ignore[reportMissingImports]
from fastapi.middleware.cors import CORSMiddleware  # pyright: ignore[reportMissingImports]
from pydantic import BaseModel, Field  # pyright: ignore[reportMissingImports]
from sqlalchemy import text  # pyright: ignore[reportMissingImports]

from .database import Base, engine, DATABASE_URL
from .models.entities import *
from .razorpay import RazorpayTestAdapter
from .model_service import predict_fraud


Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="FraudNet AI API",
    version="1.0.0",
    description="Defensive synthetic fraud ring investigation API"
)

configured_origins = [
    origin.strip()
    for origin in os.getenv("CORS_ORIGINS", "").split(",")
    if origin.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=configured_origins or ["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)


TXNS = [
    {
        "transaction_id": "txn_8F29A1",
        "customer_id": "CUST-1042",
        "amount": 18450,
        "score": 0.98,
        "is_fraud": True,
        "ring_id": "FR-001",
        "signals": [
            "11 customers share device DEV-77A",
            "6 transactions within 3 minutes",
            "amount is 7.2x normal average"
        ]
    },
    {
        "transaction_id": "txn_8F28C7",
        "customer_id": "CUST-1091",
        "amount": 17980,
        "score": 0.96,
        "is_fraud": True,
        "ring_id": "FR-001",
        "signals": [
            "shared payment instrument PI-204",
            "new IP address",
            "coordinated timing"
        ]
    },
    {
        "transaction_id": "txn_8F27B4",
        "customer_id": "CUST-1138",
        "amount": 18200,
        "score": 0.94,
        "is_fraud": True,
        "ring_id": "FR-001",
        "signals": [
            "shared device DEV-77A",
            "new device",
            "similar transaction amount"
        ]
    },
    {
        "transaction_id": "txn_8F266D",
        "customer_id": "CUST-0877",
        "amount": 8920,
        "score": 0.81,
        "is_fraud": True,
        "ring_id": "FR-002",
        "signals": [
            "velocity spike",
            "shared IP address"
        ]
    }
]


RINGS = [
    {
        "ring_id": "FR-001",
        "risk_score": 98,
        "severity": "CRITICAL",
        "customers": 11,
        "devices": 4,
        "ips": 2,
        "transactions": 37,
        "suspicious_amount": 428000,
        "evidence": TXNS[0]["signals"]
    },
    {
        "ring_id": "FR-002",
        "risk_score": 84,
        "severity": "HIGH",
        "customers": 7,
        "devices": 2,
        "ips": 2,
        "transactions": 19,
        "suspicious_amount": 78420,
        "evidence": [
            "7 customers share an IP",
            "high transaction velocity"
        ]
    },
    {
        "ring_id": "FR-003",
        "risk_score": 72,
        "severity": "HIGH",
        "customers": 5,
        "devices": 3,
        "ips": 1,
        "transactions": 12,
        "suspicious_amount": 42890,
        "evidence": [
            "5 customers share payment instrument",
            "similar amounts"
        ]
    }
]


class ScoreRequest(BaseModel):
    amount: float = Field(gt=0)
    customer_id: str = Field(min_length=3, max_length=80)
    device_id: str | None = Field(default=None, max_length=80)
    ip_address: str | None = Field(default=None, max_length=80)

    transaction_frequency: int = Field(default=1, ge=0)
    customer_age_days: int = Field(default=30, ge=0)
    previous_transaction_count: int = Field(default=0, ge=0)
    previous_fraud_count: int = Field(default=0, ge=0)

    is_new_device: bool = False
    is_new_ip: bool = False


@app.get("/health")
def health():
    database_status = "connected"

    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
    except Exception:
        database_status = "unavailable"

    return {
        "status": "ok",
        "mode": "synthetic-demo",
        "timestamp": datetime.utcnow().isoformat(),
        "database": database_status,
        "database_provider": (
            "neon-postgres"
            if DATABASE_URL.startswith("postgresql")
            else "sqlite"
        ),
        "razorpay": RazorpayTestAdapter().status(),
        "investigator": "local-deterministic",
    }


@app.get("/api/integrations/status")
def integration_status():
    return {
        "database": {
            "provider": (
                "neon-postgres"
                if DATABASE_URL.startswith("postgresql")
                else "sqlite"
            ),
            "configured": bool(os.getenv("DATABASE_URL")),
        },
        "razorpay": RazorpayTestAdapter().status(),
        "investigator": {
            "provider": os.getenv("LLM_PROVIDER", "local"),
            "fallback_available": True,
        },
    }


@app.get("/api/dashboard/summary")
def summary():
    return {
        "total_transactions": 48291,
        "fraud_detected": 1284,
        "high_risk_transactions": 312,
        "fraud_rings": 3,
        "suspicious_amount": 28400000,
        "metrics": metrics(),
    }


@app.get("/api/transactions")
def transactions(
    q: str | None = Query(default=None),
    limit: int = Query(default=100, ge=1, le=500),
):
    items = [
        x for x in TXNS
        if not q or q.lower() in str(x).lower()
    ][:limit]

    return {
        "items": items,
        "total": len(items),
    }


@app.get("/api/transactions/{transaction_id}")
def transaction(transaction_id: str):
    x = next(
        (x for x in TXNS if x["transaction_id"] == transaction_id),
        None
    )

    if not x:
        raise HTTPException(404, "Transaction not found")

    return x


@app.post("/api/transactions/score")
def score(r: ScoreRequest):

    features = {
        "amount": r.amount,
        "transaction_frequency": r.transaction_frequency,
        "customer_age_days": r.customer_age_days,
        "previous_transaction_count": r.previous_transaction_count,
        "previous_fraud_count": r.previous_fraud_count,
        "is_new_device": r.is_new_device,
        "is_new_ip": r.is_new_ip,
    }

    result = predict_fraud(features)

    probability = result["fraud_probability"]
    risk_score = round(probability * 100, 2)

    signals = []

    if r.amount > 10000:
        signals.append("High transaction amount")

    if r.transaction_frequency >= 8:
        signals.append("High transaction velocity")

    if r.previous_fraud_count > 0:
        signals.append("Customer has previous fraud history")

    if r.is_new_device:
        signals.append("Transaction from a new device")

    if r.is_new_ip:
        signals.append("Transaction from a new IP address")

    if probability >= 0.80:
        action = "BLOCK_OR_MANUAL_REVIEW"
    elif probability >= 0.50:
        action = "MANUAL_REVIEW"
    else:
        action = "MONITOR"

    return {
        "customer_id": r.customer_id,
        "model": "Random Forest",
        "prediction": (
            "FRAUD"
            if result["prediction"] == 1
            else "LEGITIMATE"
        ),
        "ml_probability": round(probability, 4),
        "risk_score": risk_score,
        "signals": signals,
        "recommended_action": action,
    }


@app.get("/api/fraud-rings")
def rings():
    return {
        "items": RINGS,
        "total": 3,
    }


@app.get("/api/fraud-rings/{ring_id}")
def ring(ring_id: str):
    x = next(
        (x for x in RINGS if x["ring_id"] == ring_id),
        None
    )

    if not x:
        raise HTTPException(404, "Fraud ring not found")

    return x


@app.get("/api/fraud-rings/{ring_id}/graph")
def graph(ring_id: str):
    ring(ring_id)

    return {
        "ring_id": ring_id,
        "nodes": [
            {"id": "CUST-1042", "type": "customer"},
            {"id": "CUST-1091", "type": "customer"},
            {"id": "DEV-77A", "type": "device"},
            {"id": "IP-103.24", "type": "ip"},
            {"id": "PI-204", "type": "payment_instrument"},
        ],
        "edges": [
            {"source": "CUST-1042", "target": "DEV-77A"},
            {"source": "CUST-1091", "target": "DEV-77A"},
            {"source": "DEV-77A", "target": "IP-103.24"},
            {"source": "CUST-1042", "target": "PI-204"},
            {"source": "CUST-1091", "target": "PI-204"},
        ],
    }


@app.get("/api/fraud-rings/{ring_id}/timeline")
def timeline(ring_id: str):
    ring(ring_id)

    return {
        "ring_id": ring_id,
        "points": [
            {"day": "Aug 21", "customers": 2},
            {"day": "Aug 25", "customers": 4},
            {"day": "Aug 29", "customers": 7},
            {"day": "Sep 03", "customers": 11},
        ],
    }


def investigation(transaction_id: str):
    x = transaction(transaction_id)

    return {
        "transaction_id": transaction_id,
        "risk_summary": "High-confidence coordinated fraud activity.",
        "explanation": (
            "Observed shared devices, payment instruments, and tightly "
            "coordinated timing connect this transaction to a suspicious ring."
        ),
        "key_evidence": x["signals"],
        "recommended_action": "TEMPORARY_RESTRICTION",
        "confidence": 0.94,
        "provider": "local-deterministic",
    }


@app.get("/api/investigations/{transaction_id}")
def get_investigation(transaction_id: str):
    return investigation(transaction_id)


@app.post("/api/investigations/{transaction_id}/run")
def run_investigation(transaction_id: str):
    return investigation(transaction_id)


@app.get("/api/model/metrics")
def metrics():
    p = Path("ml/artifacts/metrics.json")

    if p.exists():
        return json.loads(p.read_text())

    return {
        "model": "Random Forest",
        "test_set_size": 0,
        "accuracy": 0,
        "precision": 0,
        "recall": 0,
        "f1": 0,
        "roc_auc": 0,
        "confusion_matrix": [[0, 0], [0, 0]],
        "false_positives": 0,
    }


@app.post("/api/simulation/block-device")
def simulation(
    device_id: str = Query(min_length=3)
):
    return {
        "device_id": device_id,
        "affected_accounts": 11 if device_id == "DEV-77A" else 0,
        "affected_transactions": 37 if device_id == "DEV-77A" else 0,
        "affected_value": 428000 if device_id == "DEV-77A" else 0,
        "estimated_suspicious_activity_reduction": (
            0.82 if device_id == "DEV-77A" else 0
        ),
        "is_estimate": True,
    }


@app.get("/api/entities/{entity_id}")
def entity(entity_id: str):
    return {
        "entity_id": entity_id,
        "entity_type": (
            "device"
            if entity_id.startswith("DEV")
            else "customer"
        ),
        "relationships": [
            "CUST-1042",
            "CUST-1091",
            "CUST-1138",
        ],
        "risk_context": (
            "Connected to FR-001"
            if entity_id == "DEV-77A"
            else "No ring context"
        ),
    }