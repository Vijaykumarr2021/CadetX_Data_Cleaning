
import subprocess
import sys
from pathlib import Path

SRC_DIR = Path(__file__).resolve().parent

scripts = [
    "batch_cleaner.py",
    "batch_validator.py",
    "advanced_validator.py",
    "quality_summary.py"
]

print("Starting CadetX Batch Pipeline...\n", flush=True)

for script in scripts:
    print(f"Running {script}...", flush=True)

    subprocess.run(
        [sys.executable, str(SRC_DIR / script)],
        check=True
    )

print("\nCadetX Batch Pipeline Completed Successfully!")
