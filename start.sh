#!/bin/bash

LOG_FILE="server.log"
VENV_DIR="venv"

# Activate virtual environment
source $VENV_DIR/bin/activate

start() {
    if pgrep -f "gunicorn app:app" >/dev/null || pgrep -f "python3 worker.py" >/dev/null; then
        echo "Server is already running!"
        exit 1
    fi

    echo "Starting Flask API and worker..."
    nohup bash -c "gunicorn app:app -b 0.0.0.0:5000 & python3 worker.py" > $LOG_FILE 2>&1 &
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
    if pgrep -f "gunicorn app:app" >/dev/null || pgrep -f "python3 worker.py" >/dev/null; then
        echo "Server is running."
    else
        echo "Server is not running."
    fi
}

logs() {
    tail -f $LOG_FILE
}

# Main
case "$1" in
    start)
        start
        ;;
    stop)
        stop
        ;;
    restart)
        restart
        ;;
    status)
        status
        ;;
    logs)
        logs
        ;;
    *)
        echo "Usage: $0 {start|stop|restart|status|logs}"
        exit 1
        ;;
esac