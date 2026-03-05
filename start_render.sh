#!/bin/bash

# Start Flask API in background
echo "Starting Flask API..."
gunicorn app:app -b 0.0.0.0:$PORT &

# Start background worker in background
echo "Starting background worker..."
python3 worker.py &

# Wait so the shell doesn’t exit
wait