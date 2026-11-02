
import json
import re
from pathlib import Path

import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent
INPUT_DIR = BASE_DIR / "data" / "processed"
REPORTS_DIR = BASE_DIR / "reports"


def detect_column_type(column_name, series):
    name = column_name.lower()

    if "email" in name:
        return "email"

    if "phone" in name or "mobile" in name:
        return "phone"

    if name == "id" or name.endswith("_id"):
        return "identifier"

    if "date" in name or "timestamp" in name:
        return "date"

    if pd.api.types.is_numeric_dtype(series):
        return "numeric"

    return "text"


def extract_metadata(file_path):
    df = pd.read_csv(file_path)

    columns = []

    for column in df.columns:
        series = df[column]

        columns.append({
            "column_name": column,
            "data_type": str(series.dtype),
            "semantic_type": detect_column_type(
                column, series
            ),
            "missing_values": int(series.isna().sum()),
            "unique_values": int(series.nunique(dropna=True)),
            "sample_values": [
                str(value)
                for value in series.dropna().head(3)
            ]
        })

    return {
        "file_name": file_path.name,
        "total_rows": int(len(df)),
        "total_columns": int(len(df.columns)),
        "duplicate_rows": int(df.duplicated().sum()),
        "columns": columns
    }


def main():
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    csv_files = sorted(INPUT_DIR.glob("*.csv"))

    if not csv_files:
        print("No CSV files found in data/processed")
        return

    results = [
        extract_metadata(file_path)
        for file_path in csv_files
    ]

    output_path = REPORTS_DIR / "metadata_report.json"

    with open(output_path, "w", encoding="utf-8") as file:
        json.dump(results, file, indent=4)

    print("Day 16: Metadata extraction completed!")
    print("Files analyzed:", len(results))
    print("Report saved to:", output_path)


if __name__ == "__main__":
    main()
