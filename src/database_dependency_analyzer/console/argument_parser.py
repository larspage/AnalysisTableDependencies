"""Command-line argument parsing for the database dependency analyzer."""

import argparse
from pathlib import Path
from typing import Any


class ArgumentParser:
    """Handles command-line argument parsing for the analyzer.

    This class provides a clean interface for parsing command-line arguments
    and converting them to a format suitable for configuration management.
    """

    def __init__(self):
        """Initialize the argument parser."""
        self.parser = self._create_parser()

    def _create_parser(self) -> argparse.ArgumentParser:
        """Create and configure the argument parser.

        Returns:
            Configured ArgumentParser instance.
        """
        parser = argparse.ArgumentParser(
            prog='db-analyzer',
            description='Analyze Microsoft Access database dependencies to identify unused tables',
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Examples:
  %(prog)s tables.xml objects.xml table_deps.xml object_deps.xml
  %(prog)s -o report.html -v tables.xml objects.xml table_deps.xml object_deps.xml
  %(prog)s --max-workers 8 --memory-limit 1024 tables.xml objects.xml table_deps.xml object_deps.xml
            """
        )

        # Required positional arguments
        parser.add_argument(
            'tables_file',
            type=Path,
            help='Path to the Analysis_Tables.xml file'
        )

        parser.add_argument(
            'objects_file',
            type=Path,
            help='Path to the Analysis_Objects.xml file'
        )

        parser.add_argument(
            'table_dependencies_file',
            type=Path,
            help='Path to the Analysis_TableDependencies.xml file'
        )

        parser.add_argument(
            'object_dependencies_file',
            type=Path,
            help='Path to the Analysis_ObjectDependencies.xml file'
        )

        # Output options
        parser.add_argument(
            '-o', '--output',
            type=Path,
            help='Output HTML report file (default: stdout)'
        )

        # Console output options
        parser.add_argument(
            '-q', '--quiet',
            action='store_true',
            help='Suppress console output'
        )

        parser.add_argument(
            '-v', '--verbose',
            action='store_true',
            help='Enable verbose logging'
        )

        # Processing options
        parser.add_argument(
            '--include-inactive',
            action='store_true',
            help='Include inactive dependencies in analysis'
        )

        parser.add_argument(
            '--max-workers',
            type=int,
            default=4,
            help='Maximum number of worker threads (default: 4)'
        )

        parser.add_argument(
            '--memory-limit',
            type=int,
            default=512,
            help='Memory limit in MB (default: 512)'
        )

        return parser

    def parse_args(self, args: list[str] = None) -> Any:
        """Parse command-line arguments.

        Args:
            args: List of arguments to parse (default: sys.argv)

        Returns:
            Parsed arguments namespace.
        """
        return self.parser.parse_args(args)

    def print_help(self) -> None:
        """Print help message."""
        self.parser.print_help()

    def print_usage(self) -> None:
        """Print usage message."""
        self.parser.print_usage()