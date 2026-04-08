# extract_real_ecg.py - Extract REAL patient ECG heartbeats
import wfdb
import numpy as np
import pandas as pd
import os

DATA_PATH = "data/mit-bih/"

# Patient records (each is a different real patient)
REAL_PATIENTS = [
    '100', '101', '102', '103', '104', '105', '106', '107',
    '108', '109', '111', '112', '113', '114', '115', '116',
    '117', '118', '119', '121', '122', '123', '124', '200',
    '201', '202', '203', '205', '207', '208', '209', '210',
    '212', '213', '214', '215', '217', '219', '220', '221',
    '222', '223', '228', '230', '231', '232', '233', '234'
]

def extract_patient_heartbeats(record_name, num_beats=10):
    """Extract real heartbeats from a patient record"""
    try:
        # Load the patient's ECG recording
        signal = wfdb.rdrecord(f"{DATA_PATH}{record_name}")
        ann = wfdb.rdann(f"{DATA_PATH}{record_name}", 'atr')
        
        # Get ECG signal
        ecg = signal.p_signal[:, 0]
        
        # Normalize
        ecg = (ecg - np.mean(ecg)) / (np.std(ecg) + 1e-8)
        
        # Get R-peak positions
        r_peaks = ann.sample
        symbols = ann.symbol
        
        heartbeats = []
        half_window = 93  # 187/2 = 93.5, use 93
        
        for i, peak in enumerate(r_peaks[:num_beats]):
            if peak < half_window or peak > len(ecg) - half_window:
                continue
            
            start = peak - half_window
            end = peak + half_window + 1
            heartbeat = ecg[start:end]
            
            if len(heartbeat) == 187:
                heartbeats.append({
                    'patient_id': record_name,
                    'beat_type': symbols[i],
                    'is_normal': symbols[i] == 'N',
                    'heartbeat': heartbeat
                })
        
        return heartbeats
    
    except Exception as e:
        print(f"Error loading patient {record_name}: {e}")
        return []

def save_real_ecg_files():
    """Save real patient heartbeats as CSV files"""
    
    # Create folder for real patient data
    os.makedirs('real_patient_data', exist_ok=True)
    
    all_patients = []
    
    for patient in REAL_PATIENTS:
        print(f"Extracting data from Patient {patient}...")
        heartbeats = extract_patient_heartbeats(patient, num_beats=5)
        
        for i, beat in enumerate(heartbeats):
            # Save each heartbeat as a separate file
            filename = f"real_patient_data/patient_{patient}_beat_{i+1}_{beat['beat_type']}.csv"
            pd.DataFrame(beat['heartbeat']).to_csv(filename, index=False, header=False)
            print(f"  Saved: {filename}")
            
            all_patients.append({
                'file': filename,
                'patient': patient,
                'beat_type': beat['beat_type'],
                'normal': beat['is_normal']
            })
    
    # Create a summary file
    summary_df = pd.DataFrame(all_patients)
    summary_df.to_csv('real_patient_data/patient_summary.csv', index=False)
    
    print(f"\n✅ Saved {len(all_patients)} real patient heartbeats!")
    print(f"📁 Folder: real_patient_data/")
    print("\n📊 Summary:")
    print(f"   Normal beats: {summary_df['normal'].sum()}")
    print(f"   Abnormal beats: {len(all_patients) - summary_df['normal'].sum()}")
    
    return all_patients

if __name__ == "__main__":
    save_real_ecg_files()