"""Database dependency analysis module.

This module provides functionality for analyzing Microsoft Access database
dependencies from XML export files. It can identify unused tables and generate
comprehensive HTML reports.

Classes:
    DependencyAnalyzer: Core analysis engine
    AnalysisResult: Container for analysis results
    AnalysisStatistics: Statistical summary of analysis
"""

__version__ = "0.1.0"
__author__ = "Database Dependency Analyzer Team"
__description__ = "Analyze Microsoft Access database dependencies"

# Import main classes and functions for easy access
from .analyzers import DependencyAnalyzer
from .models import AnalysisResult, AnalysisStatistics

__all__ = [
    "DependencyAnalyzer",
    "AnalysisResult",
    "AnalysisStatistics",
    "__version__",
    "__author__",
    "__description__",
]