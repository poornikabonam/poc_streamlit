import streamlit as st
import pandas as pd
import json
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import numpy as np
from wordcloud import WordCloud
import matplotlib.pyplot as plt

# Page config
st.set_page_config(page_title="Airbnb Analytics Dashboard", layout="wide")

# Function to execute SQL queries
def execute_sql(query):
    cursor = st.connection("snowflake").cursor()
    cursor.execute(query)
    result = cursor.fetchall()
    columns = [col[0] for col in cursor.description]
    df = pd.DataFrame(result, columns=columns)
    return df

# Function to extract numeric rating from string
def extract_rating(rating_str):
    if isinstance(rating_str, str):
        try:
            return float(rating_str.replace(',', '.'))
        except:
            return None
    return None

# Function to parse price
def parse_price(price_str):
    if isinstance(price_str, str):
        try:
            price_dict = json.loads(price_str)
            return float(price_dict['value'])
        except:
            return None
    return None

# Load data
@st.cache_data
def load_data():
    query = """
    SELECT * FROM AIRBNB_PROPERTIES_INFORMATION
    """
    df = execute_sql(query)
    
    # Parse prices
    df['price_value'] = df['PRICE'].apply(parse_price)
    
    # Parse ratings
    if 'CATEGORY_RATING' in df.columns:
        df['ratings_dict'] = df['CATEGORY_RATING'].apply(lambda x: 
            json.loads(x.replace("'", '"')) if isinstance(x, str) else None)
        
        # Extract individual ratings
        rating_types = ['Cleanliness', 'Accuracy', 'Communication', 'Location', 'Check-in', 'Value']
        for rating_type in rating_types:
            df[f'rating_{rating_type.lower()}'] = df['ratings_dict'].apply(
                lambda x: extract_rating(next((item['value'] for item in x if item['name'] == rating_type), None)) 
                if isinstance(x, list) else None
            )
    
    return df

# Load the data
df = load_data()

# Dashboard Title
st.title("🏠 Airbnb Listings Analytics Dashboard")

# Metrics Row
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Total Listings", len(df))
with col2:
    avg_price = df['price_value'].mean()
    st.metric("Average Price", f"${avg_price:.2f}")
with col3:
    avg_rating = df['rating_cleanliness'].mean()
    st.metric("Average Cleanliness Rating", f"{avg_rating:.1f}")
with col4:
    pets_allowed = (df['PETS_ALLOWED'] == True).sum()
    st.metric("Pet-Friendly Listings", pets_allowed)

# Price Distribution
st.subheader("Price Distribution")
fig_price = px.histogram(
    df, 
    x='price_value',
    nbins=50,
    title="Distribution of Listing Prices",
    labels={'price_value': 'Price ($)', 'count': 'Number of Listings'}
)
st.plotly_chart(fig_price, use_container_width=True)

# Ratings Analysis
st.subheader("Ratings Analysis")
col1, col2 = st.columns(2)

with col1:
    # Radar Chart for Average Ratings
    rating_cols = ['rating_cleanliness', 'rating_accuracy', 'rating_communication', 
                  'rating_location', 'rating_check_in', 'rating_value']
    rating_names = ['Cleanliness', 'Accuracy', 'Communication', 
                   'Location', 'Check-in', 'Value']
    
    avg_ratings = [df[col].mean() for col in rating_cols]
    
    fig_radar = go.Figure()
    fig_radar.add_trace(go.Scatterpolar(
        r=avg_ratings,
        theta=rating_names,
        fill='toself',
        name='Average Ratings'
    ))
    fig_radar.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 5])),
        showlegend=False,
        title="Average Ratings by Category"
    )
    st.plotly_chart(fig_radar, use_container_width=True)

with col2:
    # Price vs Rating Scatter Plot
    fig_scatter = px.scatter(
        df,
        x='price_value',
        y='rating_value',
        title="Price vs Value Rating",
        labels={'price_value': 'Price ($)', 'rating_value': 'Value Rating'}
    )
    st.plotly_chart(fig_scatter, use_container_width=True)

# Map of Listings
st.subheader("Geographical Distribution")
map_data = df[['LAT', 'LONG', 'NAME', 'price_value']].dropna()
st.map(map_data)

# Reviews Analysis
st.subheader("Review Analysis")
if 'REVIEWS' in df.columns:
    # Combine all reviews into a single string
    all_reviews = ' '.join([str(review) for review in df['REVIEWS'] if isinstance(review, str)])
    
    # Generate word cloud
    wordcloud = WordCloud(width=800, height=400, background_color='white').generate(all_reviews)
    
    # Display word cloud
    plt.figure(figsize=(10, 5))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off')
    st.pyplot(plt)

# Filters Sidebar
st.sidebar.title("Filters")
price_range = st.sidebar.slider(
    "Price Range",
    min_value=float(df['price_value'].min()),
    max_value=float(df['price_value'].max()),
    value=(float(df['price_value'].min()), float(df['price_value'].max()))
)

pets_filter = st.sidebar.checkbox("Show Only Pet-Friendly Listings")

# Apply filters
filtered_df = df[
    (df['price_value'] >= price_range[0]) &
    (df['price_value'] <= price_range[1])
]

if pets_filter:
    filtered_df = filtered_df[filtered_df['PETS_ALLOWED'] == True]

# Show filtered data
st.subheader("Filtered Listings")
st.dataframe(
    filtered_df[['NAME', 'price_value', 'rating_cleanliness', 'PETS_ALLOWED']].head(10),
    use_container_width=True
)
