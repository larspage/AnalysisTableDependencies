import pytest
from pathlib import Path
from typing import Dict, Any, List, Tuple
import tempfile
import logging

from database_dependency_analyzer.models.config import AnalysisConfig
from database_dependency_analyzer.models.table import Table
from database_dependency_analyzer.models.object import DatabaseObject
from database_dependency_analyzer.models.dependency import TableDependency, ObjectDependency
from database_dependency_analyzer.models.analysis_result import AnalysisResult


@pytest.fixture(scope="session")
def test_data_dir() -> Path:
    """Provide path to test data directory."""
    return Path(__file__).parent / "fixtures"


@pytest.fixture
def sample_tables() -> Dict[int, Table]:
    """Provide sample table data for testing."""
    return {
        1: Table(table_id=1, table_name="Customers"),
        2: Table(table_id=2, table_name="Orders"),
        3: Table(table_id=3, table_name="Products"),
        4: Table(table_id=4, table_name="Suppliers"),
        5: Table(table_id=5, table_name="Categories"),
    }


@pytest.fixture
def sample_objects() -> Dict[int, DatabaseObject]:
    """Provide sample database objects for testing."""
    return {
        100: DatabaseObject(object_id=100, object_name="CustomerForm", object_type="Form"),
        101: DatabaseObject(object_id=101, object_name="OrderQuery", object_type="Query"),
        102: DatabaseObject(object_id=102, object_name="ProductReport", object_type="Report"),
        103: DatabaseObject(object_id=103, object_name="InventoryMacro", object_type="Macro"),
    }


@pytest.fixture
def sample_table_dependencies() -> List[TableDependency]:
    """Provide sample table dependencies for testing."""
    return [
        TableDependency(object_id=100, table_id=1, active=True),  # CustomerForm uses Customers
        TableDependency(object_id=101, table_id=1, active=True),  # OrderQuery uses Customers
        TableDependency(object_id=101, table_id=2, active=True),  # OrderQuery uses Orders
        TableDependency(object_id=101, table_id=3, active=True),  # OrderQuery uses Products
        TableDependency(object_id=102, table_id=3, active=False), # Inactive dependency
    ]


@pytest.fixture
def sample_object_dependencies() -> List[ObjectDependency]:
    """Provide sample object dependencies for testing."""
    return [
        ObjectDependency(source_object_id=100, target_object_id=101, active=True),  # Form uses Query
        ObjectDependency(source_object_id=102, target_object_id=103, active=True),  # Report uses Macro
    ]


@pytest.fixture
def sample_analysis_result(sample_tables, sample_objects, sample_table_dependencies, sample_object_dependencies) -> AnalysisResult:
    """Provide sample analysis result for testing."""
    # Create a basic analysis result
    result = AnalysisResult()

    # Copy tables and mark some as used based on dependencies
    result.tables = sample_tables.copy()
    used_table_ids = {dep.table_id for dep in sample_table_dependencies if dep.is_active}
    for table_id in used_table_ids:
        if table_id in result.tables:
            result.tables[table_id].is_used = True

    # Add objects
    result.objects = sample_objects.copy()

    # Add dependencies
    result.table_dependencies = sample_table_dependencies
    result.object_dependencies = sample_object_dependencies

    # Calculate statistics
    total_tables = len(result.tables)
    used_tables = len([t for t in result.tables.values() if t.is_used])
    result.statistics.total_tables = total_tables
    result.statistics.used_tables = used_tables
    result.statistics.unused_tables = total_tables - used_tables
    result.statistics.total_objects = len(result.objects)

    return result


@pytest.fixture
def analysis_config(tmp_path) -> AnalysisConfig:
    """Provide a basic analysis configuration for testing."""
    # Create dummy XML files to satisfy file existence validation
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
def sample_files_config() -> AnalysisConfig:
    """Provide configuration using actual sample XML files."""
    return AnalysisConfig(
        tables_file=Path("SampleXMLFiles/Analysis_Tables.xml"),
        objects_file=Path("SampleXMLFiles/Analysis_Objects.xml"),
        table_dependencies_file=Path("SampleXMLFiles/Analysis_TableDependencies.xml"),
        object_dependencies_file=Path("SampleXMLFiles/Analysis_ObjectDependencies.xml"),
        output_file=None,
        console_output=False,
        verbose=False,
        ignore_inactive_dependencies=True,
        max_workers=2,
        memory_limit_mb=256
    )


@pytest.fixture(scope="session", autouse=True)
def setup_logging():
    """Configure logging for tests."""
    logging.basicConfig(
        level=logging.WARNING,  # Reduce log noise during tests
        format='%(levelname)s: %(message)s'
    )


@pytest.fixture
def temp_xml_file(tmp_path):
    """Create a temporary XML file for testing."""
    def _create_xml_file(content: str, filename: str = "test.xml") -> Path:
        file_path = tmp_path / filename
        file_path.write_text(content, encoding='utf-8')
        return file_path
    return _create_xml_file


@pytest.fixture
def sample_data_small(sample_tables, sample_objects, sample_table_dependencies, sample_object_dependencies) -> Tuple[Dict, Dict, List, List]:
    """Provide small sample dataset for performance testing."""
    return sample_tables, sample_objects, sample_table_dependencies, sample_object_dependencies


@pytest.fixture
def sample_data_large() -> Tuple[Dict[int, Table], Dict[int, DatabaseObject], List[TableDependency], List[ObjectDependency]]:
    """Provide large sample dataset for performance testing."""
    # Generate larger dataset programmatically
    tables = {}
    for i in range(1, 1001):  # 1000 tables
        tables[i] = Table(table_id=i, table_name=f"Table{i}")

    objects = {}
    object_types = ["Form", "Query", "Macro", "Report"]
    for i in range(1, 251):  # 250 objects
        objects[i] = DatabaseObject(object_id=i, object_name=f"{obj_type}{i}", object_type=obj_type)

    # Create dependencies for ~70% of tables
    table_deps = []
    for i in range(1, 701):
        object_id = (i % 250) + 1
        table_deps.append(TableDependency(object_id=object_id, table_id=i, active=True))

    # Mark tables as used
    for dep in table_deps:
        if dep.table_id in tables:
            tables[dep.table_id].is_used = True

    object_deps = []
    for i in range(1, 101):  # 100 object dependencies
        parent_id = (i % 250) + 1
        child_id = ((i + 50) % 250) + 1
        object_deps.append(ObjectDependency(source_object_id=parent_id, target_object_id=child_id, active=True))

    return tables, objects, table_deps, object_deps