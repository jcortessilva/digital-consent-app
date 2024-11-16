import streamlit as st
from fpdf import FPDF
import uuid
from datetime import datetime

# Base de datos simulada para usuarios registrados
user_database = {}

# Función para generar un ID único
def generate_unique_id(email, phone):
    return str(uuid.uuid5(uuid.NAMESPACE_DNS, f"{email}-{phone}"))

# Función para generar el PDF del consentimiento
def generate_pdf(consent_data):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    
    pdf.cell(200, 10, txt="Consent Form", ln=True, align='C')
    pdf.ln(10)  # Line break
    
    pdf.cell(200, 10, txt=f"User ID: {consent_data['user_id']}", ln=True)
    pdf.cell(200, 10, txt=f"Between: {consent_data['person1']}", ln=True)
    pdf.cell(200, 10, txt=f"And: {consent_data['person2']}", ln=True)
    pdf.cell(200, 10, txt=f"Date: {consent_data['date']}", ln=True)
    pdf.cell(200, 10, txt=f"Validation Period: {consent_data['start_time']} to {consent_data['end_time']}", ln=True)
    pdf.cell(200, 10, txt=f"Phone Number: {consent_data['phone_number']}", ln=True)
    pdf.cell(200, 10, txt=f"Email: {consent_data['email']}", ln=True)
    pdf.cell(200, 10, txt=f"Person 1 Age: {consent_data['age1']}, Sex: {consent_data['sex1']}", ln=True)
    pdf.cell(200, 10, txt=f"Person 2 Age: {consent_data['age2']}, Sex: {consent_data['sex2']}", ln=True)
    
    pdf.ln(10)
    pdf.cell(200, 10, txt="Both parties consent to this agreement.", ln=True)
    
    return pdf.output(dest="S").encode("latin1")

# Configuración inicial de la app
st.title("Digital Consent App")

# Opción de registro o inicio de sesión
st.sidebar.title("User Authentication")
auth_option = st.sidebar.radio("Select an option:", ["Register", "Sign In"])

# Registro de usuario
if auth_option == "Register":
    st.header("Register a New Account")
    email = st.text_input("Email Address")
    phone_number = st.text_input("Phone Number")
    full_name = st.text_input("Full Name")
    age = st.number_input("Age", min_value=18, max_value=120)
    sex = st.selectbox("Sex", ["Male", "Female", "Other"])
    
    if st.button("Register"):
        if email and phone_number and full_name:
            user_id = generate_unique_id(email, phone_number)
            if user_id not in user_database:
                user_database[user_id] = {
                    "email": email,
                    "phone_number": phone_number,
                    "full_name": full_name,
                    "age": age,
                    "sex": sex,
                }
                st.success(f"Registration successful! Your unique user ID is: {user_id}")
            else:
                st.warning("A user with this email and phone number already exists.")
        else:
            st.error("Please fill in all required fields.")

# Inicio de sesión y formulario de consentimiento
elif auth_option == "Sign In":
    st.header("Sign In to Your Account")
    email = st.text_input("Email Address", key="login_email")
    phone_number = st.text_input("Phone Number", key="login_phone")
    
    if st.button("Sign In"):
        user_id = generate_unique_id(email, phone_number)
        if user_id in user_database:
            st.success(f"Welcome back, {user_database[user_id]['full_name']}!")
            
            # Mostrar formulario de consentimiento
            with st.form("consent_form"):
                person1 = user_database[user_id]['full_name']
                person2 = st.text_input("Other Party's Full Name")
                start_time = st.time_input("Start Time")
                end_time = st.time_input("End Time")
                date = datetime.now().strftime("%Y-%m-%d")
                age2 = st.number_input("Other Party's Age", min_value=18, max_value=120)
                sex2 = st.selectbox("Other Party's Sex", ["Male", "Female", "Other"])
                
                submitted = st.form_submit_button("Generate Consent PDF")
                
                if submitted:
                    if not person2:
                        st.error("Please fill out all required fields.")
                    else:
                        consent_data = {
                            "user_id": user_id,
                            "person1": person1,
                            "person2": person2,
                            "phone_number": user_database[user_id]['phone_number'],
                            "email": user_database[user_id]['email'],
                            "age1": user_database[user_id]['age'],
                            "sex1": user_database[user_id]['sex'],
                            "age2": age2,
                            "sex2": sex2,
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

