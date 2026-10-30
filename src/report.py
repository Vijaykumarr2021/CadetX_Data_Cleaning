
import pandas as pd
from datetime import datetime

# Load original and cleaned datasets
original = pd.read_csv("data/customer.csv")
cleaned = pd.read_csv("data/cleaned_customer.csv")

# Calculate quality metrics
total_records = len(original)
cleaned_records = len(cleaned)
duplicates_removed = total_records - len(
    original.drop_duplicates()
)
missing_before = original.isnull().sum().sum()
missing_after = cleaned.isnull().sum().sum()

invalid_ages = (~cleaned["Age"].between(18, 60)).sum()
invalid_salaries = (cleaned["Salary"] <= 0).sum()
duplicate_ids = cleaned["EmployeeID"].duplicated().sum()

passed = (
    missing_after == 0
    and invalid_ages == 0
    and invalid_salaries == 0
    and duplicate_ids == 0
)

# Generate report
report = f"""
CADETX DATA QUALITY REPORT
--------------------------
Generated: {datetime.now()}

Original Records: {total_records}
Cleaned Records: {cleaned_records}
Duplicate Rows Removed: {duplicates_removed}
Missing Values Before: {missing_before}
Missing Values After: {missing_after}
Invalid Ages: {invalid_ages}
Invalid Salaries: {invalid_salaries}
Duplicate Employee IDs: {duplicate_ids}

Validation Status: {"PASSED" if passed else "FAILED"}
"""

# Display report
print(report)

# Save report to a text file
with open("reports/data_quality_report.txt", "w") as file:
    file.write(report)

print("Report saved successfully!")
