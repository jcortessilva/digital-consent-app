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
from fpdf import FPDF

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

# Initialize CSV files
def initialize_csv_file(file_path, headers):
    try:
        with open(file_path, mode='x', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(headers)
    except FileExistsError:
        pass

initialize_csv_file(USER_DATA_FILE, ["email", "phone_number", "full_name", "age", "sex"])
initialize_csv_file(PENDING_CONSENTS_FILE, ["id", "initiator", "other_party_email", "details", "validity", "status", "confirmation_link"])

# Save a new record to a CSV file
def save_to_csv(file_path, data):
    try:
        with open(file_path, mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(data)
    except Exception as e:
        st.error(f"Error saving data: {e}")

# Send an email
def send_email(to_email, subject, body):
    try:
        st.write(f"Preparing to send email to {to_email}")
        st.write(f"SMTP_SERVER: {SMTP_SERVER}")
        st.write(f"SMTP_PORT: {SMTP_PORT}")
        st.write(f"VERIFIED_SENDER_EMAIL: {VERIFIED_SENDER_EMAIL}")

        msg = MIMEMultipart()
        msg["From"] = VERIFIED_SENDER_EMAIL
        msg["To"] = to_email
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))

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

# Check if a user exists by email
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

# Generate a PDF of the consent
def generate_pdf(consent_data):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    pdf.cell(200, 10, txt="Consent Agreement", ln=True, align='C')
    pdf.ln(10)

    pdf.cell(200, 10, txt=f"Consent ID: {consent_data['id']}", ln=True)
    pdf.cell(200, 10, txt=f"Initiator: {consent_data['initiator']}", ln=True)
    pdf.cell(200, 10, txt=f"Other Party: {consent_data['other_party_email']}", ln=True)
    pdf.cell(200, 10, txt=f"Details: {consent_data['details']}", ln=True)
    pdf.cell(200, 10, txt=f"Validity: {consent_data['validity']}", ln=True)
    pdf.cell(200, 10, txt=f"Status: {consent_data['status']}", ln=True)

    pdf.ln(10)
    pdf.cell(200, 10, txt="Both parties consented to this agreement.", ln=True)

    return pdf.output(dest="S").encode("latin1")

# Notify initiator about consent status
def notify_initiator(initiator_email, status):
    subject = "Consent Request Update"
    body = f"Your consent request has been {status}."

    st.write(f"Sending notification to initiator: {initiator_email}")
    email_sent = send_email(initiator_email, subject, body)

    if email_sent:
        st.success(f"Notification sent to {initiator_email}.")
    else:
        st.error(f"Failed to send notification to {initiator_email}.")

# Update consent status in the file
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

# Handle consent by ID
def handle_consent_by_id():
    query_params = st.query_params
    consent_id = query_params.get("consent_id", None)
    if isinstance(consent_id, list):
        consent_id = consent_id[0]

    if not consent_id:
        return False

    try:
        with open(PENDING_CONSENTS_FILE, mode='r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                if row["id"] == consent_id:
                    if row["status"] == "confirmed":
                        st.success("This consent has already been confirmed.")
                        return True
                    elif row["status"] == "rejected":
                        st.error("This consent was rejected.")
                        return True

                    st.subheader("Consent Details")
                    st.write(f"Initiator: {row['initiator']}")
                    st.write(f"Other Party: {row['other_party_email']}")
                    st.write(f"Details: {row['details']}")
                    st.write(f"Validity: {row['validity']}")

                    col1, col2 = st.columns(2)
                    if col1.button("Confirm Consent"):
                        update_consent_status(consent_id, "confirmed")
                        st.success("Consent confirmed successfully!")

                        pdf_data = generate_pdf(row)
                        st.download_button(
                            label="Download Consent PDF",
                            data=pdf_data,
                            file_name=f"consent_{consent_id}.pdf",
                            mime="application/pdf",
                        )
                        notify_initiator(row['initiator'], "confirmed")
                        return True
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

# Main application logic
if not handle_consent_by_id():
    st.title("Digital Consent App")

    auth_option = st.sidebar.radio("Select an option:", ["Register", "Sign In"])

    if auth_option == "Register":
        st.header("Register a New Account")
        email = st.text_input("Email Address")
        phone_number = st.text_input("Phone Number")
        full_name = st.text_input("Full Name")
        age = st.number_input("Age", min_value=18, max_value=120)
        sex = st.selectbox("Sex", ["Male", "Female", "Other"])

        if st.button("Register"):
            if email and phone_number and full_name:
                save_to_csv(USER_DATA_FILE, [email, phone_number, full_name, age, sex])
                st.success("Registration successful!")
            else:
                st.error("Please fill in all required fields.")

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

                save_to_csv(PENDING_CONSENTS_FILE, [unique_consent_id, st.session_state["user"]["email"], other_party_email, consent_details, validity, "pending", confirmation_link])
                email_sent = send_email(other_party_email, "Consent Request", f"Please confirm the consent: {confirmation_link}")
                if email_sent:
                    st.success(f"Consent request sent to {other_party_email}.")


