# app_advanced.py - ECG App with Multiple Graphs
import streamlit as st
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import os
import sys
import hashlib
import json
from datetime import datetime
from scipy import signal
from scipy.fft import fft, fftfreq

sys.path.append('src')

# ==================== PAGE SETUP ====================
st.set_page_config(
    page_title="ECG Heart Analyzer Pro",
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

def check_login(username, password):
    users = load_users()
    if username in users and users[username]["password"] == hash_pass(password):
        return users[username]
    return None

# ==================== SESSION ====================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user" not in st.session_state:
    st.session_state.user = None
if "username" not in st.session_state:
    st.session_state.username = None
if "history" not in st.session_state:
    st.session_state.history = []
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
        background: linear-gradient(135deg, #10b981, #34d399);
        padding: 20px;
        border-radius: 15px;
        text-align: center;
        color: white;
    }
    .result-abnormal {
        background: linear-gradient(135deg, #ef4444, #f97316);
        padding: 20px;
        border-radius: 15px;
        text-align: center;
        color: white;
        animation: pulse 2s infinite;
    }
    @keyframes pulse {
        0%, 100% { transform: scale(1); }
        50% { transform: scale(1.02); }
    }
    .sidebar-user {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 15px;
        text-align: center;
        color: white;
        margin-bottom: 20px;
    }
    .stButton button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 10px 20px;
        border-radius: 10px;
        font-weight: bold;
        width: 100%;
    }
    .metric-card {
        background: linear-gradient(135deg, #f8f9fa, #e9ecef);
        padding: 15px;
        border-radius: 10px;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# ==================== LOAD MODEL ====================
@st.cache_resource
def load_model():
    try:
        from predict import ECGClassifier
        return ECGClassifier()
    except:
        return None

# ==================== ECG ANALYSIS FUNCTIONS ====================
def calculate_heart_rate(ecg, fs=360):
    """Calculate heart rate from ECG signal"""
    peaks, _ = signal.find_peaks(ecg, height=np.std(ecg), distance=fs*0.4)
    if len(peaks) > 1:
        rr_intervals = np.diff(peaks) / fs
        heart_rate = 60 / np.mean(rr_intervals)
        return heart_rate, len(peaks)
    return 75, 0

def calculate_hrv(ecg, fs=360):
    """Calculate Heart Rate Variability"""
    peaks, _ = signal.find_peaks(ecg, height=np.std(ecg), distance=fs*0.4)
    if len(peaks) > 1:
        rr_intervals = np.diff(peaks) / fs
        return np.std(rr_intervals) * 1000
    return 50

def get_frequency_analysis(ecg, fs=360):
    """Get frequency domain analysis"""
    n = len(ecg)
    yf = fft(ecg)
    xf = fftfreq(n, 1/fs)[:n//2]
    magnitude = np.abs(yf[:n//2])
    
    # Get frequency bands
    lf_band = (0.04, 0.15)  # Low frequency
    hf_band = (0.15, 0.4)   # High frequency
    
    lf_power = np.sum(magnitude[(xf >= lf_band[0]) & (xf < lf_band[1])])
    hf_power = np.sum(magnitude[(xf >= hf_band[0]) & (xf < hf_band[1])])
    lf_hf_ratio = lf_power / (hf_power + 1e-8)
    
    return xf, magnitude, lf_hf_ratio

# ==================== LOGIN ====================
def show_login():
    st.markdown('<div class="main-header"><h1>❤️ ECG Heart Analyzer Pro</h1><p>Advanced AI-Powered Cardiac Health Monitoring</p></div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown('<div class="card">', unsafe_allow_html=True)
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
        
        st.info("Demo: doctor/doctor123  |  patient/patient123")
        st.markdown('</div>', unsafe_allow_html=True)

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
        
        if st.session_state.history:
            normal_count = sum(1 for h in st.session_state.history if h['result'] == 'NORMAL')
            abnormal_count = len(st.session_state.history) - normal_count
            st.metric("Normal Beats", normal_count)
            st.metric("Abnormal Beats", abnormal_count)
        
        st.markdown("---")
        st.markdown("### 📁 Upload ECG")
        uploaded = st.file_uploader("Choose CSV/TXT/NPY", type=['csv', 'txt', 'npy'])
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
                st.download_button("Download CSV", csv, "ecg_history.csv")
    
    # Main content
    st.markdown(f"""
    <div class="main-header">
        <h2>Welcome, {st.session_state.user['name']}! 👋</h2>
        <p>{datetime.now().strftime('%A, %B %d, %Y')}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Tabs
    tab1, tab2, tab3, tab4 = st.tabs(["🔬 ECG Analysis", "📊 Advanced Analytics", "📈 History", "👤 Profile"])
    
    # ==================== TAB 1: ECG ANALYSIS ====================
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
                            "confidence": f"{conf:.1%}",
                            "heart_rate": calculate_heart_rate(st.session_state.heartbeat)[0],
                            "hrv": calculate_hrv(st.session_state.heartbeat)
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
            st.subheader("📈 ECG Signal")
            
            if st.session_state.heartbeat is not None:
                ecg = st.session_state.heartbeat
                
                # Main ECG plot
                fig = go.Figure()
                fig.add_trace(go.Scatter(y=ecg, mode='lines', name='ECG', line=dict(color='#667eea', width=2)))
                fig.add_trace(go.Scatter(y=ecg, mode='markers', name='Samples', marker=dict(size=3, color='#764ba2')))
                fig.update_layout(height=350, title="Raw ECG Signal", xaxis_title="Sample", yaxis_title="Amplitude")
                st.plotly_chart(fig, use_container_width=True)
                
                # Statistics
                c1, c2, c3, c4 = st.columns(4)
                c1.metric("Max", f"{np.max(ecg):.3f}")
                c2.metric("Min", f"{np.min(ecg):.3f}")
                c3.metric("Mean", f"{np.mean(ecg):.3f}")
                c4.metric("Std", f"{np.std(ecg):.3f}")
            else:
                st.info("👈 Generate or upload an ECG")
            
            st.markdown('</div>', unsafe_allow_html=True)
    
    # ==================== TAB 2: ADVANCED ANALYTICS ====================
    with tab2:
        if st.session_state.heartbeat is not None:
            ecg = st.session_state.heartbeat
            fs = 360
            
            # Heart Rate and HRV
            hr, num_peaks = calculate_heart_rate(ecg, fs)
            hrv = calculate_hrv(ecg, fs)
            
            col_a, col_b, col_c = st.columns(3)
            with col_a:
                st.markdown(f"""
                <div class="metric-card">
                    <h3>❤️ Heart Rate</h3>
                    <h1 style="color:#667eea">{hr:.0f} BPM</h1>
                    <p>{'Normal' if 60 <= hr <= 100 else 'Abnormal'}</p>
                </div>
                """, unsafe_allow_html=True)
            with col_b:
                st.markdown(f"""
                <div class="metric-card">
                    <h3>📊 HRV</h3>
                    <h1 style="color:#667eea">{hrv:.0f} ms</h1>
                    <p>Heart Rate Variability</p>
                </div>
                """, unsafe_allow_html=True)
            with col_c:
                st.markdown(f"""
                <div class="metric-card">
                    <h3>⚡ R-Peaks</h3>
                    <h1 style="color:#667eea">{num_peaks}</h1>
                    <p>Detected in signal</p>
                </div>
                """, unsafe_allow_html=True)
            
            # Frequency Analysis
            st.markdown("---")
            st.subheader("🌊 Frequency Domain Analysis")
            
            xf, magnitude, lf_hf_ratio = get_frequency_analysis(ecg, fs)
            
            fig_freq = go.Figure()
            fig_freq.add_trace(go.Scatter(x=xf[1:50], y=magnitude[1:50], mode='lines', name='Power Spectrum', line=dict(color='#ef4444', width=2)))
            fig_freq.update_layout(title="Frequency Spectrum (0-20 Hz)", xaxis_title="Frequency (Hz)", yaxis_title="Magnitude", height=300)
            st.plotly_chart(fig_freq, use_container_width=True)
            
            # LF/HF Ratio
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #667eea20, #764ba220); padding: 15px; border-radius: 10px; margin-top: 10px;">
                <h4>Autonomic Nervous System Balance</h4>
                <p><strong>LF/HF Ratio:</strong> {lf_hf_ratio:.2f}</p>
                <p>{'Sympathetic dominance' if lf_hf_ratio > 1.5 else 'Balanced' if lf_hf_ratio > 0.8 else 'Parasympathetic dominance'}</p>
            </div>
            """, unsafe_allow_html=True)
            
            # R-R Intervals
            peaks, _ = signal.find_peaks(ecg, height=np.std(ecg), distance=fs*0.4)
            if len(peaks) > 1:
                rr_intervals = np.diff(peaks) / fs * 1000
                fig_rr = go.Figure()
                fig_rr.add_trace(go.Scatter(y=rr_intervals, mode='lines+markers', name='RR Intervals', line=dict(color='#10b981', width=2)))
                fig_rr.update_layout(title="R-R Intervals", xaxis_title="Beat Number", yaxis_title="Interval (ms)", height=250)
                st.plotly_chart(fig_rr, use_container_width=True)
        else:
            st.info("No ECG data. Please analyze a heartbeat first!")
    
    # ==================== TAB 3: HISTORY ====================
    with tab3:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("📊 Test History")
        
        if st.session_state.history:
            df = pd.DataFrame(st.session_state.history)
            
            # Summary metrics
            col_h1, col_h2, col_h3 = st.columns(3)
            with col_h1:
                st.metric("Total Tests", len(df))
            with col_h2:
                normal_count = len(df[df['result'] == 'NORMAL'])
                st.metric("Normal", normal_count)
            with col_h3:
                abnormal_count = len(df[df['result'] == 'ABNORMAL'])
                st.metric("Abnormal", abnormal_count)
            
            # History table
            st.dataframe(df, use_container_width=True)
            
            # Confidence trend
            df_display = df.copy()
            df_display['confidence_val'] = df_display['confidence'].str.rstrip('%').astype(float)
            
            fig_trend = px.line(df_display, x='date', y='confidence_val', color='result', title='Confidence Trend')
            st.plotly_chart(fig_trend, use_container_width=True)
            
            # Result distribution
            fig_pie = px.pie(df, names='result', title='Result Distribution', color='result', color_discrete_map={'NORMAL': '#10b981', 'ABNORMAL': '#ef4444'})
            st.plotly_chart(fig_pie, use_container_width=True)
        else:
            st.info("No tests yet. Analyze an ECG first!")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # ==================== TAB 4: PROFILE ====================
    with tab4:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("👤 Profile")
        
        c1, c2 = st.columns(2)
        with c1:
            st.write(f"**Name:** {st.session_state.user['name']}")
            st.write(f"**Username:** {st.session_state.username}")
            st.write(f"**Role:** {st.session_state.user['role'].upper()}")
        with c2:
            st.write(f"**Tests Done:** {len(st.session_state.history)}")
            if st.session_state.history:
                normal = sum(1 for h in st.session_state.history if h['result'] == 'NORMAL')
                st.write(f"**Normal Rate:** {normal/len(st.session_state.history)*100:.1f}%")
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