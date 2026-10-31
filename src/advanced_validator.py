
import pandas as pd
from pathlib import Path
from validation_rules import validate_dataframe

BASE_DIR = Path(__file__).resolve().parent.parent
INPUT_DIR = BASE_DIR / "data" / "processed"
REPORTS_DIR = BASE_DIR / "reports"

REPORTS_DIR.mkdir(parents=True, exist_ok=True)

csv_files = sorted(INPUT_DIR.glob("*.csv"))

if not csv_files:
    print("No CSV files found in data/processed")
    raise SystemExit(1)

results = []

print("Starting CadetX Advanced Validation...\n")

for file in csv_files:
    df = pd.read_csv(file)

    # Apply reusable validation rules
    errors = validate_dataframe(df)

    total_errors = sum(errors.values())
    status = "PASSED" if total_errors == 0 else "FAILED"

    results.append({
        "File": file.name,
        "Records": len(df),
        **errors,
        "Total_Errors": total_errors,
        "Status": status
    })

    print(f"File: {file.name}")
    print(f"Records: {len(df)}")
    print(f"Total Errors: {total_errors}")
    print(f"Status: {status}")
    print("-" * 40)

# Generate advanced validation report
report = pd.DataFrame(results)

output_file = REPORTS_DIR / "advanced_validation_report.csv"
report.to_csv(output_file, index=False)

print("\nAdvanced Validation Completed!")
print("Total Files:", len(report))
print("Passed:", int((report["Status"] == "PASSED").sum()))
print("Failed:", int((report["Status"] == "FAILED").sum()))
print("Report saved to:", output_file)
