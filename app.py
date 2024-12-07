import streamlit as st
import openai
import pandas as pd
import plotly.express as px
import os
from dotenv import load_dotenv
import plotly.graph_objects as go
import altair as alt
import snowflake.connector
import json

# Execute SQL query function using Streamlit's connection context
def execute_sql(query):
    # Use the context already established in Streamlit (ctx)
    cursor = st.connection("snowflake").cursor()
    cursor.execute(query)
    result = cursor.fetchall()
    columns = [col[0] for col in cursor.description]
    df = pd.DataFrame(result, columns=columns)
    return df

# Load data from Snowflake
def get_snowflake_data():
    query = "SELECT * FROM AIRBNB_PROPERTIES_INFORMATION"  # Replace with your table name
    df = execute_sql(query)
    return df

# Preprocess and clean data
def preprocess_data(data):
    # Handling JSON in 'AMENITIES' column
    data['AMENITIES'] = data['AMENITIES'].apply(json.loads)
    
    # Expanding 'AMENITIES' into individual rows
    amenities_df = data.explode('AMENITIES').reset_index(drop=True)
    #amenities_df['AMENITY'] = amenities_df['AMENITIES'].apply(lambda x: x['name'] if isinstance(x, dict) else None)
    amenities_df.drop(columns=['AMENITIES'], inplace=True)
    
    # Splitting Available Dates to list of dates
    data['AVAILABLE_DATES'] = data['AVAILABLE_DATES'].apply(lambda x: x.split(',') if isinstance(x, str) else [])
    
    # Handle missing data, etc.
    data.dropna(subset=['PRICE', 'RATINGS', 'CATEGORY'], inplace=True)
    return data, amenities_df

# Processed Data
data = get_snowflake_data()
data, amenities_df = preprocess_data(data)

# Streamlit UI Customizations
st.set_page_config(page_title="Airbnb Listings Dashboard", layout="wide", page_icon="🏠")

# Custom CSS Styling
st.markdown("""
    <style>
        .main {
            background-color: #F4F7FB;
        }
        .stButton>button {
            background-color: #008CBA;
            color: white;
            border-radius: 10px;
            font-weight: bold;
        }
        .stSlider>div>label {
            font-size: 14px;
        }
        .stSelectbox>div>label {
            font-size: 14px;
        }
        .stDataFrame {
            margin-top: 20px;
        }
        .stHeader {
            font-size: 24px;
            font-weight: bold;
        }
    </style>
""", unsafe_allow_html=True)

# Streamlit Title
st.title("Airbnb Listings Dashboard")
st.markdown("Explore Airbnb listings and insights with an interactive and visually appealing dashboard.")

# Sidebar for filtering
st.sidebar.header("Filters")
min_price = int(data['PRICE'].min())
max_price = int(data['PRICE'].max())
price_range = st.sidebar.slider("Price Range", min_price, max_price, (min_price, max_price), step=10)

categories = data['CATEGORY'].unique()
selected_category = st.sidebar.selectbox("Select Category", categories)

# Filtering based on price and category
filtered_data = data[(data['PRICE'] >= price_range[0]) & (data['PRICE'] <= price_range[1])]
filtered_data = filtered_data[filtered_data['CATEGORY'] == selected_category]

# Display Filtered Data
st.subheader("Filtered Listings")
st.write(f"Showing {filtered_data.shape[0]} listings")
st.dataframe(filtered_data[['NAME', 'PRICE', 'RATINGS', 'CATEGORY', 'DESCRIPTION', 'AVAILABLE_DATES']], height=400)

# Layout with Columns for Visualizations
col1, col2 = st.columns([3, 2])

# Price Distribution Plot
with col1:
    st.subheader("Price Distribution")
    fig_price = px.histogram(filtered_data, x="PRICE", title="Price Distribution", nbins=30, color_discrete_sequence=["#4C8BF5"])
    fig_price.update_layout(template="plotly_dark", showlegend=False)
    st.plotly_chart(fig_price, use_container_width=True)

# Ratings Distribution Plot
with col2:
    st.subheader("Ratings Distribution")
    fig_ratings = px.histogram(filtered_data, x="RATINGS", title="Ratings Distribution", nbins=20, color_discrete_sequence=["#EF476F"])
    fig_ratings.update_layout(template="plotly_dark", showlegend=False)
    st.plotly_chart(fig_ratings, use_container_width=True)

# Popular Amenities Visualization
st.subheader("Top 10 Most Common Amenities")
amenity_counts = amenities_df['AMENITY'].value_counts().head(10)
fig_amenities = px.bar(amenity_counts, x=amenity_counts.index, y=amenity_counts.values, title="Top 10 Most Common Amenities", labels={"x": "Amenity", "y": "Count"}, color=amenity_counts.values, color_continuous_scale="Viridis")
fig_amenities.update_layout(template="plotly_dark", showlegend=False)
st.plotly_chart(fig_amenities, use_container_width=True)

# Interactive Map with Listings
st.subheader("Listings Map")
fig_map = px.scatter_mapbox(
    filtered_data, 
    lat="LAT", 
    lon="LONG", 
    hover_name="NAME", 
    hover_data=["PRICE", "RATINGS"], 
    color="CATEGORY", 
    size="RATINGS", 
    size_max=10, 
    zoom=10, 
    height=600,
    title="Airbnb Listings Location Map"
)
fig_map.update_layout(mapbox_style="carto-positron")
st.plotly_chart(fig_map)

# Show selected listing details
st.subheader("Listing Details")
listing_url = st.selectbox("Select a listing to view details", filtered_data['URL'])
selected_listing = filtered_data[filtered_data['URL'] == listing_url].iloc[0]

st.write(f"**Name**: {selected_listing['NAME']}")
st.write(f"**Price**: ${selected_listing['PRICE']}")
st.write(f"**Rating**: {selected_listing['RATINGS']} stars")
st.write(f"**Category**: {selected_listing['CATEGORY']}")
st.write(f"**Description**: {selected_listing['DESCRIPTION']}")
st.write(f"**House Rules**: {selected_listing['HOUSE_RULES']}")
st.write(f"**Pets Allowed**: {selected_listing['PETS_ALLOWED']}")

# Display Images
st.image(selected_listing['IMAGES'].split(',')[0], use_column_width=True)
