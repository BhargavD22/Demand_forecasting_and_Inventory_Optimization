import streamlit as st
import pandas as pd
import plotly.graph_objs as go
from datetime import datetime

# Load data
@st.cache_data
def load_data():
    df = pd.read_csv("sample_supply_chain_data.csv", parse_dates=["date"])
    return df

# Theming: Apply background based on theme
def set_background(theme):
    if theme == "Dark":
        st.markdown(
            f"""
            <style>
                .stApp {{
                    background-image: url("https://images.unsplash.com/photo-1504384308090-c894fdcc538d");
                    background-size: cover;
                }}
            </style>
            """,
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            f"""
            <style>
                .stApp {{
                    background-image: url("https://images.unsplash.com/photo-1518779578993-ec3579fee39f");
                    background-size: cover;
                }}
            </style>
            """,
            unsafe_allow_html=True
        )

# Load dataset
df = load_data()

# Sidebar config
st.sidebar.image("miracle_logo.png", width=180)  # <-- Make sure this file is in your working directory
st.sidebar.title("Miracle Insights")
theme_mode = st.sidebar.radio("Theme Mode", ["Light", "Dark"])
set_background(theme_mode)

st.sidebar.header("Filters")
product = st.sidebar.selectbox("Select Product", df["part_type"].unique())
start_date = st.sidebar.date_input("Start Date", df["date"].min())
end_date = st.sidebar.date_input("End Date", df["date"].max())

# Filtered data
filtered_df = df[
    (df["part_type"] == product) & 
    (df["date"] >= pd.to_datetime(start_date)) & 
    (df["date"] <= pd.to_datetime(end_date))
]

# Main content
st.markdown("## Demand Forecast & Inventory Optimization")
st.markdown(f"### Product: {product} — Filtered View")

# KPI cards
total_demand = filtered_df["parts_delivered"].sum()
avg_inventory = filtered_df["parts_planned"].mean()
critical_breaches = filtered_df[filtered_df["supplier_status"] == "Disrupted"].shape[0]
col1, col2, col3 = st.columns(3)
col1.metric("📦 Total Demand", f"{total_demand}")
col2.metric("📊 Avg Inventory", f"{avg_inventory:.2f}")
col3.metric("🚨 Critical Breaches", f"{critical_breaches}")

# Historical demand chart
demand_fig = go.Figure()
demand_fig.add_trace(go.Scatter(
    x=filtered_df["date"], 
    y=filtered_df["parts_delivered"],
    mode="lines+markers", 
    name="Units Sold"
))
demand_fig.update_layout(
    title="Historical Demand",
    template="plotly_dark" if theme_mode == "Dark" else "plotly_white",
    xaxis_title="Date", 
    yaxis_title="Units Delivered",
    xaxis_rangeslider_visible=True,
    hovermode='x unified'
)
st.plotly_chart(demand_fig, use_container_width=True)

# Inventory levels chart
inventory_fig = go.Figure()
inventory_fig.add_trace(go.Scatter(
    x=filtered_df["date"], 
    y=filtered_df["parts_planned"],
    mode="lines+markers", 
    name="Inventory Level"
))
inventory_fig.add_trace(go.Scatter(
    x=filtered_df["date"],
    y=[300]*len(filtered_df),
    mode="lines", 
    name="Critical Level", 
    line=dict(dash='dash', color='red')
))
inventory_fig.update_layout(
    title="Inventory Levels",
    template="plotly_dark" if theme_mode == "Dark" else "plotly_white",
    xaxis_title="Date", 
    yaxis_title="Units Planned",
    xaxis_rangeslider_visible=True,
    hovermode='x unified'
)
st.plotly_chart(inventory_fig, use_container_width=True)
