
import sys
from pathlib import Path

import pandas as pd
import pytest

# Import validation_rules.py from src/
SRC_DIR = Path(__file__).resolve().parent.parent / "src"
sys.path.insert(0, str(SRC_DIR))

from validation_rules import validate_dataframe


def test_valid_sales_data():
    df = pd.DataFrame({
        "OrderID": [1, 2],
        "Product": ["Laptop", "Mouse"],
        "Quantity": [2, 3],
        "Price": [50000, 500]
    })

    errors = validate_dataframe(df)

    assert sum(errors.values()) == 0


def test_negative_price():
    df = pd.DataFrame({
        "OrderID": [1],
        "Product": ["Keyboard"],
        "Quantity": [1],
        "Price": [-100]
    })

    errors = validate_dataframe(df)

    assert errors["Invalid_Prices"] == 1


def test_invalid_quantity():
    df = pd.DataFrame({
        "OrderID": [1, 2, 3],
        "Product": ["Laptop", "Mouse", "Keyboard"],
        "Quantity": [-2, 0, 1.5],
        "Price": [50000, 500, 1000]
    })

    errors = validate_dataframe(df)

    assert errors["Invalid_Quantities"] == 3


def test_duplicate_order_id():
    df = pd.DataFrame({
        "OrderID": [1, 1],
        "Product": ["Laptop", "Mouse"],
        "Quantity": [1, 2],
        "Price": [50000, 500]
    })

    errors = validate_dataframe(df)

    assert errors["Duplicate_IDs"] == 1


def test_missing_value():
    df = pd.DataFrame({
        "OrderID": [1, 2],
        "Product": ["Laptop", None],
        "Quantity": [2, 1],
        "Price": [50000, 500]
    })

    errors = validate_dataframe(df)

    assert errors["Missing_Values"] == 1


def test_invalid_employee_age():
    df = pd.DataFrame({
        "EmployeeID": [1, 2],
        "Name": ["Amit", "Ravi"],
        "Age": [17, 65],
        "Department": ["IT", "HR"],
        "Salary": [30000, 40000]
    })

    errors = validate_dataframe(df)

    assert errors["Invalid_Ages"] == 2


def test_invalid_salary():
    df = pd.DataFrame({
        "EmployeeID": [1, 2],
        "Name": ["Amit", "Ravi"],
        "Age": [25, 30],
        "Department": ["IT", "HR"],
        "Salary": [-1000, 0]
    })

    errors = validate_dataframe(df)

    assert errors["Invalid_Salaries"] == 2


def test_unknown_product():
    df = pd.DataFrame({
        "OrderID": [1],
        "Product": ["Unknown"],
        "Quantity": [2],
        "Price": [100]
    })

    errors = validate_dataframe(df)

    assert errors["Invalid_Text_Fields"] == 1


def test_invalid_sales_csv():
    test_file = (
        Path(__file__).resolve().parent
        / "invalid_sales.csv"
    )

    df = pd.read_csv(test_file)
    errors = validate_dataframe(df)

    assert errors["Invalid_Quantities"] == 2
    assert errors["Invalid_Prices"] == 1
    assert errors["Invalid_Text_Fields"] == 1
    assert sum(errors.values()) == 4


@pytest.mark.parametrize(
    "quantity",
    [-1, 0, 1.5, "invalid"]
)
def test_bad_quantity_values(quantity):
    df = pd.DataFrame({
        "OrderID": [1],
        "Product": ["Mouse"],
        "Quantity": [quantity],
        "Price": [500]
    })

    errors = validate_dataframe(df)

    assert errors["Invalid_Quantities"] == 1
