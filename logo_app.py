# app.py
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np
from datetime import datetime, timedelta


# ============ PAGE CONFIG ============
st.set_page_config(page_title="Demand & Inventory Dashboard", layout="wide", page_icon="📦")


# ============ CUSTOM CSS ============
st.markdown("""
<style>
/* Gradient background */
body {
background: linear-gradient(135deg, #f0f4f8 0%, #d9e2ec 100%) !important;
}


/* Watermark */
body::after {
content: "Miracle Inc.";
position: fixed;
bottom: 10px;
right: 20px;
font-size: 14px;
color: rgba(180, 180, 180, 0.4);
z-index: 9999;
}


/* Sidebar glow */
section[data-testid="stSidebar"] {
box-shadow: 0 0 10px rgba(0, 123, 255, 0.5);
}
</style>
""", unsafe_allow_html=True)


# ============ SAMPLE DATA ============
dates = pd.date_range(start="2024-01-01", periods=180)
demand = np.random.poisson(lam=200, size=len(dates))
inventory = np.clip(1000 - np.cumsum(np.random.randint(100, 200, size=len(dates))) + np.random.randint(50, 150, size=len(dates)), 0, None)
data = pd.DataFrame({"Date": dates, "Demand": demand, "Inventory": inventory})


# ============ SIDEBAR ============
with st.sidebar:
st.image("miracle-logo-dark.png", use_column_width=True)
st.markdown("---")
st.title("🛠 Controls")
theme = st.radio("Theme Mode", ["Light", "Dark"], help="Switch between app themes")
threshold = st.slider("Critical Inventory Threshold", min_value=0, max_value=1000, value=300, step=10, help="Below this value, inventory is critical")
with st.expander("ℹ️ Info"):
st.markdown("This dashboard tracks demand & inventory with critical level detection, KPI summaries, and forecast insights.")


# ============ KPI CARDS ============
total_demand = int(data["Demand"].sum())
avg_inventory = int(data["Inventory"].mean())
critical_breaches = int((data["Inventory"] < threshold).sum())


kpi1, kpi2, kpi3 = st.columns(3)
kpi1.metric("📦 Total Demand", f"{total_demand}")
kpi2.metric("📉 Avg Inventory", f"{avg_inventory}")
kpi3.metric("⚠️ Critical Breaches", f"{critical_breaches}")


# ============ CONDITIONAL FORMATTING COLORS ============
def get_inventory_color(val):
return "red" if val < threshold else "green"


colors = data["Inventory"].apply(get_inventory_color)


# ============ HISTORICAL DEMAND (ANIMATED) ============
frames = []
for i in range(10, len(data), 5):
frames.append(go.Frame(data=[go.Scatter(x=data["Date"][:i], y=data["Demand"][:i], mode="lines+markers")]))


fig_demand = go.Figure(
data=[go.Scatter(x=data["Date"][:10], y=data["Demand"][:10], mode="lines+markers")],
layout=go.Layout(
title="Historical Demand (Animated)",
xaxis=dict(rangeslider=dict(visible=True)),
yaxis_title="Units",
updatemenus=[dict(
st.plotly_chart(fig_inventory, use_container_width=True)
