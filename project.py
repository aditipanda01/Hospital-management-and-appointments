import streamlit as st
import pymysql

# ✅ Set Streamlit page config FIRST
st.set_page_config(layout="wide")

# ✅ Custom Background + Input Styling
page_bg_img = f"""
<style>
html, body, [data-testid="stAppViewContainer"], [data-testid="stAppViewContainer"] > .main {{
    background-image: url("https://images.rawpixel.com/image_800/czNmcy1wcml2YXRlL3Jhd3BpeGVsX2ltYWdlcy93ZWJzaXRlX2NvbnRlbnQvbHIvcm0zNzNiYXRjaDE1LTIxNy0wMS1rcWRqYWp2aC5qcGc.jpg");
    background-size: cover;
    background-repeat: no-repeat;
    background-attachment: fixed;
    background-position: center;
    color: black;
}}

label, .stTextInput label, .stNumberInput label, .stSelectbox label, .stDateInput label, .stTimeInput label, .stTextArea label {{
    color: black !important;
}}

input, textarea, select {{
    background-color: rgba(0, 0, 0, 0.7);
    color: white !important;
    border: 1px solid white;
    border-radius: 5px;
}}

input[type="date"], input[type="time"] {{
    color: white !important;
    background-color: rgba(0, 0, 0, 0.7) !important;
}}

h2 {{
    color: red !important;
    font-weight: bold;
}}

.stButton > button {{
    background-color: red !important;
    color: white !important;
    border-radius: 5px;
    font-weight: bold;
    border: 2px solid darkred;
}}

form#Admit\\ Patient button,
form#Book\\ Appointment button {{
    background-color: red !important;
    color: white !important;
    font-weight: bold;
    border: 2px solid darkred !important;
}}

form#Admit\\ Patient button:none,
form#Book\\ Appointment button:none {{
    background-color: red !important;
    color: white !important;
}}
</style>
"""

st.markdown(page_bg_img, unsafe_allow_html=True)

# ✅ Database connection
def db_connection():
    return pymysql.connect(host="localhost", user="root", passwd="Aditi@1124", database="my_database")

# ✅ Patient functions
def insert_patient(id, name, b_group, desease, medication, addr):
    con = db_connection()
    cur = con.cursor()
    cur.execute("INSERT INTO hospital (id, name, b_group, desease, medication, addr) VALUES (%s, %s, %s, %s, %s, %s)",
                (id, name, b_group, desease, medication, addr))
    con.commit()
    con.close()

def fetch_patient_by_id(pid):
    con = db_connection()
    cur = con.cursor()
    cur.execute("SELECT * FROM hospital WHERE id = %s", (pid,))
    data = cur.fetchone()
    con.close()
    return data

def discharge_patient(pid):
    con = db_connection()
    cur = con.cursor()
    cur.execute("DELETE FROM hospital WHERE id = %s", (pid,))
    con.commit()
    con.close()

# ✅ Appointment functions
def insert_appointment(doctor_name, appointment_date, appointment_time, reason):
    con = db_connection()
    cur = con.cursor()
    cur.execute("INSERT INTO appointments (doctor_name, appointment_date, appointment_time, reason) VALUES (%s, %s, %s, %s)",
                (doctor_name, appointment_date, appointment_time, reason))
    con.commit()
    con.close()

def is_slot_booked(doctor_name, appointment_date, appointment_time):
    con = db_connection()
    cur = con.cursor()
    cur.execute("SELECT COUNT(*) FROM appointments WHERE doctor_name = %s AND appointment_date = %s AND appointment_time = %s",
                (doctor_name, appointment_date, appointment_time))
    result = cur.fetchone()[0]
    con.close()
    return result > 0

# ✅ Streamlit UI
st.title("🏥 Hospital Management System")

if 'selected_patient' not in st.session_state:
    st.session_state.selected_patient = None

# ➕ Admit New Patient
st.subheader("➕ Admit New Patient")
with st.form("Admit Patient"):
    col1, col2 = st.columns(2)
    with col1:
        pid = st.number_input("Patient ID", step=1)
        name = st.text_input("Name")
        b_group = st.text_input("Blood Group")
        desease = st.text_input("Disease")
    with col2:
        medication = st.text_input("Medication")
        addr = st.text_input("Address")
    if st.form_submit_button("Admit"):
        if pid and name and b_group and desease and medication and addr:
            try:
                insert_patient(pid, name, b_group, desease, medication, addr)
                st.success(f"Patient {name} admitted successfully.")
                st.session_state.selected_patient = fetch_patient_by_id(pid)
            except Exception as e:
                st.error(f"Error: {e}")
        else:
            st.warning("Please fill all fields.")

# ⚙ Patient Actions
st.subheader("⚙ Patient Actions")
with st.form("Patient Operations"):
    op_col1, op_col2 = st.columns(2)
    with op_col1:
        p_id = st.number_input("Enter Patient ID", step=1, key="ops_id")
    with op_col2:
        selected_action = st.selectbox("Select Action", ["Fetch Details", "Discharge"])
    if st.form_submit_button("Apply"):
        if not p_id:
            st.warning("Please enter a Patient ID.")
        else:
            try:
                if selected_action == "Fetch Details":
                    patient = fetch_patient_by_id(p_id)
                    if patient:
                        st.success("Patient found!")
                        st.session_state.selected_patient = patient
                    else:
                        st.warning("No patient found with given ID.")
                elif selected_action == "Discharge":
                    discharge_patient(p_id)
                    st.success(f"Patient {p_id} discharged.")
                    st.session_state.selected_patient = None
            except Exception as e:
                st.error(f"Error: {e}")

# 📋 Display Patient Details
if st.session_state.selected_patient:
    st.subheader("📋 Patient Details")
    patient = st.session_state.selected_patient
    patient_data = {
        "ID": patient[0],
        "Name": patient[1],
        "Blood Group": patient[2],
        "Disease": patient[3],
        "Medication": patient[4],
        "Address": patient[5]
    }
    st.table([patient_data])

# 📅 Manage Appointments
st.subheader("📅 Manage Appointments")
with st.form("Book Appointment"):
    col1, col2 = st.columns([2, 1])
    with col1:
        doctor_name = st.text_input("Doctor Name")
        appointment_date = st.date_input("Appointment Date")
        appointment_time = st.time_input("Appointment Time")
    with col2:
        reason = st.text_area("Reason for Appointment")
    if st.form_submit_button("Book Appointment"):
        if is_slot_booked(doctor_name, appointment_date, appointment_time):
            st.error("⚠️ This time slot is already booked for the selected doctor.")
        else:
            try:
                insert_appointment(doctor_name, appointment_date, appointment_time, reason)
                st.success("✅ Appointment booked successfully!")
            except Exception as e:
                st.error(f"Error while booking appointment: {e}")
