# =========================================================
# ClimateScope Analytics Dashboard — Milestone 2
# =========================================================

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(
    page_title="ClimateScope Weather Analytics",
    page_icon="🌍",
    layout="wide"
)

st.set_page_config(page_title="ClimateScope Dashboard", layout="wide")

st.title("🌍 ClimateScope Weather Analytics Dashboard")
st.markdown(
    "Interactive climate insights using global weather data."
)
st.divider()
# =========================================================
# LOAD DATA
# =========================================================

@st.cache_data(show_spinner=False)
def load_data():
    df = pd.read_csv("data/weather_cleaned.csv")

    # ===== Create Season Column =====
    if "last_updated" in df.columns:
        df["last_updated"] = pd.to_datetime(df["last_updated"], errors="coerce")
        df["month"] = df["last_updated"].dt.month

        def get_season(month):
            if month in [12, 1, 2]:
                return "Winter"
            elif month in [3, 4, 5]:
                return "Summer"
            elif month in [6, 7, 8, 9]:
                return "Monsoon"
            else:
                return "Post-Monsoon"

        df["season"] = df["month"].apply(get_season)

    return df

df = load_data()

# =====================================================
# SIDEBAR — GLOBAL DASHBOARD CONTROLS
# =====================================================

st.sidebar.header("🔧 ClimateScope Controls")

# -----------------------------------------------------
# Country filter
# -----------------------------------------------------
countries = sorted(df["country"].dropna().unique())

selected_country = st.sidebar.selectbox(
    "🌍 Select Country",
    options=["All Countries"] + countries,
    index=0
)

# -----------------------------------------------------
# Date range filter
# -----------------------------------------------------
min_date = df["last_updated"].min()
max_date = df["last_updated"].max()

date_range = st.sidebar.date_input(
    "📅 Select Date Range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)

# -----------------------------------------------------
# Time aggregation selector
# -----------------------------------------------------
time_agg = st.sidebar.selectbox(
    "⏱ Time Aggregation",
    ["Daily", "Monthly", "Yearly"],
    index=0
)

# -----------------------------------------------------
# Season filter
# -----------------------------------------------------
available_seasons = sorted(df["season"].dropna().unique())

selected_seasons = st.sidebar.multiselect(
    "🌦 Filter by Season",
    options=available_seasons,
    default=available_seasons
)

# -----------------------------------------------------
# Extreme temperature threshold (advanced control)
# -----------------------------------------------------
temp_threshold = st.sidebar.slider(
    "🔥 Extreme Temperature Threshold (°C)",
    min_value=float(df["temperature_celsius"].min()),
    max_value=float(df["temperature_celsius"].max()),
    value=float(df["temperature_celsius"].quantile(0.95))
)

# =====================================================
# APPLY ALL FILTERS
# =====================================================

filtered_df = df.copy()

# Country filter
if selected_country != "All Countries":
    filtered_df = filtered_df[
        filtered_df["country"] == selected_country
    ]

# Date filter
if isinstance(date_range, (list, tuple)) and len(date_range) == 2:
    start_date, end_date = date_range
    filtered_df = filtered_df[
        (filtered_df["last_updated"] >= pd.to_datetime(start_date)) &
        (filtered_df["last_updated"] <= pd.to_datetime(end_date))
    ]

# Season filter
if selected_seasons:
    filtered_df = filtered_df[
        filtered_df["season"].isin(selected_seasons)
    ]

# -----------------------------------------------------
# Time aggregation processing
# -----------------------------------------------------
if time_agg == "Monthly":
    filtered_df["time_period"] = filtered_df["last_updated"].dt.to_period("M").astype(str)

elif time_agg == "Yearly":
    filtered_df["time_period"] = filtered_df["last_updated"].dt.year.astype(str)

else:
    filtered_df["time_period"] = filtered_df["last_updated"].dt.date.astype(str)

# -----------------------------------------------------
# Extreme temperature flag (useful across charts)
# -----------------------------------------------------
filtered_df["is_extreme_temp"] = filtered_df["temperature_celsius"] > temp_threshold

# =====================================================
# SAFETY CHECK 
# =====================================================

st.sidebar.markdown("---")
st.sidebar.write(f"📊 Filtered Rows: {len(filtered_df):,}")

# =====================================================
# FINAL DATA OVERRIDE (makes all charts reactive)
# =====================================================
df = filtered_df.copy()

# =====================================================
# PRECOMPUTE — Temperature Volatility (used in KPIs)
# =====================================================

if "country" in df.columns and "temperature_celsius" in df.columns:
    volatility_df = (
        df.groupby("country")["temperature_celsius"]
        .agg(["mean", "std"])
        .reset_index()
    )

    volatility_df["volatility"] = (
        volatility_df["std"] / volatility_df["mean"]
    )
else:
    volatility_df = pd.DataFrame()

# =====================================================
# Detect rainfall column safely (GLOBAL)
# =====================================================

rain_col = None
for col in ["precip_mm", "precipitation_mm", "precip"]:
    if col in df.columns:
        rain_col = col
        break

st.success("✅ Data loaded successfully")
# =========================================================
# KPI METRICS
# =========================================================

st.subheader("📊 Key Climate Indicators")

col1, col2, col3 = st.columns(3)

col1.metric(
    "🌡 Avg Temperature",
    f"{df['temperature_celsius'].mean():.2f} °C"
)

if 'humidity' in df.columns:
    col2.metric(
        "💧 Avg Humidity",
        f"{df['humidity'].mean():.2f} %"
    )

if 'precip_mm' in df.columns:
    col3.metric(
        "🌧 Total Rainfall",
        f"{df['precip_mm'].sum():.0f} mm"
    )

st.subheader("🔎 Key Climate Insights")

col1, col2, col3 = st.columns(3)

with col1:
    hottest_country = df.groupby("country")["temperature_celsius"].mean().idxmax()
    st.info(f"🔥 Hottest Country: {hottest_country}")

with col2:
    wettest_country = df.groupby("country")[rain_col].mean().idxmax()
    st.info(f"🌧 Wettest Country: {wettest_country}")

with col3:
    most_volatile = volatility_df.sort_values("volatility", ascending=False)["country"].iloc[0]
    st.info(f"📊 Most Temperature Volatile: {most_volatile}")

# =========================================================
# SECTION — Country Temperature Volatility
# =========================================================

st.subheader("Temperature Volatility by Country")

if "country" in df.columns:

    country_stats = (
        df.groupby("country")["temperature_celsius"]
        .agg(["mean", "std"])
        .reset_index()
    )

    country_stats["volatility"] = (
        country_stats["std"] / country_stats["mean"]
    )

    top_vol = country_stats.sort_values(
        by="volatility", ascending=False
    ).head(15)

    fig_vol = px.bar(
        top_vol,
        x="country",
        y="volatility",
        title="Top Volatile Countries"
    )

    st.plotly_chart(fig_vol, use_container_width=True, key="temperature_votal")

else:
    st.warning("Country column not found")

# =========================================================
# SECTION - TEMPERATURE DISTRIBUTION
# =========================================================

st.subheader("Temperature Distribution")

fig_hist = px.histogram(
    df,
    x="temperature_celsius",
    nbins=50,
    title="Temperature Distribution",
)

st.plotly_chart(fig_hist, use_container_width=True, key="temperature_hist")

# =========================================================
# SECTION — Temperature Trend Over Time
# =========================================================

st.subheader("📈 Temperature Trend Over Time")

if "last_updated" in df.columns and "temperature_celsius" in df.columns:

    temp_time = (
        df.sort_values("last_updated")
          .groupby(pd.Grouper(key="last_updated", freq="D"))["temperature_celsius"]
          .mean()
          .reset_index()
    )

    fig_time = px.line(
        temp_time,
        x="last_updated",
        y="temperature_celsius",
        title="Average Daily Temperature Trend"
    )

    st.plotly_chart(fig_time, use_container_width=True, key="tempreature_line")

else:
    st.warning("⚠️ Required columns not found for time series")

# =========================================================
# SECTION - CORRELATION HEATMAP
# =========================================================

st.subheader("Correlation Heatmap")

numeric_cols = df.select_dtypes(include=np.number).columns
corr_matrix = df[numeric_cols].corr()

fig_heat = px.imshow(
    corr_matrix,
    text_auto=True,
    aspect="auto",
    title="Correlation Matrix",
)

st.plotly_chart(fig_heat, use_container_width=True, key="corr_heatmap")

st.subheader("📅 Seasonal Correlation Heatmap")

if "season" in df.columns:

    for season in df["season"].dropna().unique():
        st.write(f"**Season: {season}**")

        season_df = df[df["season"] == season]

        corr = season_df.select_dtypes(include=np.number).corr()

        fig_season_corr = px.imshow(
            corr,
            text_auto=True,
            title=f"Correlation Matrix — {season}"
        )

        st.plotly_chart(
            fig_season_corr,
            use_container_width=True,
            key=f"season_corr_{season}"
        )

# =========================================================
# SECTION — Latitude vs Temperature
# =========================================================

st.subheader("Latitudinal Temperature Gradient")

if {"latitude", "temperature_celsius"}.issubset(df.columns):

    fig_lat = px.scatter(
        df.sample(min(5000, len(df))),
        x="latitude",
        y="temperature_celsius",
        title="Temperature vs Latitude",
        opacity=0.5
    )

    st.plotly_chart(fig_lat, use_container_width=True, key="lat_scatter")

else:
    st.warning("Latitude or temperature column missing")

# =========================================================
# SECTION — Country-wise Temperature Comparison
# =========================================================

st.subheader("🌍 Average Temperature by Country")

if "country" in df.columns and "temperature_celsius" in df.columns:

    country_temp = (
        df.groupby("country")["temperature_celsius"]
          .mean()
          .sort_values(ascending=False)
          .head(15)
          .reset_index()
    )

    fig_country = px.bar(
        country_temp,
        x="country",
        y="temperature_celsius",
        title="Top Countries by Average Temperature"
    )

    st.plotly_chart(fig_country, use_container_width=True, key="temp_bar")

else:
    st.warning("⚠️ Country or temperature column missing")

# =========================================================
# SECTION - GLOBAL TEMPERATURE MAP
# =========================================================

st.subheader("Average Temperature by Country")

country_temp = (
    df.groupby("country")["temperature_celsius"]
    .mean()
    .reset_index()
)

fig_map = px.choropleth(
    country_temp,
    locations="country",
    locationmode="country names",
    color="temperature_celsius",
    title="Average Temperature by Country",
    color_continuous_scale="RdYlBu_r",
)

st.plotly_chart(fig_map, use_container_width=True, key="choropleth_map")

# =========================================================
# SECTION - TEMPERATURE TREND
# =========================================================

st.subheader("Temperature Time Trend")

if "last_updated" in df.columns:
    df["last_updated"] = pd.to_datetime(df["last_updated"], errors="coerce")

    temp_time = (
        df.groupby("last_updated")["temperature_celsius"]
        .mean()
        .reset_index()
        .sort_values("last_updated")
    )

    fig_line = px.line(
        temp_time,
        x="last_updated",
        y="temperature_celsius",
        title="Temperature Trend Over Time",
    )

    st.plotly_chart(fig_line, use_container_width=True, key="temp_line")

# =========================================================
# SECTION - HUMIDITY VS PRECIPITATION
# =========================================================

st.subheader("Humidity vs Precipitation")

if {"humidity", "precip_mm"}.issubset(df.columns):
    fig_scatter = px.scatter(
        df,
        x="humidity",
        y="precip_mm",
        title="Humidity vs Precipitation",
        opacity=0.5,
    )

    st.plotly_chart(fig_scatter, use_container_width=True, key="hum_prec_scatter")

# =========================================================
# SECTION - SEASONAL HEATMAP
# =========================================================

st.header("Seasonal Temperature Pattern")

if "season" in df.columns and "temperature_celsius" in df.columns:
    
    seasonal_temp = (
        df.groupby("season")["temperature_celsius"]
        .mean()
        .reset_index()
    )

    if not seasonal_temp.empty:
        fig_season = px.bar(
            seasonal_temp,
            x="season",
            y="temperature_celsius",
            title="Average Temperature by Season"
        )
        st.plotly_chart(fig_season, use_container_width=True, key="seasonal_bar")
    else:
        st.warning("No seasonal data available.")
else:
    st.warning("Season column not found.")

# =========================================================
# SECTION - Extreme Temperature Events
# =========================================================

st.header("Extreme Temperature Events")

# Safety check
if "temperature_celsius" in df.columns:

    # ---- Clean temperature data ----
    temp_series = df["temperature_celsius"].dropna()

    # ---- Define extreme threshold (top 5% hottest) ----
    extreme_threshold = temp_series.quantile(0.95)

    extreme_events = temp_series[temp_series > extreme_threshold]

    # ---- Metric display ----
    st.metric(
        label="🔥 Extreme Temperature Events",
        value=len(extreme_events)
    )

    # ---- Boxplot for outlier detection ----
    st.subheader("Temperature Outlier Detection")

    fig_box = px.box(
        df,
        y="temperature_celsius",
        title="Temperature Outlier Detection",
        color_discrete_sequence=["#FF6B6B"]
    )

    st.plotly_chart(fig_box, use_container_width=True, key="temp_box")

    # ---- Optional insight ----
    st.caption(
        f"Extreme threshold (95th percentile): {extreme_threshold:.2f} °C"
    )

else:
    st.error("temperature_celsius column not found in dataset.")

# =========================================================
# SECTION - Temperature Volatility by Country
# =========================================================

st.subheader("Temperature Volatility by Country")

if {"country", "temperature_celsius"}.issubset(df.columns):

    volatility_df = (
        df.groupby("country")["temperature_celsius"]
        .agg(["mean", "std"])
        .reset_index()
    )

    volatility_df["volatility"] = (
        volatility_df["std"] / volatility_df["mean"]
    )

    volatility_df = volatility_df.replace([np.inf, -np.inf], np.nan).dropna()

    top_volatility = volatility_df.sort_values(
        "volatility", ascending=False
    ).head(15)

    fig_vol = px.bar(
        top_volatility,
        x="country",
        y="volatility",
        title="Top Temperature Volatile Countries"
    )

    st.plotly_chart(fig_vol, use_container_width=True, key="votal_bar")

# =========================================================
# SECTION - Flood Risk Detection
# =========================================================

st.subheader("Flood Risk Detection")

# ---- Detect correct rainfall column automatically ----
rain_col = None
for col in ["precip_mm", "precipitation_mm", "precip"]:
    if col in df.columns:
        rain_col = col
        break

if rain_col:

    # ---- Calculate extreme rainfall threshold ----
    rain_threshold = df[rain_col].quantile(0.95)
    flood_risk = df[df[rain_col] > rain_threshold]

    st.metric("🌊 Potential Flood Risk Events", len(flood_risk))

    st.write(f"Rainfall records used: {df[rain_col].notna().sum()}")

    # ---- Rainfall histogram ----
    fig_rain = px.histogram(
        df,
        x=rain_col,
        nbins=50,
        title="Rainfall Distribution"
    )

    st.plotly_chart(fig_rain, use_container_width=True, key="rain_histogram")

else:
    st.warning("⚠️ Rainfall column not found in dataset")

# =========================================================
# SECTION — Wind Speed Distribution
# =========================================================

st.subheader("💨 Wind Speed Distribution (Weibull Approx)")

if "wind_kph" in df.columns:

    wind = df["wind_kph"].dropna()

    shape = (wind.mean() / wind.std()) ** 1.086
    scale = wind.mean()

    st.write(f"Estimated Weibull Shape: {shape:.2f}")
    st.write(f"Estimated Weibull Scale: {scale:.2f}")

    fig_wind = px.histogram(
        wind,
        nbins=50,
        title="Wind Speed Distribution"
    )

    st.plotly_chart(fig_wind, use_container_width=True, key="wind_weibull")

# =========================================================
# SECTION - Latitude vs Temperature Gradient
# =========================================================

st.subheader("🌍 Latitude vs Temperature Gradient")

lat_col = "latitude"  # ← change if your name differs

if lat_col in df.columns:

    lat_temp = (
        df.groupby(lat_col)["temperature_celsius"]
        .mean()
        .reset_index()
    )

    fig_lat = px.scatter(
        lat_temp,
        x=lat_col,
        y="temperature_celsius",
        trendline="ols",
        title="Latitude vs Average Temperature"
    )

    st.plotly_chart(
        fig_lat,
        use_container_width=True,
        key="lat_temp_gradient"
    )
else:
    st.warning("Latitude column not found.")

# =========================================================
# SECTION — Country Temperature Volatility
# =========================================================

st.subheader("Temperature Volatility by Country")

if "country" in df.columns:

    country_stats = (
        df.groupby("country")["temperature_celsius"]
        .agg(["mean", "std"])
        .reset_index()
    )

    country_stats["volatility"] = (
        country_stats["std"] / country_stats["mean"]
    )

    top_vol = country_stats.sort_values(
        by="volatility", ascending=False
    ).head(15)

    fig_vol = px.bar(
        top_vol,
        x="country",
        y="volatility",
        title="Top Volatile Countries"
    )

    st.plotly_chart(fig_vol, use_container_width=True,key="volatility_bar_chart")


else:
    st.warning("Country column not found")

st.subheader("📊 Volatility vs Climate Factors")

vol_df = (
    df.groupby("country")["temperature_celsius"]
    .std()
    .reset_index(name="temp_volatility")
)

climate_avg = (
    df.groupby("country")[["humidity", "wind_kph"]]
    .mean()
    .reset_index()
)

merged_vol = vol_df.merge(climate_avg, on="country")

corr_vol = merged_vol.corr(numeric_only=True)

fig_vol_corr = px.imshow(
    corr_vol,
    text_auto=True,
    title="Correlation: Temperature Volatility vs Climate Factors"
)

st.plotly_chart(
    fig_vol_corr,
    use_container_width=True,
    key="volatility_correlation"
)

# =========================================================
# FOOTER
# =========================================================

st.markdown("---")
st.caption("ClimateScope Analytics • Milestone 2")

