import pandas as pd

# Load dataset
df = pd.read_csv("data/weather.csv")

# Show first 5 rows
print("First 5 rows:")
print(df.head())

# Show column info
print("\nDataset info:")
print(df.info())

# Show statistics
print("\nStatistics:")
print(df.describe())