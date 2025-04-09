import streamlit as st
from streamlit_option_menu import option_menu
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import time
import random
from typing import Dict, List, Tuple
import os
import json
from auth import AuthHandler
from models import init_db, Patient, VitalSign, Alarm, SystemLog
from hl7_simulator import HL7Simulator

# Initialize components
auth_handler = AuthHandler()
db_session = init_db()
hl7_simulator = HL7Simulator()

# Set page config (MUST BE FIRST STREAMLIT COMMAND)
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

# Custom CSS for professional healthcare monitoring interface
st.markdown("""
    <style>
    /* Main theme colors */
    :root {
        --primary-color: #1a237e;
        --secondary-color: #283593;
        --accent-color: #3949ab;
        --background-color: #f8f9fa;
        --text-color: #212529;
        --card-bg: #ffffff;
        --border-color: #e0e0e0;
        --success-color: #2e7d32;
        --warning-color: #ed6c02;
        --danger-color: #d32f2f;
        --info-color: #0288d1;
    }
    
    /* Global styles */
    .stApp {
        background-color: var(--background-color);
        color: var(--text-color);
        font-family: 'Roboto', 'Helvetica Neue', Arial, sans-serif;
        line-height: 1.5;
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background-color: var(--primary-color) !important;
        color: white !important;
        font-weight: 500;
    }
    
    /* Button styling */
    .stButton>button {
        background-color: var(--accent-color);
        color: white;
        border-radius: 4px;
        border: none;
        padding: 8px 16px;
        font-weight: 500;
        transition: all 0.2s ease;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        text-transform: uppercase;
        letter-spacing: 0.5px;
        font-size: 0.875rem;
    }
    
    .stButton>button:hover {
        background-color: var(--secondary-color);
        transform: translateY(-1px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
    
    /* Metric cards */
    .metric-card {
        background: var(--card-bg);
        border-radius: 4px;
        padding: 16px;
        margin: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        border: 1px solid var(--border-color);
        transition: all 0.2s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.15);
    }
    
    .metric-card h3 {
        color: var(--secondary-color);
        font-size: 0.875rem;
        margin-bottom: 8px;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .metric-card h2 {
        color: var(--primary-color);
        font-size: 1.5rem;
        margin: 0;
        font-weight: 600;
    }
    
    /* Alert styling */
    .alert-critical {
        background-color: var(--danger-color);
        color: white;
        padding: 12px 16px;
        border-radius: 4px;
        margin: 8px 0;
        font-weight: 500;
        border-left: 4px solid #b71c1c;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    
    .alert-warning {
        background-color: var(--warning-color);
        color: white;
        padding: 12px 16px;
        border-radius: 4px;
        margin: 8px 0;
        font-weight: 500;
        border-left: 4px solid #e65100;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    
    /* Chart containers */
    .chart-container {
        background: var(--card-bg);
        border-radius: 4px;
        padding: 16px;
        margin: 16px 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        border: 1px solid var(--border-color);
    }
    
    /* Login page styling */
    .login-container {
        max-width: 400px;
        margin: 40px auto;
        padding: 24px;
        background: var(--card-bg);
        border-radius: 4px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        border: 1px solid var(--border-color);
    }
    
    /* Text styling */
    h1, h2, h3, h4, h5, h6 {
        color: var(--primary-color);
        font-weight: 600;
        margin-bottom: 1rem;
    }
    
    /* Table styling */
    .stDataFrame {
        background-color: var(--card-bg);
        border-radius: 4px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        border: 1px solid var(--border-color);
    }
    
    /* Form elements */
    .stTextInput>div>div>input,
    .stSelectbox>div>div>select {
        border: 1px solid var(--border-color);
        border-radius: 4px;
        padding: 8px 12px;
        font-size: 0.875rem;
    }
    
    /* Tabs styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 2rem;
        border-bottom: 2px solid var(--border-color);
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 48px;
        white-space: pre-wrap;
        background-color: transparent;
        border-radius: 4px 4px 0 0;
        gap: 1rem;
        padding: 0 16px;
        font-weight: 500;
        color: var(--text-color);
    }
    
    .stTabs [aria-selected="true"] {
        background-color: var(--accent-color);
        color: white;
    }
    
    /* Status indicators */
    .status-indicator {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        padding: 4px 8px;
        border-radius: 4px;
        font-weight: 500;
        font-size: 0.875rem;
    }
    
    .status-online {
        background-color: #e8f5e9;
        color: var(--success-color);
    }
    
    .status-offline {
        background-color: #ffebee;
        color: var(--danger-color);
    }
    
    /* Vital signs grid */
    .vitals-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 16px;
        margin: 16px 0;
    }
    
    /* Alarm indicators */
    .alarm-indicator {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        padding: 4px 8px;
        border-radius: 4px;
        font-weight: 500;
        font-size: 0.875rem;
    }
    
    .alarm-critical {
        background-color: #ffebee;
        color: var(--danger-color);
    }
    
    .alarm-warning {
        background-color: #fff3e0;
        color: var(--warning-color);
    }
    
    /* Control panel */
    .control-panel {
        background: var(--card-bg);
        border-radius: 4px;
        padding: 16px;
        margin: 16px 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        border: 1px solid var(--border-color);
    }
    </style>
""", unsafe_allow_html=True)

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
if 'theme' not in st.session_state:
    st.session_state.theme = 'dark'

# Modern login page
def login_page():
    st.markdown("""
        <div style='text-align: center; margin-bottom: 40px;'>
            <h1 style='color: var(--primary-color); font-size: 2.5em; margin-bottom: 10px;'>SkanRay</h1>
            <h2 style='color: var(--secondary-color); font-size: 1.5em;'>Real-Time Patient Monitoring System</h2>
        </div>
    """, unsafe_allow_html=True)
    
    with st.container():
        st.markdown('<div class="login-container">', unsafe_allow_html=True)
        
        # Login form
        username = st.text_input("Username", key="username").lower()
        password = st.text_input("Password", type="password", key="password")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Login", key="login_button"):
                user_data = auth_handler.login(username, password)
                if user_data:
                    st.session_state.authenticated = True
                    st.session_state.current_user = user_data
                    st.success(f"Welcome, {user_data['name']}!")
                    st.rerun()
                else:
                    st.error("Invalid credentials. Please try again.")
        
        with col2:
            if st.button("Forgot Password?", key="forgot_password"):
                st.info("Password reset feature coming soon!")
        
        st.markdown('</div>', unsafe_allow_html=True)

# Modern monitor console view
def monitor_console_view():
    st.markdown("""
        <div style='text-align: center; margin-bottom: 30px;'>
            <h1 style='color: var(--primary-color); margin-bottom: 10px;'>Monitor Console</h1>
            <p style='color: var(--secondary-color); font-size: 1.1em;'>Real-time patient monitoring dashboard</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Create tabs for each bed with modern styling
    bed_tabs = st.tabs([f"Bed {i+1} 🏥" for i in range(NUM_BEDS)])
    
    for i, tab in enumerate(bed_tabs):
        with tab:
            bed_id = i + 1
            if bed_id not in st.session_state.patient_data:
                st.session_state.patient_data[bed_id] = {
                    'vitals': {},
                    'alarms': [],
                    'last_sync': None,
                    'offline': False
                }
            
            patient = st.session_state.patient_data[bed_id]
            
            # Status bar
            col1, col2, col3 = st.columns(3)
            with col1:
                status = "🟢 Online" if not patient['offline'] else "🔴 Offline"
                st.markdown(f"**Status:** {status}")
            with col2:
                if patient['last_sync']:
                    st.markdown(f"**Last Sync:** {patient['last_sync']}")
            with col3:
                if st.button("🔄 Toggle Offline Mode", key=f"offline_{bed_id}"):
                    patient['offline'] = not patient['offline']
            
            # Generate vitals
            vitals = {}
            for vital, params in VITAL_SIGNS.items():
                value = random.uniform(params['min'], params['max'])
                if random.random() < 0.1:  # 10% chance of variation
                    value += random.uniform(-5, 5)
                vitals[vital] = round(value, 1)
            
            # Check alarms
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
            
            # Display vitals in modern cards
            cols = st.columns(5)
            for idx, (vital, value) in enumerate(vitals.items()):
                with cols[idx]:
                    st.markdown(f"""
                        <div class="metric-card">
                            <h3>{VITAL_SIGNS[vital]['icon']} {vital}</h3>
                            <h2 style='color: #00a8e8;'>{value} {VITAL_SIGNS[vital]['unit']}</h2>
                        </div>
                    """, unsafe_allow_html=True)
            
            # Display alarms
            if alarms:
                st.markdown("### 🚨 Active Alarms")
                for alarm in alarms:
                    alert_class = "alert-critical" if alarm['severity'] == 'critical' else "alert-warning"
                    st.markdown(f"""
                        <div class="{alert_class}">
                            <strong>{alarm['vital']}</strong>: {alarm['value']} ({alarm['severity']})
                        </div>
                    """, unsafe_allow_html=True)
            
            # Time series chart
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
            
            # Control panel
            st.markdown("### Control Panel")
            col1, col2, col3 = st.columns(3)
            with col1:
                if st.button("🔄 Sync Data", key=f"sync_{bed_id}"):
                    patient['last_sync'] = datetime.now().strftime('%H:%M:%S')
                    st.success(f"Last synced: {patient['last_sync']}")
            with col2:
                if st.button("📊 Export Data", key=f"export_{bed_id}"):
                    hl7_data = hl7_simulator.export_patient_data(str(bed_id))
                    st.download_button(
                        label="Download HL7",
                        data=hl7_data,
                        file_name=f"patient_{bed_id}_data.hl7",
                        mime="text/plain"
                    )
            with col3:
                if st.button("📝 Add Note", key=f"note_{bed_id}"):
                    st.text_area("Clinical Notes", key=f"notes_{bed_id}")

# Modern CNS view
def cns_view():
    st.markdown("""
        <div style='text-align: center; margin-bottom: 30px;'>
            <h1 style='color: var(--primary-color); margin-bottom: 10px;'>Central Nursing System</h1>
            <p style='color: var(--secondary-color); font-size: 1.1em;'>Multi-bed monitoring dashboard</p>
        </div>
    """, unsafe_allow_html=True)
    
    if not st.session_state.authenticated:
        st.warning("Please login to access the CNS")
        return
    
    # Filter panel
    st.markdown("### Filter Panel")
    col1, col2, col3 = st.columns(3)
    with col1:
        bed_filter = st.multiselect("Filter by Bed", [f"Bed {i+1}" for i in range(NUM_BEDS)])
    with col2:
        severity_filter = st.multiselect("Filter by Severity", ["critical", "warning", "normal"])
    with col3:
        status_filter = st.multiselect("Filter by Status", ["Online", "Offline"])
    
    # Patient overview
    st.markdown("### Patient Overview")
    patient_data = []
    for bed_id, patient in st.session_state.patient_data.items():
        vitals = patient.get('vitals', {})
        patient_data.append({
            'Bed ID': bed_id,
            'Status': 'Online' if not patient.get('offline', False) else 'Offline',
            'Heart Rate': vitals.get('Heart Rate', 0),
            'Blood Pressure': vitals.get('Blood Pressure', 0),
            'SpO2': vitals.get('SpO2', 0),
            'Respiration Rate': vitals.get('Respiration Rate', 0),
            'Temperature': vitals.get('Temperature', 0)
        })
    
    df = pd.DataFrame(patient_data)
    st.dataframe(
        df.style.background_gradient(cmap='Blues'),
        use_container_width=True
    )
    
    # Alarm panel
    st.markdown("### Alarm Panel")
    all_alarms = []
    for bed_id, patient in st.session_state.patient_data.items():
        alarms = patient.get('alarms', [])
        for alarm in alarms:
            alarm['bed_id'] = bed_id
            all_alarms.append(alarm)
    
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

# Admin panel
def admin_panel():
    if not st.session_state.authenticated or st.session_state.current_user['role'] != 'Admin':
        st.warning("Access denied. Admin privileges required.")
        return
    
    st.markdown("""
        <div style='text-align: center; margin-bottom: 30px;'>
            <h1 style='color: var(--primary-color); margin-bottom: 10px;'>Admin Panel</h1>
            <p style='color: var(--secondary-color); font-size: 1.1em;'>System administration and configuration</p>
        </div>
    """, unsafe_allow_html=True)
    
    # User management
    st.markdown("### User Management")
    tab1, tab2, tab3 = st.tabs(["Add User", "Edit User", "Delete User"])
    
    with tab1:
        with st.form("add_user_form"):
            new_username = st.text_input("Username")
            new_password = st.text_input("Password", type="password")
            new_role = st.selectbox("Role", ["Doctor", "Nurse", "Admin"])
            new_name = st.text_input("Full Name")
            new_email = st.text_input("Email")
            
            if st.form_submit_button("Add User"):
                if auth_handler.register_user(new_username, new_password, new_role, new_name, new_email):
                    st.success("User added successfully!")
                else:
                    st.error("Username already exists!")
    
    with tab2:
        users = list(auth_handler.users.keys())
        selected_user = st.selectbox("Select User", users)
        if selected_user:
            user_data = auth_handler.users[selected_user]
            with st.form("edit_user_form"):
                new_role = st.selectbox("Role", ["Doctor", "Nurse", "Admin"], 
                                      index=["Doctor", "Nurse", "Admin"].index(user_data["role"]))
                new_name = st.text_input("Full Name", value=user_data["name"])
                new_email = st.text_input("Email", value=user_data["email"])
                
                if st.form_submit_button("Update User"):
                    if auth_handler.update_user(selected_user, role=new_role, name=new_name, email=new_email):
                        st.success("User updated successfully!")
                    else:
                        st.error("Failed to update user!")
    
    with tab3:
        users = list(auth_handler.users.keys())
        user_to_delete = st.selectbox("Select User to Delete", users)
        if st.button("Delete User"):
            if auth_handler.delete_user(user_to_delete):
                st.success("User deleted successfully!")
            else:
                st.error("Failed to delete user!")
    
    # System logs
    st.markdown("### System Logs")
    logs = db_session.query(SystemLog).order_by(SystemLog.timestamp.desc()).limit(100).all()
    if logs:
        log_data = []
        for log in logs:
            log_data.append({
                'Timestamp': log.timestamp,
                'User': log.user,
                'Action': log.action,
                'Details': log.details
            })
        st.dataframe(pd.DataFrame(log_data), use_container_width=True)
    else:
        st.info("No system logs available")

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
            
            # Theme toggle
            if st.button("🌓 Toggle Theme"):
                st.session_state.theme = 'light' if st.session_state.theme == 'dark' else 'dark'
                st.rerun()
    
    if not st.session_state.authenticated:
        login_page()
    else:
        # Modern navigation menu
        selected = option_menu(
            menu_title=None,
            options=["Monitor Console", "Central Nursing System", "Admin Panel", "Logs"],
            icons=["monitor", "hospital", "gear", "list"],
            menu_icon="cast",
            default_index=0,
            orientation="horizontal",
        )
        
        if selected == "Monitor Console":
            monitor_console_view()
        elif selected == "Central Nursing System":
            cns_view()
        elif selected == "Admin Panel":
            admin_panel()
        elif selected == "Logs":
            st.title("System Logs")
            st.write("Log viewing features coming soon...")
        
        if st.sidebar.button("Logout"):
            st.session_state.authenticated = False
            st.session_state.current_user = None
            st.rerun()

if __name__ == "__main__":
    main() 
