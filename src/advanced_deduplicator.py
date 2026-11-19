
import csv
import json
import re
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent

INPUT_DIR = BASE_DIR / "data" / "imputed"
OUTPUT_DIR = BASE_DIR / "data" / "deduplicated"
REPORTS_DIR = BASE_DIR / "reports"

PREFERRED_KEYS = (
    "orderid",
    "transactionid",
    "employeeid",
    "recordid",
    "customerid",
)


def choose_key_columns(df, key_columns=None):
    # Explicitly selected columns take priority.
    if key_columns is not None:
        missing = [
            key for key in key_columns
            if key not in df.columns
        ]

        if missing:
            raise ValueError(
                f"Key columns not found: {missing}"
            )

        return list(key_columns)

    # Otherwise look for a known ID column.
    normalized_names = {
        re.sub(
            r"[\s_-]+", "", str(column)
        ).lower(): column
        for column in df.columns
    }

    for candidate in PREFERRED_KEYS:
        if candidate in normalized_names:
            return [normalized_names[candidate]]

    return []


def deduplicate_dataframe(df, key_columns=None):
    original = df.reset_index(drop=True).copy()

    keys = choose_key_columns(
        original, key_columns
    )

    # Step 1: Find exact duplicate rows.
    # Retain the first occurrence.
    exact_duplicate_mask = original.duplicated(
        keep="first"
    )

    # Row numbers correspond to CSV lines
    # (including the header at line 1).
    removed_rows = [
        int(index) + 2
        for index in original.index[exact_duplicate_mask]
    ]

    audit_entries = [
        {
            "source_row": row,
            "issue": "exact_duplicate",
            "action": "removed_keep_first",
            "key_columns": ",".join(keys),
        }
        for row in removed_rows
    ]

    remaining = original.loc[
        ~exact_duplicate_mask
    ].copy()

    # Step 2: Find repeated non-empty IDs.
    # Keep conflicting rows for manual review.
    collision_groups = 0
    collision_rows = 0

    if keys:
        valid = remaining[keys].notna().all(
            axis=1
        )

        for key in keys:
            valid &= remaining[key].map(
                lambda value: bool(value.strip())
                if isinstance(value, str)
                else True
            )

        grouped = remaining.loc[valid].groupby(
            keys,
            sort=False,
            dropna=False
        )

        for _, group in grouped:
            if len(group) <= 1:
                continue

            collision_groups += 1
            collision_rows += len(group)

            for index in group.index:
                audit_entries.append({
                    "source_row": int(index) + 2,
                    "issue": "same_key_different_values",
                    "action": "retained_for_review",
                    "key_columns": ",".join(keys),
                })

    summary = {
        "original_rows": len(original),
        "output_rows": len(remaining),
        "exact_duplicates_removed": len(
            removed_rows
        ),
        "key_columns_used": keys,
        "key_collision_groups_retained": (
            collision_groups
        ),
        "key_collision_rows_retained": (
            collision_rows
        ),
    }

    return (
        remaining.reset_index(drop=True),
        summary,
        audit_entries
    )


def main():
    csv_files = sorted(INPUT_DIR.glob("*.csv"))

    if not csv_files:
        raise FileNotFoundError(
            "No CSV files found in data/imputed"
        )

    OUTPUT_DIR.mkdir(
        parents=True, exist_ok=True
    )
    REPORTS_DIR.mkdir(
        parents=True, exist_ok=True
    )

    summaries = []
    audit = []

    for file_path in csv_files:
        # Read as strings to preserve IDs
        # with leading zeros.
        df = pd.read_csv(
            file_path,
            dtype="string"
        )

        cleaned, summary, events = (
            deduplicate_dataframe(df)
        )

        output_path = OUTPUT_DIR / (
            file_path.stem + "_deduplicated.csv"
        )

        cleaned.to_csv(
            output_path,
            index=False
        )

        summaries.append({
            "input_file": file_path.name,
            "output_file": str(
                output_path.relative_to(BASE_DIR)
            ),
            **summary
        })

        audit.extend(
            {
                "file_name": file_path.name,
                **event
            }
            for event in events
        )

        print(
            f"{file_path.name}: "
            f"{summary['original_rows']} -> "
            f"{summary['output_rows']} rows; "
            f"{summary['key_collision_groups_retained']} "
            f"key groups for review"
        )

    # Save JSON summary
    report_path = (
        REPORTS_DIR / "deduplication_report.json"
    )

    report = {
        "generated_at_utc": datetime.now(
            timezone.utc
        ).isoformat(),
        "policy": (
            "Remove exact duplicates; "
            "retain differing key collisions"
        ),
        "total_files": len(summaries),
        "files": summaries
    }

    with report_path.open(
        "w", encoding="utf-8"
    ) as file:
        json.dump(report, file, indent=4)

    # Save CSV audit
    audit_path = (
        REPORTS_DIR / "duplicate_audit.csv"
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
                "issue",
                "action",
                "key_columns"
            ]
        )

        writer.writeheader()
        writer.writerows(audit)

    print(
        "\nDay 25: Duplicate Detection Completed!"
    )
    print("Files processed:", len(summaries))
    print("Deduplicated data:", OUTPUT_DIR)
    print("JSON report:", report_path)
    print("CSV audit:", audit_path)


if __name__ == "__main__":
    main()
