import pandas as pd

# Load dataset
print("Loading dataset...")
df = pd.read_csv("data/weather.csv")

# Inspect basic information
print("\nFirst 5 rows:")
print(df.head())

print("\nDataset shape:")
print(df.shape)

print("\nDataset info:")
print(df.info())

print("\nMissing values before cleaning:")
print(df.isnull().sum())

# Handle missing values
print("\nCleaning missing values...")

# Fill numeric columns with mean
df.fillna(df.mean(numeric_only=True), inplace=True)

# Fill object columns with most frequent value
for column in df.select_dtypes(include='object'):
    df[column].fillna(df[column].mode()[0], inplace=True)

print("\nMissing values after cleaning:")
print(df.isnull().sum())

# Remove duplicate rows
print("\nRemoving duplicate rows...")
df.drop_duplicates(inplace=True)

print("New dataset shape after removing duplicates:")
print(df.shape)

# Convert date column to datetime
print("\nConverting date column...")

if 'last_updated' in df.columns:
    df['last_updated'] = pd.to_datetime(df['last_updated'], errors='coerce')

# Aggregate data (monthly average temperature)
print("\nMonthly average temperature:")

if 'temperature_celsius' in df.columns and 'last_updated' in df.columns:
    monthly_avg = df.groupby(df['last_updated'].dt.month)['temperature_celsius'].mean()
    print(monthly_avg)

# Save cleaned dataset
print("\nSaving cleaned dataset...")

df.to_csv("data/weather_cleaned.csv", index=False)

print("Cleaned dataset saved as data/weather_cleaned.csv")

print("\nMilestone 1 Data Preparation Complete")
