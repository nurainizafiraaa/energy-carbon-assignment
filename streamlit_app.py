import streamlit as st
import pandas as pd
import altair as alt

# --- PAGE CONFIGURATION ---
st.set_page_config(
   page_title="Energy and Carbon Emission Review",
   page_icon="⚡",
   layout="wide",
   initial_sidebar_state="expanded",
)

# --- DATA LOADING ---
@st.cache_data
def load_data():
    file_id = "16A_4BmOEsbhhv9vUBQWemk8s3M4WDB5D"
    url = f"https://drive.google.com/uc?id={file_id}"
    df = pd.read_csv(url)
    df.dropna(inplace=True)
    return df

df = load_data()

# --- APP TITLE AND DESCRIPTION ---
st.title("⚡ Energy and Carbon Emission Review")
st.markdown("""
This dashboard provides an **exploratory data analysis (EDA)** 
on global **energy consumption** and **carbon emissions** data.  
Use the filters in the sidebar to explore trends by country and year.
""")

# --- SIDEBAR FILTERS ---
st.sidebar.header("🔎 Filters")

# Country filter
Country = st.sidebar.multiselect(
   "Select Country",
   options=df["Country"].unique(),
)

# Year filter
Year = st.sidebar.multiselect(
   "Select Year",
   options=df["Year"].unique(),
)


# --- FILTER DATA ---
df_selection = df.copy()

if Country:
   df_selection = df_selection[df_selection["Country"].isin(Country)]
if Year:
   df_selection = df_selection[df_selection["Year"].isin(Year)]

df_selection = df_selection[
   (df_selection["Total Energy Consumption (TWh)"] >= energy_range[0]) & 
   (df_selection["Total Energy Consumption (TWh)"] <= energy_range[1])
]

if df_selection.empty:
   st.warning("⚠️ No data available for the selected filters. Please adjust your selection.")
   st.stop()

# --- TABS ---
tab1, tab2, tab3, tab4 = st.tabs(["📊 Metrics", "📈 Trends", "🌍 Correlation", "📄 Raw Data"])

# --- TAB 1: METRICS ---
with tab1:
    st.subheader("📊 Key Metrics")
    col1, col2 = st.columns(2)
    with col1:
        total_energy = df_selection["Total Energy Consumption (TWh)"].sum()
        st.metric("Total Energy Consumption (TWh)", f"{total_energy:,.0f}")
    with col2:
        avg_emission = df_selection["Carbon Emissions (Million Tons)"].mean()
        st.metric("Average Carbon Emissions (Million Tons)", f"{avg_emission:,.2f}")

# --- TAB 2: TRENDS ---
with tab2:
    st.subheader("📈 Fossil vs Renewable Energy Over Time")
    chart_data = (
        df_selection.groupby("Year")[["Fossil Fuel Dependency (%)", "Renewable Energy Share (%)"]]
        .mean()
        .reset_index()
    )
    st.line_chart(chart_data.set_index("Year"))

# --- TAB 3: CORRELATION ---
with tab3:
    st.subheader("🌍 Correlation: Energy vs Carbon Emissions per Country")

    # Aggregate per country
    agg_data = (
        df_selection.groupby("Country")[["Total Energy Consumption (TWh)", "Carbon Emissions (Million Tons)"]]
        .sum()
        .reset_index()
    )

    # Sidebar options
    show_trend = st.sidebar.checkbox("Show regression line", value=True)
    log_scale = st.sidebar.checkbox("Use log scale", value=False)

    # Axis scaling
    x_scale = alt.Scale(type="log") if log_scale else alt.Scale(
        domain=[
            agg_data["Total Energy Consumption (TWh)"].min() * 0.9,
            agg_data["Total Energy Consumption (TWh)"].max() * 1.1,
        ]
    )
    y_scale = alt.Scale(type="log") if log_scale else alt.Scale(
        domain=[
            agg_data["Carbon Emissions (Million Tons)"].min() * 0.9,
            agg_data["Carbon Emissions (Million Tons)"].max() * 1.1,
        ]
    )

    # Scatter plot
    scatter_total = alt.Chart(agg_data).mark_circle(size=200).encode(
        x=alt.X("Total Energy Consumption (TWh):Q", title="Total Energy Consumption (TWh)", scale=x_scale),
        y=alt.Y("Carbon Emissions (Million Tons):Q", title="Carbon Emissions (Million Tons)", scale=y_scale),
        color="Country:N",
        tooltip=["Country", "Total Energy Consumption (TWh)", "Carbon Emissions (Million Tons)"]
    ).properties(width=800, height=500)

    # Regression line
    if show_trend:
        trend = alt.Chart(agg_data).transform_regression(
            "Total Energy Consumption (TWh)",
            "Carbon Emissions (Million Tons)"
        ).mark_line(color="red")
        st.altair_chart(scatter_total + trend, use_container_width=True)
    else:
        st.altair_chart(scatter_total, use_container_width=True)

# --- TAB 4: RAW DATA ---
with tab4:
    st.subheader("📄 Raw Data")
    st.dataframe(df_selection)
    st.markdown(f"**Data Dimensions:** {df_selection.shape[0]} rows × {df_selection.shape[1]} columns")

# --- FOOTER ---
st.markdown("---")
st.caption("📊 Data Source: [Google Drive Dataset](https://drive.google.com/uc?id=16A_4BmOEsbhhv9vUBQWemk8s3M4WDB5D)")
