import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# -------------------------------------------
# Page config (single call)
# -------------------------------------------
st.set_page_config(
    page_title="ClimateScope Weather Analytics",
    page_icon="🌍",
    layout="wide",
)

st.title("🌍 ClimateScope Weather Analytics Dashboard")

st.markdown("""
This interactive dashboard analyzes **global weather patterns**, temperature trends,
and extreme climate events using real-world weather data.

Use the **sidebar filters** to explore climate patterns across countries,
time periods, and seasons.
""")

st.divider()

# -------------------------------------------
# Data Load and Preprocessing
# -------------------------------------------
@st.cache_data
def load_data(path="data/weather_cleaned.csv"):
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
    st.stop()

rain_col = detect_rain_col(df)

# -------------------------------------------
# Sidebar filters
# -------------------------------------------
st.sidebar.header("🔧 ClimateScope Controls")

countries = sorted(df["country"].dropna().unique())

selected_countries = st.sidebar.multiselect(
    "Select Countries for Comparison",
    countries,
    default=countries[:3] if len(countries) >= 3 else countries,
)

min_date = df["last_updated"].min()
max_date = df["last_updated"].max()

date_range = st.sidebar.date_input(
    "📅 Select Date Range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date,
)

time_agg = st.sidebar.selectbox(
    "⏱ Time Aggregation",
    ["Daily", "Monthly", "Yearly"],
    index=0,
)

available_seasons = sorted(df["season"].dropna().unique())

selected_seasons = st.sidebar.multiselect(
    "🌦 Filter by Season",
    options=available_seasons,
    default=available_seasons,
)

temp_threshold = st.sidebar.slider(
    "🔥 Extreme Temperature Threshold (°C)",
    min_value=float(df["temperature_celsius"].min()),
    max_value=float(df["temperature_celsius"].max()),
    value=float(df["temperature_celsius"].quantile(0.95)),
)

st.sidebar.markdown("---")
st.sidebar.subheader("Dataset Info")

st.sidebar.write(f"Total Records: {len(df):,}")

if "country" in df.columns:
    st.sidebar.write(f"Countries: {df['country'].nunique()}")

if "last_updated" in df.columns:
    st.sidebar.write(
        f"Date Range: {df['last_updated'].min().date()} → {df['last_updated'].max().date()}"
    )
# -------------------------------------------
# Apply filters
# -------------------------------------------
filtered_df = df.copy()

if selected_countries:
    filtered_df = filtered_df[filtered_df["country"].isin(selected_countries)]

if isinstance(date_range, (list, tuple)) and len(date_range) == 2:
    start_date, end_date = date_range
    filtered_df = filtered_df[
        (filtered_df["last_updated"] >= pd.to_datetime(start_date))
        & (filtered_df["last_updated"] <= pd.to_datetime(end_date))
    ]

if selected_seasons:
    filtered_df = filtered_df[filtered_df["season"].isin(selected_seasons)]

if time_agg == "Monthly":
    filtered_df = filtered_df.assign(
        time_period=filtered_df["last_updated"].dt.to_period("M").astype(str)
    )
elif time_agg == "Yearly":
    filtered_df = filtered_df.assign(
        time_period=filtered_df["last_updated"].dt.year.astype(str)
    )
else:
    filtered_df = filtered_df.assign(
        time_period=filtered_df["last_updated"].dt.date.astype(str)
    )

filtered_df = filtered_df.assign(
    is_extreme_temp=filtered_df["temperature_celsius"] > temp_threshold
)

st.sidebar.markdown("---")
st.sidebar.write(f"📊 Filtered Rows: {len(filtered_df):,}")

# Final working frame
df = filtered_df.copy()
volatility_df = compute_country_vol(df)

st.success("✅ Data loaded successfully")
# -------------------------------------------
# Dashboard Layout Tabs
# -------------------------------------------

tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "Overview",
    "Temperature Analysis",
    "Climate Relationships",
    "Extreme Events",
    "Geographic Insights",
    "Advanced Insights"
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
        "These indicators summarize the overall climate conditions in the filtered dataset, "
        "including average temperature, humidity levels, and rainfall intensity."
    )

    # -------------------------------------------
    # Country-wise Temperature Comparison
    # -------------------------------------------
    st.subheader("🌍 Average Temperature by Country")
    if {"country", "temperature_celsius"}.issubset(df.columns):
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
            title="Top Countries by Average Temperature",
            labels={"temperature_celsius": "Avg Temp (°C)"},
        )
        fig_country.update_layout(height=500)
        st.plotly_chart(fig_country, use_container_width=True, key="temp_bar")
        with st.expander("📊 Insight"):
         st.write(
           "This bar chart compares the average temperature across countries. "
           "Countries with taller bars experience higher mean temperatures, "
           "indicating warmer climate conditions. Differences between countries "
           "highlight regional climate variability and geographical influence "
           "such as latitude, altitude, and proximity to oceans."
        )
    else:
        st.warning("Country/temperature column missing for country comparison.")

    # -------------------------------------------
    # Country climate comparison chart
    # -------------------------------------------
    st.subheader("Country Climate Comparison")
    metric = st.selectbox(
        "Select Climate Metric",
        [m for m in ["temperature_celsius", "humidity", rain_col or "precip_mm", "wind_kph"] if m in df.columns],
    )
    comparison = (
        df.groupby("country")[metric].mean().reset_index()
    )
    fig_compare = px.bar(
        comparison,
        x="country",
        y=metric,
        title=f"{metric} Comparison Across Countries",
    )
    fig_compare.update_layout(height=500)
    st.plotly_chart(fig_compare, use_container_width=True)
    with st.expander("📊 Insight"):
     st.write(
        "This chart compares the average temperature across countries. "
        "Countries with higher bars experience warmer climate conditions on average."
    )
        
    # -------------------------------------------
    # Temperature Volatility by Country
    # -------------------------------------------
    st.subheader("Temperature Volatility by Country")

    if "country" in df.columns and "temperature_celsius" in df.columns:
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
            "Countries with higher volatility experience larger temperature fluctuations. "
            "These regions may have unstable climate patterns or seasonal variability."
        )
    else:
        st.warning("Country/temperature columns not available for volatility chart.")

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
    else:
        st.write("No country summary columns available.")

    # 2) extreme events and anomalies
    if "temperature_celsius" in df.columns:
        extreme_temp_df = df[df["temperature_celsius"] > df["temperature_celsius"].quantile(0.95)]
        st.write("🔥 Extreme Temperature Events (95th percentile)")
        st.dataframe(
            extreme_temp_df[["country", "last_updated", "temperature_celsius", "condition_text"]]
            .sort_values("temperature_celsius", ascending=False)
            .head(30),
            use_container_width=True,
        )

    if rain_col:
        extreme_rain_df = df[df[rain_col] > df[rain_col].quantile(0.95)]
        st.write("🌧 Extreme Rainfall Events (95th percentile)")
        st.dataframe(
            extreme_rain_df[["country", "last_updated", rain_col, "condition_text"]]
            .sort_values(rain_col, ascending=False)
            .head(30),
            use_container_width=True,
        )

    # 3) month-year aggregate stats
    if "last_updated" in df.columns and "temperature_celsius" in df.columns:
        monthly_stats = (
            df.assign(year=df["last_updated"].dt.year, month=df["last_updated"].dt.month)
            .groupby(["year", "month"])
            .agg(
                avg_temp=("temperature_celsius", "mean"),
                max_temp=("temperature_celsius", "max"),
                min_temp=("temperature_celsius", "min"),
                avg_humidity=("humidity", "mean") if "humidity" in df.columns else pd.NamedAgg(column="temperature_celsius", aggfunc="count"),
                total_rain=(rain_col, "sum") if rain_col else pd.NamedAgg(column="temperature_celsius", aggfunc="count"),
            )
            .reset_index()
            .sort_values(["year", "month"])
        )
        st.write("🗓 Monthly Aggregated Climate Stats")
        st.dataframe(monthly_stats, use_container_width=True)

    with st.expander("📊 Insight"):
     st.write(
        "The table provides a summarized view of climate statistics by country, "
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

    extreme_temp = df[df["temperature_celsius"] > 35].shape[0] if "temperature_celsius" in df.columns else 0
    heavy_rain = df[df.get(rain_col, pd.Series([])) > 50].shape[0] if rain_col else 0

    st.subheader("Extreme Weather Insights")
    st.warning(f"🔥 Heatwave Events Detected: {extreme_temp}")
    st.warning(f"🌧 Potential Flood Events Detected: {heavy_rain}")

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
    st.subheader("Temperature Distribution")
    fig_hist = px.histogram(
        df,
        x="temperature_celsius",
        nbins=50,
        title="Temperature Distribution",
        labels={"temperature_celsius": "Temperature (°C)"},
    )
    fig_hist.update_layout(height=450)
    st.plotly_chart(fig_hist, use_container_width=True, key="temperature_hist")
    with st.expander("📊 Insight"):
        st.write(
            "This histogram shows the frequency distribution of temperature values. "
            "Most values cluster around moderate ranges, while extreme values appear in the tails."
        )

    st.subheader("Season Distribution")
    season_counts = df["season"].fillna("Unknown").value_counts()
    fig_pie = px.pie(
        names=season_counts.index,
        values=season_counts.values,
        title="Weather Records by Season",
    )
    st.plotly_chart(fig_pie, use_container_width=True, key="season_pie")
    with st.expander("📊 Insight"):
        st.write(
            "This pie chart shows how weather observations are distributed across seasons. "
            "A higher share of one season may indicate seasonal bias in data collection."
        )

    # -------------------------------------------
    # Temperature Trend Over Time
    # -------------------------------------------
    st.subheader("📈 Temperature Trend Over Time")

    df = df.sort_values("last_updated")
    if "country" in df.columns and "temperature_celsius" in df.columns:
        df["temp_roll_7"] = (
            df.groupby("country")["temperature_celsius"]
            .rolling(7, min_periods=1)
            .mean()
            .reset_index(level=0, drop=True)
        )

        fig_roll = px.line(
            df,
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
            "Rolling averages smooth short-term fluctuations and highlight long-term temperature trends."
        )

    if "last_updated" in df.columns and "temperature_celsius" in df.columns:
        temp_time = (
            df.groupby(pd.Grouper(key="last_updated", freq="D"))["temperature_celsius"]
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
            "This time series shows how temperature evolves over time and helps identify warming or cooling trends."
        )
    else:
        st.warning("Time-series columns missing for average temperature trend.")

    # -------------------------------------------
    # Seasonal Temperature Pattern
    # -------------------------------------------
    st.header("Seasonal Temperature Pattern")
    if "season" in df.columns and "temperature_celsius" in df.columns:
        seasonal_temp = (
            df.groupby("season")["temperature_celsius"]
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
                "Average temperature varies across seasons due to changes in solar radiation and weather patterns."
           )
        else:
            st.warning("No seasonal data available.")
    else:
        st.warning("Season or temperature column missing.")


    #-----------------------------------------------
    #country-wise temperature distribution boxplot
    #-----------------------------------------------
    
    if "country" in df.columns and "temperature_celsius" in df.columns and "last_updated" in df.columns:
     st.subheader("📍 LHorizon: Country Temperature Boxplot (select metric)")
    metric_for_box = st.selectbox(
        "Select metric for country-wise distribution",
        options=["temperature_celsius"] + (["humidity"] if "humidity" in df.columns else []),
        index=0,
        key="box_metric_selector"
    )
    fig_box2 = px.box(
        df,
        x="country",
        y=metric_for_box,
        color="country",
        title=f"{metric_for_box.replace('_', ' ').title()} Distribution by Country",
    )
    fig_box2.update_layout(height=520, showlegend=False)
    st.plotly_chart(fig_box2, use_container_width=True, key="country_boxplot")
    with st.expander("📊 Insight"):
     st.write(
        "This box plot visualizes the distribution of temperature values across countries. "
        "The box represents the interquartile range (middle 50% of values), the line inside "
        "the box represents the median temperature, and points outside the whiskers represent "
        "outliers. Countries with wider boxes indicate higher variability in temperature."
     )


with tab3:
    #-------------------------------------------
    # Correlation heatmaps
    # -------------------------------------------
    st.subheader("Correlation Heatmap")
    numeric_cols = df.select_dtypes(include=np.number).columns
    corr_matrix = df[numeric_cols].corr()
    fig_heat = px.imshow(
        corr_matrix,
        text_auto=True,
        aspect="auto",
        title="Correlation Matrix",
    )
    fig_heat.update_layout(height=500)
    st.plotly_chart(fig_heat, use_container_width=True, key="corr_heatmap")
    with st.expander("📊 Insight"):
        st.write(
            "Correlation heatmap highlights relationships between climate variables. "
            "Positive values indicate variables moving together, while negative values show inverse relationships."
            )

    st.subheader("📅 Seasonal Correlation Heatmap")
    if "season" in df.columns:
        for season in sorted(df["season"].dropna().unique()):
            st.write(f"*Season: {season}*")
            season_df = df[df["season"] == season]
            corr = season_df.select_dtypes(include=np.number).corr()
            fig_season_corr = px.imshow(
                corr,
                text_auto=True,
                title=f"Correlation Matrix — {season}",
            )
            fig_season_corr.update_layout(height=500)
            st.plotly_chart(fig_season_corr, use_container_width=True, key=f"season_corr_{season}")
            with st.expander(f"📊 Insight for {season}"):
                st.write(
                "The correlation matrix for **{season}** shows relationships between climate variables "
                    "such as temperature, humidity, wind speed, and precipitation."
        )
    else:
        st.warning("Season column missing.")    
    # -------------------------------------------
    # Humidity vs Precipitation
    # -------------------------------------------
    st.subheader("Humidity vs Precipitation")
    if {"humidity", rain_col}.issubset(df.columns):
        fig_scatter = px.scatter(
            df,
            x="humidity",
            y=rain_col,
            title="Humidity vs Precipitation",
            opacity=0.6,
        )
        fig_scatter.update_layout(height=450)
        st.plotly_chart(fig_scatter, use_container_width=True, key="hum_prec_scatter")
        with st.expander("📊 Insight"):
         st.write(
           "Higher humidity often leads to increased precipitation because moisture-rich air promotes rainfall."
        )
    else:
        st.warning("Humidity vs precipitation chart requires both columns.")

    #-------------------------------------------
    # Bubble chart for temp vs humidity vs wind
    #-------------------------------------------

    if {"temperature_celsius", "humidity", "wind_kph"}.issubset(df.columns):
     st.subheader("🌪️ Bubble Chart: Temperature vs Humidity vs Wind")
    fig_bubble = px.scatter(
        df,
        x="humidity",
        y="temperature_celsius",
        size="wind_kph",
        color="country" if "country" in df.columns else None,
        hover_name="country" if "country" in df.columns else None,
        title="Temperature vs Humidity with Wind Intensity",
        labels={"humidity": "Humidity (%)", "temperature_celsius": "Temperature (°C)", "wind_kph": "Wind Speed (kph)"},
        opacity=0.7,
    )
    fig_bubble.update_layout(height=520)
    st.plotly_chart(fig_bubble, use_container_width=True, key="bubble_hum_temp_wind")
    with st.expander("📊 Insight"):
     st.write(
        "Bubble size represents wind speed, allowing simultaneous analysis of temperature, humidity, and wind intensity."
     )

    # -------------------------------------------
    # Country comparison radar chart
    # -------------------------------------------
    st.subheader("Country Climate Comparison Radar")
    radar_metrics = ["temperature_celsius", "humidity", rain_col if rain_col else "precip_mm", "wind_kph"]
    radar_metrics = [c for c in radar_metrics if c in df.columns]

    if {"country"}.issubset(df.columns) and radar_metrics:
        radar_data = df.groupby("country")[radar_metrics].mean()
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
            "Radar chart compares multiple climate variables across countries simultaneously."
        )
    else:
        st.warning("Radar chart cannot be created - missing data.")

with tab4:
    #-------------------------------------------
    # volatility vs climate factors correlation
    #-------------------------------------------

    st.subheader("📊 Volatility vs Climate Factors")
    if {"country", "temperature_celsius", "humidity", "wind_kph"}.issubset(df.columns):
        vol_std = df.groupby("country")["temperature_celsius"].std().reset_index(name="temp_volatility")
        climate_avg = df.groupby("country")[["humidity", "wind_kph"]].mean().reset_index()
        merged_vol = vol_std.merge(climate_avg, on="country")
        corr_vol = merged_vol.corr(numeric_only=True)
        fig_vol_corr = px.imshow(corr_vol, text_auto=True, title="Correlation: Temperature Volatility vs Climate Factors")
        fig_vol_corr.update_layout(height=450)
        st.plotly_chart(fig_vol_corr, use_container_width=True, key="volatility_correlation")
        with st.expander(" Insight"):
         st.write("This heatmap shows the relationship between temperature volatility, humidity, and wind speed. "
           "Positive correlations indicate that increases in one variable are associated with increases in another."
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
        anomalies = df[abs(df["temp_anomaly"]) > 2]
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
            "Anomalies represent temperature values significantly different from the historical mean."
        )
    else:
        st.warning("No temperature data for anomaly detection.")

    if "temperature_celsius" in df.columns:
        temp_series = df["temperature_celsius"].dropna()
        extreme_threshold = temp_series.quantile(0.95)
        extreme_events = temp_series[temp_series > extreme_threshold]
        st.metric("🔥 Extreme Temperature Events", len(extreme_events))
        st.subheader("Temperature Outlier Detection")
        fig_box = px.box(
            df,
            y="temperature_celsius",
            title="Temperature Outlier Detection",
            color_discrete_sequence=["#FF6B6B"],
        )
        fig_box.update_layout(height=450)
        st.plotly_chart(fig_box, use_container_width=True, key="temp_box")
        with st.expander("📊 Insight"):
         st.write(
            "Box plots help identify extreme outliers and unusual temperature spikes."
        )
        st.caption(f"Extreme threshold (95th percentile): {extreme_threshold:.2f} °C")
    else:
        st.error("temperature_celsius column not found in dataset.")

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
            "Timeline highlights periods where extreme heat events occurred."
        )

    # -------------------------------------------
    # Flood Risk Detection
    # -------------------------------------------
    st.subheader("Flood Risk Detection")
    if rain_col:
        rain_threshold = df[rain_col].quantile(0.95)
        flood_risk = df[df[rain_col] > rain_threshold]
        st.metric("🌊 Potential Flood Risk Events", len(flood_risk))
        st.write(f"Rainfall records used: {df[rain_col].notna().sum()}")
        fig_rain = px.histogram(df, x=rain_col, nbins=50, title="Rainfall Distribution")
        fig_rain.update_layout(height=450)
        st.plotly_chart(fig_rain, use_container_width=True, key="rain_histogram")
        with st.expander("📊 Insight"):
         st.write(
            "Flood risk events are detected when rainfall exceeds the 95th percentile."
        )
    else:
        st.warning("Rainfall column not found in dataset")

    # -------------------------------------------
    # Wind Speed Distribution
    # -------------------------------------------
    st.subheader("💨 Wind Speed Distribution (Weibull Approx)")
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
            "Wind speed distribution follows a Weibull-like pattern common in meteorological datasets."
        )
    else:
        st.warning("wind_kph column missing.")

    #---------------------
    # rainfall time series
    #----------------------

    if rain_col and "country" in df.columns and "last_updated" in df.columns:
     st.subheader("⏳ Rainfall Time Series by Country")
    selected_country = st.selectbox(
        "Select Country for Rainfall Time-Series",
        options=sorted(df["country"].dropna().unique()),
        index=0,
        key="rain_country_selector"
    )
    country_rain = (
        df[df["country"] == selected_country]
        .groupby(pd.Grouper(key="last_updated", freq="M"))[rain_col]
        .mean()
        .reset_index()
    )
    fig_rain_ts = px.line(
        country_rain,
        x="last_updated",
        y=rain_col,
        title=f"Average Monthly {rain_col} for {selected_country}",
        labels={"last_updated": "Date", rain_col: "Rainfall (mm)"},
    )
    fig_rain_ts.update_layout(height=520)
    st.plotly_chart(fig_rain_ts, use_container_width=True, key="rainfall_timeseries")
    with st.expander("📊 Insight"):
     st.write(
        "This time series chart shows how rainfall changes over time for the selected country. "
        "Peaks in the line represent periods of heavy rainfall, while lower values indicate "
        "dry conditions. Identifying these peaks helps detect seasonal rainfall patterns and "
        "potential flood risk periods."
     )

with tab5:
    # -------------------------------------------
    # Global Temperature Evolution
    # -------------------------------------------

    st.subheader("Global Temperature Evolution")
    if {"country", "last_updated", "temperature_celsius"}.issubset(df.columns):
        temp_time_anim = (
            df.groupby(["country", "last_updated"])["temperature_celsius"]
            .mean()
            .reset_index()
        )
        fig_anim = px.choropleth(
            temp_time_anim,
            locations="country",
            locationmode="country names",
            color="temperature_celsius",
            animation_frame="last_updated",
            title="Global Temperature Over Time",
        )
        fig_anim.update_layout(height=600)
        st.plotly_chart(fig_anim, use_container_width=True)
        with st.expander("📊 Insight"):
         st.write(
            "The choropleth map visualizes geographic temperature patterns across countries."
        )
    else:
        st.warning("Cannot draw global evolution; missing columns.")

    # -------------------------------------------
    # Global Temperature Map
    # -------------------------------------------
    st.subheader("Average Temperature by Country")
    if {"country", "temperature_celsius"}.issubset(df.columns):
        country_temp_map = (
            df.groupby("country")["temperature_celsius"]
            .mean()
            .reset_index()
        )
        fig_map = px.choropleth(
            country_temp_map,
            locations="country",
            locationmode="country names",
            color="temperature_celsius",
            hover_data=["temperature_celsius"],
            title="Average Temperature by Country",
        )
        fig_map.update_layout(height=600)
        st.plotly_chart(fig_map, use_container_width=True)
        with st.expander("📊 Insight"):
         st.write(
        "Choropleth maps highlight temperature differences across countries."
        )
    else:
        st.warning("Country/temperature cannot build map.")

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
          "Temperature generally decreases as latitude increases due to reduced solar radiation."
        )
    else:
        st.warning("Latitude or temperature column missing for scatter.")


    #-------------------------
    # Timezone cloud coverage
    #-------------------------

    if "timezone" in df.columns and "cloud" in df.columns and "country" in df.columns:
     st.write("Timezone vs Cloud Coverage")
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
        "precipitation probability."
     )

    #------------------------------------------
    # Moonrise Moonset
    #-------------------------------------------

    if "moonrise" in df.columns and "moonset" in df.columns and "country" in df.columns:
        st.write("Moonrise/Moonset for Selected Country")
        selected_country_moon = st.selectbox(
            "Choose Country for Moon Cycle",
            options=sorted(df["country"].dropna().unique()),
            key="moon_country_selector"
        )
        country_moon = df[df["country"] == selected_country_moon][["moonrise", "moonset", "last_updated"]].dropna()
    if not country_moon.empty:
        country_moon["moonrise"] = pd.to_datetime(country_moon["moonrise"], errors="coerce")
        country_moon["moonset"] = pd.to_datetime(country_moon["moonset"], errors="coerce")
        country_moon = country_moon.dropna(subset=["moonrise", "moonset", "last_updated"])
        country_moon = country_moon.sort_values("last_updated")

        fig_moon = px.line(
            country_moon,
            x="last_updated",
            y=["moonrise", "moonset"],
            title=f"Moonrise and Moonset Over Time for {selected_country_moon}",
            labels={"value": "Time", "last_updated": "Date", "variable": "Moon Event"},
        )
        fig_moon.update_layout(height=520)
        st.plotly_chart(fig_moon, use_container_width=True, key="mooncycle_country")
        with st.expander("📊 Insight"):
         st.write(
           "This chart tracks moonrise and moonset timings across dates for the selected country. "
           "The variation occurs due to the Moon's orbital cycle around Earth. Observing these "
           "patterns helps understand lunar cycles and their potential influence on tides and "
           "nighttime environmental conditions."
         )
    else:
        st.info("No moonrise/moonset data available for selected country.")

with tab6:

    # -------------------------------------------
    # AI insights generator (simple static logic)
    # -------------------------------------------
    st.header("AI Climate Insight Generator")
    temp_mean = df["temperature_celsius"].mean() if "temperature_celsius" in df.columns else np.nan
    temp_std = df["temperature_celsius"].std() if "temperature_celsius" in df.columns else np.nan
    humidity_mean = df["humidity"].mean() if "humidity" in df.columns else np.nan
    rain_mean = df[rain_col].mean() if rain_col in df.columns else np.nan
    wind_mean = df["wind_kph"].mean() if "wind_kph" in df.columns else np.nan

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

st.markdown("---")

st.caption(
    "ClimateScope Weather Analytics Dashboard | "
    "Developed for Infosys Internship Program"
)