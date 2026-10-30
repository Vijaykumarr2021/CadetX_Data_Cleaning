
import subprocess
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

scripts = [
    "check_errors.py",
    "main.py",
    "validation.py",
    "report.py",
    "quality_score.py",
    "visualization.py",
    "dashboard.py"
]

print("Starting CadetX Data Pipeline...\n")

for script in scripts:
    print(f"\nRunning {script}...", flush=True)

    subprocess.run(
        [sys.executable, str(BASE_DIR / "src" / script)],
        cwd=BASE_DIR,
        check=True
    )

print("\nCadetX Pipeline Completed Successfully!")
