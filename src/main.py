
import pandas as pd

# Step 1: Load dataset
df = pd.read_csv("data/customer.csv")

print("Original Dataset:")
print(df)

# Step 2: Check missing values
print("\nMissing Values Before Cleaning:")
print(df.isnull().sum())

# Step 3: Remove duplicate rows
df = df.drop_duplicates()

# Step 4: Fill missing Age with median
df["Age"] = df["Age"].fillna(df["Age"].median())

# Step 5: Fill missing Salary with median
df["Salary"] = df["Salary"].fillna(df["Salary"].median())

# Step 6: Check cleaned data
print("\nCleaned Dataset:")
print(df)

# Step 7: Save cleaned CSV
df.to_csv("data/cleaned_customer.csv", index=False)
print("\nData cleaning completed successfully!")
