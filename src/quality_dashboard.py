
import pandas as pd
from pathlib import Path
from datetime import datetime
from html import escape

BASE_DIR = Path(__file__).resolve().parent.parent
REPORTS_DIR = BASE_DIR / "reports"

INPUT_FILE = REPORTS_DIR / "combined_validation_summary.csv"
OUTPUT_FILE = REPORTS_DIR / "quality_dashboard.html"

if not INPUT_FILE.exists():
    raise FileNotFoundError(
        "Combined validation summary not found. "
        "Run quality_summary.py first."
    )

df = pd.read_csv(INPUT_FILE)

required = {
    "File", "Records", "Total_Errors", "Final_Status"
}

if not required.issubset(df.columns):
    raise ValueError("Summary report has missing columns.")

# Calculate dashboard metrics
total_datasets = len(df)
total_records = int(
    pd.to_numeric(df["Records"], errors="coerce")
    .fillna(0).sum()
)

total_errors = int(
    pd.to_numeric(df["Total_Errors"], errors="coerce")
    .fillna(0).sum()
)

passed = int((df["Final_Status"] == "PASSED").sum())
failed = total_datasets - passed

pass_rate = (
    passed / total_datasets * 100
    if total_datasets else 0
)

overall_status = (
    "PASSED" if total_datasets > 0 and failed == 0
    else "FAILED"
)

# Generate HTML table rows
table_rows = ""

for _, row in df.iterrows():
    filename = escape(str(row["File"]))
    status = str(row["Final_Status"])
    safe_status = escape(status)

    css_class = (
        "passed" if status == "PASSED" else "failed"
    )

    records = escape(str(row["Records"]))
    errors = escape(str(row["Total_Errors"]))

    table_rows += f"""
    <tr>
        <td>{filename}</td>
        <td>{records}</td>
        <td>{errors}</td>
        <td>
            <span class="status {css_class}">
                {safe_status}
            </span>
        </td>
    </tr>
    """

# Generate dashboard HTML
html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport"
      content="width=device-width, initial-scale=1.0">

<title>CadetX Data Quality Dashboard</title>

<style>
* {{
    box-sizing: border-box;
}}

body {{
    margin: 0;
    background: #f4f7fb;
    font-family: Arial, sans-serif;
    color: #1e293b;
}}

.container {{
    max-width: 1100px;
    margin: 40px auto;
    padding: 20px;
}}

.header {{
    background: #172554;
    color: white;
    padding: 30px;
    border-radius: 14px;
    margin-bottom: 25px;
}}

.header h1 {{
    margin: 0 0 10px;
}}

.header p {{
    margin: 0;
    color: #cbd5e1;
}}

.cards {{
    display: grid;
    grid-template-columns:
        repeat(auto-fit, minmax(190px, 1fr));
    gap: 18px;
    margin-bottom: 25px;
}}

.card {{
    background: white;
    padding: 25px;
    border-radius: 12px;
    box-shadow: 0 3px 12px rgba(0,0,0,0.06);
}}

.card h3 {{
    font-size: 14px;
    color: #64748b;
    margin: 0 0 15px;
}}

.card .number {{
    font-size: 32px;
    font-weight: bold;
}}

.section {{
    background: white;
    padding: 25px;
    border-radius: 12px;
    overflow-x: auto;
}}

table {{
    width: 100%;
    border-collapse: collapse;
}}

th, td {{
    padding: 15px;
    text-align: left;
    border-bottom: 1px solid #e2e8f0;
}}

th {{
    background: #f8fafc;
}}

.status {{
    display: inline-block;
    padding: 7px 12px;
    border-radius: 20px;
    font-weight: bold;
    font-size: 12px;
}}

.passed {{
    background: #dcfce7;
    color: #166534;
}}

.failed {{
    background: #fee2e2;
    color: #991b1b;
}}

.footer {{
    margin-top: 20px;
    color: #64748b;
    font-size: 13px;
}}

@media (max-width: 600px) {{
    .container {{
        margin: 10px auto;
        padding: 12px;
    }}

    .header {{
        padding: 20px;
    }}
}}
</style>
</head>

<body>
<div class="container">

    <div class="header">
        <h1>CadetX Data Quality Dashboard</h1>
        <p>Automated Data Cleaning & Validation System</p>
        <p>Overall Status: {overall_status}</p>
    </div>

    <div class="cards">
        <div class="card">
            <h3>Total Datasets</h3>
            <div class="number">{total_datasets}</div>
        </div>

        <div class="card">
            <h3>Total Records</h3>
            <div class="number">{total_records}</div>
        </div>

        <div class="card">
            <h3>Dataset Pass Rate</h3>
            <div class="number">{pass_rate:.2f}%</div>
        </div>

        <div class="card">
            <h3>Validation Errors</h3>
            <div class="number">{total_errors}</div>
        </div>
    </div>

    <div class="section">
        <h2>Dataset Validation Results</h2>

        <table>
            <thead>
                <tr>
                    <th>Dataset</th>
                    <th>Records</th>
                    <th>Errors</th>
                    <th>Status</th>
                </tr>
            </thead>

            <tbody>
                {table_rows}
            </tbody>
        </table>
    </div>

    <div class="footer">
        Generated:
        {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
        | CadetX Automated Data Quality System
    </div>

</div>
</body>
</html>
"""

OUTPUT_FILE.write_text(html, encoding="utf-8")

print("CadetX HTML Dashboard Generated Successfully!")
print("Total Datasets:", total_datasets)
print("Total Records:", total_records)
print("Passed:", passed)
print("Failed:", failed)
print("Pass Rate:", f"{pass_rate:.2f}%")
print("Validation Errors:", total_errors)
print("Dashboard saved to:", OUTPUT_FILE)
