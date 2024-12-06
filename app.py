import streamlit as st
import openai
import pandas as pd
import plotly.express as px
import os
from dotenv import load_dotenv
import plotly.graph_objects as go
import altair as alt
import snowflake.connector



# Connect to Snowflake
def get_snowflake_data(query):
  
    
    cursor = st.connection("snowflake").cursor()
    cursor.execute(query)
    df = cursor.fetch_pandas_all()  # Fetches data as a Pandas DataFrame
    conn.close()
    
    return df

# Streamlit Layout
st.title('Interactive Airbnb Listings Dashboard')

# Date Picker for Filtering Data by Timestamp
st.sidebar.header("Filter by Date Range")
start_date = st.sidebar.date_input('Start Date', pd.to_datetime('2023-01-01'))
end_date = st.sidebar.date_input('End Date', pd.to_datetime('2024-12-31'))

# Query 1: Get data within the selected date range
query_data = f"""
    SELECT CATEGORY, PRICE, LAT, LONG, TIMESTAMP
    FROM AIRBNB_PROPERTIES_INFORMATION
    WHERE TIMESTAMP BETWEEN '{start_date}' AND '{end_date}'
"""
df = get_snowflake_data(query_data)

# Sidebar filter for Category
st.sidebar.header("Filter by Category")
category_options = df['CATEGORY'].unique()
selected_category = st.sidebar.multiselect('Select Category:', category_options, default=category_options)

# Apply the category filter
filtered_df = df[df['CATEGORY'].isin(selected_category)]

# Price Distribution by Category (Interactive Box Plot)
st.subheader("Price Distribution by Category")
fig1 = px.box(filtered_df, x='CATEGORY', y='PRICE', title="Price Distribution by Category")
st.plotly_chart(fig1)

# Query 2: Get average price and count of listings by category
query_avg_price = f"""
    SELECT CATEGORY, AVG(PRICE) AS AVG_PRICE, COUNT(*) AS LISTINGS_COUNT
    FROM AIRBNB_PROPERTIES_INFORMATION
    WHERE TIMESTAMP BETWEEN '{start_date}' AND '{end_date}'
    GROUP BY CATEGORY
"""
avg_price_df = get_snowflake_data(query_avg_price)

# Display average price and total listings count
st.subheader("Average Price and Listings Count by Category")
st.write(avg_price_df)

# Query 3: Get geographical distribution of listings by category
query_location = f"""
    SELECT LAT, LONG, CATEGORY
    FROM AIRBNB_PROPERTIES_INFORMATION
    WHERE TIMESTAMP BETWEEN '{start_date}' AND '{end_date}'
"""
location_df = get_snowflake_data(query_location)

# Geographical Distribution: Map
st.subheader("Listings Location by Latitude and Longitude")
fig2 = px.scatter_geo(location_df, lat='LAT', lon='LONG', color='CATEGORY',
                      hover_name='CATEGORY', title="Listings Location on Map")
st.plotly_chart(fig2)

# Query 4: Get price trend over time by category
query_price_trend = f"""
    SELECT TIMESTAMP, CATEGORY, AVG(PRICE) AS AVG_PRICE
    FROM AIRBNB_PROPERTIES_INFORMATION
    WHERE TIMESTAMP BETWEEN '{start_date}' AND '{end_date}'
    GROUP BY TIMESTAMP, CATEGORY
    ORDER BY TIMESTAMP
"""
price_trend_df = get_snowflake_data(query_price_trend)

# Price Trend Over Time
st.subheader("Price Trend Over Time by Category")
fig3 = px.line(price_trend_df, x='TIMESTAMP', y='AVG_PRICE', color='CATEGORY', 
               title="Price Trend Over Time by Category")
st.plotly_chart(fig3)

# Query 5: Price range per category
query_price_range = f"""
    SELECT CATEGORY, MIN(PRICE) AS MIN_PRICE, MAX(PRICE) AS MAX_PRICE
    FROM AIRBNB_PROPERTIES_INFORMATION
    WHERE TIMESTAMP BETWEEN '{start_date}' AND '{end_date}'
    GROUP BY CATEGORY
"""
price_range_df = get_snowflake_data(query_price_range)

# Price Range per Category
st.subheader("Price Range per Category")
st.write(price_range_df)

# Query 6: Number of Listings by Category over Time
query_listing_trend = f"""
    SELECT TIMESTAMP, CATEGORY, COUNT(*) AS LISTINGS_COUNT
    FROM AIRBNB_PROPERTIES_INFORMATION
    WHERE TIMESTAMP BETWEEN '{start_date}' AND '{end_date}'
    GROUP BY TIMESTAMP, CATEGORY
    ORDER BY TIMESTAMP
"""
listing_trend_df = get_snowflake_data(query_listing_trend)

# Listings Count Over Time
st.subheader("Listing Count Over Time by Category")
fig4 = px.line(listing_trend_df, x='TIMESTAMP', y='LISTINGS_COUNT', color='CATEGORY', 
               title="Listing Count Over Time by Category")
st.plotly_chart(fig4)

# Additional Metrics
total_listings = len(filtered_df)
avg_price_all = filtered_df['PRICE'].mean()

st.sidebar.header("Summary Statistics")
st.sidebar.write(f"Total Listings: {total_listings}")
st.sidebar.write(f"Average Price (All Listings): ${avg_price_all:,.2f}")

# Optional: Show Filtered Data in Table
st.subheader("Filtered Data Table")
st.dataframe(filtered_df, use_container_width=True)
