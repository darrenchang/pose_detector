#!/bin/bash

set -e

# Create .env from the sample if it doesn't exist
if [ ! -f .env ]; then
  echo "No .env found, copying .env.sample to .env..."
  cp .env.sample .env
fi

source .env

RUN_BACKEND=1
RUN_WEB=1

# Parse named arguments
while [[ "$#" -gt 0 ]]; do
    case "$1" in
        --video_source) VIDEO_SOURCE="$2"; shift ;;
        --backend-only) RUN_WEB=0 ;;
        --web-only) RUN_BACKEND=0 ;;
        --help)
            echo "Usage: $0 [--video_source <0|videos/skate.mp4>] [--backend-only | --web-only]"
            echo
            echo "Starts the app backend (port 8000) and the web frontend (port 8080)."
            echo "  --video_source   camera index or video path (relative to app/src)"
            echo "  --backend-only   start only the python backend"
            echo "  --web-only       start only the vite dev server"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
    shift
done

BACKEND_PID=""
WEB_PID=""

set -m

# Stop whichever servers are still running. SIGINT lets the backend launcher
# run its own teardown (workers + redis), and npm forwards it to vite.
cleanup() {
    trap - INT TERM EXIT
    echo
    echo "Shutting down..."
    for pid in $BACKEND_PID $WEB_PID; do
        kill -INT -- -"$pid" 2>/dev/null || true
    done
    wait 2>/dev/null || true
}
trap cleanup INT TERM EXIT

if [ "$RUN_BACKEND" = 1 ]; then
    # Set up python venv if not already setup
    if [ ! -d app/venv ]; then
      echo "Setting up python venv..."
      python3.12 -m venv app/venv;
      source app/venv/bin/activate;
      python -m pip install app/src/.;
    fi

    source app/venv/bin/activate;

    (
    echo "Starting the backend server..."
    cd app/src;
    VIDEO_SOURCE=${VIDEO_SOURCE} \
    python launcher.py;
    ) &
    BACKEND_PID=$!
fi

if [ "$RUN_WEB" = 1 ]; then
    (
    cd ./web/pose-gui/;
    echo "Installing web packages...";
    npm install;
    echo "Starting the web development server...";
    npm run dev;
    ) &
    WEB_PID=$!
fi

while :; do
    for pid in $BACKEND_PID $WEB_PID; do
        kill -0 "$pid" 2>/dev/null || exit 0
    done
    sleep 1
done
