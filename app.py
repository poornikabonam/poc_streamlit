import streamlit as st
import openai
import pandas as pd
import plotly.express as px
import os
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

# Set your OpenAI API key
openai.api_key = st.secrets["API_KEY"]
# Function to call OpenAI API and generate SQL query
def get_sql_query(user_input):
    schema="""
      AIRBNB_PROPERTIES_INFORMATION Schema:
      Columns:
      - TIMESTAMP, URL, AMENITIES, AVAILABILITY, AVAILABLE_DATES, CATEGORY, CATEGORY_RATING, DESCRIPTION, DESCRIPTION_ITEMS, DETAILS, FINAL_URL, GUESTS, HIGHLIGHTS, HOUSE_RULES, IMAGE, IMAGES, LAT, LONG, NAME, PETS_ALLOWED, PRICE, RATINGS, REVIEWS, SELLER_INFO
      """
    prompt = f"""
    Given the following database schema:
    {schema}
    Translate this user query into a SQL query:
    {user_input}
    """
    response = openai.chat.completions.create(
        model="gpt-4",  # You can use the model you have access to
        messages=[{"role": "user", "content": prompt}]
    )
    
    sql_query = response.choices[0].message
    st.write(sql_query)
    return sql_query

# Function to execute the SQL query (using the already established connection)
def execute_sql(query):
    # Use the context already established in Streamlit (ctx)
    cursor = st.connection("snowflake").cursor()
    cursor.execute(query)
    result = cursor.fetchall()
    columns = [col[0] for col in cursor.description]
    df = pd.DataFrame(result, columns=columns)
    return df

# Streamlit dashboard setup
st.title("Interactive Dashboard with LLM")

# Take user input (question)
user_query = st.text_input("Ask a question (e.g., 'Show properties in New York with rating above 4')")

# Process user input and generate SQL
if user_query:
    # Get SQL query from LLM
    sql_query = get_sql_query(user_query)
    st.write(f"Generated SQL Query: {sql_query}")
    
    # Execute the generated SQL query and get the results
    data = execute_sql(sql_query)
    
    # Display data in a table
    st.dataframe(data)
    
    # Create a visualization (if relevant data exists)
    if 'price' in data.columns:
        fig = px.bar(data, x='name', y='price', title="Property Prices")
        st.plotly_chart(fig)
