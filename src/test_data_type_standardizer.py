
import pandas as pd

from data_type_standardizer import standardize_dataframe


def test_numeric_conversion_and_identifier():
    df = pd.DataFrame({
        "EmployeeID": ["001", "002"],
        "Age": ["25", "30"],
        "Salary": ["₹1,200.50", "2,000"]
    })

    result, log = standardize_dataframe(df)

    assert result["EmployeeID"].tolist() == ["001", "002"]
    assert result["Age"].iloc[0] == 25
    assert result["Salary"].iloc[0] == 1200.50
    assert "Salary" in log["numeric_columns_converted"]


def test_date_standardization():
    df = pd.DataFrame({
        "Order_Date": [
            "2026-11-05",
            "05/11/2026",
            "05-11-2026"
        ]
    })

    result, _ = standardize_dataframe(df)

    assert result["Order_Date"].tolist() == [
        "2026-11-05",
        "2026-11-05",
        "2026-11-05"
    ]


def test_text_normalization():
    df = pd.DataFrame({
        "Department": ["  Human   Resources  ", "HR"],
        "Status": [" ACTIVE ", "Pending"]
    })

    result, _ = standardize_dataframe(df)

    assert result["Department"].iloc[0] == "Human Resources"
    assert result["Department"].iloc[1] == "HR"
    assert result["Status"].tolist() == ["active", "pending"]


def test_invalid_numeric_preserved():
    df = pd.DataFrame({
        "Salary": ["1000", "invalid"]
    })

    result, log = standardize_dataframe(df)

    assert result["Salary"].tolist() == ["1000", "invalid"]
    assert len(log["warnings"]) == 1


def test_invalid_date_preserved():
    df = pd.DataFrame({
        "Order_Date": ["31/02/2026", "05/11/2026"]
    })

    result, log = standardize_dataframe(df)

    assert result["Order_Date"].iloc[0] == "31/02/2026"
    assert len(log["warnings"]) == 1


def test_missing_numeric_value_preserved():
    df = pd.DataFrame({
        "Age": ["25", None, "30"]
    })

    result, _ = standardize_dataframe(df)

    assert pd.isna(result["Age"].iloc[1])
    assert result["Age"].iloc[2] == 30
