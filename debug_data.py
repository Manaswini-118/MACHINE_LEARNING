# debug_data.py - Check what's in the data
import wfdb
import numpy as np

# Test first 5 records
records = ['100', '101', '102', '103', '104']

for record in records:
    print(f"\n{'='*40}")
    print(f"Record: {record}")
    print('='*40)
    
    try:
        # Load signal and annotations
        signal = wfdb.rdrecord(f'data/mit-bih/{record}')
        ann = wfdb.rdann(f'data/mit-bih/{record}', 'atr')
        
        print(f"Signal length: {len(signal.p_signal)}")
        print(f"Number of annotations: {len(ann.sample)}")
        print(f"First 20 annotation symbols: {ann.symbol[:20]}")
        
        # Check unique symbols
        unique_symbols = set(ann.symbol)
        print(f"Unique symbols: {unique_symbols}")
        
        # Check if 'N' exists
        if 'N' in unique_symbols:
            print("✓ Has NORMAL beats")
        else:
            print("✗ No NORMAL beats found")
            
        # Get ECG signal
        ecg = signal.p_signal[:, 0]
        half = 93
        
        # Check first few peaks
        valid_beats = 0
        for i, peak in enumerate(ann.sample[:10]):
            if peak > half and peak < len(ecg) - half:
                valid_beats += 1
                print(f"  Beat {i}: peak={peak}, symbol={ann.symbol[i]}")
            else:
                print(f"  Beat {i}: peak={peak} - OUT OF BOUNDS")
        
        print(f"Valid beats in first 10: {valid_beats}/10")
        
    except Exception as e:
        print(f"Error: {e}")