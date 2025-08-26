
# =============================================================================
# FILE: src/data/preprocessor.py
# =============================================================================

import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split
from typing import List, Optional, Tuple

class NetworkDataPreprocessor:
    """Preprocess network traffic data"""
    
    def __init__(self, config):
        self.config = config
        self.scaler = StandardScaler()
        self.label_encoders = {}
        self.feature_names = []
        self.is_fitted = False
        self.label_col: Optional[str] = None
        self.y_name: Optional[str] = None

    def _detect_label_column(self, df: pd.DataFrame) -> Optional[str]:
        candidates = [
            'label', 'Label', 'labels', 'Labels', 'class', 'Class', 'attack', 'Attack',
            'Attack_type', 'attack_type', 'Category', 'category'
        ]
        for c in candidates:
            if c in df.columns:
                return c
        return None

    def _encode_object_columns(self, df: pd.DataFrame, fit: bool) -> pd.DataFrame:
        df_out = df.copy()
        obj_cols = [c for c in df_out.columns if df_out[c].dtype == 'object']
        for col in obj_cols:
            if fit:
                le = LabelEncoder()
                # Replace NaN with a placeholder string for encoding
                series = df_out[col].astype(str).fillna('<NA>')
                le.fit(series)
                df_out[col] = le.transform(series)
                self.label_encoders[col] = le
            else:
                if col in self.label_encoders:
                    le = self.label_encoders[col]
                    series = df_out[col].astype(str).fillna('<NA>')
                    # Safely handle unseen labels by extending classes_
                    unseen = np.setdiff1d(series.unique(), le.classes_)
                    if len(unseen) > 0:
                        le.classes_ = np.concatenate([le.classes_, unseen])
                    df_out[col] = le.transform(series)
                else:
                    # No encoder from fit phase; fallback to factorize (stable order within batch)
                    df_out[col] = pd.factorize(df_out[col].astype(str).fillna('<NA>'))[0]
        return df_out

    def _coerce_numeric(self, df: pd.DataFrame) -> pd.DataFrame:
        df_num = df.copy()
        for col in df_num.columns:
            if df_num[col].dtype == 'object':
                # Should already be encoded, but coerce just in case
                df_num[col] = pd.to_numeric(df_num[col], errors='coerce')
        # Fill any NaNs created during coercion
        df_num = df_num.replace([np.inf, -np.inf], np.nan).fillna(0.0)
        return df_num

    def fit_transform(self, data) -> Tuple[np.ndarray, np.ndarray, Optional[np.ndarray], Optional[np.ndarray]]:
        """Fit preprocessor and transform data"""
        df = data.copy()

        # Detect and remove label column from features
        self.label_col = self._detect_label_column(df)
        y = None
        if self.label_col is not None:
            y = df[self.label_col].copy()
            df = df.drop(columns=[self.label_col])

        # Encode all object columns robustly
        df = self._encode_object_columns(df, fit=True)

        # Coerce any remaining non-numeric columns and handle NaNs
        df = self._coerce_numeric(df)

        # Store feature names consistently
        self.feature_names = df.columns.tolist()

        # Split data (and labels if available)
        X = df.values.astype(float)
        if y is not None:
            X_train, X_test, y_train, y_test = train_test_split(
                X,
                y.values,
                test_size=self.config.get('test_size', 0.2),
                random_state=self.config.get('random_state', 42)
            )
        else:
            X_train, X_test = train_test_split(
                X,
                test_size=self.config.get('test_size', 0.2),
                random_state=self.config.get('random_state', 42)
            )
            y_train, y_test = None, None
        
        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        self.is_fitted = True
        return X_train_scaled, X_test_scaled, y_train, y_test
    
    def transform(self, data) -> Tuple[Optional[np.ndarray], np.ndarray, Optional[np.ndarray], Optional[np.ndarray]]:
        """Transform new data using fitted preprocessor"""
        if not self.is_fitted:
            raise ValueError("Preprocessor not fitted")
        
        df = data.copy()

        # Drop label column if present
        if self.label_col is not None and self.label_col in df.columns:
            y = df[self.label_col].copy()
            df = df.drop(columns=[self.label_col])
        else:
            y = None

        # Ensure we only use columns seen during fit; add any missing as zeros
        # First, bring df to include all fit columns
        for col in self.feature_names:
            if col not in df.columns:
                df[col] = 0
        # Remove any unexpected extra columns
        df = df[self.feature_names]

        # Encode object columns with fitted encoders (handle unseen)
        df = self._encode_object_columns(df, fit=False)

        # Coerce numeric and handle NaNs
        df = self._coerce_numeric(df)

        # Scale
        X = df.values.astype(float)
        X_scaled = self.scaler.transform(X)
        
        # During transform we only provide test set and its labels
        return None, X_scaled, None, (y.values if y is not None else None)
