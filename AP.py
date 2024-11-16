import os
import csv
import streamlit as st

# File path for user data
USER_DATA_FILE = "users.csv"

# Function to initialize the CSV file
def initialize_user_data_file():
    st.write("Initializing file at:", os.path.abspath(USER_DATA_FILE))
    try:
        with open(USER_DATA_FILE, mode='x', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["email", "phone_number", "full_name", "age", "sex"])  # Add headers
            st.write("File created successfully.")
    except FileExistsError:
        st.write("File already exists.")
    except Exception as e:
        st.error(f"Error initializing file: {e}")

# Initialize the CSV file
initialize_user_data_file()


