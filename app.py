import streamlit as st
from snowflake.snowpark.functions import col
import openai
import pandas as pd

# Streamlit title and description
st.title("Airbnb Property Insights")
st.write("Explore and analyze Airbnb property descriptions with the power of Snowflake and LLM.")

# Initialize Snowflake connection using Streamlit's built-in method
ctx = st.connection("snowflake")
session = ctx.session()

# Query Airbnb dataset from Snowflake
@st.cache_data
def fetch_airbnb_data():
    query = (
        session.table("airbnb_properties_information.public.airbnb_properties_information")  # Adjust schema and table name as needed
        .select(
            col("PROPERTY_NAME").alias("name"),
            col("DESCRIPTION").alias("description"),
            col("LOCATION").alias("location"),
        )
        .limit(100)  # Fetch a sample of 100 rows for demo purposes
    )
    return query.to_pandas()

# Fetch data
properties_df = fetch_airbnb_data()

# Display data in a table
st.subheader("Properties Overview")
st.dataframe(properties_df)

# OpenAI API key input (hide it for security in production apps)
openai_api_key = st.text_input("Enter your OpenAI API Key:", type="password")
openai.api_key = openai_api_key

# Function to summarize property description
@st.cache_data(show_spinner=False)
def summarize_description(description):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Summarize the following property description."},
                {"role": "user", "content": description},
            ],
        )
        return response["choices"][0]["message"]["content"]
    except Exception as e:
        return f"Error: {e}"

# Interactive property selection
selected_property = st.selectbox("Select a property to analyze:", properties_df["name"])
property_info = properties_df[properties_df["name"] == selected_property].iloc[0]

st.subheader("Property Details")
st.write(f"**Name:** {property_info['name']}")
st.write(f"**Location:** {property_info['location']}")
st.write(f"**Description:** {property_info['description']}")

# Summarize description
if st.button("Generate Summary"):
    with st.spinner("Generating summary..."):
        summary = summarize_description(property_info["description"])
    st.write("### Summary:")
    st.write(summary)
