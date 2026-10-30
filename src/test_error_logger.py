
import pandas as pd
from error_logger import log_invalid_records

employees = pd.DataFrame({
    "Employee_ID": [101, 102, 103, 104],
    "Age": [25, 16, 30, 70],
    "Salary": [35000, 20000, -5000, 40000]
})

invalid_records = log_invalid_records(employees)

print(invalid_records)
