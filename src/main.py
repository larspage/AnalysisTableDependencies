"""Main entry point for the database dependency analyzer CLI."""

import logging
import sys
from pathlib import Path
from typing import Optional

from database_dependency_analyzer.analyzers.dependency_analyzer import DependencyAnalyzer
from database_dependency_analyzer.console import ArgumentParser, OutputFormatter, ProgressTracker
from database_dependency_analyzer.models.analysis_result import AnalysisResult
from database_dependency_analyzer.parsers import (
    ObjectParser,
    TableParser,
    DependencyParser
)

from .config import ConfigManager


def setup_logging(verbose: bool = False) -> None:
    """Setup logging configuration.

    Args:
        verbose: Whether to enable verbose logging.
    """
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stderr)
        ]
    )


def load_data(config, progress_tracker: ProgressTracker) -> tuple:
    """Load and parse all input data.

    Args:
        config: Analysis configuration.
        progress_tracker: Progress tracker instance.

    Returns:
        Tuple of (tables, objects, table_dependencies, object_dependencies).
    """
    logger = logging.getLogger(__name__)

    with progress_tracker.track_operation(4, "Loading data") as progress:
        # Parse tables
        progress_tracker.show_message("Parsing tables...")
        table_parser = TableParser(config)
        tables = table_parser.parse_file(config.tables_file)
        progress.update()

        # Parse objects
        progress_tracker.show_message("Parsing objects...")
        object_parser = ObjectParser(config)
        objects = object_parser.parse_file(config.objects_file)
        progress.update()

        # Parse table dependencies
        progress_tracker.show_message("Parsing table dependencies...")
        table_dep_parser = DependencyParser(config)
        table_dependencies = table_dep_parser.parse_table_dependencies(config.table_dependencies_file)
        progress.update()

        # Parse object dependencies
        progress_tracker.show_message("Parsing object dependencies...")
        object_dep_parser = DependencyParser(config)
        object_dependencies = object_dep_parser.parse_object_dependencies(config.object_dependencies_file)
        progress.update()

    logger.info(f"Loaded {len(tables)} tables, {len(objects)} objects, "
               f"{len(table_dependencies)} table dependencies, "
               f"{len(object_dependencies)} object dependencies")

    return tables, objects, table_dependencies, object_dependencies


def perform_analysis(config, tables: dict, objects: dict,
                    table_dependencies: list, object_dependencies: list,
                    progress_tracker: ProgressTracker) -> AnalysisResult:
    """Perform the dependency analysis.

    Args:
        config: Analysis configuration.
        tables: Dictionary of tables.
        objects: Dictionary of objects.
        table_dependencies: List of table dependencies.
        object_dependencies: List of object dependencies.
        progress_tracker: Progress tracker instance.

    Returns:
        AnalysisResult containing the findings.
    """
    progress_tracker.show_message("Performing dependency analysis...")

    analyzer = DependencyAnalyzer(config)
    result = analyzer.analyze(tables, objects, table_dependencies, object_dependencies)

    progress_tracker.show_message(f"Analysis complete. Found {len(result.unused_tables)} unused tables.")

    return result


def generate_output(config, result: AnalysisResult,
                   output_formatter: OutputFormatter) -> Optional[str]:
    """Generate output based on configuration.

    Args:
        config: Analysis configuration.
        result: Analysis results.
        output_formatter: Output formatter instance.

    Returns:
        HTML output string if generating HTML, None otherwise.
    """
    logger = logging.getLogger(__name__)

    # Console output
    if config.console_output:
        print("\n" + output_formatter.format_summary(result))
        print("\n" + output_formatter.format_unused_tables(result.unused_tables))

        if config.verbose:
            print("\n" + output_formatter.format_statistics(result.statistics))

    # HTML output (placeholder for Phase 3)
    if config.output_file:
        logger.warning("HTML report generation not yet implemented (Phase 3)")
        # Security check: ensure output directory exists and is writable
        try:
            config.output_file.parent.mkdir(parents=True, exist_ok=True)
            # Test write access
            with open(config.output_file, 'w') as f:
                f.write("")
            config.output_file.unlink()  # Remove test file
        except (OSError, PermissionError) as e:
            raise ValueError(f"Cannot write to output file: {config.output_file}") from e

        print(f"\nHTML report generation not yet implemented. Output file: {config.output_file}")

    return None


def setup_components(args) -> tuple:
    """Setup configuration and components.

    Args:
        args: Parsed command line arguments.

    Returns:
        Tuple of (config, progress_tracker, output_formatter).
    """
    # Setup logging
    setup_logging(args.verbose)

    logger = logging.getLogger(__name__)
    logger.info("Starting database dependency analyzer")

    # Load configuration
    config_manager = ConfigManager()
    config = config_manager.load_from_args(args)

    # Setup output components
    progress_tracker = ProgressTracker(enabled=config.console_output, verbose=config.verbose)
    output_formatter = OutputFormatter(verbose=config.verbose)

    return config, progress_tracker, output_formatter


def handle_error(error: Exception, verbose: bool = False) -> int:
    """Handle and display errors.

    Args:
        error: The exception that occurred.
        verbose: Whether to show verbose error details.

    Returns:
        Exit code (always 1 for errors).
    """
    logger = logging.getLogger(__name__)
    logger.error(f"Analysis failed: {error}", exc_info=True)

    # Try to show user-friendly error
    output_formatter = OutputFormatter(verbose=verbose)
    print(output_formatter.format_error(error, verbose=verbose), file=sys.stderr)
    return 1


def main() -> int:
    """Main entry point for the CLI application.

    Returns:
        Exit code (0 for success, 1 for error).
    """
    try:
        # Parse command line arguments
        arg_parser = ArgumentParser()
        args = arg_parser.parse_args()

        # Setup components
        config, progress_tracker, output_formatter = setup_components(args)

        # Load data
        tables, objects, table_dependencies, object_dependencies = load_data(config, progress_tracker)

        # Perform analysis
        result = perform_analysis(config, tables, objects, table_dependencies, object_dependencies, progress_tracker)

        # Generate output
        generate_output(config, result, output_formatter)

        logger = logging.getLogger(__name__)
        logger.info("Analysis completed successfully")
        return 0

    except KeyboardInterrupt:
        print("\nOperation cancelled by user", file=sys.stderr)
        return 1
    except Exception as e:
        return handle_error(e, getattr(args, 'verbose', False) if 'args' in locals() else False)


if __name__ == "__main__":
    sys.exit(main())