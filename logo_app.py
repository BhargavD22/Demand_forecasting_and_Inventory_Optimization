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
# THEME TOGGLE
# ================================
theme = st.sidebar.selectbox("Choose Theme", ["Light", "Dark"])
if theme == "Dark":
    bg_gradient = "linear-gradient(135deg, #2c3e50 0%, #4ca1af 100%)"
    sidebar_shadow = "rgba(255, 255, 255, 0.3)"
else:
    bg_gradient = "linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%)"
    sidebar_shadow = "rgba(0, 123, 255, 0.3)"

st.markdown(f"""
    <style>
    body {{
        background: {bg_gradient} !important;
    }}
    .stApp {{
        background-image: url('https://upload.wikimedia.org/wikipedia/commons/thumb/2/27/Miracle_Software_Systems_Logo.svg/512px-Miracle_Software_Systems_Logo.svg.png');
        background-repeat: no-repeat;
        background-position: bottom right;
        background-size: 150px;
        opacity: 0.98;
    }}
    [data-testid="stSidebar"] {{
        box-shadow: 0 0 15px {sidebar_shadow};
    }}
    </style>
""", unsafe_allow_html=True)

# ================================
# SIDEBAR CONTROLS WITH TOOLTIPS
# ================================
st.sidebar.image("miracle-logo-dark.png", use_column_width=True)

with st.sidebar.expander("🔧 Settings", expanded=True):
    critical_threshold = st.slider(
        "Set Critical Inventory Level",
        min_value=0,
        max_value=200,
        value=50,
        step=5,
        help="Inventory level below which alerts will be shown"
    )

# ================================
# DATA GENERATION
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
df['Is_Critical'] = df['Inventory_Level'] < critical_threshold

# ================================
# KPI CARDS
# ================================
total_demand = df['Demand'].sum()
avg_inventory = df['Inventory_Level'].mean()
critical_breach_pct = (df['Is_Critical'].sum() / len(df)) * 100

col1, col2, col3 = st.columns(3)
col1.metric("📦 Total Demand", f"{total_demand:,}")
col2.metric("🏷 Avg Inventory", f"{avg_inventory:.2f}")
col3.metric("⚠️ Critical Breach %", f"{critical_breach_pct:.1f}%")

# ================================
# DEMAND CHART WITH ANIMATION
# ================================
st.subheader("📊 Historical Demand (Animated)")
df_anim = df.copy()
df_anim['Month'] = df_anim['Date'].dt.to_period('M').astype(str)

anim_fig = px.line(
    df_anim,
    x='Date',
    y='Demand',
    animation_frame='Month',
    title='Demand Over Time',
    labels={'Demand': 'Demand', 'Date': 'Date'},
    height=500
)
anim_fig.update_layout(hovermode='x unified')
st.plotly_chart(anim_fig, use_container_width=True)

# ================================
# INVENTORY CHART WITH ALERT COLORS
# ================================
st.subheader("📦 Inventory Levels with Alerts")
inventory_fig = go.Figure()
inventory_fig.add_trace(go.Scatter(
    x=df['Date'],
    y=df['Inventory_Level'],
    mode='lines+markers',
    name='Inventory Level',
    marker=dict(
        color=np.where(df['Is_Critical'], 'red', 'green')
    )
))

# Add threshold line
inventory_fig.add_hline(
    y=critical_threshold,
    line_dash="dash",
    line_color="red",
    annotation_text="Critical Level",
    annotation_position="top right"
)

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
