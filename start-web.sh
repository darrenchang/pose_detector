#!/bin/bash

set -e

# Set up python venv if not already setup

(
cd ./web/pose-gui/;
echo "Installing packages...";
npm install;
echo "Starting the development server...";
npm run dev;
)
