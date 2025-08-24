
# =============================================================================
# FILE: src/data/preprocessor.py
# =============================================================================

import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split

class NetworkDataPreprocessor:
    """Preprocess network traffic data"""
    
    def __init__(self, config):
        self.config = config
        self.scaler = StandardScaler()
        self.label_encoders = {}
        self.feature_names = []
        self.is_fitted = False
    
    def fit_transform(self, data):
        """Fit preprocessor and transform data"""
        # Encode categorical variables
        data_processed = data.copy()
        categorical_cols = ['protocol', 'service', 'flag']
        
        for col in categorical_cols:
            if col in data_processed.columns:
                le = LabelEncoder()
                data_processed[col] = le.fit_transform(data_processed[col])
                self.label_encoders[col] = le
        
        # Store feature names
        self.feature_names = data_processed.columns.tolist()
        
        # Split data
        X = data_processed.values
        X_train, X_test = train_test_split(
            X, 
            test_size=self.config.get('test_size', 0.2),
            random_state=self.config.get('random_state', 42)
        )
        
        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        self.is_fitted = True
        return X_train_scaled, X_test_scaled
    
    def transform(self, data):
        """Transform new data using fitted preprocessor"""
        if not self.is_fitted:
            raise ValueError("Preprocessor not fitted")
        
        # Encode categorical variables
        data_processed = data.copy()
        for col, le in self.label_encoders.items():
            if col in data_processed.columns:
                data_processed[col] = le.transform(data_processed[col])
        
        # Scale features
        X = data_processed.values
        X_scaled = self.scaler.transform(X)
        
        return None, X_scaled  # Return None for X_train since we're only transforming
