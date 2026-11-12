import sys
sys.path.insert(0, ".")
from app.pipeline import run_check

with open("../samples/stale_pricing.txt", "r", encoding="utf-8") as f:
    text = f.read().strip()

print("Running pipeline on sample text...")
res = run_check(text)
import json
print(json.dumps(res, indent=2))
