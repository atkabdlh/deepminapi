#!/bin/bash

# Activate venv
source venv/bin/activate

# Start background worker
echo "Starting worker..."
nohup python3 worker.py > worker.log 2>&1 &

# Start Flask API via Gunicorn
echo "Starting Flask API..."
gunicorn app:app -b 0.0.0.0:5000 -w 1 --timeout 120