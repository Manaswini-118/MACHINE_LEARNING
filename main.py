# main.py - MAIN SCRIPT
import os
import sys
sys.path.append('src')

from data_loader import download_dataset, load_local_data, create_dataset
from model import create_resnet34
from train import train_model

def main():
    print("="*50)
    print("ECG Arrhythmia Classification")
    print("="*50)
    
    os.makedirs('models', exist_ok=True)
    
    # Check if data exists
    if not os.path.exists('data/mit-bih/'):
        download_dataset()
    
    # Load data
    signals, annotations = load_local_data()
    
    if len(signals) == 0:
        print("❌ No data found!")
        return
    
    # Create dataset
    X, y = create_dataset(signals, annotations)
    
    if len(X) == 0:
        print("❌ No heartbeats extracted!")
        return
    
    print(f"\n✅ Dataset ready! Shape: {X.shape}")
    
    # Build model
    print("\n🏗️ Building model...")
    model = create_resnet34(input_shape=(187, 1), num_classes=2)
    model.summary()
    
    # Train
    history, accuracy = train_model(model, X, y, epochs=20, batch_size=64)
    
    print("\n" + "="*50)
    print("✅ Training Complete!")
    print(f"🏆 Test Accuracy: {accuracy:.4f}")
    print("="*50)

if __name__ == "__main__":
    main()