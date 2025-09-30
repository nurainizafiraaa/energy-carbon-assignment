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

    # Scatter pakai data tahunan (per country & year)
    scatter = alt.Chart(df_selection).mark_circle(size=80).encode(
        x=alt.X("Total Energy Consumption (TWh):Q", title="Total Energy Consumption (TWh)"),
        y=alt.Y("Carbon Emissions (Million Tons):Q", title="Carbon Emissions (Million Tons)"),
        color="Country:N",
        tooltip=["Country", "Year", "Total Energy Consumption (TWh)", "Carbon Emissions (Million Tons)"]
    ).properties(width=800, height=500)

    st.altair_chart(scatter, use_container_width=True)


# --- TAB 4: RAW DATA ---
with tab4:
    st.subheader("📄 Raw Data")
    st.dataframe(df_selection)
    st.markdown(f"**Data Dimensions:** {df_selection.shape[0]} rows × {df_selection.shape[1]} columns")

# --- FOOTER ---
st.markdown("---")
st.caption("📊 Data Source: [Google Drive Dataset](https://drive.google.com/uc?id=16A_4BmOEsbhhv9vUBQWemk8s3M4WDB5D)")
