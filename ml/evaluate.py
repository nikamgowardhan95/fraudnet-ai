import json
from pathlib import Path
from .train import train
if __name__=='__main__':
    metrics=train(); print(json.dumps(metrics,indent=2)); assert metrics['test_set_size']>0
