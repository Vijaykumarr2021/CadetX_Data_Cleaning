
import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

original_path = BASE_DIR / "data" / "customer.csv"
cleaned_path = BASE_DIR / "data" / "cleaned_customer.csv"

original_df = pd.read_csv(original_path)
cleaned_df = pd.read_csv(cleaned_path)

# Calculate total cells
original_cells = original_df.size
cleaned_cells = cleaned_df.size

# Count missing values
missing_before = original_df.isnull().sum().sum()
missing_after = cleaned_df.isnull().sum().sum()

# Count duplicate rows
duplicate_count = original_df.duplicated().sum()

# Calculate percentages
missing_percentage = (
    missing_before / original_cells * 100
    if original_cells else 0
)

duplicate_percentage = (
    duplicate_count / len(original_df) * 100
    if len(original_df) else 0
)

completeness_before = 100 - missing_percentage

completeness_after = (
    (1 - missing_after / cleaned_cells) * 100
    if cleaned_cells else 0
)

# Completeness-based quality score
quality_score = completeness_after

# Display results
print("\nCADETX DATA QUALITY ANALYSIS")
print("----------------------------")
print("Original Records:", len(original_df))
print("Cleaned Records:", len(cleaned_df))
print("Missing Values Before:", missing_before)
print("Missing Values After:", missing_after)
print("Duplicate Rows:", duplicate_count)
print(f"Missing Value Rate: {missing_percentage:.2f}%")
print(f"Duplicate Rate: {duplicate_percentage:.2f}%")
print(f"Original Completeness: {completeness_before:.2f}%")
print(f"Cleaned Completeness: {completeness_after:.2f}%")
print(f"Data Quality Score: {quality_score:.2f}%")

# Save report
report = pd.DataFrame([{
    "Original_Records": len(original_df),
    "Cleaned_Records": len(cleaned_df),
    "Missing_Before": missing_before,
    "Missing_After": missing_after,
    "Duplicates_Before": duplicate_count,
    "Missing_Rate_Percent": round(missing_percentage, 2),
    "Duplicate_Rate_Percent": round(duplicate_percentage, 2),
    "Completeness_Before": round(completeness_before, 2),
    "Completeness_After": round(completeness_after, 2),
    "Quality_Score": round(quality_score, 2)
}])

report_path = BASE_DIR / "reports" / "quality_score.csv"
report_path.parent.mkdir(parents=True, exist_ok=True)

report.to_csv(report_path, index=False)

print("\nQuality report saved to:", report_path)
