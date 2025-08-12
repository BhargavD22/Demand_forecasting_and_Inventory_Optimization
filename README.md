# 📊 Demand Forecast & Inventory Optimization App

This is a **Streamlit** web application that connects to **Snowflake** to visualize and forecast product demand, monitor inventory levels, and calculate reorder points using statistical forecasting (Prophet).

It is designed as a demo for **manufacturing analytics**, using a tailored demand & inventory dataset (`DEMAND_INVENTORY`) stored in Snowflake.

---

## 🚀 Features

- Connects directly to Snowflake for live data queries  
- Filters **by Product, Date Range, and Season** directly in the sidebar  
- Displays **historical demand** and **inventory levels** in interactive Plotly charts  
- Forecasts future demand using **Facebook Prophet**  
- Calculates **recommended reorder point** based on forecast and lead times  
- Supports seasonality & promotional impacts  

---

## 🗄️ Snowflake Table Used

**Database:** `DEMAND_FORECASTING_DB`  
**Schema:** `INVENTORY_OPT_SCHEMA`  
**Table:** `DEMAND_INVENTORY`

Schema:

| Column             | Type     | Description |
|--------------------|----------|-------------|
| week_start         | DATE     | Start of week (date) |
| product_id         | VARCHAR  | Product code/SKU |
| product_name       | VARCHAR  | Product name |
| units_sold         | INTEGER  | Weekly demand |
| inventory_on_hand  | INTEGER  | Stock available at week start |
| lead_time_days     | INTEGER  | Lead time for replenishment |
| season             | VARCHAR  | Season of the year |
| promotions         | INTEGER  | 0 or 1 flag for promo week |
| unit_price         | FLOAT    | Price per unit |

---

## 📦 Installation & Setup

### 1. Clone this repository

### 2. Install dependencies

Dependencies include:
- streamlit
- pandas
- numpy
- plotly
- prophet
- snowflake-connector-python

---

## 🔑 Snowflake Credentials

### Using `.streamlit/secrets.toml`

Create a folder called `.streamlit` in your project root and inside it a file named `secrets.toml` (never commit this file to GitHub):

