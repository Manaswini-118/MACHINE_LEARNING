# predict.py - ECG Classifier
import numpy as np
import tensorflow as tf
import os

class ECGClassifier:
    def __init__(self, model_path='models/best_model.h5'):
        self.model_path = model_path
        self.model = None
        self.load_model()
    
    def load_model(self):
        """Load the trained model"""
        if os.path.exists(self.model_path):
            try:
                self.model = tf.keras.models.load_model(self.model_path)
                print("✅ Model loaded successfully!")
                return True
            except Exception as e:
                print(f"❌ Error loading model: {e}")
                return False
        else:
            print("❌ Model not found! Please train first.")
            return False
    
    def preprocess_heartbeat(self, heartbeat):
        """Preprocess a single heartbeat for prediction"""
        if len(heartbeat) != 187:
            print(f"⚠️ Expected 187 samples, got {len(heartbeat)}")
            return None
        
        # Normalize to zero mean and unit variance
        heartbeat = (heartbeat - np.mean(heartbeat)) / (np.std(heartbeat) + 1e-8)
        # Reshape for model (batch_size, time, channels)
        heartbeat = heartbeat.reshape(1, 187, 1)
        return heartbeat
    
    def predict(self, heartbeat):
        """Predict if heartbeat is normal or abnormal"""
        if self.model is None:
            return None, None
        
        processed = self.preprocess_heartbeat(heartbeat)
        if processed is None:
            return None, None
        
        # Make prediction
        prediction = self.model.predict(processed, verbose=0)
        
        class_id = np.argmax(prediction[0])
        confidence = float(prediction[0][class_id])
        
        result = {
            0: {'label': 'NORMAL', 'color': 'green', 'risk': 'LOW', 'emoji': '✅', 'message': 'Heartbeat is normal'},
            1: {'label': 'ABNORMAL', 'color': 'red', 'risk': 'HIGH', 'emoji': '⚠️', 'message': 'Arrhythmia detected! Consult doctor'}
        }
        
        return result[class_id], confidence

# Test if run directly
if __name__ == "__main__":
    print("Testing ECG Classifier...")
    classifier = ECGClassifier()
    if classifier.model:
        # Test with random data
        dummy = np.random.randn(187)
        result, conf = classifier.predict(dummy)
        if result:
            print(f"Test Result: {result['emoji']} {result['label']} ({conf:.1%})")
            print(f"Message: {result['message']}")