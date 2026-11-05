
import pandas as pd

from advanced_cleaner import clean_dataframe


def test_duplicate_removal():
    df = pd.DataFrame({
        "EmployeeID": [101, 102, 102],
        "Age": [25, 30, 30],
        "Salary": [30000, 40000, 40000]
    })

    cleaned, log = clean_dataframe(df)

    assert len(cleaned) == 2
    assert log["duplicates_removed"] == 1


def test_missing_numeric_values():
    df = pd.DataFrame({
        "Age": [20, 30, None],
        "Salary": [20000, 40000, None]
    })

    cleaned, log = clean_dataframe(df)

    assert cleaned["Age"].iloc[2] == 25
    assert cleaned["Salary"].iloc[2] == 30000
    assert log["missing_after"] == 0


def test_whitespace_cleaning():
    df = pd.DataFrame({
        "Name": [" Amit ", "Rohit"],
        "Department": [" Sales ", "HR"]
    })

    cleaned, log = clean_dataframe(df)

    assert cleaned["Name"].iloc[0] == "Amit"
    assert cleaned["Department"].iloc[0] == "Sales"
    assert log["whitespace_values_trimmed"] == 2


def test_identifier_not_imputed():
    df = pd.DataFrame({
        "EmployeeID": ["101", None],
        "Age": [25, 30]
    })

    cleaned, _ = clean_dataframe(df)

    assert pd.isna(
        cleaned["EmployeeID"].iloc[1]
    )
