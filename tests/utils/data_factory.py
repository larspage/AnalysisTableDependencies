"""
Data Factory for Test Fixtures

This module provides factories for creating test data objects
that can be used across different test scenarios.
"""

from typing import Dict, List, Tuple, Optional
import random
from database_dependency_analyzer.models.table import Table
from database_dependency_analyzer.models.object import DatabaseObject, ObjectReference
from database_dependency_analyzer.models.dependency import TableDependency, ObjectDependency
from database_dependency_analyzer.models.analysis_result import AnalysisResult, AnalysisStatistics


class TableFactory:
    """Factory for creating Table objects."""

    @staticmethod
    def create_table(table_id: int, name: str, is_used: bool = False) -> Table:
        """Create a single table."""
        table = Table(table_id=table_id, table_name=name)
        table.is_used = is_used
        return table

    @staticmethod
    def create_tables(count: int, prefix: str = "Table", start_id: int = 1) -> Dict[int, Table]:
        """Create multiple tables."""
        tables = {}
        for i in range(count):
            table_id = start_id + i
            name = f"{prefix}{table_id}"
            tables[table_id] = TableFactory.create_table(table_id, name)
        return tables

    @staticmethod
    def create_realistic_tables() -> Dict[int, Table]:
        """Create a set of realistic table names."""
        table_names = [
            "Customers", "Orders", "OrderDetails", "Products", "Categories",
            "Suppliers", "Shippers", "Employees", "Territories", "Regions",
            "CustomerCustomerDemo", "CustomerDemographics", "Sales", "Inventory",
            "PurchaseOrders", "Vendors", "Warehouses", "Transactions"
        ]

        tables = {}
        for i, name in enumerate(table_names, 1):
            tables[i] = TableFactory.create_table(i, name)
        return tables


class DatabaseObjectFactory:
    """Factory for creating DatabaseObject instances."""

    OBJECT_TYPES = ["Form", "Query", "Macro", "Report"]

    @staticmethod
    def create_object(object_id: int, name: str, obj_type: str) -> DatabaseObject:
        """Create a single database object."""
        if obj_type not in DatabaseObjectFactory.OBJECT_TYPES:
            raise ValueError(f"Invalid object type: {obj_type}")
        return DatabaseObject(object_id=object_id, object_name=name, object_type=obj_type)

    @staticmethod
    def create_objects(count: int, start_id: int = 100) -> Dict[int, DatabaseObject]:
        """Create multiple database objects with varied types."""
        objects = {}
        for i in range(count):
            object_id = start_id + i
            obj_type = DatabaseObjectFactory.OBJECT_TYPES[i % len(DatabaseObjectFactory.OBJECT_TYPES)]
            name = f"{obj_type}{object_id}"
            objects[object_id] = DatabaseObjectFactory.create_object(object_id, name, obj_type)
        return objects

    @staticmethod
    def create_realistic_objects() -> Dict[int, DatabaseObject]:
        """Create realistic database objects."""
        objects_data = [
            (100, "CustomerForm", "Form"),
            (101, "OrderEntry", "Form"),
            (102, "ProductCatalog", "Form"),
            (103, "CustomerQuery", "Query"),
            (104, "OrderSummary", "Query"),
            (105, "ProductSearch", "Query"),
            (106, "InventoryMacro", "Macro"),
            (107, "DataCleanup", "Macro"),
            (108, "CustomerReport", "Report"),
            (109, "SalesReport", "Report"),
            (110, "InventoryReport", "Report")
        ]

        objects = {}
        for obj_id, name, obj_type in objects_data:
            objects[obj_id] = DatabaseObjectFactory.create_object(obj_id, name, obj_type)
        return objects


class DependencyFactory:
    """Factory for creating dependency objects."""

    @staticmethod
    def create_table_dependency(object_id: int, table_id: int, is_active: bool = True) -> TableDependency:
        """Create a table dependency."""
        return TableDependency(object_id=object_id, table_id=table_id, is_active=is_active)

    @staticmethod
    def create_object_dependency(parent_id: int, child_id: int, is_active: bool = True) -> ObjectDependency:
        """Create an object dependency."""
        return ObjectDependency(parent_object_id=parent_id, child_object_id=child_id, is_active=is_active)

    @staticmethod
    def create_random_dependencies(objects: Dict[int, DatabaseObject],
                                 tables: Dict[int, Table],
                                 dependency_ratio: float = 0.7) -> Tuple[List[TableDependency], List[ObjectDependency]]:
        """Create random dependencies between objects and tables."""
        table_deps = []
        object_deps = []

        object_ids = list(objects.keys())
        table_ids = list(tables.keys())

        # Create table dependencies
        for table_id in table_ids:
            if random.random() < dependency_ratio:
                object_id = random.choice(object_ids)
                is_active = random.choice([True, False])
                table_deps.append(DependencyFactory.create_table_dependency(object_id, table_id, is_active))

        # Create some object dependencies (forms using queries, etc.)
        for _ in range(len(object_ids) // 3):
            parent_id = random.choice(object_ids)
            child_id = random.choice([oid for oid in object_ids if oid != parent_id])
            is_active = random.choice([True, False])
            object_deps.append(DependencyFactory.create_object_dependency(parent_id, child_id, is_active))

        return table_deps, object_deps


class AnalysisResultFactory:
    """Factory for creating AnalysisResult objects."""

    @staticmethod
    def create_empty_result() -> AnalysisResult:
        """Create an empty analysis result."""
        return AnalysisResult()

    @staticmethod
    def create_from_data(tables: Dict[int, Table],
                        objects: Dict[int, DatabaseObject],
                        table_deps: List[TableDependency],
                        object_deps: List[ObjectDependency]) -> AnalysisResult:
        """Create an analysis result from data."""
        result = AnalysisResult()
        result.tables = tables.copy()
        result.objects = objects.copy()
        result.table_dependencies = table_deps.copy()
        result.object_dependencies = object_deps.copy()

        # Mark used tables
        used_table_ids = {dep.table_id for dep in table_deps if dep.is_active}
        for table_id in used_table_ids:
            if table_id in result.tables:
                result.tables[table_id].is_used = True

        # Calculate statistics
        total_tables = len(result.tables)
        used_tables = len([t for t in result.tables.values() if t.is_used])
        result.statistics.total_tables = total_tables
        result.statistics.used_tables = used_tables
        result.statistics.unused_tables = total_tables - used_tables
        result.statistics.total_objects = len(result.objects)

        return result

    @staticmethod
    def create_realistic_result() -> AnalysisResult:
        """Create a realistic analysis result."""
        tables = TableFactory.create_realistic_tables()
        objects = DatabaseObjectFactory.create_realistic_objects()
        table_deps, object_deps = DependencyFactory.create_random_dependencies(objects, tables)

        return AnalysisResultFactory.create_from_data(tables, objects, table_deps, object_deps)


class ObjectReferenceFactory:
    """Factory for creating ObjectReference objects."""

    @staticmethod
    def create_reference(object_id: int, name: str, obj_type: str, is_active: bool = True) -> ObjectReference:
        """Create an object reference."""
        return ObjectReference(object_id=object_id, object_name=name, object_type=obj_type, is_active=is_active)

    @staticmethod
    def create_from_objects(objects: Dict[int, DatabaseObject]) -> List[ObjectReference]:
        """Create object references from database objects."""
        references = []
        for obj in objects.values():
            references.append(ObjectReferenceFactory.create_reference(
                obj.object_id, obj.object_name, obj.object_type, True
            ))
        return references


def create_test_dataset(size: str = "small") -> Tuple[Dict[int, Table], Dict[int, DatabaseObject], List[TableDependency], List[ObjectDependency]]:
    """
    Create a complete test dataset.

    Args:
        size: Size of dataset ("small", "medium", "large")

    Returns:
        Tuple of (tables, objects, table_dependencies, object_dependencies)
    """
    if size == "small":
        tables = TableFactory.create_tables(5)
        objects = DatabaseObjectFactory.create_objects(4, 100)
        table_deps, object_deps = DependencyFactory.create_random_dependencies(objects, tables, 0.6)
    elif size == "medium":
        tables = TableFactory.create_tables(20)
        objects = DatabaseObjectFactory.create_objects(15, 100)
        table_deps, object_deps = DependencyFactory.create_random_dependencies(objects, tables, 0.7)
    elif size == "large":
        tables = TableFactory.create_tables(100)
        objects = DatabaseObjectFactory.create_objects(50, 100)
        table_deps, object_deps = DependencyFactory.create_random_dependencies(objects, tables, 0.8)
    else:
        raise ValueError(f"Unknown size: {size}")

    return tables, objects, table_deps, object_deps


def create_edge_case_dataset(case: str) -> Tuple[Dict[int, Table], Dict[int, DatabaseObject], List[TableDependency], List[ObjectDependency]]:
    """
    Create datasets for edge cases.

    Args:
        case: Type of edge case ("empty", "no_dependencies", "circular_deps", "duplicate_ids")

    Returns:
        Tuple of test data
    """
    if case == "empty":
        return {}, {}, [], []
    elif case == "no_dependencies":
        tables = TableFactory.create_tables(5)
        objects = DatabaseObjectFactory.create_objects(3, 100)
        return tables, objects, [], []
    elif case == "circular_deps":
        # Create circular object dependencies
        objects = DatabaseObjectFactory.create_objects(3, 100)
        object_deps = [
            ObjectDependency(100, 101, True),
            ObjectDependency(101, 102, True),
            ObjectDependency(102, 100, True),  # Creates cycle
        ]
        tables = TableFactory.create_tables(2)
        table_deps = [TableDependency(100, 1, True)]
        return tables, objects, table_deps, object_deps
    elif case == "duplicate_ids":
        # This would normally be invalid, but let's create it for testing
        tables = {1: TableFactory.create_table(1, "Table1")}
        objects = {100: DatabaseObjectFactory.create_object(100, "Object1", "Form")}
        table_deps = [
            TableDependency(100, 1, True),
            TableDependency(100, 1, False),  # Duplicate
        ]
        return tables, objects, table_deps, []
    else:
        raise ValueError(f"Unknown edge case: {case}")