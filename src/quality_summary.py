
import pandas as pd
from pathlib import Path
from datetime import datetime

# Project paths
BASE_DIR = Path(__file__).resolve().parent.parent
REPORTS_DIR = BASE_DIR / "reports"

batch_file = REPORTS_DIR / "batch_validation_report.csv"
advanced_file = REPORTS_DIR / "advanced_validation_report.csv"

# Check that reports exist
for file in [batch_file, advanced_file]:
    if not file.exists():
        raise FileNotFoundError(
            f"Required report not found: {file}"
        )

# Read validation reports
batch = pd.read_csv(batch_file)
advanced = pd.read_csv(advanced_file)

# Check required columns
for name, df in [
    ("Batch", batch),
    ("Advanced", advanced)
]:
    required = {"File", "Status"}

    if not required.issubset(df.columns):
        raise ValueError(
            f"{name} report is missing required columns"
        )

# Combine results by filename
combined = batch[["File", "Status"]].rename(
    columns={"Status": "Batch_Status"}
).merge(
    advanced[["File", "Records", "Total_Errors", "Status"]].rename(
        columns={"Status": "Advanced_Status"}
    ),
    on="File",
    how="outer",
    validate="one_to_one",
    indicator=True
)

# Missing or unmatched reports count as failures
combined["Final_Status"] = combined.apply(
    lambda row: (
        "PASSED"
        if (
            row["_merge"] == "both"
            and row["Batch_Status"] == "PASSED"
            and row["Advanced_Status"] == "PASSED"
        )
        else "FAILED"
    ),
    axis=1
)

# Calculate summary metrics
total_files = len(combined)

passed_files = int(
    (combined["Final_Status"] == "PASSED").sum()
)

failed_files = total_files - passed_files

total_records = int(
    pd.to_numeric(
        combined["Records"], errors="coerce"
    ).fillna(0).sum()
)

total_errors = int(
    pd.to_numeric(
        combined["Total_Errors"], errors="coerce"
    ).fillna(0).sum()
)

pass_rate = (
    passed_files / total_files * 100
    if total_files else 0
)

# Save per-file combined report
details_file = REPORTS_DIR / "combined_validation_summary.csv"

combined.drop(columns=["_merge"]).to_csv(
    details_file, index=False
)

# Generate text summary
summary = f"""
CADETX AUTOMATED DATA QUALITY SUMMARY
====================================

Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

Total Datasets: {total_files}
Total Records: {total_records}

Datasets Passed: {passed_files}
Datasets Failed: {failed_files}

Total Advanced Validation Errors: {total_errors}

Dataset Pass Rate: {pass_rate:.2f}%

Overall Status: {
    "PASSED" if failed_files == 0 and total_files > 0
    else "FAILED"
}

Detailed Report: {details_file.name}
"""

output_file = REPORTS_DIR / "data_quality_summary.txt"

output_file.write_text(
    summary.strip() + "\n",
    encoding="utf-8"
)

print(summary)
print("Summary saved to:", output_file)
print("Details saved to:", details_file)
