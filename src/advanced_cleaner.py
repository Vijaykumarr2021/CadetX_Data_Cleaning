
import json
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent
INPUT_DIR = BASE_DIR / "data"
OUTPUT_DIR = INPUT_DIR / "advanced_cleaned"
REPORTS_DIR = BASE_DIR / "reports"

# Only these columns are automatically imputed.
NUMERIC_COLUMNS = {
    "age", "salary", "price", "amount", "quantity"
}

CATEGORICAL_COLUMNS = {
    "department", "city", "category"
}


def clean_dataframe(df):
    cleaned = df.copy()

    original_rows = len(cleaned)
    whitespace_changes = 0
    filled_values = {}

    # Step 1: Remove leading/trailing whitespace
    for column in cleaned.select_dtypes(
        include=["object", "string"]
    ).columns:

        whitespace_changes += sum(
            value != value.strip()
            for value in cleaned[column]
            if isinstance(value, str)
        )

        cleaned[column] = cleaned[column].map(
            lambda value: value.strip()
            if isinstance(value, str) else value
        )

        # Treat empty strings as missing values
        cleaned[column] = cleaned[column].replace(
            "", pd.NA
        )

    missing_before = int(
        cleaned.isna().sum().sum()
    )

    # Step 2: Remove exact duplicate rows
    duplicate_count = int(
        cleaned.duplicated().sum()
    )

    cleaned = cleaned.drop_duplicates().reset_index(
        drop=True
    )

    # Step 3: Fill selected numeric columns
    for column in cleaned.columns:
        normalized_name = column.strip().lower()

        if normalized_name not in NUMERIC_COLUMNS:
            continue

        if not pd.api.types.is_numeric_dtype(
            cleaned[column]
        ):
            continue

        missing = int(cleaned[column].isna().sum())

        if missing == 0:
            continue

        median = cleaned[column].median()

        if pd.notna(median):
            cleaned[column] = cleaned[column].fillna(
                median
            )
            filled_values[column] = {
                "method": "median",
                "count": missing,
                "value": float(median)
            }

    # Step 4: Fill selected categorical columns
    for column in cleaned.columns:
        if column.strip().lower() not in CATEGORICAL_COLUMNS:
            continue

        missing = int(cleaned[column].isna().sum())

        if missing == 0:
            continue

        modes = cleaned[column].mode(dropna=True)

        if not modes.empty:
            mode = modes.iloc[0]
            cleaned[column] = cleaned[column].fillna(
                mode
            )
            filled_values[column] = {
                "method": "mode",
                "count": missing,
                "value": str(mode)
            }

    missing_after = int(
        cleaned.isna().sum().sum()
    )

    log = {
        "original_rows": original_rows,
        "cleaned_rows": len(cleaned),
        "duplicates_removed": duplicate_count,
        "whitespace_values_trimmed": whitespace_changes,
        "missing_before": missing_before,
        "missing_after": missing_after,
        "filled_values": filled_values
    }

    return cleaned, log


def main():
    OUTPUT_DIR.mkdir(
        parents=True, exist_ok=True
    )
    REPORTS_DIR.mkdir(
        parents=True, exist_ok=True
    )

    csv_files = sorted(INPUT_DIR.glob("*.csv"))

    if not csv_files:
        print("No raw CSV files found in data/")
        return

    results = []

    for file_path in csv_files:
        df = pd.read_csv(file_path)

        cleaned, log = clean_dataframe(df)

        output_path = OUTPUT_DIR / (
            file_path.stem + "_cleaned.csv"
        )

        cleaned.to_csv(
            output_path, index=False
        )

        results.append({
            "input_file": file_path.name,
            "output_file": str(
                output_path.relative_to(BASE_DIR)
            ),
            **log
        })

        print(
            f"{file_path.name}: "
            f"{log['original_rows']} -> "
            f"{log['cleaned_rows']} rows"
        )

    report = {
        "project": "CadetX Data Cleaning",
        "generated_at_utc": datetime.now(
            timezone.utc
        ).isoformat(),
        "total_files": len(results),
        "files": results
    }

    log_path = REPORTS_DIR / "cleaning_log.json"

    with open(
        log_path, "w", encoding="utf-8"
    ) as file:
        json.dump(report, file, indent=4)

    print("\nDay 22: Advanced Cleaning Completed!")
    print("Files processed:", len(results))
    print("Cleaned data:", OUTPUT_DIR)
    print("Cleaning log:", log_path)


if __name__ == "__main__":
    main()
