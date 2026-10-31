
import pandas as pd
from pathlib import Path
from validation_rules import validate_dataframe

BASE_DIR = Path(__file__).resolve().parent.parent
INPUT_DIR = BASE_DIR / "data" / "processed"
REPORTS_DIR = BASE_DIR / "reports"

REPORTS_DIR.mkdir(parents=True, exist_ok=True)

results = []

df = pd.read_csv(file)
errors = validate_dataframe(df)

if not csv_files:
    print("No CSV files found in data/processed")
    raise SystemExit(1)

print("Starting CadetX Advanced Validation...\n")

for file in csv_files:
    df = pd.read_csv(file)
    errors = {}

    # Check missing values
    errors["Missing_Values"] = int(
        df.isna().sum().sum()
    )

    # Check duplicate rows
    errors["Duplicate_Rows"] = int(
        df.duplicated().sum()
    )

    # Check duplicate IDs
    id_columns = [
        col for col in ["EmployeeID", "OrderID"]
        if col in df.columns
    ]

    errors["Duplicate_IDs"] = sum(
        int(df[col].duplicated().sum())
        for col in id_columns
    )

    # Check positive numeric IDs
    errors["Invalid_IDs"] = 0

    for col in id_columns:
        values = pd.to_numeric(
            df[col], errors="coerce"
        )
        errors["Invalid_IDs"] += int(
            (values.isna() |
             (values <= 0) |
             (values % 1 != 0)).sum()
        )

    # Check employee ages
    errors["Invalid_Ages"] = 0

    if "Age" in df.columns:
        ages = pd.to_numeric(
            df["Age"], errors="coerce"
        )

        errors["Invalid_Ages"] = int(
            (~ages.between(18, 60)).sum()
        )

    # Check employee salaries
    errors["Invalid_Salaries"] = 0

    if "Salary" in df.columns:
        salaries = pd.to_numeric(
            df["Salary"], errors="coerce"
        )

        errors["Invalid_Salaries"] = int(
            (salaries.isna() |
             (salaries <= 0)).sum()
        )

    # Check sales quantities
    errors["Invalid_Quantities"] = 0

    if "Quantity" in df.columns:
        quantities = pd.to_numeric(
            df["Quantity"], errors="coerce"
        )

        errors["Invalid_Quantities"] = int(
            (quantities.isna() |
             (quantities <= 0) |
             (quantities % 1 != 0)).sum()
        )

    # Check sales prices
    errors["Invalid_Prices"] = 0

    if "Price" in df.columns:
        prices = pd.to_numeric(
            df["Price"], errors="coerce"
        )

        errors["Invalid_Prices"] = int(
            (prices.isna() |
             (prices <= 0)).sum()
        )

    # Check required text fields
    errors["Invalid_Text_Fields"] = 0

    for col in ["Name", "Product", "Department"]:
        if col in df.columns:
            values = df[col].astype("string").str.strip()

            invalid = (
                values.isna() |
                values.eq("") |
                values.str.lower().eq("unknown")
            ).fillna(True)

            errors["Invalid_Text_Fields"] += int(
                invalid.sum()
            )

    # Determine final status
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
    print("Records:", len(df))
    print("Total Errors:", total_errors)
    print("Status:", status)
    print("-" * 40)

# Generate combined report
report = pd.DataFrame(results)

output_file = REPORTS_DIR / "advanced_validation_report.csv"
report.to_csv(output_file, index=False)

print("\nAdvanced Validation Completed!")
print("Total Files:", len(report))
print("Passed:", int((report["Status"] == "PASSED").sum()))
print("Failed:", int((report["Status"] == "FAILED").sum()))
print("Report saved to:", output_file)
