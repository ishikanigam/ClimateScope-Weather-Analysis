import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
# -------------------------------------------
# Page config (single call)
# -------------------------------------------

st.set_page_config(
    page_title="ClimateScope Weather Analytics",
    page_icon="🌍",
    layout="wide",
)

st.title("ClimateScope Weather Analytics Dashboard")

st.markdown("""
<style>
.big-font {
    font-size:20px !important;
    font-weight:600;
}
</style>
""", unsafe_allow_html=True)

st.markdown("""
This interactive dashboard analyzes **global weather patterns**, temperature trends,
and extreme climate events using real-world weather data.

Use the **filters** to explore climate patterns across countries,
time periods, and seasons. If no filters are applied, the dashboard will show insights based on the entire dataset.
""")

st.divider()

# -------------------------------------------
# Data Load and Preprocessing
# -------------------------------------------

@st.cache_data
def load_data(path="data/weather_final_analysis.csv"):
    df = pd.read_csv(path)
    if "last_updated" in df.columns:
        df["last_updated"] = pd.to_datetime(df["last_updated"], errors="coerce")
        df["month"] = df["last_updated"].dt.month

        season_map = {
            12: "Winter", 1: "Winter", 2: "Winter",
            3: "Summer", 4: "Summer", 5: "Summer",
            6: "Monsoon", 7: "Monsoon", 8: "Monsoon", 9: "Monsoon",
            10: "Post-Monsoon", 11: "Post-Monsoon"
        }

        df["season"] = df["month"].map(season_map).fillna("Unknown")

    return df


@st.cache_data
def detect_rain_col(df):
    for col in ["precip_mm", "precipitation_mm", "precip"]:
        if col in df.columns:
            return col
    return None


@st.cache_data
def compute_country_vol(df):
    if {"country", "temperature_celsius"}.issubset(df.columns):
        vol = (
            df.groupby("country")["temperature_celsius"]
            .agg(["mean", "std"])
            .reset_index()
        )
        vol["volatility"] = vol["std"] / vol["mean"].replace(0, np.nan)
        return vol.replace([np.inf, -np.inf], np.nan).dropna(subset=["volatility"])
    return pd.DataFrame()


with st.spinner("Loading climate dataset..."):
    df = load_data()

if df.empty:
    st.error("No data loaded from `data/weather_cleaned.csv`.")
df.columns = df.columns.str.lower().str.strip()

df = df.rename(columns={
    "temperature_c": "temperature_celsius",
    "temp_c": "temperature_celsius",
    "temp": "temperature_celsius",
    "country_name": "country",
    "datetime": "last_updated",
    "date": "last_updated"
})

rain_col = detect_rain_col(df)

# -------------------------------------------
# Sidebar filters
# -------------------------------------------

st.sidebar.header("🔧 ClimateScope Controls")

st.sidebar.write("**Dataset Overview**")
st.sidebar.write(f"Total Records: {len(df):,} / {df['country'].nunique()} Countries")
if "last_updated" in df.columns:
    st.sidebar.write(f"Date Range: {df['last_updated'].min().date()} → {df['last_updated'].max().date()}")

st.sidebar.markdown("---")

# Reintroduce some core sidebar filters
countries = sorted(df["country"].dropna().unique())

selected_countries = st.sidebar.multiselect(
    "📍 Select Countries",
    options=countries,
    default=[],
    help="Select one or more countries to filter the dashboard."
)

st.sidebar.markdown("### 🎯 Active Filters")

if selected_countries:
    st.sidebar.write(f"Countries: {', '.join(selected_countries)}")
else:
    st.sidebar.write("Countries: All")

date_range_sidebar = st.sidebar.date_input(
    "📅 Date Range",
    value=(df["last_updated"].min().date(), df["last_updated"].max().date()) if "last_updated" in df.columns else (None, None),
    min_value=df["last_updated"].min().date() if "last_updated" in df.columns else None,
    max_value=df["last_updated"].max().date() if "last_updated" in df.columns else None,
    help="Optional date filter for all visualizations.",
)

st.sidebar.markdown("---")

# Apply global filters for baseline dataset
filtered_df = df.copy()
if selected_countries:
    filtered_df = filtered_df[filtered_df["country"].isin(selected_countries)]

if isinstance(date_range_sidebar, (list, tuple)) and len(date_range_sidebar) == 2 and "last_updated" in df.columns:
    start_date, end_date = date_range_sidebar
    if start_date and end_date:
        filtered_df = filtered_df[(filtered_df["last_updated"] >= pd.to_datetime(start_date)) & (filtered_df["last_updated"] <= pd.to_datetime(end_date))]

# Final working frame
df = filtered_df.copy()
# ---------------------------
# CRITICAL DATA FIX
# ---------------------------
df = df.dropna(subset=["country", "temperature_celsius", "last_updated"])

# Ensure datetime is proper
df["last_updated"] = pd.to_datetime(df["last_updated"], errors="coerce")
df = df.dropna(subset=["last_updated"])

volatility_df = compute_country_vol(df)

st.success("✅ Data loaded successfully")

# -------------------------------------------
# Dashboard Layout Tabs
# -------------------------------------------

tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "Executive Overview",
    "Temperature Intelligence",
    "Climate Relationships",
    "Extreme Event Analysis",
    "Geographic Insights",
    "Decision Intelligence - Application"
])

with tab1:
    # -------------------------------------------
    # KPI METRICS
    # -------------------------------------------
    st.subheader("📊 Key Climate Indicators")

    kpi_cols = st.columns(3)

    kpi_cols[0].metric(
        "🌡 Avg Temperature",
        f"{df['temperature_celsius'].mean():.2f} °C",
    )

    if "humidity" in df.columns:
        kpi_cols[1].metric(
            "💧 Avg Humidity",
            f"{df['humidity'].mean():.2f} %",
        )
    else:
        kpi_cols[1].write("No humidity data.")

    if rain_col:
        kpi_cols[2].metric(
            "🌧 Total Rainfall",
            f"{df[rain_col].sum():.0f} mm",
        )
    else:
        kpi_cols[2].write("No rainfall data.")

    st.subheader("🔎 Key Climate Insights")

    c1, c2, c3 = st.columns(3)

    with c1:
        if "country" in df.columns:
            hottest_country = (
                df.groupby("country")["temperature_celsius"]
                .mean()
                .idxmax()
            )
            st.info(f"🔥 Hottest Country: {hottest_country}")
        else:
            st.warning("No country column for hottest country insight.")

    with c2:
        if rain_col and "country" in df.columns:
            wettest_country = (
                df.groupby("country")[rain_col]
                .mean()
                .idxmax()
            )
            st.info(f"🌧 Wettest Country: {wettest_country}")
        else:
            st.warning("Rainfall country insight not available.")

    with c3:
        if not volatility_df.empty:
            most_volatile = volatility_df.sort_values(
                "volatility", ascending=False
            )["country"].iloc[0]
            st.info(f"📊 Most Temperature Volatile: {most_volatile}")
        else:
            st.warning("Volatility data not available.")

    st.subheader("Climate Risk Indicators")

    r1, r2, r3 = st.columns(3)

    heatwaves = df[df["temperature_celsius"] > 35].shape[0] if "temperature_celsius" in df.columns else 0
    if rain_col:
        rain_series = pd.to_numeric(df[rain_col], errors="coerce")
        rain_threshold = rain_series.quantile(0.95)
        flood_events = rain_series[rain_series > rain_threshold].shape[0]
    else:
        flood_events = 0
    high_wind = df[df.get("wind_kph", pd.Series([])) > 40].shape[0] if "wind_kph" in df.columns else 0

    r1.metric("Heatwave Events", heatwaves)
    r2.metric("Flood Risk Events", flood_events)
    r3.metric("High Wind Events", high_wind)

    with st.expander("📊 Insight"):
     st.write(
        "These key performance indicators provide a snapshot of the overall climate conditions in the dataset, "
        "including average temperature, humidity levels, and rainfall intensity. "
        "Temperature indicates general warmth/coldness, humidity shows moisture content affecting comfort, "
        "and rainfall measures precipitation which impacts agriculture and water resources. "
        "These metrics help identify dominant climate patterns and potential environmental challenges."
    )

    # -------------------------------------------
    # Country climate comparison chart
    # -------------------------------------------

    st.subheader("Country Climate Comparison")
    
    # Local filters
    comp_metric = st.selectbox(
        "Select Climate Metric",
        [m for m in ["temperature_celsius", "humidity", rain_col or "precip_mm", "wind_kph"] if m in df.columns],
        key="comp_metric"
    )
    comparison_df = df
    
    comparison = (
        comparison_df.groupby("country")[comp_metric].mean().reset_index()
    )
    fig_compare = px.bar(
        comparison,
        x="country",
        y=comp_metric,
        title=f"{comp_metric.replace('_', ' ').title()} Comparison Across Countries",
    )
    fig_compare.update_layout(height=500)
    st.plotly_chart(fig_compare, use_container_width=True)
    with st.expander("📊 Insight"):
     st.write(
        f"This chart compares the average {comp_metric.replace('_', ' ')} across selected countries. "
        "Higher values indicate regions with more intense conditions for this metric. "
        "Use the filters to customize the comparison and gain insights into regional climate patterns. "
        "For example, comparing temperature can reveal equatorial vs polar differences, "
        "while humidity comparison shows arid vs tropical zones."
    )
        
    # -------------------------------------------
    # Temperature Volatility by Country
    # -------------------------------------------

    st.subheader("Temperature Volatility by Country")

    # Local filter
    country_stats = (
        df.groupby("country")["temperature_celsius"]
        .agg(["mean", "std"])
        .reset_index()
    )

    country_stats["volatility"] = country_stats["std"] / country_stats["mean"].replace(0, np.nan)

    top_vol = country_stats.sort_values("volatility", ascending=False).head(15)

    fig_vol = px.bar(
        top_vol,
        x="country",
        y="volatility",
        title="Top Volatile Countries",
        labels={"volatility": "Temperature Volatility"},
    )
    fig_vol.update_layout(height=450, margin=dict(t=40, b=30, l=30, r=30))
    st.plotly_chart(fig_vol, use_container_width=True, key="temperature_volatility_bar")
    with st.expander("📊 Insight"):
        st.write(
        "Temperature volatility measures how much temperatures fluctuate around the mean. "
        "Countries with higher volatility experience more variable weather, which can indicate "
        "unstable climate patterns, seasonal extremes, or proximity to weather fronts. "
        "High volatility may suggest challenges for agriculture, energy planning, and daily activities. "
        "Use the filter to analyze specific countries of interest."
    )

    #----------------------------------------
    # Climate Insights Summary
    #----------------------------------------

    st.subheader("Climate Insights")
    if "country" in df.columns and "temperature_celsius" in df.columns:
        hottest_country2 = df.groupby("country")["temperature_celsius"].mean().idxmax()
        st.info(f"Hottest Country: {hottest_country2}")
    if rain_col and "country" in df.columns:
        wettest_country2 = df.groupby("country")[rain_col].mean().idxmax()
        st.info(f"Wettest Country: {wettest_country2}")
    if "country" in df.columns and "wind_kph" in df.columns:
        most_windy = df.groupby("country")["wind_kph"].mean().idxmax()
        st.info(f"Most Windy Country: {most_windy}")


    # -------------------------------------------
    # Data Tables for key insights
    # -------------------------------------------

    st.subheader("📋 Key Data Tables")

    # 1) country summary (temp/humidity/rain intensity/wind)
    table_cols = ["country"]
    if "temperature_celsius" in df.columns:
        table_cols.append("temperature_celsius")
    if "humidity" in df.columns:
        table_cols.append("humidity")
    if rain_col:
        table_cols.append(rain_col)
    if "wind_kph" in df.columns:
        table_cols.append("wind_kph")

    if len(table_cols) > 1:
        country_summary = (
            df.groupby("country")[table_cols[1:]]
            .mean()
            .reset_index()
            .sort_values("temperature_celsius", ascending=False if "temperature_celsius" in table_cols else True)
        )
        st.write("🌍 Country-level Lively Summary")
        st.dataframe(country_summary.head(20), use_container_width=True)
        with st.expander("📊 Insight"):
         st.write(
           "Countries at the top show higher average temperatures, indicating warmer climates. "
           "Compare humidity and rainfall columns to identify tropical vs arid regions. "
           "Higher wind speeds may indicate coastal or storm-prone areas."
        )
    else:
        st.write("No country summary columns available.")

    # 2) extreme events and anomalies
    if "temperature_celsius" in df.columns:
        extreme_temp_df = df[df["temperature_celsius"] > df["temperature_celsius"].quantile(0.95)]
        st.write("Extreme Temperature Events (95th percentile)")
        st.dataframe(
            extreme_temp_df[["country", "last_updated", "temperature_celsius", "condition_text"]]
            .sort_values("temperature_celsius", ascending=False)
            .head(30),
            use_container_width=True,
        )
        with st.expander("📊 Insight"):
         st.write(
           "These are the most extreme heat events (top 5%). "
           "Frequent appearance of certain countries indicates recurring heatwaves, "
           "which may signal climate change impact or regional vulnerability."
        )

    if rain_col:
        extreme_rain_df = df[df[rain_col] > df[rain_col].quantile(0.95)]
        st.write("Extreme Rainfall Events (95th percentile)")
        st.dataframe(
            extreme_rain_df[["country", "last_updated", rain_col, "condition_text"]]
            .sort_values(rain_col, ascending=False)
            .head(30),
            use_container_width=True,
        )
        with st.expander("📊 Insight"):
         st.write(
            "These records represent unusually high rainfall events. "
            "Clusters in specific countries may indicate flood-prone regions or monsoon effects."
        )

    with st.expander("📊 Overall Table Insight"):
     st.write(
        "The tables provides a summarized view of climate statistics by country, "
        "allowing deeper exploration of the dataset beyond visual charts."
     )

    # -------------------------------------------
    # Interactive climate story insights
    # -------------------------------------------

    st.header("Interactive Climate Story Insights")
    avg_temp = df["temperature_celsius"].mean() if "temperature_celsius" in df.columns else np.nan

    hottest_country3 = df.groupby("country")["temperature_celsius"].mean().idxmax() if "country" in df.columns and "temperature_celsius" in df.columns else "N/A"
    coldest_country = df.groupby("country")["temperature_celsius"].mean().idxmin() if "country" in df.columns and "temperature_celsius" in df.columns else "N/A"
    wettest_country3 = df.groupby("country")[rain_col].mean().idxmax() if rain_col and "country" in df.columns else "N/A"
    most_humid = df.groupby("country")["humidity"].mean().idxmax() if "humidity" in df.columns and "country" in df.columns else "N/A"
    most_windy2 = df.groupby("country")["wind_kph"].mean().idxmax() if "wind_kph" in df.columns and "country" in df.columns else "N/A"

    st.subheader("Key Climate Insights")
    st.success(f"🌡 Average Temperature across selected data: {avg_temp:.2f} °C")
    st.info(f"🔥 Hottest Country: {hottest_country3}")
    st.info(f"❄ Coldest Country: {coldest_country}")
    st.info(f"🌧 Wettest Country: {wettest_country3}")
    st.info(f"💧 Most Humid Country: {most_humid}")
    st.info(f"💨 Windiest Country: {most_windy2}")

    st.subheader("Climate Story")
    st.write(
        f"""
    The selected climate data shows an average temperature of **{avg_temp:.2f}°C**.
    The **hottest region** currently observed is **{hottest_country3}**, while the
    **coldest region** is **{coldest_country}**.

    Rainfall analysis indicates that **{wettest_country3}** receives the most precipitation.
    Humidity levels are highest in **{most_humid}**, and the strongest wind activity
    is observed in **{most_windy2}**.

    These insights help identify climate variability and potential extreme weather risks.
    """
    )

with tab2:
    # -------------------------------------------
    # Temperature Distribution
    # -------------------------------------------

    # --- Filters for tab2 ---
    st.subheader("Temperature Distribution")

    temp_dist_seasons = st.multiselect(
        "Filter by season (leave empty for all):",
        options=sorted(df["season"].dropna().unique()),
        default=[],
        key="tab2_tempdist_seasons"
    )
    temp_dist_df = df
    if temp_dist_seasons:
        temp_dist_df = temp_dist_df[temp_dist_df["season"].isin(temp_dist_seasons)]
    fig_hist = px.histogram(
        temp_dist_df,
        x="temperature_celsius",
        nbins=50,
        title="Temperature Distribution",
        labels={"temperature_celsius": "Temperature (°C)"},
    )
    fig_hist.update_layout(height=450)
    st.plotly_chart(fig_hist, use_container_width=True, key="temperature_hist")
    with st.expander("📊 Insight"):
        st.write(
            "This histogram shows the frequency distribution of temperature values for the selected countries/seasons. "
            "A narrow peak suggests consistent temperatures, while a wide spread indicates high variability. "
            "Extreme values in the tails represent heatwaves or cold snaps. Filtering helps assess climate stability and risks for specific regions or times."
        )

    st.subheader("Season Distribution")

    pie_df = df[df["season"].notna()] if "season" in df.columns else df
    season_counts = pie_df["season"].fillna("Unknown").value_counts()
    fig_pie = px.pie(
        names=season_counts.index,
        values=season_counts.values,
        title="Weather Records by Season",
    )
    st.plotly_chart(fig_pie, use_container_width=True, key="season_pie")
    with st.expander("📊 Insight"):
        st.write(
            "This pie chart shows how weather observations are distributed across seasons for the selected countries. "
            "A higher proportion of one season may indicate seasonal bias in data collection, or reflect actual climate patterns. "
            "Balanced distribution indicates comprehensive seasonal coverage, while imbalance could affect the reliability of seasonal climate analysis."
        )

    # -------------------------------------------
    # Temperature Trend Over Time
    # -------------------------------------------

    st.subheader("Temperature Trend Over Time")

    trend_df = df[df["temperature_celsius"].notna() & df["last_updated"].notna()]
    if "country" in trend_df.columns and "temperature_celsius" in trend_df.columns:
        trend_df["temp_roll_7"] = (
            trend_df.groupby("country")["temperature_celsius"]
            .rolling(7, min_periods=1)
            .mean()
            .reset_index(level=0, drop=True)
        )
        fig_roll = px.line(
            trend_df,
            x="last_updated",
            y="temp_roll_7",
            color="country",
            title="7-Day Rolling Average Temperature",
            labels={"temp_roll_7": "7-day roll avg (°C)"},
        )
        fig_roll.update_layout(height=450)
        st.plotly_chart(fig_roll, use_container_width=True)
        with st.expander("📊 Insight"):
         st.write(
            "7-day rolling averages smooth daily fluctuations to reveal underlying temperature trends. "
            "This technique filters out short-term weather noise to show longer-term patterns, "
            "making it easier to identify warming or cooling trends, seasonal cycles, and climate shifts. "
            "Different colored lines for each country allow comparison of regional temperature evolution."
        )

    st.subheader("Average Daily Temperature Trend")

    avgtrend_df = df[df["temperature_celsius"].notna() & df["last_updated"].notna()]
    if "last_updated" in avgtrend_df.columns and "temperature_celsius" in avgtrend_df.columns:
        temp_time = (
            avgtrend_df.groupby(pd.Grouper(key="last_updated", freq="D"))["temperature_celsius"]
            .mean()
            .reset_index()
        )
        fig_time = px.line(
            temp_time,
            x="last_updated",
            y="temperature_celsius",
            title="Average Daily Temperature Trend",
            labels={"temperature_celsius": "Temperature (°C)"},
        )
        fig_time.update_layout(height=450)
        st.plotly_chart(fig_time, use_container_width=True, key="temperature_time_trend")
        with st.expander("📊 Insight"):
         st.write(
            "This time series shows how average daily temperatures evolve for the selected countries. "
            "Upward trends indicate warming, downward suggest cooling. Seasonal patterns appear as "
            "regular oscillations. Breaks or anomalies in the pattern may indicate extreme weather events "
            "or data gaps. This visualization is crucial for understanding long-term climate change "
            "and planning adaptation strategies."
        )
    else:
        st.warning("Time-series columns missing for average temperature trend.")

    # -------------------------------------------
    # Seasonal Temperature Pattern
    # -------------------------------------------

    st.header("Seasonal Temperature Pattern")

    season_pattern_df = df[df["temperature_celsius"].notna() & df["season"].notna()]
    if "season" in season_pattern_df.columns and "temperature_celsius" in season_pattern_df.columns:
        seasonal_temp = (
            season_pattern_df.groupby("season")["temperature_celsius"]
            .mean()
            .reset_index()
        )
        if len(seasonal_temp):
            fig_season = px.bar(
                seasonal_temp,
                x="season",
                y="temperature_celsius",
                title="Average Temperature by Season",
                labels={"temperature_celsius": "Temp (°C)"},
            )
            fig_season.update_layout(height=450)
            st.plotly_chart(fig_season, use_container_width=True, key="seasonal_bar")
            with st.expander("📊 Insight"):
             st.write(
                "Average temperature varies across seasons due to changes in solar radiation and weather patterns. "
                "Winter typically shows lowest temperatures due to reduced sunlight, while summer peaks. "
                "Monsoon and post-monsoon seasons may show different patterns based on regional rainfall. "
                "Understanding seasonal variation helps in agricultural planning, energy demand forecasting, "
                "and preparing for seasonal climate challenges."
           )
        else:
            st.warning("No seasonal data available.")
    else:
        st.warning("Season or temperature column missing.")

    #-----------------------------------------------
    #country-wise temperature distribution boxplot
    #-----------------------------------------------
    
    if "country" in df.columns and "temperature_celsius" in df.columns and "last_updated" in df.columns:
     st.subheader("Country Temperature Boxplot")
     
     # Local filter

     metric_for_box = st.selectbox(
        "Select metric for country-wise distribution",
        options=["temperature_celsius"] + (["humidity"] if "humidity" in df.columns else []),
        index=0,
        key="box_metric_selector"
     )

    box_df = df[["country", metric_for_box, "last_updated"]].dropna()
    fig_box2 = px.box(
        box_df,
        x="country",
        y=metric_for_box,
        color="country",
        title=f"{metric_for_box.replace('_', ' ').title()} Distribution by Country",
    )
    fig_box2.update_layout(height=350, showlegend=False)
    st.plotly_chart(fig_box2, use_container_width=True, key="country_boxplot")
    with st.expander("📊 Insight"):
     st.write(
        "This box plot visualizes the distribution of temperature values across countries. "
        "The box represents the interquartile range (middle 50% of values), the line inside "
        "the box represents the median temperature, and points outside the whiskers represent "
        "outliers. Countries with wider boxes indicate higher variability in temperature. "
        "Outliers may indicate extreme weather events. Use the filters to compare specific countries "
        "and understand regional climate stability."
     )

with tab3:
    #-------------------------------------------
    # Correlation heatmaps
    # -------------------------------------------
    st.subheader("Correlation Heatmap")
    
    important_cols = [
    "temperature_celsius",
    "humidity",
    "wind_kph",
    rain_col if rain_col else "precip_mm"
    ]

    # to Keep only available columns
    available_cols = [col for col in important_cols if col in df.columns]

    corr_df = df[available_cols].dropna()

    corr_matrix = corr_df.corr().round(2)
    fig_heat = px.imshow(
        corr_matrix,
        text_auto=True,   # shows r values
        color_continuous_scale="RdBu_r",
        zmin=-1,
        zmax=1,
        title="Correlation Matrix (Key Climate Variables)"
    )

    fig_heat.update_layout(height=500)

    st.plotly_chart(fig_heat, use_container_width=True)
    with st.expander("📊 Insight"):
        st.write(
            "Correlation heatmaps reveal how climate variables move together across selected data. "
            "This helps quantify whether factors like temperature, humidity, and precipitation are strongly linked, "
            "which is useful for risk modeling and identifying dependencies in climate systems."
            " Correlation coefficient (r) ranges from -1 to +1\n"
            "• r > 0 → Positive relationship\n"
            "• r < 0 → Negative relationship\n"
            "• r ≈ 0 → No relationship\n\n"
            " Strong correlations (|r| > 0.6) are most important."
        )

    # -------------------------------------------
    #  Seasonal Correlation Heatmap 
    # -------------------------------------------

    st.subheader(" Seasonal Correlation Heatmap")

    if "season" in df.columns:

        # 🔘 Step 1: Toggle (Enable / Disable)
        show_seasonal = st.checkbox("Enable Seasonal Heatmap")

        if show_seasonal:

            #  Step 2: Important columns only
            important_cols = [
                "temperature_celsius",
                "humidity",
                "wind_kph",
                "uv",
                rain_col
            ]

            available_cols = [col for col in important_cols if col in df.columns]

            # 🎛 Step 3: Select seasons
            season_options = sorted(df["season"].dropna().unique())

            selected_seasons = st.multiselect(
                "Select season(s):",
                options=season_options,
                default=[season_options[0]],   # default one season
                key="season_corr_filter"
            )

            #  step 4: If nothing selected
            if not selected_seasons:
                st.warning("Please select at least one season.")

            #  Step 5: Generate heatmap for each selected season
            for season in selected_seasons:

                st.markdown(f"### 🌦 Season: {season}")

                season_df = df[df["season"] == season][available_cols].dropna()

                if season_df.empty:
                    st.warning(f"No data available for {season}")
                    continue

                corr = season_df.corr().round(2)

                fig_season_corr = px.imshow(
                    corr,
                    text_auto=True,   # 🔥 shows r values
                    color_continuous_scale="RdBu_r",
                    zmin=-1,
                    zmax=1,
                    title=f"Correlation Matrix — {season}"
                )

                fig_season_corr.update_layout(height=450)

                st.plotly_chart(fig_season_corr, use_container_width=True)

                # 📊 Insight
                with st.expander(f"📊 Insight for {season}"):
                    st.write(
                        f"""
                    This heatmap shows how climate variables interact during **{season}**.

                    • Positive values (closer to +1) → variables increase together  
                    • Negative values (closer to -1) → inverse relationship  
                    • Values near 0 → weak or no relationship  

                    Strong correlations (|r| > 0.6) are most important for seasonal climate behavior.
                    """
                    )

    else:
        st.warning("Season column not available in dataset.")

    # -------------------------------------------
    # Humidity vs Precipitation
    # -------------------------------------------

    st.subheader("Humidity vs Precipitation")
    if {"humidity", rain_col}.issubset(df.columns):
        hum_min, hum_max = st.slider(
            "Humidity range for plot", 0, 100, (0, 100), key="hum_prec_range"
        )
        prec_min, prec_max = st.slider(
            "Rainfall range for plot", 0, int(df[rain_col].max() if rain_col and rain_col in df.columns else 100),
            (0, int(df[rain_col].quantile(0.95) if rain_col and rain_col in df.columns else 100)),
            key="prec_range"
        )

        scatter_df = df[(df["humidity"] >= hum_min) & (df["humidity"] <= hum_max) & (df[rain_col] >= prec_min) & (df[rain_col] <= prec_max)].dropna(subset=["humidity", rain_col])

        fig_scatter = px.scatter(
            scatter_df,
            x="humidity",
            y=rain_col,
            title="Humidity vs Precipitation",
            opacity=0.6,
        )
        fig_scatter.update_layout(height=450)
        st.plotly_chart(fig_scatter, use_container_width=True, key="hum_prec_scatter")
        with st.expander("📊 Insight"):
         st.write(
           "Higher humidity often leads to increased precipitation because moisture-rich air promotes rainfall. "
           "This scatter reveals how strong humidity values correspond to rain intensity and highlights non-linear behavior in wet vs dry climates."
        )
    else:
        st.warning("Humidity vs precipitation chart requires both columns.")

    #-------------------------------------------
    # Bubble chart for temp vs humidity vs wind
    #-------------------------------------------

    if {"temperature_celsius", "humidity", "wind_kph"}.issubset(df.columns):
        st.subheader("Bubble Chart: Temperature vs Humidity vs Wind")

        bubble_limit = st.slider(
            "Max points to display (speed/load):",
            100, min(5000, len(df)), min(1000, len(df)),
            step=100,
            key="bubble_n"
        )

        bubble_df = df[["temperature_celsius", "humidity", "wind_kph", "country"]].dropna().head(bubble_limit)

        fig_bubble = px.scatter(
            bubble_df,
            x="humidity",
            y="temperature_celsius",
            size="wind_kph",
            color="country" if "country" in bubble_df.columns else None,
            hover_name="country" if "country" in bubble_df.columns else None,
            title="Temperature vs Humidity with Wind Intensity",
            labels={"humidity": "Humidity (%)", "temperature_celsius": "Temperature (°C)", "wind_kph": "Wind Speed (kph)"},
            opacity=0.7,
        )
        fig_bubble.update_layout(height=520)
        st.plotly_chart(fig_bubble, use_container_width=True, key="bubble_hum_temp_wind")
        with st.expander("📊 Insight"):
         st.write(
            "Bubble size represents wind speed, allowing simultaneous analysis of temperature, humidity, and wind intensity. "
            "Use country and point-limit filters to keep chart responsive while focusing on target regions and conditions."
         )

    # -------------------------------------------
    # Country comparison radar chart
    # -------------------------------------------

    st.subheader("Country Climate Comparison Radar")

    radar_df = df
    
    radar_metrics = ["temperature_celsius", "humidity", rain_col if rain_col else "precip_mm", "wind_kph"]

    if {"country"}.issubset(df.columns) and radar_metrics:
        radar_data = radar_df.groupby("country")[radar_metrics].mean()
        fig_radar = go.Figure()
        for country in radar_data.index:
            fig_radar.add_trace(
                go.Scatterpolar(
                    r=radar_data.loc[country].values,
                    theta=radar_data.columns,
                    fill="toself",
                    name=country,
                )
            )
        fig_radar.update_layout(polar=dict(radialaxis=dict(visible=True)), showlegend=True, height=600)
        st.plotly_chart(fig_radar, use_container_width=True)
        with st.expander("📊 Insight"):
         st.write(
            "Radar charts provide a holistic view of multiple climate variables for each country. "
            "The shape of each country's polygon indicates its climate profile - for example, "
            "a country with high values across all metrics would have a large polygon, "
            "while one with balanced values would be more circular. This helps identify "
            "countries with extreme conditions in specific areas (e.g., very rainy but cool) "
            "versus those with moderate all-around climates."
        )
    else:
        st.warning("Radar chart cannot be created - missing data.")

with tab4:
    #-------------------------------------------
    # volatility vs climate factors correlation
    #-------------------------------------------

    st.subheader("Volatility vs Climate Factors")

    vol_n = st.slider("Show top N countries by temperature volatility", 5, 30, 15, key="vol_topn")

    vol_df = df[["country", "temperature_celsius", "humidity", "wind_kph"]].dropna() if {"country", "temperature_celsius", "humidity", "wind_kph"}.issubset(df.columns) else df
    if {"country", "temperature_celsius", "humidity", "wind_kph"}.issubset(vol_df.columns):
        vol_std = vol_df.groupby("country")["temperature_celsius"].std().reset_index(name="temp_volatility")
        climate_avg = vol_df.groupby("country")[["humidity", "wind_kph"]].mean().reset_index()
        merged_vol = vol_std.merge(climate_avg, on="country")

        merged_vol = merged_vol.sort_values("temp_volatility", ascending=False).head(vol_n)

        corr_vol = merged_vol.corr(numeric_only=True)
        fig_vol_corr = px.imshow(corr_vol, text_auto=True, title="Correlation: Temperature Volatility vs Climate Factors")
        fig_vol_corr.update_layout(height=450)
        st.plotly_chart(fig_vol_corr, use_container_width=True, key="volatility_correlation")
        with st.expander("📊 Insight"):
         st.write(
            "This heatmap shows the relationship between temperature volatility and other climate factors in selected countries. "
            "Positive correlations imply that as temperature variability increases, humidity or wind may also rise; "
            "negative correlations suggest potential compensation effects. Use top-N filtering to isolate the most unstable regions."
        )
    else:
        st.warning("Not enough columns for volatility correlation analysis.")

    # -------------------------------------------
    # Extreme Temperature Events
    # -------------------------------------------

    st.header("Extreme Temperature Events")
    st.subheader("Temperature Anomaly Detection")

    if "temperature_celsius" in df.columns:
        mean_temp = df["temperature_celsius"].mean()
        std_temp = df["temperature_celsius"].std()
        df["temp_anomaly"] = (df["temperature_celsius"] - mean_temp) / std_temp

        anomaly_threshold = st.slider(
            "Anomaly sigma threshold", 1.5, 4.0, 2.0, 0.1, key="anomaly_sigma"
        )
        anomalies = df[abs(df["temp_anomaly"]) > anomaly_threshold]

        fig_anomaly = px.scatter(
            anomalies,
            x="last_updated",
            y="temperature_celsius",
            color="country",
            title="Temperature Anomalies Over Time",
        )
        fig_anomaly.update_layout(height=450)
        st.plotly_chart(fig_anomaly)
        with st.expander("📊 Insight"):
         st.write(
            "Anomalies represent temperature values significantly different from the historical mean. "
            "Adjust the sigma threshold to highlight larger deviations and identify extreme heat/cold events. "
            "Plotting only anomalies helps decision-makers focus on critical climate risk occurrences."
        )
    else:
        st.warning("No temperature data for anomaly detection.")

    if "temperature_celsius" in df.columns:
        temp_series = df["temperature_celsius"].dropna()
        extreme_threshold = temp_series.quantile(0.95)
        extreme_events = temp_series[temp_series > extreme_threshold]
        st.metric("🔥 Extreme Temperature Events", len(extreme_events))

    st.subheader("Extreme Temperature Event Timeline")
    extreme_df = df[df["temperature_celsius"] > 35] if "temperature_celsius" in df.columns else df.iloc[0:0]
    fig_extreme = px.scatter(
        extreme_df,
        x="last_updated",
        y="temperature_celsius",
        color="country",
        title="Extreme Temperature Events Over Time",
    )
    fig_extreme.update_layout(height=450)
    st.plotly_chart(fig_extreme)
    with st.expander("📊 Insight"):
        st.write(
            "This timeline scatter plot marks extreme temperature events (above 35°C) over time, colored by country. "
            "Clusters indicate heatwave periods, while sparse points show isolated events. "
            "Tracking these helps identify trends in extreme weather frequency and intensity, crucial for climate adaptation planning."
        )

    # -------------------------------------------
    # Flood Risk Detection
    # -------------------------------------------

    st.subheader("Flood Risk Detection")
    if rain_col:
        rain_threshold = df[rain_col].quantile(0.95)
        flood_risk = df[df[rain_col] > rain_threshold]
        st.metric("Potential Flood Risk Events", len(flood_risk))
        st.write(f"Rainfall records used: {df[rain_col].notna().sum()}")
        fig_rain = px.histogram(df, x=rain_col, nbins=50, title="Rainfall Distribution")
        fig_rain.update_layout(height=450)
        st.plotly_chart(fig_rain, use_container_width=True, key="rain_histogram")
        with st.expander("📊 Insight"):
         st.write(
            "Flood risk is assessed by identifying rainfall events above the 95th percentile threshold. "
            "The histogram shows most rainfall is low, with a long tail of extreme events. "
            "High counts in the tail indicate regions prone to flooding, helping prioritize infrastructure investments and emergency preparedness."
        )
    else:
        st.warning("Rainfall column not found in dataset")

    # -------------------------------------------
    # Wind Speed Distribution
    # -------------------------------------------

    st.subheader("Wind Speed Distribution (Weibull Approx)")
    if "wind_kph" in df.columns:
        wind = df["wind_kph"].dropna()
        shape = (wind.mean() / wind.std()) ** 1.086 if wind.std() > 0 else np.nan
        scale = wind.mean()
        st.write(f"Estimated Weibull Shape: {shape:.2f}")
        st.write(f"Estimated Weibull Scale: {scale:.2f}")
        fig_wind = px.histogram(wind, nbins=50, title="Wind Speed Distribution")
        fig_wind.update_layout(height=450)
        st.plotly_chart(fig_wind, use_container_width=True, key="wind_weibull")
        with st.expander("📊 Insight"):
         st.write(
            "Wind speed often follows a Weibull distribution, with shape parameter indicating variability and scale parameter the average speed. "
            "A higher shape value suggests more consistent winds, while lower values indicate gusty conditions. "
            "This analysis aids in wind energy potential assessment and storm risk evaluation."
        )
    else:
        st.warning("wind_kph column missing.")

    #---------------------
    # rainfall time series
    #----------------------

    if rain_col and "country" in df.columns and "last_updated" in df.columns:
     st.subheader("Rainfall Time Series by Country")
     rain_country = st.selectbox(
        "Select Country for Rainfall Time-Series",
        options=sorted(df["country"].dropna().unique()),
        index=0,
        key="rain_country_selector"
    )
     country_rain = (
        df[df["country"] == rain_country]
        .groupby(pd.Grouper(key="last_updated", freq="M"))[rain_col]
        .mean()
        .reset_index()
    )
     fig_rain_ts = px.line(
        country_rain,
        x="last_updated",
        y=rain_col,
        title=f"Average Monthly {rain_col} for {rain_country}",
        labels={"last_updated": "Date", rain_col: "Rainfall (mm)"},
    )
     fig_rain_ts.update_layout(height=520)
     st.plotly_chart(fig_rain_ts, use_container_width=True, key="rainfall_timeseries")
     with st.expander("📊 Insight"):
      st.write(
        "This time series displays monthly average rainfall for the selected country, revealing seasonal patterns and trends. "
        "Peaks indicate monsoon or wet seasons, while troughs show dry periods. "
        "Analyzing these cycles helps predict water availability, agricultural planning, and flood risks over time."
     )

with tab5:
    # -------------------------------------------
    # Global Temperature Evolution
    # -------------------------------------------

    st.subheader("Global Temperature Evolution")
    #--------------------------
    # Filter data
    # -------------------------
    
    anim_df = df.copy()
    # -------------------------
    # Safety check
    # -------------------------
    if anim_df.empty:
        st.error("⚠️ No data available for selected date range.")
    else:
        temp_time_anim = (
         anim_df.groupby([
            "country",
            pd.Grouper(key="last_updated", freq="7D")  
        # 🔥 weekly aggregation
         ])["temperature_celsius"]
         .mean()
         .reset_index()
        )   

        temp_time_anim = temp_time_anim.sort_values("last_updated")

        temp_time_anim["last_updated"] = temp_time_anim["last_updated"].astype(str)

        fig_anim = px.choropleth(
            temp_time_anim,
            locations="country",
            locationmode="country names",
            color="temperature_celsius",
            hover_name="country",
            animation_frame="last_updated",
            title="Global Temperature Evolution",
            color_continuous_scale="RdYlBu_r",
        )

        fig_anim.update_layout(height=600)

        with st.spinner("Generating animation..."):
            st.plotly_chart(fig_anim, use_container_width=True)
        with st.expander("📊 Insight"):
            st.write(
            "This animated choropleth map shows how global temperature patterns evolve over time. "
            "Darker colors indicate higher temperatures. Watch for seasonal patterns, "
            "regional warming trends, and how climate change affects different parts of the world. "
            "Use the date range filter to focus on specific time periods for detailed analysis."
        )
         
    # -------------------------------------------
    # Latitude vs Temperature
    # -------------------------------------------
    st.subheader("Latitudinal Temperature Gradient")
    if {"latitude", "temperature_celsius"}.issubset(df.columns):
        sample_df = df.sample(min(5000, len(df)))
        fig_lat = px.scatter(
            sample_df,
            x="latitude",
            y="temperature_celsius",
            title="Temperature vs Latitude",
            opacity=0.6,
            labels={"temperature_celsius": "Temp (°C)"},
        )
        fig_lat.update_layout(height=450)
        st.plotly_chart(fig_lat, use_container_width=True, key="lat_scatter")
        with st.expander("📊 Insight"):
         st.write(
          "Temperature generally decreases as latitude increases due to reduced solar radiation at higher latitudes. "
          "This scatter plot samples data points to show the gradient, with equatorial regions warmer and polar areas cooler. "
          "Outliers may indicate microclimates influenced by altitude or ocean currents."
        )
    else:
        st.warning("Latitude or temperature column missing for scatter.")

    #-------------------------
    # Timezone cloud coverage
    #-------------------------

    st.subheader("Timezone Cloud Coverage")
    if "timezone" in df.columns and "cloud" in df.columns and "country" in df.columns:
        tz_cloud = (
            df.groupby("timezone")["cloud"].mean().reset_index().sort_values("cloud", ascending=False)
        )
        fig_tz_cloud = px.bar(
            tz_cloud.head(20),
            x="timezone",
            y="cloud",
            title="Average Cloud Coverage by Timezone (top 20)",
            labels={"cloud": "Cloud (%)"},
        )
        fig_tz_cloud.update_layout(height=480)
        st.plotly_chart(fig_tz_cloud, use_container_width=True, key="timezone_cloud")
        with st.expander("📊 Insight"):
         st.write(
            "This chart shows the average cloud coverage across different timezones. "
            "Higher cloud values indicate regions with more persistent cloud presence, "
            "which may influence temperature patterns, solar radiation levels, and "
            "precipitation probability. Timezone differences can reveal diurnal or regional cloud patterns."
         )
    else:
        st.info("Timezone and cloud data not available for this analysis.")

    # -------------------------------------------
    # AI insights generator (simple static logic)
    # -------------------------------------------

    st.header("AI Climate Insight Generator")
    temp_mean = df["temperature_celsius"].mean() if "temperature_celsius" in df.columns else np.nan
    temp_std = df["temperature_celsius"].std() if "temperature_celsius" in df.columns else np.nan
    humidity_mean = df.get("humidity", pd.Series([])).mean() if "humidity" in df.columns else np.nan
    rain_mean = df.get(rain_col, pd.Series([])).mean() if rain_col in df.columns else np.nan
    wind_mean = df.get("wind_kph", pd.Series([])).mean() if "wind_kph" in df.columns else np.nan

    insights = []
    if temp_mean > 30:
        insights.append("The dataset indicates generally high temperatures, suggesting warmer climate conditions.")
    if rain_mean > 10:
        insights.append("Rainfall levels are relatively high, which may indicate wetter climate patterns.")
    if humidity_mean > 70:
        insights.append("Humidity levels are elevated, suggesting potentially humid atmospheric conditions.")
    if wind_mean > 20:
        insights.append("Wind speeds are relatively strong in several regions, indicating possible windy climate zones.")
    if temp_std > 8:
        insights.append("Temperature variability is high, suggesting unstable or fluctuating weather conditions.")
    if not insights:
        insights.append("No strong climate insights (all values within expected range).")

    st.subheader("Generated Climate Insights")
    for insight in insights:
        st.write("• " + insight)

    st.subheader("AI Climate Summary")
    st.write(
        f"""
    Based on the selected data, the average temperature is **{temp_mean:.2f}°C**.
    Average humidity is **{humidity_mean:.2f}%**, and rainfall averages **{rain_mean:.2f} mm**.

    The climate conditions suggest patterns of **temperature variability, humidity levels,
    and precipitation trends** that can help understand regional weather behaviour.
    """
    )

    with st.expander("📊 Insight"):
     st.write(
        "The AI insight generator summarizes key climate indicators using statistical "
        "thresholds derived from the dataset. It evaluates temperature variability, "
        "humidity levels, rainfall intensity, and wind speed patterns to identify "
        "possible climate conditions such as warm climates, humid regions, or areas "
        "with strong wind activity."
     )

with tab6:
 # -------------------------------------------
   # Climate Decision Intelligence System
   # -------------------------------------------

    st.header("🧠 Climate Decision Intelligence System")

    st.markdown("""
    ### Urban Activity Planning  
    This system helps users decide whether activities like travel, commuting, or outdoor events are safe based on climate conditions.
    """)

    st.markdown("---")

    # -------------------------
    # USER INPUTS
    # -------------------------
    col1, col2, col3 = st.columns(3)

    with col1:
        selected_country = st.selectbox(
            "🌍 Select Country",
            sorted(df["country"].dropna().unique())
        )

    with col2:
        risk_tolerance = st.selectbox(
            "⚙️ Risk Tolerance",
            ["Low (Very Safe)", "Medium (Balanced)", "High (Risk Acceptable)"]
        )

    with col3:
        activity = st.selectbox(
            "🎯 Select Activity",
            ["Travel", "Outdoor Sports", "Daily Commute", "Event Planning"]
        )
        
    country_df = df[df["country"] == selected_country]

    # -------------------------
    # METRICS
    # -------------------------
    avg_temp = country_df["temperature_celsius"].mean()
    avg_humidity = country_df.get("humidity", pd.Series([])).mean() if "humidity" in df.columns else 0
    avg_rain = country_df.get(rain_col, pd.Series([])).mean() if rain_col else 0
    avg_wind = country_df.get("wind_kph", pd.Series([])).mean() if "wind_kph" in df.columns else 0

    # Handle NaN
    avg_temp = 0 if pd.isna(avg_temp) else avg_temp
    avg_humidity = 0 if pd.isna(avg_humidity) else avg_humidity
    avg_rain = 0 if pd.isna(avg_rain) else avg_rain
    avg_wind = 0 if pd.isna(avg_wind) else avg_wind

    # -------------------------
    # CLIMATE SUMMARY
    # -------------------------
    st.subheader("📊 Climate Summary")

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("🌡 Temp", f"{avg_temp:.2f} °C")
    m2.metric("💧 Humidity", f"{avg_humidity:.2f}%")
    m3.metric("🌧 Rainfall", f"{avg_rain:.2f}")
    m4.metric("💨 Wind", f"{avg_wind:.2f}")

    with st.expander("📌 What does this tell you?"):
     st.write(
        "These values show the overall climate conditions of the selected country. "
        "If temperature, humidity, or rainfall are high, it indicates potentially uncomfortable "
        "or risky conditions for outdoor activities. Use this as a quick snapshot before making decisions."
    )

    # -------------------------
    # CLIMATE TRENDS (NEW FEATURE)
    # -------------------------
    st.subheader("📈 Climate Trends")

    if "month" in country_df.columns:
        monthly_data = country_df.groupby("month").agg({
            "temperature_celsius": "mean",
            "humidity": "mean" if "humidity" in df.columns else lambda x: 0,
            rain_col: "mean" if rain_col else lambda x: 0,
            "wind_kph": "mean" if "wind_kph" in df.columns else lambda x: 0
        }).reset_index()

        # Rename columns for plotting
        monthly_data.columns = ["Month", "Temperature (°C)", "Humidity (%)", "Rainfall", "Wind (kph)"]

        # Plot temperature trend
        fig_trend = px.line(monthly_data, x="Month", y="Temperature (°C)", 
                           title="Monthly Average Temperature",
                           markers=True)
        st.plotly_chart(fig_trend, use_container_width=True)

        # Option to show other trends
        trend_options = st.multiselect("Select additional trends to view:",
                                      ["Humidity (%)", "Rainfall", "Wind (kph)"],
                                      default=[])
        if trend_options:
         for trend in trend_options:
            fig = px.line(
                monthly_data,
                x="Month",
                y=trend,
                title=f"Monthly Average {trend}",
                markers=True
            )

            st.plotly_chart(fig, use_container_width=True)

        else:
            st.info("Select a trend to display additional insights.")
    else:
        st.write("Monthly trend data not available.")

        with st.expander("📌 How to interpret trends?"):
         st.write(
        "This chart helps you understand how climate changes over time. "
        "If temperature or rainfall is increasing in certain months, you can avoid planning activities during those periods. "
        "It helps identify seasonal patterns and better timing for travel or events."
    )

    # -------------------------
    # FORECAST SIMULATION (NEW FEATURE)
    # -------------------------
    st.subheader("🔮 Forecast Simulation")

    forecast_days = st.slider("Select forecast days:", 1, 7, 3)

    # Simulate forecast by adding some noise to current averages
    np.random.seed(42)  # For reproducibility
    forecast_temp = [avg_temp + np.random.normal(0, 2) for _ in range(forecast_days)]
    forecast_rain = [max(0, avg_rain + np.random.normal(0, 1)) for _ in range(forecast_days)]
    forecast_humidity = [min(100, max(0, avg_humidity + np.random.normal(0, 5))) for _ in range(forecast_days)]
    forecast_wind = [max(0, avg_wind + np.random.normal(0, 3)) for _ in range(forecast_days)]

    forecast_df = pd.DataFrame({
        "Day": [f"Day {i+1}" for i in range(forecast_days)],
        "Temperature (°C)": forecast_temp,
        "Rainfall": forecast_rain,
        "Humidity (%)": forecast_humidity,
        "Wind (kph)": forecast_wind
    })

    st.dataframe(forecast_df)

    # Plot forecast
    fig_forecast = px.line(forecast_df, x="Day", y="Temperature (°C)", 
                          title="Temperature Forecast",
                          markers=True)
    st.plotly_chart(fig_forecast, use_container_width=True)
    with st.expander("📌 How to use this forecast?"):
     st.write(
        "This simulated forecast gives a short-term expectation of weather conditions. "
        "If upcoming days show higher temperature or rainfall, you may need to plan accordingly, "
        "such as carrying protection or rescheduling activities."
    )

    # -------------------------
    # DYNAMIC THRESHOLDS
    # -------------------------
    temp_high = df["temperature_celsius"].quantile(0.9)
    temp_mid = df["temperature_celsius"].quantile(0.7)

    rain_high = df[rain_col].quantile(0.9) if rain_col else 0
    rain_mid = df[rain_col].quantile(0.7) if rain_col else 0

    wind_high = df["wind_kph"].quantile(0.9) if "wind_kph" in df.columns else 0
    humidity_high = df.get("humidity", pd.Series([])).quantile(0.9) if "humidity" in df.columns else 0

    # -------------------------
    # RISK BREAKDOWN
    # -------------------------
    st.subheader("🔍 Risk Breakdown")

    breakdown = {
        "🌡 Temperature Risk": 3 if avg_temp > temp_high else 2 if avg_temp > temp_mid else 1,
        "🌧 Rainfall Risk": 3 if avg_rain > rain_high else 2 if avg_rain > rain_mid else 1,
        "💨 Wind Risk": 2 if avg_wind > wind_high else 1,
        "💧 Humidity Risk": 1 if avg_humidity > humidity_high else 0
    }

    # DISPLAY BREAKDOWN (THIS WAS MISSING)
    for k, v in breakdown.items():
        st.write(f"{k}: **{v}**")

    # Highlight highest factor
    max_factor = max(breakdown, key=breakdown.get)
    st.warning(f"⚠️ Highest contributing factor: **{max_factor}**")

    with st.expander("📌 What affects your risk the most?"):
     st.write(
        "This section shows which climate factor contributes most to the overall risk. "
        "For example, if temperature risk is high, heat is the main concern. "
        "Focus on the highest factor to take targeted precautions."
    )

    # -------------------------
    # RISK SCORE
    # -------------------------
    risk_score = sum(breakdown.values())

    # -------------------------
    # USER TOLERANCE
    # -------------------------
    if "Low" in risk_tolerance:
        threshold = 3
    elif "Medium" in risk_tolerance:
        threshold = 5
    else:
        threshold = 7

    # -------------------------
    # RISK VISUALIZATION
    # -------------------------
    st.subheader("⚠️ Risk Assessment")

    st.progress(min(risk_score / 10, 1.0))

    fig_gauge = go.Figure(go.Indicator(
        mode="gauge+number",
        value=risk_score,
        title={'text': "Risk Score"},
        gauge={
            'axis': {'range': [0, 10]},
            'bar': {'color': "darkred"},
            'steps': [
                {'range': [0, 3], 'color': "green"},
                {'range': [3, 6], 'color': "yellow"},
                {'range': [6, 10], 'color': "red"}
            ],
        }
    ))

    st.plotly_chart(fig_gauge, use_container_width=True)

    with st.expander("📌 How to read this risk score?"):
     st.write(
        "The risk score combines multiple climate conditions into a single value. "
        "Lower scores indicate safe conditions, while higher scores indicate potential danger. "
        "Use this score to quickly decide whether it is safe to proceed with your plans."
    )

    # -------------------------
    # DECISION ENGINE
    # -------------------------
    if risk_score >= threshold:
        st.error("🔴 HIGH RISK")
        decision = "High Risk"
    elif risk_score >= threshold - 2:
        st.warning("🟠 MODERATE RISK")
        decision = "Moderate Risk"
    else:
        st.success("🟢 LOW RISK")
        decision = "Low Risk"

    # -------------------------
    # ACTIVITY DECISION
    # -------------------------
    st.subheader("🎯 Activity Recommendation")

    if decision == "High Risk":
        st.error(f"{activity} is NOT recommended.")
    elif decision == "Moderate Risk":
        st.warning(f"{activity} can be done with precautions.")
    else:
        st.success(f"{activity} is safe.")

    with st.expander("📌 How is this decision made?"):
     st.write(
        "This recommendation is based on your selected activity and the calculated risk level. "
        "If risk is high, the system advises against the activity. "
        "If moderate, precautions are needed. If low, conditions are safe."
    )

    # -------------------------
    # FINAL SUMMARY
    # -------------------------
    st.markdown("---")
    st.subheader("📌 Final Decision Summary")

    st.info(f"""
    Country: **{selected_country}**  
    Activity: **{activity}**  
    Risk Level: **{decision}**  
    Risk Score: **{risk_score}/10**

    Decision is based on combined climate conditions and user risk tolerance.
    """)
    with st.expander("📌 What should you conclude from this?"):
     st.write(
        "This is your final decision output combining climate data, risk score, and your preferences. "
        "You can use this as a clear guideline for whether to proceed, delay, or modify your plans."
    )

    # -------------------------
    # SAVE DECISION (NEW FEATURE)
    # -------------------------
    if st.button("💾 Save This Decision"):
        decision_record = {
            "timestamp": pd.Timestamp.now(),
            "country": selected_country,
            "activity": activity,
            "risk_tolerance": risk_tolerance,
            "risk_score": risk_score,
            "decision": decision,
            "temperature": avg_temp,
            "humidity": avg_humidity,
            "rainfall": avg_rain,
            "wind": avg_wind
        }
        
        if "decision_history" not in st.session_state:
            st.session_state.decision_history = []
        st.session_state.decision_history.append(decision_record)
        st.success("Decision saved! View history below.")

    # Show history if exists
    if "decision_history" in st.session_state and st.session_state.decision_history:
        st.subheader("📚 Decision History")
        history_df = pd.DataFrame(st.session_state.decision_history)
        st.dataframe(history_df.tail(10))  # Show last 10

    # -------------------------
    # SMART RECOMMENDATIONS
    # -------------------------
    st.subheader("💡 Smart Recommendations")

    if avg_temp > temp_high:
        st.write("• Avoid extreme heat exposure.")
    if avg_rain > rain_high:
        st.write("• Risk of heavy rainfall — carry protection.")
    if avg_wind > wind_high:
        st.write("• Strong winds — avoid open areas.")
    if avg_humidity > humidity_high:
        st.write("• High humidity — stay hydrated.")

    if decision == "Low Risk":
        st.write("• Conditions are safe for most activities.")

    with st.expander("📌 How to act on these suggestions?"):
     st.write(
        "These recommendations help you reduce risk. "
        "For example, high temperature suggests avoiding outdoor exposure, "
        "while high rainfall suggests carrying protection. "
        "Follow these tips to stay safe and comfortable."
    )

    # -------------------------
    # SYSTEM EXPLANATION
    # -------------------------
    with st.expander("📌 How this system works"):
        st.write("""
        This system converts climate data into a decision-making model.

        Each climate factor contributes to a risk score:
        • Temperature → Heat risk  
        • Rainfall → Flood risk  
        • Wind → Storm risk  
        • Humidity → Comfort risk  

        The system adapts to dataset values using dynamic thresholds, providing personalized recommendations based on user risk tolerance and activity type.
        """)

    # -------------------------
    # USER FEEDBACK (NEW FEATURE)
    # -------------------------
    st.subheader("📝 User Feedback")

    feedback_rating = st.slider("Rate the accuracy of this decision (1-5):", 1, 5, 3)
    feedback_text = st.text_area("Any additional comments or suggestions?")

    if st.button("Submit Feedback"):
        feedback_record = {
            "timestamp": pd.Timestamp.now(),
            "country": selected_country,
            "activity": activity,
            "rating": feedback_rating,
            "comments": feedback_text
        }
        
        if "feedback_history" not in st.session_state:
            st.session_state.feedback_history = []
        st.session_state.feedback_history.append(feedback_record)
        st.success("Thank you for your feedback!")

    # Show average rating if feedback exists
    if "feedback_history" in st.session_state and st.session_state.feedback_history:
        avg_rating = np.mean([f["rating"] for f in st.session_state.feedback_history])
        st.write(f"Average user rating: **{avg_rating:.1f}/5** ({len(st.session_state.feedback_history)} responses)")

    # -------------------------
    # EXPORT REPORT (NEW FEATURE)
    # -------------------------
    st.subheader("📄 Export Report")

    report_text = f"""
    Climate Decision Intelligence System Report
    ==========================================

    Country: {selected_country}
    Activity: {activity}
    Risk Tolerance: {risk_tolerance}
    Risk Score: {risk_score}/10
    Decision: {decision}

    Climate Metrics:
    - Temperature: {avg_temp:.2f} °C
    - Humidity: {avg_humidity:.2f}%
    - Rainfall: {avg_rain:.2f}
    - Wind Speed: {avg_wind:.2f} kph

    Risk Breakdown:
    {chr(10).join([f"- {k}: {v}" for k, v in breakdown.items()])}

    Recommendations:
    {chr(10).join([f"- {rec}" for rec in [
        "Avoid extreme heat exposure." if avg_temp > temp_high else "",
        "Risk of heavy rainfall — carry protection." if avg_rain > rain_high else "",
        "Strong winds — avoid open areas." if avg_wind > wind_high else "",
        "High humidity — stay hydrated." if avg_humidity > humidity_high else "",
        "Conditions are safe for most activities." if decision == "Low Risk" else ""
    ] if rec])}

    Generated on: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}
    """
    def generate_pdf_report():
        from io import BytesIO
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
        from reportlab.lib.styles import getSampleStyleSheet

        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer)
        styles = getSampleStyleSheet()

        content = []

        # -------------------------
        # TITLE
        # -------------------------
        content.append(Paragraph("Climate Decision Intelligence Report", styles["Title"]))
        content.append(Spacer(1, 10))

        # -------------------------
        # USER INPUTS
        # -------------------------
        content.append(Paragraph(f"<b>Country:</b> {selected_country}", styles["Normal"]))
        content.append(Paragraph(f"<b>Activity:</b> {activity}", styles["Normal"]))
        content.append(Paragraph(f"<b>Risk Tolerance:</b> {risk_tolerance}", styles["Normal"]))
        content.append(Spacer(1, 10))

        # -------------------------
        # CLIMATE METRICS
        # -------------------------
        content.append(Paragraph("<b>Climate Summary:</b>", styles["Heading3"]))
        content.append(Paragraph(f"Temperature: {avg_temp:.2f} °C", styles["Normal"]))
        content.append(Paragraph(f"Humidity: {avg_humidity:.2f} %", styles["Normal"]))
        content.append(Paragraph(f"Rainfall: {avg_rain:.2f}", styles["Normal"]))
        content.append(Paragraph(f"Wind Speed: {avg_wind:.2f} kph", styles["Normal"]))
        content.append(Spacer(1, 10))

        # -------------------------
        # RISK BREAKDOWN
        # -------------------------
        content.append(Paragraph("<b>Risk Breakdown:</b>", styles["Heading3"]))
        for k, v in breakdown.items():
            content.append(Paragraph(f"{k}: {v}", styles["Normal"]))

        max_factor = max(breakdown, key=breakdown.get)
        content.append(Paragraph(f"Highest Risk Factor: {max_factor}", styles["Normal"]))
        content.append(Spacer(1, 10))

        # -------------------------
        # RISK SCORE + DECISION
        # -------------------------
        content.append(Paragraph("<b>Risk Assessment:</b>", styles["Heading3"]))
        content.append(Paragraph(f"Risk Score: {risk_score}/10", styles["Normal"]))
        content.append(Paragraph(f"Decision: {decision}", styles["Normal"]))
        content.append(Spacer(1, 10))

        # -------------------------
        # FORECAST (VERY IMPORTANT ⭐)
        # -------------------------
        content.append(Paragraph("<b>Forecast (Next Days):</b>", styles["Heading3"]))

        for i in range(len(forecast_df)):
            row = forecast_df.iloc[i]
            content.append(Paragraph(
                f"{row['Day']} → Temp: {row['Temperature (°C)']:.2f}°C, "
                f"Rain: {row['Rainfall']:.2f}, "
                f"Humidity: {row['Humidity (%)']:.2f}%, "
                f"Wind: {row['Wind (kph)']:.2f} kph",
                styles["Normal"]
            ))

        content.append(Spacer(1, 10))

        # -------------------------
        # RECOMMENDATIONS
        # -------------------------
        content.append(Paragraph("<b>Smart Recommendations:</b>", styles["Heading3"]))

        if avg_temp > temp_high:
            content.append(Paragraph("Avoid extreme heat exposure.", styles["Normal"]))
        if avg_rain > rain_high:
            content.append(Paragraph("Risk of heavy rainfall — carry protection.", styles["Normal"]))
        if avg_wind > wind_high:
            content.append(Paragraph("Strong winds — avoid open areas.", styles["Normal"]))
        if avg_humidity > humidity_high:
            content.append(Paragraph("High humidity — stay hydrated.", styles["Normal"]))
        if decision == "Low Risk":
            content.append(Paragraph("Conditions are safe for most activities.", styles["Normal"]))

        content.append(Spacer(1, 10))

        # -------------------------
        # FINAL SUMMARY
        # -------------------------
        content.append(Paragraph("<b>Final Summary:</b>", styles["Heading3"]))
        content.append(Paragraph(
            f"For {activity} in {selected_country}, the system predicts a {decision} "
            f"with a risk score of {risk_score}/10 based on current climate conditions.",
            styles["Normal"]
        ))

        content.append(Spacer(1, 10))

        # -------------------------
        # TIMESTAMP
        # -------------------------
        content.append(Paragraph(
            f"Generated on: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}",
            styles["Normal"]
        ))

        doc.build(content)

        buffer.seek(0)
        return buffer

    pdf_file = generate_pdf_report()

    st.download_button(
        label="📄 Download Report as PDF",
        data=pdf_file,
        file_name=f"climate_report_{selected_country}_{activity.replace(' ', '_')}.pdf",
        mime="application/pdf"
    )

st.markdown("---")

st.caption(
    "ClimateScope Weather Analytics Dashboard and Application"
    "Developed for Infosys Internship Program"
)