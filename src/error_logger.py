
import pandas as pd


def log_invalid_records(df):
    """
    Identify records with invalid Age or Salary values.

    Rules:
    - Age must be between 18 and 60.
    - Salary must be zero or greater.
    """
    invalid_mask = pd.Series(False, index=df.index)

    if "Age" in df.columns:
        age = pd.to_numeric(df["Age"], errors="coerce")
        invalid_mask |= age.isna() | (age < 18) | (age > 60)

    if "Salary" in df.columns:
        salary = pd.to_numeric(df["Salary"], errors="coerce")
        invalid_mask |= salary.isna() | (salary < 0)

    return df.loc[invalid_mask].copy()
