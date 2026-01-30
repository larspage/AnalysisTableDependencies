"""Integration tests for XML parsers using real sample files."""

import pytest
from pathlib import Path

from database_dependency_analyzer.parsers.table_parser import TableParser
from database_dependency_analyzer.parsers.object_parser import ObjectParser
from database_dependency_analyzer.parsers.dependency_parser import DependencyParser


class TestParsersIntegration:
    """Integration tests for parsers using actual sample XML files."""

    def test_parse_real_tables_file(self, sample_files_config):
        """Test parsing the actual sample tables XML file."""
        parser = TableParser(sample_files_config)
        tables = parser.parse(sample_files_config.tables_file)

        # Verify we get some tables
        assert isinstance(tables, dict)
        assert len(tables) > 0
        
        # Verify table structure
        for table_id, table in tables.items():
            assert table.table_id == table_id
            assert table.table_name
            assert isinstance(table.table_name, str)

    def test_parse_real_objects_file(self, sample_files_config):
        """Test parsing the actual sample objects XML file."""
        parser = ObjectParser(sample_files_config)
        objects = parser.parse(sample_files_config.objects_file)

        # Verify we get some objects
        assert isinstance(objects, dict)
        assert len(objects) > 0
        
        # Verify object structure
        for object_id, obj in objects.items():
            assert obj.object_id == object_id
            assert obj.object_name
            assert obj.object_type
            assert isinstance(obj.object_name, str)
            assert isinstance(obj.object_type, str)

    def test_parse_real_table_dependencies(self, sample_files_config):
        """Test parsing the actual sample table dependencies XML file."""
        parser = DependencyParser(sample_files_config)
        dependencies = parser.parse_table_dependencies(sample_files_config.table_dependencies_file)

        # Verify we get some dependencies
        assert isinstance(dependencies, list)
        assert len(dependencies) > 0
        
        # Verify dependency structure
        for dep in dependencies:
            assert dep.object_id > 0
            assert dep.table_id > 0
            assert isinstance(dep.active, bool)

    def test_parse_real_object_dependencies(self, sample_files_config):
        """Test parsing the actual sample object dependencies XML file."""
        parser = DependencyParser(sample_files_config)
        dependencies = parser.parse_object_dependencies(sample_files_config.object_dependencies_file)

        # Verify we get some dependencies
        assert isinstance(dependencies, list)
        assert len(dependencies) > 0
        
        # Verify dependency structure
        for dep in dependencies:
            assert dep.source_object_id > 0
            assert dep.target_object_id > 0
            assert isinstance(dep.active, bool)