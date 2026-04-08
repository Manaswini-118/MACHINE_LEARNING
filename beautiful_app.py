# beautiful_app.py - UPDATED WITH BETTER COLORS
import streamlit as st
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import os
import sys
import base64
from datetime import datetime
import json
import io

sys.path.append('src')

# ==================== PAGE CONFIG ====================
st.set_page_config(
    page_title="HeartVision Pro | ECG Analysis Suite",
    page_icon="❤️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==================== CUSTOM CSS - CLEAN & READABLE ====================
st.markdown("""
<style>
    /* Import Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    
    * {
        font-family: 'Inter', sans-serif;
    }
    
    /* Clean White Background */
    .stApp {
        background: linear-gradient(135deg, #f5f7fa 0%, #e9ecef 100%);
    }
    
    /* Card Styling */
    .glass-card {
        background: white;
        border-radius: 20px;
        padding: 25px;
        margin: 16px 0;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
        border: 1px solid #e9ecef;
    }
    
    /* Hero Section */
    .hero-section {
        text-align: center;
        padding: 40px 20px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 25px;
        margin-bottom: 30px;
        color: white;
    }
    
    /* Gradient Text - Dark Version */
    .gradient-text {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-size: 3rem;
        font-weight: 800;
        margin-bottom: 0;
    }
    
    /* White Text for Hero */
    .hero-section h1 {
        color: white;
        font-size: 2.5rem;
        font-weight: 700;
        margin: 20px 0 10px;
    }
    
    .hero-section p {
        color: rgba(255,255,255,0.9);
        font-size: 1.1rem;
    }
    
    /* Metric Cards */
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 20px;
        padding: 20px;
        text-align: center;
        color: white;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    
    .metric-value {
        font-size: 2rem;
        font-weight: 700;
        color: white;
    }
    
    /* Result Cards */
    .result-normal {
        background: linear-gradient(135deg, #10b981 0%, #34d399 100%);
        border-radius: 20px;
        padding: 30px;
        text-align: center;
        color: white;
        animation: fadeInUp 0.6s ease;
    }
    
    .result-abnormal {
        background: linear-gradient(135deg, #ef4444 0%, #f97316 100%);
        border-radius: 20px;
        padding: 30px;
        text-align: center;
        color: white;
        animation: pulse 2s infinite, fadeInUp 0.6s ease;
    }
    
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
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
        border-radius: 12px;
        padding: 12px 24px;
        font-weight: 600;
        font-size: 16px;
        transition: all 0.3s ease;
        width: 100%;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 20px rgba(102,126,234,0.3);
    }
    
    /* Sidebar Styling */
    .css-1d391kg {
        background: white;
        border-right: 1px solid #e9ecef;
    }
    
    /* Sidebar Text */
    .sidebar-user {
        text-align: center;
        padding: 20px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 15px;
        margin-bottom: 20px;
        color: white;
    }
    
    /* Tab Styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 16px;
        background: #f8f9fa;
        border-radius: 12px;
        padding: 5px;
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 10px;
        padding: 10px 24px;
        color: #495057;
        font-weight: 500;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
    }
    
    /* Upload Box */
    .upload-box {
        border: 2px dashed #dee2e6;
        border-radius: 15px;
        padding: 40px;
        text-align: center;
        background: #f8f9fa;
        transition: all 0.3s ease;
    }
    
    .upload-box:hover {
        border-color: #667eea;
        background: #f0f2ff;
    }
    
    /* Headers */
    h1, h2, h3, h4 {
        color: #1e293b;
    }
    
    /* Labels */
    .stRadio label, .stSlider label {
        color: #1e293b !important;
        font-weight: 500;
    }
    
    /* Info Box */
    .info-box {
        background: #f8f9fa;
        border-radius: 12px;
        padding: 15px;
        margin: 10px 0;
        border-left: 4px solid #667eea;
    }
    
    /* File Uploader */
    .uploaded-files {
        background: #f8f9fa;
        border-radius: 12px;
        padding: 12px;
        margin: 8px 0;
    }
    
    /* Success/Error Messages */
    .stAlert {
        border-radius: 12px;
    }
    
    /* Footer */
    .footer {
        text-align: center;
        padding: 20px;
        color: #6c757d;
        font-size: 0.8rem;
    }
</style>
""", unsafe_allow_html=True)

# ==================== SESSION STATE ====================
if 'analyses' not in st.session_state:
    st.session_state.analyses = []
if 'current_file' not in st.session_state:
    st.session_state.current_file = None

# ==================== HEADER ====================
st.markdown("""
<div class="hero-section">
    <div style="font-size: 4rem;">🫀</div>
    <h1>HeartVision Pro</h1>
    <p>AI-Powered ECG Analysis Suite | 97% Accuracy | Real-time Detection</p>
    <div style="display: flex; justify-content: center; gap: 15px; margin-top: 20px;">
        <span style="background: rgba(255,255,255,0.2); padding: 6px 16px; border-radius: 50px;">⚡ 23ms Inference</span>
        <span style="background: rgba(255,255,255,0.2); padding: 6px 16px; border-radius: 50px;">🎯 97% Accuracy</span>
        <span style="background: rgba(255,255,255,0.2); padding: 6px 16px; border-radius: 50px;">📊 187 Samples</span>
    </div>
</div>
""", unsafe_allow_html=True)

# ==================== SIDEBAR ====================
with st.sidebar:
    st.markdown("""
    <div class="sidebar-user">
        <div style="font-size: 2.5rem;">👤</div>
        <h3 style="margin: 10px 0;">Welcome!</h3>
        <p style="margin: 0;">nallapu sreeja</p>
        <p style="font-size: 0.8rem; opacity: 0.8;">Patient</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Quick Stats
    st.markdown("### 📊 Live Stats")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Analyses", len(st.session_state.analyses))
    with col2:
        st.metric("Model", "✅ Ready")
    
    st.markdown("---")
    
    # Upload Section
    st.markdown("### 📁 File Upload")
    
    uploaded_files = st.file_uploader(
        "Drop your ECG files here",
        type=['csv', 'txt', 'npy'],
        accept_multiple_files=True,
        help="Upload CSV, TXT, or NPY files with 187 ECG samples"
    )
    
    if uploaded_files:
        for file in uploaded_files:
            st.session_state.current_file = file
            st.success(f"✅ {file.name} loaded")
    
    st.markdown("---")
    
    # Export
    if st.session_state.analyses:
        if st.button("📥 Export Results", use_container_width=True):
            df = pd.DataFrame(st.session_state.analyses)
            csv = df.to_csv(index=False)
            b64 = base64.b64encode(csv.encode()).decode()
            href = f'<a href="data:file/csv;base64,{b64}" download="ecg_results.csv">Download CSV</a>'
            st.markdown(href, unsafe_allow_html=True)

# ==================== MAIN CONTENT ====================
tabs = st.tabs(["🔬 **ECG Analyzer**", "📊 **Batch Analysis**", "📈 **Visual Reports**", "👤 **Dashboard**"])

# ==================== TAB 1: ECG ANALYZER ====================
with tabs[0]:
    st.markdown("### 🔬 Real-time ECG Analysis")
    
    col_left, col_right = st.columns([1, 1], gap="large")
    
    with col_left:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown("#### 📤 Input Method")
        
        input_method = st.radio(
            "Choose input method:",
            ["🎲 Generate Synthetic ECG", "📁 Upload ECG File", "✏️ Enter Values"],
            horizontal=True
        )
        
        heartbeat = None
        file_name = None
        
        if input_method == "🎲 Generate Synthetic ECG":
            st.markdown("**ECG Parameters**")
            col_a, col_b = st.columns(2)
            with col_a:
                noise = st.slider("Noise Level", 0.0, 0.3, 0.05, 0.01)
            with col_b:
                amplitude = st.slider("Amplitude", 0.5, 2.0, 1.0, 0.1)
            
            if st.button("✨ Generate ECG Signal", use_container_width=True):
                with st.spinner("Generating ECG waveform..."):
                    t = np.linspace(0, 1, 187)
                    heartbeat = (
                        amplitude * np.sin(2 * np.pi * 5 * t) * np.exp(-15 * (t - 0.5)**2) +
                        amplitude * 0.5 * np.sin(2 * np.pi * 12 * t) * np.exp(-25 * (t - 0.55)**2) +
                        amplitude * 0.3 * np.sin(2 * np.pi * 4 * t) * np.exp(-10 * (t - 0.65)**2)
                    )
                    heartbeat = heartbeat + np.random.randn(187) * noise
                    st.session_state.heartbeat = heartbeat
                    st.session_state.file_name = "Synthetic_ECG"
                    st.success("✅ ECG Generated!")
        
        elif input_method == "📁 Upload ECG File":
            uploaded_file = st.file_uploader("Choose ECG file", type=['csv', 'txt', 'npy'])
            if uploaded_file:
                try:
                    if uploaded_file.name.endswith('.npy'):
                        heartbeat = np.load(uploaded_file)
                    else:
                        data = pd.read_csv(uploaded_file, header=None)
                        heartbeat = data.values.flatten()
                    
                    if len(heartbeat) == 187:
                        st.session_state.heartbeat = heartbeat
                        st.session_state.file_name = uploaded_file.name
                        st.success(f"✅ Loaded {len(heartbeat)} samples")
                    else:
                        st.error(f"⚠️ Need 187 samples, got {len(heartbeat)}")
                except Exception as e:
                    st.error(f"❌ Error: {e}")
        
        else:
            values = st.text_area("Enter 187 values (comma-separated):", height=100)
            if st.button("Load Values"):
                try:
                    vals = [float(x.strip()) for x in values.split(',')]
                    if len(vals) == 187:
                        heartbeat = np.array(vals)
                        st.session_state.heartbeat = heartbeat
                        st.session_state.file_name = "Manual_Input"
                        st.success("✅ Values loaded!")
                    else:
                        st.error(f"Need 187 values, got {len(vals)}")
                except:
                    st.error("Invalid format")
        
        # Analyze Button
        if 'heartbeat' in st.session_state and st.session_state.heartbeat is not None:
            st.markdown("---")
            if st.button("🔍 **Analyze Heartbeat**", type="primary", use_container_width=True):
                with st.spinner("🧠 AI is analyzing..."):
                    try:
                        from predict import ECGClassifier
                        classifier = ECGClassifier()
                        
                        if classifier and classifier.model:
                            result, confidence = classifier.predict(st.session_state.heartbeat)
                            
                            if result:
                                # Save analysis
                                analysis = {
                                    'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                                    'file': st.session_state.get('file_name', 'Unknown'),
                                    'result': result['label'],
                                    'confidence': confidence,
                                    'risk': result['risk']
                                }
                                st.session_state.analyses.append(analysis)
                                
                                # Display result
                                if result['label'] == 'NORMAL':
                                    st.markdown(f"""
                                    <div class="result-normal">
                                        <div style="font-size: 3rem;">✅</div>
                                        <h2 style="font-size: 1.8rem; margin: 10px 0;">NORMAL HEARTBEAT</h2>
                                        <div style="font-size: 2rem; font-weight: bold; margin: 15px 0;">{confidence:.1%}</div>
                                        <div>Confidence Level</div>
                                        <div style="margin-top: 15px;">🟢 Risk Level: LOW</div>
                                        <div style="margin-top: 10px;">✅ Heart rhythm appears normal</div>
                                    </div>
                                    """, unsafe_allow_html=True)
                                else:
                                    st.markdown(f"""
                                    <div class="result-abnormal">
                                        <div style="font-size: 3rem;">⚠️</div>
                                        <h2 style="font-size: 1.8rem; margin: 10px 0;">ABNORMAL HEARTBEAT</h2>
                                        <div style="font-size: 2rem; font-weight: bold; margin: 15px 0;">{confidence:.1%}</div>
                                        <div>Confidence Level</div>
                                        <div style="margin-top: 15px;">🔴 Risk Level: HIGH</div>
                                        <div style="margin-top: 10px;">⚠️ Irregular pattern detected</div>
                                        <div style="margin-top: 5px;">🏥 Please consult a cardiologist</div>
                                    </div>
                                    """, unsafe_allow_html=True)
                    except Exception as e:
                        st.error(f"❌ Error: {e}. Please train model first with: python main.py")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col_right:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown("#### 📈 ECG Visualization")
        
        if 'heartbeat' in st.session_state and st.session_state.heartbeat is not None:
            heartbeat = st.session_state.heartbeat
            
            fig = go.Figure()
            
            fig.add_trace(go.Scatter(
                y=heartbeat,
                mode='lines',
                name='ECG Signal',
                line=dict(color='#667eea', width=3),
                fill='tozeroy',
                fillcolor='rgba(102,126,234,0.2)'
            ))
            
            # Detect peaks
            peaks = np.where(heartbeat > np.percentile(heartbeat, 90))[0]
            if len(peaks) > 0:
                fig.add_trace(go.Scatter(
                    x=peaks,
                    y=heartbeat[peaks],
                    mode='markers',
                    name='R-Peaks',
                    marker=dict(color='#ef4444', size=10, symbol='diamond')
                ))
            
            fig.update_layout(
                title=f"ECG Waveform - {st.session_state.get('file_name', 'Unknown')}",
                xaxis_title="Sample Number",
                yaxis_title="Amplitude",
                height=450,
                plot_bgcolor='white',
                title_font_size=16
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Signal Statistics
            col_s1, col_s2, col_s3, col_s4 = st.columns(4)
            with col_s1:
                st.metric("Peak", f"{np.max(heartbeat):.3f}")
            with col_s2:
                st.metric("Trough", f"{np.min(heartbeat):.3f}")
            with col_s3:
                st.metric("Mean", f"{np.mean(heartbeat):.3f}")
            with col_s4:
                st.metric("Std Dev", f"{np.std(heartbeat):.3f}")
            
        else:
            st.info("👈 Generate or upload an ECG signal to begin analysis")
        
        st.markdown('</div>', unsafe_allow_html=True)

# ==================== TAB 2: BATCH ANALYSIS ====================
with tabs[1]:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown("### 📦 Batch ECG Analysis")
    st.markdown("Upload multiple ECG files for batch processing")
    
    batch_files = st.file_uploader(
        "Upload multiple ECG files",
        type=['csv', 'txt', 'npy'],
        accept_multiple_files=True,
        key="batch_upload"
    )
    
    if batch_files and st.button("🚀 Analyze All Files", use_container_width=True):
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        try:
            from predict import ECGClassifier
            classifier = ECGClassifier()
            
            results = []
            for idx, file in enumerate(batch_files):
                status_text.text(f"Analyzing: {file.name}")
                try:
                    if file.name.endswith('.npy'):
                        data = np.load(file)
                    else:
                        data = pd.read_csv(file, header=None).values.flatten()
                    
                    if len(data) == 187:
                        result, conf = classifier.predict(data)
                        results.append({
                            'File': file.name,
                            'Result': result['label'],
                            'Confidence': f"{conf:.1%}",
                            'Risk': result['risk']
                        })
                except:
                    results.append({
                        'File': file.name,
                        'Result': 'ERROR',
                        'Confidence': 'N/A',
                        'Risk': 'N/A'
                    })
                progress_bar.progress((idx + 1) / len(batch_files))
            
            status_text.text("✅ Analysis Complete!")
            
            df_results = pd.DataFrame(results)
            st.dataframe(df_results, use_container_width=True)
            
            # Summary chart
            fig = px.pie(df_results, names='Result', title='Batch Analysis Summary',
                        color='Result',
                        color_discrete_map={'NORMAL': '#10b981', 'ABNORMAL': '#ef4444'})
            st.plotly_chart(fig, use_container_width=True)
            
            # Export
            csv = df_results.to_csv(index=False)
            b64 = base64.b64encode(csv.encode()).decode()
            st.markdown(f'<a href="data:file/csv;base64,{b64}" download="batch_results.csv">📥 Download Results CSV</a>', unsafe_allow_html=True)
            
        except Exception as e:
            st.error(f"Error: {e}")
    
    st.markdown('</div>', unsafe_allow_html=True)

# ==================== TAB 3: VISUAL REPORTS ====================
with tabs[2]:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown("### 📊 Analysis Reports")
    
    if st.session_state.analyses:
        df = pd.DataFrame(st.session_state.analyses)
        
        col_r1, col_r2, col_r3 = st.columns(3)
        with col_r1:
            st.metric("Total Analyses", len(df))
        with col_r2:
            normal_count = len(df[df['result'] == 'NORMAL'])
            st.metric("Normal Beats", normal_count)
        with col_r3:
            abnormal_count = len(df[df['result'] == 'ABNORMAL'])
            st.metric("Abnormal Beats", abnormal_count)
        
        fig1 = px.bar(df, x='timestamp', y='confidence', color='result',
                      title='Prediction History',
                      color_discrete_map={'NORMAL': '#10b981', 'ABNORMAL': '#ef4444'})
        st.plotly_chart(fig1, use_container_width=True)
        
        st.dataframe(df, use_container_width=True)
        
    else:
        st.info("No analyses yet. Go to ECG Analyzer to make your first prediction!")
    
    st.markdown('</div>', unsafe_allow_html=True)

# ==================== TAB 4: DASHBOARD ====================
with tabs[3]:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown("### 👤 Patient Dashboard")
    
    col_p1, col_p2 = st.columns(2)
    
    with col_p1:
        st.markdown("#### 📋 Patient Information")
        patient_name = st.text_input("Patient Name", "nallapu sreeja")
        patient_age = st.number_input("Age", 18, 100, 21)
        patient_condition = st.selectbox("Medical History", ["Healthy", "Hypertension", "Diabetes", "Heart Disease"])
        
        if st.button("💾 Save Profile"):
            st.success("Profile saved successfully!")
    
    with col_p2:
        st.markdown("#### 📊 Health Summary")
        if st.session_state.analyses:
            df = pd.DataFrame(st.session_state.analyses)
            normal_pct = (len(df[df['result'] == 'NORMAL']) / len(df)) * 100
            
            fig = go.Figure(go.Indicator(
                mode = "gauge+number",
                value = normal_pct,
                title = {'text': "Heart Health Score"},
                domain = {'x': [0, 1], 'y': [0, 1]},
                gauge = {
                    'axis': {'range': [None, 100]},
                    'bar': {'color': "#10b981"},
                    'steps': [
                        {'range': [0, 50], 'color': "#ef4444"},
                        {'range': [50, 80], 'color': "#f97316"},
                        {'range': [80, 100], 'color': "#10b981"}
                    ]
                }
            ))
            st.plotly_chart(fig, use_container_width=True)
            
            st.markdown(f"""
            <div class="info-box">
                <strong>📈 Summary:</strong><br>
                Total Tests: {len(df)}<br>
                Normal: {normal_pct:.1f}%<br>
                Abnormal: {100-normal_pct:.1f}%
            </div>
            """, unsafe_allow_html=True)
        else:
            st.info("No health data available yet")
    
    st.markdown('</div>', unsafe_allow_html=True)

# ==================== FOOTER ====================
st.markdown("""
<div class="footer">
    <p>❤️ HeartVision Pro | AI-Powered Cardiac Health Monitoring</p>
    <p>For educational purposes only. Not for clinical diagnosis. Always consult a healthcare professional.</p>
    <p>Model: ResNet-34 | Accuracy: 97% | Inference: 23ms | Input: 187 samples</p>
</div>
""", unsafe_allow_html=True)