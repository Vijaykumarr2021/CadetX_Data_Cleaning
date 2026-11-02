
import json
from pathlib import Path

import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent
INPUT_DIR = BASE_DIR / "data" / "processed"
REPORTS_DIR = BASE_DIR / "reports"


def analyze_missing_values(file_path):
    df = pd.read_csv(file_path)
    total_rows = len(df)

    columns = []

    for column in df.columns:
        missing_count = int(df[column].isna().sum())

        missing_percentage = (
            round(missing_count / total_rows * 100, 2)
            if total_rows > 0 else 0.0
        )

        if missing_percentage == 0:
            severity = "None"
        elif missing_percentage <= 5:
            severity = "Low"
        elif missing_percentage <= 20:
            severity = "Medium"
        else:
            severity = "High"

        columns.append({
            "column_name": column,
            "missing_count": missing_count,
            "missing_percentage": missing_percentage,
            "severity": severity
        })

    return {
        "file_name": file_path.name,
        "total_rows": total_rows,
        "total_columns": len(df.columns),
        "total_missing_values": int(df.isna().sum().sum()),
        "columns": columns
    }


def main():
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    csv_files = sorted(INPUT_DIR.glob("*.csv"))

    if not csv_files:
        print("No CSV files found in data/processed")
        return

    results = [
        analyze_missing_values(file_path)
        for file_path in csv_files
    ]

    output_path = REPORTS_DIR / "missing_value_report.json"

    with open(output_path, "w", encoding="utf-8") as file:
        json.dump(results, file, indent=4)

    print("Day 17: Missing Value Analysis Completed!")
    print("Files analyzed:", len(results))
    print("Report saved to:", output_path)


if __name__ == "__main__":
    main()
