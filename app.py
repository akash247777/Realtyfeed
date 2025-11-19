import streamlit as st
import google.generativeai as genai
import pandas as pd
from sqlalchemy import create_engine, text
from urllib.parse import quote_plus
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Configure Gemini LLM
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Function to generate SQL query using Gemini LLM
def generate_sql_query(user_query, db_structure, prompt):
    model = genai.GenerativeModel('gemini-2.5-flash')
    response = model.generate_content(
        f"{prompt}\nDatabase Structure:\n{db_structure}\nUser Query:\n{user_query}"
    )
    return response.text.strip()

# Function to execute SQL query and return results
def execute_sql_query(sql_query, db_connection_string):
    engine = create_engine(db_connection_string)
    with engine.connect() as connection:
        result = connection.execute(text(sql_query))
        return pd.DataFrame(result.fetchall(), columns=result.keys())

# Streamlit UI
st.title("SQL Query Assistant")

# User input
user_query = st.text_input("Ask your question:")

# SQL Server connection details
server = r'192.168.1.16,49170'
database = 'Real_estate'
username = 'akash'
password = 'akash@123'

# Build connection string
password_encoded = quote_plus(password)
db_connection_string = f'mssql+pyodbc://{username}:{password_encoded}@{server}/{database}?driver=ODBC+Driver+17+for+SQL+Server'

# Database structure
db_structure = """
Tables:
- Properties (property_id, unparsed_address, list_price, bedrooms, bathrooms, square_footage, property_type, year_built, description, latitude, longitude)
- Amenities (amenity_id, property_id, amenity_type, title, address, distance_km)
"""

# Prompt for Gemini LLM
prompt = """
You are an expert in converting natural language questions to SQL queries and ddon't make mistake in SQL query.
Given the database structure below, generate a SQL query for the user's question.
- Alwaays display the Properties use  P.*
- For properties with a pool, check the 'description' field for the word 'pool'.
- For amenities, only use the following key words values for 'amenity_type': Transit, Malls, Pharmacies, Hospitals, Schools, Restaurants, Groceries, ATMs, Parks.
- Use DISTINCT to avoid duplicate rows.
- Use LIKE for case-insensitive searches, not ILIKE.
- Use <= for less than or equal to comparisons.
- Use the correct spelling for locations (e.g., 'South Carolina').
Only return the SQL query, nothing else.
"""

if st.button("Get Answer"):
    if user_query:
        # Generate SQL query
        sql_query = generate_sql_query(user_query, db_structure, prompt)
        st.code(sql_query, language="sql")
        print("Generated SQL Query:", sql_query)  # Debug print

        # Clean the SQL query
        cleaned_sql_query = sql_query.replace("```sql", "").replace("```", "").strip()
        print("Cleaned SQL Query:", cleaned_sql_query)  # Debug print

        # Execute SQL query
        try:
            results = execute_sql_query(cleaned_sql_query, db_connection_string)
            st.dataframe(results)
        except Exception as e:
            st.error(f"Error executing SQL query: {e}")
            st.code(cleaned_sql_query, language="sql")  # Show the query that failed
    else:
        st.warning("Please enter a question.")
