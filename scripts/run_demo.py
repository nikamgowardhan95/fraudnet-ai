import subprocess, sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from scripts.generate_dataset import generate
print('Generated', generate())
try:
 from ml.train import train
 print('Metrics:', train())
except Exception as exc:
 print('Training skipped:', exc)
print('Start backend with: uvicorn backend.app.main:app --reload --port 8000')
print('Start frontend with: pnpm dev')
