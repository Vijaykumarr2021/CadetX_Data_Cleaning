
import pandas as pd
from pathlib import Path
from error_logger import log_invalid_records

BASE_DIR = Path(__file__).resolve().parent.parent

input_path = BASE_DIR / "data" / "customer.csv"

df = pd.read_csv(input_path)

invalid_records = log_invalid_records(df)

print("Total invalid records:", len(invalid_records))
