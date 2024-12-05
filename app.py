import streamlit as st
import openai
import pandas as pd
import plotly.express as px
import os
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

# Set your OpenAI API key
openai.api_key = st.secrets["general"]["API_KEY"]
# Function to call OpenAI API and generate SQL query
def get_sql_query(user_input):
    schema="""
      AIRBNB_PROPERTIES_INFORMATION Schema:
      Columns:
      - TIMESTAMP, URL, AMENITIES, AVAILABILITY, AVAILABLE_DATES, CATEGORY, CATEGORY_RATING, DESCRIPTION, DESCRIPTION_ITEMS, DETAILS, FINAL_URL, GUESTS, HIGHLIGHTS, HOUSE_RULES, IMAGE, IMAGES, LAT, LONG, NAME, PETS_ALLOWED, PRICE, RATINGS, REVIEWS, SELLER_INFO
      """
    data = """
    2022-12-30	
    https://www.airbnb.com/rooms/48682162	
    [{"group_name":"Bathroom","items":[{"name":"Hair dryer"},{"name":"Cleaning products"},{"name":"Body soap"},{"name":"Outdoor shower"},{"name":"Hot water"}]},{"group_name":"Bedroom and laundry","items":[{"name":"Essentials","value":"Towels, bed sheets, soap, and toilet paper"},{"name":"Hangers"},{"name":"Bed linens"},{"name":"Clothing storage: closet"}]},{"group_name":"Entertainment","items":[{"name":"50\" HDTV with standard cable"}]},{"group_name":"Heating and cooling","items":[{"name":"AC - split type ductless system"},{"name":"Heating"}]},{"group_name":"Home safety","items":[{"name":"Security cameras on property","value":"All common areas are recorded for your safety. The door locks are also monitored through a security company. "},{"name":"Smoke alarm","value":"“There are two smoke alarms in the suite as well as a fire extinguisher.”"},{"name":"Fire extinguisher"},{"name":"Lock on bedroom door","value":"Private room can be locked for safety and privacy"}]},{"group_name":"Internet and office","items":[{"name":"Wifi"}]},{"group_name":"Kitchen and dining","items":[{"name":"Microwave"},{"name":"Dishes and silverware","value":"Bowls, chopsticks, plates, cups, etc."},{"name":"Mini fridge"},{"name":"Coffee maker: Keurig coffee machine"},{"name":"Wine glasses"},{"name":"Barbecue utensils","value":"Grill, charcoal, bamboo skewers/iron skewers, etc."},{"name":"Dining table"}]},{"group_name":"Location features","items":[{"name":"Public or shared beach access – Beachfront","value":"Guests can enjoy a nearby beach"},{"name":"Private entrance","value":"Separate street or building entrance"},{"name":"Laundromat nearby"}]},{"group_name":"Outdoor","items":[{"name":"Shared patio or balcony"},{"name":"Shared backyard – Not fully fenced","value":"An open space on the property usually covered in grass"},{"name":"Outdoor furniture"},{"name":"Outdoor dining area"}]},{"group_name":"Parking and facilities","items":[{"name":"Free driveway parking on premises – 1 space"},{"name":"Single level home","value":"No stairs in home"}]},{"group_name":"Services","items":[{"name":"Self check-in"},{"name":"Keypad","value":"Check yourself into the home with a door code"}]},{"group_name":"Not included","items":[]}]
    TRUE
    2022-12-29,2022-12-30,2022-12-31,2023-01-01,2023-01-02,2023-01-03,2023-01-04,2023-01-05,2023-01-06,2023-01-07,2023-01-08,2023-01-09,2023-01-10,2023-01-11,2023-01-12,2023-01-13,2023-01-14,2023-01-15,2023-01-16,2023-01-17,2023-01-18,2023-01-19,2023-01-20,2023-01-21,2023-01-22,2023-01-23,2023-01-24,2023-01-25,2023-01-26,2023-01-27,2023-01-28,2023-01-29,2023-01-30,2023-01-31,2023-02-01,2023-02-02,2023-02-03,2023-02-04,2023-02-05,2023-02-06,2023-02-07,2023-02-08,2023-02-09,2023-02-10,2023-02-11,2023-02-12,2023-02-13,2023-02-14,2023-02-15,2023-02-16,2023-02-17,2023-02-18,2023-02-19,2023-02-20,2023-02-21,2023-02-22,2023-02-23,2023-02-24,2023-02-25,2023-02-26,2023-02-27,2023-02-28,2023-03-01,2023-03-02,2023-03-03,2023-03-04,2023-03-05,2023-03-06,2023-03-07,2023-03-08,2023-03-09,2023-03-10,2023-03-11,2023-03-12,2023-03-13,2023-03-14,2023-03-15,2023-03-16,2023-03-17,2023-03-18,2023-03-19,2023-03-20,2023-03-21,2023-03-22,2023-03-23,2023-03-24,2023-03-25,2023-03-26,2023-03-27,2023-03-28,2023-03-29,2023-03-30,2023-03-31,2023-04-01,2023-04-02,2023-04-03,2023-04-04,2023-04-05,2023-04-06,2023-04-07,2023-04-08,2023-04-09,2023-04-10,2023-04-11,2023-04-12,2023-04-13,2023-04-14,2023-04-15,2023-04-16,2023-04-17,2023-04-18,2023-04-19,2023-04-20,2023-04-21,2023-04-22,2023-04-23,2023-04-24,2023-04-25,2023-04-26,2023-04-27,2023-04-28,2023-04-29,2023-04-30,2023-05-01,2023-05-02,2023-05-03,2023-05-04,2023-05-05,2023-05-06,2023-05-07,2023-05-08,2023-05-09,2023-05-10,2023-05-11,2023-05-12,2023-05-13,2023-05-14,2023-05-15,2023-05-16,2023-05-17,2023-05-18,2023-05-19,2023-05-20,2023-05-21,2023-05-22,2023-05-23,2023-05-24,2023-05-25,2023-05-26,2023-05-27,2023-05-28,2023-05-29,2023-05-30,2023-05-31,2023-06-01,2023-06-02,2023-06-03,2023-06-04,2023-06-05,2023-06-06,2023-06-07,2023-06-08,2023-06-09,2023-06-10,2023-06-11,2023-06-12,2023-06-13,2023-06-14,2023-06-15,2023-06-16,2023-06-17,2023-06-18,2023-06-19,2023-06-20,2023-06-21,2023-06-22,2023-06-23,2023-06-24,2023-06-25,2023-06-26,2023-06-27,2023-06-28,2023-06-29,2023-06-30,2023-07-01,2023-07-02,2023-07-03,2023-07-04,2023-07-05,2023-07-06,2023-07-07,2023-07-08,2023-07-09,2023-07-10,2023-07-11,2023-07-12,2023-07-13,2023-07-14,2023-07-15,2023-07-16,2023-07-17,2023-07-18,2023-07-19,2023-07-20,2023-07-21,2023-07-22,2023-07-23,2023-07-24,2023-07-25,2023-07-26,2023-07-27,2023-07-28,2023-07-29,2023-07-30,2023-07-31,2023-08-01,2023-08-02,2023-08-03,2023-08-04,2023-08-05,2023-08-06,2023-08-07,2023-08-08,2023-08-09,2023-08-10,2023-08-11,2023-08-12,2023-08-13,2023-08-14,2023-08-15,2023-08-16,2023-08-17,2023-08-18,2023-08-19,2023-08-20,2023-08-21,2023-08-22,2023-08-23,2023-08-24,2023-08-25,2023-08-26,2023-08-27,2023-08-28,2023-08-29,2023-08-30,2023-08-31,2023-09-01,2023-09-02,2023-09-03,2023-09-04,2023-09-05,2023-09-06,2023-09-07,2023-09-08,2023-09-09,2023-09-10,2023-09-11,2023-09-12,2023-09-13,2023-09-14,2023-09-15,2023-09-16,2023-09-17,2023-09-18,2023-09-19,2023-09-20,2023-09-21,2023-09-22,2023-09-23,2023-09-24,2023-09-25,2023-09-26,2023-09-27,2023-09-28,2023-09-29,2023-09-30,2023-10-01,2023-10-02,2023-10-03,2023-10-04,2023-10-05,2023-10-06,2023-10-07,2023-10-08,2023-10-09,2023-10-10,2023-10-11,2023-10-12,2023-10-13,2023-10-14,2023-10-15,2023-10-16,2023-10-17,2023-10-18,2023-10-19,2023-10-20,2023-10-21,2023-10-22,2023-10-23,2023-10-24,2023-10-25,2023-10-26,2023-10-27,2023-10-28,2023-10-29,2023-10-30,2023-10-31,2023-11-01,2023-11-02,2023-11-03,2023-11-04,2023-11-05,2023-11-06,2023-11-07,2023-11-08,2023-11-09,2023-11-10,2023-11-11,2023-11-12,2023-11-13,2023-11-14,2023-11-15,2023-11-16,2023-11-17,2023-11-18,2023-11-19,2023-11-20,2023-11-21,2023-11-22,2023-11-23,2023-11-24,2023-11-25,2023-11-26,2023-11-27,2023-11-28,2023-11-29,2023-11-30
    Stays	
    [{"name":"Cleanliness","value":"4.9"},{"name":"Accuracy","value":"4.9"},{"name":"Communication","value":"4.9"},{"name":"Location","value":"5.0"},{"name":"Check-in","value":"5.0"},{"name":"Value","value":"4.8"}]
    The Driftwood Suite<br />Get ready to relax in the largest of our single rooms. Guests will find a table and chairs; a sleep-in-late queen bed with plush pillows and hotel-quality linens; two relaxing chairs; a TV with premium channel streaming for guests; a kitchenette with a microwave, drink refrigerator, K-cup coffee maker, sink and set of dishes, glasses, cups and utensils; and a master bathroom with closet nook, walk-in shower and Granite counter tops. Set for two guest. No pets, service animals, The space Amenities in all rooms: <br />•  Wide-screen TV with guest-accessible streaming services<br />•  Wi-Fi<br />•  In-room climate control<br />•  Kitchenette with Granite counters, stocked with K-cup coffee maker, small set of dishes, utensils, cups and glasses and with microwave and drink refrigerator<br />• Table and chairs<br />• Luggage rack<br />• Recessed lighting with dimmers<br />• Plantation blinds<br />• Keyless entrance with pre-arranged passcode (never lose your key!), Guest access You will be able to access the patio, grill and green space while enjoying your own suite.	Private room in condo,1 bed,1 private bath	2 guests,1 bedroom,1 bed,1 private bath	https://www.airbnb.com/rooms/48682162?enable_auto_translate=false&source_impression_id=p3_1672274649_wljRz3lOUlqVZ6%2FR#availability-calendar	2	[{"name":"Self check-in","value":"Check yourself in with the keypad."},{"name":"John is a Superhost","value":"Superhosts are experienced, highly rated hosts who are committed to providing great stays for guests."},{"name":"Great location","value":"100% of recent guests gave the location a 5-star rating."}]	Check-in after 3:00 PM,Checkout before 11:00 AM,2 guests maximum	https://a0.muscache.com/pictures/ce84fd22-f158-473c-a738-56ea22c2b3b6.jpg	https://a0.muscache.com/pictures/ce84fd22-f158-473c-a738-56ea22c2b3b6.jpg,https://a0.muscache.com/pictures/2c932c2a-5c28-4709-ae32-0093cc1f087b.jpg,https://a0.muscache.com/pictures/22e2f22a-f050-45f1-a791-9039cf7a805d.jpg,https://a0.muscache.com/pictures/d431cc1c-1a3f-4998-81af-04670105fe7e.jpg,https://a0.muscache.com/pictures/a40da461-92a8-44b3-9dd1-b8ac367534a8.jpg,https://a0.muscache.com/pictures/be9c05c8-776f-47e7-98c8-ff17441303c0.jpg,https://a0.muscache.com/pictures/b990811a-51c0-42d7-ae81-e9f3ed066694.jpg,https://a0.muscache.com/pictures/d766ee67-6f6b-4fdf-97b5-f260685a6e6a.jpg,https://a0.muscache.com/pictures/51b01c37-a7f3-4611-afad-d963ca882c95.jpg,https://a0.muscache.com/pictures/ff2027db-b43e-4fed-ba0b-8f6f49d33742.jpg,https://a0.muscache.com/pictures/6eb2537a-b560-4fac-8e3b-dc3cb34143a2.jpg,https://a0.muscache.com/pictures/miso/Hosting-48682162/original/df6e8e0d-c046-4cf3-8669-ad54cc9d14b3.jpeg,https://a0.muscache.com/pictures/miso/Hosting-48682162/original/41f4e552-9bb7-47e6-9c79-7b86163a2a08.jpeg,https://a0.muscache.com/pictures/miso/Hosting-48682162/original/815fb3f7-bb2e-40ad-aa54-15bd28242259.jpeg,https://a0.muscache.com/pictures/miso/Hosting-48682162/original/e7268a14-f0f5-4bed-a59e-f8100c4d09f2.jpeg
    34	
    -78	
    The Driftwood Suite at LazyOak.Life	
    FALSE	
    {"currency":"USD","symbol":"$","value":125}	
    5	
    It was peaceful,This is our second trip here. We just love it and planning a third trip. The location is perfect. The place is perfect for us. Meet the host this past weekend and enjoyed talking to him. Can’t wait till our next trip to oak island. Driftwood suite.,This is the perfect spot, great location, has everything you need. We will definitely be back. John was amazing, communication was great. All around just a cozy little spot! I highly recommend!,Wonderful location and place to stay.,Super clean accomodations. Easy access & everything provided to make our stay excellent!,Great place!,Cute and clean spot to get away! We loved spending a long weekend here!	{"avatar":"https://a0.muscache.com/im/pictures/user/dc8bef65-b808-49a0-ab99-a1e5272b2d20.jpg?aki_policy=profile_x_medium","features":[{"name":"Response rate","value":"100%"},{"name":"Response time","value":"within an hour"}],"name":"Hosted by John","url":"https://www.airbnb.ru/contact_host/48682162/send_message"}
    """
    prompt = f"""
    Given the following database schema:
    {schema}
    Example data:
    {data}
    Translate this user query into a SQL query, give strictly only the sql query and properly look at how values are in json sometimes:
    {user_input}
    """
    response = openai.chat.completions.create(
        model="gpt-4",  # You can use the model you have access to
        messages=[{"role": "user", "content": prompt}]
    )
    
    sql_query = response.choices[0].message.content
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
    
    df = pd.DataFrame(data)

    # Display the results in a table
    st.subheader("Query Results:")
    st.dataframe(df)

    # Dynamic Visualization
    if not df.empty:
        st.subheader("Visualization")
        numeric_columns = df.select_dtypes(include=["number"]).columns
        string_columns = df.select_dtypes(include=["object", "string"]).columns
    
        if len(numeric_columns) >= 1 and len(string_columns) >= 1:
            # Allow X-axis as varchar and Y-axis as numeric
            x_axis = st.selectbox("Select X-axis (categorical):", string_columns)
            y_axis = st.selectbox("Select Y-axis (numeric):", numeric_columns)
            
            # Create a line chart
            st.line_chart(data=df, x=x_axis, y=y_axis)
    else:
        st.write("No data returned from the query.")

