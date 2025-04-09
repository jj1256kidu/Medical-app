import streamlit as st
import sys
import os

# Add current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    import plotly.graph_objects as go
    import pandas as pd
    import numpy as np
    from datetime import datetime, timedelta
    import sqlite3
    import time
    import random
    from typing import Dict, List, Tuple
except ImportError as e:
    st.error(f"Required package not found: {str(e)}")
    st.error("Please ensure all dependencies are installed correctly.")
    st.stop()

def check_and_install_plotly():
    try:
        import plotly.graph_objects as go
        return True
    except ImportError:
        st.warning("Plotly not found. Attempting to install...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "plotly==5.18.0"])
            import plotly.graph_objects as go
            return True
        except Exception as e:
            st.error(f"Failed to install plotly: {str(e)}")
            return False

if not check_and_install_plotly():
    st.error("Plotly installation failed. Please check your environment setup.")
    st.stop()

# Set page config
st.set_page_config(
    page_title="SkanRay Real-Time Patient Monitoring System",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Constants
NUM_BEDS = 4
VITAL_SIGNS = {
    'Heart Rate': {'min': 60, 'max': 100, 'unit': 'bpm'},
    'Blood Pressure': {'min': 90, 'max': 140, 'unit': 'mmHg'},
    'SpO2': {'min': 95, 'max': 100, 'unit': '%'},
    'Respiration Rate': {'min': 12, 'max': 20, 'unit': '/min'},
    'Temperature': {'min': 36.5, 'max': 37.5, 'unit': '°C'}
}

# Initialize session state
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'current_user' not in st.session_state:
    st.session_state.current_user = None
if 'patient_data' not in st.session_state:
    st.session_state.patient_data = {}

# Database setup
def init_db():
    conn = sqlite3.connect('patient_monitoring.db')
    c = conn.cursor()
    
    # Create tables
    c.execute('''CREATE TABLE IF NOT EXISTS patients
                 (bed_id INTEGER PRIMARY KEY,
                  name TEXT,
                  age INTEGER,
                  gender TEXT,
                  admission_date TEXT)''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS vitals
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  bed_id INTEGER,
                  timestamp TEXT,
                  heart_rate REAL,
                  blood_pressure REAL,
                  spo2 REAL,
                  respiration_rate REAL,
                  temperature REAL)''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (username TEXT PRIMARY KEY,
                  password TEXT,
                  role TEXT)''')
    
    conn.commit()
    conn.close()

# Initialize database
init_db()

# Patient simulator class
class PatientSimulator:
    def __init__(self, bed_id: int):
        self.bed_id = bed_id
        self.vitals = {}
        self.alarms = []
        self.last_sync = None
        
    def generate_vitals(self) -> Dict:
        vitals = {}
        for vital, params in VITAL_SIGNS.items():
            # Add some randomness to make it more realistic
            value = random.uniform(params['min'], params['max'])
            # Occasionally add some variation for realism
            if random.random() < 0.1:
                value += random.uniform(-5, 5)
            vitals[vital] = round(value, 1)
        return vitals
    
    def check_alarms(self, vitals: Dict) -> List[Dict]:
        alarms = []
        for vital, value in vitals.items():
            params = VITAL_SIGNS[vital]
            if value < params['min'] or value > params['max']:
                severity = 'critical' if abs(value - (params['min'] + params['max'])/2) > 10 else 'warning'
                alarms.append({
                    'vital': vital,
                    'value': value,
                    'severity': severity,
                    'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                })
        return alarms

# Monitor Console View
def monitor_console_view():
    st.title("Monitor Console")
    
    # Create tabs for each bed
    bed_tabs = st.tabs([f"Bed {i+1}" for i in range(NUM_BEDS)])
    
    for i, tab in enumerate(bed_tabs):
        with tab:
            bed_id = i + 1
            if bed_id not in st.session_state.patient_data:
                st.session_state.patient_data[bed_id] = PatientSimulator(bed_id)
            
            patient = st.session_state.patient_data[bed_id]
            
            # Generate new vitals
            vitals = patient.generate_vitals()
            alarms = patient.check_alarms(vitals)
            
            # Display vitals in columns
            col1, col2, col3, col4, col5 = st.columns(5)
            
            with col1:
                st.metric("Heart Rate", f"{vitals['Heart Rate']} bpm")
            with col2:
                st.metric("Blood Pressure", f"{vitals['Blood Pressure']} mmHg")
            with col3:
                st.metric("SpO2", f"{vitals['SpO2']}%")
            with col4:
                st.metric("Respiration Rate", f"{vitals['Respiration Rate']} /min")
            with col5:
                st.metric("Temperature", f"{vitals['Temperature']}°C")
            
            # Display alarms if any
            if alarms:
                st.warning("Active Alarms:")
                for alarm in alarms:
                    st.error(f"{alarm['vital']}: {alarm['value']} ({alarm['severity']})")
            
            # Time series chart
            st.subheader("Vital Signs Trend")
            fig = go.Figure()
            for vital in VITAL_SIGNS.keys():
                fig.add_trace(go.Scatter(
                    x=[datetime.now()],
                    y=[vitals[vital]],
                    name=vital,
                    mode='lines+markers'
                ))
            st.plotly_chart(fig, use_container_width=True)
            
            # Control panel
            st.subheader("Control Panel")
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Simulate USB-HID Data", key=f"usb_{bed_id}"):
                    st.success("USB-HID data simulated successfully")
            with col2:
                if st.button("Sync to Central Server", key=f"sync_{bed_id}"):
                    patient.last_sync = datetime.now()
                    st.success(f"Last synced: {patient.last_sync}")

# Central Nursing System View
def cns_view():
    st.title("Central Nursing System")
    
    # Role-based access control
    if not st.session_state.authenticated:
        st.warning("Please login to access the CNS")
        return
    
    # Display all patients in a table
    st.subheader("Patient Overview")
    patient_data = []
    for bed_id, patient in st.session_state.patient_data.items():
        vitals = patient.generate_vitals()
        patient_data.append({
            'Bed ID': bed_id,
            'Heart Rate': vitals['Heart Rate'],
            'Blood Pressure': vitals['Blood Pressure'],
            'SpO2': vitals['SpO2'],
            'Respiration Rate': vitals['Respiration Rate'],
            'Temperature': vitals['Temperature']
        })
    
    df = pd.DataFrame(patient_data)
    st.dataframe(df, use_container_width=True)
    
    # Alarm panel
    st.subheader("Alarm Panel")
    all_alarms = []
    for patient in st.session_state.patient_data.values():
        all_alarms.extend(patient.check_alarms(patient.generate_vitals()))
    
    if all_alarms:
        for alarm in all_alarms:
            st.error(f"Bed {alarm.get('bed_id', 'Unknown')}: {alarm['vital']} - {alarm['value']} ({alarm['severity']})")
    else:
        st.success("No active alarms")

# Login page
def login_page():
    st.title("SkanRay Login")
    
    # Simple login form (in production, use proper authentication)
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    role = st.selectbox("Role", ["Doctor", "Nurse", "Admin"])
    
    if st.button("Login"):
        # Simple authentication (in production, use proper authentication)
        if username and password:
            st.session_state.authenticated = True
            st.session_state.current_user = {"username": username, "role": role}
            st.success("Login successful!")
            st.rerun()
        else:
            st.error("Please enter both username and password")

# Main app
def main():
    # Sidebar navigation
    st.sidebar.title("Navigation")
    if not st.session_state.authenticated:
        login_page()
    else:
        page = st.sidebar.radio(
            "Go to",
            ["Monitor Console", "Central Nursing System", "Admin Panel", "Logs"]
        )
        
        if page == "Monitor Console":
            monitor_console_view()
        elif page == "Central Nursing System":
            cns_view()
        elif page == "Admin Panel":
            st.title("Admin Panel")
            st.write("Admin features coming soon...")
        elif page == "Logs":
            st.title("System Logs")
            st.write("Log viewing features coming soon...")
        
        # Logout button
        if st.sidebar.button("Logout"):
            st.session_state.authenticated = False
            st.session_state.current_user = None
            st.rerun()

if __name__ == "__main__":
    main() 
