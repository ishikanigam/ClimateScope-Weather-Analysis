# ClimateScope Weather Analysis

## Project Overview
ClimateScope is a data analytics project that explores the Global Weather Repository dataset to understand global weather behavior, seasonal patterns, extreme events, and cross-country climate variations.

The project applies statistical analysis and interactive visualization techniques to uncover meaningful climate insights.

This work is part of the Infosys Springboard Internship Program.

---

## Dataset Source
Global Weather Repository dataset from Kaggle:  
https://www.kaggle.com/datasets/nelgiriyewithana/global-weather-repository

---

# Milestone 1: Data Preparation & Cleaning

### Tasks Completed

- Downloaded dataset from Kaggle  
- Set up Python development environment  
- Inspected dataset structure and data types  
- Handled missing and inconsistent values  
- Removed duplicate records  
- Standardized date formats  
- Performed basic feature engineering  
- Generated cleaned dataset for analysis  

### Output

- `weather_cleaned.csv` — cleaned and analysis-ready dataset

---

# Milestone 2: Core Analysis & Visualization Design

## Statistical Analysis Performed

- Distribution analysis of temperature, humidity, wind speed, and precipitation  
- Correlation analysis between key weather variables  
- Seasonal pattern analysis  
- Temperature volatility analysis by country  
- Latitude–temperature gradient analysis  
- Rolling time-series trend analysis  

---

## Extreme Event Detection

The following extreme weather conditions were identified:

- Extreme temperature events  
- Heavy rainfall / flood-risk events  
- High wind speed events  

Thresholds were determined using statistical quantiles to ensure robustness.

---

## Comparative Climate Analysis

Cross-country comparisons were performed to identify:

- Hottest and coldest regions  
- Most volatile climates  
- Seasonal variability differences  
- Regional rainfall patterns  

---

## Visualization Strategy

The dashboard uses appropriate visualization types:

- **Line charts** → time-series trends  
- **Scatter plots** → correlation analysis  
- **Heatmaps** → seasonal and correlation patterns  
- **Histograms** → distribution analysis  
- **Choropleth map** → global geographic patterns  

---

## Interactive Dashboard

An interactive Streamlit dashboard was designed with:

- Country filter  
- Date range filter  
- Time aggregation control  
- Season filter  
- Comparative country analysis  
- Real-time KPI metrics  

The dashboard dynamically updates visualizations based on user selections.

---

## Technologies Used

- Python  
- Pandas  
- NumPy  
- Plotly  
- Streamlit  
- Matplotlib  
- Seaborn  
- Git & GitHub  
- VS Code  

---

## Current Status

✅ Milestone 1 — Completed  
✅ Milestone 2 — Completed  

The project now includes statistical analysis, extreme event detection, and an interactive dashboard for climate exploration.

---

### Note on Dashboard Scope

The current dashboard implementation focuses on exploratory analytics and interactive visualization as required for Milestone 2. 

The architecture has been designed to be extensible, and further refinements such as advanced predictive modeling, enhanced interactivity, and deployment optimization are planned for subsequent milestones.