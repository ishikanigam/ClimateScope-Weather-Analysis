# Milestone 1 Summary – Data Preparation & Initial Analysis

## Dataset Overview

Dataset Name: Global Weather Repository  
Source: Kaggle  
Records: 124,135 rows  
Columns: 41 columns  

The dataset contains global weather information including temperature, humidity, wind speed, precipitation, location, and time data.

---

## Key Variables

Important variables include:

- temperature_celsius
- temperature_fahrenheit
- humidity
- wind_kph
- wind_mph
- precipitation
- latitude
- longitude
- country
- location_name
- last_updated

These variables help analyze weather trends and climate conditions.

---

## Data Inspection

Initial inspection revealed:

- Dataset contains 124,135 records
- Data types include numeric, text, and datetime
- Global coverage across multiple countries

---

## Data Quality Issues Identified

The following issues were found:

- Missing values in some numeric columns
- Missing values in some categorical columns
- Duplicate records present
- Inconsistent date format in last_updated column

---

## Data Cleaning Steps Performed

The following cleaning steps were applied:

- Missing numeric values filled using mean
- Missing categorical values filled using mode
- Duplicate records removed
- Date column converted to datetime format
- Dataset validated for consistency

---

## Final Output

Cleaned dataset saved as:

data/weather_cleaned.csv

This dataset is now ready for visualization and dashboard development.

---

## Milestone 1 Status

Milestone 1 successfully completed.

Dataset is clean, structured, and ready for analysis.

---