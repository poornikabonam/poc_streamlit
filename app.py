import streamlit as st
from transformers import pipeline
from snowflake.snowpark.functions import col

# Title of the app
st.title("Review Insights with Snowflake and LLM")
st.subheader("Analyze customer reviews using Snowflake and an LLM")

# Fetch data from Snowflake
@st.cache_data
def fetch_reviews():
    ctx = st.connection("snowflake")  # Connect using Streamlit's Snowflake integration
    session = ctx.session()  # Get the Snowflake session
    # Replace the table/columns with your actual Snowflake dataset
    reviews_df = (
        session.table("reviews.public.customer_reviews")  # Example dataset
        .select(col("REVIEW_TEXT").alias("review"), col("PRODUCT_NAME").alias("product"))
    )
    return reviews_df.to_pandas()

# Load the LLM pipeline for sentiment analysis
@st.cache_resource
def load_llm():
    return pipeline("sentiment-analysis")

# Main logic
def main():
    # Fetch data
    st.write("Fetching customer reviews from Snowflake...")
    reviews_df = fetch_reviews()
    
    if reviews_df.empty:
        st.error("No reviews found in the database!")
        return
    
    st.write("Fetched reviews:")
    st.dataframe(reviews_df)

    # Load the LLM
    st.write("Loading the sentiment analysis model...")
    sentiment_model = load_llm()

    # Perform sentiment analysis
    st.write("Analyzing sentiments...")
    reviews_df["sentiment"] = reviews_df["review"].apply(
        lambda text: sentiment_model(text)[0]["label"]
    )

    # Display results
    st.write("Sentiment Analysis Results:")
    st.dataframe(reviews_df)

    # Optional: Download results as CSV
    st.download_button(
        label="Download Results as CSV",
        data=reviews_df.to_csv(index=False),
        file_name="sentiment_analysis_results.csv",
        mime="text/csv",
    )

if __name__ == "__main__":
    main()
