    
import json
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent

INPUT_DIR = BASE_DIR / "data" / "standardized"
OUTPUT_DIR = BASE_DIR / "data" / "imputed"
REPORTS_DIR = BASE_DIR / "reports"


DEFAULT_STRATEGIES = {
    "age": {"method": "median"},
    "salary": {"method": "median"},
    "price": {"method": "median"},
    "amount": {"method": "median"},
    "quantity": {"method": "median"},
    "department": {"method": "mode"},
    "city": {"method": "mode"},
    "category": {"method": "mode"},
    "status": {
        "method": "constant",
        "value": "Unknown"
    }
}


def normalize_column_name(name):
    return (
        name.strip()
        .lower()
        .replace("_", "")
        .replace(" ", "")
    )


def impute_dataframe(df, strategies=None):
    cleaned = df.copy()

    if strategies is None:
        strategies = DEFAULT_STRATEGIES

    # Convert blank strings into missing values
    for column in cleaned.columns:
        if (
            pd.api.types.is_object_dtype(cleaned[column])
            or pd.api.types.is_string_dtype(cleaned[column])
        ):
            cleaned[column] = cleaned[column].map(
                lambda value: pd.NA
                if isinstance(value, str) and not value.strip()
                else value
            )

    missing_before = int(cleaned.isna().sum().sum())

    log = {
        "total_rows": len(cleaned),
        "missing_before": missing_before,
        "missing_after": 0,
        "filled_values": [],
        "warnings": []
    }

    for column in cleaned.columns:
        key = normalize_column_name(column)

        if key not in strategies:
            continue

        missing_count = int(
            cleaned[column].isna().sum()
        )

        if missing_count == 0:
            continue

        rule = strategies[key]
        method = rule["method"]

        # Strategy 1: Median for numeric columns
        if method == "median":
            numeric = pd.to_numeric(
                cleaned[column],
                errors="coerce"
            )

            invalid = (
                cleaned[column].notna()
                & numeric.isna()
            )

            if invalid.any():
                log["warnings"].append({
                    "column": column,
                    "issue": "Invalid numeric values",
                    "count": int(invalid.sum()),
                    "action": "Column preserved for review"
                })
                continue

            if numeric.notna().sum() == 0:
                log["warnings"].append({
                    "column": column,
                    "issue": "No valid values for median"
                })
                continue

            fill_value = float(numeric.median())

            cleaned[column] = numeric.fillna(fill_value)

        # Strategy 2: Mode for categorical columns
        elif method == "mode":
            modes = cleaned[column].mode(dropna=True)

            if modes.empty:
                log["warnings"].append({
                    "column": column,
                    "issue": "No valid values for mode"
                })
                continue

            fill_value = modes.iloc[0]
            cleaned[column] = cleaned[column].fillna(
                fill_value
            )

        # Strategy 3: Constant replacement
        elif method == "constant":
            fill_value = rule["value"]
            cleaned[column] = cleaned[column].fillna(
                fill_value
            )

        else:
            log["warnings"].append({
                "column": column,
                "issue": f"Unknown method: {method}"
            })
            continue

        log["filled_values"].append({
            "column": column,
            "strategy": method,
            "count": missing_count,
            "value": str(fill_value)
        })

    log["missing_after"] = int(
        cleaned.isna().sum().sum()
    )

    return cleaned, log


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    csv_files = sorted(INPUT_DIR.glob("*.csv"))

    if not csv_files:
        raise FileNotFoundError(
            "No CSV files found in data/standardized"
        )

    results = []

    for file_path in csv_files:
        # Preserve identifiers with leading zeros
        df = pd.read_csv(file_path, dtype="string")

        cleaned, log = impute_dataframe(df)

        output_path = OUTPUT_DIR / (
            file_path.stem + "_imputed.csv"
        )

        cleaned.to_csv(output_path, index=False)

        results.append({
            "input_file": file_path.name,
            "output_file": str(
                output_path.relative_to(BASE_DIR)
            ),
            **log
        })

        print(
            f"{file_path.name}: "
            f"Missing {log['missing_before']} -> "
            f"{log['missing_after']}"
        )

    report = {
        "project": "CadetX Data Cleaning",
        "module": "Advanced Missing Value Handling",
        "generated_at_utc": datetime.now(
            timezone.utc
        ).isoformat(),
        "total_files": len(results),
        "files": results
    }

    log_path = REPORTS_DIR / "imputation_log.json"

    with open(log_path, "w", encoding="utf-8") as file:
        json.dump(report, file, indent=4)

    print("\nDay 24: Missing Value Handling Completed!")
    print("Files processed:", len(results))
    print("Output directory:", OUTPUT_DIR)
    print("Imputation log:", log_path)


if __name__ == "__main__":
    main()
