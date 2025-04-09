import streamlit as st

# Set page config with modern theme (MUST BE FIRST STREAMLIT COMMAND)
st.set_page_config(
    page_title="SkanRay Real-Time Patient Monitoring System",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://www.skanray.com/support',
        'Report a bug': "https://www.skanray.com/bug",
        'About': "# SkanRay Real-Time Patient Monitoring System v2.0"
    }
)

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

# Custom CSS for modern, futuristic look
st.markdown("""
    <style>
    /* Main theme colors */
    :root {
        --primary-color: #00a8e8;
        --secondary-color: #003459;
        --accent-color: #007ea7;
        --background-color: #00171f;
        --text-color: #ffffff;
    }
    
    /* Global styles */
    .stApp {
        background-color: var(--background-color);
        color: var(--text-color);
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background-color: var(--secondary-color) !important;
    }
    
    /* Button styling */
    .stButton>button {
        background-color: var(--primary-color);
        color: white;
        border-radius: 10px;
        border: none;
        padding: 10px 20px;
        font-weight: bold;
        transition: all 0.3s ease;
    }
    
    .stButton>button:hover {
        background-color: var(--accent-color);
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0, 168, 232, 0.3);
    }
    
    /* Metric cards */
    .metric-card {
        background: linear-gradient(145deg, var(--secondary-color), var(--background-color));
        border-radius: 15px;
        padding: 20px;
        margin: 10px;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
        transition: all 0.3s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 16px rgba(0, 168, 232, 0.4);
    }
    
    /* Alert styling */
    .alert-critical {
        background-color: #ff4444;
        color: white;
        padding: 10px;
        border-radius: 10px;
        margin: 5px 0;
        animation: pulse 2s infinite;
    }
    
    .alert-warning {
        background-color: #ffbb33;
        color: white;
        padding: 10px;
        border-radius: 10px;
        margin: 5px 0;
    }
    
    @keyframes pulse {
        0% { opacity: 1; }
        50% { opacity: 0.7; }
        100% { opacity: 1; }
    }
    
    /* Chart containers */
    .chart-container {
        background: rgba(0, 55, 95, 0.2);
        border-radius: 15px;
        padding: 20px;
        margin: 10px 0;
    }
    
    /* Login page styling */
    .login-container {
        max-width: 400px;
        margin: 0 auto;
        padding: 20px;
        background: rgba(0, 55, 95, 0.3);
        border-radius: 15px;
        box-shadow: 0 8px 16px rgba(0, 0, 0, 0.2);
    }
    </style>
""", unsafe_allow_html=True)

# Predefined users
USERS = {
    "doctor": {
        "password": "doctor123",
        "role": "Doctor",
        "name": "Dr. Smith"
    },
    "nurse": {
        "password": "nurse123",
        "role": "Nurse",
        "name": "Nurse Johnson"
    },
    "admin": {
        "password": "admin123",
        "role": "Admin",
        "name": "Admin"
    }
}

# Constants
NUM_BEDS = 4
VITAL_SIGNS = {
    'Heart Rate': {'min': 60, 'max': 100, 'unit': 'bpm', 'icon': '❤️'},
    'Blood Pressure': {'min': 90, 'max': 140, 'unit': 'mmHg', 'icon': '🩸'},
    'SpO2': {'min': 95, 'max': 100, 'unit': '%', 'icon': '🫁'},
    'Respiration Rate': {'min': 12, 'max': 20, 'unit': '/min', 'icon': '🌬️'},
    'Temperature': {'min': 36.5, 'max': 37.5, 'unit': '°C', 'icon': '🌡️'}
}

# Initialize session state
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'current_user' not in st.session_state:
    st.session_state.current_user = None
if 'patient_data' not in st.session_state:
    st.session_state.patient_data = {}

# Modern login page
def login_page():
    st.markdown("""
        <div style='text-align: center; margin-bottom: 30px;'>
            <h1 style='color: #00a8e8; font-size: 2.5em;'>SkanRay</h1>
            <h2 style='color: #ffffff;'>Real-Time Patient Monitoring System</h2>
        </div>
    """, unsafe_allow_html=True)
    
    with st.container():
        st.markdown('<div class="login-container">', unsafe_allow_html=True)
        
        # Login form
        username = st.text_input("Username", key="username").lower()
        password = st.text_input("Password", type="password", key="password")
        
        if st.button("Login", key="login_button"):
            if username in USERS and password == USERS[username]["password"]:
                st.session_state.authenticated = True
                st.session_state.current_user = {
                    "username": username,
                    "role": USERS[username]["role"],
                    "name": USERS[username]["name"]
                }
                st.success(f"Welcome, {USERS[username]['name']}!")
                st.rerun()
            else:
                st.error("Invalid credentials. Please try again.")
        
        st.markdown('</div>', unsafe_allow_html=True)

# Modern monitor console view
def monitor_console_view():
    st.markdown("""
        <div style='text-align: center; margin-bottom: 30px;'>
            <h1 style='color: #00a8e8;'>Monitor Console</h1>
            <p style='color: #ffffff;'>Real-time patient monitoring dashboard</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Create tabs for each bed with modern styling
    bed_tabs = st.tabs([f"Bed {i+1} 🏥" for i in range(NUM_BEDS)])
    
    for i, tab in enumerate(bed_tabs):
        with tab:
            bed_id = i + 1
            if bed_id not in st.session_state.patient_data:
                st.session_state.patient_data[bed_id] = PatientSimulator(bed_id)
            
            patient = st.session_state.patient_data[bed_id]
            vitals = patient.generate_vitals()
            alarms = patient.check_alarms(vitals)
            
            # Modern metric display
            cols = st.columns(5)
            for idx, (vital, value) in enumerate(vitals.items()):
                with cols[idx]:
                    st.markdown(f"""
                        <div class="metric-card">
                            <h3>{VITAL_SIGNS[vital]['icon']} {vital}</h3>
                            <h2 style='color: #00a8e8;'>{value} {VITAL_SIGNS[vital]['unit']}</h2>
                        </div>
                    """, unsafe_allow_html=True)
            
            # Alarm display with modern styling
            if alarms:
                st.markdown("### 🚨 Active Alarms")
                for alarm in alarms:
                    alert_class = "alert-critical" if alarm['severity'] == 'critical' else "alert-warning"
                    st.markdown(f"""
                        <div class="{alert_class}">
                            <strong>{alarm['vital']}</strong>: {alarm['value']} ({alarm['severity']})
                        </div>
                    """, unsafe_allow_html=True)
            
            # Modern chart display
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            st.subheader("Vital Signs Trend")
            fig = go.Figure()
            for vital in VITAL_SIGNS.keys():
                fig.add_trace(go.Scatter(
                    x=[datetime.now()],
                    y=[vitals[vital]],
                    name=vital,
                    mode='lines+markers',
                    line=dict(color='#00a8e8', width=2)
                ))
            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='white'),
                xaxis=dict(showgrid=False),
                yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.1)')
            )
            st.plotly_chart(fig, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Modern control panel
            st.markdown("### Control Panel")
            col1, col2 = st.columns(2)
            with col1:
                if st.button("🔄 Sync Data", key=f"sync_{bed_id}"):
                    patient.last_sync = datetime.now()
                    st.success(f"Last synced: {patient.last_sync.strftime('%H:%M:%S')}")
            with col2:
                if st.button("📊 Export Data", key=f"export_{bed_id}"):
                    st.success("Data exported successfully")

# Modern CNS view
def cns_view():
    st.markdown("""
        <div style='text-align: center; margin-bottom: 30px;'>
            <h1 style='color: #00a8e8;'>Central Nursing System</h1>
            <p style='color: #ffffff;'>Multi-bed monitoring dashboard</p>
        </div>
    """, unsafe_allow_html=True)
    
    if not st.session_state.authenticated:
        st.warning("Please login to access the CNS")
        return
    
    # Modern patient overview
    st.markdown("### Patient Overview")
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
    st.dataframe(
        df.style.background_gradient(cmap='Blues'),
        use_container_width=True
    )
    
    # Modern alarm panel
    st.markdown("### Alarm Panel")
    all_alarms = []
    for patient in st.session_state.patient_data.values():
        all_alarms.extend(patient.check_alarms(patient.generate_vitals()))
    
    if all_alarms:
        for alarm in all_alarms:
            alert_class = "alert-critical" if alarm['severity'] == 'critical' else "alert-warning"
            st.markdown(f"""
                <div class="{alert_class}">
                    <strong>Bed {alarm.get('bed_id', 'Unknown')}</strong>: {alarm['vital']} - {alarm['value']} ({alarm['severity']})
                </div>
            """, unsafe_allow_html=True)
    else:
        st.success("No active alarms")

# Main app with modern navigation
def main():
    # Modern sidebar
    with st.sidebar:
        st.markdown("""
            <div style='text-align: center; margin-bottom: 30px;'>
                <h2 style='color: #00a8e8;'>SkanRay</h2>
                <p style='color: #ffffff;'>Patient Monitoring</p>
            </div>
        """, unsafe_allow_html=True)
        
        if st.session_state.authenticated:
            st.markdown(f"""
                <div style='text-align: center; margin-bottom: 20px;'>
                    <p style='color: #00a8e8;'>Welcome, {st.session_state.current_user['name']}</p>
                    <p style='color: #ffffff;'>{st.session_state.current_user['role']}</p>
                </div>
            """, unsafe_allow_html=True)
    
    if not st.session_state.authenticated:
        login_page()
    else:
        page = st.sidebar.radio(
            "Navigation",
            ["Monitor Console", "Central Nursing System", "Admin Panel", "Logs"],
            format_func=lambda x: f"📊 {x}" if x == "Monitor Console" else 
                                f"🏥 {x}" if x == "Central Nursing System" else
                                f"⚙️ {x}" if x == "Admin Panel" else
                                f"📝 {x}"
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
        
        if st.sidebar.button("Logout"):
            st.session_state.authenticated = False
            st.session_state.current_user = None
            st.rerun()

if __name__ == "__main__":
    main() 
