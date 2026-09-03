FEATURES=['amount','transaction_frequency','customer_age_days','previous_transaction_count','previous_fraud_count','is_new_device','is_new_ip']
def row_to_features(row):
    return [float(row[k]) if k not in ('is_new_device','is_new_ip') else int(row[k] in (True,'True',1,'1')) for k in FEATURES]
