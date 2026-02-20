"""Unit tests for the DependencyAnalyzer class."""

import pytest
from datetime import datetime
from unittest.mock import Mock

from src.database_dependency_analyzer.analyzers.dependency_analyzer import DependencyAnalyzer
from src.database_dependency_analyzer.models.analysis_result import AnalysisResult, AnalysisStatistics
from database_dependency_analyzer.models.config import AnalysisConfig
from tests.conftest import analysis_config as conftest_analysis_config
from src.database_dependency_analyzer.models.dependency import TableDependency, ObjectDependency
from src.database_dependency_analyzer.models.object import DatabaseObject
from src.database_dependency_analyzer.models.table import Table, ObjectReference


class TestDependencyAnalyzer:
    """Test suite for DependencyAnalyzer class."""
    
    @pytest.fixture
    def config(self, tmp_path):
        """Create a mock configuration for testing."""
        # Create dummy XML files
        (tmp_path / "tables.xml").write_text("<xml></xml>")
        (tmp_path / "objects.xml").write_text("<xml></xml>")
        (tmp_path / "table_deps.xml").write_text("<xml></xml>")
        (tmp_path / "object_deps.xml").write_text("<xml></xml>")

        return AnalysisConfig(
            tables_file=tmp_path / "tables.xml",
            objects_file=tmp_path / "objects.xml",
            table_dependencies_file=tmp_path / "table_deps.xml",
            object_dependencies_file=tmp_path / "object_deps.xml",
            output_file=tmp_path / "report.html"
        )
    
    @pytest.fixture
    def analyzer(self, config):
        """Create a DependencyAnalyzer instance for testing."""
        return DependencyAnalyzer(config)
    
    @pytest.fixture
    def sample_tables(self):
        """Create sample tables for testing."""
        return {
            1: Table(table_id=1, table_name="Customers", is_used=False),
            2: Table(table_id=2, table_name="Orders", is_used=False),
            3: Table(table_id=3, table_name="Products", is_used=False),
            4: Table(table_id=4, table_name="UnusedTable", is_used=False)
        }
    
    @pytest.fixture
    def sample_objects(self):
        """Create sample database objects for testing."""
        return {
            100: DatabaseObject(object_id=100, object_name="CustomerForm", object_type="Form"),
            101: DatabaseObject(object_id=101, object_name="OrderQuery", object_type="Query"),
            102: DatabaseObject(object_id=102, object_name="ProductReport", object_type="Report"),
            103: DatabaseObject(object_id=103, object_name="MainForm", object_type="Form")
        }
    
    @pytest.fixture
    def sample_table_dependencies(self):
        """Create sample table dependencies for testing."""
        return [
            TableDependency(object_id=100, table_id=1, active=True),  # CustomerForm -> Customers
            TableDependency(object_id=101, table_id=2, active=True),  # OrderQuery -> Orders
            TableDependency(object_id=102, table_id=3, active=True),  # ProductReport -> Products
            TableDependency(object_id=101, table_id=1, active=True),  # OrderQuery -> Customers (secondary)
        ]
    
    @pytest.fixture
    def sample_object_dependencies(self):
        """Create sample object dependencies for testing."""
        return [
            ObjectDependency(source_object_id=103, target_object_id=100, active=True),  # MainForm -> CustomerForm
            ObjectDependency(source_object_id=103, target_object_id=101, active=True),  # MainForm -> OrderQuery
        ]
    
    def test_analyze_basic_functionality(self, analyzer, sample_tables, sample_objects, 
                                        sample_table_dependencies, sample_object_dependencies):
        """Test basic analysis functionality."""
        result = analyzer.analyze(
            tables=sample_tables,
            objects=sample_objects,
            table_dependencies=sample_table_dependencies,
            object_dependencies=sample_object_dependencies
        )
        
        # Verify result structure
        assert isinstance(result, AnalysisResult)
        assert isinstance(result.statistics, AnalysisStatistics)
        assert result.processing_time > 0
        assert isinstance(result.timestamp, datetime)
        
        # Verify statistics
        assert result.statistics.total_tables == 4
        assert result.statistics.used_tables == 3  # Customers, Orders, Products
        assert result.statistics.unused_tables == 1  # UnusedTable
        assert result.statistics.total_objects == 4
        assert result.statistics.total_dependencies == 4
        assert result.statistics.active_dependencies == 4
    
    def test_direct_dependencies(self, analyzer, sample_tables, sample_objects, 
                                sample_table_dependencies, sample_object_dependencies):
        """Test direct table dependencies are correctly identified."""
        result = analyzer.analyze(
            tables=sample_tables,
            objects=sample_objects,
            table_dependencies=sample_table_dependencies,
            object_dependencies=sample_object_dependencies
        )
        
        # Check that directly referenced tables are marked as used
        customers = result.tables[1]
        orders = result.tables[2]
        products = result.tables[3]
        
        assert customers.is_used
        assert orders.is_used
        assert products.is_used
        
        # Check that OrderQuery is in Customers' references
        customer_refs = [ref.object_name for ref in customers.referencing_objects]
        assert "OrderQuery" in customer_refs
    
    def test_transitive_dependencies(self, analyzer, sample_tables, sample_objects, 
                                   sample_table_dependencies, sample_object_dependencies):
        """Test transitive dependencies through object chains."""
        result = analyzer.analyze(
            tables=sample_tables,
            objects=sample_objects,
            table_dependencies=sample_table_dependencies,
            object_dependencies=sample_object_dependencies
        )
        
        # MainForm depends on CustomerForm and OrderQuery
        # CustomerForm depends on Customers table
        # OrderQuery depends on Orders and Customers tables
        # So MainForm indirectly depends on Customers and Orders tables
        
        # All tables referenced directly or indirectly should be used
        assert result.tables[1].is_used  # Customers
        assert result.tables[2].is_used  # Orders
        assert result.tables[3].is_used  # Products
        assert not result.tables[4].is_used  # UnusedTable
    
    def test_inactive_dependencies(self, analyzer, sample_tables, sample_objects):
        """Test that inactive dependencies are ignored."""
        inactive_deps = [
            TableDependency(object_id=101, table_id=1, active=False),  # Inactive
            TableDependency(object_id=102, table_id=2, active=True),   # Active
        ]
        
        result = analyzer.analyze(
            tables=sample_tables,
            objects=sample_objects,
            table_dependencies=inactive_deps,
            object_dependencies=[]
        )
        
        # Only table 2 should be used (active dependency)
        assert not result.tables[1].is_used  # Customers (inactive dependency)
        assert result.tables[2].is_used      # Orders (active dependency)
        assert not result.tables[3].is_used  # Products (no dependency)
        assert not result.tables[4].is_used  # UnusedTable (no dependency)
    
    def test_empty_inputs(self, analyzer):
        """Test behavior with empty inputs."""
        result = analyzer.analyze(
            tables={},
            objects={},
            table_dependencies=[],
            object_dependencies=[]
        )
        
        # Should handle empty inputs gracefully
        assert result.statistics.total_tables == 0
        assert result.statistics.used_tables == 0
        assert result.statistics.unused_tables == 0
        assert result.statistics.total_objects == 0
        assert result.statistics.total_dependencies == 0
        assert result.statistics.active_dependencies == 0
    
    def test_performance_with_large_dataset(self, analyzer):
        """Test performance with a larger dataset."""
        # Create a larger dataset
        tables = {i: Table(table_id=i, table_name=f"Table{i}", is_used=False)
                 for i in range(1, 101)}
        objects = {i: DatabaseObject(object_id=i, object_name=f"Object{i}",
                                    object_type="Query")
                  for i in range(1001, 1101)}

        # Create dependencies
        table_deps = [TableDependency(object_id=obj_id, table_id=table_id, active=True)
                     for obj_id in range(1001, 1051)  # First 50 objects
                     for table_id in range(1, 26)]    # First 25 tables

        object_deps = [ObjectDependency(source_object_id=1050, target_object_id=obj_id, active=True)
                      for obj_id in range(1001, 1026)]  # Chain some objects

        # Run the analysis
        result = analyzer.analyze(tables, objects, table_deps, object_deps)

        # Verify results are reasonable
        assert result.statistics.total_tables == 100
        assert result.statistics.used_tables == 25  # First 25 tables used
        assert result.statistics.unused_tables == 75  # Remaining 75 unused
    
    def test_get_unused_tables(self, analyzer, sample_tables, sample_objects, 
                              sample_table_dependencies, sample_object_dependencies):
        """Test the get_unused_tables method."""
        result = analyzer.analyze(
            tables=sample_tables,
            objects=sample_objects,
            table_dependencies=sample_table_dependencies,
            object_dependencies=sample_object_dependencies
        )
        
        unused_tables = result.get_unused_tables()
        assert len(unused_tables) == 1
        assert unused_tables[0].table_name == "UnusedTable"
        assert not unused_tables[0].is_used
    
    def test_get_used_tables(self, analyzer, sample_tables, sample_objects, 
                            sample_table_dependencies, sample_object_dependencies):
        """Test the get_used_tables method."""
        result = analyzer.analyze(
            tables=sample_tables,
            objects=sample_objects,
            table_dependencies=sample_table_dependencies,
            object_dependencies=sample_object_dependencies
        )
        
        used_tables = result.get_used_tables()
        assert len(used_tables) == 3
        used_table_names = {table.table_name for table in used_tables}
        assert used_table_names == {"Customers", "Orders", "Products"}
        assert all(table.is_used for table in used_tables)