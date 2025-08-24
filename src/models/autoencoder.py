
# =============================================================================
# FILE: src/models/autoencoder.py
# =============================================================================

import numpy as np
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers

class AutoencoderDetector:
    """Autoencoder anomaly detector"""
    
    def __init__(self, config):
        self.config = config
        self.model = None
        self.threshold = None
        self.is_trained = False
    
    def _build_model(self, input_dim):
        """Build autoencoder architecture"""
        encoding_dim = self.config.get('encoding_dim', 10)
        
        # Input layer
        input_layer = keras.Input(shape=(input_dim,))
        
        # Encoder
        encoded = layers.Dense(32, activation='relu')(input_layer)
        encoded = layers.Dense(16, activation='relu')(encoded)
        encoded = layers.Dense(encoding_dim, activation='relu')(encoded)
        
        # Decoder
        decoded = layers.Dense(16, activation='relu')(encoded)
        decoded = layers.Dense(32, activation='relu')(decoded)
        decoded = layers.Dense(input_dim, activation='linear')(decoded)
        
        # Create model
        autoencoder = keras.Model(input_layer, decoded)
        autoencoder.compile(optimizer='adam', loss='mse', metrics=['mae'])
        
        return autoencoder
    
    def train(self, X_train):
        """Train the autoencoder"""
        input_dim = X_train.shape[1]
        self.model = self._build_model(input_dim)
        
        # Train model
        self.model.fit(
            X_train, X_train,
            epochs=self.config.get('epochs', 50),
            batch_size=self.config.get('batch_size', 32),
            validation_split=self.config.get('validation_split', 0.1),
            verbose=1,
            shuffle=True
        )
        
        # Calculate threshold from training data
        train_pred = self.model.predict(X_train)
        train_mse = np.mean(np.power(X_train - train_pred, 2), axis=1)
        self.threshold = np.percentile(train_mse, 95)
        self.is_trained = True
    
    def predict(self, X_test):
        """Predict anomalies"""
        if not self.is_trained:
            raise ValueError("Model not trained")
        
        # Get reconstructions
        reconstructions = self.model.predict(X_test)
        
        # Calculate reconstruction errors
        mse = np.mean(np.power(X_test - reconstructions, 2), axis=1)
        
        # Classify anomalies
        anomalies = mse > self.threshold
        
        return {
            'reconstruction_errors': mse,
            'anomalies': anomalies,
            'threshold': self.threshold
        }

