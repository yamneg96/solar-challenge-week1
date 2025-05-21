# === IMPORTS ===
import os
import streamlit as st
import pandas as pd
import plotly.express as px

# === PAGE CONFIG ===
st.set_page_config(
    page_title="Solar Challenge Dashboard",
    layout="wide"
)

# === TITLE AND SIDEBAR ===
st.title("☀️ Solar Radiation Dashboard - MoonLight Energy Solutions")
st.sidebar.header("🔍 Filter Options")

# === DATA LOADING FUNCTION ===
@st.cache_data
def load_data():
    data_dir = "data"
    datasets = {
        "Benin": "benin_clean.csv",
        "Sierra Leone": "sierra_leone_clean.csv",
        "Togo": "togo_clean.csv"
    }

    data_frames = []
    for country, filename in datasets.items():
        filepath = os.path.join(data_dir, filename)
        if os.path.exists(filepath):
            df = pd.read_csv(filepath, parse_dates=["Timestamp"])
            df["Country"] = country
            data_frames.append(df)
        else:
            st.warning(f"File not found: {filepath}")

    if data_frames:
        return pd.concat(data_frames, ignore_index=True)
    else:
        return pd.DataFrame()

# === LOAD DATA ===
df_all = load_data()

if df_all.empty:
    st.error("No data loaded. Please ensure CSV files exist in the data/ directory.")
    st.stop()

# === SIDEBAR MULTISELECT ===
countries = df_all["Country"].unique().tolist()
selected_countries = st.sidebar.multiselect(
    "Select Countries to View",
    options=countries,
    default=countries
)

# === FILTERED DATA ===
filtered_df = df_all[df_all["Country"].isin(selected_countries)]

# === BOX PLOT: GHI ===
st.subheader("📦 GHI Distribution by Country")

if not filtered_df.empty:
    fig = px.box(
        filtered_df,
        x="Country",
        y="GHI",
        color="Country",
        title="Global Horizontal Irradiance (GHI) by Country",
        labels={"GHI": "GHI (W/m²)", "Country": "Country"},
        points="outliers"
    )
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("Please select at least one country to view data.")

# === SUMMARY: AVERAGE GHI ===
st.subheader("📊 Average GHI per Country")

if not filtered_df.empty:
    ghi_summary = filtered_df.groupby("Country")["GHI"].mean().round(2).sort_values(ascending=False).reset_index()
    ghi_summary.columns = ["Country", "Average GHI (W/m²)"]
    st.dataframe(ghi_summary, use_container_width=True)
else:
    st.info("No data to summarize. Select countries to see average GHI.")
