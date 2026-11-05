
import json
from datetime import datetime, timezone
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
REPORTS_DIR = BASE_DIR / "reports"

INPUT_FILE = REPORTS_DIR / "profiling_report.json"
JSON_OUTPUT = REPORTS_DIR / "profiling_insights.json"
TEXT_OUTPUT = REPORTS_DIR / "profiling_summary.txt"


def generate_insights(profile):
    if not isinstance(profile.get("datasets"), list):
        raise ValueError("Invalid profiling report: datasets missing")

    results = []
    scores = []

    for dataset in profile["datasets"]:
        name = dataset["dataset_name"]
        quality = dataset["quality_scores"]
        missing = dataset.get("missing_value_analysis", {})

        score = float(quality["overall_quality_score"])
        missing_count = int(quality.get("missing_cells", 0))
        duplicate_count = int(quality.get("duplicate_rows", 0))
        invalid_count = int(quality.get("invalid_rows", 0))

        scores.append(score)

        issues = []
        recommendations = []

        if missing_count > 0:
            issues.append(
                f"{missing_count} missing cells detected"
            )
            recommendations.append(
                "Inspect missing values before choosing "
                "a suitable imputation strategy."
            )

        if duplicate_count > 0:
            issues.append(
                f"{duplicate_count} duplicate rows detected"
            )
            recommendations.append(
                "Review duplicate records before removal."
            )

        if invalid_count > 0:
            issues.append(
                f"{invalid_count} rows failed validation checks"
            )
            recommendations.append(
                "Review invalid values using existing "
                "validation rules."
            )

        if score >= 95:
            status = "Excellent"
        elif score >= 80:
            status = "Good"
        else:
            status = "Needs Improvement"

        if not issues:
            recommendations.append(
                "Maintain data quality monitoring. "
                "No issues found by current checks."
            )

        results.append({
            "dataset_name": name,
            "quality_score": score,
            "quality_status": status,
            "issues": issues,
            "recommendations": recommendations
        })

    average_score = (
        round(sum(scores) / len(scores), 2)
        if scores else None
    )

    return {
        "project": "CadetX Data Cleaning and Validation",
        "generated_at_utc": datetime.now(
            timezone.utc
        ).isoformat(),
        "total_datasets": len(results),
        "average_quality_score": average_score,
        "assessment_scope": (
            "Results reflect the existing completeness, "
            "uniqueness and limited validity checks."
        ),
        "datasets": results
    }


def create_text_summary(report):
    lines = [
        "CADETX AUTOMATED DATA PROFILING SUMMARY",
        "=" * 45,
        f"Total Datasets: {report['total_datasets']}",
        f"Average Quality Score: "
        f"{report['average_quality_score']}",
        "",
    ]

    for dataset in report["datasets"]:
        lines.append(
            f"Dataset: {dataset['dataset_name']}"
        )
        lines.append(
            f"Quality Score: {dataset['quality_score']}/100"
        )
        lines.append(
            f"Status: {dataset['quality_status']}"
        )

        if dataset["issues"]:
            lines.append("Issues:")
            for issue in dataset["issues"]:
                lines.append(f"  - {issue}")
        else:
            lines.append("Issues: None detected")

        lines.append("Recommendations:")

        for recommendation in dataset["recommendations"]:
            lines.append(f"  - {recommendation}")

        lines.append("-" * 45)

    lines.append(report["assessment_scope"])

    return "\n".join(lines) + "\n"


def main():
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    if not INPUT_FILE.exists():
        raise FileNotFoundError(
            "Run the Day 19 unified profiler first."
        )

    with open(INPUT_FILE, "r", encoding="utf-8") as file:
        profile = json.load(file)

    insights = generate_insights(profile)

    with open(JSON_OUTPUT, "w", encoding="utf-8") as file:
        json.dump(insights, file, indent=4)

    with open(TEXT_OUTPUT, "w", encoding="utf-8") as file:
        file.write(create_text_summary(insights))

    print("Day 21: Automated Profiling Insights Completed!")
    print("Datasets analyzed:", insights["total_datasets"])
    print("Average quality score:",
          insights["average_quality_score"])
    print("JSON report:", JSON_OUTPUT)
    print("Text report:", TEXT_OUTPUT)


if __name__ == "__main__":
    main()
