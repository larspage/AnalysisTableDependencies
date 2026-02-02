#!/bin/bash

# Script to start the Database Dependency Analyzer web interface
# This provides an interactive UI for uploading XML files and viewing analysis results

set -e

echo "Starting Database Dependency Analyzer Web Interface..."

# Check if virtual environment is activated
if [[ "$VIRTUAL_ENV" != "" ]]; then
    echo "Virtual environment detected: $VIRTUAL_ENV"
else
    echo "Warning: No virtual environment detected. Consider activating one."
fi

# Check if Flask is installed
if ! python -c "import flask" 2>/dev/null; then
    echo "Flask not installed. Installing..."
    pip install flask werkzeug
fi

# Change to src directory for imports
cd src

echo "Starting Flask development server..."
echo ""
echo "Web Interface: http://localhost:5000"
echo "Press Ctrl+C to stop the server"
echo ""

# Start Flask app
python -m database_dependency_analyzer.web.app
