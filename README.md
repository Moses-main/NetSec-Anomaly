# Network Anomaly Detection System

Identifies suspicious network traffic patterns using unsupervised learning.

- Models: Isolation Forest, Autoencoder (Ensemble)
- Stack: Python (scikit-learn, TensorFlow/Keras, Flask), React (Vite, Tailwind CSS)

---

create a virtual environment and install the required packages

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Quick Start (one command)

Run both backend and frontend together with the helper script:

```bash
chmod +x start.sh
./start.sh
```

What it does:

- Generates results if missing (runs the pipeline once)
- Starts Flask API on http://127.0.0.1:5000
- Installs frontend deps (first run) and starts Vite on http://127.0.0.1:5173
- Cleans up the backend on exit

Then open the app at http://127.0.0.1:5173.

## Prerequisites

- Python 3.9+
- Node.js 18+ and npm

## 1) Backend setup

Install Python dependencies (preferably in a venv):

```bash
pip install -r requirements.txt
```

Generate results (report + images). You can run on sample data:

```bash
python src/main.py --mode full
```

Or run on your dataset (CSV or JSON with expected columns):

```bash
python src/main.py --mode full --data path/to/your_data.csv
```

This will produce:

- `results/detection_report.json`
- `results/if_scores.png`, `results/ae_errors.png`, `results/detection_comparison.png`

Start the API server (serves report and images):

```bash
python src/server.py
```

API endpoints:

- `GET /api/health`
- `GET /api/report`
- `GET /api/images`
- `POST /api/upload` (multipart/form-data: field `file`) — upload CSV/JSON, run pipeline, return report and images
- `GET /results/<filename>`

## 2) Frontend setup (Vite + React + Tailwind)

In a separate terminal:

```bash
cd frontend
npm install
npm run dev
```

Visit the dashboard at:

- http://127.0.0.1:5173

The dev server proxies `/api/*` and `/results/*` to the Flask backend at `http://127.0.0.1:5000`.

### Upload and test via the UI

- Navigate to the "Upload" page in the top navigation.
- Choose a CSV or JSON with the expected columns (see schema below).
- Click "Upload & Run" to process; results and charts will display and are also available on the Dashboard.
- A sample dataset is provided at `samples/sample_dataset.csv`.

Build for production:

```bash
npm run build
```

## Expected dataset schema

Supported formats: CSV (`.csv`), JSON (`.json`).

Columns used (rename/map if your dataset differs):

- Numeric: `duration`, `src_bytes`, `dst_bytes`, `count`, `srv_count`
- Categorical: `protocol` (tcp/udp/icmp), `service` (http/ftp/telnet/smtp/dns), `flag` (SF/S0/REJ/RSTR)

Example column mapping snippet:

```python
import pandas as pd

df = pd.read_csv("path/to/your_dataset.csv")
df = df.rename(columns={
    "duration_sec": "duration",
    "srcBytes": "src_bytes",
    "dstBytes": "dst_bytes",
    "conn_count": "count",
    "service_count": "srv_count",
    "proto": "protocol",
    "svc": "service",
    "tcp_flag": "flag",
})
for c in ["protocol", "service", "flag"]:
    if c in df.columns:
        df[c] = df[c].astype(str)
df.to_csv("data/your_data_mapped.csv", index=False)
```

Then run:

```bash
python src/main.py --mode full --data data/your_data_mapped.csv
```

Or upload your file through the UI ("Upload" page) or via curl:

```bash
curl -F "file=@samples/sample_dataset.csv" http://127.0.0.1:5000/api/upload
```

## Troubleshooting

- Frontend blank or report missing: ensure you've run `python src/main.py --mode full` and that `src/server.py` is running.
- Test backend:
  - `curl http://127.0.0.1:5000/api/health`
  - `curl http://127.0.0.1:5000/api/report`
- If running across network/containers, bind Flask to `0.0.0.0` in `src/server.py`.
- TypeScript type errors: in `frontend/` install types with `npm i -D @types/react @types/react-dom`.

## Project structure

```
.
├── src/
│   ├── main.py                  # Orchestrates pipeline
│   ├── server.py                # Flask API (report/images)
│   ├── data/                    # Loading & preprocessing
│   ├── models/                  # IF, AE, Ensemble
│   └── utils/                   # Metrics, visualization
├── results/                     # Generated report & plots
├── frontend/                    # Vite + React + Tailwind UI
└── requirements.txt
```

## Security and Git hygiene

Sensitive/large artifacts are ignored via `./.gitignore` (models, logs, results, env files, node_modules, etc.).
