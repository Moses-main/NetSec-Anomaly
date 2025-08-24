# =============================================================================
# FILE: src/data/data_loader.py
# =============================================================================

import pandas as pd
import numpy as np

class NetworkDataLoader:
    """Load network traffic data"""
    
    def __init__(self, config):
        self.config = config
        
    def generate_sample_data(self):
        """Generate sample network traffic data"""
        np.random.seed(self.config.get('random_state', 42))
        n_samples = self.config.get('sample_size', 10000)
        
        # Normal traffic patterns
        data = {
            'duration': np.random.exponential(2, n_samples),
            'src_bytes': np.random.lognormal(8, 1.5, n_samples),
            'dst_bytes': np.random.lognormal(6, 1.2, n_samples),
            'count': np.random.poisson(10, n_samples),
            'srv_count': np.random.poisson(5, n_samples),
            'protocol': np.random.choice(['tcp', 'udp', 'icmp'], n_samples, p=[0.7, 0.2, 0.1]),
            'service': np.random.choice(['http', 'ftp', 'telnet', 'smtp', 'dns'], n_samples),
            'flag': np.random.choice(['SF', 'S0', 'REJ', 'RSTR'], n_samples, p=[0.6, 0.2, 0.1, 0.1])
        }
        
        # Add anomalies (10% of data)
        n_anomalies = int(n_samples * 0.1)
        anomaly_indices = np.random.choice(n_samples, n_anomalies, replace=False)
        
        for idx in anomaly_indices:
            if np.random.random() > 0.5:
                data['src_bytes'][idx] *= 100  # Large data transfer
            else:
                data['count'][idx] *= 50  # High connection count
        
        return pd.DataFrame(data)
    
    def load_from_file(self, filepath):
        """Load data from file"""
        if filepath.endswith('.csv'):
            return pd.read_csv(filepath)
        elif filepath.endswith('.json'):
            return pd.read_json(filepath)
        else:
            raise ValueError(f"Unsupported file format: {filepath}")

