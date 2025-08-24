
# =============================================================================
# FILE: src/utils/visualization.py
# =============================================================================

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

class DetectionVisualizer:
    """Visualization utilities for anomaly detection"""
    
    def plot_anomaly_scores(self, scores, save_path=None):
        """Plot anomaly scores distribution"""
        plt.figure(figsize=(10, 6))
        plt.hist(scores, bins=50, alpha=0.7, edgecolor='black')
        plt.title('Isolation Forest Anomaly Scores')
        plt.xlabel('Anomaly Score')
        plt.ylabel('Frequency')
        
        if save_path:
            plt.savefig(save_path)
            plt.close()
        else:
            plt.show()
    
    def plot_reconstruction_errors(self, errors, threshold, save_path=None):
        """Plot reconstruction errors"""
        plt.figure(figsize=(10, 6))
        plt.hist(errors, bins=50, alpha=0.7, edgecolor='black')
        plt.axvline(threshold, color='red', linestyle='--', 
                   label=f'Threshold: {threshold:.6f}')
        plt.title('Autoencoder Reconstruction Errors')
        plt.xlabel('Mean Squared Error')
        plt.ylabel('Frequency')
        plt.legend()
        
        if save_path:
            plt.savefig(save_path)
            plt.close()
        else:
            plt.show()
    
    def plot_detection_comparison(self, results, X_test, save_path=None):
        """Plot detection comparison"""
        plt.figure(figsize=(12, 8))
        
        if_anomalies = results['isolation_forest']['predictions'] == -1
        ae_anomalies = results['autoencoder']['anomalies']
        
        normal_mask = ~(if_anomalies | ae_anomalies)
        if_only = if_anomalies & ~ae_anomalies
        ae_only = ae_anomalies & ~if_anomalies
        both = if_anomalies & ae_anomalies
        
        plt.scatter(X_test[normal_mask, 0], X_test[normal_mask, 1], 
                   c='blue', alpha=0.6, label='Normal', s=20)
        plt.scatter(X_test[if_only, 0], X_test[if_only, 1], 
                   c='orange', alpha=0.8, label='IF Only', s=30)
        plt.scatter(X_test[ae_only, 0], X_test[ae_only, 1], 
                   c='green', alpha=0.8, label='AE Only', s=30)
        plt.scatter(X_test[both, 0], X_test[both, 1], 
                   c='red', alpha=0.9, label='Both Methods', s=40)
        
        plt.title('Anomaly Detection Comparison')
        plt.xlabel('Feature 1 (Normalized)')
        plt.ylabel('Feature 2 (Normalized)')
        plt.legend()
        
        if save_path:
            plt.savefig(save_path)
            plt.close()
        else:
            plt.show()
