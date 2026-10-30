
import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

INPUT_DIR = BASE_DIR / "data" / "raw"
OUTPUT_DIR = BASE_DIR / "data" / "processed"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

csv_files = sorted(INPUT_DIR.glob("*.csv"))

if not csv_files:
    print("No CSV files found in data/raw")
else:
    print("Starting CadetX Batch Cleaning...\n")

    for file in csv_files:
        print(f"Processing: {file.name}")

        df = pd.read_csv(file)

        original_rows = len(df)

        # Remove duplicate rows
        df = df.drop_duplicates().copy()

        # Fill missing numeric values with median
        for column in df.select_dtypes(include="number").columns:
            if df[column].isna().any():
                median_value = df[column].median()
                if pd.notna(median_value):
                    df[column] = df[column].fillna(median_value)

        # Fill missing text values
        for column in df.select_dtypes(
            include=["object", "string"]
        ).columns:
            df[column] = df[column].fillna("Unknown")

        output_file = OUTPUT_DIR / f"cleaned_{file.name}"

        df.to_csv(output_file, index=False)

        print("Original rows:", original_rows)
        print("Cleaned rows:", len(df))
        print("Missing values remaining:",
              int(df.isna().sum().sum()))
        print("Saved to:", output_file)
        print("-" * 40)

    print("\nBatch Cleaning Completed Successfully!")
