import streamlit as st
import csv
import os
from fpdf import FPDF
from datetime import datetime, timedelta

# File paths for user data and pending consents
USER_DATA_FILE = "users.csv"
PENDING_CONSENTS_FILE = "pending_consents.csv"

# Function to initialize CSV files
def initialize_csv_file(file_path, headers):
    try:
        with open(file_path, mode='x', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(headers)
    except FileExistsError:
        pass

# Initialize CSV files
initialize_csv_file(USER_DATA_FILE, ["email", "phone_number", "full_name", "age", "sex"])
initialize_csv_file(PENDING_CONSENTS_FILE, ["initiator", "other_party_email", "details", "validity", "status"])

# Function to save a new record to a CSV file
def save_to_csv(file_path, data):
    try:
        with open(file_path, mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(data)
    except Exception as e:
        st.error(f"Error saving data: {e}")

# Function to check if a user exists by email and phone
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

# Function to check if a user exists by email
def user_exists_by_email(email):
    try:
        with open(USER_DATA_FILE, mode='r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                if row["email"].strip().lower() == email.strip().lower():
                    return True  # Return True if user is found
    except FileNotFoundError:
        st.error("CSV file not found.")
    return False

# Function to fetch pending consents for a user
def get_pending_consents(email):
    try:
        with open(PENDING_CONSENTS_FILE, mode='r') as file:
            reader = csv.DictReader(file)
            return [row for row in reader if row["other_party_email"] == email and row["status"] == "pending"]
    except FileNotFoundError:
        st.error("CSV file not found.")
    return []

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
    pdf.cell(200, 10, txt=f"Signed by: {consent_data['initiator']}", ln=True)
    pdf.cell(200, 10, txt=f"Other Party: {consent_data['other_party_email']}", ln=True)
    pdf.ln(10)
    
    pdf.cell(200, 10, txt="Consent Agreement:", ln=True)
    pdf.multi_cell(0, 10, consent_data['details'])
    
    return pdf.output(dest="S").encode("latin1")

# Streamlit app title
st.title("Digital Consent App")

# Sidebar for registration and sign-in options
auth_option = st.sidebar.radio("Select an option:", ["Register", "Sign In"])

# Session state to persist user data
if "user" not in st.session_state:
    st.session_state.user = None

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
                save_to_csv(USER_DATA_FILE, [email, phone_number, full_name, age, sex])
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
            st.session_state.user = user
            st.success(f"Welcome back, {user['full_name']}!")
        else:
            st.error("Invalid email or phone number. Please register first.")

# Consent Writing Section
if st.session_state.user:
    st.subheader("Write Your Consent Agreement")
    other_party_email = st.text_input("Email of the Other Party", key="other_party_email")
    validity_hours = st.selectbox("Validity Period (hours)", [24, 28], key="validity_hours")
    consent_details = st.text_area("Enter the consent details (e.g., purpose):", key="consent_details")
    
    if st.button("Send Consent Request"):
        if not other_party_email.strip() or not consent_details.strip():
            st.error("Please fill in all fields.")
        elif not user_exists_by_email(other_party_email):
            st.error(f"The email '{other_party_email}' is not registered. Please ensure both parties have an account.")
        else:
            validity = (datetime.now() + timedelta(hours=validity_hours)).strftime("%Y-%m-%d %H:%M:%S")
            save_to_csv(PENDING_CONSENTS_FILE, [st.session_state.user["email"], other_party_email, consent_details.strip(), validity, "pending"])
            st.success(f"Consent request sent to {other_party_email}!")

# Approval Section
if st.session_state.user:
    pending_consents = get_pending_consents(st.session_state.user["email"])
    if pending_consents:
        st.subheader("Pending Consents for Your Approval")
        for consent in pending_consents:
            st.text(f"Consent from {consent['initiator']}: {consent['details']}")
            if st.button(f"Approve Consent from {consent['initiator']}"):
                consent["status"] = "approved"
                st.success(f"Consent approved for {consent['initiator']}")



