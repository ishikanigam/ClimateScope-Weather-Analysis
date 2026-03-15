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

## Milestone 2: Core Analysis & Visualization Design

### Tasks Completed

- Performed statistical analysis of the weather dataset
- Analyzed distributions of temperature, humidity, rainfall, and wind speed
- Computed correlation matrices to understand relationships between climate variables
- Performed seasonal analysis using derived season features
- Detected extreme weather events using quantile thresholds and anomaly detection
- Compared weather conditions across countries
- Implemented rolling averages to observe temperature trends
- Designed visualization plan for the interactive dashboard

### Key Analysis Performed

- Temperature volatility analysis by country
- Latitudinal temperature gradient analysis
- Seasonal climate pattern analysis
- Extreme temperature event detection
- Flood risk detection using rainfall thresholds
- Correlation analysis between climate variables

### Visualization Types Selected

- Line charts for time-series trends
- Histograms for distribution analysis
- Box plots for outlier detection
- Scatter plots for correlation analysis
- Choropleth maps for geographic patterns
- Heatmaps for correlation matrices
- Bar charts for country comparisons

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


### Milestone 2 Status

Completed Successfully

Statistical insights and visualization design were finalized for dashboard development.

### Note on Dashboard Scope

The current dashboard implementation focuses on exploratory analytics and interactive visualization as required for Milestone 2. 

The architecture has been designed to be extensible, and further refinements such as advanced predictive modeling, enhanced interactivity, and deployment optimization are planned for subsequent milestones.

---

## Milestone 3: Interactive Climate Dashboard

### Objective

Develop a fully interactive climate analytics dashboard to visualize global weather patterns and extreme climate events.

### Dashboard Features

- Interactive Streamlit dashboard
- Dynamic filters for country, season, and date range
- Real-time updates of visualizations based on user input
- Multiple interactive Plotly charts
- Insight explanations for each visualization

### Visualizations Implemented

- Temperature distribution histogram
- Temperature trend over time
- Seasonal temperature patterns
- Correlation heatmap of climate variables
- Seasonal correlation heatmaps
- Latitudinal temperature gradient
- Country-wise temperature comparison
- Global temperature choropleth map
- Temperature volatility analysis
- Extreme temperature event detection
- Flood risk detection using rainfall distribution
- Wind speed distribution (Weibull approximation)
- Humidity vs precipitation correlation
- Radar chart for country climate comparison
- Bubble chart for temperature–humidity–wind interaction
- Sunburst chart for seasonal temperature distribution

### Additional Analytical Features

- Rolling temperature trend analysis
- Extreme weather anomaly detection
- Climate insight storytelling
- AI-generated climate insights
- Environmental metrics analysis
- Interactive climate comparison tools

### Technologies Used

- Python
- Pandas
- NumPy
- Plotly
- Streamlit
- Git
- GitHub

### Milestone 3 Status

Completed Successfully

An interactive climate analytics dashboard was developed to explore global weather patterns, climate risks, and environmental trends.

## Current Status

✅ Milestone 1 — Completed  
✅ Milestone 2 — Completed  
✅ Milestone 3 — Completed  
The project now includes statistical analysis, extreme event detection, and an interactive dashboard for climate exploration.

---