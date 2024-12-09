import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import json
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import pydeck as pdk

# Page configuration
st.set_page_config(
    page_title="🏠 Stays Analytics Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
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
    }
    div[data-testid="stMetricValue"] {
        font-size: 28px;
        color: #ff385c;
    }
    .plot-container {
        background-color: white;
        border-radius: 10px;
        padding: 20px;
        margin: 10px 0;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
</style>
""", unsafe_allow_html=True)

# Function to execute SQL queries
def execute_sql(query):
    cursor = st.connection("snowflake").cursor()
    cursor.execute(query)
    result = cursor.fetchall()
    columns = [col[0] for col in cursor.description]
    return pd.DataFrame(result, columns=columns)

# Data processing functions
def parse_price(price_str):
    if isinstance(price_str, str):
        try:
            price_dict = json.loads(price_str)
            return float(price_dict['value'])
        except:
            return None
    return None

def parse_ratings(rating_str):
    if isinstance(rating_str, str):
        try:
            ratings = json.loads(rating_str.replace("'", '"'))
            rating_dict = {}
            for rating in ratings:
                value = rating.get('value', '0').replace(',', '.')
                # Convert the name to match our column naming convention
                name = rating['name'].lower().replace('-', '_')
                rating_dict[name] = float(value)
            return rating_dict
        except:
            return {}
    return {}

def parse_amenities(amenities_str):
    if isinstance(amenities_str, str):
        try:
            amenities_dict = json.loads(amenities_str.replace("'", '"'))
            amenities_by_group = {}
            for group in amenities_dict:
                group_name = group.get('group_name', 'Other')
                if 'items' in group:
                    amenities_by_group[group_name] = []
                    for item in group['items']:
                        amenity_name = item.get('name', '')
                        amenity_value = item.get('value', '')
                        if amenity_value:
                            amenities_by_group[group_name].append(
                                f"{amenity_name} ({amenity_value})")
                        else:
                            amenities_by_group[group_name].append(amenity_name)
            return amenities_by_group
        except:
            return {}
    return {}

def process_available_dates(dates_str):
    if isinstance(dates_str, str):
        return dates_str.split(',')
    return []

# Load and process data
@st.cache_data
def load_data():
    # Query only stays listings
    df = execute_sql("SELECT * FROM AIRBNB_PROPERTIES_INFORMATION WHERE CATEGORY = 'Stays'")
    
    # Process prices
    df['price_value'] = df['PRICE'].apply(parse_price)
    
    # Process ratings
    df['ratings'] = df['CATEGORY_RATING'].apply(parse_ratings)
    
    # Use consistent column names that match the data
    rating_cols = {
        'cleanliness': 'rating_cleanliness',
        'accuracy': 'rating_accuracy',
        'communication': 'rating_communication',
        'location': 'rating_location',
        'check-in': 'rating_check_in',  # Note the hyphen in the original data
        'value': 'rating_value'
    }
    
    for original, col_name in rating_cols.items():
        df[col_name] = df['ratings'].apply(lambda x: x.get(original.lower(), None))
    
    # Process amenities
    df['amenities_dict'] = df['AMENITIES'].apply(parse_amenities)
    
    # Process details
    def extract_details(details_str):
        if pd.isna(details_str):
            return None, None, None
        parts = str(details_str).split(',')
        guests = rooms = beds = None
        for part in parts:
            if 'guest' in part.lower():
                guests = int(''.join(filter(str.isdigit, part)) or 0)
            elif 'bedroom' in part.lower():
                rooms = int(''.join(filter(str.isdigit, part)) or 0)
            elif 'bed' in part.lower() and 'bedroom' not in part.lower():
                beds = int(''.join(filter(str.isdigit, part)) or 0)
        return guests, rooms, beds

    df[['guests', 'bedrooms', 'beds']] = pd.DataFrame(
        df['DETAILS'].apply(extract_details).tolist(),
        columns=['guests', 'bedrooms', 'beds']
    )
    
    return df

# Load data
df = load_data()

# Header
st.title("🏠 Airbnb Stays Analytics Dashboard")
st.markdown("Comprehensive analysis of Airbnb Stays listings")

# Main metrics row
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Total Stays Listed", f"{len(df):,}")
with col2:
    avg_price = df['price_value'].mean()
    st.metric("Average Price", f"${avg_price:.2f}")
with col3:
    avg_rating = df['rating_cleanliness'].mean()
    st.metric("Average Rating", f"{avg_rating:.2f}⭐")
with col4:
    pet_friendly = (df['PETS_ALLOWED'] == True).sum()
    st.metric("Pet Friendly", f"{pet_friendly:,}")

# Create tabs for different analyses
tabs = st.tabs(["📊 Overview", "🗺️ Location", "💰 Pricing", "⭐ Ratings", "🏠 Details"])

# Overview Tab
with tabs[0]:
    col1, col2 = st.columns(2)
    
    with col1:
        # Guest capacity distribution
        valid_guests = df[df['guests'].notna() & (df['guests'] > 0)]
        fig = px.histogram(valid_guests, 
                          x='guests',
                          title='Distribution of Guest Capacity',
                          labels={'guests': 'Number of Guests'})
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Bedroom distribution
        valid_bedrooms = df[df['bedrooms'].notna() & (df['bedrooms'] > 0)]
        fig = px.histogram(valid_bedrooms,
                          x='bedrooms',
                          title='Distribution of Bedrooms',
                          labels={'bedrooms': 'Number of Bedrooms'})
        st.plotly_chart(fig, use_container_width=True)

    # Availability trends
    st.subheader("Availability Trends")
all_dates = []
for dates in df['AVAILABLE_DATES'].apply(process_available_dates):
    all_dates.extend(dates)

if all_dates:
    availability_df = pd.DataFrame(all_dates, columns=['date'])
    # Handle different date formats
    availability_df['date'] = pd.to_datetime(availability_df['date'], format='mixed')
    availability_counts = availability_df['date'].value_counts().reset_index()
    availability_counts.columns = ['date', 'count']
    availability_counts = availability_counts.sort_values('date')
    
    fig = px.line(availability_counts, 
                 x='date', 
                 y='count',
                 title='Number of Available Properties by Date')
    fig.update_xaxes(title='Date')
    fig.update_yaxes(title='Number of Available Properties')
    st.plotly_chart(fig, use_container_width=True)

# Location Tab
with tabs[1]:
    st.subheader("Geographical Distribution of Stays")
    
    # Prepare location data
    valid_locations = df[df['LAT'].notna() & df['LONG'].notna()].copy()
    valid_locations['LAT'] = valid_locations['LAT'].astype(float)
    valid_locations['LONG'] = valid_locations['LONG'].astype(float)
    
    
    # Alternative map using Plotly for backup
    fig = px.scatter_mapbox(valid_locations,
                           lat='LAT',
                           lon='LONG',
                           color='price_value',
                           size_max=15,
                           color_continuous_scale=px.colors.sequential.Reds,
                           zoom=0,
                           title='Property Locations by Price')
    fig.update_layout(mapbox_style="carto-positron")
    st.plotly_chart(fig, use_container_width=True)

# Pricing Tab
with tabs[2]:
    col1, col2 = st.columns(2)
    
    with col1:
        # Price distribution
        valid_prices = df[df['price_value'].notna()]
        fig = px.histogram(valid_prices,
                          x='price_value',
                          title='Price Distribution',
                          labels={'price_value': 'Price ($)'})
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Price vs Guests
        valid_data = df[df['price_value'].notna() & df['guests'].notna() & df['rating_value'].notna()]
        fig = px.scatter(valid_data,
                        x='guests',
                        y='price_value',
                        color='rating_value',
                        title='Price vs Guest Capacity',
                        labels={'guests': 'Number of Guests',
                               'price_value': 'Price ($)',
                               'rating_value': 'Rating'})
        st.plotly_chart(fig, use_container_width=True)

# Ratings Tab
with tabs[3]:
    # Ratings breakdown
    rating_cols = [
        'rating_cleanliness',
        'rating_accuracy',
        'rating_communication',
        'rating_location',
        'rating_check_in',
        'rating_value'
    ]
    
    # Make sure all columns exist and handle missing ones
    available_cols = [col for col in rating_cols if col in df.columns]
    if available_cols:
        valid_ratings = df[available_cols].mean()
        
        # Create readable labels
        labels = {col: col.replace('rating_', '').title() for col in available_cols}
        
        fig = go.Figure(data=[
            go.Bar(
                x=[labels[col] for col in available_cols],
                y=valid_ratings.values,
                marker_color='#ff385c'
            )
        ])
        fig.update_layout(
            title='Average Ratings by Category',
            xaxis_title='Rating Category',
            yaxis_title='Average Score'
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("No rating data available")

# Details Tab
with tabs[4]:
    # Amenities analysis
    st.subheader("Amenities Analysis")
    
    # Flatten amenities for counting
    all_amenities = []
    for amenities_dict in df['amenities_dict']:
        for group, amenities in amenities_dict.items():
            all_amenities.extend(amenities)
    
    if all_amenities:
        amenities_count = pd.Series(all_amenities).value_counts().head(15)
        fig = px.bar(amenities_count,
                     title='Top 15 Most Common Amenities',
                     labels={'index': 'Amenity', 'value': 'Count'})
        st.plotly_chart(fig, use_container_width=True)

# Sidebar filters
with st.sidebar:
    st.header("Filters")
    
    valid_prices = df[df['price_value'].notna()]
    price_range = st.slider(
        "Price Range ($)",
        min_value=int(valid_prices['price_value'].min()),
        max_value=int(valid_prices['price_value'].max()),
        value=(int(valid_prices['price_value'].min()),
               int(valid_prices['price_value'].max()))
    )
    
    valid_guests = df[df['guests'].notna()]
    guest_range = st.slider(
        "Guest Capacity",
        min_value=int(valid_guests['guests'].min()),
        max_value=int(valid_guests['guests'].max()),
        value=(int(valid_guests['guests'].min()),
               int(valid_guests['guests'].max()))
    )
    
    min_rating = st.slider(
        "Minimum Rating",
        min_value=0.0,
        max_value=5.0,
        value=0.0
    )
    
    pet_friendly = st.checkbox("Pet Friendly Only")
    
    apply_filters = st.button("Apply Filters")

# Apply filters
if apply_filters:
    filtered_df = df[
        (df['price_value'] >= price_range[0]) &
        (df['price_value'] <= price_range[1]) &
        (df['guests'] >= guest_range[0]) &
        (df['guests'] <= guest_range[1]) &
        (df['rating_cleanliness'] >= min_rating)
    ]
    
    if pet_friendly:
        filtered_df = filtered_df[filtered_df['PETS_ALLOWED'] == True]
    
    st.success(f"Found {len(filtered_df)} stays matching your criteria!")
    
    # Show filtered results
    st.dataframe(
        filtered_df[['NAME', 'price_value', 'guests', 'bedrooms', 
                    'rating_cleanliness', 'PETS_ALLOWED']].head(10),
        use_container_width=True
    )


