#!/bin/bash

# Script to start the Database Dependency Analyzer web interface
# This provides an interactive UI for uploading XML files and viewing analysis results

set -e

echo "Starting Database Dependency Analyzer Web Interface..."

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Check if virtual environment exists and activate it
if [ -f "$SCRIPT_DIR/venv/bin/activate" ]; then
    echo "Activating virtual environment..."
    source "$SCRIPT_DIR/venv/bin/activate"
    echo "Virtual environment active: $VIRTUAL_ENV"
elif [[ "$VIRTUAL_ENV" != "" ]]; then
    echo "Using already activated virtual environment: $VIRTUAL_ENV"
else
    echo "No virtual environment found at $SCRIPT_DIR/venv/"
    echo ""
    echo "Creating virtual environment..."
    python3 -m venv "$SCRIPT_DIR/venv"
    source "$SCRIPT_DIR/venv/bin/activate"
    echo "Virtual environment created and activated: $VIRTUAL_ENV"
fi

# Install dependencies if needed
if ! python -c "import flask" 2>/dev/null; then
    echo "Installing Flask and dependencies..."
    pip install flask werkzeug
fi

# Install the package in development mode if not already installed
if ! python -c "import database_dependency_analyzer" 2>/dev/null; then
    echo "Installing database_dependency_analyzer package..."
    pip install -e "$SCRIPT_DIR"
fi

# Change to src directory for imports
cd "$SCRIPT_DIR/src"

echo ""
echo "Starting Flask development server..."
echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║  Web Interface: http://localhost:5000                      ║"
echo "║  Press Ctrl+C to stop the server                           ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Start Flask app
python -m database_dependency_analyzer.web.app
