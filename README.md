This Python script creates a comprehensive Demand Forecasting and Inventory Optimization dashboard using the Streamlit library. The application connects to a Snowflake database to retrieve sales and inventory data, performs time-series forecasting, and recommends an inventory reorder point.
**Key Functionalities:**
**1. Data Connection and Filtering:**
Snowflake Integration: The application securely connects to a Snowflake data warehouse using credentials stored in Streamlit's secrets management.[1][2]
User-Driven Filters: A sidebar allows users to filter the data by product, date range, and season. This interactivity enables customized analysis for specific business needs.
Cached Data Loading: The load_data function uses Streamlit's caching (@st.cache_data) to store data retrieved from Snowflake for 10 minutes. This improves performance by avoiding repeated database queries when the user changes filters that don't require new data.
**2. Data Visualization:**
Historical Trends: The dashboard displays two line charts for visualizing historical data: one for weekly units sold (demand) and another for inventory on-hand levels.
Interactive Charts: It uses the Plotly library to create interactive charts, allowing users to hover over data points for more detail.
**3. Predictive Forecasting:**
Time-Series Modeling: The script employs the Prophet library, an open-source forecasting tool developed by Facebook, to predict future demand. Prophet is adept at handling time-series data with seasonal patterns.[3][4]
Forecasting Horizon: Users can select the number of future weeks (from 4 to 24) for which they want to generate a demand forecast.
Forecast Visualization: The forecast, including upper and lower uncertainty intervals, is plotted on an interactive chart, providing a clear visual representation of predicted future demand.[5]
**4. Inventory Management:**
Reorder Point Calculation: The application calculates a recommended "Reorder Point," which is the inventory level at which a new order should be placed to avoid stockouts.
Safety Stock Formula: The calculation is based on a standard inventory management formula: Reorder Point = (Demand during lead time) + Safety Stock.[6][7] In this script, it specifically uses the forecasted demand and its variability to determine these values, aiming for a 95% service level (the probability of not stocking out).
**5. User Interface and Experience:**
Streamlit Framework: The entire application is built with Streamlit, an open-source Python framework that simplifies the creation of web-based data apps.[8][9][10]
Clear Layout: The app is organized with a main panel for charts and metrics, a sidebar for controls, and an expandable section to view the raw data.
Error Handling: The script includes checks to ensure there is sufficient data for forecasting and gracefully handles cases where no data matches the user's filters.
