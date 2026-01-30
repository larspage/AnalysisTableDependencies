"""Console output formatting for analysis results."""

import logging
from typing import Dict, List

from ..models.analysis_result import AnalysisResult, AnalysisStatistics
from ..models.table import Table


class OutputFormatter:
    """Formats analysis results for console output.

    This class provides methods to format analysis results in a human-readable
    format suitable for console display, including tables, statistics, and summaries.
    """

    def __init__(self, verbose: bool = False):
        """Initialize the output formatter.

        Args:
            verbose: Whether to enable verbose output.
        """
        self.verbose = verbose
        self.logger = logging.getLogger(__name__)

    def _calculate_table_stats(self, result: AnalysisResult) -> tuple:
        """Calculate table statistics.

        Args:
            result: The analysis result.

        Returns:
            Tuple of (total_tables, used_tables, unused_tables, unused_percentage).
        """
        total_tables = len(result.tables)
        unused_tables = result.get_unused_tables()
        used_tables = result.get_used_tables()
        unused_percentage = len(unused_tables) / total_tables * 100 if total_tables > 0 else 0

        return total_tables, len(used_tables), len(unused_tables), unused_percentage

    def _format_basic_stats(self, total_tables: int, used_tables: int,
                           unused_tables: int, unused_percentage: float) -> list:
        """Format basic table statistics.

        Args:
            total_tables: Total number of tables.
            used_tables: Number of used tables.
            unused_tables: Number of unused tables.
            unused_percentage: Percentage of unused tables.

        Returns:
            List of formatted lines.
        """
        lines = []
        lines.append("Database Dependency Analysis Summary")
        lines.append("=" * 40)
        lines.append(f"Total tables analyzed: {total_tables}")
        lines.append(f"Used tables: {used_tables}")
        lines.append(f"Unused tables: {unused_tables}")
        lines.append(f"Unused percentage: {unused_percentage:.1f}%" if total_tables > 0 else "Unused percentage: N/A")

        return lines

    def _format_statistics_section(self, stats: AnalysisStatistics) -> list:
        """Format the statistics section.

        Args:
            stats: Analysis statistics.

        Returns:
            List of formatted lines.
        """
        lines = []
        lines.append("")
        lines.append("Statistics:")
        lines.append(f"  Total dependencies: {stats.total_dependencies}")
        lines.append(f"  Active dependencies: {stats.active_dependencies}")

        return lines

    def format_summary(self, result: AnalysisResult) -> str:
        """Format a summary of the analysis results.

        Args:
            result: The analysis result to format.

        Returns:
            Formatted summary string.
        """
        total_tables, used_tables, unused_tables, unused_percentage = self._calculate_table_stats(result)

        lines = self._format_basic_stats(total_tables, used_tables, unused_tables, unused_percentage)

        if result.statistics:
            lines.extend(self._format_statistics_section(result.statistics))

        return "\n".join(lines)

    def format_unused_tables(self, unused_tables: List[Table]) -> str:
        """Format the list of unused tables.

        Args:
            unused_tables: List of unused tables to format.

        Returns:
            Formatted table string.
        """
        if not unused_tables:
            return "No unused tables found."

        lines = []
        lines.append("Unused Tables")
        lines.append("-" * 50)
        lines.append(f"{'ID':<8} {'Name':<30} {'Type':<10}")
        lines.append("-" * 50)

        for table in sorted(unused_tables, key=lambda t: t.table_name):
            table_type = getattr(table, 'table_type', 'Unknown')
            lines.append(f"{table.table_id:<8} {table.table_name:<30} {table_type:<10}")

        lines.append("-" * 50)
        lines.append(f"Total: {len(unused_tables)} unused tables")

        return "\n".join(lines)

    def format_table_details(self, table: Table) -> str:
        """Format detailed information about a specific table.

        Args:
            table: The table to format details for.

        Returns:
            Formatted table details string.
        """
        lines = []
        lines.append(f"Table Details: {table.table_name}")
        lines.append("-" * (15 + len(table.table_name)))

        lines.append(f"ID: {table.table_id}")
        lines.append(f"Name: {table.table_name}")
        lines.append(f"Type: {getattr(table, 'table_type', 'Unknown')}")
        lines.append(f"Description: {getattr(table, 'description', 'N/A')}")

        if hasattr(table, 'attributes') and table.attributes:
            lines.append("Attributes:")
            for key, value in table.attributes.items():
                lines.append(f"  {key}: {value}")

        if table.referencing_objects:
            lines.append("References:")
            for ref in table.referencing_objects:
                lines.append(f"  - {ref.object_name} ({ref.object_type})")

        return "\n".join(lines)

    def format_statistics(self, stats: AnalysisStatistics) -> str:
        """Format analysis statistics.

        Args:
            stats: The statistics to format.

        Returns:
            Formatted statistics string.
        """
        lines = []
        lines.append("Analysis Statistics")
        lines.append("-" * 20)

        lines.append(f"Total dependencies analyzed: {stats.total_dependencies}")
        lines.append(f"Active dependencies: {stats.active_dependencies}")

        return "\n".join(lines)

    def format_error(self, error: Exception, verbose: bool = False) -> str:
        """Format an error message for console output.

        Args:
            error: The exception to format.
            verbose: Whether to include stack trace.

        Returns:
            Formatted error string.
        """
        lines = []
        lines.append("Error occurred during analysis:")
        lines.append(f"  {type(error).__name__}: {error}")

        if verbose:
            import traceback
            lines.append("")
            lines.append("Stack trace:")
            lines.extend(traceback.format_exception(type(error), error, error.__traceback__))

        return "\n".join(lines)

    def format_progress(self, current: int, total: int, message: str = "") -> str:
        """Format a progress message.

        Args:
            current: Current progress value.
            total: Total progress value.
            message: Optional progress message.

        Returns:
            Formatted progress string.
        """
        percentage = (current / total * 100) if total > 0 else 0
        progress_bar = self._create_progress_bar(current, total)

        parts = [f"[{progress_bar}] {percentage:.1f}%"]
        if message:
            parts.append(message)

        return " ".join(parts)

    def _create_progress_bar(self, current: int, total: int, width: int = 20) -> str:
        """Create a simple text-based progress bar.

        Args:
            current: Current progress value.
            total: Total progress value.
            width: Width of the progress bar.

        Returns:
            Progress bar string.
        """
        if total == 0:
            return "=" * width

        filled = int(width * current / total)
        bar = "=" * filled + " " * (width - filled)
        return f"[{bar}]"