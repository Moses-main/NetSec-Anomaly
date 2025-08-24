#!/usr/bin/env python3
"""
Simple Flask server to expose detection results and images for the frontend,
and handle dataset uploads to run the detection pipeline.
"""
from flask import Flask, jsonify, send_from_directory, abort, request
from pathlib import Path
import json
from werkzeug.utils import secure_filename

# Import the pipeline orchestrator robustly (supports `python src/server.py` and `python -m src.server`)
try:  # when running as a package module
    from .main import NetworkAnomalyDetectionSystem  # type: ignore
except Exception:  # when running as a script
    try:
        from src.main import NetworkAnomalyDetectionSystem  # type: ignore
    except Exception:
        # Fallback: modify sys.path to include project root
        import sys as _sys
        _sys.path.append(str(Path(__file__).resolve().parent.parent))
        from src.main import NetworkAnomalyDetectionSystem  # type: ignore

app = Flask(__name__)

BASE_DIR = Path(__file__).resolve().parent.parent
RESULTS_DIR = BASE_DIR / "results"
UPLOADS_DIR = RESULTS_DIR / "uploads"
ALLOWED_EXT = {"csv", "json"}
LOG_FILE = BASE_DIR / "logs" / "detector.log"


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.get("/api/report")
def get_report():
    report_path = RESULTS_DIR / "detection_report.json"
    if not report_path.exists():
        return jsonify({"error": "detection_report.json not found", "path": str(report_path)}), 404
    with open(report_path, "r") as f:
        data = json.load(f)
    return jsonify(data)


@app.get("/api/images")
def list_images():
    if not RESULTS_DIR.exists():
        return jsonify([])
    files = []
    for p in RESULTS_DIR.iterdir():
        if p.suffix.lower() in {".png", ".jpg", ".jpeg", ".webp"}:
            files.append(p.name)
    return jsonify(files)


@app.get("/api/logs")
def get_logs():
    """Return recent log lines from logs/detector.log. Query params: tail (int)."""
    tail = request.args.get("tail", default=200, type=int)
    tail = max(1, min(tail, 5000))  # clamp
    if not LOG_FILE.exists():
        return jsonify({"lines": [], "message": f"Log file not found at {str(LOG_FILE)}"})
    try:
        # Read last N lines efficiently
        lines = LOG_FILE.read_text(encoding="utf-8", errors="ignore").splitlines()
        lines = lines[-tail:]
        return jsonify({
            "lines": lines,
            "path": str(LOG_FILE),
            "count": len(lines)
        })
    except Exception as e:
        return jsonify({"error": f"Failed to read logs: {e}"}), 500


@app.post("/api/upload")
def upload_and_run():
    """Accept a dataset file, run the pipeline, and return the latest report & images."""
    if "file" not in request.files:
        return jsonify({"error": "No file part in request. Use form field 'file'."}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No selected file."}), 400

    filename = secure_filename(file.filename)
    ext = filename.rsplit('.', 1)[-1].lower() if '.' in filename else ''
    if ext not in ALLOWED_EXT:
        return jsonify({"error": f"Unsupported file type: .{ext}. Allowed: {sorted(ALLOWED_EXT)}"}), 400

    # Ensure directories exist
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    UPLOADS_DIR.mkdir(parents=True, exist_ok=True)

    save_path = UPLOADS_DIR / filename
    file.save(save_path)

    # Run the pipeline on the uploaded file, writing outputs into RESULTS_DIR
    system = NetworkAnomalyDetectionSystem()
    try:
        outcome = system.run_full_pipeline(data_path=str(save_path), output_dir=str(RESULTS_DIR))
    except Exception as e:
        return jsonify({"error": f"Pipeline failed: {e}"}), 500

    # Compose response: report JSON and images list
    report_path = RESULTS_DIR / "detection_report.json"
    report = {}
    if report_path.exists():
        with open(report_path, "r") as f:
            report = json.load(f)

    images = []
    for p in RESULTS_DIR.iterdir():
        if p.suffix.lower() in {".png", ".jpg", ".jpeg", ".webp"}:
            images.append(p.name)

    return jsonify({
        "message": "Upload processed successfully",
        "filename": filename,
        "report": report,
        "images": images,
    })


@app.get("/results/<path:filename>")
def serve_result_file(filename: str):
    safe_path = RESULTS_DIR / filename
    if not safe_path.exists():
        abort(404)
    # Serve images (and allow other static assets if needed)
    return send_from_directory(RESULTS_DIR, filename)


if __name__ == "__main__":
    # Prefer a production WSGI server if available
    try:
        from waitress import serve as _serve
        # Run on localhost:5000 by default
        _serve(app, host="127.0.0.1", port=5000)
    except Exception:
        # Fallback to Flask's built-in server
        app.run(host="127.0.0.1", port=5000, debug=False, use_reloader=False, threaded=True)
