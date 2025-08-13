# app.py
import streamlit as st
import pandas as pd
import snowflake.connector
from prophet import Prophet
from prophet.plot import plot_plotly
import plotly.express as px
import numpy as np
from datetime import date
import warnings

# ==============================
# PAGE CONFIG
# ==============================
st.set_page_config(page_title="Demand Forecast & Inventory Optimization", layout="wide")

# ==============================
# WARNINGS
# ==============================
warnings.filterwarnings("ignore")

# ==============================
# SNOWFLAKE CONNECTION SETTINGS (use Streamlit secrets)
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
# FUNCTION: Load data from Snowflake with filters
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
        SELECT
            week_start,
            product_id,
            product_name,
            units_sold,
            inventory_on_hand,
            lead_time_days,
            season,
            promotions,
            unit_price
        FROM {SNOWFLAKE_DATABASE}.{SNOWFLAKE_SCHEMA}.{TABLE_NAME}
        WHERE {where_sql}
        ORDER BY week_start;
    """
    df = pd.read_sql(query, conn)
    conn.close()
    df.columns = [col.lower() for col in df.columns]  # ✅ Normalize columns
    return df

# ==============================
# SIDEBAR FILTERS
# ==============================
st.sidebar.header("Filters")

product_display = st.sidebar.selectbox(
    "Select Product",
    options=list(product_map.values())
)
product_choice = [k for k, v in product_map.items() if v == product_display][0]

default_start = date(2023, 1, 1)
default_end = date.today()
start_date = st.sidebar.date_input("Start Date", default_start)
end_date = st.sidebar.date_input("End Date", default_end)

season_choice = st.sidebar.selectbox(
    "Select Season",
    ["All", "Winter", "Spring", "Summer", "Fall"]
)

forecast_weeks = st.sidebar.slider("Weeks to Forecast", min_value=4, max_value=24, value=8)

# ==============================
# LOAD DATA
# ==============================
data = load_data(product_choice, start_date, end_date, season_choice)

if data.empty:
    st.warning("No data matches your filters.")
    st.stop()

st.title("📊 Demand Forecast & Inventory Optimization")
#st.caption(f"Data Source: {SNOWFLAKE_DATABASE}.{SNOWFLAKE_SCHEMA}.{TABLE_NAME}")
st.write(f"### Product: {data['product_name'].iloc[0]} ({product_choice}) — Filtered View")

# ==============================
# HISTORICAL CHARTS
# ==============================
col1, col2 = st.columns(2)
with col1:
    st.subheader("Weekly Units Sold")
    st.plotly_chart(
        px.line(data, x="week_start", y="units_sold", title="Historical Demand"),
        use_container_width=True
    )

with col2:
    st.subheader("Inventory On Hand")
    st.plotly_chart(
        px.line(data, x="week_start", y="inventory_on_hand", title="Inventory Levels"),
        use_container_width=True
    )

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

# ✅ Handle the case where std is NaN (e.g., when weeks_lead is 1)
if np.isnan(forecast_std):
    forecast_std = 0

z_score = 1.65  # 95% service level

reorder_point = forecast_mean * weeks_lead + z_score * forecast_std * np.sqrt(weeks_lead)

# ✅ Ensure reorder_point is not negative before displaying
reorder_point = max(0, reorder_point) 

st.metric(label="Recommended Reorder Point (units)", value=f"{int(reorder_point):,}")

# ==============================
# RAW DATA VIEW
# ==============================
with st.expander("View Raw Data from Snowflake"):
    st.dataframe(data)


