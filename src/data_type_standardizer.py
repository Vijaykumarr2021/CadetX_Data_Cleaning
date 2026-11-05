
import json
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent
INPUT_DIR = BASE_DIR / "data" / "advanced_cleaned"
OUTPUT_DIR = BASE_DIR / "data" / "standardized"
REPORTS_DIR = BASE_DIR / "reports"

NUMERIC_COLUMNS = {
    "age", "salary", "price", "amount", "quantity"
}

DATE_COLUMNS = {
    "date", "orderdate", "transactiondate",
    "joiningdate", "hiredate"
}

TEXT_COLUMNS = {
    "department", "city", "category", "status"
}

DATE_FORMATS = (
    "%Y-%m-%d",
    "%d/%m/%Y",
    "%d-%m-%Y"
)


def normalize_column_name(name):
    return name.strip().lower().replace("_", "").replace(" ", "")


def normalize_date(value):
    if pd.isna(value) or str(value).strip() == "":
        return pd.NA

    text = str(value).strip()

    for date_format in DATE_FORMATS:
        try:
            parsed = datetime.strptime(text, date_format)
            return parsed.strftime("%Y-%m-%d")
        except ValueError:
            continue

    return None


def normalize_text(value, column_key):
    if not isinstance(value, str):
        return value

    text = " ".join(value.split())

    if column_key == "status":
        text = text.casefold()

    return text


def standardize_dataframe(df):
    cleaned = df.copy()

    log = {
        "total_rows": len(df),
        "numeric_columns_converted": [],
        "date_columns_standardized": [],
        "text_values_changed": {},
        "warnings": []
    }

    for column in cleaned.columns:
        key = normalize_column_name(column)

        # Convert known numeric columns
        if key in NUMERIC_COLUMNS:
            values = cleaned[column].astype("string")

            normalized = (
                values.str.strip()
                .str.replace(",", "", regex=False)
                .str.replace("₹", "", regex=False)
                .str.replace("$", "", regex=False)
                .replace("", pd.NA)
            )

            converted = pd.to_numeric(
                normalized, errors="coerce"
            )

            invalid = normalized.notna() & converted.isna()

            if invalid.any():
                log["warnings"].append({
                    "column": column,
                    "issue": "Invalid numeric values",
                    "count": int(invalid.sum()),
                    "action": "Column preserved for review"
                })
                continue

            cleaned[column] = converted

            log["numeric_columns_converted"].append(
                column
            )

        # Convert known date columns
        
        elif key in DATE_COLUMNS:
            # Keep results in a Python list so invalid dates
            # remain None until validation is complete.
            converted_values = [
                normalize_date(value)
                for value in cleaned[column]
            ]

            invalid_count = sum(
                value is None
                for value in converted_values
            )

            if invalid_count > 0:
                log["warnings"].append({
                    "column": column,
                    "issue": "Invalid date values",
                    "count": invalid_count,
                    "action": "Column preserved for review"
                })
                continue

            cleaned[column] = pd.Series(
                converted_values,
                index=cleaned.index,
                dtype="string"
            )

            log["date_columns_standardized"].append(
                column
            )


        # Normalize known text columns
        elif key in TEXT_COLUMNS:
            original = cleaned[column]

            changed = sum(
                isinstance(value, str)
                and value != normalize_text(value, key)
                for value in original
            )

            cleaned[column] = original.map(
                lambda value: normalize_text(value, key)
            )

            log["text_values_changed"][column] = changed

    return cleaned, log


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    csv_files = sorted(INPUT_DIR.glob("*.csv"))

    if not csv_files:
        raise FileNotFoundError(
            "No CSV files found in data/advanced_cleaned"
        )

    results = []

    for file_path in csv_files:
        # Reading as strings preserves IDs with leading zeros
        df = pd.read_csv(file_path, dtype="string")

        standardized, log = standardize_dataframe(df)

        output_path = OUTPUT_DIR / (
            file_path.stem + "_standardized.csv"
        )

        standardized.to_csv(output_path, index=False)

        results.append({
            "input_file": file_path.name,
            "output_file": str(
                output_path.relative_to(BASE_DIR)
            ),
            **log
        })

        print(f"Standardized: {file_path.name}")

    report = {
        "project": "CadetX Automated Data Cleaning",
        "module": "Data Type Standardization",
        "generated_at_utc": datetime.now(
            timezone.utc
        ).isoformat(),
        "total_files": len(results),
        "files": results
    }

    log_path = REPORTS_DIR / "transformation_log.json"

    with open(log_path, "w", encoding="utf-8") as file:
        json.dump(report, file, indent=4)

    print("\nDay 23: Data Type Standardization Completed!")
    print("Files processed:", len(results))
    print("Output directory:", OUTPUT_DIR)
    print("Transformation log:", log_path)


if __name__ == "__main__":
    main()
