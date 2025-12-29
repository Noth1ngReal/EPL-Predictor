import pandas as pd

df = pd.read_csv("../data/raw/matches.csv")

print("\n=== DATASET OVERVIEW ===")
print(f"Total matches: {len(df)}")
print(f"\nColumn names:")
print(df.columns.tolist())

# Show first few rows
print("\n=== FIRST 5 MATCHES ===")
print(df.head())

# Show data types
print("\n=== DATA TYPES ===")
print(df.dtypes)

# Check for missing values
print("\n=== MISSING VALUES ===")
print(df.isnull().sum())

print("\n✓ Data exploration complete!")
