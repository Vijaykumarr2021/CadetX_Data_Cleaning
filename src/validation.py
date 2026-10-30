
import pandas as pd
import sys
from pathlib import Path

# Project folder path
BASE_DIR = Path(__file__).resolve().parent.parent

# Load cleaned dataset
file_path = BASE_DIR / "data" / "cleaned_customer.csv"

df = pd.read_csv(file_path)

print("Starting Data Validation...\n")

# Check missing values
missing = df.isnull().sum().sum()

# Check duplicate Employee IDs
duplicates = df["EmployeeID"].duplicated().sum()

# Convert Age and Salary to numeric values
age = pd.to_numeric(df["Age"], errors="coerce")
salary = pd.to_numeric(df["Salary"], errors="coerce")

# Check invalid ages (valid range: 18 to 60)
invalid_age = (~age.between(18, 60)).sum()

# Check invalid salaries
invalid_salary = (
    salary.isna() | (salary <= 0)
).sum()

# Display validation results
print("Missing Values:", missing)
print("Duplicate Employee IDs:", duplicates)
print("Invalid Ages:", invalid_age)
print("Invalid Salaries:", invalid_salary)

# Final validation
if (
    missing == 0
    and duplicates == 0
    and invalid_age == 0
    and invalid_salary == 0
):
    print("\nValidation Passed!")
else:
    print("\nValidation Failed!")
    sys.exit(1)
