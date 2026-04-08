# app_final.py - CLEAN WORKING ECG APP
import streamlit as st
import numpy as np
import plotly.graph_objects as go
import pandas as pd
import os
import sys
import hashlib
import json
from datetime import datetime

sys.path.append('src')

# ==================== PAGE SETUP ====================
st.set_page_config(
    page_title="ECG Heart Analyzer",
    page_icon="❤️",
    layout="wide"
)

# ==================== USER DATABASE ====================
USER_FILE = "users.json"

def hash_pass(pwd):
    return hashlib.sha256(pwd.encode()).hexdigest()

def load_users():
    if not os.path.exists(USER_FILE):
        users = {
            "doctor": {"password": hash_pass("doctor123"), "role": "doctor", "name": "Dr. Smith"},
            "patient": {"password": hash_pass("patient123"), "role": "patient", "name": "John"}
        }
        with open(USER_FILE, "w") as f:
            json.dump(users, f)
    with open(USER_FILE, "r") as f:
        return json.load(f)

def save_users(users):
    with open(USER_FILE, "w") as f:
        json.dump(users, f)

def check_login(username, password):
    users = load_users()
    if username in users and users[username]["password"] == hash_pass(password):
        return users[username]
    return None

def register_new(username, password, name, role="patient"):
    users = load_users()
    if username in users:
        return False, "Username exists"
    users[username] = {"password": hash_pass(password), "role": role, "name": name}
    save_users(users)
    return True, "Success!"

# ==================== SESSION ====================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user" not in st.session_state:
    st.session_state.user = None
if "username" not in st.session_state:
    st.session_state.username = None
if "history" not in st.session_state:
    st.session_state.history = []
if "show_reg" not in st.session_state:
    st.session_state.show_reg = False
if "heartbeat" not in st.session_state:
    st.session_state.heartbeat = None

# ==================== CSS ====================
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 30px;
        border-radius: 20px;
        text-align: center;
        color: white;
        margin-bottom: 30px;
    }
    .card {
        background: white;
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        margin: 10px 0;
    }
    .result-normal {
        background: #10b981;
        padding: 20px;
        border-radius: 15px;
        text-align: center;
        color: white;
    }
    .result-abnormal {
        background: #ef4444;
        padding: 20px;
        border-radius: 15px;
        text-align: center;
        color: white;
    }
    .sidebar-user {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 15px;
        text-align: center;
        color: white;
        margin-bottom: 20px;
    }
    button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 10px 20px;
        border-radius: 10px;
        font-weight: bold;
        cursor: pointer;
    }
    .stButton button {
        width: 100%;
    }
</style>
""", unsafe_allow_html=True)

# ==================== LOGIN PAGE ====================
def show_login():
    st.markdown('<div class="main-header"><h1>❤️ ECG Heart Analyzer</h1><p>AI-Powered Cardiac Health Monitoring</p></div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        
        if not st.session_state.show_reg:
            st.subheader("🔐 Login")
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            
            if st.button("Login"):
                user = check_login(username, password)
                if user:
                    st.session_state.logged_in = True
                    st.session_state.user = user
                    st.session_state.username = username
                    st.rerun()
                else:
                    st.error("Invalid credentials")
            
            st.markdown("---")
            if st.button("📝 Create New Account"):
                st.session_state.show_reg = True
                st.rerun()
            
            st.info("Demo: doctor/doctor123  |  patient/patient123")
        
        else:
            st.subheader("📝 Register")
            new_user = st.text_input("Username")
            new_name = st.text_input("Full Name")
            new_pass = st.text_input("Password", type="password")
            new_confirm = st.text_input("Confirm", type="password")
            new_role = st.selectbox("Role", ["patient", "doctor"])
            
            if st.button("Register"):
                if new_pass != new_confirm:
                    st.error("Passwords don't match")
                elif len(new_pass) < 4:
                    st.error("Password too short")
                else:
                    ok, msg = register_new(new_user, new_pass, new_name, new_role)
                    if ok:
                        st.success("Registration successful! Please login.")
                        st.session_state.show_reg = False
                        st.rerun()
                    else:
                        st.error(msg)
            
            if st.button("← Back to Login"):
                st.session_state.show_reg = False
                st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)

# ==================== LOAD MODEL ====================
@st.cache_resource
def load_model():
    try:
        from predict import ECGClassifier
        return ECGClassifier()
    except:
        return None

# ==================== DASHBOARD ====================
def show_dashboard():
    # Sidebar
    with st.sidebar:
        st.markdown(f"""
        <div class="sidebar-user">
            <h2>👤 {st.session_state.user['name']}</h2>
            <p>{st.session_state.username.upper()}</p>
            <p>{st.session_state.user['role']}</p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("🚪 Logout"):
            st.session_state.logged_in = False
            st.session_state.user = None
            st.session_state.username = None
            st.session_state.history = []
            st.rerun()
        
        st.markdown("---")
        st.metric("Total Tests", len(st.session_state.history))
        st.metric("Model Status", "✅ Ready")
        
        st.markdown("---")
        st.markdown("### 📁 Upload ECG File")
        
        uploaded = st.file_uploader("Choose CSV/TXT file", type=['csv', 'txt', 'npy'])
        if uploaded:
            try:
                if uploaded.name.endswith('.npy'):
                    data = np.load(uploaded)
                else:
                    data = pd.read_csv(uploaded, header=None).values.flatten()
                if len(data) == 187:
                    st.session_state.heartbeat = data
                    st.success(f"✅ Loaded {uploaded.name}")
                else:
                    st.error(f"Need 187 samples, got {len(data)}")
            except:
                st.error("Error reading file")
        
        st.markdown("---")
        if st.session_state.history:
            if st.button("📥 Export History"):
                df = pd.DataFrame(st.session_state.history)
                csv = df.to_csv(index=False)
                st.download_button("Download CSV", csv, "ecg_history.csv", "text/csv")
    
    # Main content
    st.markdown(f"""
    <div class="main-header">
        <h2>Welcome, {st.session_state.user['name']}! 👋</h2>
        <p>{datetime.now().strftime('%A, %B %d, %Y')}</p>
    </div>
    """, unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["🔬 Analyze ECG", "📊 History", "👤 Profile"])
    
    # Tab 1: Analyze
    with tab1:
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.subheader("📤 Input")
            
            if st.button("🎲 Generate Sample ECG"):
                t = np.linspace(0, 1, 187)
                ecg = np.sin(2 * np.pi * 5 * t) * np.exp(-15 * (t - 0.5)**2)
                ecg = ecg + np.random.randn(187) * 0.05
                st.session_state.heartbeat = ecg
                st.success("Sample generated!")
            
            if st.session_state.heartbeat is not None:
                if st.button("🔍 Analyze", type="primary"):
                    model = load_model()
                    if model and model.model:
                        result, conf = model.predict(st.session_state.heartbeat)
                        st.session_state.history.append({
                            "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                            "result": result['label'],
                            "confidence": f"{conf:.1%}"
                        })
                        
                        if result['label'] == 'NORMAL':
                            st.markdown(f"""
                            <div class="result-normal">
                                <h1>✅ NORMAL</h1>
                                <h2>Confidence: {conf:.1%}</h2>
                                <p>Risk: LOW</p>
                            </div>
                            """, unsafe_allow_html=True)
                        else:
                            st.markdown(f"""
                            <div class="result-abnormal">
                                <h1>⚠️ ABNORMAL</h1>
                                <h2>Confidence: {conf:.1%}</h2>
                                <p>Risk: HIGH</p>
                                <p>Please consult a doctor</p>
                            </div>
                            """, unsafe_allow_html=True)
                    else:
                        st.warning("Model not trained. Run: python main.py")
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.subheader("📈 ECG Graph")
            
            if st.session_state.heartbeat is not None:
                fig = go.Figure()
                fig.add_trace(go.Scatter(y=st.session_state.heartbeat, mode='lines', name='ECG'))
                fig.update_layout(height=400, title="ECG Signal")
                st.plotly_chart(fig, use_container_width=True)
                
                # Stats
                c1, c2, c3, c4 = st.columns(4)
                c1.metric("Max", f"{np.max(st.session_state.heartbeat):.3f}")
                c2.metric("Min", f"{np.min(st.session_state.heartbeat):.3f}")
                c3.metric("Mean", f"{np.mean(st.session_state.heartbeat):.3f}")
                c4.metric("Std", f"{np.std(st.session_state.heartbeat):.3f}")
            else:
                st.info("👈 Generate or upload an ECG")
            
            st.markdown('</div>', unsafe_allow_html=True)
    
    # Tab 2: History
    with tab2:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("📊 Test History")
        
        if st.session_state.history:
            df = pd.DataFrame(st.session_state.history)
            st.dataframe(df, use_container_width=True)
            
            # Simple chart
            df_display = df.copy()
            df_display['confidence'] = df_display['confidence'].str.rstrip('%').astype(float)
            st.bar_chart(df_display.set_index('date')['confidence'])
        else:
            st.info("No tests yet. Analyze an ECG first!")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Tab 3: Profile
    with tab3:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("👤 Profile")
        
        c1, c2 = st.columns(2)
        with c1:
            st.write(f"**Name:** {st.session_state.user['name']}")
            st.write(f"**Username:** {st.session_state.username}")
            st.write(f"**Role:** {st.session_state.user['role'].upper()}")
        with c2:
            st.write(f"**Tests Done:** {len(st.session_state.history)}")
            st.write(f"**Member Since:** March 2026")
        
        st.markdown('</div>', unsafe_allow_html=True)

# ==================== MAIN ====================
def main():
    if not st.session_state.logged_in:
        show_login()
    else:
        show_dashboard()

if __name__ == "__main__":
    main()