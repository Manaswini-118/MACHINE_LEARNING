# simple_test.py - Test one record
import wfdb
import numpy as np

# Load record 100
print("Loading record 100...")
signal = wfdb.rdrecord('data/mit-bih/100')
ann = wfdb.rdann('data/mit-bih/100', 'atr')

print(f"Signal length: {len(signal.p_signal)}")
print(f"Number of annotations: {len(ann.sample)}")
print(f"First 10 symbols: {ann.symbol[:10]}")
print(f"First 10 peaks: {ann.sample[:10]}")

# Get ECG signal
ecg = signal.p_signal[:, 0]
half = 93
WINDOW_SIZE = 187

print("\nChecking first 10 beats:")
for i in range(10):
    peak = ann.sample[i]
    symbol = ann.symbol[i]
    
    if peak < half or peak > len(ecg) - half:
        print(f"  Beat {i}: peak={peak}, symbol={symbol} - OUT OF BOUNDS")
    else:
        start = peak - half
        end = peak + half
        heartbeat = ecg[start:end]
        print(f"  Beat {i}: peak={peak}, symbol={symbol}, heartbeat length={len(heartbeat)}")