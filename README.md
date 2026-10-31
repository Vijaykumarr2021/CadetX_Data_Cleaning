
# CadetX Automated Data Cleaning & Validation System

[![CadetX Python Tests](https://github.com/Vijaykumarr2021/CadetX_Data_Cleaning/actions/workflows/python-tests.yml/badge.svg)](https://github.com/Vijaykumarr2021/CadetX_Data_Cleaning/actions/workflows/python-tests.yml)

An automated Python-based data quality system that cleans, validates, and analyzes CSV datasets. The project generates validation reports, data quality summaries, visualizations, and an HTML dashboard.

## Project Overview

Poor-quality data can lead to inaccurate analysis and business decisions.

This project provides a reusable workflow for identifying data quality issues, cleaning datasets, validating records, and generating reports.

It demonstrates practical skills in Python programming, Pandas, data preprocessing, automated testing, and continuous integration.

## Key Features

- Automated CSV data cleaning
- Missing value detection and handling
- Duplicate record detection
- Data validation using reusable rules
- Invalid record logging
- Batch processing of multiple datasets
- Advanced validation for IDs, ages, salaries, quantities, prices, and text fields
- Data quality score calculation
- CSV and text-based validation reports
- Data quality visualizations
- HTML data quality dashboard
- Automated testing using pytest
- GitHub Actions continuous integration

## Technologies Used

| Technology | Purpose |
|------------|---------|
| Python | Core programming language |
| Pandas | Data cleaning and processing |
| pytest | Automated unit testing |
| HTML/CSS | Data quality dashboard |
| Git | Version control |
| GitHub | Source code hosting |
| GitHub Actions | Continuous integration |
| VS Code | Development environment |

## Project Structure

```text
CadetX_Data_Cleaning/
├── .github/
│   └── workflows/
│       └── python-tests.yml
├── data/
│   ├── raw/
│   ├── processed/
│   ├── customer.csv
│   └── cleaned_customer.csv
├── reports/
│   ├── batch_validation_report.csv
│   ├── advanced_validation_report.csv
│   ├── combined_validation_summary.csv
│   ├── data_quality_summary.txt
│   └── quality_dashboard.html
├── src/
│   ├── main.py
│   ├── validation.py
│   ├── validation_rules.py
│   ├── advanced_validator.py
│   ├── batch_cleaner.py
│   ├── batch_validator.py
│   ├── quality_score.py
│   ├── quality_summary.py
│   ├── quality_dashboard.py
│   └── run_batch_pipeline.py
├── tests/
│   ├── test_validation_rules.py
│   └── invalid_sales.csv
├── requirements.txt
└── README.md
```

The structure above highlights the main project files.

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/Vijaykumarr2021/CadetX_Data_Cleaning.git
cd CadetX_Data_Cleaning
```

### 2. Create a virtual environment

```bash
python3 -m venv .venv
```

### 3. Activate the environment

On macOS or Linux:

```bash
source .venv/bin/activate
```

### 4. Install dependencies

```bash
python -m pip install -r requirements.txt
```

## How to Run

### Run the batch processing pipeline

```bash
python src/run_batch_pipeline.py
```

### Generate the data quality dashboard

```bash
python src/quality_dashboard.py
```

Open `reports/quality_dashboard.html` in a web browser to view the dashboard.

## Automated Testing

Run the validation tests:

```bash
python -m pytest tests/test_validation_rules.py -v
```

The project includes 13 validation tests covering data quality checks and invalid input scenarios.

GitHub Actions automatically runs the tests when code is pushed to the `main` branch or a pull request targets `main`.

## Sample Project Results

During the Day 9 sample dataset run:

| Metric | Result |
|--------|--------|
| Datasets processed | 3 |
| Records processed | 14 |
| Datasets passed | 3 |
| Datasets failed | 0 |
| Validation errors | 0 |
| Dataset pass rate | 100% |

These results describe the sample datasets used during development, not a guarantee for all input data.

## Business Applications

This system can support:

- Data preprocessing before analysis
- Customer data quality checks
- Employee record validation
- Sales data validation
- Data quality reporting
- Reusable ETL data validation workflows

## Future Improvements

- Configurable validation rules
- Additional data formats
- Database integration
- Interactive dashboard filters
- Automated reporting and notifications

## Author

**Vijay Kumar**

Aspiring Data Analyst | Python | SQL | Excel | Power BI

[LinkedIn](https://www.linkedin.com/in/vijay-kumar-005159250/) |
[GitHub](https://github.com/Vijaykumarr2021)

## License

No license has been specified for this repository.
```
