#!/bin/bash

# Script to run all tests for the AnalysisTableDependencies project
# This script ensures tests are run in the WSL environment with python3

echo "Starting test execution..."

# Check if we're in WSL environment
if grep -q Microsoft /proc/version; then
    echo "Running in WSL environment"
else
    echo "Warning: Not running in WSL environment"
fi

# Activate virtual environment
if [ -f "venv/bin/activate" ]; then
    echo "Activating virtual environment..."
    source venv/bin/activate
fi

# Run pytest with verbose output and coverage
python3 -m pytest tests/ -v --tb=short

# Check exit status
exit_status=$?

if [ $exit_status -eq 0 ]; then
    echo "All tests passed successfully!"
else
    echo "Some tests failed with exit code: $exit_status"
fi

exit $exit_status