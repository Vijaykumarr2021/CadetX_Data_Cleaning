
import pandas as pd
import pytest

from advanced_deduplicator import (
    deduplicate_dataframe
)


def test_exact_duplicate_removed():
    df = pd.DataFrame({
        "EmployeeID": ["101", "101", "102"],
        "Salary": [20000, 20000, 30000]
    })

    result, log, audit = deduplicate_dataframe(df)

    assert len(result) == 2
    assert log["exact_duplicates_removed"] == 1
    assert audit[0]["source_row"] == 3
    assert audit[0]["action"] == "removed_keep_first"


def test_same_id_different_values():
    df = pd.DataFrame({
        "EmployeeID": ["101", "101"],
        "Salary": [10000, 20000]
    })

    result, log, audit = deduplicate_dataframe(df)

    assert len(result) == 2
    assert log["key_collision_groups_retained"] == 1
    assert log["key_collision_rows_retained"] == 2
    assert len(audit) == 2
    assert all(
        item["action"] == "retained_for_review"
        for item in audit
    )


def test_missing_identifiers():
    df = pd.DataFrame({
        "EmployeeID": ["", None, "101"],
        "Salary": [10000, 20000, 30000]
    })

    result, log, audit = deduplicate_dataframe(df)

    assert len(result) == 3
    assert log["key_collision_groups_retained"] == 0
    assert audit == []


def test_automatic_id_detection():
    df = pd.DataFrame({
        "Employee_ID": ["A1", "A1"],
        "Age": [23, 24]
    })

    result, log, _ = deduplicate_dataframe(df)

    assert len(result) == 2
    assert log["key_columns_used"] == ["Employee_ID"]
    assert log["key_collision_groups_retained"] == 1


def test_multiple_key_columns():
    df = pd.DataFrame({
        "CustomerID": ["A", "A", "A"],
        "OrderID": ["1", "1", "2"],
        "Amount": [10, 20, 30]
    })

    result, log, _ = deduplicate_dataframe(
        df,
        key_columns=["CustomerID", "OrderID"]
    )

    assert len(result) == 3
    assert log["key_collision_groups_retained"] == 1


def test_without_identifier():
    df = pd.DataFrame({
        "Name": ["Amit", "Amit"],
        "City": ["Delhi", "Mumbai"]
    })

    result, log, _ = deduplicate_dataframe(df)

    assert len(result) == 2
    assert log["key_columns_used"] == []


def test_original_dataframe_unchanged():
    df = pd.DataFrame({
        "EmployeeID": ["101", "101"],
        "Age": [20, 20]
    })

    original = df.copy(deep=True)

    deduplicate_dataframe(df)

    pd.testing.assert_frame_equal(df, original)


def test_invalid_key_column():
    df = pd.DataFrame({
        "EmployeeID": ["101"]
    })

    with pytest.raises(
        ValueError,
        match="Key columns not found"
    ):
        deduplicate_dataframe(
            df,
            key_columns=["MissingColumn"]
        )
