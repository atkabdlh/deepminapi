#!/bin/bash

LOG_FILE="server.log"
VENV_DIR="venv"

# Activate virtual environment
if [ -f "$VENV_DIR/bin/activate" ]; then
    source $VENV_DIR/bin/activate
else
    echo "Virtual environment not found! Please run 'python3 -m venv venv' and install requirements."
    exit 1
fi

# Function to start Flask API
start_flask() {
    if pgrep -f "gunicorn app:app" >/dev/null; then
        echo "Flask API already running!"
    else
        nohup bash -c '
        while true; do
            echo "$(date) - Starting Flask API..."
            gunicorn app:app -b 0.0.0.0:5000 -w 1 --timeout 120 >> '"$LOG_FILE"' 2>&1
            echo "$(date) - Flask API crashed! Restarting in 3s..."
            sleep 3
        done
        ' &
        echo "Flask API loop started."
    fi
}

# Function to start worker
start_worker() {
    if pgrep -f "python3 worker.py" >/dev/null; then
        echo "Worker already running!"
    else
        nohup bash -c '
        while true; do
            echo "$(date) - Starting background worker..."
            python3 worker.py >> '"$LOG_FILE"' 2>&1
            echo "$(date) - Worker crashed! Restarting in 3s..."
            sleep 3
        done
        ' &
        echo "Worker loop started."
    fi
}

# Stop all running processes
stop() {
    echo "Stopping server..."
    pkill -f "gunicorn app:app"
    pkill -f "python3 worker.py"
    echo "Server stopped."
}

# Start everything
start() {
    start_flask
    start_worker
    echo "Server started! Logs: $LOG_FILE"
}

# Restart server
restart() {
    stop
    sleep 1
    start
}

# Status check
status() {
    if pgrep -f "gunicorn app:app" >/dev/null; then
        echo "Flask API is running."
    else
        echo "Flask API is not running."
    fi

    if pgrep -f "python3 worker.py" >/dev/null; then
        echo "Worker is running."
    else
        echo "Worker is not running."
    fi
}

# Tail logs
logs() {
    tail -f $LOG_FILE
}

case "$1" in
    start) start ;;
    stop) stop ;;
    restart) restart ;;
    status) status ;;
    logs) logs ;;
    *) echo "Usage: $0 {start|stop|restart|status|logs}" ;;
esac