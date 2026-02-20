"""Unit tests for XML parsers."""

import pytest
import tempfile
from pathlib import Path
from unittest.mock import patch

from database_dependency_analyzer.models.config import AnalysisConfig
from tests.conftest import analysis_config
from src.database_dependency_analyzer.parsers.xml_parser import BaseXMLParser, XMLParseError
from src.database_dependency_analyzer.parsers.table_parser import TableParser
from src.database_dependency_analyzer.parsers.object_parser import ObjectParser
from src.database_dependency_analyzer.parsers.dependency_parser import DependencyParser
from src.database_dependency_analyzer.models.table import Table
from src.database_dependency_analyzer.models.object import DatabaseObject
from src.database_dependency_analyzer.models.dependency import TableDependency, ObjectDependency


class TestBaseXMLParser:
    """Test BaseXMLParser functionality."""

    def test_parse_file_success(self, tmp_path, analysis_config):
        """Test successful XML file parsing."""
        xml_content = """<?xml version="1.0"?>
        <dataroot xmlns:od="urn:schemas-microsoft-com:officedata">
        </dataroot>"""

        xml_file = tmp_path / "test.xml"
        xml_file.write_text(xml_content)

        parser = TableParser(analysis_config)
        tree = parser.parse_file(xml_file)

        assert tree is not None
        assert tree.getroot().tag == "dataroot"

    def test_parse_file_not_found(self, tmp_path):
        """Test parsing non-existent file."""
        # Create dummy config files
        (tmp_path / "tables.xml").write_text("<xml></xml>")
        (tmp_path / "objects.xml").write_text("<xml></xml>")
        (tmp_path / "table_deps.xml").write_text("<xml></xml>")
        (tmp_path / "object_deps.xml").write_text("<xml></xml>")

        config = AnalysisConfig(
            tables_file=tmp_path / "tables.xml",
            objects_file=tmp_path / "objects.xml",
            table_dependencies_file=tmp_path / "table_deps.xml",
            object_dependencies_file=tmp_path / "object_deps.xml"
        )
        parser = TableParser(config)

        with pytest.raises(FileNotFoundError):
            parser.parse_file(Path("nonexistent.xml"))

    def test_parse_malformed_xml(self, tmp_path):
        """Test parsing malformed XML."""
        xml_file = tmp_path / "malformed.xml"
        xml_file.write_text("<invalid>")

        # Create dummy config files
        (tmp_path / "tables.xml").write_text("<xml></xml>")
        (tmp_path / "objects.xml").write_text("<xml></xml>")
        (tmp_path / "table_deps.xml").write_text("<xml></xml>")
        (tmp_path / "object_deps.xml").write_text("<xml></xml>")

        config = AnalysisConfig(
            tables_file=tmp_path / "tables.xml",
            objects_file=tmp_path / "objects.xml",
            table_dependencies_file=tmp_path / "table_deps.xml",
            object_dependencies_file=tmp_path / "object_deps.xml"
        )
        parser = TableParser(config)

        with pytest.raises(XMLParseError):
            parser.parse_file(xml_file)

    def test_find_elements_namespaced(self, tmp_path):
        """Test finding elements with namespace."""
        xml_content = """<?xml version="1.0"?>
        <dataroot xmlns:od="urn:schemas-microsoft-com:officedata">
          <od:Analysis_Tables>
            <od:TableID>1</od:TableID>
          </od:Analysis_Tables>
        </dataroot>"""

        xml_file = tmp_path / "namespaced.xml"
        xml_file.write_text(xml_content)

        # Create dummy config files
        (tmp_path / "tables.xml").write_text("<xml></xml>")
        (tmp_path / "objects.xml").write_text("<xml></xml>")
        (tmp_path / "table_deps.xml").write_text("<xml></xml>")
        (tmp_path / "object_deps.xml").write_text("<xml></xml>")

        config = AnalysisConfig(
            tables_file=tmp_path / "tables.xml",
            objects_file=tmp_path / "objects.xml",
            table_dependencies_file=tmp_path / "table_deps.xml",
            object_dependencies_file=tmp_path / "object_deps.xml"
        )
        parser = TableParser(config)
        tree = parser.parse_file(xml_file)
        root = tree.getroot()

        elements = parser.find_elements(root, 'Analysis_Tables')
        assert len(elements) == 1

    def test_find_elements_non_namespaced_fallback(self, tmp_path):
        """Test fallback to non-namespaced elements."""
        xml_content = """<?xml version="1.0"?>
        <dataroot>
          <Analysis_Tables>
            <TableID>1</TableID>
          </Analysis_Tables>
        </dataroot>"""

        xml_file = tmp_path / "non_namespaced.xml"
        xml_file.write_text(xml_content)

        # Create dummy config files
        (tmp_path / "tables.xml").write_text("<xml></xml>")
        (tmp_path / "objects.xml").write_text("<xml></xml>")
        (tmp_path / "table_deps.xml").write_text("<xml></xml>")
        (tmp_path / "object_deps.xml").write_text("<xml></xml>")

        config = AnalysisConfig(
            tables_file=tmp_path / "tables.xml",
            objects_file=tmp_path / "objects.xml",
            table_dependencies_file=tmp_path / "table_deps.xml",
            object_dependencies_file=tmp_path / "object_deps.xml"
        )
        parser = TableParser(config)
        tree = parser.parse_file(xml_file)
        root = tree.getroot()

        elements = parser.find_elements(root, 'Analysis_Tables')
        assert len(elements) == 1

    def test_get_text_namespaced(self, tmp_path):
        """Test getting text from namespaced elements."""
        xml_content = """<?xml version="1.0"?>
        <dataroot xmlns:od="urn:schemas-microsoft-com:officedata">
          <od:Analysis_Tables>
            <od:TableName>TestTable</od:TableName>
          </od:Analysis_Tables>
        </dataroot>"""

        xml_file = tmp_path / "test.xml"
        xml_file.write_text(xml_content)

        # Create dummy config files
        (tmp_path / "tables.xml").write_text("<xml></xml>")
        (tmp_path / "objects.xml").write_text("<xml></xml>")
        (tmp_path / "table_deps.xml").write_text("<xml></xml>")
        (tmp_path / "object_deps.xml").write_text("<xml></xml>")

        config = AnalysisConfig(
            tables_file=tmp_path / "tables.xml",
            objects_file=tmp_path / "objects.xml",
            table_dependencies_file=tmp_path / "table_deps.xml",
            object_dependencies_file=tmp_path / "object_deps.xml"
        )
        parser = TableParser(config)
        tree = parser.parse_file(xml_file)
        root = tree.getroot()
        element = root[0]

        text = parser.get_text(element, 'TableName')
        assert text == "TestTable"

    def test_get_text_non_namespaced_fallback(self, tmp_path):
        """Test getting text from non-namespaced elements."""
        xml_content = """<?xml version="1.0"?>
        <dataroot>
          <Analysis_Tables>
            <TableName>TestTable</TableName>
          </Analysis_Tables>
        </dataroot>"""

        xml_file = tmp_path / "test.xml"
        xml_file.write_text(xml_content)

        # Create dummy config files
        (tmp_path / "tables.xml").write_text("<xml></xml>")
        (tmp_path / "objects.xml").write_text("<xml></xml>")
        (tmp_path / "table_deps.xml").write_text("<xml></xml>")
        (tmp_path / "object_deps.xml").write_text("<xml></xml>")

        config = AnalysisConfig(
            tables_file=tmp_path / "tables.xml",
            objects_file=tmp_path / "objects.xml",
            table_dependencies_file=tmp_path / "table_deps.xml",
            object_dependencies_file=tmp_path / "object_deps.xml"
        )
        parser = TableParser(config)
        tree = parser.parse_file(xml_file)
        root = tree.getroot()
        element = root[0]

        text = parser.get_text(element, 'TableName')
        assert text == "TestTable"

    def test_get_int_valid(self, tmp_path):
        """Test getting valid integer values."""
        xml_content = """<?xml version="1.0"?>
        <dataroot xmlns:od="urn:schemas-microsoft-com:officedata">
          <od:Analysis_Tables>
            <od:TableID>123</od:TableID>
          </od:Analysis_Tables>
        </dataroot>"""

        xml_file = tmp_path / "test.xml"
        xml_file.write_text(xml_content)

        # Create dummy config files
        (tmp_path / "tables.xml").write_text("<xml></xml>")
        (tmp_path / "objects.xml").write_text("<xml></xml>")
        (tmp_path / "table_deps.xml").write_text("<xml></xml>")
        (tmp_path / "object_deps.xml").write_text("<xml></xml>")

        config = AnalysisConfig(
            tables_file=tmp_path / "tables.xml",
            objects_file=tmp_path / "objects.xml",
            table_dependencies_file=tmp_path / "table_deps.xml",
            object_dependencies_file=tmp_path / "object_deps.xml"
        )
        parser = TableParser(config)
        tree = parser.parse_file(xml_file)
        root = tree.getroot()
        element = root[0]

        value = parser.get_int(element, 'TableID')
        assert value == 123

    def test_get_int_invalid(self, tmp_path):
        """Test getting invalid integer values."""
        xml_content = """<?xml version="1.0"?>
        <dataroot xmlns:od="urn:schemas-microsoft-com:officedata">
          <od:Analysis_Tables>
            <od:TableID>invalid</od:TableID>
          </od:Analysis_Tables>
        </dataroot>"""

        xml_file = tmp_path / "test.xml"
        xml_file.write_text(xml_content)

        # Create dummy config files
        (tmp_path / "tables.xml").write_text("<xml></xml>")
        (tmp_path / "objects.xml").write_text("<xml></xml>")
        (tmp_path / "table_deps.xml").write_text("<xml></xml>")
        (tmp_path / "object_deps.xml").write_text("<xml></xml>")

        config = AnalysisConfig(
            tables_file=tmp_path / "tables.xml",
            objects_file=tmp_path / "objects.xml",
            table_dependencies_file=tmp_path / "table_deps.xml",
            object_dependencies_file=tmp_path / "object_deps.xml"
        )
        parser = TableParser(config)
        tree = parser.parse_file(xml_file)
        root = tree.getroot()
        element = root[0]

        value = parser.get_int(element, 'TableID')
        assert value == 0  # default

    def test_get_bool_valid(self, tmp_path, analysis_config):
        """Test getting valid boolean values."""
        xml_content = """<?xml version="1.0"?>
        <dataroot xmlns:od="urn:schemas-microsoft-com:officedata">
          <od:Analysis_Tables>
            <od:Active>true</od:Active>
          </od:Analysis_Tables>
        </dataroot>"""

        xml_file = tmp_path / "test.xml"
        xml_file.write_text(xml_content)

        parser = TableParser(analysis_config)
        tree = parser.parse_file(xml_file)
        root = tree.getroot()
        element = root[0]

        value = parser.get_bool(element, 'Active')
        assert value is True

    def test_get_bool_invalid(self, tmp_path, analysis_config):
        """Test getting invalid boolean values."""
        xml_content = """<?xml version="1.0"?>
        <dataroot xmlns:od="urn:schemas-microsoft-com:officedata">
          <od:Analysis_Tables>
            <od:Active>maybe</od:Active>
          </od:Analysis_Tables>
        </dataroot>"""

        xml_file = tmp_path / "test.xml"
        xml_file.write_text(xml_content)

        parser = TableParser(analysis_config)
        tree = parser.parse_file(xml_file)
        root = tree.getroot()
        element = root[0]

        value = parser.get_bool(element, 'Active')
        assert value is True  # default


class TestTableParser:
    """Test TableParser functionality."""

    def test_parse_tables_success(self, tmp_path, analysis_config):
        """Test successful table parsing."""
        xml_content = """<?xml version="1.0"?>
        <dataroot xmlns:od="urn:schemas-microsoft-com:officedata">
          <Analysis_Tables>
            <TableID>1</TableID>
            <TableName>Customers</TableName>
          </Analysis_Tables>
          <Analysis_Tables>
            <TableID>2</TableID>
            <TableName>Orders</TableName>
          </Analysis_Tables>
        </dataroot>"""

        xml_file = tmp_path / "tables.xml"
        xml_file.write_text(xml_content)

        parser = TableParser(analysis_config)
        tables = parser.parse(xml_file)

        assert isinstance(tables, dict)
        assert len(tables) == 2
        assert 1 in tables
        assert 2 in tables
        assert tables[1].table_name == "Customers"
        assert tables[2].table_name == "Orders"

    def test_parse_tables_namespace_fallback(self, tmp_path, analysis_config):
        """Test parsing tables without namespaces."""
        xml_content = """<?xml version="1.0"?>
        <dataroot>
          <Analysis_Tables>
            <TableID>1</TableID>
            <TableName>TestTable</TableName>
          </Analysis_Tables>
        </dataroot>"""

        xml_file = tmp_path / "no_namespace.xml"
        xml_file.write_text(xml_content)

        parser = TableParser(analysis_config)
        tables = parser.parse(xml_file)

        assert 1 in tables
        assert tables[1].table_name == "TestTable"

    def test_parse_invalid_table_data(self, tmp_path):
        """Test parsing invalid table data."""
        xml_content = """<?xml version="1.0"?>
        <dataroot xmlns:od="urn:schemas-microsoft-com:officedata">
          <Analysis_Tables>
            <TableID>invalid</TableID>
            <TableName></TableName>
          </Analysis_Tables>
          <Analysis_Tables>
            <TableID>2</TableID>
            <TableName>ValidTable</TableName>
          </Analysis_Tables>
        </dataroot>"""

        xml_file = tmp_path / "invalid.xml"
        xml_file.write_text(xml_content)

        # Create dummy config files
        (tmp_path / "tables.xml").write_text("<xml></xml>")
        (tmp_path / "objects.xml").write_text("<xml></xml>")
        (tmp_path / "table_deps.xml").write_text("<xml></xml>")
        (tmp_path / "object_deps.xml").write_text("<xml></xml>")

        config = AnalysisConfig(
            tables_file=tmp_path / "tables.xml",
            objects_file=tmp_path / "objects.xml",
            table_dependencies_file=tmp_path / "table_deps.xml",
            object_dependencies_file=tmp_path / "object_deps.xml"
        )
        parser = TableParser(config)
        tables = parser.parse(xml_file)

        # Should skip invalid entries but parse valid ones
        assert isinstance(tables, dict)
        assert len(tables) == 1
        assert 2 in tables

    def test_parse_duplicate_table_ids(self, tmp_path):
        """Test handling of duplicate table IDs."""
        xml_content = """<?xml version="1.0"?>
        <dataroot xmlns:od="urn:schemas-microsoft-com:officedata">
          <Analysis_Tables>
            <TableID>1</TableID>
            <TableName>FirstTable</TableName>
          </Analysis_Tables>
          <Analysis_Tables>
            <TableID>1</TableID>
            <TableName>SecondTable</TableName>
          </Analysis_Tables>
        </dataroot>"""

        xml_file = tmp_path / "duplicates.xml"
        xml_file.write_text(xml_content)

        # Create dummy config files
        (tmp_path / "tables.xml").write_text("<xml></xml>")
        (tmp_path / "objects.xml").write_text("<xml></xml>")
        (tmp_path / "table_deps.xml").write_text("<xml></xml>")
        (tmp_path / "object_deps.xml").write_text("<xml></xml>")

        config = AnalysisConfig(
            tables_file=tmp_path / "tables.xml",
            objects_file=tmp_path / "objects.xml",
            table_dependencies_file=tmp_path / "table_deps.xml",
            object_dependencies_file=tmp_path / "object_deps.xml"
        )
        parser = TableParser(config)
        tables = parser.parse(xml_file)

        # Should keep the first occurrence
        assert len(tables) == 1
        assert tables[1].table_name == "FirstTable"


class TestObjectParser:
    """Test ObjectParser functionality."""

    def test_parse_objects_success(self, tmp_path, analysis_config):
        """Test successful object parsing."""
        xml_content = """<?xml version="1.0"?>
        <dataroot xmlns:od="urn:schemas-microsoft-com:officedata">
          <Analysis_Objects>
            <ObjectID>100</ObjectID>
            <ObjectName>CustomerForm</ObjectName>
            <ObjectType>Form</ObjectType>
          </Analysis_Objects>
          <Analysis_Objects>
            <ObjectID>200</ObjectID>
            <ObjectName>SalesQuery</ObjectName>
            <ObjectType>Query</ObjectType>
          </Analysis_Objects>
        </dataroot>"""

        xml_file = tmp_path / "objects.xml"
        xml_file.write_text(xml_content)

        parser = ObjectParser(analysis_config)
        objects = parser.parse(xml_file)

        assert isinstance(objects, dict)
        assert len(objects) == 2
        assert 100 in objects
        assert 200 in objects
        assert objects[100].object_name == "CustomerForm"
        assert objects[100].object_type == "Form"
        assert objects[200].object_name == "SalesQuery"
        assert objects[200].object_type == "Query"

    def test_parse_invalid_object_data(self, tmp_path, analysis_config):
        """Test parsing invalid object data."""
        xml_content = """<?xml version="1.0"?>
        <dataroot xmlns:od="urn:schemas-microsoft-com:officedata">
          <Analysis_Objects>
            <ObjectID>invalid</ObjectID>
            <ObjectName></ObjectName>
            <ObjectType>Form</ObjectType>
          </Analysis_Objects>
          <Analysis_Objects>
            <ObjectID>200</ObjectID>
            <ObjectName>ValidObject</ObjectName>
            <ObjectType>Query</ObjectType>
          </Analysis_Objects>
        </dataroot>"""

        xml_file = tmp_path / "invalid.xml"
        xml_file.write_text(xml_content)

        parser = ObjectParser(analysis_config)
        objects = parser.parse(xml_file)

        # Should skip invalid entries
        assert isinstance(objects, dict)
        assert len(objects) == 1
        assert 200 in objects


class TestDependencyParser:
    """Test DependencyParser functionality."""

    def test_parse_table_dependencies_success(self, tmp_path, analysis_config):
        """Test successful table dependency parsing."""
        xml_content = """<?xml version="1.0"?>
        <dataroot xmlns:od="urn:schemas-microsoft-com:officedata">
          <Analysis_TableDependencies>
            <ObjectID>100</ObjectID>
            <TableID>1</TableID>
            <Active>true</Active>
          </Analysis_TableDependencies>
          <Analysis_TableDependencies>
            <ObjectID>200</ObjectID>
            <TableID>2</TableID>
            <Active>false</Active>
          </Analysis_TableDependencies>
        </dataroot>"""

        xml_file = tmp_path / "table_deps.xml"
        xml_file.write_text(xml_content)

        parser = DependencyParser(analysis_config)
        dependencies = parser.parse_table_dependencies(xml_file)

        assert isinstance(dependencies, list)
        assert len(dependencies) == 2
        assert dependencies[0].object_id == 100
        assert dependencies[0].table_id == 1
        assert dependencies[0].active is True
        assert dependencies[1].object_id == 200
        assert dependencies[1].table_id == 2
        assert dependencies[1].active is False

    def test_parse_object_dependencies_success(self, tmp_path, analysis_config):
        """Test successful object dependency parsing."""
        xml_content = """<?xml version="1.0"?>
        <dataroot xmlns:od="urn:schemas-microsoft-com:officedata">
          <Analysis_ObjectDependencies>
            <SourceObjectID>100</SourceObjectID>
            <TargetObjectID>200</TargetObjectID>
            <Active>true</Active>
          </Analysis_ObjectDependencies>
        </dataroot>"""

        xml_file = tmp_path / "object_deps.xml"
        xml_file.write_text(xml_content)

        parser = DependencyParser(analysis_config)
        dependencies = parser.parse_object_dependencies(xml_file)

        assert isinstance(dependencies, list)
        assert len(dependencies) == 1
        assert dependencies[0].source_object_id == 100
        assert dependencies[0].target_object_id == 200
        assert dependencies[0].active is True

    def test_parse_invalid_dependency_data(self, tmp_path):
        """Test parsing invalid dependency data."""
        xml_content = """<?xml version="1.0"?>
        <dataroot xmlns:od="urn:schemas-microsoft-com:officedata">
          <Analysis_TableDependencies>
            <ObjectID>invalid</ObjectID>
            <TableID>1</TableID>
            <Active>true</Active>
          </Analysis_TableDependencies>
          <Analysis_TableDependencies>
            <ObjectID>200</ObjectID>
            <TableID>2</TableID>
            <Active>true</Active>
          </Analysis_TableDependencies>
        </dataroot>"""

        xml_file = tmp_path / "invalid_deps.xml"
        xml_file.write_text(xml_content)

        # Create dummy config files
        (tmp_path / "tables.xml").write_text("<xml></xml>")
        (tmp_path / "objects.xml").write_text("<xml></xml>")
        (tmp_path / "table_deps.xml").write_text("<xml></xml>")
        (tmp_path / "object_deps.xml").write_text("<xml></xml>")

        config = AnalysisConfig(
            tables_file=tmp_path / "tables.xml",
            objects_file=tmp_path / "objects.xml",
            table_dependencies_file=tmp_path / "table_deps.xml",
            object_dependencies_file=tmp_path / "object_deps.xml"
        )
        parser = DependencyParser(config)
        dependencies = parser.parse_table_dependencies(xml_file)

        # Should skip invalid entries
        assert isinstance(dependencies, list)
        assert len(dependencies) == 1
        assert dependencies[0].object_id == 200