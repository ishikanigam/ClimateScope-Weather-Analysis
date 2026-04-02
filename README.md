 ClimateScope Weather Analytics

 Project Overview

ClimateScope is an advanced data-driven weather analytics and decision-support system built using real-world global weather data.

The project analyzes climate patterns such as temperature, humidity, rainfall, and wind speed across countries and time, and transforms them into interactive insights and intelligent recommendations.

In addition to analysis, the project includes a Climate Decision Intelligence System that helps users determine whether activities like travel, outdoor sports, or daily commuting are safe under given weather conditions.

This project is developed as part of the Infosys Internship Program.

---

 Problem Statement

Weather conditions significantly impact human activities, safety, and planning. However, raw weather data is difficult to interpret.

This project aims to:

- Analyze global climate patterns
- Detect extreme weather conditions
- Provide actionable insights
- Build a decision-support application for real-world use

---

 Dataset Information

Dataset: Global Weather Repository (Kaggle)
Link: https://www.kaggle.com/datasets/nelgiriyewithana/global-weather-repository

Key Features:

- Temperature (°C)
- Humidity (%)
- Precipitation (mm)
- Wind Speed (kph)
- Latitude & Longitude
- Date & Time
- Weather Conditions

---

 Technologies Used

- Python
- Pandas
- NumPy
- Plotly
- Streamlit
- Git & GitHub

---

 Milestone 1: Data Preparation & Cleaning

Tasks Completed:

- Loaded and explored dataset
- Handled missing values
- Removed duplicates
- Converted date-time columns
- Standardized column names
- Created cleaned dataset

Output:

- "weather_cleaned.csv"

---

 Milestone 2: Data Analysis & Visualization

Analysis Performed:

- Univariate, bivariate, multivariate analysis
- Correlation analysis
- Seasonal trends
- Time-series analysis
- Rolling averages (7-day, 30-day)
- Volatility analysis
- Extreme event detection
- Anomaly detection (Z-score, IQR)

Visualizations:

- Line charts (time trends)
- Bar charts (country comparison)
- Heatmaps (correlation & seasonal)
- Scatter plots (relationships)
- Box plots (outliers)
- Histograms (distribution)
- Choropleth maps (geographic insights)
- Radar charts (multi-variable comparison)
- Bubble charts (multi-dimensional analysis)

---

 Milestone 3: Interactive Dashboard

Dashboard Features:

- Built using Streamlit + Plotly
- Multi-tab layout:
  - Overview
  - Temperature Analysis
  - Climate Relationships
  - Extreme Events
  - Geographic Insights
  - Climate Risk Advisor

Key Functionalities:

- Dynamic filters (country, date, season)
- Interactive plots
- Real-time updates
- Climate storytelling insights

---

 Milestone 4: Finalization & Application

 Climate Decision Intelligence System (Application)

A real-world decision-support system that:

- Evaluates climate risk
- Provides recommendations for activities
- Helps users make informed decisions

Features:

- Country selection
- Risk tolerance selection
- Activity-based recommendations
- Risk score calculation
- Risk breakdown (temperature, rainfall, wind, humidity)
- Gauge visualization
- Forecast simulation
- Country comparison
- Smart recommendations
- Decision history tracking
- User feedback system
- Report export (TXT)

---

 Testing & Validation

Comprehensive testing was performed including:

- Functional testing
- Risk logic validation
- Edge case handling
- Performance testing
- Bug fixing

All features were verified to ensure accuracy and stability.

---

 Key Insights

- Temperature decreases with increasing latitude
- High humidity correlates with higher precipitation
- Certain regions show high climate volatility
- Extreme temperature events are concentrated in specific regions
- Rainfall patterns indicate flood-prone zones

---

 Methodology

1. Data Cleaning & Preprocessing
2. Feature Engineering (season, time, rolling metrics)
3. Statistical Analysis (mean, std, quantile, z-score)
4. Visualization Design
5. Dashboard Development
6. Application Development
7. Testing & Validation

---

 How to Run the Project

Step 1: Clone Repository

git clone <your-repo-link>
cd ClimateScope

Step 2: Install Dependencies

pip install -r requirements.txt

Step 3: Run Dashboard

streamlit run dashboard.py

---

 Project Structure

ClimateScope/
│
├── data/
│   └── weather_cleaned.csv
    └── weather_final_analysis.csv
│   └── weather.csv
│
├── analysis.py
├── dashboard.py
├── documentation.txt
├── Milestone1_summary.md
├── Milestone2_summary.md
├── Milestone3_summary.md
├── Milestone4_summary.md
├── README.md
├── report.txt
├── summary.txt
├── test_cases.txt



---

 Future Enhancements

- Live weather API integration
- Machine learning-based forecasting
- Real-time anomaly alerts
- Mobile-friendly dashboard
- Advanced predictive analytics

---

 Conclusion

ClimateScope successfully transforms raw weather data into meaningful insights and an intelligent decision-making system.

The project demonstrates:

- Strong data analysis skills
- Effective visualization
- Real-world problem solving
- Application development

---

 Author

Ishika Nigam
Infosys Internship Program

---