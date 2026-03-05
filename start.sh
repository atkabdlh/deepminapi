#!/bin/bash

# Start the Flask API in background (so the script can continue)
echo "Starting Flask API..."
gunicorn app:app -b 0.0.0.0:5000 &

# Start the background worker
echo "Starting background worker..."
python3 worker.py