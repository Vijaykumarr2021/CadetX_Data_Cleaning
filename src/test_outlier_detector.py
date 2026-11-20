
import pandas as pd
import pytest

from outlier_detector import analyze_outliers


def sample_salary_data():
    return pd.DataFrame({
        "Salary": [10, 11, 12, 13, 14, 100]
    })


# Test 1: IQR detects an outlier
def test_iqr_detection():
    df = sample_salary_data()

    result, summary, audit = analyze_outliers(df)

    assert summary["outliers_flagged"] == 1
    assert len(result) == 6
    assert result["Salary"].iloc[-1] == 100
    assert audit[0]["source_row"] == 7
    assert "IQR" in audit[0]["detected_by"]


# Test 2: No outliers in normal values
def test_no_outliers():
    df = pd.DataFrame({
        "Salary": [10, 11, 12, 13, 14, 15]
    })

    result, summary, audit = analyze_outliers(df)

    assert len(result) == 6
    assert summary["outliers_flagged"] == 0
    assert audit == []


# Test 3: Optional capping
def test_iqr_capping():
    df = sample_salary_data()

    result, summary, audit = analyze_outliers(
        df, mode="cap"
    )

    assert float(result["Salary"].iloc[-1]) == 17.5
    assert summary["values_capped"] == 1
    assert audit[0]["action"] == "capped_to_iqr_bound"


# Test 4: Identifiers are not analyzed
def test_identifier_ignored():
    df = pd.DataFrame({
        "EmployeeID": [
            "001", "002", "003",
            "004", "005", "99999"
        ],
        "Age": [20, 21, 22, 23, 24, 25]
    })

    result, summary, _ = analyze_outliers(df)

    assert result["EmployeeID"].iloc[-1] == "99999"
    assert summary["outliers_flagged"] == 0
    assert "EmployeeID" not in summary["columns_analyzed"]


# Test 5: Missing values are preserved
def test_missing_values_preserved():
    df = pd.DataFrame({
        "Salary": [10, 11, None, 12, 13, 100]
    })

    result, summary, _ = analyze_outliers(df)

    assert pd.isna(result["Salary"].iloc[2])
    assert summary["outliers_flagged"] == 1


# Test 6: Invalid numeric values are protected
def test_invalid_numeric_preserved():
    df = pd.DataFrame({
        "Salary": [
            "10", "11", "12",
            "invalid", "13", "100"
        ]
    })

    result, summary, _ = analyze_outliers(df)

    assert result["Salary"].iloc[3] == "invalid"
    assert summary["outliers_flagged"] == 0
    assert len(summary["warnings"]) == 1


# Test 7: Small datasets are skipped
def test_small_dataset():
    df = pd.DataFrame({
        "Salary": [10, 12, 500]
    })

    result, summary, audit = analyze_outliers(df)

    assert len(result) == 3
    assert summary["outliers_flagged"] == 0
    assert audit == []
    assert len(summary["warnings"]) == 1


# Test 8: Z-score detection
def test_z_score_detection():
    df = pd.DataFrame({
        "Salary": [10] * 20 + [100]
    })

    result, summary, audit = analyze_outliers(df)

    assert len(result) == 21
    assert summary["outliers_flagged"] == 1
    assert "Z-score" in audit[0]["detected_by"]


def test_invalid_mode():
    df = sample_salary_data()

    with pytest.raises(ValueError):
        analyze_outliers(df, mode="delete")
