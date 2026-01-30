#!/usr/bin/env python3
"""Script to generate HTML report from XML data."""

import sys
import os
import argparse
from pathlib import Path

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from database_dependency_analyzer.analyzers.dependency_analyzer import DependencyAnalyzer
from database_dependency_analyzer.generators.html_generator import HTMLGenerator
from database_dependency_analyzer.parsers import (
    ObjectParser,
    TableParser,
    DependencyParser
)
from database_dependency_analyzer.models.config import AnalysisConfig as Config
from database_dependency_analyzer.console.progress_tracker import ProgressTracker

def generate_report(tables_file=None, objects_file=None, table_deps_file=None, object_deps_file=None):
    """Generate HTML report from XML files."""
    if tables_file and objects_file and table_deps_file and object_deps_file:
        print("Generating HTML report from provided XML files...")
        config = Config(
            tables_file=Path(tables_file),
            objects_file=Path(objects_file),
            table_dependencies_file=Path(table_deps_file),
            object_dependencies_file=Path(object_deps_file),
            console_output=False,
            verbose=False
        )
    else:
        print("Generating HTML report from sample data...")
        # Use sample XML files
        sample_dir = Path("SampleXMLFiles")
        config = Config(
            tables_file=sample_dir / "Analysis_Tables.xml",
            objects_file=sample_dir / "Analysis_Objects.xml",
            table_dependencies_file=sample_dir / "Analysis_TableDependencies.xml",
            object_dependencies_file=sample_dir / "Analysis_ObjectDependencies.xml",
            console_output=False,
            verbose=False
        )

    progress_tracker = ProgressTracker(enabled=False, verbose=False)

    # Load data (similar to main.py)
    with progress_tracker.track_operation(4, "Loading data"):
        table_parser = TableParser(config)
        tables = table_parser.parse(config.tables_file)
        progress_tracker.update()

        object_parser = ObjectParser(config)
        objects = object_parser.parse(config.objects_file)
        progress_tracker.update()

        table_dep_parser = DependencyParser(config)
        table_dependencies = table_dep_parser.parse_table_dependencies(config.table_dependencies_file)
        progress_tracker.update()

        object_dep_parser = DependencyParser(config)
        object_dependencies = object_dep_parser.parse_object_dependencies(config.object_dependencies_file)
        progress_tracker.update()

    print(f"Loaded {len(tables)} tables, {len(objects)} objects")

    # Perform analysis
    analyzer = DependencyAnalyzer(config)
    result = analyzer.analyze(tables, objects, table_dependencies, object_dependencies)

    print(f"Analysis complete. Found {len(result.get_unused_tables())} unused tables.")

    # Generate HTML
    generator = HTMLGenerator(result)
    html = generator.generate_html()

    # Save to file
    with open('report.html', 'w', encoding='utf-8') as f:
        f.write(html)

    print(f"HTML report generated and saved to report.html")
    print(f"Report length: {len(html)} characters")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Generate HTML report from database dependency XML files',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s  # Use sample files
  %(prog)s tables.xml objects.xml table_deps.xml object_deps.xml
        """
    )
    parser.add_argument(
        'tables_file',
        nargs='?',
        help='Path to the Analysis_Tables.xml file (optional, uses sample if not provided)'
    )
    parser.add_argument(
        'objects_file',
        nargs='?',
        help='Path to the Analysis_Objects.xml file (optional, uses sample if not provided)'
    )
    parser.add_argument(
        'table_dependencies_file',
        nargs='?',
        help='Path to the Analysis_TableDependencies.xml file (optional, uses sample if not provided)'
    )
    parser.add_argument(
        'object_dependencies_file',
        nargs='?',
        help='Path to the Analysis_ObjectDependencies.xml file (optional, uses sample if not provided)'
    )

    args = parser.parse_args()

    # Check if all files are provided or none
    files = [args.tables_file, args.objects_file, args.table_dependencies_file, args.object_dependencies_file]
    if any(files) and not all(files):
        parser.error("Either provide all four XML files or none to use sample files")

    generate_report(args.tables_file, args.objects_file, args.table_dependencies_file, args.object_dependencies_file)