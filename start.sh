#!/bin/bash

set -e

# Set up python venv if not already setup
if [ ! -d app/venv ]; then
  echo "Setting up python venv..."
  python3 -m venv app/venv;
  source app/venv/bin/activate;
  python -m pip install app/.;
fi

(
echo "Starting the server..."
cd app;
gunicorn -c config.py app_main:app;
)
