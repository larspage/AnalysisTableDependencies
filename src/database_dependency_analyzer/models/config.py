"""Analysis configuration data model."""

import argparse
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass
class AnalysisConfig:
    """Configuration for the dependency analysis.

    Attributes:
        tables_file: Path to the tables XML file.
        objects_file: Path to the objects XML file.
        table_dependencies_file: Path to the table dependencies XML file.
        object_dependencies_file: Path to the object dependencies XML file.
        output_file: Optional path for output file.
        console_output: Whether to output to console.
        verbose: Whether to enable verbose logging.
        ignore_inactive_dependencies: Whether to ignore inactive dependencies.
        max_workers: Maximum number of worker threads.
        memory_limit_mb: Memory limit in MB.
    """

    # Input files
    tables_file: Path
    objects_file: Path
    table_dependencies_file: Path
    object_dependencies_file: Path

    # Output options
    output_file: Optional[Path] = None
    console_output: bool = True
    verbose: bool = False

    # Processing options
    ignore_inactive_dependencies: bool = True
    max_workers: int = 4
    memory_limit_mb: int = 512

    def __post_init__(self):
        """Validate configuration."""
        required_files = [
            self.tables_file,
            self.objects_file,
            self.table_dependencies_file,
            self.object_dependencies_file
        ]

        for file_path in required_files:
            if not file_path.exists():
                raise FileNotFoundError(f"Required file not found: {file_path}")

        if self.output_file and self.output_file.exists():
            if not self.output_file.is_file():
                raise ValueError(f"Output path is not a file: {self.output_file}")

    @classmethod
    def from_args(cls, args: argparse.Namespace) -> 'AnalysisConfig':
        """Create config from command line arguments."""
        return cls(
            tables_file=Path(args.tables_file),
            objects_file=Path(args.objects_file),
            table_dependencies_file=Path(args.table_dependencies_file),
            object_dependencies_file=Path(args.object_dependencies_file),
            output_file=Path(args.output) if args.output else None,
            console_output=not args.quiet,
            verbose=args.verbose,
            ignore_inactive_dependencies=not args.include_inactive,
            max_workers=args.max_workers,
            memory_limit_mb=args.memory_limit
        )