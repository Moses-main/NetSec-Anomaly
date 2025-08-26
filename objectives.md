# Project Objectives and Achievements

This document outlines the project objectives, provides in-depth discussion for each, and includes an “Objectives Achieved (Based on Results)” section to align with the actual outputs produced by the pipeline.

## Objectives

1. Feature identification for network anomaly detection
2. Build an Isolation Forest model
3. Implement an autoencoder-based deep learning anomaly detection model
4. Compare Isolation Forest and Autoencoder in terms of accuracy, performance, and computational overhead

---

## 1) Feature Identification for Network Anomaly Detection

- Purpose: Select features that best capture behavioral deviations in network traffic.
- Selected features (defined in `src/data/data_loader.py`, processed in `src/data/preprocessor.py`):
  - `duration`: Connection length; extremes can suggest abnormal sessions.
  - `src_bytes`, `dst_bytes`: Directional data volume; spikes can signal exfiltration or floods.
  - `count`, `srv_count`: Frequency indicators; surges hint at scanning or DDoS.
  - `protocol`: Transport protocol (TCP/UDP/ICMP); differences affect normal baselines.
  - `service`: Application/service type (HTTP/FTP/Telnet/SMTP/DNS); captures app-layer norms.
  - `flag`: TCP status flags (SF, S0, REJ, RSTR); identify failed/odd handshakes.
- Preprocessing (`NetworkDataPreprocessor` in `src/data/preprocessor.py`):
  - Label encodes categorical features with resilience to unseen categories at inference.
  - Coerces non-numeric to numeric, handles NaN/inf, then standardizes via `StandardScaler`.
  - Splits into train/test and returns `(X_train, X_test, y_train, y_test)` when a label exists.
- Label availability: The synthetic generator injects anomalies and sets `label` (0=normal, 1=anomaly) to enable supervised evaluation.

Rationale: This set balances traffic volume, connection frequency, protocol/service semantics, and transport-layer states—collectively capturing a wide spectrum of anomalous behavior.

---

## 2) Isolation Forest Model

- Implementation: `IsolationForestDetector` (`src/models/isolation_forest.py`).
- Configuration (defaults via `src/main.py` → `_get_default_config()`):
  - `contamination`: Expected anomaly ratio (default 0.1).
  - `n_estimators`: Trees (default 100).
  - `random_state`: Reproducibility.
- Behavior in pipeline (`src/main.py`):
  - Trained on scaled `X_train`.
  - Predicts on `X_test` with `predictions` (−1 anomaly, +1 normal) and `scores` (`decision_function`).
  - Training and inference time recorded under `results['metadata']['timings_sec']`.
- Strengths: Fast, simple, effective baseline without labels.
- Considerations: Sensitive to `contamination`; may miss complex non-linear structures.

---

## 3) Autoencoder-Based Deep Learning Model

- Implementation: `AutoencoderDetector` (`src/models/autoencoder.py`) using TensorFlow/Keras.
- Architecture:
  - Encoder: Dense 32 → 16 → bottleneck (`encoding_dim`, default 10).
  - Decoder: Mirrors back to input dimensionality.
  - Loss: MSE; Optimizer: Adam; metric: MAE.
- Thresholding strategy:
  - Compute training reconstruction error distribution; threshold set to 95th percentile.
  - At inference, `reconstruction_errors > threshold` → anomaly.
- Behavior in pipeline (`src/main.py`):
  - Trained on scaled `X_train`.
  - Predicts reconstruction errors and boolean `anomalies` on `X_test`.
  - Training and inference times recorded in `timings_sec`.
- Strengths: Captures non-linear manifolds; can improve recall for subtle anomalies.
- Considerations: Higher computational cost; sensitive to normalization and threshold choice.

---

## 4) Comparison: Accuracy, Performance, Computational Overhead

- Metrics (`src/utils/metrics.py` and evaluation in `src/main.py`):
  - With labels (present in synthetic data), supervised metrics are computed for Isolation Forest, Autoencoder, and an ensemble (majority vote in `src/models/ensemble.py`): accuracy, precision, recall, F1.
  - Without labels, unsupervised summaries include detection rates and method agreement.
- Overhead/Performance:
  - Training time (seconds): `results['metadata']['timings_sec']['train']`.
  - Inference time (seconds): `results['metadata']['timings_sec']['inference']`.
- Practical findings (expected):
  - Isolation Forest: strong baseline, low compute, fast inference.
  - Autoencoder: potentially higher recall on complex patterns, with increased training time.

---

## Objectives Achieved (Based on Results)

After running:

```bash
python3 src/main.py --mode full --output results
```

The report `results/detection_report.json` contains metrics and timings. Populate the placeholders below from the report.

- Feature Identification:

  - Features used: duration, src_bytes, dst_bytes, count, srv_count, protocol, service, flag.
  - Label column detected and used: `label`.

- Isolation Forest Model:

  - Accuracy: <from `performance_metrics.isolation_forest.accuracy`>
  - Precision: <from `performance_metrics.isolation_forest.precision`>
  - Recall: <from `performance_metrics.isolation_forest.recall`>
  - F1: <from `performance_metrics.isolation_forest.f1_score`>
  - Train time (s): <from `results.metadata.timings_sec.train.isolation_forest_sec`>
  - Inference time (s): <from `results.metadata.timings_sec.inference.isolation_forest_sec`>

- Autoencoder Model:

  - Accuracy: <from `performance_metrics.autoencoder.accuracy`>
  - Precision: <from `performance_metrics.autoencoder.precision`>
  - Recall: <from `performance_metrics.autoencoder.recall`>
  - F1: <from `performance_metrics.autoencoder.f1_score`>
  - Train time (s): <from `results.metadata.timings_sec.train.autoencoder_sec`>
  - Inference time (s): <from `results.metadata.timings_sec.inference.autoencoder_sec`>

- Comparative Insight:
  - Accuracy/F1 winner: <IF or AE>
  - Performance (speed) winner: <IF or AE>
  - Trade-off: <e.g., “AE improved recall by X with Y× train time vs IF.”>

Optional quick extraction examples:

```bash
jq '.performance_metrics' results/detection_report.json
jq '.results.metadata.timings_sec' results/detection_report.json
```

---

## Alignment With the Codebase

- Data generation and labeling: `src/data/data_loader.py` (`label` column added for injected anomalies).
- Preprocessing/encoding/scaling/label handling and splits: `src/data/preprocessor.py`.
- Models:
  - Isolation Forest: `src/models/isolation_forest.py`
  - Autoencoder: `src/models/autoencoder.py`
  - Ensemble combiner: `src/models/ensemble.py`
- Orchestration, evaluation, visualizations, report: `src/main.py`, `src/utils/metrics.py`, `src/utils/visualization.py`.
