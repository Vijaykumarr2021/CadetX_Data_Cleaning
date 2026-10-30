
# CadetX Automated Data Cleaning & Validation System

A Python-based automated data cleaning and validation
system developed using Pandas.

## Features

- Import employee data from CSV files
- Identify missing values
- Remove duplicate records
- Fill missing values using median
- Validate employee ages and salaries
- Detect duplicate employee IDs
- Generate automated data quality reports
- Execute the complete pipeline with one command

## Technologies Used

- Python 3
- Pandas
- CSV
- VS Code

## Project Structure

CadetX_Data_Cleaning/
- data/ - Raw and cleaned datasets
- src/ - Python source code
- reports/ - Generated quality reports
- tests/ - Automated tests (planned)
- requirements.txt - Python dependencies
- .gitignore - Git exclusions

## Installation

Create and activate a virtual environment:

python3 -m venv .venv
source .venv/bin/activate

Install dependencies:

python3 -m pip install -r requirements.txt

## Run the Project

python3 src/run_pipeline.py

## Sample Results

- Original records: 7
- Cleaned records: 6
- Missing values filled: 2
- Duplicate rows removed: 1
- Validation status: PASSED

## Output

- data/cleaned_customer.csv
- reports/data_quality_report.txt
