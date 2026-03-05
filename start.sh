#!/bin/bash

# Start the background worker in background
echo "Starting background worker..."
python3 worker.py &

# Start the Flask API in foreground (Render watches this)
echo "Starting Flask API..."
exec gunicorn app:app -b 0.0.0.0:5000