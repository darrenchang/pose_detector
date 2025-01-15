#!/bin/bash

set -e

VIDEO_SOURCE=0

# Parse named arguments
while [[ "$#" -gt 0 ]]; do
    case "$1" in
        --video_source) VIDEO_SOURCE="$2"; shift ;;
        --help)
            echo "Usage: $0 [--video_source <0|videos/skate.mp4>]"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
    shift
done

# Set up python venv if not already setup
if [ ! -d app/venv ]; then
  echo "Setting up python venv..."
  python3 -m venv app/venv;
  source app/venv/bin/activate;
  python -m pip install app/.;
fi

source app/venv/bin/activate;
(
echo "Starting the server..."
cd app;
VIDEO_SOURCE=${VIDEO_SOURCE} \
gunicorn -c config.py app_main:app;
)
