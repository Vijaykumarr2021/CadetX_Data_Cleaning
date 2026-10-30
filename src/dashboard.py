
import pandas as pd
from pathlib import Path
from datetime import datetime

# Project paths
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
REPORTS_DIR = BASE_DIR / "reports"

REPORTS_DIR.mkdir(parents=True, exist_ok=True)

# Load datasets
original = pd.read_csv(DATA_DIR / "customer.csv")
cleaned = pd.read_csv(DATA_DIR / "cleaned_customer.csv")

# Calculate metrics
original_records = len(original)
cleaned_records = len(cleaned)

missing_before = int(original.isnull().sum().sum())
missing_after = int(cleaned.isnull().sum().sum())

duplicates_removed = int(original.duplicated().sum())

total_cells = cleaned.size

completeness = (
    (1 - missing_after / total_cells) * 100
    if total_cells else 0
)

# Validate cleaned data
age = pd.to_numeric(cleaned["Age"], errors="coerce")
salary = pd.to_numeric(cleaned["Salary"], errors="coerce")

valid = (
    missing_after == 0
    and cleaned["EmployeeID"].duplicated().sum() == 0
    and age.between(18, 60).all()
    and (salary > 0).all()
)

status = "PASSED" if valid else "FAILED"
status_color = "#16a34a" if valid else "#dc2626"

# Generate dashboard HTML
html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport"
          content="width=device-width, initial-scale=1">
    <title>CadetX Data Quality Dashboard</title>

    <style>
        body {{
            font-family: Arial, sans-serif;
            background: #f1f5f9;
            margin: 0;
            padding: 30px;
            color: #0f172a;
        }}

        .container {{
            max-width: 1100px;
            margin: auto;
        }}

        h1 {{
            color: #1e3a8a;
        }}

        .subtitle {{
            color: #64748b;
        }}

        .cards {{
            display: grid;
            grid-template-columns:
                repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-top: 25px;
        }}

        .card {{
            background: white;
            padding: 25px;
            border-radius: 12px;
            box-shadow: 0 2px 8px #00000012;
        }}

        .card h2 {{
            font-size: 32px;
            margin: 10px 0;
            color: #2563eb;
        }}

        .card p {{
            color: #64748b;
            margin: 0;
        }}

        .status {{
            color: {status_color};
            font-weight: bold;
        }}

        .charts {{
            display: grid;
            grid-template-columns:
                repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-top: 25px;
        }}

        .chart {{
            background: white;
            padding: 20px;
            border-radius: 12px;
        }}

        .chart img {{
            width: 100%;
            height: auto;
        }}

        footer {{
            margin-top: 30px;
            color: #64748b;
            text-align: center;
        }}
    </style>
</head>

<body>
<div class="container">

    <h1>CadetX Data Quality Dashboard</h1>

    <p class="subtitle">
        Automated Data Cleaning & Validation System
    </p>

    <p>Generated: {datetime.now().strftime("%d %B %Y, %I:%M %p")}</p>

    <div class="cards">

        <div class="card">
            <p>Original Records</p>
            <h2>{original_records}</h2>
        </div>

        <div class="card">
            <p>Cleaned Records</p>
            <h2>{cleaned_records}</h2>
        </div>

        <div class="card">
            <p>Missing Values Fixed</p>
            <h2>{missing_before - missing_after}</h2>
        </div>

        <div class="card">
            <p>Duplicates Removed</p>
            <h2>{duplicates_removed}</h2>
        </div>

        <div class="card">
            <p>Data Completeness Score</p>
            <h2>{completeness:.2f}%</h2>
        </div>

        <div class="card">
            <p>Validation Status</p>
            <h2 class="status">{status}</h2>
        </div>

    </div>

    <div class="charts">

        <div class="chart">
            <h3>Missing Values Comparison</h3>
            <img src="missing_values_chart.png"
                 alt="Missing values chart">
        </div>

        <div class="chart">
            <h3>Duplicate Records Comparison</h3>
            <img src="duplicate_records_chart.png"
                 alt="Duplicate records chart">
        </div>

    </div>

    <footer>
        CadetX Automated Data Quality Dashboard
    </footer>

</div>
</body>
</html>
"""

# Save dashboard
output_path = REPORTS_DIR / "dashboard.html"

output_path.write_text(html, encoding="utf-8")

print("CadetX Dashboard Generated Successfully!")
print("Validation Status:", status)
print("Data Completeness Score:", f"{completeness:.2f}%")
print("Dashboard saved to:", output_path)
