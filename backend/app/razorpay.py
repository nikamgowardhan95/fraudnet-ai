import os
class RazorpayTestAdapter:
    """Non-charging test-mode boundary. Synthetic mode remains the default."""
    def __init__(self):
        self.enabled=bool(os.getenv('RAZORPAY_KEY_ID') and os.getenv('RAZORPAY_KEY_SECRET'))
        self.mode='test' if self.enabled else 'synthetic'
    def status(self):
        return {'enabled':self.enabled,'mode':self.mode,'charges_enabled':False,'message':'No real payments are processed by FraudNet AI.'}
