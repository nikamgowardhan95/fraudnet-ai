from pathlib import Path
from joblib import load


MODEL_PATH = Path("ml/artifacts/fraud_model.joblib")


def get_model():
    if not MODEL_PATH.exists():
        raise FileNotFoundError(
            f"Fraud model not found at {MODEL_PATH}. "
            "Please run the model training first."
        )

    return load(MODEL_PATH)


def predict_fraud(features: dict):

    model = get_model()

    values = [[
        float(features["amount"]),
        float(features["transaction_frequency"]),
        float(features["customer_age_days"]),
        float(features["previous_transaction_count"]),
        float(features["previous_fraud_count"]),
        int(features["is_new_device"]),
        int(features["is_new_ip"]),
    ]]

    prediction = int(model.predict(values)[0])

    probability = float(
        model.predict_proba(values)[0][1]
    )

    return {
        "prediction": prediction,
        "fraud_probability": probability
    }