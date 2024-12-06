import streamlit as st
import openai
import pandas as pd
import plotly.express as px
import os
from dotenv import load_dotenv
import altair as alt

# Set up the page configuration
#st.set_page_config(page_title="Airbnb Dashboard", layout="wide")

# Fetch data from Snowflake
@st.cache_data
def fetch_data(query):
    # Use Streamlit's connection method to connect to Snowflake
    cursor = st.connection("snowflake").cursor()
    cursor.execute(query)
    data = cursor.fetchall()
    columns = [desc[0] for desc in cursor.description]
    return pd.DataFrame(data, columns=columns)

# Query Airbnb data
def get_airbnb_data(date_range=None, availability=None):
    query = "SELECT date, url, amenities, availability, calendar_dates FROM AIRBNB_PROPERTIES_INFORMATION"
    filters = []
    
    if date_range:
        filters.append(f"date BETWEEN '{date_range[0]}' AND '{date_range[1]}'")
    if availability:
        filters.append("availability = TRUE")
    
    if filters:
        query += " WHERE " + " AND ".join(filters)
        
    return fetch_data(query)

# Dashboard Header
st.title("Airbnb Dashboard")
st.markdown("### Interactive Dashboard to Explore Airbnb Listings")

# Sidebar Filters
st.sidebar.header("Filter Listings")
date_range = st.sidebar.date_input("Select Date Range", [])
availability = st.sidebar.checkbox("Show Only Available Properties")

# Fetch and filter data
data = get_airbnb_data(date_range=date_range, availability=availability)

# Show filtered data
st.subheader("Filtered Data")
if data.empty:
    st.warning("No data available for the selected filters.")
else:
    st.dataframe(data)

    # Split into columns for visualizations
    col1, col2 = st.columns(2)

    # Visualization 1: Availability Distribution
    with col1:
        st.markdown("### Availability Status")
        availability_chart = alt.Chart(data).mark_bar().encode(
            x=alt.X("availability", title="Availability"),
            y=alt.Y("count()", title="Count of Listings"),
            color="availability"
        ).properties(height=400)
        st.altair_chart(availability_chart, use_container_width=True)

    # Visualization 2: Calendar Insights
    with col2:
        st.markdown("### Dates of Availability")
        calendar_data = data.explode("calendar_dates")
        calendar_chart = alt.Chart(calendar_data).mark_bar().encode(
            x=alt.X("calendar_dates:T", title="Dates"),
            y=alt.Y("count()", title="Number of Listings"),
            color=alt.Color("availability", legend=alt.Legend(title="Availability"))
        ).properties(height=400)
        st.altair_chart(calendar_chart, use_container_width=True)

    # Visualization 3: Common Amenities
    st.markdown("### Most Common Amenities")
    amenities = data["amenities"].apply(lambda x: x if x else [])
    all_amenities = [item for sublist in amenities for item in sublist]
    amenities_df = pd.DataFrame(all_amenities, columns=["Amenity"])
    top_amenities = amenities_df["Amenity"].value_counts().head(10).reset_index()
    top_amenities.columns = ["Amenity", "Count"]

    amenities_chart = alt.Chart(top_amenities).mark_bar().encode(
        x=alt.X("Count", title="Count"),
        y=alt.Y("Amenity", title="Amenity", sort="-x"),
        color=alt.Color("Count", scale=alt.Scale(scheme="blues"))
    ).properties(height=400)
    st.altair_chart(amenities_chart, use_container_width=True)

# Footer
st.markdown("---")
st.markdown("**Built with Streamlit and Snowflake** | © 2024 Your Name")
