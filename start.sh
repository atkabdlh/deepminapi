#!/bin/bash

LOG_FILE="server.log"
VENV_DIR="venv"

# Activate virtual environment
source $VENV_DIR/bin/activate

start_flask() {
    # Check if Flask API is already running
    if pgrep -f "gunicorn app:app" >/dev/null; then
        echo "Flask API already running!"
    else
        nohup bash -c '
        while true; do
            echo "$(date) - Starting Flask API..."
            gunicorn app:app -b 0.0.0.0:5000 >> '"$LOG_FILE"' 2>&1
            echo "$(date) - Flask API crashed! Restarting in 3s..."
            sleep 3
        done
        ' &
        echo "Flask API loop started."
    fi
}

start_worker() {
    # Check if worker is already running
    if pgrep -f "python3 worker.py" >/dev/null; then
        echo "Worker already running!"
    else
        nohup bash -c '
        while true; do
            echo "$(date) - Starting worker..."
            python3 worker.py >> '"$LOG_FILE"' 2>&1
            echo "$(date) - Worker crashed! Restarting in 3s..."
            sleep 3
        done
        ' &
        echo "Worker loop started."
    fi
}

start() {
    start_flask
    start_worker
    echo "Server started! Logs: $LOG_FILE"
}

stop() {
    echo "Stopping server..."
    pkill -f "gunicorn app:app"
    pkill -f "python3 worker.py"
    echo "Server stopped."
}

restart() {
    stop
    sleep 1
    start
}

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