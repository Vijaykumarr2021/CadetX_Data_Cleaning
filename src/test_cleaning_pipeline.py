
import json

import pandas as pd
import pytest

from cleaning_pipeline import (
    process_dataframe,
    run_pipeline
)


def test_complete_pipeline():
    df = pd.DataFrame({
        "EmployeeID": [
            "001", "002", "002",
            "003", "004", "005"
        ],
        "Age": [
            "20", "30", "30",
            None, "40", "50"
        ],
        "Salary": [
            "10", "11", "11",
            "12", "13", "100"
        ],
        "Department": [
            " Sales ", "HR", "HR",
            "Sales", None, "HR"
        ]
    })

    original = df.copy(deep=True)

    result, logs, audit = process_dataframe(df)

    # Exact duplicate removed during cleaning
    assert len(result) == 5
    assert logs["cleaning"]["duplicates_removed"] == 1

    # Missing Age filled using median
    assert float(result.loc[2, "Age"]) == 35

    # Leading zeros preserved
    assert result["EmployeeID"].iloc[0] == "001"

    # Outlier flagged, not removed or capped
    assert float(result["Salary"].iloc[-1]) == 100
    assert logs["outliers"]["outliers_flagged"] == 1
    assert len(audit["outliers"]) == 1

    # Source dataframe remains unchanged
    pd.testing.assert_frame_equal(df, original)


def test_conflicting_ids_retained():
    df = pd.DataFrame({
        "EmployeeID": ["A", "A", "B", "C", "D"],
        "Salary": [10, 20, 30, 40, 50]
    })

    result, logs, audit = process_dataframe(df)

    assert len(result) == 5
    assert (
        logs["deduplication"][
            "key_collision_groups_retained"
        ] == 1
    )
    assert len(audit["duplicates"]) == 2


def test_date_and_status_standardization():
    df = pd.DataFrame({
        "EmployeeID": ["001", "002"],
        "Order_Date": [
            "05/11/2026", "2026-11-06"
        ],
        "Status": [None, " Active "],
        "Age": ["20", "30"]
    })

    result, _, _ = process_dataframe(df)

    assert result["Order_Date"].tolist() == [
        "2026-11-05", "2026-11-06"
    ]

    assert result["Status"].tolist() == [
        "Unknown", "active"
    ]


def test_invalid_numeric_preserved():
    df = pd.DataFrame({
        "EmployeeID": [
            "001", "002", "003", "004", "005"
        ],
        "Salary": [
            "100", "invalid", None, "30", "40"
        ]
    })

    result, logs, _ = process_dataframe(df)

    assert result["Salary"].iloc[1] == "invalid"
    assert pd.isna(result["Salary"].iloc[2])
    assert logs["missing_values"]["warnings"]


def test_pipeline_creates_reports(tmp_path):
    input_dir = tmp_path / "input"
    output_dir = tmp_path / "output"
    reports_dir = tmp_path / "reports"

    input_dir.mkdir()

    df = pd.DataFrame({
        "EmployeeID": [
            "001", "002", "003",
            "004", "005", "006"
        ],
        "Salary": [
            10, 11, 12, 13, 14, 100
        ]
    })

    df.to_csv(
        input_dir / "sample.csv",
        index=False
    )

    report = run_pipeline(
        input_dir=input_dir,
        output_dir=output_dir,
        reports_dir=reports_dir
    )

    assert report["total_files"] == 1
    assert report["total_output_rows"] == 6

    assert (
        output_dir / "sample_pipeline_cleaned.csv"
    ).exists()

    assert (
        reports_dir / "pipeline_run_report.json"
    ).exists()

    assert (
        reports_dir / "pipeline_duplicate_audit.csv"
    ).exists()

    assert (
        reports_dir / "pipeline_outlier_audit.csv"
    ).exists()

    with (
        reports_dir / "pipeline_run_report.json"
    ).open() as file:
        saved_report = json.load(file)

    assert saved_report["total_files"] == 1
    assert saved_report["outlier_policy"] == "flag_only"


def test_empty_input_directory(tmp_path):
    input_dir = tmp_path / "empty"
    input_dir.mkdir()

    with pytest.raises(
        FileNotFoundError,
        match="No CSV files"
    ):
        run_pipeline(
            input_dir=input_dir,
            output_dir=tmp_path / "out",
            reports_dir=tmp_path / "reports"
        )
