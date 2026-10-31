
import pandas as pd


def validate_dataframe(df):
    """Return validation error counts for a DataFrame."""

    errors = {}

    errors["Missing_Values"] = int(
        df.isna().sum().sum()
    )

    errors["Duplicate_Rows"] = int(
        df.duplicated().sum()
    )

    id_columns = [
        col for col in ["EmployeeID", "OrderID"]
        if col in df.columns
    ]

    errors["Duplicate_IDs"] = sum(
        int(df[col].duplicated().sum())
        for col in id_columns
    )

    errors["Invalid_IDs"] = 0

    for col in id_columns:
        values = pd.to_numeric(
            df[col], errors="coerce"
        )

        errors["Invalid_IDs"] += int(
            (
                values.isna()
                | (values <= 0)
                | (values % 1 != 0)
            ).sum()
        )

    errors["Invalid_Ages"] = 0

    if "Age" in df.columns:
        ages = pd.to_numeric(
            df["Age"], errors="coerce"
        )

        errors["Invalid_Ages"] = int(
            (~ages.between(18, 60)).sum()
        )

    errors["Invalid_Salaries"] = 0

    if "Salary" in df.columns:
        salaries = pd.to_numeric(
            df["Salary"], errors="coerce"
        )

        errors["Invalid_Salaries"] = int(
            (salaries.isna() | (salaries <= 0)).sum()
        )

    errors["Invalid_Quantities"] = 0

    if "Quantity" in df.columns:
        quantities = pd.to_numeric(
            df["Quantity"], errors="coerce"
        )

        errors["Invalid_Quantities"] = int(
            (
                quantities.isna()
                | (quantities <= 0)
                | (quantities % 1 != 0)
            ).sum()
        )

    errors["Invalid_Prices"] = 0

    if "Price" in df.columns:
        prices = pd.to_numeric(
            df["Price"], errors="coerce"
        )

        errors["Invalid_Prices"] = int(
            (prices.isna() | (prices <= 0)).sum()
        )

    errors["Invalid_Text_Fields"] = 0

    for col in ["Name", "Product", "Department"]:
        if col in df.columns:
            values = df[col].astype("string").str.strip()

            invalid = (
                values.isna()
                | values.eq("")
                | values.str.lower().eq("unknown")
            ).fillna(True)

            errors["Invalid_Text_Fields"] += int(
                invalid.sum()
            )

    return errors
