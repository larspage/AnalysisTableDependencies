"""Integration tests for full analysis workflow."""

import pytest
from datetime import datetime

from database_dependency_analyzer.analyzers.dependency_analyzer import DependencyAnalyzer
from database_dependency_analyzer.parsers.table_parser import TableParser
from database_dependency_analyzer.parsers.object_parser import ObjectParser
from database_dependency_analyzer.parsers.dependency_parser import DependencyParser


class TestFullAnalysisIntegration:
    """Integration tests for the complete analysis workflow."""

    def test_full_analysis_workflow(self, sample_files_config):
        """Test the complete analysis workflow with real sample files."""
        # Parse all input files
        table_parser = TableParser(sample_files_config)
        object_parser = ObjectParser(sample_files_config)
        dependency_parser = DependencyParser(sample_files_config)

        tables = table_parser.parse(sample_files_config.tables_file)
        objects = object_parser.parse(sample_files_config.objects_file)
        table_dependencies = dependency_parser.parse_table_dependencies(
            sample_files_config.table_dependencies_file)
        object_dependencies = dependency_parser.parse_object_dependencies(
            sample_files_config.object_dependencies_file)

        # Verify we have data to analyze
        assert len(tables) > 0
        assert len(objects) > 0
        assert len(table_dependencies) > 0
        assert len(object_dependencies) > 0

        # Run the analysis
        analyzer = DependencyAnalyzer(sample_files_config)
        result = analyzer.analyze(tables, objects, table_dependencies, object_dependencies)

        # Verify result structure
        assert result is not None
        assert result.statistics is not None
        assert result.processing_time > 0
        assert isinstance(result.timestamp, datetime)

        # Verify statistics are reasonable
        assert result.statistics.total_tables == len(tables)
        assert result.statistics.total_objects == len(objects)
        assert result.statistics.total_dependencies >= 0
        assert result.statistics.active_dependencies >= 0

        # Verify we have some used and unused tables
        assert result.statistics.used_tables >= 0
        assert result.statistics.unused_tables >= 0
        assert result.statistics.used_tables + result.statistics.unused_tables == len(tables)

        # Verify we can get used and unused tables
        used_tables = result.get_used_tables()
        unused_tables = result.get_unused_tables()

        assert len(used_tables) == result.statistics.used_tables
        assert len(unused_tables) == result.statistics.unused_tables

        # Verify all used tables have is_used=True
        for table in used_tables:
            assert table.is_used

        # Verify all unused tables have is_used=False
        for table in unused_tables:
            assert not table.is_used

    def test_analysis_with_sample_data_consistency(self, sample_files_config):
        """Test that analysis produces consistent results across multiple runs."""
        # Run analysis multiple times
        analyzer = DependencyAnalyzer(sample_files_config)
        
        results = []
        for _ in range(3):
            # Parse files each time to simulate fresh run
            table_parser = TableParser(sample_files_config)
            object_parser = ObjectParser(sample_files_config)
            dependency_parser = DependencyParser(sample_files_config)

            tables = table_parser.parse(sample_files_config.tables_file)
            objects = object_parser.parse(sample_files_config.objects_file)
            table_dependencies = dependency_parser.parse_table_dependencies(
                sample_files_config.table_dependencies_file)
            object_dependencies = dependency_parser.parse_object_dependencies(
                sample_files_config.object_dependencies_file)

            result = analyzer.analyze(tables, objects, table_dependencies, object_dependencies)
            results.append(result)

        # Verify all runs produce identical statistics
        for i in range(1, len(results)):
            assert results[i].statistics.total_tables == results[0].statistics.total_tables
            assert results[i].statistics.total_objects == results[0].statistics.total_objects
            assert results[i].statistics.used_tables == results[0].statistics.used_tables
            assert results[i].statistics.unused_tables == results[0].statistics.unused_tables
            assert results[i].statistics.total_dependencies == results[0].statistics.total_dependencies
            assert results[i].statistics.active_dependencies == results[0].statistics.active_dependencies