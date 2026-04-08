# login_app.py - Complete ECG App with Login System
import streamlit as st
import numpy as np
import plotly.graph_objects as go
import os
import sys
from datetime import datetime
import users

# Add src to path
sys.path.append('src')

# ==================== PAGE CONFIG ====================
st.set_page_config(
    page_title="HeartGuardian | ECG Analysis System",
    page_icon="❤️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==================== SESSION STATE ====================
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'username' not in st.session_state:
    st.session_state.username = None
if 'user_data' not in st.session_state:
    st.session_state.user_data = None
if 'predictions' not in st.session_state:
    st.session_state.predictions = []

# ==================== CUSTOM CSS ====================
st.markdown("""
<style>
    /* Modern Font */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    * {
        font-family: 'Inter', sans-serif;
    }
    
    /* Login Container */
    .login-container {
        display: flex;
        justify-content: center;
        align-items: center;
        min-height: 80vh;
    }
    
    .login-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 30px;
        padding: 50px;
        color: white;
        box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        text-align: center;
        max-width: 450px;
        margin: auto;
    }
    
    /* Dashboard Cards */
    .stat-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 20px;
        padding: 25px;
        color: white;
        text-align: center;
        margin: 10px 0;
    }
    
    .welcome-card {
        background: linear-gradient(135deg, #00b09b, #96c93d);
        border-radius: 20px;
        padding: 30px;
        color: white;
        margin-bottom: 20px;
    }
    
    /* Result Cards */
    .result-normal {
        background: linear-gradient(135deg, #00b09b, #96c93d);
        border-radius: 20px;
        padding: 30px;
        text-align: center;
        color: white;
    }
    
    .result-abnormal {
        background: linear-gradient(135deg, #f093fb, #f5576c);
        border-radius: 20px;
        padding: 30px;
        text-align: center;
        color: white;
        animation: pulse 1.5s infinite;
    }
    
    @keyframes pulse {
        0%, 100% { transform: scale(1); }
        50% { transform: scale(1.02); }
    }
    
    /* Button Styling */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 50px;
        padding: 12px 30px;
        font-weight: 600;
        width: 100%;
        transition: all 0.3s;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 20px rgba(102,126,234,0.4);
    }
    
    /* Sidebar */
    .sidebar-user {
        text-align: center;
        padding: 20px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 15px;
        margin-bottom: 20px;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

# ==================== LOGIN PAGE ====================
def login_page():
    st.markdown('<div class="login-container">', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("""
        <div class="login-card">
            <div style="font-size: 4rem;">❤️</div>
            <h1 style="font-size: 2rem; margin: 20px 0;">HeartGuardian</h1>
            <p style="margin-bottom: 30px;">AI-Powered ECG Analysis System</p>
        </div>
        """, unsafe_allow_html=True)
        
        with st.form("login_form"):
            st.markdown("### 🔐 Login to Your Account")
            username = st.text_input("Username", placeholder="doctor or patient")
            password = st.text_input("Password", type="password", placeholder="doctor123 or patient123")
            
            col_a, col_b = st.columns(2)
            with col_a:
                submit = st.form_submit_button("Login", use_container_width=True)
            with col_b:
                if st.form_submit_button("Register", use_container_width=True):
                    st.session_state.show_register = True
            
            if submit:
                user = users.verify_user(username, password)
                if user:
                    st.session_state.logged_in = True
                    st.session_state.username = username
                    st.session_state.user_data = user
                    st.rerun()
                else:
                    st.error("❌ Invalid username or password")
        
        st.markdown("""
        <div style="text-align: center; margin-top: 20px; font-size: 0.8rem; color: #666;">
            <p>Demo Accounts:</p>
            <p>👨‍⚕️ Doctor: <strong>doctor</strong> / <strong>doctor123</strong></p>
            <p>👤 Patient: <strong>patient</strong> / <strong>patient123</strong></p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

# ==================== REGISTER PAGE ====================
def register_page():
    st.markdown('<div class="login-container">', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown('<div class="login-card">', unsafe_allow_html=True)
        st.markdown("### 📝 Create New Account")
        
        with st.form("register_form"):
            username = st.text_input("Username")
            name = st.text_input("Full Name")
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            confirm = st.text_input("Confirm Password", type="password")
            role = st.selectbox("Account Type", ["patient", "doctor"])
            
            if st.form_submit_button("Register", use_container_width=True):
                if password != confirm:
                    st.error("❌ Passwords do not match")
                elif len(password) < 6:
                    st.error("❌ Password must be at least 6 characters")
                else:
                    success, msg = users.register_user(username, password, name, email, role)
                    if success:
                        st.success("✅ Registration successful! Please login.")
                        st.session_state.show_register = False
                    else:
                        st.error(f"❌ {msg}")
        
        if st.button("← Back to Login", use_container_width=True):
            st.session_state.show_register = False
            st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

# ==================== DASHBOARD PAGE ====================
def dashboard_page():
    user = st.session_state.user_data
    role = user.get('role', 'patient')
    
    # Sidebar
    with st.sidebar:
        st.markdown(f"""
        <div class="sidebar-user">
            <div style="font-size: 3rem;">{'👨‍⚕️' if role == 'doctor' else '👤'}</div>
            <h3>{user.get('name', st.session_state.username)}</h3>
            <p style="margin: 0;">{role.upper()}</p>
            <p style="font-size: 0.8rem; margin-top: 10px;">{user.get('email', '')}</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Navigation
        page = st.radio(
            "Navigation",
            ["🏠 Dashboard", "🔬 ECG Analysis", "📊 History", "👤 Profile"],
            label_visibility="collapsed"
        )
        
        st.markdown("---")
        
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.username = None
            st.session_state.user_data = None
            st.rerun()
    
    # Welcome Banner
    st.markdown(f"""
    <div class="welcome-card">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <div>
                <h1>Welcome, {user.get('name', st.session_state.username)}! 👋</h1>
                <p>{datetime.now().strftime('%A, %B %d, %Y')}</p>
            </div>
            <div style="font-size: 3rem;">❤️</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Dashboard Content
    if page == "🏠 Dashboard":
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown("""
            <div class="stat-card">
                <div style="font-size: 2rem;">📊</div>
                <div style="font-size: 2rem; font-weight: bold;">97%</div>
                <div>Model Accuracy</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div class="stat-card">
                <div style="font-size: 2rem;">⚡</div>
                <div style="font-size: 2rem; font-weight: bold;">23ms</div>
                <div>Inference Time</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown("""
            <div class="stat-card">
                <div style="font-size: 2rem;">🎯</div>
                <div style="font-size: 2rem; font-weight: bold;">2.3MB</div>
                <div>Model Size</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            st.markdown("""
            <div class="stat-card">
                <div style="font-size: 2rem;">📈</div>
                <div style="font-size: 2rem; font-weight: bold;">187</div>
                <div>Input Samples</div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("---")
        st.markdown("### 🔬 Quick Actions")
        
        col_a, col_b, col_c = st.columns(3)
        with col_a:
            if st.button("🧪 Start New Analysis", use_container_width=True):
                st.session_state.page = "🔬 ECG Analysis"
                st.rerun()
        with col_b:
            st.button("📊 View Reports", use_container_width=True)
        with col_c:
            st.button("👨‍⚕️ Consult Doctor", use_container_width=True)
    
    elif page == "🔬 ECG Analysis":
        st.markdown("### 🔬 ECG Signal Analysis")
        
        col_left, col_right = st.columns([1, 1])
        
        with col_left:
            st.markdown("#### 📤 Input ECG Signal")
            
            if st.button("🎲 Generate Sample ECG", use_container_width=True):
                t = np.linspace(0, 1, 187)
                heartbeat = (
                    np.sin(2 * np.pi * 5 * t) * np.exp(-15 * (t - 0.5)**2) +
                    np.sin(2 * np.pi * 12 * t) * np.exp(-25 * (t - 0.55)**2)
                )
                heartbeat = heartbeat + np.random.randn(187) * 0.05
                st.session_state.heartbeat = heartbeat
                st.success("✅ Sample ECG Generated!")
            
            if 'heartbeat' in st.session_state:
                if st.button("🔍 Analyze Heartbeat", type="primary", use_container_width=True):
                    # Load model and predict
                    try:
                        from predict import ECGClassifier
                        classifier = ECGClassifier()
                        if classifier.model:
                            result, confidence = classifier.predict(st.session_state.heartbeat)
                            
                            if result['label'] == 'NORMAL':
                                st.markdown(f"""
                                <div class="result-normal">
                                    <div style="font-size: 3rem;">✅</div>
                                    <h1>NORMAL BEAT</h1>
                                    <div style="font-size: 2rem;">{confidence:.1%}</div>
                                    <p>Confidence Level</p>
                                    <p>🟢 Risk Level: LOW</p>
                                </div>
                                """, unsafe_allow_html=True)
                            else:
                                st.markdown(f"""
                                <div class="result-abnormal">
                                    <div style="font-size: 3rem;">⚠️</div>
                                    <h1>ABNORMAL BEAT</h1>
                                    <div style="font-size: 2rem;">{confidence:.1%}</div>
                                    <p>Confidence Level</p>
                                    <p>🔴 Risk Level: HIGH</p>
                                    <p>⚕️ Please consult a cardiologist</p>
                                </div>
                                """, unsafe_allow_html=True)
                            
                            # Save to history
                            st.session_state.predictions.append({
                                'date': datetime.now().strftime('%Y-%m-%d %H:%M'),
                                'result': result['label'],
                                'confidence': confidence
                            })
                    except:
                        st.error("❌ Model not loaded. Please train first with: python main.py")
        
        with col_right:
            st.markdown("#### 📈 ECG Visualization")
            if 'heartbeat' in st.session_state:
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    y=st.session_state.heartbeat,
                    mode='lines',
                    name='ECG Signal',
                    line=dict(color='#667eea', width=2)
                ))
                fig.update_layout(
                    height=400,
                    xaxis_title="Sample Number",
                    yaxis_title="Amplitude",
                    plot_bgcolor='white'
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("👈 Generate a sample ECG to begin")
    
    elif page == "📊 History":
        st.markdown("### 📊 Prediction History")
        
        if st.session_state.predictions:
            df = pd.DataFrame(st.session_state.predictions)
            st.dataframe(df, use_container_width=True)
            
            # Chart
            fig = px.bar(df, x='date', y='confidence', color='result',
                         title='Prediction History')
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No predictions yet. Go to ECG Analysis to make your first prediction!")
    
    elif page == "👤 Profile":
        st.markdown("### 👤 Profile Information")
        
        col_p1, col_p2 = st.columns(2)
        with col_p1:
            st.markdown("""
            <div class="dashboard-card">
                <h3>Personal Information</h3>
                <p><strong>Name:</strong> {}</p>
                <p><strong>Username:</strong> {}</p>
                <p><strong>Role:</strong> {}</p>
                <p><strong>Email:</strong> {}</p>
            </div>
            """.format(
                user.get('name', 'N/A'),
                st.session_state.username,
                role.upper(),
                user.get('email', 'N/A')
            ), unsafe_allow_html=True)
        
        with col_p2:
            st.markdown("""
            <div class="dashboard-card">
                <h3>Account Statistics</h3>
                <p><strong>Predictions Made:</strong> {}</p>
                <p><strong>Member Since:</strong> {}</p>
                <p><strong>Last Active:</strong> Today</p>
            </div>
            """.format(
                len(st.session_state.predictions),
                datetime.now().strftime('%B %Y')
            ), unsafe_allow_html=True)

# ==================== MAIN ====================
def main():
    if not st.session_state.logged_in:
        if 'show_register' in st.session_state and st.session_state.show_register:
            register_page()
        else:
            login_page()
    else:
        dashboard_page()

if __name__ == "__main__":
    main()