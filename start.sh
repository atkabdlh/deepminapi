#!/bin/bash
# start.sh

# Start Flask app on port 5000 in background
export FLASK_APP=app.py
export FLASK_ENV=production
flask run --host=0.0.0.0 --port=5000 &

# Start worker in the foreground
python worker.py