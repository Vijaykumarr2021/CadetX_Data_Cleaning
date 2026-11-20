
import argparse
import csv
import json
import re
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent
INPUT_DIR = BASE_DIR / "data" / "deduplicated"
OUTPUT_DIR = BASE_DIR / "data" / "outlier_review"
REPORTS_DIR = BASE_DIR / "reports"

# Only these numeric fields are analyzed.
# Identifiers are intentionally excluded.
TARGET_COLUMNS = {
    "age",
    "salary",
    "price",
    "amount",
    "quantity",
    "sales",
    "revenue",
    "monthlycharges",
    "totalcharges",
}

MIN_OBSERVATIONS = 5
Z_THRESHOLD = 3.0


def normalize_name(name):
    return re.sub(
        r"[\s_-]+", "", str(name)
    ).lower()


def analyze_outliers(df, mode="flag"):
    if mode not in {"flag", "cap"}:
        raise ValueError(
            "Mode must be 'flag' or 'cap'"
        )

    original = df.reset_index(drop=True)
    result = original.copy(deep=True)

    audit = []
    warnings = []
    analyzed_columns = []
    capped_count = 0

    for column in original.columns:
        if normalize_name(column) not in TARGET_COLUMNS:
            continue

        source = original[column]

        # Convert known numeric columns for analysis.
        numeric = pd.to_numeric(
            source, errors="coerce"
        )

        # Do not analyze a column with invalid
        # non-missing numeric values.
        invalid_mask = (
            source.notna() & numeric.isna()
        )

        if invalid_mask.any():
            warnings.append({
                "column": column,
                "reason": "Invalid numeric values",
                "count": int(invalid_mask.sum())
            })
            continue

        valid = numeric.dropna()

        if len(valid) < MIN_OBSERVATIONS:
            warnings.append({
                "column": column,
                "reason": "Insufficient observations",
                "valid_count": len(valid)
            })
            continue

        analyzed_columns.append(column)

        # IQR method
        q1 = float(valid.quantile(0.25))
        q3 = float(valid.quantile(0.75))

        iqr = q3 - q1

        lower = (
            q1 - 1.5 * iqr
            if iqr > 0 else None
        )

        upper = (
            q3 + 1.5 * iqr
            if iqr > 0 else None
        )

        # Z-score method
        mean = float(valid.mean())
        std = float(valid.std(ddof=0))

        if mode == "cap":
            result[column] = result[column].astype(
                "object"
            )

        for index, value in numeric.items():
            if pd.isna(value):
                continue

            value = float(value)

            iqr_hit = (
                lower is not None
                and (value < lower or value > upper)
            )

            z_score = (
                abs(value - mean) / std
                if std > 0 else 0.0
            )

            z_hit = z_score > Z_THRESHOLD

            if not iqr_hit and not z_hit:
                continue

            detectors = []

            if iqr_hit:
                detectors.append("IQR")

            if z_hit:
                detectors.append("Z-score")

            output_value = value
            action = "flagged_for_review"

            # Optional treatment: cap values that
            # fall outside the IQR boundaries.
            if mode == "cap" and iqr_hit:
                output_value = max(
                    lower, min(value, upper)
                )
                output_value = round(
                    output_value, 6
                )

                result.at[index, column] = (
                    output_value
                )

                action = "capped_to_iqr_bound"
                capped_count += 1

            audit.append({
                "source_row": int(index) + 2,
                "column": column,
                "original_value": value,
                "iqr_lower": lower,
                "iqr_upper": upper,
                "z_score": round(z_score, 4),
                "detected_by": ", ".join(detectors),
                "action": action,
                "output_value": output_value
            })

    summary = {
        "input_rows": len(original),
        "output_rows": len(result),
        "mode": mode,
        "columns_analyzed": analyzed_columns,
        "outliers_flagged": len(audit),
        "values_capped": capped_count,
        "warnings": warnings
    }

    return result, summary, audit


def main():
    parser = argparse.ArgumentParser(
        description="CadetX Day 26 Outlier Detector"
    )

    parser.add_argument(
        "--mode",
        choices=["flag", "cap"],
        default="flag"
    )

    args = parser.parse_args()

    csv_files = sorted(
        INPUT_DIR.glob("*.csv")
    )

    if not csv_files:
        raise FileNotFoundError(
            "No CSV files found in data/deduplicated"
        )

    OUTPUT_DIR.mkdir(
        parents=True, exist_ok=True
    )
    REPORTS_DIR.mkdir(
        parents=True, exist_ok=True
    )

    summaries = []
    audit_records = []

    for file_path in csv_files:
        # Preserve IDs and string formatting
        df = pd.read_csv(
            file_path, dtype="string"
        )

        result, summary, events = analyze_outliers(
            df, mode=args.mode
        )

        output_path = OUTPUT_DIR / (
            file_path.stem + "_outlier_checked.csv"
        )

        result.to_csv(
            output_path, index=False
        )

        summaries.append({
            "input_file": file_path.name,
            "output_file": str(
                output_path.relative_to(BASE_DIR)
            ),
            **summary
        })

        for event in events:
            audit_records.append({
                "file_name": file_path.name,
                **event
            })

        print(
            f"{file_path.name}: "
            f"{summary['outliers_flagged']} outliers; "
            f"{summary['values_capped']} capped"
        )

    report = {
        "project": "CadetX Data Cleaning",
        "module": "Outlier Detection",
        "generated_at_utc": datetime.now(
            timezone.utc
        ).isoformat(),
        "mode": args.mode,
        "total_files": len(summaries),
        "files": summaries
    }

    report_path = (
        REPORTS_DIR / "outlier_report.json"
    )

    with report_path.open(
        "w", encoding="utf-8"
    ) as file:
        json.dump(report, file, indent=4)

    audit_path = (
        REPORTS_DIR / "outlier_audit.csv"
    )

    with audit_path.open(
        "w",
        newline="",
        encoding="utf-8"
    ) as file:
        writer = csv.DictWriter(
            file,
            fieldnames=[
                "file_name",
                "source_row",
                "column",
                "original_value",
                "iqr_lower",
                "iqr_upper",
                "z_score",
                "detected_by",
                "action",
                "output_value"
            ]
        )

        writer.writeheader()
        writer.writerows(audit_records)

    print("\nDay 26: Outlier Detection Completed!")
    print("Files processed:", len(summaries))
    print("Mode:", args.mode)
    print("Output directory:", OUTPUT_DIR)
    print("JSON report:", report_path)
    print("CSV audit:", audit_path)


if __name__ == "__main__":
    main()
