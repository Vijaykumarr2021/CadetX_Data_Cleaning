
import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
INPUT_DIR = BASE_DIR / "data" / "processed"
REPORTS_DIR = BASE_DIR / "reports"

REPORTS_DIR.mkdir(parents=True, exist_ok=True)

results = []

csv_files = sorted(INPUT_DIR.glob("*.csv"))

if not csv_files:
    print("No CSV files found in data/processed")
    raise SystemExit(1)

print("Starting CadetX Batch Validation...\n")

for file in csv_files:
    print(f"Validating: {file.name}")

    df = pd.read_csv(file)

    # Check missing values
    missing_values = int(df.isna().sum().sum())

    # Check duplicate rows
    duplicate_rows = int(df.duplicated().sum())

    # Check duplicate IDs when present
    id_column = next(
        (
            col for col in ["EmployeeID", "OrderID"]
            if col in df.columns
        ),
        None
    )

    duplicate_ids = (
        int(df[id_column].duplicated().sum())
        if id_column else 0
    )

    # Check ages only when Age column exists
    invalid_ages = 0

    if "Age" in df.columns:
        ages = pd.to_numeric(
            df["Age"], errors="coerce"
        )

        invalid_ages = int(
            (~ages.between(18, 60)).sum()
        )

    # Check salaries only when Salary exists
    invalid_salaries = 0

    if "Salary" in df.columns:
        salaries = pd.to_numeric(
            df["Salary"], errors="coerce"
        )

        invalid_salaries = int(
            (salaries.isna() | (salaries <= 0)).sum()
        )

    # Overall validation status
    passed = (
        missing_values == 0
        and duplicate_rows == 0
        and duplicate_ids == 0
        and invalid_ages == 0
        and invalid_salaries == 0
    )

    status = "PASSED" if passed else "FAILED"

    results.append({
        "File": file.name,
        "Total_Records": len(df),
        "Missing_Values": missing_values,
        "Duplicate_Rows": duplicate_rows,
        "Duplicate_IDs": duplicate_ids,
        "Invalid_Ages": invalid_ages,
        "Invalid_Salaries": invalid_salaries,
        "Status": status
    })

    print("Records:", len(df))
    print("Missing Values:", missing_values)
    print("Duplicate Rows:", duplicate_rows)
    print("Duplicate IDs:", duplicate_ids)
    print("Invalid Ages:", invalid_ages)
    print("Invalid Salaries:", invalid_salaries)
    print("Status:", status)
    print("-" * 40)

# Generate combined report
report_df = pd.DataFrame(results)

output_file = REPORTS_DIR / "batch_validation_report.csv"

report_df.to_csv(output_file, index=False)

print("\nBatch Validation Completed!")
print("Total Files:", len(report_df))
print("Passed:", int((report_df["Status"] == "PASSED").sum()))
print("Failed:", int((report_df["Status"] == "FAILED").sum()))
print("Report saved to:", output_file)
