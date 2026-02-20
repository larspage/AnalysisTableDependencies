#!/bin/bash

# Script to run the database dependency analyzer site locally
# This generates an HTML report and serves it on a local web server

set -e

# Define ports used by the application
HTTP_SERVER_PORT=8000
FLASK_SERVER_PORT=5000

# Function to kill any process running on a specified port
kill_port() {
    local port=$1
    local pid=$(lsof -t -i:$port 2>/dev/null)
    if [ -n "$pid" ]; then
        echo "Killing process on port $port (PID: $pid)"
        kill -9 $pid 2>/dev/null || true
    fi
}

echo "Setting up the database dependency analyzer..."

# Activate virtual environment if it exists
if [ -f "venv/bin/activate" ]; then
    echo "Activating virtual environment..."
    source venv/bin/activate
else
    echo "Error: Virtual environment not found at ./venv/"
    echo "Please create one with: python3 -m venv venv"
    exit 1
fi

# Verify venv is activated
if [[ "$VIRTUAL_ENV" == "" ]]; then
    echo "Error: Failed to activate virtual environment"
    exit 1
fi
echo "Virtual environment active: $VIRTUAL_ENV"

# Install dependencies in development mode if not already installed
if ! python -c "import database_dependency_analyzer" 2>/dev/null; then
    echo "Installing dependencies..."
    pip install -e .
else
    echo "Dependencies already installed."
fi

echo "Generating HTML report..."

# Run the report generator to create report.html
python generate_report.py "$@"

# Check if report.html was created
if [ ! -f "report.html" ]; then
    echo "Error: report.html was not generated. Check for errors above."
    exit 1
fi

echo "HTML report generated successfully."

# Clean up any existing processes on the ports we need
echo "Checking for existing processes on ports..."
kill_port $HTTP_SERVER_PORT
kill_port $FLASK_SERVER_PORT

echo "Starting local web server on port $HTTP_SERVER_PORT..."

# Start a simple HTTP server in background
python -m http.server $HTTP_SERVER_PORT &
SERVER_PID=$!

# Wait a moment for server to start
sleep 1

echo "Site URL: http://localhost:$HTTP_SERVER_PORT/report.html"
echo "Server is running in the background (PID: $SERVER_PID)"
echo "Press Ctrl+C to stop the server"

# Wait for the server process
wait $SERVER_PID