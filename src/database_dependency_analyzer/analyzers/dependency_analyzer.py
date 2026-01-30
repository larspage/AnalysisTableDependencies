"""Dependency analyzer for identifying unused database tables."""

import logging
import time
from collections import defaultdict
from typing import Dict, List, Set

from ..models.analysis_result import AnalysisResult, AnalysisStatistics
from ..models.config import AnalysisConfig
from ..models.dependency import TableDependency, ObjectDependency
from ..models.object import DatabaseObject
from ..models.table import Table, ObjectReference


class DependencyAnalyzer:
    """Analyzes database dependencies to identify unused tables.
    
    This class implements the core business logic for determining which tables
    are used by database objects and which can be considered unused.
    """
    
    def __init__(self, config: AnalysisConfig):
        """Initialize the dependency analyzer.
        
        Args:
            config: Analysis configuration.
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
    
    def analyze(self, tables: Dict[int, Table], 
                objects: Dict[int, DatabaseObject], 
                table_dependencies: List[TableDependency], 
                object_dependencies: List[ObjectDependency]) -> AnalysisResult:
        """Perform dependency analysis and return results.
        
        Args:
            tables: Dictionary of tables by ID
            objects: Dictionary of database objects by ID
            table_dependencies: List of table dependency relationships
            object_dependencies: List of object dependency relationships
            
        Returns:
            AnalysisResult containing the complete analysis findings
        """
        start_time = time.time()
        self.logger.info("Starting dependency analysis")
        
        # Step 1: Build dependency graph
        self.logger.debug("Building dependency graph")
        dependency_graph = self._build_dependency_graph(
            tables, objects, table_dependencies, object_dependencies
        )
        
        # Step 2: Mark used tables
        self.logger.debug("Marking used tables")
        self._mark_used_tables(dependency_graph)
        
        # Step 3: Calculate statistics
        self.logger.debug("Calculating statistics")
        statistics = self._calculate_statistics(dependency_graph)
        
        # Step 4: Generate results
        processing_time = time.time() - start_time
        result = AnalysisResult(
            tables=dependency_graph['tables'],
            objects=dependency_graph['objects'],
            statistics=statistics,
            processing_time=processing_time
        )
        
        self.logger.info(f"Analysis completed in {processing_time:.3f} seconds")
        self.logger.info(f"Found {statistics.unused_tables} unused tables out of {statistics.total_tables}")
        
        return result
    
    def _build_dependency_graph(self, tables: Dict[int, Table], 
                               objects: Dict[int, DatabaseObject], 
                               table_dependencies: List[TableDependency], 
                               object_dependencies: List[ObjectDependency]) -> Dict:
        """Build a comprehensive dependency graph.
        
        Args:
            tables: Dictionary of tables by ID
            objects: Dictionary of database objects by ID
            table_dependencies: List of table dependency relationships
            object_dependencies: List of object dependency relationships
            
        Returns:
            Dictionary containing the dependency graph with:
            - 'tables': Updated tables with references
            - 'objects': All objects
            - 'object_deps': Object-to-object dependencies
            - 'active_table_deps': Active table dependencies by table ID
        """
        # Create working copies to avoid modifying originals
        tables_copy = {table_id: table for table_id, table in tables.items()}
        objects_copy = {obj_id: obj for obj_id, obj in objects.items()}
        
        # Filter active dependencies
        active_table_deps = [
            dep for dep in table_dependencies if dep.active
        ]
        active_object_deps = [
            dep for dep in object_dependencies if dep.active
        ]
        
        # Build object-to-table mapping
        object_to_tables: Dict[int, List[int]] = defaultdict(list)
        for dep in active_table_deps:
            object_to_tables[dep.object_id].append(dep.table_id)
        
        # Build object-to-object mapping
        object_to_objects: Dict[int, List[int]] = defaultdict(list)
        for dep in active_object_deps:
            object_to_objects[dep.source_object_id].append(dep.target_object_id)
        
        # Build table-to-objects mapping for quick lookup
        table_to_objects: Dict[int, List[int]] = defaultdict(list)
        for dep in active_table_deps:
            table_to_objects[dep.table_id].append(dep.object_id)
        
        # Add references to tables
        for table_id, referencing_object_ids in table_to_objects.items():
            if table_id in tables_copy:
                table = tables_copy[table_id]
                for obj_id in referencing_object_ids:
                    if obj_id in objects_copy:
                        obj = objects_copy[obj_id]
                        ref = ObjectReference(
                            object_id=obj.object_id,
                            object_name=obj.object_name,
                            object_type=obj.object_type,
                            active=True
                        )
                        # Create new table instance with updated references
                        new_table = Table(
                            table_id=table.table_id,
                            table_name=table.table_name,
                            is_used=table.is_used,
                            referencing_objects=table.referencing_objects + [ref]
                        )
                        tables_copy[table_id] = new_table
        
        return {
            'tables': tables_copy,
            'objects': objects_copy,
            'object_deps': object_to_objects,
            'active_table_deps': active_table_deps
        }
    
    def _mark_used_tables(self, dependency_graph: Dict) -> None:
        """Mark tables as used based on dependencies.
        
        Args:
            dependency_graph: Dependency graph from _build_dependency_graph
        """
        tables = dependency_graph['tables']
        object_deps = dependency_graph['object_deps']
        active_table_deps = dependency_graph['active_table_deps']
        
        # Step 1: Mark tables with direct active dependencies
        directly_used_table_ids = {dep.table_id for dep in active_table_deps}
        
        # Step 2: Handle transitive dependencies through object chains
        indirectly_used_table_ids = self._find_indirectly_used_tables(
            directly_used_table_ids, object_deps, active_table_deps
        )
        
        # Step 3: Mark all used tables
        all_used_table_ids = directly_used_table_ids | indirectly_used_table_ids
        
        for table_id, table in tables.items():
            if table_id in all_used_table_ids:
                if not table.is_used:
                    # Create new table instance with updated usage status
                    new_table = Table(
                        table_id=table.table_id,
                        table_name=table.table_name,
                        is_used=True,
                        referencing_objects=table.referencing_objects
                    )
                    tables[table_id] = new_table
    
    def _find_indirectly_used_tables(self, directly_used_table_ids: Set[int], 
                                    object_deps: Dict[int, List[int]], 
                                    active_table_deps: List[TableDependency]) -> Set[int]:
        """Find tables that are used indirectly through object dependency chains.
        
        Args:
            directly_used_table_ids: IDs of tables with direct dependencies
            object_deps: Object-to-object dependency mapping
            active_table_deps: Active table dependencies
            
        Returns:
            Set of table IDs that are used indirectly
        """
        indirectly_used = set()
        
        # Build object-to-table mapping for quick lookup
        object_to_tables = defaultdict(set)
        for dep in active_table_deps:
            object_to_tables[dep.object_id].add(dep.table_id)
        
        # For each object that references a directly used table,
        # find all objects that depend on it (transitively)
        visited_objects = set()
        
        # Find objects that directly reference used tables
        seed_objects = set()
        for dep in active_table_deps:
            if dep.table_id in directly_used_table_ids:
                seed_objects.add(dep.object_id)
        
        # Perform BFS to find all objects in dependency chains
        queue = list(seed_objects)
        
        while queue:
            current_obj_id = queue.pop(0)
            if current_obj_id in visited_objects:
                continue
            
            visited_objects.add(current_obj_id)
            
            # Add tables referenced by this object
            indirectly_used.update(object_to_tables.get(current_obj_id, set()))
            
            # Add objects that depend on this object
            for dependent_obj_id in object_deps.get(current_obj_id, []):
                if dependent_obj_id not in visited_objects:
                    queue.append(dependent_obj_id)
        
        # Remove directly used tables from the result
        return indirectly_used - directly_used_table_ids
    
    def _calculate_statistics(self, dependency_graph: Dict) -> AnalysisStatistics:
        """Calculate analysis statistics.
        
        Args:
            dependency_graph: Dependency graph from _build_dependency_graph
            
        Returns:
            AnalysisStatistics object with computed metrics
        """
        tables = dependency_graph['tables']
        objects = dependency_graph['objects']
        active_table_deps = dependency_graph['active_table_deps']
        
        total_tables = len(tables)
        used_tables = sum(1 for table in tables.values() if table.is_used)
        unused_tables = total_tables - used_tables
        
        total_objects = len(objects)
        object_type_distribution: Dict[str, int] = {}
        for obj in objects.values():
            obj_type = obj.object_type
            object_type_distribution[obj_type] = object_type_distribution.get(obj_type, 0) + 1
        
        # Get unused table IDs
        unused_table_ids = [table.table_id for table in tables.values() if not table.is_used]
        
        # Find most referenced table
        most_referenced_table = None
        max_refs = 0
        for table in tables.values():
            ref_count = len(table.referencing_objects)
            if ref_count > max_refs:
                max_refs = ref_count
                most_referenced_table = {
                    "table_id": table.table_id,
                    "table_name": table.table_name,
                    "reference_count": ref_count
                }
        
        total_dependencies = len(active_table_deps)
        active_dependencies = len(active_table_deps)
        
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