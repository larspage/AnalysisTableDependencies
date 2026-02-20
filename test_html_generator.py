#!/usr/bin/env python3
"""Simple test script for HTML generator."""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from database_dependency_analyzer.generators.html_generator import HTMLGenerator
from database_dependency_analyzer.models.analysis_result import AnalysisResult, AnalysisStatistics
from database_dependency_analyzer.models.table import Table, ObjectReference
from database_dependency_analyzer.models.object import DatabaseObject

def test_html_generator():
    """Test the HTML generator with sample data."""
    print("Testing HTML Generator...")

    # Create sample data
    stats = AnalysisStatistics(
        total_tables=10,
        used_tables=7,
        unused_tables=3,
        total_objects=25,
        objects_by_type={'Form': 10, 'Query': 8, 'Macro': 4, 'Report': 3},
        total_dependencies=45,
        active_dependencies=42
    )

    tables = {
        1: Table(
            table_id=1,
            table_name='Users',
            is_used=True,
            referencing_objects=[
                ObjectReference(1, 'UserForm', 'Form', True),
                ObjectReference(2, 'UserQuery', 'Query', True)
            ]
        ),
        2: Table(
            table_id=2,
            table_name='Products',
            is_used=False,
            referencing_objects=[]
        )
    }

    objects = {
        1: DatabaseObject(1, 'UserForm', 'Form'),
        2: DatabaseObject(2, 'UserQuery', 'Query')
    }

    result = AnalysisResult(
        tables=tables,
        objects=objects,
        statistics=stats,
        processing_time=1.5
    )

    # Generate HTML
    generator = HTMLGenerator(result)
    html = generator.generate_html()

    print(f"✓ HTML generation successful! Length: {len(html)} characters")

    # Basic checks
    assert '<!DOCTYPE html>' in html
    assert 'Database Dependency Analysis Report' in html
    assert 'analysis-data' in html
    assert 'ReportController' in html

    print("✓ Basic HTML structure validated")
    print("✓ Test passed!")

    return html

if __name__ == '__main__':
    html = test_html_generator()
    with open('report.html', 'w', encoding='utf-8') as f:
        f.write(html)
    print(f"HTML report generated and saved to report.html")
    print(f"Report length: {len(html)} characters")
    print(f"Open report.html in your browser to view the interactive report")