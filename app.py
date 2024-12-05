import streamlit as st
import pandas as pd
from transformers import pipeline

# Initialize Hugging Face LLM pipeline
st.title("Review Insights App")
st.subheader("Extract actionable insights from product reviews")

# Instructions for the user
st.write("This app fetches product reviews from Snowflake, "
         "extracts key topics or features using an LLM, "
         "and generates actionable insights for improvement.")

# Snowflake integration
# Assume you use Streamlit's built-in connection for Snowflake
# (Settings -> Data -> Add Snowflake)
@st.cache_data
def fetch_reviews():
    query = """
        SELECT review_id, product_name, review_text, rating
        FROM product_reviews
        WHERE product_category = 'Electronics'
        ORDER BY review_date DESC
        LIMIT 10;
    """
    # Use Streamlit's connection to query Snowflake
    connection = st.experimental_connection("snowflake", type="sql")
    result = connection.query(query)
    return pd.DataFrame(result)

# Hugging Face LLM pipeline
@st.cache_resource
def initialize_llm_pipeline():
    return pipeline("zero-shot-classification", model="facebook/bart-large-mnli")

# Fetch and display reviews
st.subheader("Recent Product Reviews")
reviews_df = fetch_reviews()
if not reviews_df.empty:
    st.write("Recent Reviews Fetched from Snowflake:")
    st.dataframe(reviews_df)

    # Extract review text for selection
    selected_review = st.selectbox(
        "Select a review to analyze:", 
        reviews_df["review_text"].tolist()
    )

    # Extract features from selected review
    if selected_review:
        st.subheader("Extracted Features or Topics")
        llm = initialize_llm_pipeline()
        candidate_labels = ["battery life", "screen quality", "customer service", "performance", "usability"]
        result = llm(selected_review, candidate_labels)

        # Display extracted topics and scores
        for label, score in zip(result["labels"], result["scores"]):
            st.write(f"**{label}:** {score:.2f}")

        # Actionable insights
        st.subheader("Actionable Insights")
        actionable_features = [
            label for label, score in zip(result["labels"], result["scores"]) if score > 0.5
        ]
        if actionable_features:
            st.write("Consider focusing on improving these areas:")
            st.write(", ".join(actionable_features))
        else:
            st.write("No specific actionable areas identified.")
else:
    st.write("No reviews available in the database. Please add reviews to proceed.")

st.write("**Note**: This is a demo app for Snowflake, LLM, and Streamlit integration.")
