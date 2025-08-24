
# =============================================================================
# FILE: src/utils/metrics.py
# =============================================================================

import numpy as np
from sklearn.metrics import precision_score, recall_score, f1_score, roc_auc_score

class DetectionMetrics:
    """Calculate performance metrics for anomaly detection"""
    
    def calculate_metrics(self, y_true, y_pred):
        """Calculate supervised metrics"""
        return {
            'precision': precision_score(y_true, y_pred),
            'recall': recall_score(y_true, y_pred),
            'f1_score': f1_score(y_true, y_pred),
            'accuracy': np.mean(y_true == y_pred)
        }
    
    def calculate_unsupervised_metrics(self, results):
        """Calculate unsupervised metrics"""
        total_samples = results['metadata']['total_samples']
        
        return {
            'detection_rates': {
                'isolation_forest': results['metadata']['if_anomalies'] / total_samples,
                'autoencoder': results['metadata']['ae_anomalies'] / total_samples,
                'ensemble': results['metadata']['ensemble_anomalies'] / total_samples
            },
            'method_agreement': self._calculate_agreement(results),
            'total_samples': total_samples
        }
    
    def _calculate_agreement(self, results):
        """Calculate agreement between methods"""
        if_anomalies = results['isolation_forest']['predictions'] == -1
        ae_anomalies = results['autoencoder']['anomalies']
        agreement = np.mean(if_anomalies == ae_anomalies)
        return agreement

