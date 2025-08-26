# app.py
import streamlit as st
import pandas as pd
import snowflake.connector
from prophet import Prophet
from prophet.plot import plot_plotly
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from datetime import date
import warnings

# ==============================
# PAGE CONFIG
# ==============================
st.set_page_config(
    page_title="Demand Forecast & Inventory Optimization",
    page_icon="miracle-logo-dark.png",  # Favicon
    layout="wide"
)

# ==============================
# CUSTOM CSS FOR STICKY HEADER
# ==============================
st.markdown(
    """
    <style>
        .header-bar {
            background-color: #002244;
            padding: 10px 0;
            position: sticky;
            top: 0;
            z-index: 999;
            border-radius: 0 0 10px 10px;
            text-align: center;
        }
        .header-bar img {
            height: 60px;
        }
        .header-bar h1 {
            color: white;
            margin: 10px 0 0 0;
            font-size: 24px;
        }
    </style>

    <div class="header-bar">
        <img src="miracle-logo-dark.png">
        <h1>Demand Forecast & Inventory Optimization</h1>
    </div>
    """,
    unsafe_allow_html=True
)

# ==============================
# WARNINGS
# ==============================
warnings.filterwarnings("ignore")

# ==============================
# SIDEBAR: LOGO + FILTERS
# ==============================
with st.sidebar:
    st.image("miracle-logo-dark.png", width=180)
    st.markdown("### Miracle Insights")
    st.markdown("---")

    theme = st.radio("Theme Mode", ["Light", "Dark"], horizontal=True)
    if theme == "Dark":
        st.markdown(
            """<style>body { background-color: #1e1e1e; color: white; }</style>""",
            unsafe_allow_html=True
        )

st.sidebar.header("Filters")

# ==============================
# SNOWFLAKE CONNECTION SETTINGS
# ==============================
SNOWFLAKE_USER = st.secrets["snowflake"]["USER"]
SNOWFLAKE_PASSWORD = st.secrets["snowflake"]["PASSWORD"]
SNOWFLAKE_ACCOUNT = st.secrets["snowflake"]["ACCOUNT"]
SNOWFLAKE_WAREHOUSE = st.secrets["snowflake"]["WAREHOUSE"]
SNOWFLAKE_DATABASE = "DEMAND_FORECASTING_DB"
SNOWFLAKE_SCHEMA = "INVENTORY_OPT_SCHEMA"
TABLE_NAME = "DEMAND_INVENTORY"

# ==============================
# PRODUCT MAPPING
# ==============================
product_map = {
    "P001": "Gear Shaft",
    "P002": "Bearing Set",
    "P003": "Drive Belt",
    "P004": "Hydraulic Pump",
    "P005": "Valve Assembly"
}

# ==============================
# FUNCTION: Load data from Snowflake
# ==============================
@st.cache_data(ttl=600)
def load_data(product_id, start_date, end_date, season):
    conn = snowflake.connector.connect(
        user=SNOWFLAKE_USER,
        password=SNOWFLAKE_PASSWORD,
        account=SNOWFLAKE_ACCOUNT,
        warehouse=SNOWFLAKE_WAREHOUSE,
        database=SNOWFLAKE_DATABASE,
        schema=SNOWFLAKE_SCHEMA
    )

    where_clauses = [f"product_id = '{product_id}'"]
    where_clauses.append(f"week_start >= '{start_date}'")
    where_clauses.append(f"week_start <= '{end_date}'")
    if season != "All":
        where_clauses.append(f"season = '{season}'")
    where_sql = " AND ".join(where_clauses)

    query = f"""
        SELECT *
        FROM {SNOWFLAKE_DATABASE}.{SNOWFLAKE_SCHEMA}.{TABLE_NAME}
        WHERE {where_sql}
        ORDER BY week_start;
    """
    df = pd.read_sql(query, conn)
    conn.close()
    df.columns = [col.lower() for col in df.columns]
    return df

# ==============================
# SIDEBAR FILTERS CONTINUED
# ==============================
product_display = st.sidebar.selectbox("Select Product", options=list(product_map.values()))
product_choice = [k for k, v in product_map.items() if v == product_display][0]

default_start = date(2023, 1, 1)
default_end = date.today()
start_date = st.sidebar.date_input("Start Date", default_start)
end_date = st.sidebar.date_input("End Date", default_end)

season_choice = st.sidebar.selectbox("Select Season", ["All", "Winter", "Spring", "Summer", "Fall"])
forecast_weeks = st.sidebar.slider("Weeks to Forecast", min_value=4, max_value=24, value=8)

# ==============================
# LOAD DATA
# ==============================
data = load_data(product_choice, start_date, end_date, season_choice)
if data.empty:
    st.warning("No data matches your filters.")
    st.stop()

st.write(f"### Product: {data['product_name'].iloc[0]} ({product_choice}) — Filtered View")

# ==============================
# CRITICAL THRESHOLD SLIDER
# ==============================
default_threshold = int(data["inventory_on_hand"].mean() * 0.25)
user_threshold = st.slider("Set Critical Inventory Threshold", min_value=0, max_value=500, value=default_threshold)

# ==============================
# HISTORICAL CHARTS (Interactive)
# ==============================
col1, col2 = st.columns(2)
with col1:
    st.subheader("Weekly Units Sold")
    units_fig = go.Figure()
    units_fig.add_trace(go.Scatter(x=data["week_start"], y=data["units_sold"], mode='lines+markers', name='Units Sold'))
    units_fig.update_layout(title="Historical Demand", xaxis_title="Week", yaxis_title="Units Sold")
    st.plotly_chart(units_fig, use_container_width=True)

with col2:
    st.subheader("Inventory On Hand")
    inventory_fig = go.Figure()
    inventory_fig.add_trace(go.Scatter(x=data["week_start"], y=data["inventory_on_hand"], mode='lines+markers', name='Inventory'))
    inventory_fig.add_hline(y=user_threshold, line_dash="dash", line_color="red", annotation_text="Critical Level")
    inventory_fig.update_layout(title="Inventory Levels", xaxis_title="Week", yaxis_title="Inventory")
    st.plotly_chart(inventory_fig, use_container_width=True)

# ==============================
# DEMAND FORECASTING
# ==============================
st.subheader("Forecasted Demand")

df_prophet = data.rename(columns={"week_start": "ds", "units_sold": "y"})
df_prophet["ds"] = pd.to_datetime(df_prophet["ds"])

if len(df_prophet) < 4:
    st.warning("Not enough historical data for forecasting.")
    st.stop()

model = Prophet()
model.fit(df_prophet)

future = model.make_future_dataframe(periods=forecast_weeks, freq="W")
forecast = model.predict(future)

st.plotly_chart(plot_plotly(model, forecast), use_container_width=True)

# ==============================
# INVENTORY REORDER POINT
# ==============================
st.subheader("Reorder Point Recommendation")
lead_time = int(data["lead_time_days"].iloc[0])
weeks_lead = max(1, lead_time // 7)

forecast_tail = forecast.tail(weeks_lead)
forecast_mean = forecast_tail["yhat"].mean()
forecast_std = forecast_tail["yhat"].std()
forecast_std = 0 if np.isnan(forecast_std) else forecast_std
z_score = 1.65

reorder_point = forecast_mean * weeks_lead + z_score * forecast_std * np.sqrt(weeks_lead)
reorder_point = max(0, reorder_point)

st.metric(label="Recommended Reorder Point (units)", value=f"{int(reorder_point):,}")

# ==============================
# DOWNLOAD FORECAST
# ==============================
st.download_button(
    label="📥 Download Forecast CSV",
    data=forecast.to_csv(index=False).encode('utf-8'),
    file_name=f"{product_choice}_forecast.csv",
    mime='text/csv'
)

# ==============================
# RAW DATA VIEW
# ==============================
with st.expander("View Raw Data from Snowflake"):
    st.dataframe(data)
