import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Load dataset
print("Loading dataset...")
df = pd.read_csv("data/weather_cleaned.csv")
print("COLUMNS:", df.columns.tolist())
print("current dataframe shape:",df.shape)
print("\nCleaned dataset loaded for analysis")

# Inspect basic information
print("\nFirst 5 rows:")
print(df.head())

print("\nDataset shape:")
print(df.shape)

print("\nDataset info:")
df.info()

print("\nMissing values before cleaning:")
print(df.isnull().sum())

# Handle missing values
print("\nCleaning missing values...")

# Fill numeric columns with mean
numeric_means = df.mean(numeric_only=True)
df.fillna(numeric_means, inplace=True)

# Fill object columns with most frequent value
for column in df.select_dtypes(include='object'):
    df[column] = df[column].fillna(df[column].mode()[0])

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

# =========================================================
# TRANSFORM FEATURE (ROW-LEVEL ENRICHMENT)
# =========================================================

print("\nCreating transform-based features...")

if "country" in df.columns:

    df["country_temp_mean"] = (
        df.groupby("country")["temperature_celsius"]
        .transform("mean")
    )

    df["temp_deviation_from_country"] = (
        df["temperature_celsius"] - df["country_temp_mean"]
    )

    print("Transform features created")

else:
    print("Country column not found for transform")

# =========================================================
# TIME-BASED AGGREGATIONS
# =========================================================

print("\nPerforming time-based aggregations...")

if "last_updated" in df.columns:

    # Ensure datetime
    df["last_updated"] = pd.to_datetime(df["last_updated"], errors="coerce")

    # Weekly aggregation
    weekly_temp = (
        df.groupby(pd.Grouper(key="last_updated", freq="W"))["temperature_celsius"]
        .mean()
        .reset_index()
    )

    # Monthly aggregation
    monthly_temp = (
        df.groupby(pd.Grouper(key="last_updated", freq="M"))["temperature_celsius"]
        .mean()
        .reset_index()
    )

    # Yearly aggregation
    yearly_temp = (
        df.groupby(pd.Grouper(key="last_updated", freq="Y"))["temperature_celsius"]
        .mean()
        .reset_index()
    )

    print("Time aggregations created successfully")

else:
    print("last_updated column not found")

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

# ================================
# COLUMN AUDIT
# ================================

print("\n--- COLUMN AUDIT ---")

column_audit = pd.DataFrame({
    "Column Name": df.columns,
    "Data Type": df.dtypes,
    "Missing Values": df.isnull().sum(),
    "Unique Values": df.nunique()
})

print(column_audit)

# ================================
# EXTREME VALUE CHECK (IQR METHOD)
# ================================

print("\n--- EXTREME VALUE ANALYSIS (IQR) ---")

numeric_cols = df.select_dtypes(include=['number']).columns

for col in numeric_cols:
    Q1 = df[col].quantile(0.25)
    Q3 = df[col].quantile(0.75)
    IQR = Q3 - Q1

    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR

    outliers = df[(df[col] < lower_bound) | (df[col] > upper_bound)]

    print(f"{col}: {len(outliers)} potential outliers")

# ================================
# DISTRIBUTION ANALYSIS
# ================================

print("\n--- SKEWNESS & KURTOSIS ---")

skew_kurt = pd.DataFrame({
    "Skewness": df[numeric_cols].skew(),
    "Kurtosis": df[numeric_cols].kurtosis()
})

print(skew_kurt)

# ================================
# DUPLICATE VERIFICATION
# ================================

print("\n--- DUPLICATE CHECK ---")

duplicate_count = df.duplicated().sum()
print(f"Total duplicate rows remaining: {duplicate_count}")

# ================================
# DATA TYPE VALIDATION
# ================================

print("\n--- DATA TYPES SUMMARY ---")

dtype_summary = df.dtypes.value_counts()
print(dtype_summary)

# ================================
# FULL STATISTICAL SUMMARY
# ================================

print("\n--- FULL STATISTICAL SUMMARY ---")

full_summary = df.describe(include='all')
print(full_summary)

print(df.shape)

# ============================================
# NUMERIC-ONLY STATISTICAL SUMMARY (CLEAN VIEW)
# ============================================

print("\nNumeric columns summary:")

numeric_df = df.select_dtypes(include=['number'])
print(numeric_df.describe())

# =========================================================
# COUNTRY TEMPERATURE VOLATILITY
# =========================================================

print("\nAnalyzing country temperature volatility...")

if "country" in df.columns:

    country_stats = (
        df.groupby("country")["temperature_celsius"]
        .agg(["mean", "std", "count"])
        .reset_index()
    )

    country_stats["volatility"] = (
        country_stats["std"] / country_stats["mean"]
    )

    top_volatile_countries = country_stats.sort_values(
        by="volatility", ascending=False
    ).head(15)

    print("Volatility analysis completed")

else:
    print("Country column missing for volatility")

# =========================================================
# MILESTONE 2 — TEMPORAL FEATURE ENGINEERING
# =========================================================

print("\nCreating temporal features...")

# Ensure datetime format
df['last_updated'] = pd.to_datetime(df['last_updated'], errors='coerce')

# Year
df['year'] = df['last_updated'].dt.year

# Month
df['month'] = df['last_updated'].dt.month

# Day of week
df['day_of_week'] = df['last_updated'].dt.day_name()

# Week number
df['week'] = df['last_updated'].dt.isocalendar().week

# Season mapping
def get_season(month):
    if month in [12, 1, 2]:
        return 'Winter'
    elif month in [3, 4, 5]:
        return 'Summer'
    elif month in [6, 7, 8]:
        return 'Monsoon'
    else:
        return 'Autumn'

df['season'] = df['month'].apply(get_season)

print("Temporal features created successfully")

print(df[['year','month','season']].head()) 
print(df['season'].value_counts())

# ==================================================
# BASIC STATISTICAL SUMMARY
# ==================================================

print("\nGenerating statistical summary...")

numeric_cols = df.select_dtypes(include=['float64', 'int64']).columns

stats_summary = df[numeric_cols].describe().T
stats_summary['skewness'] = df[numeric_cols].skew()
stats_summary['kurtosis'] = df[numeric_cols].kurtosis()

print("\nStatistical summary with skewness & kurtosis:")
print(stats_summary.head(10))

# ==================================================
# IQR AND QUANTILE ANALYSIS
# ==================================================

print("\nCalculating IQR for temperature...")

Q1 = df['temperature_celsius'].quantile(0.25)
Q3 = df['temperature_celsius'].quantile(0.75)
IQR = Q3 - Q1

print(f"Q1: {Q1}")
print(f"Q3: {Q3}")
print(f"IQR: {IQR}")

# ==================================================
# Z-SCORE ANOMALY DETECTION
# ==================================================

print("\nDetecting temperature anomalies using Z-score...")

temp_mean = df['temperature_celsius'].mean()
temp_std = df['temperature_celsius'].std()

df['temp_zscore'] = (df['temperature_celsius'] - temp_mean) / temp_std

extreme_temp = df[np.abs(df['temp_zscore']) > 3]

print(f"Extreme temperature events found: {len(extreme_temp)}")
# ==================================================
# IQR-BASED OUTLIER DETECTION (TEMPERATURE)
# ==================================================

print("\nDetecting temperature outliers using IQR...")

Q1 = df['temperature_celsius'].quantile(0.25)
Q3 = df['temperature_celsius'].quantile(0.75)
IQR = Q3 - Q1

lower_bound = Q1 - 1.5 * IQR
upper_bound = Q3 + 1.5 * IQR

iqr_outliers = df[
    (df['temperature_celsius'] < lower_bound) |
    (df['temperature_celsius'] > upper_bound)
]

print("IQR temperature outliers detected:", len(iqr_outliers))

# ==================================================
# COUNTRY TEMPERATURE VOLATILITY
# ==================================================

print("\nCalculating temperature volatility by country...")

country_stats = (
    df.groupby('country')['temperature_celsius']
    .agg(['mean', 'std'])
    .reset_index()
)

country_stats['volatility'] = country_stats['std'] / country_stats['mean']

top_volatile = country_stats.sort_values(
    by='volatility', ascending=False
).head(15)

print("\nTop volatile countries:")
print(top_volatile)

# ==================================================
# MONTHLY TEMPERATURE TREND
# ==================================================

print("\nComputing monthly temperature trends...")

monthly_trend = (
    df.groupby(['year', 'month'])['temperature_celsius']
    .mean()
    .reset_index()
)

print(monthly_trend.head())

# ==================================================
# SEASONAL TEMPERATURE ANALYSIS
# ==================================================

print("\nSeasonal temperature analysis...")

seasonal_temp = (
    df.groupby('season')['temperature_celsius']
    .agg(['mean', 'std', 'count'])
    .reset_index()
)

print(seasonal_temp)

# ==================================================
# SORT DATA FOR ROLLING ANALYSIS
# ==================================================

df = df.sort_values('last_updated')

# ==================================================
# ROLLING TEMPERATURE FEATURES
# ==================================================

print("\nCreating rolling temperature features...")

df['temp_roll7_mean'] = (
    df['temperature_celsius']
    .rolling(window=7, min_periods=1)
    .mean()
)

df['temp_roll7_std'] = (
    df['temperature_celsius']
    .rolling(window=7, min_periods=1)
    .std()
)

df['temp_roll30_mean'] = (
    df['temperature_celsius']
    .rolling(window=30, min_periods=1)
    .mean()
)

df['temp_roll30_std'] = (
    df['temperature_celsius']
    .rolling(window=30, min_periods=1)
    .std()
)

print("Rolling features created.")

# ==================================================
# CORRELATION MATRIX
# ==================================================

print("\nComputing correlation matrix...")

corr_matrix = df[numeric_cols].corr()
print(corr_matrix.head())
# ==================================================
# SKEWNESS AND KURTOSIS ANALYSIS
# ==================================================

print("\nComputing skewness and kurtosis...")

skew_vals = df[numeric_cols].skew()
kurt_vals = df[numeric_cols].kurtosis()

print("\nSkewness (first few columns):")
print(skew_vals.head())

print("\nKurtosis (first few columns):")
print(kurt_vals.head())

# ==================================================
# LATITUDINAL TEMPERATURE GRADIENT
# ==================================================

print("\nAnalyzing temperature vs latitude...")

lat_temp = (
   df.groupby(
    pd.cut(df['latitude'], bins=20),
    observed=False
)['temperature_celsius']
    .mean()
    .reset_index()
)

print(lat_temp.head())

# ==================================================
# HUMIDITY vs PRECIPITATION RELATIONSHIP
# ==================================================

print("\nAnalyzing humidity vs precipitation correlation...")

if 'humidity' in df.columns and 'precip_mm' in df.columns:
    hum_precip_corr = df['humidity'].corr(df['precip_mm'])
    print("Humidity–Precipitation correlation:", hum_precip_corr)
    # Interpretation for mentor clarity
if abs(hum_precip_corr) < 0.3:
    print("Insight: Weak relationship between humidity and precipitation.")
elif abs(hum_precip_corr) < 0.7:
    print("Insight: Moderate relationship between humidity and precipitation.")
else:
    print("Insight: Strong relationship between humidity and precipitation.")


# ==================================================
# FLOOD RISK DETECTION USING ROLLING RAINFALL
# ==================================================

print("\nDetecting potential flood-risk periods...")

if 'precip_mm' in df.columns:
    
    df['rain_roll7'] = (
        df['precip_mm']
        .rolling(window=7, min_periods=1)
        .sum()
    )
    
    # flag heavy rain weeks (threshold adjustable)
    df['flood_risk_flag'] = df['rain_roll7'] > df['rain_roll7'].quantile(0.95)
    
    print("Flood risk events detected:", df['flood_risk_flag'].sum())

# ==================================================
# TOP VOLATILITY COUNTRIES
# ==================================================

print("\nCalculating temperature volatility by country...")

if 'country' in df.columns and 'temperature_celsius' in df.columns:
    
    volatility_df = (
        df.groupby('country')['temperature_celsius']
        .agg(['mean', 'std'])
        .reset_index()
    )

    # Calculate volatility = std / mean
    volatility_df['volatility'] = (
        volatility_df['std'] / volatility_df['mean']
    )

    print("Volatility table created successfully")
    print(volatility_df.head())

# ==================================================
# CLEAN VOLATILITY TABLE
# ==================================================

print("\nCleaning volatility table...")

volatility_df = volatility_df.dropna(subset=['mean', 'std', 'volatility'])
volatility_df = volatility_df[volatility_df['mean'] != 0]

print("Volatility table cleaned. Rows remaining:", len(volatility_df))

print("\nIdentifying most temperature-volatile countries...")

top_volatility = (
    volatility_df.sort_values('volatility', ascending=False)

)

print(top_volatility)

# ============================================
# CORRELATION HEATMAP DATA PREP
# ============================================

print("\nPreparing correlation heatmap data...")

numeric_cols = df.select_dtypes(include=['number']).columns
corr_matrix = df[numeric_cols].corr()

print("Correlation matrix ready. Shape:", corr_matrix.shape)

# ============================================
# DISTRIBUTION ANALYSIS
# ============================================

print("\nPerforming distribution analysis...")

key_vars = [
    'temperature_celsius',
    'humidity',
    'precip_mm',
    'wind_kph'
]

for col in key_vars:
    if col in df.columns:
        print(f"\n--- {col.upper()} SUMMARY ---")
        print("Mean:", df[col].mean())
        print("Std:", df[col].std())
        print("Skewness:", df[col].skew())
        print("Q1:", df[col].quantile(0.25))
        print("Median:", df[col].quantile(0.50))
        print("Q3:", df[col].quantile(0.75))

# =========================================
# ROLLING TIME SERIES ANALYSIS
# =========================================

print("\nPerforming rolling time-series analysis...")

# -----------------------------------------
# Ensure datetime is proper
# -----------------------------------------
if 'last_updated' in df.columns:
    df['last_updated'] = pd.to_datetime(df['last_updated'], errors='coerce')

# -----------------------------------------
# Sort data (CRITICAL for rolling)
# -----------------------------------------
print("Sorting data by country and time...")

if 'country' in df.columns and 'last_updated' in df.columns:
    df = df.sort_values(['country', 'last_updated'])

print("Data sorted successfully")

# -----------------------------------------
# Country-wise rolling calculations
# -----------------------------------------
required_cols = ['country', 'temperature_celsius']

if all(col in df.columns for col in required_cols):

    print("Creating rolling temperature features...")

    # 7-day rolling mean
    df['temp_roll7_mean'] = (
        df.groupby('country')['temperature_celsius']
        .transform(lambda x: x.rolling(window=7, min_periods=1).mean())
    )

    # 30-day rolling mean
    df['temp_roll30_mean'] = (
        df.groupby('country')['temperature_celsius']
        .transform(lambda x: x.rolling(window=30, min_periods=1).mean())
    )

    # 7-day rolling std
    df['temp_roll7_std'] = (
        df.groupby('country')['temperature_celsius']
        .transform(lambda x: x.rolling(window=7, min_periods=1).std())
    )

    # 30-day rolling std
    df['temp_roll30_std'] = (
        df.groupby('country')['temperature_celsius']
        .transform(lambda x: x.rolling(window=30, min_periods=1).std())
    )

    print("Rolling features created successfully")

    # -------------------------------------
    # Show sample output
    # -------------------------------------
    print("\nSample rolling values:")
    print(
        df[['last_updated',
            'temperature_celsius',
            'temp_roll7_mean',
            'temp_roll30_mean']]
        .head()
    )

else:
    print("Required columns for rolling analysis not found")

# =========================================================
# DISTRIBUTION ANALYSIS
# =========================================================
print("\nAnalyzing distributions of key weather variables...")

key_cols = [
    'temperature_celsius',
    'humidity',
    'precip_mm',
    'wind_kph'
]

for col in key_cols:
    if col in df.columns:
        print(f"\n--- {col} summary ---")
        print(df[col].describe())

        print("Skewness:", df[col].skew())
        print("Kurtosis:", df[col].kurt())

# =========================================================
# EXTREME RAINFALL EVENTS
# =========================================================

print("\nDetecting extreme rainfall events...")

if 'precip_mm' in df.columns:
    rain_threshold = df['precip_mm'].quantile(0.99)
    extreme_rain = df[df['precip_mm'] > rain_threshold]

    print("Extreme rainfall events found:", len(extreme_rain))
else:
    print("precip_mm column not found")

# =========================================================
# SEASONAL TEMPERATURE ANALYSIS
# =========================================================

print("\nAnalyzing seasonal temperature patterns...")

if 'season' in df.columns and 'temperature_celsius' in df.columns:
    seasonal_temp = df.groupby('season')['temperature_celsius'].agg(['mean','std','count'])
    print(seasonal_temp)
else:
    print("Required columns for seasonal analysis not found")

# =========================================================
# WIND TURBULENCE ANALYSIS
# =========================================================

print("\nAnalyzing wind turbulence...")

if 'wind_kph' in df.columns:
    wind_stats = df['wind_kph'].describe()
    wind_std = df['wind_kph'].std()

    print("\n--- WIND SUMMARY ---")
    print(wind_stats)
    print("Wind variability (std):", wind_std)

    if wind_std > df['wind_kph'].mean():
        print("Insight: High wind turbulence observed.")
    else:
        print("Insight: Wind patterns relatively stable.")
else:
    print("wind_kph column not found")

# =========================================================
# WIND OUTLIER CHECK
# =========================================================

print("\nChecking for extreme wind outliers...")

if 'wind_kph' in df.columns:
    wind_q99 = df['wind_kph'].quantile(0.99)
    extreme_wind = df[df['wind_kph'] > wind_q99]

    print("Extreme wind events detected:", len(extreme_wind))

    if df['wind_kph'].max() > 200:
        print("Insight: Dataset contains unusually high wind speed outliers.")
else:
    print("wind_kph column not found")

print("Insight: Weak relationship between humidity and precipitation.")