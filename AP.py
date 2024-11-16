import streamlit as st
from fpdf import FPDF
import csv
import os
from datetime import datetime

# File path for user data
USER_DATA_FILE = "users.csv"

# Function to initialize the CSV file
def initialize_user_data_file():
    st.write("Checking if the file exists...")
    try:
        with open(USER_DATA_FILE, mode='x', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["email", "phone_number", "full_name", "age", "sex"])  # Add headers
            st.write("File created successfully.")
    except FileExistsError:
        st.write("File already exists.")
    except Exception as e:
        st.error(f"Error initializing file: {e}")

# Function to save a new user to the CSV file
def save_user_to_csv(email, phone_number, full_name, age, sex):
    st.write("Attempting to save user to file...")
    try:
        with open(USER_DATA_FILE, mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([email, phone_number, full_name, age, sex])
            st.write("User saved successfully!")
    except Exception as e:
        st.error(f"Error saving user: {e}")

# Function to check if a user exists in the CSV file
def user_exists(email, phone_number):
    try:
        with open(USER_DATA_FILE, mode='r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                if row["email"] == email and row["phone_number"] == phone_number:
                    return row  # Return user data if found
    except FileNotFoundError:
        return None
    return None

# Initialize CSV file at the start of the app
initialize_user_data_file()

# Debugging: Display file path
st.write("Expected file path:", os.path.abspath(USER_DATA_FILE))

# Streamlit app title
st.title("Digital Consent App")

# Sidebar for registration and sign-in options
auth_option = st.sidebar.radio("Select an option:", ["Register", "Sign In"])

# Registration
if auth_option == "Register":
    st.header("Register a New Account")
    email = st.text_input("Email Address")
    phone_number = st.text_input("Phone Number")
    full_name = st.text_input("Full Name")
    age = st.number_input("Age", min_value=18, max_value=120)
    sex = st.selectbox("Sex", ["Male", "Female", "Other"])
    
    if st.button("Register"):
        st.write("Register button clicked...")
        if email and phone_number and full_name:
            st.write("All fields are filled.")
            if user_exists(email, phone_number):
                st.warning("A user with this email and phone number already exists.")
            else:
                st.write("Saving user to CSV...")
                save_user_to_csv(email, phone_number, full_name, age, sex)
                st.success("Registration successful!")
        else:
            st.error("Please fill in all required fields.")

