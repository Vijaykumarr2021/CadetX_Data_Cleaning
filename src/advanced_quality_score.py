
import json
from pathlib import Path

import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent
INPUT_DIR = BASE_DIR / "data" / "processed"
REPORTS_DIR = BASE_DIR / "reports"


def calculate_quality_score(df):
    rows, columns = df.shape
    total_cells = rows * columns

    # Completeness: percentage of non-missing cells
    missing_cells = int(df.isna().sum().sum())

    completeness = (
        (1 - missing_cells / total_cells) * 100
        if total_cells else 100.0
    )

    # Uniqueness: percentage of non-duplicate rows
    duplicate_rows = int(df.duplicated().sum())

    uniqueness = (
        (1 - duplicate_rows / rows) * 100
        if rows else 100.0
    )

    # Validity: apply basic checks when columns exist
    invalid_rows = pd.Series(False, index=df.index)

    if "Age" in df.columns:
        age = pd.to_numeric(df["Age"], errors="coerce")
        invalid_rows |= age.notna() & ~age.between(18, 60)

    if "Salary" in df.columns:
        salary = pd.to_numeric(df["Salary"], errors="coerce")
        invalid_rows |= salary.notna() & (salary < 0)

    invalid_count = int(invalid_rows.sum())

    validity = (
        (1 - invalid_count / rows) * 100
        if rows else 100.0
    )

    # Weighted overall score
    overall_score = (
        completeness * 0.40
        + uniqueness * 0.30
        + validity * 0.30
    )

    return {
        "total_rows": rows,
        "total_columns": columns,
        "missing_cells": missing_cells,
        "duplicate_rows": duplicate_rows,
        "invalid_rows": invalid_count,
        "completeness_score": round(completeness, 2),
        "uniqueness_score": round(uniqueness, 2),
        "validity_score": round(validity, 2),
        "overall_quality_score": round(overall_score, 2)
    }


def main():
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    csv_files = sorted(INPUT_DIR.glob("*.csv"))

    if not csv_files:
        print("No CSV files found in data/processed")
        return

    results = []

    for file_path in csv_files:
        df = pd.read_csv(file_path)
        score = calculate_quality_score(df)

        results.append({
            "file_name": file_path.name,
            **score
        })

        print(
            f"{file_path.name}: "
            f"{score['overall_quality_score']:.2f}/100"
        )

    output_path = REPORTS_DIR / "advanced_quality_report.json"

    with open(output_path, "w", encoding="utf-8") as file:
        json.dump(results, file, indent=4)

    print("\nDay 18: Quality scoring completed!")
    print("Files analyzed:", len(results))
    print("Report saved to:", output_path)


if __name__ == "__main__":
    main()
