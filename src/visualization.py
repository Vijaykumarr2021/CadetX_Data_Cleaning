
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

original = pd.read_csv(BASE_DIR / "data/customer.csv")
cleaned = pd.read_csv(BASE_DIR / "data/cleaned_customer.csv")

reports_dir = BASE_DIR / "reports"
reports_dir.mkdir(parents=True, exist_ok=True)

# Chart 1: Missing Values Comparison

missing_before = original.isnull().sum().sum()
missing_after = cleaned.isnull().sum().sum()

plt.figure(figsize=(8, 5))

plt.bar(
    ["Before Cleaning", "After Cleaning"],
    [missing_before, missing_after],
    color=["tomato", "seagreen"]
)

plt.title("CadetX - Missing Values Comparison")
plt.ylabel("Number of Missing Values")
plt.ylim(0, max(missing_before, missing_after) + 1)

for i, value in enumerate([missing_before, missing_after]):
    plt.text(i, value + 0.05, str(value), ha="center")

plt.savefig(
    reports_dir / "missing_values_chart.png",
    dpi=150,
    bbox_inches="tight"
)

plt.close()
print("Missing values chart saved successfully!")


# Chart 2: Duplicate Records Comparison

duplicates_before = original.duplicated().sum()
duplicates_after = cleaned.duplicated().sum()

plt.figure(figsize=(8, 5))

plt.bar(
    ["Before Cleaning", "After Cleaning"],
    [duplicates_before, duplicates_after],
    color=["orange", "seagreen"]
)

plt.title("CadetX - Duplicate Records Comparison")
plt.ylabel("Number of Duplicate Records")
plt.ylim(0, max(duplicates_before, duplicates_after) + 1)

for i, value in enumerate([duplicates_before, duplicates_after]):
    plt.text(i, value + 0.05, str(value), ha="center")

plt.savefig(
    reports_dir / "duplicate_records_chart.png",
    dpi=150,
    bbox_inches="tight"
)

plt.close()
print("Duplicate records chart saved successfully!")

print("\nBoth CadetX charts generated successfully!")
