#!/bin/bash

set -e

# Set up python venv if not already setup
if [ ! -d app/venv ]; then
  python3 -m venv app/venv;
  source app/venv/bin/activate;
  python -m pip install app/.;
fi

(
cd app;
gunicorn -c config.py app_main:app;
)
