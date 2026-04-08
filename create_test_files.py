# create_test_files.py - Create Normal and Abnormal test files
import numpy as np
import pandas as pd

# Create time array (187 samples)
t = np.linspace(0, 1, 187)

# ========== NORMAL ECG ==========
normal_ecg = (
    0.25 * np.sin(2 * np.pi * 3 * t) * np.exp(-30 * (t - 0.2)**2) +
    1.2 * np.sin(2 * np.pi * 12 * t) * np.exp(-50 * (t - 0.45)**2) +
    0.4 * np.sin(2 * np.pi * 4 * t) * np.exp(-25 * (t - 0.7)**2) +
    np.random.randn(187) * 0.05
)

# ========== ABNORMAL ECG (with extra beat) ==========
abnormal_ecg = normal_ecg.copy()
extra_beat = 1.5 * np.sin(2 * np.pi * 15 * t) * np.exp(-40 * (t - 0.75)**2)
abnormal_ecg = abnormal_ecg + extra_beat

# ========== SAVE FILES ==========
pd.DataFrame(normal_ecg).to_csv('test_normal.csv', index=False, header=False)
pd.DataFrame(abnormal_ecg).to_csv('test_abnormal.csv', index=False, header=False)

print("=" * 50)
print("TEST FILES CREATED!")
print("=" * 50)
print(" test_normal.csv - 187 samples")
print(" test_abnormal.csv - 187 samples")
print("\n Normal ECG - Regular heartbeat")
print(" Abnormal ECG - PVC (extra beat)")