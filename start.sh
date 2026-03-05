#!/bin/bash

# Activate virtual environment
source venv/bin/activate

# Optional: install/update dependencies (uncomment if needed)
pip install -r requirements.txt

# Start Flask API in background
echo "Starting Flask API..."
nohup gunicorn app:app -b 0.0.0.0:5000 > api.log 2>&1 &

# Start background worker in background
echo "Starting background worker..."
nohup python3 worker.py > worker.log 2>&1 &

echo "Server started! Check api.log and worker.log for output."