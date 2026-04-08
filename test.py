# test.py - Simple test script
import numpy as np
import tensorflow as tf
from tensorflow.keras import layers, models

print("Testing TensorFlow...")
print(f"TensorFlow version: {tf.__version__}")

# Create a simple model
model = models.Sequential([
    layers.Input(shape=(187, 1)),
    layers.Conv1D(32, 3, activation='relu'),
    layers.Flatten(),
    layers.Dense(2, activation='softmax')
])

model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])

# Create dummy data
X_dummy = np.random.randn(100, 187, 1)
y_dummy = np.random.randint(0, 2, 100)
y_dummy = tf.keras.utils.to_categorical(y_dummy, 2)

# Train
print("\nTraining on dummy data...")
model.fit(X_dummy, y_dummy, epochs=5, batch_size=32, verbose=1)

print("\n✅ Test successful!")