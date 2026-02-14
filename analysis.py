import pandas as pd

# Load dataset
df = pd.read_csv("data/weather.csv")

# Show first 5 rows
print("First 5 rows:")
print(df.head())

# Show column info
print("\nDataset info:")
<<<<<<< HEAD
df.info()
=======
print(df.info())
>>>>>>> b500aecd70d8b85242c7e76664911a60cda70e21

# Show statistics
print("\nStatistics:")
print(df.describe())