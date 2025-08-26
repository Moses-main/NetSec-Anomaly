#!/usr/bin/env python3
"""
Main entry point for Network Anomaly Detection System
Modular architecture for production deployment
"""

import argparse
import yaml
import logging
import pandas as pd
import numpy as np
from pathlib import Path
import joblib
import json
from datetime import datetime
import time

# Import custom modules
from models.isolation_forest import IsolationForestDetector
from models.autoencoder import AutoencoderDetector
from models.ensemble import EnsembleDetector
from data.data_loader import NetworkDataLoader
from data.preprocessor import NetworkDataPreprocessor
from utils.metrics import DetectionMetrics
from utils.visualization import DetectionVisualizer
from utils.logger import setup_logger

class NetworkAnomalyDetectionSystem:
    """
    Main system orchestrator for network anomaly detection
    """
    
    def __init__(self, config_path="config/config.yaml"):
        """
        Initialize the detection system with configuration
        
        Args:
            config_path (str): Path to configuration file
        """
        self.config = self._load_config(config_path)
        self.logger = setup_logger(self.config['logging'])
        
        # Initialize components
        self.data_loader = NetworkDataLoader(self.config['data'])
        self.preprocessor = NetworkDataPreprocessor(self.config['data'])
        self.metrics = DetectionMetrics()
        self.visualizer = DetectionVisualizer()
        
        # Initialize models
        self.if_detector = IsolationForestDetector(self.config['models']['isolation_forest'])
        self.ae_detector = AutoencoderDetector(self.config['models']['autoencoder'])
        self.ensemble = EnsembleDetector(self.config['detection'])
        
        # Model states
        self.models_trained = False
        self.preprocessor_fitted = False
        self.y_train = None
        self.y_test = None
        self.timings = {
            'train': {},
            'inference': {}
        }
        
    def _load_config(self, config_path):
        """Load configuration from YAML file"""
        try:
            with open(config_path, 'r') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            # Return default configuration if file not found
            return self._get_default_config()
    
    def _get_default_config(self):
        """Get default configuration"""
        return {
            'models': {
                'isolation_forest': {
                    'contamination': 0.1,
                    'n_estimators': 100,
                    'random_state': 42
                },
                'autoencoder': {
                    'encoding_dim': 10,
                    'epochs': 50,
                    'batch_size': 32,
                    'validation_split': 0.1
                }
            },
            'data': {
                'test_size': 0.2,
                'random_state': 42,
                'sample_size': 10000
            },
            'detection': {
                'ensemble_method': 'majority_vote',
                'threshold_percentile': 95
            },
            'logging': {
                'level': 'INFO',
                'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            }
        }
    
    def load_data(self, data_path=None, generate_sample=True):
        """
        Load and preprocess network traffic data
        
        Args:
            data_path (str): Path to data file
            generate_sample (bool): Whether to generate sample data
            
        Returns:
            pd.DataFrame: Loaded data
        """
        self.logger.info("Loading network traffic data...")
        
        if generate_sample or data_path is None:
            # Generate sample data for demonstration
            data = self.data_loader.generate_sample_data()
            self.logger.info(f"Generated sample data with {len(data)} records")
        else:
            # Load real data
            data = self.data_loader.load_from_file(data_path)
            self.logger.info(f"Loaded data from {data_path} with {len(data)} records")
        
        return data
    
    def preprocess_data(self, data, fit_preprocessor=True):
        """
        Preprocess network traffic data
        
        Args:
            data (pd.DataFrame): Raw network traffic data
            fit_preprocessor (bool): Whether to fit the preprocessor
            
        Returns:
            tuple: Processed training and testing data
        """
        self.logger.info("Preprocessing network traffic data...")
        
        if fit_preprocessor:
            ret = self.preprocessor.fit_transform(data)
            # Support both legacy and extended returns
            if isinstance(ret, tuple) and len(ret) == 4:
                X_train, X_test, y_train, y_test = ret
            elif isinstance(ret, tuple) and len(ret) == 3:
                X_train, X_test, y_train = ret
                y_test = None
            else:
                X_train, X_test = ret
                y_train = None
                y_test = None
            self.y_train, self.y_test = y_train, y_test
            self.preprocessor_fitted = True
        else:
            if not self.preprocessor_fitted:
                raise ValueError("Preprocessor not fitted. Call preprocess_data with fit_preprocessor=True first.")
            ret = self.preprocessor.transform(data)
            if isinstance(ret, tuple) and len(ret) == 4:
                X_train, X_test, _, y_test = ret
            elif isinstance(ret, tuple) and len(ret) == 3:
                X_train, X_test, _ = ret
                y_test = None
            else:
                X_train, X_test = ret
                y_test = None
            self.y_test = y_test
        
        self.logger.info(f"Training data shape: {X_train.shape}")
        self.logger.info(f"Testing data shape: {X_test.shape}")
        
        return X_train, X_test, self.y_train, self.y_test
    
    def train_models(self, X_train):
        """
        Train all anomaly detection models
        
        Args:
            X_train (np.ndarray): Training data
        """
        self.logger.info("Training anomaly detection models...")
        
        # Train Isolation Forest with timing
        self.logger.info("Training Isolation Forest...")
        t0 = time.perf_counter()
        self.if_detector.train(X_train)
        self.timings['train']['isolation_forest_sec'] = time.perf_counter() - t0
        
        # Train Autoencoder with timing
        self.logger.info("Training Autoencoder...")
        t0 = time.perf_counter()
        self.ae_detector.train(X_train)
        self.timings['train']['autoencoder_sec'] = time.perf_counter() - t0
        
        self.models_trained = True
        self.logger.info("All models trained successfully")
    
    def detect_anomalies(self, X_test):
        """
        Detect anomalies using trained models
        
        Args:
            X_test (np.ndarray): Test data
            
        Returns:
            dict: Detection results from all methods
        """
        if not self.models_trained:
            raise ValueError("Models not trained. Call train_models() first.")
        
        self.logger.info("Detecting anomalies...")
        
        # Get predictions from individual models with timing
        t0 = time.perf_counter()
        if_results = self.if_detector.predict(X_test)
        self.timings['inference']['isolation_forest_sec'] = time.perf_counter() - t0

        t0 = time.perf_counter()
        ae_results = self.ae_detector.predict(X_test)
        self.timings['inference']['autoencoder_sec'] = time.perf_counter() - t0
        
        # Combine using ensemble method
        ensemble_results = self.ensemble.combine_predictions(
            if_results['predictions'], 
            ae_results['anomalies']
        )
        
        results = {
            'isolation_forest': if_results,
            'autoencoder': ae_results,
            'ensemble': ensemble_results,
            'metadata': {
                'timestamp': datetime.now().isoformat(),
                'total_samples': len(X_test),
                'if_anomalies': np.sum(if_results['predictions'] == -1),
                'ae_anomalies': np.sum(ae_results['anomalies']),
                'ensemble_anomalies': np.sum(ensemble_results),
                'timings_sec': self.timings
            }
        }
        
        self.logger.info(f"Detection complete. Found {results['metadata']['ensemble_anomalies']} anomalies")
        
        return results
    
    def evaluate_performance(self, results, y_true=None):
        """
        Evaluate model performance
        
        Args:
            results (dict): Detection results
            y_true (np.ndarray): True labels (if available)
            
        Returns:
            dict: Performance metrics
        """
        self.logger.info("Evaluating model performance...")
        
        metrics = {}
        
        if y_true is not None:
            # Calculate metrics with ground truth
            if_pred = results['isolation_forest']['predictions'] == -1
            ae_pred = results['autoencoder']['anomalies']
            ensemble_pred = results['ensemble']
            
            metrics['isolation_forest'] = self.metrics.calculate_metrics(y_true, if_pred)
            metrics['autoencoder'] = self.metrics.calculate_metrics(y_true, ae_pred)
            metrics['ensemble'] = self.metrics.calculate_metrics(y_true, ensemble_pred)
        else:
            # Calculate metrics without ground truth
            metrics = self.metrics.calculate_unsupervised_metrics(results)
        
        return metrics
    
    def generate_visualizations(self, results, X_test, output_dir="results"):
        """
        Generate visualization plots
        
        Args:
            results (dict): Detection results
            X_test (np.ndarray): Test data
            output_dir (str): Output directory for plots
        """
        self.logger.info("Generating visualizations...")
        
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        # Create various plots
        self.visualizer.plot_anomaly_scores(
            results['isolation_forest']['scores'], 
            save_path=f"{output_dir}/if_scores.png"
        )
        
        self.visualizer.plot_reconstruction_errors(
            results['autoencoder']['reconstruction_errors'],
            results['autoencoder']['threshold'],
            save_path=f"{output_dir}/ae_errors.png"
        )
        
        self.visualizer.plot_detection_comparison(
            results, X_test,
            save_path=f"{output_dir}/detection_comparison.png"
        )
        
        self.logger.info(f"Visualizations saved to {output_dir}")
    
    def save_models(self, model_dir="models/saved_models"):
        """
        Save trained models to disk
        
        Args:
            model_dir (str): Directory to save models
        """
        Path(model_dir).mkdir(parents=True, exist_ok=True)
        
        # Save Isolation Forest
        joblib.dump(self.if_detector.model, f"{model_dir}/isolation_forest.joblib")
        
        # Save Autoencoder
        self.ae_detector.model.save(f"{model_dir}/autoencoder.h5")
        
        # Save preprocessor
        joblib.dump(self.preprocessor, f"{model_dir}/preprocessor.joblib")
        
        self.logger.info(f"Models saved to {model_dir}")
    
    def load_models(self, model_dir="models/saved_models"):
        """
        Load trained models from disk
        
        Args:
            model_dir (str): Directory containing saved models
        """
        # Load Isolation Forest
        self.if_detector.model = joblib.load(f"{model_dir}/isolation_forest.joblib")
        
        # Load Autoencoder
        from tensorflow import keras
        self.ae_detector.model = keras.models.load_model(f"{model_dir}/autoencoder.h5")
        
        # Load preprocessor
        self.preprocessor = joblib.load(f"{model_dir}/preprocessor.joblib")
        
        self.models_trained = True
        self.preprocessor_fitted = True
        self.logger.info(f"Models loaded from {model_dir}")
    
    def generate_report(self, results, metrics, output_file="results/detection_report.json"):
        """
        Generate comprehensive detection report
        
        Args:
            results (dict): Detection results
            metrics (dict): Performance metrics
            output_file (str): Output file path
        """
        report = {
            'summary': {
                'timestamp': datetime.now().isoformat(),
                'total_samples': results['metadata']['total_samples'],
                'anomalies_detected': {
                    'isolation_forest': results['metadata']['if_anomalies'],
                    'autoencoder': results['metadata']['ae_anomalies'],
                    'ensemble': results['metadata']['ensemble_anomalies']
                },
                'detection_rates': {
                    'isolation_forest': results['metadata']['if_anomalies'] / results['metadata']['total_samples'],
                    'autoencoder': results['metadata']['ae_anomalies'] / results['metadata']['total_samples'],
                    'ensemble': results['metadata']['ensemble_anomalies'] / results['metadata']['total_samples']
                }
            },
            'performance_metrics': metrics,
            'configuration': self.config
        }
        
        # Save report
        Path(output_file).parent.mkdir(parents=True, exist_ok=True)
        with open(output_file, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        self.logger.info(f"Report saved to {output_file}")
        
        return report
    
    def run_full_pipeline(self, data_path=None, output_dir="results"):
        """
        Run the complete anomaly detection pipeline
        
        Args:
            data_path (str): Path to input data
            output_dir (str): Output directory for results
            
        Returns:
            dict: Complete results including detection and metrics
        """
        self.logger.info("Starting full anomaly detection pipeline...")
        
        # Load data
        data = self.load_data(data_path, generate_sample=(data_path is None))
        
        # Preprocess data
        X_train, X_test, y_train, y_test = self.preprocess_data(data)
        
        # Train models
        self.train_models(X_train)
        
        # Detect anomalies
        results = self.detect_anomalies(X_test)
        
        # Evaluate performance
        metrics = self.evaluate_performance(results, y_true=y_test if y_test is not None else None)
        
        # Generate visualizations
        self.generate_visualizations(results, X_test, output_dir)
        
        # Save models
        self.save_models()
        
        # Generate report
        report = self.generate_report(results, metrics, f"{output_dir}/detection_report.json")
        
        self.logger.info("Pipeline completed successfully!")
        
        return {
            'results': results,
            'metrics': metrics,
            'report': report
        }

def main():
    """
    Command-line interface for the detection system
    """
    parser = argparse.ArgumentParser(description="Network Anomaly Detection System")
    parser.add_argument("--config", default="config/config.yaml", help="Configuration file path")
    parser.add_argument("--data", help="Input data file path")
    parser.add_argument("--output", default="results", help="Output directory")
    parser.add_argument("--mode", choices=["train", "detect", "full"], default="full", 
                       help="Operation mode")
    parser.add_argument("--load-models", help="Directory containing pre-trained models")
    
    args = parser.parse_args()
    
    # Initialize system
    detector = NetworkAnomalyDetectionSystem(args.config)
    
    if args.mode == "full":
        # Run complete pipeline
        results = detector.run_full_pipeline(args.data, args.output)
        
    elif args.mode == "train":
        # Training mode
        data = detector.load_data(args.data)
        X_train, _ = detector.preprocess_data(data)
        detector.train_models(X_train)
        detector.save_models()
        
    elif args.mode == "detect":
        # Detection mode (requires pre-trained models)
        if args.load_models:
            detector.load_models(args.load_models)
        
        data = detector.load_data(args.data)
        _, X_test = detector.preprocess_data(data, fit_preprocessor=False)
        results = detector.detect_anomalies(X_test)
        
        # Save results
        with open(f"{args.output}/detection_results.json", 'w') as f:
            json.dump(results, f, indent=2, default=str)

if __name__ == "__main__":
    main()