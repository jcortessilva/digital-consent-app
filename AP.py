import streamlit as st
import csv
import os
import smtplib
import uuid
import urllib.parse
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
from dotenv import load_dotenv, find_dotenv

# Load environment variables from email.env
dotenv_path = find_dotenv("email.env")
if not dotenv_path:
    st.error("Error: email.env file not found. Ensure it is in the correct location.")
else:
    st.write(f"Loaded environment variables from: {dotenv_path}")
    load_dotenv(dotenv_path)

# Environment variables
SMTP_SERVER = os.getenv("SMTP_SERVER")
SMTP_PORT = os.getenv("SMTP_PORT")
EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")  # Should always be "apikey" for SendGrid
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
VERIFIED_SENDER_EMAIL = "consentapptest@gmail.com"

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
initialize_csv_file(PENDING_CONSENTS_FILE, ["id", "initiator", "other_party_email", "details", "validity", "status", "confirmation_link"])

# Function to save a new record to a CSV file
def save_to_csv(file_path, data):
    try:
        with open(file_path, mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(data)
    except Exception as e:
        st.error(f"Error saving data: {e}")

# Function to send an email
def send_email(to_email, subject, body):
    if not SMTP_PORT:
        st.error("SMTP_PORT is invalid. Fix your email.env file and restart.")
        return False

    try:
        # Create the email message
        msg = MIMEMultipart()
        msg["From"] = VERIFIED_SENDER_EMAIL
        msg["To"] = to_email
        msg["Subject"] = subject

        msg.attach(MIMEText(body, "plain"))

        # Connect to the SMTP server
        with smtplib.SMTP(SMTP_SERVER, int(SMTP_PORT)) as server:
            server.ehlo()
            server.starttls()
            server.ehlo()
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            server.send_message(msg)

        return True
    except Exception as e:
        st.error(f"Error sending email: {e}")
        return False

# Function to check if a user exists by email
def user_exists_by_email(email):
    try:
        with open(USER_DATA_FILE, mode='r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                if row["email"].strip().lower() == email.strip().lower():
                    return True
    except FileNotFoundError:
        st.error("CSV file not found.")
    return False

# Function to handle consent by ID
def handle_consent_by_id():
    query_params = st.query_params
    st.write("Debugging: Raw Query Params")
    st.write(query_params)

    # Retrieve the consent_id
    consent_id = st.query_params.get("consent_id", None)
    if isinstance(consent_id, list):
        consent_id = consent_id[0]  # Use the first value if it's a list

    # Debugging: Log the parsed consent ID
    st.write(f"Parsed consent_id: {consent_id}")

    if not consent_id:
        st.error("No consent ID found in the query parameters.")
        st.write("Make sure the URL contains the consent_id parameter.")
        st.write("Example: http://localhost:8501/?consent_id=<unique_consent_id>")
        return False

    # Debugging: Log the full consent ID
    st.write("Debugging: Consent Confirmation")
    st.write(f"Consent ID from Link: {consent_id}")

    try:
        with open(PENDING_CONSENTS_FILE, mode='r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                # Debugging: Log each row being checked
                st.write(f"Checking Row: {row}")
                
                if row["id"] == consent_id:
                    if row["status"] != "pending":
                        st.error("This consent has already been processed.")
                        return True
                    
                    # Display consent details
                    st.subheader("Consent Details")
                    st.write(f"Initiator: {row['initiator']}")
                    st.write(f"Other Party: {row['other_party_email']}")
                    st.write(f"Details: {row['details']}")
                    st.write(f"Validity: {row['validity']}")

                    # Add options to confirm or reject
                    col1, col2 = st.columns(2)
                    if col1.button("Confirm Consent"):
                        update_consent_status(consent_id, "confirmed")
                        st.success("Consent confirmed successfully!")
                        notify_initiator(row['initiator'], "confirmed")
                    if col2.button("Reject Consent"):
                        update_consent_status(consent_id, "rejected")
                        st.warning("Consent rejected.")
                        notify_initiator(row['initiator'], "rejected")
                    return True

            st.error("Consent not found.")
    except FileNotFoundError:
        st.error("Pending consents file not found.")
    except Exception as e:
        st.error(f"Error handling consent: {e}")
    return True

# Function to update consent status
def update_consent_status(consent_id, new_status):
    updated_rows = []
    try:
        with open(PENDING_CONSENTS_FILE, mode='r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                if row["id"] == consent_id:
                    row["status"] = new_status
                updated_rows.append(row)
        with open(PENDING_CONSENTS_FILE, mode='w', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=reader.fieldnames)
            writer.writeheader()
            writer.writerows(updated_rows)
    except Exception as e:
        st.error(f"Error updating consent status: {e}")

# Function to notify initiator
def notify_initiator(initiator_email, status):
    subject = "Consent Request Update"
    body = f"Your consent request has been {status}."
    send_email(initiator_email, subject, body)

# Check for consent ID and handle it
if handle_consent_by_id():
    st.stop()

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
            with open(USER_DATA_FILE, mode='a', newline='') as file:
                writer = csv.writer(file)
                writer.writerow([email, phone_number, full_name, age, sex])
                st.success("Registration successful!")
        else:
            st.error("Please fill in all required fields.")

# Sign-In
elif auth_option == "Sign In":
    st.header("Sign In to Your Account")
    email = st.text_input("Email Address", key="login_email")
    phone_number = st.text_input("Phone Number", key="login_phone")
    
    if st.button("Sign In"):
        with open(USER_DATA_FILE, mode='r') as file:
            reader = csv.DictReader(file)
            user = next((row for row in reader if row["email"] == email and row["phone_number"] == phone_number), None)
            if user:
                st.session_state["user"] = user
                st.success(f"Welcome back, {user['full_name']}!")
            else:
                st.error("Invalid email or phone number. Please register first.")

# Consent Writing Section
if "user" in st.session_state:
    st.subheader("Write Your Consent Agreement")
    other_party_email = st.text_input("Email of the Other Party")
    validity_hours = st.selectbox("Validity Period (hours)", [24, 28])
    consent_details = st.text_area("Enter the consent details (e.g., purpose):")
    
    if st.button("Send Consent Request"):
        if not other_party_email.strip() or not consent_details.strip():
            st.error("Please fill in all fields.")
        elif not user_exists_by_email(other_party_email):
            st.error(f"The email '{other_party_email}' is not registered. Please ensure both parties have an account.")
        else:
            unique_consent_id = str(uuid.uuid4())
            validity = (datetime.now() + timedelta(hours=validity_hours)).strftime("%Y-%m-%d %H:%M:%S")
            confirmation_link = f"http://localhost:8501/?consent_id={urllib.parse.quote_plus(unique_consent_id)}"

            # Debugging: Log details of the consent being saved
            st.write("Debugging: Consent Saving")
            st.write(f"Unique Consent ID: {unique_consent_id}")
            st.write(f"Confirmation Link: {confirmation_link}")

            save_to_csv(PENDING_CONSENTS_FILE, [unique_consent_id, st.session_state["user"]["email"], other_party_email, consent_details, validity, "pending", confirmation_link])
            email_sent = send_email(other_party_email, "Consent Request", f"Please confirm the consent: {confirmation_link}")
            if email_sent:
                st.success(f"Consent request sent to {other_party_email}.")


