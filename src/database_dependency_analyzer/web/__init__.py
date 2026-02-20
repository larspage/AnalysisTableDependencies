"""
Web interface module for Database Dependency Analyzer.

Provides Flask-based web interface for:
- Uploading XML files for analysis
- Viewing dependency diagrams
- Exploring analysis results
"""

from .app import app, create_app, run_server

__all__ = ['app', 'create_app', 'run_server']
