#!/bin/bash

echo "PORT IS: $PORT"

echo "Starting background worker..."
python3 worker.py &

echo "Starting Flask API..."
exec gunicorn --bind 0.0.0.0:$PORT app:app