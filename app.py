import streamlit as st
import openai
import pandas as pd
import plotly.express as px

# Set your OpenAI API key
openai.api_key = secrets.API_KEY
# Function to call OpenAI API and generate SQL query
def get_sql_query(user_input):
   schema="""
Airbnb Properties Schema:
Columns:
- TIMESTAMP: Timestamp of the entry
- URL: Property URL
- AMENITIES: List of amenities
- AVAILABILITY: Availability status
- CATEGORY: Property category
- CATEGORY_RATING: Rating for the category
- DESCRIPTION: Property description
- PRICE: Price per night
- RATINGS: Overall property ratings
- REVIEWS: Reviews from guests
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
    
    sql_query = response['choices'][0]['message']['content']
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
