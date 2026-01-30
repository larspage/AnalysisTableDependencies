#!/bin/bash

# Script to run the database dependency analyzer site locally
# This generates an HTML report and serves it on a local web server

set -e

echo "Setting up the database dependency analyzer..."

# Check if virtual environment is activated
if [[ "$VIRTUAL_ENV" != "" ]]; then
    echo "Virtual environment detected: $VIRTUAL_ENV"
else
    echo "Warning: No virtual environment detected. Consider activating one."
fi

# Install dependencies in development mode
echo "Installing dependencies..."
pip install -e .

echo "Generating HTML report..."

# Run the report generator to create report.html
python generate_report.py "$@"

# Check if report.html was created
if [ ! -f "report.html" ]; then
    echo "Error: report.html was not generated. Check for errors above."
    exit 1
fi

echo "HTML report generated successfully."

echo "Starting local web server on port 8000..."

# Start a simple HTTP server in background
python -m http.server 8000 &
SERVER_PID=$!

# Wait a moment for server to start
sleep 1

echo "Site URL: http://localhost:8000/report.html"
echo "Server is running in the background (PID: $SERVER_PID)"
echo "Press Ctrl+C to stop the server"

# Wait for the server process
wait $SERVER_PID