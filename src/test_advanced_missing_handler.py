
import pandas as pd

from advanced_missing_handler import impute_dataframe


# Test 1: Median imputation
def test_median_imputation():
    df = pd.DataFrame({
        "Age": ["20", None, "40"]
    })

    result, log = impute_dataframe(df)

    assert result["Age"].iloc[1] == 30
    assert log["missing_after"] == 0


# Test 2: Mode imputation
def test_mode_imputation():
    df = pd.DataFrame({
        "Department": [
            "Sales", "Sales", None, "HR"
        ]
    })

    result, _ = impute_dataframe(df)

    assert result["Department"].iloc[2] == "Sales"


# Test 3: Constant imputation
def test_constant_imputation():
    df = pd.DataFrame({
        "Status": ["active", None]
    })

    result, _ = impute_dataframe(df)

    assert result["Status"].iloc[1] == "Unknown"


# Test 4: Preserve identifiers
def test_identifier_preserved():
    df = pd.DataFrame({
        "EmployeeID": ["001", None],
        "Age": [25, 30]
    })

    result, _ = impute_dataframe(df)

    assert result["EmployeeID"].iloc[0] == "001"
    assert pd.isna(result["EmployeeID"].iloc[1])


# Test 5: Invalid numeric values
def test_invalid_numeric_preserved():
    df = pd.DataFrame({
        "Salary": ["1000", "invalid", None]
    })

    result, log = impute_dataframe(df)

    assert result["Salary"].iloc[1] == "invalid"
    assert pd.isna(result["Salary"].iloc[2])
    assert len(log["warnings"]) == 1


# Test 6: All missing numeric values
def test_all_missing_numeric():
    df = pd.DataFrame({
        "Age": [None, None]
    })

    result, log = impute_dataframe(df)

    assert result["Age"].isna().sum() == 2
    assert len(log["warnings"]) == 1


# Test 7: Handle blank strings
def test_blank_string_as_missing():
    df = pd.DataFrame({
        "Department": ["Sales", "", "Sales"]
    })

    result, log = impute_dataframe(df)

    assert result["Department"].iloc[1] == "Sales"
    assert log["missing_before"] == 1
    assert log["missing_after"] == 0
