import streamlit as st
import csv
import os
from fpdf import FPDF
from datetime import datetime, timedelta

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
        st.error("CSV file not found.")
    return None

# Function to generate the PDF for consent
def generate_pdf(consent_data):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    
    # Header
    pdf.cell(200, 10, txt="Voluntary Consent Form", ln=True, align='C')
    pdf.ln(10)
    
    # Consent details
    pdf.cell(200, 10, txt=f"Date: {consent_data['date']}", ln=True)
    pdf.cell(200, 10, txt=f"Validity: {consent_data['validity']}", ln=True)
    pdf.cell(200, 10, txt=f"Signed by: {consent_data['signer_name']}", ln=True)
    pdf.cell(200, 10, txt=f"Other Party: {consent_data['other_party']}", ln=True)
    pdf.ln(10)
    
    pdf.cell(200, 10, txt="Consent Agreement:", ln=True)
    pdf.multi_cell(0, 10, consent_data['details'])
    
    return pdf.output(dest="S").encode("latin1")

# Initialize the CSV file
initialize_user_data_file()

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
            
            # Consent Writing Section
            st.subheader("Write Your Consent Agreement")
            other_party = st.text_input("Full Name of the Other Party")
            validity_hours = st.selectbox("Validity Period (hours)", [24, 28])
            consent_details = st.text_area("Enter the consent details (e.g., purpose):")
            
            if st.button("Generate Consent PDF"):
                if not other_party.strip() or not consent_details.strip():
                    st.error("Please fill in all fields.")
                else:
                    consent_data = {
                        "signer_name": user["full_name"],
                        "other_party": other_party.strip(),
                        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "validity": (datetime.now() + timedelta(hours=validity_hours)).strftime("%Y-%m-%d %H:%M:%S"),
                        "details": consent_details.strip(),
                    }
                    
                    pdf_data = generate_pdf(consent_data)
                    
                    st.success("Consent form generated!")
                    st.download_button(
                        label="Download Consent PDF",
                        data=pdf_data,
                        file_name="consent_form.pdf",
                        mime="application/pdf",
                    )
        else:
            st.error("Invalid email or phone number. Please register first.")


