
import argparse
import csv
import json
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

from advanced_cleaner import clean_dataframe
from data_type_standardizer import standardize_dataframe
from advanced_missing_handler import impute_dataframe
from advanced_deduplicator import deduplicate_dataframe
from outlier_detector import analyze_outliers


BASE_DIR = Path(__file__).resolve().parent.parent

INPUT_DIR = BASE_DIR / "data"
OUTPUT_DIR = BASE_DIR / "data" / "pipeline_output"
REPORTS_DIR = BASE_DIR / "reports"


def process_dataframe(df):
    """
    Run all five cleaning modules in order.
    Do not modify the original DataFrame.
    """

    # Stage 1: Advanced cleaning
    cleaned, cleaning_log = clean_dataframe(
        df.copy(deep=True)
    )

    # Stage 2: Standardize data types
    standardized, standardization_log = (
        standardize_dataframe(cleaned)
    )

    # Stage 3: Handle missing values
    imputed, imputation_log = impute_dataframe(
        standardized
    )

    # Stage 4: Detect and handle duplicates
    deduplicated, deduplication_log, duplicate_audit = (
        deduplicate_dataframe(imputed)
    )

    # Stage 5: Flag outliers (do not cap or delete)
    final_df, outlier_log, outlier_audit = (
        analyze_outliers(deduplicated, mode="flag")
    )

    stage_logs = {
        "cleaning": cleaning_log,
        "standardization": standardization_log,
        "missing_values": imputation_log,
        "deduplication": deduplication_log,
        "outliers": outlier_log
    }

    audit_logs = {
        "duplicates": duplicate_audit,
        "outliers": outlier_audit
    }

    return final_df, stage_logs, audit_logs


def write_audit_csv(path, fieldnames, records):
    with path.open(
        "w", newline="", encoding="utf-8"
    ) as file:
        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames
        )

        writer.writeheader()
        writer.writerows(records)


def run_pipeline(
    input_dir=INPUT_DIR,
    output_dir=OUTPUT_DIR,
    reports_dir=REPORTS_DIR
):
    input_dir = Path(input_dir)
    output_dir = Path(output_dir)
    reports_dir = Path(reports_dir)

    # Read only CSV files directly in input_dir.
    csv_files = sorted(input_dir.glob("*.csv"))

    if not csv_files:
        raise FileNotFoundError(
            f"No CSV files found in {input_dir}"
        )

    output_dir.mkdir(
        parents=True, exist_ok=True
    )
    reports_dir.mkdir(
        parents=True, exist_ok=True
    )

    file_reports = []
    all_duplicate_events = []
    all_outlier_events = []

    for file_path in csv_files:
        print(f"\nProcessing: {file_path.name}")

        # Preserve IDs containing leading zeros.
        df = pd.read_csv(
            file_path,
            dtype="string"
        )

        final_df, logs, audit = (
            process_dataframe(df)
        )

        output_path = output_dir / (
            file_path.stem + "_pipeline_cleaned.csv"
        )

        final_df.to_csv(
            output_path,
            index=False
        )

        file_reports.append({
            "input_file": file_path.name,
            "output_file": str(output_path),
            "input_rows": len(df),
            "output_rows": len(final_df),
            "stages": logs
        })

        for event in audit["duplicates"]:
            all_duplicate_events.append({
                "file_name": file_path.name,
                **event
            })

        for event in audit["outliers"]:
            all_outlier_events.append({
                "file_name": file_path.name,
                **event
            })

        print(
            f"Rows: {len(df)} -> {len(final_df)}"
        )
        print(
            "Outliers flagged:",
            logs["outliers"]["outliers_flagged"]
        )
        print("Saved:", output_path.name)

    report = {
        "project": (
            "CadetX Automated Data Cleaning "
            "and Validation System"
        ),
        "module": "Integrated Cleaning Pipeline",
        "generated_at_utc": datetime.now(
            timezone.utc
        ).isoformat(),
        "total_files": len(file_reports),
        "total_input_rows": sum(
            item["input_rows"]
            for item in file_reports
        ),
        "total_output_rows": sum(
            item["output_rows"]
            for item in file_reports
        ),
        "outlier_policy": "flag_only",
        "files": file_reports
    }

    report_path = (
        reports_dir / "pipeline_run_report.json"
    )

    with report_path.open(
        "w", encoding="utf-8"
    ) as file:
        json.dump(report, file, indent=4)

    duplicate_path = (
        reports_dir / "pipeline_duplicate_audit.csv"
    )

    write_audit_csv(
        duplicate_path,
        [
            "file_name",
            "source_row",
            "issue",
            "action",
            "key_columns"
        ],
        all_duplicate_events
    )

    outlier_path = (
        reports_dir / "pipeline_outlier_audit.csv"
    )

    write_audit_csv(
        outlier_path,
        [
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
        ],
        all_outlier_events
    )

    print("\nDay 27: Pipeline Completed Successfully!")
    print("Files processed:", report["total_files"])
    print("Input rows:", report["total_input_rows"])
    print("Output rows:", report["total_output_rows"])
    print("Output directory:", output_dir)
    print("Pipeline report:", report_path)

    return report


def main():
    parser = argparse.ArgumentParser(
        description="CadetX Integrated Cleaning Pipeline"
    )

    parser.add_argument(
        "--input-dir",
        type=Path,
        default=INPUT_DIR
    )

    parser.add_argument(
        "--output-dir",
        type=Path,
        default=OUTPUT_DIR
    )

    parser.add_argument(
        "--reports-dir",
        type=Path,
        default=REPORTS_DIR
    )

    args = parser.parse_args()

    run_pipeline(
        input_dir=args.input_dir,
        output_dir=args.output_dir,
        reports_dir=args.reports_dir
    )


if __name__ == "__main__":
    main()
