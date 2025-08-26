import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import numpy as np

# ================================
# PAGE CONFIG
# ================================
st.set_page_config(page_title="Demand Forecast Dashboard", page_icon="📈", layout="wide")

# ================================
# CUSTOM CSS FOR BACKGROUND AND SIDEBAR
# ================================
st.markdown("""
    <style>
    body {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%) !important;
    }
    .stApp {
        background-image: url('https://upload.wikimedia.org/wikipedia/commons/thumb/2/27/Miracle_Software_Systems_Logo.svg/512px-Miracle_Software_Systems_Logo.svg.png');
        background-repeat: no-repeat;
        background-position: bottom right;
        background-size: 150px;
        opacity: 0.98;
    }
    [data-testid="stSidebar"] {
        box-shadow: 0 0 15px rgba(0, 123, 255, 0.3);
    }
    </style>
""", unsafe_allow_html=True)

# ================================
# SIDEBAR CONTROLS
# ================================
st.sidebar.image("miracle-logo-dark.png", use_column_width=True)

critical_threshold = st.sidebar.slider("Set Critical Inventory Level", min_value=0, max_value=200, value=50, step=5)

# ================================
# SAMPLE DATA CREATION
# ================================
dates = pd.date_range(start="2024-01-01", end=datetime.today(), freq='D')
np.random.seed(42)
demand = np.random.poisson(lam=80, size=len(dates))

inventory = []
inv = 100
for d in demand:
    inv = max(inv - d + np.random.randint(40, 100), 0)
    inventory.append(inv)

# Create DataFrame
df = pd.DataFrame({
    'Date': dates,
    'Demand': demand,
    'Inventory_Level': inventory
})

# ================================
# DEMAND CHART WITH STOCK-STYLE INTERACTION
# ================================
st.subheader("📊 Historical Demand")
demand_fig = go.Figure()
demand_fig.add_trace(go.Scatter(x=df['Date'], y=df['Demand'], mode='lines+markers', name='Demand'))

demand_fig.update_layout(
    hovermode="x unified",
    xaxis=dict(
        rangeselector=dict(
            buttons=list([
                dict(count=1, label="1m", step="month", stepmode="backward"),
                dict(count=6, label="6m", step="month", stepmode="backward"),
                dict(step="all")
            ])
        ),
        rangeslider=dict(visible=True),
        type="date"
    ),
    yaxis_title="Demand",
    margin=dict(t=10, b=30)
)
st.plotly_chart(demand_fig, use_container_width=True)

# ================================
# INVENTORY LEVELS WITH CRITICAL THRESHOLD
# ================================
st.subheader("📦 Inventory Levels")
inventory_fig = go.Figure()
inventory_fig.add_trace(go.Scatter(x=df['Date'], y=df['Inventory_Level'], mode='lines+markers', name='Inventory Level'))

# Add critical threshold line
inventory_fig.add_hline(y=critical_threshold, line_dash="dash", line_color="red", annotation_text="Critical Level", annotation_position="top right")

inventory_fig.update_layout(
    hovermode="x unified",
    xaxis=dict(
        rangeselector=dict(
            buttons=list([
                dict(count=1, label="1m", step="month", stepmode="backward"),
                dict(count=6, label="6m", step="month", stepmode="backward"),
                dict(step="all")
            ])
        ),
        rangeslider=dict(visible=True),
        type="date"
    ),
    yaxis_title="Inventory Level",
    margin=dict(t=10, b=30)
)
st.plotly_chart(inventory_fig, use_container_width=True)

# ================================
# FOOTER
# ================================
st.markdown("""
    <div style='text-align: center; padding-top: 20px;'>
        <small>© 2025 Miracle Software Systems. All rights reserved.</small>
    </div>
""", unsafe_allow_html=True)
