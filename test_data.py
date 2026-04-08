# test_data.py - Test loading one record
import wfdb
import numpy as np
import os

# Try to load record 100
try:
    print("Loading record 100...")
    signal = wfdb.rdrecord('data/mit-bih/100')
    ann = wfdb.rdann('data/mit-bih/100', 'atr')
    
    print(f"Signal length: {len(signal.p_signal)}")
    print(f"Number of annotations: {len(ann.sample)}")
    print(f"First 10 annotation symbols: {ann.symbol[:10]}")
    
    # Extract one heartbeat
    ecg = signal.p_signal[:, 0]
    half = 93  # 187/2 ≈ 93
    
    peak = ann.sample[0]
    if peak > half and peak < len(ecg) - half:
        start = peak - half
        end = peak + half
        heartbeat = ecg[start:end]
        print(f"Heartbeat shape: {heartbeat.shape}")
    
    print("✅ Success!")
    
except Exception as e:
    print(f"❌ Error: {e}")