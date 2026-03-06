# Face Attendance API Deployment & Troubleshooting Guide

## Overview

This document summarizes the setup, deployment, and troubleshooting
steps for the Face Attendance API using: - Flask - Gunicorn - DeepFace -
TensorFlow (CPU) - DigitalOcean / Render servers

It also includes logging, worker management, and memory monitoring
guidance.

------------------------------------------------------------------------

# 1. Server Architecture

The system runs two main processes:

### API Server

Handles HTTP requests.

**Technology** - Flask - Gunicorn

**Responsibilities** - Receive image - Generate embeddings - Match
students - Register students - Manage job queue

### Worker

Handles background processing.

**Responsibilities** - Process registration jobs - Generate embeddings -
Update students database

------------------------------------------------------------------------

# 2. Recommended Folder Structure

    deepminapi/
    │
    ├── app.py
    ├── worker.py
    ├── start.sh
    ├── requirements.txt
    │
    ├── services/
    │   ├── embedding_service.py
    │   ├── matching_service.py
    │   └── student_service.py
    │
    ├── temp_jobs/
    │
    ├── students.json
    └── server.log

------------------------------------------------------------------------

# 3. Python Virtual Environment

Create environment

    python3 -m venv venv

Activate

    source venv/bin/activate

Install dependencies

    pip install -r requirements.txt

Recreate environment if broken

    rm -rf venv
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt

------------------------------------------------------------------------

# 4. Recommended requirements.txt

    deepface==0.0.99
    tensorflow-cpu==2.13.0
    numpy>=1.22,<1.25
    scipy==1.11.2
    opencv-python-headless==4.9.0.80
    Pillow==11.3.0
    python-dotenv==1.2.1
    gunicorn==23.0.0

Reason: TensorFlow 2.13 requires numpy \<1.25.

------------------------------------------------------------------------

# 5. Running the Server

Use start script:

    ./start.sh start

Stop server

    ./start.sh stop

Restart server

    ./start.sh restart

Check status

    ./start.sh status

View logs

    ./start.sh logs

------------------------------------------------------------------------

# 6. Example start.sh

    #!/bin/bash

    LOG_FILE="server.log"
    VENV_DIR="venv"

    source $VENV_DIR/bin/activate

    start_flask() {
        if pgrep -f "gunicorn app:app" >/dev/null; then
            echo "Flask already running"
        else
            nohup gunicorn app:app -b 0.0.0.0:5000 -w 1 --timeout 120 >> $LOG_FILE 2>&1 &
        fi
    }

    start_worker() {
        if pgrep -f "python3 worker.py" >/dev/null; then
            echo "Worker already running"
        else
            nohup python3 -u worker.py >> $LOG_FILE 2>&1 &
        fi
    }

    case "$1" in
        start)
            start_flask
            start_worker
            ;;
        stop)
            pkill -f "gunicorn app:app"
            pkill -f "python3 worker.py"
            ;;
        restart)
            pkill -f "gunicorn app:app"
            pkill -f "python3 worker.py"
            sleep 2
            start_flask
            start_worker
            ;;
        logs)
            tail -f $LOG_FILE
            ;;
        *)
            echo "Usage: ./start.sh {start|stop|restart|logs}"
            ;;
    esac

------------------------------------------------------------------------

# 7. Logging Strategy

All processes write to:

    server.log

View logs:

    tail -f server.log

Worker prints require unbuffered mode:

    python3 -u worker.py

------------------------------------------------------------------------

# 8. Common Gunicorn Errors

### Address already in use

    Connection in use: ('0.0.0.0', 5000)

Fix:

    lsof -i :5000
    kill -9 PID

or

    pkill -f gunicorn

------------------------------------------------------------------------

# 9. Worker Timeout

Example log

    WORKER TIMEOUT
    Worker was sent SIGKILL

Causes

-   Request took too long
-   Server ran out of RAM

Fix

Increase timeout

    gunicorn --timeout 120

Reduce workers

    -w 1

------------------------------------------------------------------------

# 10. Out of Memory (OOM)

Example

    Worker was sent SIGKILL! Perhaps out of memory

Typical DeepFace memory usage

  Stage          RAM
  -------------- --------
  Idle           200MB
  Model loaded   700MB
  Embedding      900MB+

If server has **1GB RAM**, crashes are likely.

Solutions

-   Use 1 gunicorn worker
-   Use tensorflow-cpu
-   Upgrade server RAM

------------------------------------------------------------------------

# 11. Security Logs

Example

    Invalid HTTP request line
    Invalid request from IP

Cause

Bots scanning internet ports.

Not dangerous if:

-   Endpoint requires valid request
-   Server is not exposing sensitive commands

------------------------------------------------------------------------

# 12. Monitoring Processes

Show python processes

    ps aux | grep python

Show gunicorn

    ps aux | grep gunicorn

Kill all gunicorn

    pkill -f gunicorn

Kill worker

    pkill -f worker.py

------------------------------------------------------------------------

# 13. Monitoring RAM Usage

Show memory usage

    top

Better view

    htop

Watch specific process

    watch -n 1 ps -o pid,%mem,rss,command -p <PID>

RSS shows RAM used.

------------------------------------------------------------------------

# 14. Running Locally for Testing

Clone repo

    git clone <repo>
    cd deepminapi

Create environment

    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt

Run worker

    python worker.py

Monitor RAM in another terminal.

------------------------------------------------------------------------

# 15. Deployment Platforms

### DigitalOcean

Manual server management

Pros - Full control - Cheaper

Cons - Need manual logs - Need process management

### Render

Managed platform

Pros - Built-in logs - Automatic restart

Cons - Less control

------------------------------------------------------------------------

# 16. Troubleshooting Checklist

If API fails

1.  Check logs

```{=html}
<!-- -->
```
    tail -f server.log

2.  Verify processes

```{=html}
<!-- -->
```
    ps aux | grep gunicorn
    ps aux | grep worker

3.  Restart server

```{=html}
<!-- -->
```
    ./start.sh restart

4.  Check RAM

```{=html}
<!-- -->
```
    top

------------------------------------------------------------------------

# 17. Health Check Endpoint

    GET /health

Response

    {
     "status": "ok",
     "service": "face-attendance-api"
    }

Useful for uptime monitoring.

------------------------------------------------------------------------

# 18. Important Lessons Learned

-   TensorFlow loads models lazily
-   First embedding uses most RAM
-   Gunicorn workers multiply memory usage
-   Background workers should run separately
-   Logging is essential for debugging

------------------------------------------------------------------------

# 19. Future Improvements

Recommended upgrades

-   Use Redis queue instead of temp files
-   Add request logging middleware
-   Add rate limiting
-   Add monitoring (Prometheus / Grafana)
-   Containerize using Docker

------------------------------------------------------------------------

# End of Documentation
