import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import json
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import altair as alt
import pydeck as pdk
from streamlit_lottie import st_lottie
import requests
from streamlit_folium import st_folium
import folium
from PIL import Image
import ast
import re

# Page configuration with custom theme
st.set_page_config(
    page_title="🏠 Ultimate Airbnb Analytics",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main {
        background-color: #fafafa;
    }
    .stButton>button {
        color: #ffffff;
        background-color: #ff385c;
        border-radius: 20px;
        padding: 10px 24px;
        border: none;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background-color: #dd2d50;
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(255, 56, 92, 0.3);
    }
    div[data-testid="stMetricValue"] {
        font-size: 28px;
        color: #ff385c;
    }
    .metric-card {
        background-color: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        transition: all 0.3s ease;
    }
    .metric-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 15px rgba(0, 0, 0, 0.1);
    }
    .plot-container {
        background-color: white;
        border-radius: 10px;
        padding: 20px;
        margin: 10px 0;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .custom-tab {
        background-color: white;
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)

# Load Lottie animation
@st.cache_data
def load_lottieurl(url):
    r = requests.get(url)
    return r.json() if r.status_code == 200 else None

# Function to execute SQL queries
@st.cache_data
def execute_sql(query):
    cursor = st.connection("snowflake").cursor()
    cursor.execute(query)
    result = cursor.fetchall()
    columns = [col[0] for col in cursor.description]
    return pd.DataFrame(result, columns=columns)

# Data processing functions
def parse_json_field(field):
    if isinstance(field, str):
        try:
            return json.loads(field.replace("'", '"'))
        except:
            return None
    return None

def extract_rating(rating_dict, key):
    try:
        if isinstance(rating_dict, list):
            rating = next((item['value'] for item in rating_dict if item['name'] == key), None)
            return float(str(rating).replace(',', '.')) if rating else None
    except:
        return None
    return None

def parse_price(price_str):
    if isinstance(price_str, str):
        try:
            price_dict = json.loads(price_str)
            return float(price_dict['value'])
        except:
            return None
    return None

def parse_dates(dates_str):
    if isinstance(dates_str, str):
        try:
            return dates_str.split(',')
        except:
            return []
    return []

# Load and process data
@st.cache_data
def load_data():
    df = execute_sql("SELECT * FROM AIRBNB_PROPERTIES_INFORMATION where category='Stays'")
    
    # Process prices
    df['price_value'] = df['PRICE'].apply(parse_price)
    
    # Process ratings
    df['ratings_dict'] = df['CATEGORY_RATING'].apply(parse_json_field)
    rating_types = ['Cleanliness', 'Accuracy', 'Communication', 'Location', 'Check-in', 'Value']
    for rating_type in rating_types:
        df[f'rating_{rating_type.lower()}'] = df['ratings_dict'].apply(
            lambda x: extract_rating(x, rating_type)
        )
    
    # Process amenities
    df['amenities_list'] = df['AMENITIES'].apply(lambda x: 
        [item[items['name']] for item in parse_json_field(x)] if parse_json_field(x) else []
    )
    
    # Process availability dates
    df['available_dates_list'] = df['AVAILABLE_DATES'].apply(parse_dates)
    df['availability_count'] = df['available_dates_list'].apply(len)
    
    # Process images
    df['image_list'] = df['IMAGES'].apply(lambda x: 
        x.split(',') if isinstance(x, str) else []
    )
    df['image_count'] = df['image_list'].apply(len)
    
    return df

# Load data
df = load_data()

# Header section
col1, col2 = st.columns([3, 1])
with col1:
    st.title("🏠 Ultimate Airbnb Analytics Dashboard")
    st.markdown("Comprehensive analysis of all Airbnb listings with advanced insights")

# Main metrics
col1, col2, col3, col4 = st.columns(4)
with col1:
    with st.container():
        st.metric("Total Listings", f"{len(df):,}")
with col2:
    with st.container():
        st.metric("Average Price", f"${df['price_value'].mean():,.2f}")
with col3:
    with st.container():
        st.metric("Average Rating", f"{df['rating_cleanliness'].mean():.2f}⭐")
with col4:
    with st.container():
        st.metric("Available Properties", 
                 f"{df[df['availability_count'] > 0].shape[0]:,}")

# Create tabs for different analyses
tabs = st.tabs(["📊 Overview", "🗺️ Location Analysis", "💰 Pricing Insights", 
                "⭐ Ratings & Reviews", "🏠 Property Details"])

# Overview Tab
with tabs[0]:
    st.subheader("Property Distribution")
    
    # Property types distribution
    fig = px.pie(df, names='CATEGORY', title='Property Types Distribution')
    st.plotly_chart(fig, use_container_width=True)
    
    # Availability trends
    st.subheader("Availability Trends")
    availability_df = pd.DataFrame({
        'date': df['available_dates_list'].explode()
    }).value_counts().reset_index()
    fig = px.line(availability_df, x='date', y=0, 
                  title='Number of Available Properties by Date')
    st.plotly_chart(fig, use_container_width=True)

# Location Analysis Tab
with tabs[1]:
    st.subheader("Geographical Distribution")
    
    # 3D Map visualization
    st.pydeck_chart(pdk.Deck(
        map_style='mapbox://styles/mapbox/light-v9',
        initial_view_state=pdk.ViewState(
            latitude=df['LAT'].mean(),
            longitude=df['LONG'].mean(),
            zoom=11,
            pitch=50,
        ),
        layers=[
            pdk.Layer(
                'HexagonLayer',
                data=df,
                get_position=['LONG', 'LAT'],
                radius=200,
                elevation_scale=4,
                elevation_range=[0, 1000],
                pickable=True,
                extruded=True,
            ),
        ]
    ))
    
    # Price heatmap by location
    st.subheader("Price Distribution by Location")
    fig = px.scatter_mapbox(df, 
                           lat='LAT', 
                           lon='LONG', 
                           color='price_value',
                           size='rating_cleanliness',
                           hover_name='NAME',
                           zoom=10)
    fig.update_layout(mapbox_style="carto-positron")
    st.plotly_chart(fig, use_container_width=True)

# Pricing Insights Tab
with tabs[2]:
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Price Distribution")
        fig = px.histogram(df, x='price_value', nbins=50,
                          title='Price Distribution')
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("Price vs Rating")
        fig = px.scatter(df, 
                        x='price_value', 
                        y='rating_value',
                        color='rating_cleanliness',
                        size='availability_count',
                        hover_name='NAME')
        st.plotly_chart(fig, use_container_width=True)
    
    # Price trends over time
    st.subheader("Price Trends")
    fig = px.box(df, 
                 x=pd.to_datetime(df['TIMESTAMP']).dt.month, 
                 y='price_value',
                 title='Price Distribution by Month')
    st.plotly_chart(fig, use_container_width=True)

# Ratings & Reviews Tab
with tabs[3]:
    col1, col2 = st.columns(2)
    
    with col1:
        # Ratings breakdown
        st.subheader("Ratings Breakdown")
        rating_cols = ['rating_cleanliness', 'rating_accuracy', 
                      'rating_communication', 'rating_location', 
                      'rating_check_in', 'rating_value']
        rating_means = df[rating_cols].mean()
        fig = go.Figure(data=[
            go.Bar(x=rating_means.index, y=rating_means.values)
        ])
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Reviews wordcloud
        st.subheader("Common Review Terms")
        all_reviews = ' '.join(df['REVIEWS'].dropna().astype(str))
        wordcloud = WordCloud(width=800, height=400, 
                            background_color='white').generate(all_reviews)
        fig, ax = plt.subplots()
        ax.imshow(wordcloud, interpolation='bilinear')
        ax.axis('off')
        st.pyplot(fig)

# Property Details Tab
with tabs[4]:
    # Amenities analysis
    st.subheader("Popular Amenities")
    all_amenities = [item for sublist in df['amenities_list'].dropna() 
                    for item in sublist]
    amenities_count = pd.Series(all_amenities).value_counts().head(20)
    fig = px.bar(amenities_count, title='Top 20 Amenities')
    st.plotly_chart(fig, use_container_width=True)
    
    # Property details table
    st.subheader("Property Details")
    cols_to_show = ['NAME', 'CATEGORY', 'price_value', 'rating_cleanliness', 
                    'availability_count', 'image_count']
    st.dataframe(df[cols_to_show].head(10))

# Sidebar filters
with st.sidebar:
    st.header("Filters")
    
    # Price range filter
    price_range = st.slider(
        "Price Range ($)",
        min_value=int(df['price_value'].min()),
        max_value=int(df['price_value'].max()),
        value=(int(df['price_value'].min()), int(df['price_value'].max()))
    )
    
    # Rating filter
    min_rating = st.slider(
        "Minimum Rating",
        min_value=0.0,
        max_value=5.0,
        value=0.0
    )
    
    # Property type filter
    property_types = st.multiselect(
        "Property Types",
        options=df['CATEGORY'].unique()
    )
    
    # Amenities filter
    all_amenities = list(set([item for sublist in df['amenities_list'].dropna() 
                            for item in sublist]))
    selected_amenities = st.multiselect(
        "Amenities",
        options=sorted(all_amenities)
    )
    
    # Apply filters button
    apply_filters = st.button("Apply Filters")

# Apply filters if button is clicked
if apply_filters:
    filtered_df = df[
        (df['price_value'] >= price_range[0]) &
        (df['price_value'] <= price_range[1]) &
        (df['rating_cleanliness'] >= min_rating)
    ]
    
    if property_types:
        filtered_df = filtered_df[filtered_df['CATEGORY'].isin(property_types)]
    
    if selected_amenities:
        filtered_df = filtered_df[filtered_df['amenities_list'].apply(
            lambda x: all(amenity in x for amenity in selected_amenities)
        )]
    
    st.success(f"Found {len(filtered_df)} properties matching your criteria!")
    
    # Show filtered results
    st.dataframe(
        filtered_df[['NAME', 'CATEGORY', 'price_value', 'rating_cleanliness']],
        use_container_width=True
    )

# Footer
st.markdown("""
<div style='text-align: center; color: #666; padding: 20px;'>
    Powered by Streamlit & Snowflake | Created with ❤️
</div>
""", unsafe_allow_html=True)
