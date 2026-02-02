# Comprehensive Test Plan

## Overview

This document outlines the comprehensive testing strategy for the Database Dependency Analyzer. The test plan covers unit testing, integration testing, performance benchmarking, and quality assurance to ensure robust, reliable software delivery.

## Test Strategy

### Testing Principles

1. **Test-Driven Development**: Write tests before or alongside code
2. **Comprehensive Coverage**: Target >90% code coverage
3. **Realistic Test Data**: Use representative sample data
4. **Automated Testing**: All tests run in CI/CD pipeline
5. **Performance Benchmarks**: Track and prevent performance regressions

### Test Categories

#### 1. Unit Tests
- Test individual functions, methods, and classes
- Mock external dependencies
- Focus on logic and edge cases
- Fast execution (< 1 second per test)

#### 2. Integration Tests
- Test component interactions
- End-to-end workflows
- External dependencies (file I/O, XML parsing)
- Medium execution time (1-10 seconds)

#### 3. System Tests
- Full application testing
- Command-line interface validation
- Output format verification
- Slow execution (10-60 seconds)

#### 4. Performance Tests
- Benchmark analysis speed
- Memory usage monitoring
- Scalability testing
- Long execution time (1-5 minutes)

## Test Structure

### Directory Structure

```
tests/
├── __init__.py
├── conftest.py                    # Shared fixtures and configuration
├── pytest.ini                    # pytest configuration
├── .coveragerc                   # Coverage configuration
├── unit/                         # Unit tests
│   ├── test_models.py           # Data model tests
│   ├── test_parsers.py          # XML parser tests
│   ├── test_analyzer.py         # Analysis logic tests
│   ├── test_generators.py       # Report generator tests
│   └── test_console.py          # CLI tests
├── integration/                  # Integration tests
│   ├── test_full_workflow.py    # End-to-end analysis
│   ├── test_large_dataset.py    # Large data handling
│   └── test_error_scenarios.py  # Error condition testing
├── performance/                  # Performance benchmarks
│   ├── benchmark_analysis.py    # Analysis performance
│   ├── benchmark_parsing.py     # XML parsing performance
│   └── benchmark_memory.py      # Memory usage tests
├── fixtures/                     # Test data
│   ├── xml/                     # XML test files
│   │   ├── sample_tables.xml
│   │   ├── sample_objects.xml
│   │   ├── sample_table_deps.xml
│   │   └── sample_object_deps.xml
│   ├── json/                    # Expected results
│   │   ├── expected_analysis.json
│   │   └── expected_statistics.json
│   └── edge_cases/              # Special test cases
│       ├── empty_files/
│       ├── malformed_xml/
│       └── large_dataset/
└── utils/                       # Test utilities
    ├── xml_generator.py         # Generate test XML
    ├── data_factory.py          # Create test data
    └── assertion_helpers.py     # Custom assertions
```

### Test Configuration

#### pytest.ini
```ini
[tool:pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts =
    --strict-markers
    --strict-config
    --cov=database_dependency_analyzer
    --cov-report=term-missing
    --cov-report=xml
    --cov-fail-under=90
markers =
    unit: Unit tests
    integration: Integration tests
    performance: Performance benchmarks
    slow: Slow running tests
```

#### conftest.py
```python
import pytest
from pathlib import Path
from typing import Dict, Any

@pytest.fixture(scope="session")
def test_data_dir() -> Path:
    """Provide path to test data directory."""
    return Path(__file__).parent / "fixtures"

@pytest.fixture
def sample_tables(test_data_dir: Path) -> Dict[int, Table]:
    """Provide sample table data."""
    # Load from XML or create programmatically
    pass

@pytest.fixture
def sample_analysis_result() -> AnalysisResult:
    """Provide sample analysis result."""
    # Create realistic analysis result
    pass

@pytest.fixture(scope="session", autouse=True)
def setup_logging():
    """Configure logging for tests."""
    import logging
    logging.basicConfig(level=logging.DEBUG)
```

## Unit Test Specifications

### Data Model Tests (test_models.py)

#### Table Model Tests
```python
class TestTable:
    def test_table_creation_valid(self):
        """Test creating valid table."""
        table = Table(table_id=1, table_name="Customers")
        assert table.table_id == 1
        assert table.table_name == "Customers"
        assert table.is_used == False

    def test_table_creation_invalid_id(self):
        """Test table creation with invalid ID."""
        with pytest.raises(ValueError, match="Invalid table_id"):
            Table(table_id=0, table_name="Test")

    def test_table_creation_empty_name(self):
        """Test table creation with empty name."""
        with pytest.raises(ValueError, match="Invalid table_name"):
            Table(table_id=1, table_name="")

    def test_table_status_property(self):
        """Test status property."""
        used_table = Table(table_id=1, table_name="Test", is_used=True)
        unused_table = Table(table_id=2, table_name="Test", is_used=False)

        assert used_table.status == "Used"
        assert unused_table.status == "Unused"

    def test_add_reference(self):
        """Test adding object references."""
        table = Table(table_id=1, table_name="Customers")
        obj_ref = ObjectReference(100, "Form1", "Form", True)

        table.add_reference(obj_ref)

        assert len(table.referencing_objects) == 1
        assert table.is_used == True  # Should be marked as used
```

#### ObjectReference Model Tests
```python
class TestObjectReference:
    def test_valid_object_types(self):
        """Test valid object types."""
        for obj_type in ["Form", "Query", "Macro", "Report"]:
            obj_ref = ObjectReference(1, "Test", obj_type, True)
            assert obj_ref.object_type == obj_type

    def test_invalid_object_type(self):
        """Test invalid object type."""
        with pytest.raises(ValueError, match="Invalid object_type"):
            ObjectReference(1, "Test", "Invalid", True)

    def test_display_name(self):
        """Test display name formatting."""
        obj_ref = ObjectReference(100, "CustomerForm", "Form", True)
        assert obj_ref.display_name == "Form: CustomerForm"

    def test_css_class(self):
        """Test CSS class generation."""
        obj_ref = ObjectReference(100, "Test", "Form", True)
        assert obj_ref.css_class == "object-form"
```

#### AnalysisResult Model Tests
```python
class TestAnalysisResult:
    def test_get_unused_tables(self, sample_analysis_result):
        """Test filtering unused tables."""
        unused = sample_analysis_result.get_unused_tables()
        assert all(not table.is_used for table in unused)

    def test_get_used_tables(self, sample_analysis_result):
        """Test filtering used tables."""
        used = sample_analysis_result.get_used_tables()
        assert all(table.is_used for table in used)

    def test_get_table_by_name(self, sample_analysis_result):
        """Test table lookup by name."""
        table = sample_analysis_result.get_table_by_name("Customers")
        assert table is not None
        assert table.table_name == "Customers"
```

### XML Parser Tests (test_parsers.py)

#### Base Parser Tests
```python
class TestBaseXMLParser:
    def test_parse_file_success(self, tmp_path):
        """Test successful XML file parsing."""
        xml_content = """<?xml version="1.0"?>
        <dataroot xmlns:od="urn:schemas-microsoft-com:officedata">
        </dataroot>"""

        xml_file = tmp_path / "test.xml"
        xml_file.write_text(xml_content)

        parser = BaseXMLParser(AnalysisConfig())
        tree = parser.parse_file(xml_file)

        assert tree is not None
        assert tree.getroot().tag == "dataroot"

    def test_parse_file_not_found(self):
        """Test parsing non-existent file."""
        parser = BaseXMLParser(AnalysisConfig())

        with pytest.raises(FileNotFoundError):
            parser.parse_file(Path("nonexistent.xml"))

    def test_parse_malformed_xml(self, tmp_path):
        """Test parsing malformed XML."""
        xml_file = tmp_path / "malformed.xml"
        xml_file.write_text("<invalid>")

        parser = BaseXMLParser(AnalysisConfig())

        with pytest.raises(XMLParseError):
            parser.parse_file(xml_file)
```

#### Table Parser Tests
```python
class TestTableParser:
    def test_parse_tables_success(self, test_data_dir):
        """Test successful table parsing."""
        parser = TableParser(AnalysisConfig())
        tables_file = test_data_dir / "xml" / "sample_tables.xml"

        tables = parser.parse(tables_file)

        assert isinstance(tables, dict)
        assert len(tables) > 0
        assert all(isinstance(table, Table) for table in tables.values())

    def test_parse_tables_namespace_fallback(self, tmp_path):
        """Test parsing tables without namespaces."""
        # Create XML without namespaces
        xml_content = """<?xml version="1.0"?>
        <dataroot>
          <Analysis_Tables>
            <TableID>1</TableID>
            <TableName>TestTable</TableName>
          </Analysis_Tables>
        </dataroot>"""

        xml_file = tmp_path / "no_namespace.xml"
        xml_file.write_text(xml_content)

        parser = TableParser(AnalysisConfig())
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
        </dataroot>"""

        xml_file = tmp_path / "invalid.xml"
        xml_file.write_text(xml_content)

        parser = TableParser(AnalysisConfig())
        tables = parser.parse(xml_file)

        # Should skip invalid entries but not crash
        assert isinstance(tables, dict)
```

### Dependency Analyzer Tests (test_analyzer.py)

#### Core Analysis Tests
```python
class TestDependencyAnalyzer:
    def test_analyze_empty_data(self):
        """Test analysis with empty datasets."""
        analyzer = DependencyAnalyzer(AnalysisConfig())
        result = analyzer.analyze({}, {}, [], [])

        assert result.tables == {}
        assert result.statistics.total_tables == 0
        assert result.statistics.used_tables == 0
        assert result.statistics.unused_tables == 0

    def test_identify_unused_tables(self, sample_tables):
        """Test identification of unused tables."""
        analyzer = DependencyAnalyzer(AnalysisConfig())

        # No dependencies = all tables unused
        result = analyzer.analyze(sample_tables, {}, [], [])

        assert result.statistics.unused_tables == len(sample_tables)
        assert result.statistics.used_tables == 0

    def test_identify_used_tables(self, sample_tables):
        """Test identification of used tables."""
        analyzer = DependencyAnalyzer(AnalysisConfig())

        # Create dependencies for some tables
        objects = {100: DatabaseObject(100, "TestForm", "Form")}
        table_deps = [
            TableDependency(100, 1, True),  # Table 1 is used
        ]

        result = analyzer.analyze(sample_tables, objects, table_deps, [])

        assert result.tables[1].is_used == True
        assert result.statistics.used_tables == 1
        assert result.statistics.unused_tables == len(sample_tables) - 1

    def test_respect_inactive_dependencies(self, sample_tables):
        """Test that inactive dependencies don't mark tables as used."""
        analyzer = DependencyAnalyzer(AnalysisConfig())

        objects = {100: DatabaseObject(100, "TestForm", "Form")}
        table_deps = [
            TableDependency(100, 1, False),  # Inactive dependency
        ]

        result = analyzer.analyze(sample_tables, objects, table_deps, [])

        assert result.tables[1].is_used == False
        assert result.statistics.used_tables == 0

    def test_transitive_dependencies(self):
        """Test handling of transitive dependencies through object chains."""
        analyzer = DependencyAnalyzer(AnalysisConfig())

        # Form references Query, Query references Table
        objects = {
            100: DatabaseObject(100, "TestForm", "Form"),
            200: DatabaseObject(200, "TestQuery", "Query"),
        }
        table_deps = [
            TableDependency(200, 1, True),  # Query uses table
        ]
        object_deps = [
            ObjectDependency(100, 200, True),  # Form uses query
        ]

        tables = {1: Table(1, "TestTable")}
        result = analyzer.analyze(tables, objects, table_deps, object_deps)

        # Table should be marked as used due to transitive dependency
        assert result.tables[1].is_used == True
```

### HTML Generator Tests (test_generators.py)

#### HTML Generation Tests
```python
class TestHTMLGenerator:
    def test_generate_basic_report(self, sample_analysis_result):
        """Test basic HTML report generation."""
        generator = HTMLGenerator(AnalysisConfig())
        html = generator.generate(sample_analysis_result)

        assert isinstance(html, str)
        assert "<!DOCTYPE html>" in html
        assert "Database Dependency Analysis Report" in html

    def test_embed_analysis_data(self, sample_analysis_result):
        """Test that analysis data is embedded in HTML."""
        generator = HTMLGenerator(AnalysisConfig())
        html = generator.generate(sample_analysis_result)

        assert "analysis-data" in html
        # Should contain JSON data
        assert '"tables"' in html
        assert '"statistics"' in html

    def test_self_contained_html(self, sample_analysis_result):
        """Test that generated HTML is self-contained."""
        generator = HTMLGenerator(AnalysisConfig())
        html = generator.generate(sample_analysis_result)

        # Should not reference external resources
        assert "http://" not in html
        assert "https://" not in html
        assert "cdn." not in html

        # Should contain embedded CSS and JS
        assert "<style>" in html
        assert "<script>" in html

    def test_color_coding(self, sample_analysis_result):
        """Test that tables are color-coded correctly."""
        generator = HTMLGenerator(AnalysisConfig())
        html = generator.generate(sample_analysis_result)

        # Should contain CSS classes for used/unused tables
        assert "table-used" in html or "used" in html
        assert "table-unused" in html or "unused" in html
```

## Integration Test Specifications

### Full Workflow Tests (integration/test_full_workflow.py)

```python
class TestFullWorkflow:
    @pytest.mark.integration
    def test_complete_analysis_workflow(self, test_data_dir, tmp_path):
        """Test complete analysis workflow from XML to HTML."""
        # Setup input files
        tables_file = test_data_dir / "xml" / "sample_tables.xml"
        objects_file = test_data_dir / "xml" / "sample_objects.xml"
        table_deps_file = test_data_dir / "xml" / "sample_table_deps.xml"
        object_deps_file = test_data_dir / "xml" / "sample_object_deps.xml"

        # Setup output file
        output_file = tmp_path / "report.html"

        # Create config
        config = AnalysisConfig(
            tables_file=tables_file,
            objects_file=objects_file,
            table_dependencies_file=table_deps_file,
            object_dependencies_file=object_deps_file,
            output_file=output_file
        )

        # Run analysis
        analyzer = DependencyAnalyzer(config)
        html_gen = HTMLGenerator(config)

        # Parse data
        table_parser = TableParser(config)
        object_parser = ObjectParser(config)
        dep_parser = DependencyParser(config)

        tables = table_parser.parse(tables_file)
        objects = object_parser.parse(objects_file)
        table_deps = dep_parser.parse_table_dependencies(table_deps_file)
        object_deps = dep_parser.parse_object_dependencies(object_deps_file)

        # Analyze
        result = analyzer.analyze(tables, objects, table_deps, object_deps)

        # Generate report
        html = html_gen.generate(result)

        # Verify output
        assert output_file.exists()
        assert len(html) > 1000  # Reasonable HTML length

        # Verify HTML content
        content = output_file.read_text()
        assert "Database Dependency Analysis Report" in content
        assert "Summary Statistics" in content

    @pytest.mark.integration
    def test_cli_workflow(self, test_data_dir, tmp_path):
        """Test command-line interface workflow."""
        output_file = tmp_path / "cli_report.html"

        # Run CLI command
        result = subprocess.run([
            "python", "-m", "database_dependency_analyzer.main",
            str(test_data_dir / "xml" / "sample_tables.xml"),
            str(test_data_dir / "xml" / "sample_objects.xml"),
            str(test_data_dir / "xml" / "sample_table_deps.xml"),
            str(test_data_dir / "xml" / "sample_object_deps.xml"),
            "--output", str(output_file)
        ], capture_output=True, text=True)

        assert result.returncode == 0
        assert output_file.exists()
        assert "Analysis complete" in result.stdout
```

### Large Dataset Tests (integration/test_large_dataset.py)

```python
class TestLargeDataset:
    @pytest.mark.integration
    @pytest.mark.slow
    def test_large_dataset_parsing(self):
        """Test parsing large XML files."""
        # Generate large test data
        large_xml = generate_large_xml_file(10000)  # 10k tables

        config = AnalysisConfig()
        parser = TableParser(config)

        start_time = time.time()
        tables = parser.parse(large_xml)
        end_time = time.time()

        # Should parse within reasonable time
        assert end_time - start_time < 30  # 30 seconds max
        assert len(tables) == 10000

    @pytest.mark.integration
    @pytest.mark.slow
    def test_large_dataset_analysis(self):
        """Test analysis of large datasets."""
        # Generate large dataset
        tables, objects, deps = generate_large_dataset(
            num_tables=5000,
            num_objects=15000,
            num_deps=20000
        )

        config = AnalysisConfig()
        analyzer = DependencyAnalyzer(config)

        start_time = time.time()
        result = analyzer.analyze(tables, objects, deps, [])
        end_time = time.time()

        # Should analyze within 5 seconds
        assert end_time - start_time < 5.0
        assert result.statistics.total_tables == 5000
```

## Performance Test Specifications

### Benchmark Tests (performance/benchmark_analysis.py)

```python
import pytest_benchmark

class BenchmarkAnalysis:
    @pytest.mark.performance
    def test_analysis_performance_small(self, benchmark, sample_data_small):
        """Benchmark analysis performance with small dataset."""
        tables, objects, table_deps, object_deps = sample_data_small
        analyzer = DependencyAnalyzer(AnalysisConfig())

        result = benchmark(
            analyzer.analyze,
            tables, objects, table_deps, object_deps
        )

        assert result.statistics.total_tables > 0

    @pytest.mark.performance
    def test_analysis_performance_large(self, benchmark, sample_data_large):
        """Benchmark analysis performance with large dataset."""
        tables, objects, table_deps, object_deps = sample_data_large
        analyzer = DependencyAnalyzer(AnalysisConfig())

        result = benchmark(
            analyzer.analyze,
            tables, objects, table_deps, object_deps
        )

        # Performance assertion
        assert result.statistics.total_tables > 1000
        # Benchmark will track execution time automatically

    @pytest.mark.performance
    def test_memory_usage(self, sample_data_large):
        """Test memory usage during analysis."""
        import psutil
        import os

        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB

        tables, objects, table_deps, object_deps = sample_data_large
        analyzer = DependencyAnalyzer(AnalysisConfig())

        result = analyzer.analyze(tables, objects, table_deps, object_deps)

        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_used = final_memory - initial_memory

        # Should not use excessive memory
        assert memory_used < 500  # 500MB limit
        assert result is not None
```

### Parsing Performance Tests (performance/benchmark_parsing.py)

```python
class BenchmarkParsing:
    @pytest.mark.performance
    def test_xml_parsing_performance(self, benchmark):
        """Benchmark XML parsing performance."""
        # Create large XML file
        xml_content = generate_large_xml_content(5000)

        config = AnalysisConfig()
        parser = TableParser(config)

        def parse_xml():
            with tempfile.NamedTemporaryFile(mode='w', suffix='.xml', delete=False) as f:
                f.write(xml_content)
                temp_file = Path(f.name)

            try:
                return parser.parse(temp_file)
            finally:
                temp_file.unlink()

        result = benchmark(parse_xml)
        assert len(result) == 5000
```

## Test Data Management

### Test Fixture Generation

#### XML Generator (tests/utils/xml_generator.py)
```python
def generate_sample_tables_xml(num_tables: int = 10) -> str:
    """Generate sample XML for testing."""
    xml_parts = ['<?xml version="1.0" encoding="utf-8"?>',
                 '<dataroot xmlns:od="urn:schemas-microsoft-com:officedata">']

    for i in range(1, num_tables + 1):
        xml_parts.extend([
            '  <Analysis_Tables>',
            f'    <TableID>{i}</TableID>',
            f'    <TableName>Table{i}</TableName>',
            '  </Analysis_Tables>'
        ])

    xml_parts.append('</dataroot>')
    return '\n'.join(xml_parts)

def generate_realistic_dataset() -> Tuple[Dict[int, Table], Dict[int, DatabaseObject], List[TableDependency]]:
    """Generate realistic test dataset."""
    # Create tables
    tables = {}
    for i in range(1, 101):  # 100 tables
        tables[i] = Table(i, f"Table{i}")

    # Create objects
    objects = {}
    object_types = ["Form", "Query", "Macro", "Report"]
    for i in range(1, 51):  # 50 objects
        obj_type = object_types[(i-1) % len(object_types)]
        objects[i] = DatabaseObject(i, f"{obj_type}{i}", obj_type)

    # Create dependencies (some tables unused)
    deps = []
    used_tables = set()

    # Create dependencies for 70% of tables
    for table_id in range(1, 71):
        object_id = (table_id % 50) + 1
        deps.append(TableDependency(object_id, table_id, True))
        used_tables.add(table_id)

    # Mark used tables
    for table_id in used_tables:
        tables[table_id].is_used = True

    return tables, objects, deps
```

### Expected Results (tests/fixtures/json/)

Store expected analysis results as JSON for comparison:

```json
{
  "statistics": {
    "total_tables": 100,
    "used_tables": 70,
    "unused_tables": 30,
    "total_objects": 50
  },
  "unused_table_ids": [71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100]
}
```

## Quality Assurance

### Coverage Requirements

- **Unit Tests**: >90% coverage
- **Integration Tests**: Cover all major workflows
- **Edge Cases**: Test error conditions and boundary cases
- **Performance**: Track and prevent regressions

### Test Execution

#### Local Development
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=database_dependency_analyzer

# Run specific test categories
pytest -m unit
pytest -m integration
pytest -m performance

# Run slow tests
pytest -m slow
```

#### CI/CD Pipeline
```yaml
# .github/workflows/test.yml
name: Test

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: [3.8, 3.9, "3.10", "3.11"]

    steps:
    - uses: actions/checkout@v3
    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}

    - name: Install dependencies
      run: pip install -e .[dev]

    - name: Run unit tests
      run: pytest tests/unit/ --cov=database_dependency_analyzer --cov-report=xml

    - name: Run integration tests
      run: pytest tests/integration/

    - name: Run performance tests
      run: pytest tests/performance/ -m performance

    - name: Upload coverage
      uses: codecov/codecov-action@v3
```

### Test Maintenance

#### Regular Tasks
- Update test data when schema changes
- Review and update performance benchmarks
- Add tests for new features
- Remove obsolete tests

#### Test Data Updates
When XML schema or business logic changes:
1. Update test fixtures
2. Update expected results
3. Review and update assertions
4. Run full test suite

## Success Criteria

### Test Coverage
- ✅ >90% code coverage across all modules
- ✅ All critical paths tested
- ✅ Error conditions handled
- ✅ Edge cases covered

### Test Quality
- ✅ Tests are fast and reliable
- ✅ Clear test names and documentation
- ✅ Realistic test data
- ✅ Proper mocking of dependencies

### Performance
- ✅ Analysis completes within time limits
- ✅ Memory usage stays within bounds
- ✅ No performance regressions

### Integration
- ✅ End-to-end workflows work correctly
- ✅ CLI interface functions properly
- ✅ HTML reports generate successfully

This comprehensive test plan ensures the Database Dependency Analyzer is thoroughly tested, reliable, and maintainable.