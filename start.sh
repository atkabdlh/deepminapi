#!/bin/bash

# Start background worker
echo "Starting background worker..."
python3 worker.py &

# Start Flask API in foreground, replace shell process
echo "Starting Flask API..."
exec gunicorn app:app -b 0.0.0.0:$PORT