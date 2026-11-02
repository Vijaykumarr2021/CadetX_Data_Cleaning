
import json
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

from metadata_extractor import extract_metadata
from missing_value_analysis import analyze_missing_values
from advanced_quality_score import calculate_quality_score

BASE_DIR = Path(__file__).resolve().parent.parent
INPUT_DIR = BASE_DIR / "data" / "processed"
REPORTS_DIR = BASE_DIR / "reports"


def generate_unified_report():
    csv_files = sorted(INPUT_DIR.glob("*.csv"))

    if not csv_files:
        raise FileNotFoundError(
            "No CSV files found in data/processed"
        )

    datasets = []

    for file_path in csv_files:
        df = pd.read_csv(file_path)

        metadata = extract_metadata(file_path)
        missing_analysis = analyze_missing_values(file_path)
        quality = calculate_quality_score(df)

        datasets.append({
            "dataset_name": file_path.name,
            "metadata": metadata,
            "missing_value_analysis": missing_analysis,
            "quality_scores": quality
        })

        print(f"Profiled: {file_path.name}")

    return {
        "project": "CadetX Automated Data Cleaning and Validation",
        "module": "Advanced Data Profiling and Metadata Intelligence",
        "generated_at_utc": datetime.now(
            timezone.utc
        ).isoformat(),
        "total_datasets": len(datasets),
        "datasets": datasets
    }


def main():
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    report = generate_unified_report()

    output_path = REPORTS_DIR / "profiling_report.json"

    with open(output_path, "w", encoding="utf-8") as file:
        json.dump(report, file, indent=4)

    print("\nDay 19: Unified profiling completed!")
    print("Total datasets:", report["total_datasets"])
    print("Report saved to:", output_path)


if __name__ == "__main__":
    main()
