# extract_all_patients.py - Extract ALL heartbeats from ALL patients
import wfdb
import numpy as np
import pandas as pd
import os

DATA_PATH = "data/mit-bih/"
OUTPUT_PATH = "real_patient_data/"

# ALL 48 patients from MIT-BIH database
ALL_PATIENTS = [
    '100', '101', '102', '103', '104', '105', '106', '107',
    '108', '109', '111', '112', '113', '114', '115', '116',
    '117', '118', '119', '121', '122', '123', '124', '200',
    '201', '202', '203', '205', '207', '208', '209', '210',
    '212', '213', '214', '215', '217', '219', '220', '221',
    '222', '223', '228', '230', '231', '232', '233', '234'
]

# Create output folder
os.makedirs(OUTPUT_PATH, exist_ok=True)

# Counter for tracking
total_files = 0
total_normal = 0
total_abnormal = 0

print("=" * 60)
print("EXTRACTING HEARTBEATS FROM ALL 48 PATIENTS")
print("=" * 60)

for patient in ALL_PATIENTS:
    try:
        # Load patient data
        signal = wfdb.rdrecord(f"{DATA_PATH}{patient}")
        ann = wfdb.rdann(f"{DATA_PATH}{patient}", 'atr')
        
        # Get ECG signal
        ecg = signal.p_signal[:, 0]
        
        # Normalize
        ecg = (ecg - np.mean(ecg)) / (np.std(ecg) + 1e-8)
        
        # Get R-peaks and symbols
        r_peaks = ann.sample
        symbols = ann.symbol
        
        half = 93  # For 187 samples
        patient_normal = 0
        patient_abnormal = 0
        
        print(f"\nPatient {patient}:")
        print(f"   Total beats in recording: {len(r_peaks)}")
        
        # Extract beats (limit to 10 per patient)
        beat_count = 0
        for i, peak in enumerate(r_peaks):
            if beat_count >= 10:
                break
                
            if peak < half or peak > len(ecg) - half:
                continue
            
            start = peak - half
            end = peak + half + 1
            heartbeat = ecg[start:end]
            
            if len(heartbeat) == 187:
                symbol = symbols[i]
                beat_count += 1
                total_files += 1
                
                # Save file
                filename = f"{OUTPUT_PATH}patient_{patient}_beat_{beat_count}_{symbol}.csv"
                pd.DataFrame(heartbeat).to_csv(filename, index=False, header=False)
                
                if symbol == 'N':
                    patient_normal += 1
                    total_normal += 1
                    print(f"   Beat {beat_count}: {symbol} - NORMAL")
                else:
                    patient_abnormal += 1
                    total_abnormal += 1
                    print(f"   Beat {beat_count}: {symbol} - ABNORMAL")
        
        print(f"   Saved: {beat_count} beats ({patient_normal} normal, {patient_abnormal} abnormal)")
        
    except Exception as e:
        print(f"   Error loading patient {patient}: {e}")

# Create summary file
summary_data = []
for patient in ALL_PATIENTS:
    patient_files = [f for f in os.listdir(OUTPUT_PATH) if f.startswith(f"patient_{patient}_")]
    summary_data.append({
        'Patient': patient,
        'Files': len(patient_files),
        'Normal': len([f for f in patient_files if '_N.csv' in f]),
        'Abnormal': len([f for f in patient_files if '_N.csv' not in f])
    })

summary_df = pd.DataFrame(summary_data)
summary_df.to_csv(f"{OUTPUT_PATH}ALL_PATIENTS_SUMMARY.csv", index=False)

print("\n" + "=" * 60)
print("EXTRACTION COMPLETE!")
print("=" * 60)
print(f"Total files saved: {total_files}")
print(f"Normal beats: {total_normal}")
print(f"Abnormal beats: {total_abnormal}")
print(f"Summary saved to: {OUTPUT_PATH}ALL_PATIENTS_SUMMARY.csv")

# List patients with abnormal beats
print("\nPATIENTS WITH ABNORMAL BEATS:")
abnormal_patients = summary_df[summary_df['Abnormal'] > 0]
for _, row in abnormal_patients.iterrows():
    print(f"   Patient {row['Patient']}: {row['Abnormal']} abnormal beats")

print("\nDONE! Now run: streamlit run app_final.py")