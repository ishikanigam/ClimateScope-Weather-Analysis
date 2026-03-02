# ClimateScope Weather Analysis

## Project Overview

This project analyzes the Global Weather Repository dataset to understand global weather trends, temperature variations, humidity, wind speed, and other climate indicators.

This project is part of the Infosys Internship Program.

## Milestone 1: Data Preparation & Initial Analysis

### Dataset Source
Global Weather Repository dataset from Kaggle:
https://www.kaggle.com/datasets/nelgiriyewithana/global-weather-repository

### Tasks Completed

- Downloaded dataset from Kaggle
- Set up project environment using Python, VS Code, and GitHub
- Inspected dataset structure and data types
- Identified missing values and anomalies
- Handled missing and inconsistent data
- Removed duplicate entries
- Converted date columns to proper format
- Aggregated temperature data to monthly averages
- Created cleaned dataset ready for analysis

### Files in Project

- `analysis.py` → Python script for data inspection and cleaning
- `weather.csv` → Original dataset
- `weather_cleaned.csv` → Cleaned dataset (Milestone 1 output)
- `.gitignore` → Specifies files ignored by Git
- `README.md` → Project documentation

### Technologies Used

- Python
- Pandas
- NumPy
- Git
- GitHub
- VS Code

---

### Milestone 1 Status

Dataset is cleaned and ready for visualization and dashboard development.

---

## Milestone 2: Core Analysis & Visualization Design

### Objective

Perform deep statistical analysis on the cleaned weather dataset and design an interactive visualization dashboard to uncover climate patterns, correlations, and extreme weather events.

### Key Analysis Performed

-Statistical Analysis
-Distribution analysis of temperature, humidity, precipitation, and wind speed
-Mean, standard deviation, quantile, IQR, and skewness calculations
-Z-score–based anomaly detection
-Extreme weather event identification

### Temporal & Seasonal Analysis

-Year, month, day-of-week, and season feature engineering
-Daily, monthly, yearly, and seasonal aggregations
-Seasonal pattern detection
-Rolling statistics (7-day and 30-day moving averages and standard deviations)

### Correlation & Multivariate Analysis

-Correlation matrix across climate variables
-Season-wise correlation heatmaps
-Temperature–precipitation relationship analysis
-Humidity–precipitation interaction study

### Geospatial & Volatility Analysis

-Country-wise temperature volatility (SD/Mean)
-Latitude–temperature gradient analysis
-Identification of high-risk climate regions
-Flood risk flagging using rolling precipitation logic

### Visualization Design

-The following visualizations were developed:
-Correlation heatmap
-Seasonal heatmap
-Choropleth global climate map
-Temperature time-series plots
-Country comparison line charts
-Distribution histograms and box plots
-Latitude vs temperature scatter plot
-Volatility bar charts
-Hexbin density plots

### Interactive Dashboard (Streamlit)

-An interactive Streamlit dashboard was designed with:
-Dynamic country filtering
-Date range selection
-Seasonal filters
-Time aggregation controls
-Multi-country comparison
-Interactive Plotly visualizations
-Climate insight panels
-The dashboard enables exploratory climate analysis across regions and time.

further enhancements to be done in next milestones

### Files Added/Updated in Milestone 2

-analysis.py → Extended with statistical and climate analysis
-dashboard.py → Interactive Streamlit dashboard
-Milestone2_Summary.md → Detailed analytical report
-weather_cleaned.csv → Used for downstream analysis

### Milestone 2 Status

 -Statistical analysis completed
 -Climate insights derived
 -Interactive dashboard designed
 -Visualization framework established
 
Project is ready for advanced modeling and prediction in Milestone 3.
