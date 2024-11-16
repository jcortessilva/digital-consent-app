import streamlit as st
from fpdf import FPDF
import csv
import os
from datetime import datetime

st.write("Current Working Directory (Streamlit):", os.getcwd())

# Debugging: Print the current working directory
st.write("Current Working Directory:", os.getcwd())

# Debugging: Check if the file exists
if os.path.exists(USER_DATA_FILE):
    st.write("File exists:", os.path.abspath(USER_DATA_FILE))
else:
    st.write("File does not exist. Initializing...")
    initialize_user_data_file()
    if os.path.exists(USER_DATA_FILE):
        st.write("File created successfully at:", os.path.abspath(USER_DATA_FILE))
    else:
        st.error("Failed to create the file.")

# File path for user data
USER_DATA_FILE = "users.csv"

# Function to initialize the CSV file
def initialize_user_data_file():
    try:
        with open(USER_DATA_FILE, mode='x', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["email", "phone_number", "full_name", "age", "sex"])  # Add headers
    except FileExistsError:
        pass

# Function to save a new user to the CSV file
def save_user_to_csv(email, phone_number, full_name, age, sex):
    try:
        with open(USER_DATA_FILE, mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([email, phone_number, full_name, age, sex])
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

# Function to generate the PDF for consent
def generate_pdf(consent_data):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    
    pdf.cell(200, 10, txt="Consent Form", ln=True, align='C')
    pdf.ln(10)  # Line break
    
    pdf.cell(200, 10, txt=f"Between: {consent_data['person1']}", ln=True)
    pdf.cell(200, 10, txt=f"And: {consent_data['person2']}", ln=True)
    pdf.cell(200, 10, txt=f"Date: {consent_data['date']}", ln=True)
    pdf.cell(200, 10, txt=f"Validation Period: {consent_data['start_time']} to {consent_data['end_time']}", ln=True)
    
    return pdf.output(dest="S").encode("latin1")

# Initialize CSV file at the start of the app
initialize_user_data_file()

# Debugging: Display file path
st.write("CSV File Path:", os.path.abspath(USER_DATA_FILE))

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
        if email and phone_number and full_name:
            if user_exists(email, phone_number):
                st.warning("A user with this email and phone number already exists.")
            else:
                save_user_to_csv(email, phone_number, full_name, age, sex)
                st.success("Registration successful!")
        else:
            st.error("Please fill in all required fields.")

# Sign-In
elif auth_option == "Sign In":
    st.header("Sign In to Your Account")
    email = st.text_input("Email Address", key="login_email")
    phone_number = st.text_input("Phone Number", key="login_phone")
    
    if st.button("Sign In"):
        user = user_exists(email, phone_number)
        if user:
            st.success(f"Welcome back, {user['full_name']}!")
            
            # Main interface for consent form
            with st.form("consent_form"):
                person1 = user["full_name"]
                person2 = st.text_input("Other Party's Full Name")
                start_time = st.time_input("Start Time")
                end_time = st.time_input("End Time")
                date = datetime.now().strftime("%Y-%m-%d")
                
                submitted = st.form_submit_button("Generate Consent PDF")
                
                if submitted:
                    if not person2:
                        st.error("Please fill out all required fields.")
                    else:
                        consent_data = {
                            "person1": person1,
                            "person2": person2,
                            "start_time": start_time.strftime("%H:%M"),
                            "end_time": end_time.strftime("%H:%M"),
                            "date": date,
                        }
                        
                        pdf_data = generate_pdf(consent_data)
                        st.success("Consent form generated!")
                        st.download_button(
                            label="Download PDF",
                            data=pdf_data,
                            file_name="consent_form.pdf",
                            mime="application/pdf",
                        )
        else:
            st.error("Invalid email or phone number. Please register first.")
