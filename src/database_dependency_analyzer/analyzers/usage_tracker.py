"""Usage tracking module for analyzing table reference patterns."""

import logging
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Any


@dataclass
class TableUsageRecord:
    """Record of a single table reference event.
    
    Attributes:
        table_id: Unique identifier for the table.
        table_name: Name of the table.
        object_id: ID of the object that referenced the table.
        object_name: Name of the referencing object.
        object_type: Type of the referencing object.
        reference_type: Type of reference (direct, indirect, transitive).
        timestamp: When the reference was recorded.
    """
    
    table_id: int
    table_name: str
    object_id: int
    object_name: str
    object_type: str
    reference_type: str = "direct"
    timestamp: float = 0.0
    
    VALID_REFERENCE_TYPES = {'direct', 'indirect', 'transitive'}
    
    def __post_init__(self):
        """Validate reference type."""
        if self.reference_type not in self.VALID_REFERENCE_TYPES:
            raise ValueError(f"Invalid reference_type: {self.reference_type}. "
                           f"Must be one of {self.VALID_REFERENCE_TYPES}")


@dataclass
class TableUsageSummary:
    """Summary statistics for table usage.
    
    Attributes:
        table_id: Unique identifier for the table.
        table_name: Name of the table.
        total_references: Total number of references.
        reference_type_counts: Count of references by type.
        referencing_object_types: Types of objects that reference this table.
        referencing_object_ids: IDs of objects that reference this table.
        referencing_object_names: Names of objects that reference this table.
        average_depth: Average dependency depth for references.
        max_depth: Maximum dependency depth for references.
    """
    
    table_id: int
    table_name: str
    total_references: int = 0
    reference_type_counts: Dict[str, int] = field(default_factory=dict)
    referencing_object_types: Dict[str, int] = field(default_factory=dict)
    referencing_object_ids: List[int] = field(default_factory=list)
    referencing_object_names: List[str] = field(default_factory=list)
    average_depth: float = 0.0
    max_depth: int = 0


class UsageTracker:
    """Tracks how tables are referenced by database objects.
    
    This class provides functionality to:
    - Record when a table is referenced by an object
    - Get usage statistics for a table
    - Identify patterns in table usage
    - Analyze reference frequency and types
    """
    
    def __init__(self):
        """Initialize the usage tracker."""
        # Track all reference records
        self._reference_records: List[TableUsageRecord] = []
        
        # Index references by table for quick lookup
        self._table_references: Dict[int, List[TableUsageRecord]] = defaultdict(list)
        
        # Index references by object for quick lookup
        self._object_references: Dict[int, List[TableUsageRecord]] = defaultdict(list)
        
        # Track reference counts over time
        self._reference_counts_by_table: Dict[int, List[tuple]] = defaultdict(list)
        
        # Logger instance
        self._logger = logging.getLogger(__name__)
    
    def record_reference(
        self,
        table_id: int,
        table_name: str,
        object_id: int,
        object_name: str,
        object_type: str,
        reference_type: str = "direct",
        depth: int = 0,
        timestamp: Optional[float] = None
    ) -> TableUsageRecord:
        """Record a table reference by a database object.
        
        Args:
            table_id: Unique identifier for the table.
            table_name: Name of the table.
            object_id: ID of the object that referenced the table.
            object_name: Name of the referencing object.
            object_type: Type of the referencing object.
            reference_type: Type of reference (direct, indirect, transitive).
            depth: Dependency depth for this reference.
            timestamp: Optional timestamp for the reference.
            
        Returns:
            TableUsageRecord representing the recorded reference.
        """
        import time
        if timestamp is None:
            timestamp = time.time()
        
        # Create the reference record
        record = TableUsageRecord(
            table_id=table_id,
            table_name=table_name,
            object_id=object_id,
            object_name=object_name,
            object_type=object_type,
            reference_type=reference_type,
            timestamp=timestamp
        )
        
        # Store the record
        self._reference_records.append(record)
        
        # Index by table
        self._table_references[table_id].append(record)
        
        # Index by object
        self._object_references[object_id].append(record)
        
        # Record count with timestamp for time-series analysis
        self._reference_counts_by_table[table_id].append((timestamp, len(self._table_references[table_id])))
        
        self._logger.debug(
            f"Recorded reference: {object_type}:{object_name} -> {table_name} "
            f"(type={reference_type}, depth={depth})"
        )
        
        return record
    
    def record_references_from_dependency(
        self,
        table_id: int,
        table_name: str,
        referencing_object_ids: List[int],
        referencing_objects: Dict[int, Any],
        reference_type: str = "direct"
    ) -> List[TableUsageRecord]:
        """Record multiple references from object dependencies.
        
        Args:
            table_id: Unique identifier for the table.
            table_name: Name of the table.
            referencing_object_ids: List of object IDs that reference this table.
            referencing_objects: Dictionary mapping object IDs to DatabaseObject instances.
            reference_type: Type of reference for all recorded references.
            
        Returns:
            List of created TableUsageRecord instances.
        """
        records = []
        for obj_id in referencing_object_ids:
            if obj_id in referencing_objects:
                obj = referencing_objects[obj_id]
                record = self.record_reference(
                    table_id=table_id,
                    table_name=table_name,
                    object_id=obj.object_id,
                    object_name=obj.object_name,
                    object_type=obj.object_type,
                    reference_type=reference_type
                )
                records.append(record)
        return records
    
    def get_table_usage_summary(self, table_id: int) -> Optional[TableUsageSummary]:
        """Get usage summary statistics for a specific table.
        
        Args:
            table_id: Unique identifier for the table.
            
        Returns:
            TableUsageSummary with usage statistics, or None if table not found.
        """
        references = self._table_references.get(table_id, [])
        
        if not references:
            return None
        
        # Get table name from first reference (all should have same name)
        table_name = references[0].table_name
        
        # Calculate reference type counts
        reference_type_counts: Dict[str, int] = defaultdict(int)
        referencing_object_types: Dict[str, int] = defaultdict(int)
        referencing_object_ids: Set[int] = set()
        referencing_object_names: Set[str] = set()
        total_depth = 0
        max_depth = 0
        
        for ref in references:
            reference_type_counts[ref.reference_type] += 1
            referencing_object_types[ref.object_type] += 1
            referencing_object_ids.add(ref.object_id)
            referencing_object_names.add(ref.object_name)
        
        return TableUsageSummary(
            table_id=table_id,
            table_name=table_name,
            total_references=len(references),
            reference_type_counts=dict(reference_type_counts),
            referencing_object_types=dict(referencing_object_types),
            referencing_object_ids=sorted(referencing_object_ids),
            referencing_object_names=sorted(referencing_object_names),
            average_depth=total_depth / len(references) if references else 0.0,
            max_depth=max_depth
        )
    
    def get_all_usage_summaries(self) -> Dict[int, TableUsageSummary]:
        """Get usage summaries for all tracked tables.
        
        Returns:
            Dictionary mapping table IDs to their usage summaries.
        """
        summaries = {}
        for table_id in self._table_references:
            summary = self.get_table_usage_summary(table_id)
            if summary:
                summaries[table_id] = summary
        return summaries
    
    def get_most_referenced_tables(self, limit: int = 10) -> List[TableUsageSummary]:
        """Get the most referenced tables.
        
        Args:
            limit: Maximum number of tables to return.
            
        Returns:
            List of TableUsageSummary sorted by total references (descending).
        """
        summaries = list(self.get_all_usage_summaries().values())
        summaries.sort(key=lambda s: s.total_references, reverse=True)
        return summaries[:limit]
    
    def get_least_referenced_tables(self, limit: int = 10) -> List[TableUsageSummary]:
        """Get the least referenced tables.
        
        Args:
            limit: Maximum number of tables to return.
            
        Returns:
            List of TableUsageSummary sorted by total references (ascending).
        """
        summaries = list(self.get_all_usage_summaries().values())
        summaries.sort(key=lambda s: s.total_references)
        return summaries[:limit]
    
    def get_references_by_object(self, object_id: int) -> List[TableUsageRecord]:
        """Get all references made by a specific object.
        
        Args:
            object_id: Unique identifier for the object.
            
        Returns:
            List of TableUsageRecord for all tables referenced by this object.
        """
        return self._object_references.get(object_id, [])
    
    def get_objects_by_type(self, object_type: str) -> Dict[int, List[TableUsageRecord]]:
        """Get all references grouped by object type.
        
        Args:
            object_type: Type of objects to filter (e.g., 'Query', 'Form').
            
        Returns:
            Dictionary mapping object IDs to their reference records.
        """
        result: Dict[int, List[TableUsageRecord]] = defaultdict(list)
        for obj_id, records in self._object_references.items():
            for record in records:
                if record.object_type == object_type:
                    result[obj_id].append(record)
        return result
    
    def get_reference_type_distribution(self) -> Dict[str, int]:
        """Get the distribution of reference types across all tables.
        
        Returns:
            Dictionary mapping reference type to count.
        """
        distribution: Dict[str, int] = defaultdict(int)
        for record in self._reference_records:
            distribution[record.reference_type] += 1
        return dict(distribution)
    
    def get_object_type_dependency_counts(self) -> Dict[str, int]:
        """Get the count of table references by object type.
        
        Returns:
            Dictionary mapping object type to number of references.
        """
        counts: Dict[str, int] = defaultdict(int)
        for record in self._reference_records:
            counts[record.object_type] += 1
        return dict(counts)
    
    def get_usage_patterns(self) -> Dict[str, Any]:
        """Analyze and return usage patterns across all tables.
        
        Returns:
            Dictionary containing various usage patterns and statistics.
        """
        total_references = len(self._reference_records)
        unique_tables = len(self._table_references)
        unique_objects = len(self._object_references)
        
        # Calculate average references per table
        avg_refs_per_table = total_references / unique_tables if unique_tables > 0 else 0
        
        # Find most common reference type
        ref_type_dist = self.get_reference_type_distribution()
        most_common_ref_type = max(ref_type_dist, key=ref_type_dist.get) if ref_type_dist else None
        
        # Find most active object type
        obj_type_counts = self.get_object_type_dependency_counts()
        most_active_object_type = max(obj_type_counts, key=obj_type_counts.get) if obj_type_counts else None
        
        return {
            "total_references": total_references,
            "unique_tables_referenced": unique_tables,
            "unique_referencing_objects": unique_objects,
            "average_references_per_table": avg_refs_per_table,
            "reference_type_distribution": ref_type_dist,
            "most_common_reference_type": most_common_ref_type,
            "object_type_dependency_counts": obj_type_counts,
            "most_active_object_type": most_active_object_type
        }
    
    def get_unused_tables(self, all_table_ids: Set[int]) -> List[int]:
        """Find tables that have no references.
        
        Args:
            all_table_ids: Set of all known table IDs.
            
        Returns:
            List of table IDs that have no references.
        """
        referenced_table_ids = set(self._table_references.keys())
        return sorted(all_table_ids - referenced_table_ids)
    
    def get_frequency_analysis(self) -> Dict[str, Any]:
        """Perform frequency analysis on table references.
        
        Returns:
            Dictionary with frequency analysis results.
        """
        # Count references per table
        table_counts = {
            table_id: len(records) 
            for table_id, records in self._table_references.items()
        }
        
        # Calculate statistics
        counts = list(table_counts.values())
        if not counts:
            return {
                "total_tables": 0,
                "min_references": 0,
                "max_references": 0,
                "average_references": 0,
                "median_references": 0,
                "tables_by_frequency": {}
            }
        
        counts.sort()
        total = sum(counts)
        min_references = counts[0]
        max_references = counts[-1]
        average_references = total / len(counts)
        median_references = counts[len(counts) // 2] if counts else 0
        
        # Group tables by frequency
        tables_by_frequency: Dict[int, List[int]] = defaultdict(list)
        for table_id, count in table_counts.items():
            tables_by_frequency[count].append(table_id)
        
        return {
            "total_tables": len(table_counts),
            "min_references": min_references,
            "max_references": max_references,
            "average_references": average_references,
            "median_references": median_references,
            "tables_by_frequency": dict(tables_by_frequency)
        }
    
    def reset(self) -> None:
        """Clear all tracked usage data."""
        self._reference_records.clear()
        self._table_references.clear()
        self._object_references.clear()
        self._reference_counts_by_table.clear()
        self._logger.info("Usage tracker data cleared")
    
    def get_total_reference_count(self) -> int:
        """Get the total number of recorded references.
        
        Returns:
            Total count of reference records.
        """
        return len(self._reference_records)
    
    def get_tracked_tables_count(self) -> int:
        """Get the number of tables with recorded references.
        
        Returns:
            Count of unique tables with references.
        """
        return len(self._table_references)
    
    def get_tracked_objects_count(self) -> int:
        """Get the number of objects with recorded references.
        
        Returns:
            Count of unique objects with references.
        """
        return len(self._object_references)
    
    def merge(self, other: "UsageTracker") -> None:
        """Merge another UsageTracker into this one.
        
        Args:
            other: Another UsageTracker to merge from.
        """
        # Copy all reference records
        self._reference_records.extend(other._reference_records)
        
        # Rebuild indexes
        for table_id, records in other._table_references.items():
            self._table_references[table_id].extend(records)
        
        for object_id, records in other._object_references.items():
            self._object_references[object_id].extend(records)
        
        for table_id, counts in other._reference_counts_by_table.items():
            self._reference_counts_by_table[table_id].extend(counts)
        
        self._logger.info(f"Merged {other.get_total_reference_count()} references from another tracker")
