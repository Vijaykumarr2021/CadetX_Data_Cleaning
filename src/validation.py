
import pandas as pd
import sys

df = pd.read_csv("data/cleaned_customer.csv")

print("Starting Data Validation...\n")

missing = df.isnull().sum().sum()
duplicates = df["EmployeeID"].duplicated().sum()
invalid_age = (~df["Age"].between(18, 60)).sum()
invalid_salary = (
    (df["Salary"].isna()) |
    (df["Salary"] <= 0)
).sum()

print("Missing Values:", missing)
print("Duplicate Employee IDs:", duplicates)
print("Invalid Ages:", invalid_age)
print("Invalid Salaries:", invalid_salary)

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
