"""Statistics calculator for dependency analysis."""

from dataclasses import dataclass
from typing import Dict, List, Optional, Any, Union

from database_dependency_analyzer.models.table import Table
from database_dependency_analyzer.models.object import DatabaseObject
from database_dependency_analyzer.models.dependency import TableDependency, ObjectDependency
from database_dependency_analyzer.models.analysis_result import AnalysisStatistics


@dataclass
class TableReferenceInfo:
    """Info about a table's references for statistics."""

    table_id: int
    table_name: str
    reference_count: int


class StatisticsCalculator:
    """Calculate statistics from analysis data."""

    def calculate(
        self,
        tables: Dict[int, Table],
        objects: Dict[int, DatabaseObject],
        dependencies: List[Union[TableDependency, ObjectDependency]]
    ) -> AnalysisStatistics:
        """Calculate all statistics from analysis data.

        Args:
            tables: Dictionary of tables by ID.
            objects: Dictionary of database objects by ID.
            dependencies: List of dependencies (TableDependency or ObjectDependency).

        Returns:
            AnalysisStatistics with calculated values.
        """
        # Calculate counts
        total_tables = len(tables)
        used_tables = sum(1 for t in tables.values() if t.is_used)
        unused_tables = total_tables - used_tables

        # Get unused table IDs
        unused_table_ids = [t.table_id for t in tables.values() if not t.is_used]

        # Calculate object type distribution
        object_type_distribution: Dict[str, int] = {}
        for obj in objects.values():
            obj_type = obj.object_type
            object_type_distribution[obj_type] = object_type_distribution.get(obj_type, 0) + 1

        total_objects = len(objects)

        # Find most referenced table
        most_referenced: Optional[TableReferenceInfo] = None
        max_refs = 0
        for table in tables.values():
            ref_count = len(table.referencing_objects)
            if ref_count > max_refs:
                max_refs = ref_count
                most_referenced = TableReferenceInfo(
                    table_id=table.table_id,
                    table_name=table.table_name,
                    reference_count=ref_count
                )

        most_referenced_table = None
        if most_referenced:
            most_referenced_table = {
                "table_id": most_referenced.table_id,
                "table_name": most_referenced.table_name,
                "reference_count": most_referenced.reference_count
            }

        # Calculate dependencies
        total_dependencies = len(dependencies)
        active_dependencies = sum(1 for d in dependencies if d.active)

        return AnalysisStatistics(
            total_tables=total_tables,
            used_tables=used_tables,
            unused_tables=unused_tables,
            total_objects=total_objects,
            unused_table_ids=unused_table_ids,
            most_referenced_table=most_referenced_table,
            object_type_distribution=object_type_distribution,
            total_dependencies=total_dependencies,
            active_dependencies=active_dependencies
        )
