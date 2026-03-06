#!/bin/bash

LOG_FILE="server.log"
VENV_DIR="venv"
MIN_MEM_MB=200   # minimum free memory required to start worker/API

# Activate virtual environment
source $VENV_DIR/bin/activate

check_memory() {
    local free_mem=$(free -m | awk '/^Mem:/{print $7}') # available memory in MB
    if [ "$free_mem" -lt "$MIN_MEM_MB" ]; then
        echo "$(date) - Not enough free memory ($free_mem MB). Waiting 5s..."
        sleep 5
        return 1
    fi
    return 0
}

# -----------------------------
# Start Flask API
# -----------------------------
start_flask() {
    if pgrep -f "gunicorn app:app" >/dev/null; then
        echo "Flask API already running!"
    else
        nohup bash -c '
        while true; do
            '"check_memory"' || continue
            echo "$(date) - Starting Flask API..."
            gunicorn app:app -b 0.0.0.0:5000 -w 1 --threads 2 --timeout 180 >> '"$LOG_FILE"' 2>&1
            echo "$(date) - Flask API crashed or killed! Restarting in 5s..."
            sleep 5
        done
        ' &
        echo "Flask API loop started."
    fi
}

# -----------------------------
# Start background worker
# -----------------------------
start_worker() {
    if pgrep -f "python3 worker.py" >/dev/null; then
        echo "Worker already running!"
    else
        nohup bash -c '
        while true; do
            '"check_memory"' || continue
            echo "$(date) - Starting worker..."
            python3 worker.py >> '"$LOG_FILE"' 2>&1
            echo "$(date) - Worker crashed or killed! Restarting in 5s..."
            sleep 5
        done
        ' &
        echo "Worker loop started."
    fi
}

# -----------------------------
# Server control functions
# -----------------------------
start() {
    start_flask
    start_worker
    echo "Server started! Logs in $LOG_FILE"
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