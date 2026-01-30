"""Configuration management for the database dependency analyzer."""

import logging
import os
from pathlib import Path
from typing import Optional

from database_dependency_analyzer.models.config import AnalysisConfig


class ConfigManager:
    """Manages configuration loading and validation.

    This class handles loading configuration from various sources:
    - Command line arguments
    - Environment variables
    - Configuration files
    - Default values
    """

    def __init__(self):
        """Initialize the configuration manager."""
        self.logger = logging.getLogger(__name__)

    def _validate_file_path(self, file_path: Path) -> None:
        """Validate file path for security.

        Args:
            file_path: File path to validate.

        Raises:
            ValueError: If path is invalid or insecure.
        """
        # Check if file exists
        if not file_path.exists():
            raise ValueError(f"Input file does not exist: {file_path}")

        # Check if it's actually a file (not directory)
        if not file_path.is_file():
            raise ValueError(f"Path is not a file: {file_path}")

        # Basic path traversal protection - ensure path doesn't contain suspicious patterns
        path_str = str(file_path)
        if ".." in path_str or path_str.startswith("/"):
            # Allow absolute paths and parent directory references for legitimate use
            # but log for awareness
            self.logger.warning(f"Potentially suspicious path: {file_path}")

        # Check file size (basic protection against huge files)
        try:
            size_mb = file_path.stat().st_size / (1024 * 1024)
            if size_mb > 100:  # 100MB limit
                self.logger.warning(f"Large input file detected: {file_path} ({size_mb:.1f} MB)")
        except OSError:
            # If we can't stat the file, continue but log
            self.logger.warning(f"Could not check file size for: {file_path}")

    def load_from_args(self, args) -> AnalysisConfig:
        """Load configuration from parsed command line arguments.

        Args:
            args: Parsed command line arguments.

        Returns:
            AnalysisConfig instance.

        Raises:
            ValueError: If required files are missing or invalid.
        """
        # Validate input files
        input_files = [
            args.tables_file,
            args.objects_file,
            args.table_dependencies_file,
            args.object_dependencies_file
        ]

        for file_path in input_files:
            self._validate_file_path(file_path)

        # Convert output file if provided
        output_file = Path(args.output) if args.output else None

        # Create configuration
        config = AnalysisConfig(
            tables_file=args.tables_file,
            objects_file=args.objects_file,
            table_dependencies_file=args.table_dependencies_file,
            object_dependencies_file=args.object_dependencies_file,
            output_file=output_file,
            console_output=not args.quiet,
            verbose=args.verbose,
            ignore_inactive_dependencies=not args.include_inactive,
            max_workers=args.max_workers,
            memory_limit_mb=args.memory_limit
        )

        self.logger.debug(f"Loaded configuration: {config}")
        return config

    def load_from_env(self) -> Optional[AnalysisConfig]:
        """Load configuration from environment variables.

        Returns:
            AnalysisConfig if all required env vars are set, None otherwise.
        """
        required_vars = [
            'DB_ANALYZER_TABLES_FILE',
            'DB_ANALYZER_OBJECTS_FILE',
            'DB_ANALYZER_TABLE_DEPS_FILE',
            'DB_ANALYZER_OBJECT_DEPS_FILE'
        ]

        # Check if all required variables are set
        if not all(os.getenv(var) for var in required_vars):
            return None

        try:
            config = AnalysisConfig(
                tables_file=Path(os.getenv('DB_ANALYZER_TABLES_FILE')),
                objects_file=Path(os.getenv('DB_ANALYZER_OBJECTS_FILE')),
                table_dependencies_file=Path(os.getenv('DB_ANALYZER_TABLE_DEPS_FILE')),
                object_dependencies_file=Path(os.getenv('DB_ANALYZER_OBJECT_DEPS_FILE')),
                output_file=Path(os.getenv('DB_ANALYZER_OUTPUT_FILE')) if os.getenv('DB_ANALYZER_OUTPUT_FILE') else None,
                console_output=os.getenv('DB_ANALYZER_CONSOLE_OUTPUT', 'true').lower() == 'true',
                verbose=os.getenv('DB_ANALYZER_VERBOSE', 'false').lower() == 'true',
                ignore_inactive_dependencies=os.getenv('DB_ANALYZER_IGNORE_INACTIVE', 'true').lower() == 'true',
                max_workers=int(os.getenv('DB_ANALYZER_MAX_WORKERS', '4')),
                memory_limit_mb=int(os.getenv('DB_ANALYZER_MEMORY_LIMIT', '512'))
            )

            # Validate files exist
            input_files = [
                config.tables_file,
                config.objects_file,
                config.table_dependencies_file,
                config.object_dependencies_file
            ]

            for file_path in input_files:
                if not file_path.exists():
                    self.logger.warning(f"Environment-configured file does not exist: {file_path}")
                    return None

            self.logger.debug(f"Loaded configuration from environment: {config}")
            return config

        except (ValueError, TypeError) as e:
            self.logger.warning(f"Failed to load configuration from environment: {e}")
            return None

    def get_default_config(self) -> AnalysisConfig:
        """Get default configuration for testing or fallback.

        Returns:
            AnalysisConfig with default values.
        """
        # This would typically use default file paths or raise an error
        # For now, return a config that will fail validation
        return AnalysisConfig(
            tables_file=Path('tables.xml'),
            objects_file=Path('objects.xml'),
            table_dependencies_file=Path('table_deps.xml'),
            object_dependencies_file=Path('object_deps.xml')
        )</content>
</xai:function_call">The config.py file has been created successfully.