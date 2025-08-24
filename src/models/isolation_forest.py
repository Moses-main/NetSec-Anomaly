
# =============================================================================
# FILE: src/models/isolation_forest.py
# =============================================================================

import numpy as np
from sklearn.ensemble import IsolationForest
import joblib

class IsolationForestDetector:
    """Isolation Forest anomaly detector"""
    
    def __init__(self, config):
        self.config = config
        self.model = None
        self.is_trained = False
    
    def train(self, X_train):
        """Train the Isolation Forest model"""
        self.model = IsolationForest(
            contamination=self.config.get('contamination', 0.1),
            n_estimators=self.config.get('n_estimators', 100),
            random_state=self.config.get('random_state', 42),
            n_jobs=-1
        )
        self.model.fit(X_train)
        self.is_trained = True
    
    def predict(self, X_test):
        """Predict anomalies"""
        if not self.is_trained:
            raise ValueError("Model not trained")
        
        scores = self.model.decision_function(X_test)
        predictions = self.model.predict(X_test)  # -1 for anomaly, 1 for normal
        
        return {
            'scores': scores,
            'predictions': predictions
        }
