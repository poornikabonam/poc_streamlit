import streamlit as st
from snowflake.snowpark.functions import col
from transformers import pipeline
import pandas as pd

# Streamlit title and description
st.title("Airbnb Property Insights")
st.write("Analyze Airbnb property data with Snowflake and Transformers-powered insights.")

# Initialize Snowflake connection using Streamlit's built-in method
ctx = st.connection("snowflake")
session = ctx.session()

# Query Airbnb dataset from Snowflake
@st.cache_data
def fetch_airbnb_data():
    query = (
        session.table("AIRBNB_PROPERTIES_INFORMATION.public.AIRBNB_PROPERTIES_INFORMATION")  # Adjust schema and table name
        .select(
            col("NAME").alias("name"),
            col("DESCRIPTION").alias("description"),
            col("PRICE").alias("price"),
            col("CATEGORY").alias("category"),
            col("CATEGORY_RATING").alias("category_rating"),
            col("RATINGS").alias("ratings"),
        )
        .limit(100)  # Fetch a sample of 100 rows for demo purposes
    )
    return query.to_pandas()

# Fetch data
properties_df = fetch_airbnb_data()

# Display data in a table
st.subheader("Properties Overview")
st.dataframe(properties_df)

# Load the summarization model from Transformers
@st.cache_resource
def load_summarizer():
    return pipeline("summarization", model="facebook/bart-large-cnn")

summarizer = load_summarizer()

# Summarize property descriptions
def summarize_description(description):
    if not description or pd.isna(description):
        return "No description available."
    try:
        summary = summarizer(description, do_sample=False)
        # Check if the summary has expected output
        if not summary or len(summary) == 0:
            return "Summary not available."
        return summary[0].get('summary_text', "Summary not found in response.")
    except Exception as e:
        # Log error and return fallback text
        st.error(f"Error summarizing description: {str(e)}")
        return "Error summarizing description."
# Apply summarization to the dataset
st.subheader("Property Descriptions Summarized")
properties_df['DESCRIPTION'] = properties_df['DESCRIPTION'].fillna("No description available")
properties_df['summary'] = properties_df['DESCRIPTION'].apply(summarize_description)

# Display summarized descriptions
st.dataframe(properties_df[['name', 'summary', 'price', 'category', 'ratings']])

# Insights on categories and ratings
st.subheader("Category Analysis")
category_analysis = properties_df.groupby('category').agg(
    avg_price=('price', 'mean'),
    avg_rating=('ratings', 'mean')
).reset_index()

st.bar_chart(category_analysis, x='category', y=['avg_price', 'avg_rating'])

