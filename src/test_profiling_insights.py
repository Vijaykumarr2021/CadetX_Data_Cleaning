
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from profiling_insights import generate_insights


def test_clean_dataset():
    profile = {
        "datasets": [
            {
                "dataset_name": "clean.csv",
                "quality_scores": {
                    "overall_quality_score": 100,
                    "missing_cells": 0,
                    "duplicate_rows": 0,
                    "invalid_rows": 0
                }
            }
        ]
    }

    result = generate_insights(profile)

    assert result["total_datasets"] == 1
    assert result["average_quality_score"] == 100
    assert result["datasets"][0]["issues"] == []
    assert result["datasets"][0]["quality_status"] == "Excellent"


def test_problem_dataset():
    profile = {
        "datasets": [
            {
                "dataset_name": "problem.csv",
                "quality_scores": {
                    "overall_quality_score": 75,
                    "missing_cells": 4,
                    "duplicate_rows": 2,
                    "invalid_rows": 1
                }
            }
        ]
    }

    result = generate_insights(profile)
    dataset = result["datasets"][0]

    assert dataset["quality_status"] == "Needs Improvement"
    assert len(dataset["issues"]) == 3
    assert len(dataset["recommendations"]) == 3
