# app.py
import streamlit as st
import pandas as pd
import plotly.graph_objs as go
from datetime import datetime

# PAGE CONFIG
st.set_page_config(page_title="Demand Forecast & Inventory Optimization", layout="wide")

# LOAD THE DATASET
@st.cache_data
def load_data():
    df = pd.read_csv("tailored_demand_inventory.csv")
    df['week_start'] = pd.to_datetime(df['week_start'])
    return df

df_full = load_data()

# SIDEBAR: Filters
with st.sidebar:
    # Display the logo at the top of the sidebar
    st.image("miracle-logo-dark.png", width=150)
    
    st.markdown("### Filters")
    
    # Get unique products and seasons for the filters
    products = sorted(df_full['product_name'].unique().tolist())
    product = st.selectbox("Select Product", products, help="Choose product to visualize")
    
    # Dynamically populate seasons, adding 'All' as a default option
    seasons = sorted(df_full['season'].unique().tolist())
    season_options = ['All'] + seasons
    season = st.selectbox("Select Season", season_options, help="Optional season filter")
    
    start_date = st.date_input("Start Date", df_full['week_start'].min())
    end_date = st.date_input("End Date", df_full['week_start'].max())
    critical_threshold = st.slider("Critical Inventory Level", min_value=100, max_value=500, value=300)

# APPLY FILTERS TO THE DATA
df_filtered = df_full[
    (df_full['product_name'] == product) &
    (df_full['week_start'] >= pd.Timestamp(start_date)) &
    (df_full['week_start'] <= pd.Timestamp(end_date))
]

if season != 'All':
    df_filtered = df_filtered[df_filtered['season'] == season]

# Check if filtered data is empty
if df_filtered.empty:
    st.warning("No data available for the selected filters.")
else:
    df_filtered["critical_breach"] = df_filtered["inventory_on_hand"] < critical_threshold

    # Inject custom CSS for KPI cards
    st.markdown("""
        <style>
            .kpi-card {
                background-color: #f0f2f6; /* A subtle grey for contrast */
                border-radius: 10px;
                padding: 20px;
                text-align: center;
                box-shadow: 0 4px 8px 0 rgba(0, 0, 0, 0.1), 0 6px 20px 0 rgba(0, 0, 0, 0.1);
                transition: transform 0.3s ease-in-out;
            }
            .kpi-card:hover {
                transform: translateY(-5px); /* Creates the "levitating" effect */
            }
            .kpi-value {
                font-size: 2.5em;
                font-weight: bold;
                color: #007bff; /* Highlight color */
                margin-top: 10px;
            }
            .kpi-label {
                font-size: 1.1em;
                color: #555;
            }
        </style>
    """, unsafe_allow_html=True)
    
    # KPI CARDS - Now using custom HTML for styling
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.markdown(f'<div class="kpi-card"><div class="kpi-label">📦 Total Demand</div><div class="kpi-value">{df_filtered["units_sold"].sum()}</div></div>', unsafe_allow_html=True)
    with col2:
        st.markdown(f'<div class="kpi-card"><div class="kpi-label">📊 Avg Inventory</div><div class="kpi-value">{int(df_filtered["inventory_on_hand"].mean())}</div></div>', unsafe_allow_html=True)
    with col3:
        pct_critical = 100 * df_filtered['critical_breach'].mean()
        st.markdown(f'<div class="kpi-card"><div class="kpi-label">🚨 % Critical Breaches</div><div class="kpi-value">{pct_critical:.2f}%</div></div>', unsafe_allow_html=True)
    with col4:
        total_revenue = (df_filtered['units_sold'] * df_filtered['unit_price']).sum()
        st.markdown(f'<div class="kpi-card"><div class="kpi-label">💰 Total Revenue</div><div class="kpi-value">${total_revenue:,.2f}</div></div>', unsafe_allow_html=True)
    with col5:
        avg_lead_time = df_filtered['lead_time_days'].mean()
        st.markdown(f'<div class="kpi-card"><div class="kpi-label">⏳ Avg Lead Time</div><div class="kpi-value">{avg_lead_time:.1f} days</div></div>', unsafe_allow_html=True)

    # TITLE
    st.markdown(f"## Product: {product} — Filtered View")
    st.markdown("### Weekly Units Sold")

    # DEMAND GRAPH - Now a static line chart
    fig1 = go.Figure()
    fig1.add_trace(go.Scatter(x=df_filtered['week_start'], y=df_filtered['units_sold'],
                                mode='lines+markers',
                                line=dict(color='royalblue'),
                                name="Units Sold"))
    fig1.update_layout(
        xaxis_title="Date",
        yaxis_title="Units Sold",
        template="plotly_white",
        height=400,
        margin=dict(t=10, r=10, l=10, b=10)
    )

    # INVENTORY LEVELS WITH ALERT LINE
    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(
        x=df_filtered["week_start"],
        y=df_filtered["inventory_on_hand"],
        mode="lines+markers",
        name="Inventory",
        line=dict(color="mediumseagreen")
    ))
    fig2.add_trace(go.Scatter(
        x=df_filtered["week_start"],
        y=[critical_threshold]*len(df_filtered),
        mode="lines",
        name="Critical Level",
        line=dict(color="red", dash="dash")
    ))

    fig2.update_layout(
        title="Inventory On Hand",
        xaxis_title="Date",
        yaxis_title="Inventory",
        template="plotly_white",
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
    if df_filtered["critical_breach"].any():
        st.warning("⚠️ Critical inventory threshold breached in the selected period!")
