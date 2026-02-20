"""Analysis result and statistics data models."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Any

from .table import Table
from .object import DatabaseObject


@dataclass(frozen=True)
class AnalysisStatistics:
    """Statistical summary of the analysis results.

    Attributes:
        total_tables: Total number of tables analyzed.
        used_tables: Number of tables that are used.
        unused_tables: Number of tables that are unused.
        total_objects: Total number of database objects.
        object_type_distribution: Count of objects by type.
        total_dependencies: Total number of dependencies.
        active_dependencies: Number of active dependencies.
        unused_table_ids: List of IDs for unused tables.
        most_referenced_table: Information about the most referenced table.
    """

    total_tables: int
    used_tables: int
    unused_tables: int
    total_objects: int
    object_type_distribution: Dict[str, int]
    total_dependencies: int
    active_dependencies: int
    unused_table_ids: List[int]
    most_referenced_table: Optional[Dict[str, Any]] = None

    @property
    def usage_percentage(self) -> float:
        """Return percentage of tables that are used."""
        if self.total_tables == 0:
            return 0.0
        return (self.used_tables / self.total_tables) * 100

    @property
    def unused_percentage(self) -> float:
        """Return percentage of tables that are unused."""
        if self.total_tables == 0:
            return 0.0
        return (self.unused_tables / self.total_tables) * 100

    def summary_text(self) -> str:
        """Return formatted summary text."""
        ref_info = ""
        if self.most_referenced_table:
            ref_info = (
                f"\n  Most Referenced Table: {self.most_referenced_table['table_name']} "
                f"({self.most_referenced_table['reference_count']} references)"
            )
        return (f"Analysis Summary:\n"
                f"  Total Tables: {self.total_tables}\n"
                f"  Used Tables: {self.used_tables} ({self.usage_percentage:.1f}%)\n"
                f"  Unused Tables: {self.unused_tables} ({self.unused_percentage:.1f}%)\n"
                f"  Total Objects: {self.total_objects}\n"
                f"  Dependencies: {self.active_dependencies}/{self.total_dependencies} active"
                f"{ref_info}")


@dataclass
class AnalysisResult:
    """Contains the complete results of a dependency analysis.

    Attributes:
        tables: Dictionary of tables by ID.
        objects: Dictionary of database objects by ID.
        statistics: Statistical summary of the analysis.
        processing_time: Time taken to perform the analysis in seconds.
        timestamp: When the analysis was performed.
    """

    tables: Dict[int, Table]
    objects: Dict[int, DatabaseObject]
    statistics: AnalysisStatistics
    processing_time: float
    timestamp: datetime = field(default_factory=datetime.now)

    def get_unused_tables(self) -> List[Table]:
        """Return list of unused tables."""
        return [table for table in self.tables.values() if not table.is_used]

    def get_used_tables(self) -> List[Table]:
        """Return list of used tables."""
        return [table for table in self.tables.values() if table.is_used]

    def get_table_by_name(self, name: str) -> Optional[Table]:
        """Find table by name (case-insensitive)."""
        for table in self.tables.values():
            if table.table_name.lower() == name.lower():
                return table
        return None
