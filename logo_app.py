# app.py
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objs as go
from datetime import datetime

# PAGE CONFIG
st.set_page_config(page_title="Demand Forecast & Inventory Optimization", layout="wide")

# THEME TOGGLE
theme = st.sidebar.radio("Theme Mode", options=["Light", "Dark"], index=1, help="Switch between dark/light themes")

# SIDEBAR: Filters
with st.sidebar:
    st.markdown("### Filters")
    product = st.selectbox("Select Product", ["Gear Shaft", "Clutch Plate", "Piston Rod"], help="Choose product to visualize")
    start_date = st.date_input("Start Date", datetime(2023, 1, 1))
    end_date = st.date_input("End Date", datetime.today())
    season = st.selectbox("Select Season", ["All", "Summer", "Winter", "Monsoon"], help="Optional season filter")
    critical_threshold = st.slider("Critical Inventory Level", min_value=100, max_value=500, value=300)

# GENERATE SYNTHETIC DATA
np.random.seed(42)
dates = pd.date_range(start=start_date, end=end_date, freq='W')
df = pd.DataFrame({
    "date": dates,
    "units_sold": np.random.poisson(350, len(dates)),
    "inventory_on_hand": np.random.randint(200, 800, len(dates))
})
df["critical_breach"] = df["inventory_on_hand"] < critical_threshold

# KPI CARDS
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("📦 Total Demand", f"{df['units_sold'].sum()}")
with col2:
    st.metric("📊 Avg Inventory", f"{int(df['inventory_on_hand'].mean())}")
with col3:
    pct_critical = 100 * df['critical_breach'].mean()
    st.metric("🚨 % Critical Breaches", f"{pct_critical:.2f}%")

# TITLE
st.markdown(f"## Product: {product} — Filtered View")
st.markdown("### Weekly Units Sold")

# ANIMATED DEMAND GRAPH
fig1 = go.Figure()

for i in range(len(df)):
    fig1.add_trace(go.Scatter(x=df['date'][:i+1], y=df['units_sold'][:i+1],
                              mode='lines+markers',
                              line=dict(color='royalblue'),
                              name="Units Sold",
                              showlegend=False))

fig1.update_layout(
    updatemenus=[dict(
        type="buttons",
        buttons=[dict(label="Play", method="animate", args=[None])],
        showactive=False,
        x=1.05,
        y=1.2
    )],
    xaxis_title="Date",
    yaxis_title="Units Sold",
    template="plotly_dark" if theme == "Dark" else "plotly_white",
    height=400,
    margin=dict(t=10, r=10, l=10, b=10)
)

frames = [go.Frame(data=[go.Scatter(x=df['date'][:k+1], y=df['units_sold'][:k+1])]) for k in range(len(df))]
fig1.frames = frames

# INVENTORY LEVELS WITH ALERT LINE
fig2 = go.Figure()
fig2.add_trace(go.Scatter(
    x=df["date"],
    y=df["inventory_on_hand"],
    mode="lines+markers",
    name="Inventory",
    line=dict(color="mediumseagreen")
))
fig2.add_trace(go.Scatter(
    x=df["date"],
    y=[critical_threshold]*len(df),
    mode="lines",
    name="Critical Level",
    line=dict(color="red", dash="dash")
))

fig2.update_layout(
    title="Inventory On Hand",
    xaxis_title="Date",
    yaxis_title="Inventory",
    template="plotly_dark" if theme == "Dark" else "plotly_white",
    height=400,
    margin=dict(t=10, r=10, l=10, b=10)
)

# MAIN DASHBOARD
col4, col5 = st.columns(2)
with col4:
    st.plotly_chart(fig1, use_container_width=True)
with col5:
    st.plotly_chart(fig2, use_container_width=True)

# ALERT MESSAGE
if df["critical_breach"].any():
    st.warning("⚠️ Critical inventory threshold breached in the selected period!")

