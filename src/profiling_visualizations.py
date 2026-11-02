
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent
INPUT_DIR = BASE_DIR / "data" / "processed"
REPORTS_DIR = BASE_DIR / "reports"
OUTPUT_DIR = REPORTS_DIR / "visualizations"


def load_quality_report():
    path = REPORTS_DIR / "advanced_quality_report.json"

    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


def plot_quality_scores(results):
    names = [
        item["file_name"].replace(".csv", "")
        for item in results
    ]

    scores = [
        item["overall_quality_score"]
        for item in results
    ]

    fig, ax = plt.subplots(figsize=(10, 5))

    bars = ax.bar(names, scores)

    ax.set_title("Data Quality Scores")
    ax.set_ylabel("Quality Score")
    ax.set_ylim(0, 110)

    for bar, score in zip(bars, scores):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 1,
            f"{score:.2f}",
            ha="center"
        )

    plt.xticks(rotation=15)
    fig.tight_layout()

    fig.savefig(
        OUTPUT_DIR / "quality_scores.png",
        dpi=150
    )
    plt.close(fig)


def plot_missing_values():
    names = []
    missing_counts = []

    for file_path in sorted(INPUT_DIR.glob("*.csv")):
        df = pd.read_csv(file_path)

        names.append(file_path.stem)
        missing_counts.append(
            int(df.isna().sum().sum())
        )

    fig, ax = plt.subplots(figsize=(10, 5))

    ax.bar(names, missing_counts)

    ax.set_title("Missing Values by Dataset")
    ax.set_ylabel("Missing Cells")

    plt.xticks(rotation=15)
    fig.tight_layout()

    fig.savefig(
        OUTPUT_DIR / "missing_values.png",
        dpi=150
    )
    plt.close(fig)


def plot_data_types():
    type_counts = {}

    for file_path in sorted(INPUT_DIR.glob("*.csv")):
        df = pd.read_csv(file_path)

        for dtype in df.dtypes:
            dtype_name = str(dtype)

            type_counts[dtype_name] = (
                type_counts.get(dtype_name, 0) + 1
            )

    if not type_counts:
        raise ValueError("No columns found for visualization")

    fig, ax = plt.subplots(figsize=(8, 5))

    ax.bar(
        list(type_counts.keys()),
        list(type_counts.values())
    )

    ax.set_title("Column Data Type Distribution")
    ax.set_xlabel("Pandas Data Type")
    ax.set_ylabel("Number of Columns")

    plt.xticks(rotation=20)
    fig.tight_layout()

    fig.savefig(
        OUTPUT_DIR / "data_types.png",
        dpi=150
    )
    plt.close(fig)


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    csv_files = list(INPUT_DIR.glob("*.csv"))

    if not csv_files:
        raise FileNotFoundError(
            "No CSV files found in data/processed"
        )

    quality_results = load_quality_report()

    plot_quality_scores(quality_results)
    plot_missing_values()
    plot_data_types()

    print("Day 20: Profiling visualizations completed!")
    print("Charts generated: 3")
    print("Output directory:", OUTPUT_DIR)


if __name__ == "__main__":
    main()
