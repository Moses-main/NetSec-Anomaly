
# =============================================================================
# FILE: src/models/ensemble.py
# =============================================================================

import numpy as np

class EnsembleDetector:
    """Ensemble method combining multiple detectors"""
    
    def __init__(self, config):
        self.config = config
        self.method = config.get('ensemble_method', 'majority_vote')
    
    def combine_predictions(self, if_predictions, ae_anomalies):
        """Combine predictions from IF and AE"""
        # Convert IF predictions to boolean (True for anomaly)
        if_anomalies = if_predictions == -1
        
        if self.method == 'majority_vote':
            # Flag as anomaly if either method detects it
            return if_anomalies | ae_anomalies
        elif self.method == 'intersection':
            # Flag as anomaly only if both methods detect it
            return if_anomalies & ae_anomalies
        elif self.method == 'union':
            # Same as majority_vote for two methods
            return if_anomalies | ae_anomalies
        else:
            return if_anomalies | ae_anomalies

