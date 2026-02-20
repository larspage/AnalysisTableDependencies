"""Unit tests for console interface components."""

import logging
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

from database_dependency_analyzer.console.argument_parser import ArgumentParser
from database_dependency_analyzer.console.output_formatter import OutputFormatter
from database_dependency_analyzer.console.progress_tracker import ProgressTracker
from database_dependency_analyzer.models.analysis_result import AnalysisResult, AnalysisStatistics
from database_dependency_analyzer.models.table import Table


class TestArgumentParser:
    """Test cases for ArgumentParser."""

    def test_parse_args_required_files(self, tmp_path):
        """Test parsing with required file arguments."""
        parser = ArgumentParser()

        tables_file = tmp_path / "tables.xml"
        objects_file = tmp_path / "objects.xml"
        table_deps_file = tmp_path / "table_deps.xml"
        object_deps_file = tmp_path / "object_deps.xml"

        # Create dummy files
        for f in [tables_file, objects_file, table_deps_file, object_deps_file]:
            f.write_text("<xml></xml>")

        args = parser.parse_args([
            str(tables_file),
            str(objects_file),
            str(table_deps_file),
            str(object_deps_file)
        ])

        assert args.tables_file == tables_file
        assert args.objects_file == objects_file
        assert args.table_dependencies_file == table_deps_file
        assert args.object_dependencies_file == object_deps_file
        assert args.output is None
        assert not args.quiet
        assert not args.verbose
        assert not args.include_inactive
        assert args.max_workers == 4
        assert args.memory_limit == 512

    def test_parse_args_with_options(self, tmp_path):
        """Test parsing with optional arguments."""
        parser = ArgumentParser()

        tables_file = tmp_path / "tables.xml"
        objects_file = tmp_path / "objects.xml"
        table_deps_file = tmp_path / "table_deps.xml"
        object_deps_file = tmp_path / "object_deps.xml"
        output_file = tmp_path / "report.html"

        # Create dummy files
        for f in [tables_file, objects_file, table_deps_file, object_deps_file]:
            f.write_text("<xml></xml>")

        args = parser.parse_args([
            str(tables_file),
            str(objects_file),
            str(table_deps_file),
            str(object_deps_file),
            "-o", str(output_file),
            "-v",
            "--max-workers", "8",
            "--memory-limit", "1024"
        ])

        assert args.output == output_file
        assert args.verbose
        assert args.max_workers == 8
        assert args.memory_limit == 1024

    def test_parse_args_missing_files(self, tmp_path):
        """Test parsing succeeds even with missing files (validation happens later)."""
        parser = ArgumentParser()

        args = parser.parse_args([
            "nonexistent1.xml",
            "nonexistent2.xml",
            "nonexistent3.xml",
            "nonexistent4.xml"
        ])

        assert args.tables_file == Path("nonexistent1.xml")
        assert args.objects_file == Path("nonexistent2.xml")
        assert args.table_dependencies_file == Path("nonexistent3.xml")
        assert args.object_dependencies_file == Path("nonexistent4.xml")


class TestOutputFormatter:
    """Test cases for OutputFormatter."""

    @pytest.fixture
    def sample_result(self):
        """Create a sample analysis result for testing."""
        stats = AnalysisStatistics(
            total_tables=3,
            used_tables=1,
            unused_tables=2,
            total_objects=5,
            object_type_distribution={'Form': 2, 'Query': 2, 'Report': 1},
            total_dependencies=100,
            active_dependencies=80,
            unused_table_ids=[1, 2],
            most_referenced_table={'table_id': 3, 'table_name': 'UsedTable', 'reference_count': 0}
        )

        table1 = Table(table_id=1, table_name="UnusedTable1", is_used=False)
        table2 = Table(table_id=2, table_name="UnusedTable2", is_used=False)
        table3 = Table(table_id=3, table_name="UsedTable", is_used=True)

        return AnalysisResult(
            tables={1: table1, 2: table2, 3: table3},
            objects={},
            statistics=stats,
            processing_time=2.5
        )

    def test_format_summary(self, sample_result):
        """Test summary formatting."""
        formatter = OutputFormatter()
        summary = formatter.format_summary(sample_result)

        assert "Database Dependency Analysis Summary" in summary
        assert "Total tables analyzed: 3" in summary
        assert "Used tables: 1" in summary
        assert "Unused tables: 2" in summary
        assert "66.7%" in summary  # unused percentage

    def test_format_unused_tables(self, sample_result):
        """Test unused tables formatting."""
        formatter = OutputFormatter()
        output = formatter.format_unused_tables(sample_result.get_unused_tables())

        assert "Unused Tables" in output
        assert "UnusedTable1" in output
        assert "UnusedTable2" in output
        assert "Total: 2 unused tables" in output

    def test_format_unused_tables_empty(self):
        """Test formatting when no unused tables."""
        formatter = OutputFormatter()
        output = formatter.format_unused_tables([])

        assert "No unused tables found." in output

    def test_format_statistics(self, sample_result):
        """Test statistics formatting."""
        formatter = OutputFormatter()
        output = formatter.format_statistics(sample_result.statistics)

        assert "Analysis Statistics" in output
        assert "Total dependencies analyzed: 100" in output
        assert "Active dependencies: 80" in output

    def test_format_error(self):
        """Test error formatting."""
        formatter = OutputFormatter()
        error = ValueError("Test error")
        output = formatter.format_error(error)

        assert "Error occurred during analysis:" in output
        assert "ValueError: Test error" in output

    def test_format_error_verbose(self):
        """Test verbose error formatting."""
        formatter = OutputFormatter(verbose=True)
        error = ValueError("Test error")
        output = formatter.format_error(error, verbose=True)

        assert "Stack trace:" in output

    def test_format_progress(self):
        """Test progress formatting."""
        formatter = OutputFormatter()
        output = formatter.format_progress(50, 100, "Processing")

        assert "[==========" in output  # partial progress bar
        assert "50.0%" in output
        assert "Processing" in output


class TestProgressTracker:
    """Test cases for ProgressTracker."""

    def test_initialization(self):
        """Test progress tracker initialization."""
        tracker = ProgressTracker(enabled=True, verbose=True)
        assert tracker.enabled
        assert tracker.verbose
        assert tracker._current_progress is None

    def test_disabled_tracker(self):
        """Test disabled progress tracker."""
        tracker = ProgressTracker(enabled=False)
        assert not tracker.enabled

        progress = tracker.start_operation(10, "Test")
        assert progress is None

        tracker.update(5)  # Should not raise error
        elapsed = tracker.finish_operation()
        assert elapsed >= 0

    @patch('sys.stdout.isatty', return_value=True)
    def test_start_operation(self, mock_isatty):
        """Test starting a progress operation."""
        tracker = ProgressTracker(enabled=True)

        progress = tracker.start_operation(100, "Test operation")
        assert progress is not None
        assert tracker._current_progress is not None

        tracker.finish_operation()
        assert tracker._current_progress is None

    def test_update_and_finish(self):
        """Test updating progress and finishing."""
        tracker = ProgressTracker(enabled=False)  # Use disabled to avoid tqdm issues

        tracker.start_operation(10, "Test")
        tracker.update(5)
        tracker.set_description("Updated description")
        elapsed = tracker.finish_operation()

        assert elapsed >= 0

    def test_track_operation_context_manager(self):
        """Test context manager for tracking operations."""
        tracker = ProgressTracker(enabled=False)

        with tracker.track_operation(10, "Context test") as progress:
            assert progress is None  # disabled
            tracker.update(5)

        # Should have finished automatically

    def test_log_progress(self, caplog):
        """Test progress logging."""
        tracker = ProgressTracker(enabled=True, verbose=True)

        with caplog.at_level(logging.INFO):
            tracker.log_progress(50, 100, "Test message")

        assert len(caplog.records) == 1
        assert "50/100" in caplog.records[0].message
        assert "Test message" in caplog.records[0].message

    def test_show_message(self):
        """Test showing messages."""
        tracker = ProgressTracker(enabled=True)

        with patch('builtins.print') as mock_print:
            tracker.show_message("Test message")
            mock_print.assert_called_with("ℹ️  Test message")

            tracker.show_message("Warning message", "warning")
            mock_print.assert_called_with("⚠️  Warning message")

            tracker.show_message("Error message", "error")
            mock_print.assert_called_with("❌ Error message")

    def test_create_subtracker(self):
        """Test creating sub-trackers."""
        tracker = ProgressTracker(enabled=True, verbose=True)
        subtracker = tracker.create_subtracker(50, "Sub-operation")

        assert isinstance(subtracker, ProgressTracker)
        assert subtracker.enabled == tracker.enabled
        assert subtracker.verbose == tracker.verbose