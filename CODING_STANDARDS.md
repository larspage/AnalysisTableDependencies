# Coding Standards and Patterns

## Overview

This document establishes coding standards, patterns, and best practices for the Database Dependency Analyzer project. Consistent application of these standards ensures maintainable, readable, and reliable code across all modules.

## Python Standards

### Code Style

#### PEP 8 Compliance
- Use 4 spaces for indentation (no tabs)
- Limit lines to 88 characters (Black default)
- Use blank lines to separate logical sections
- Follow naming conventions:
  - `snake_case` for functions, variables, and methods
  - `PascalCase` for classes
  - `UPPER_CASE` for constants
  - `_private` prefix for private attributes/methods

#### Black Code Formatting
```python
# Configuration in pyproject.toml
[tool.black]
line-length = 88
target-version = ['py38']
include = '\.pyi?$'
extend-exclude = '''
/(
  # directories
  \.eggs
  | \.git
  | \.hg
  | \.mypy_cache
  | \.tox
  | \.venv
  | build
  | dist
)/
'''
```

#### isort Import Sorting
```python
# Configuration in pyproject.toml
[tool.isort]
profile = "black"
multi_line_output = 3
line_length = 88
known_first_party = ["database_dependency_analyzer"]
```

### Type Hints

#### Comprehensive Type Annotations
```python
from typing import Dict, List, Optional, Union, Any
from pathlib import Path
import datetime

def process_data(data: Dict[str, Any], output_path: Path) -> Optional[str]:
    """Process data and return result or None if failed."""
    pass

class DataProcessor:
    def __init__(self, config: 'AnalysisConfig') -> None:
        self.config = config
        self._cache: Dict[str, datetime.datetime] = {}

    def get_item(self, key: str) -> Union[DataItem, None]:
        """Retrieve item from cache."""
        return self._cache.get(key)
```

#### Generic Types
```python
from typing import TypeVar, Generic

T = TypeVar('T')

class Result(Generic[T]):
    def __init__(self, value: T, error: Optional[str] = None) -> None:
        self.value = value
        self.error = error

    @property
    def is_success(self) -> bool:
        return self.error is None
```

### Data Classes

#### Immutable Data Classes
```python
from dataclasses import dataclass, field
from typing import List

@dataclass(frozen=True)
class Table:
    """Immutable table representation."""
    table_id: int
    table_name: str
    is_used: bool = False
    referencing_objects: List['ObjectReference'] = field(default_factory=list)

    def __post_init__(self) -> None:
        """Validate after initialization."""
        if self.table_id <= 0:
            raise ValueError(f"Invalid table_id: {self.table_id}")
        if not self.table_name.strip():
            raise ValueError(f"Invalid table_name: {self.table_name}")

    @property
    def status(self) -> str:
        """Computed property."""
        return "Used" if self.is_used else "Unused"
```

#### Mutable Data Classes (When Needed)
```python
@dataclass
class AnalysisResult:
    """Mutable result container."""
    tables: Dict[int, Table] = field(default_factory=dict)
    statistics: Optional['AnalysisStatistics'] = None
    processing_time: float = 0.0

    def add_table(self, table: Table) -> None:
        """Add table to results."""
        self.tables[table.table_id] = table
```

### Error Handling

#### Custom Exceptions
```python
class AnalysisError(Exception):
    """Base exception for analysis operations."""
    pass

class XMLParseError(AnalysisError):
    """Raised when XML parsing fails."""
    pass

class ValidationError(AnalysisError):
    """Raised when data validation fails."""
    pass
```

#### Error Handling Patterns
```python
def parse_xml_file(file_path: Path) -> ET.ElementTree:
    """Parse XML with proper error handling."""
    try:
        tree = ET.parse(file_path)
        validate_root(tree.getroot())
        return tree
    except ET.ParseError as e:
        raise XMLParseError(f"Failed to parse {file_path}: {e}") from e
    except FileNotFoundError as e:
        raise FileNotFoundError(f"XML file not found: {file_path}") from e
    except Exception as e:
        logger.error(f"Unexpected error parsing {file_path}: {e}")
        raise AnalysisError(f"Failed to parse {file_path}") from e
```

#### Result Pattern for Operations
```python
from typing import Union

@dataclass
class Result(Generic[T]):
    value: Optional[T] = None
    error: Optional[str] = None

    @property
    def is_success(self) -> bool:
        return self.error is None

    @property
    def is_failure(self) -> bool:
        return self.error is not None

    @classmethod
    def success(cls, value: T) -> 'Result[T]':
        return cls(value=value)

    @classmethod
    def failure(cls, error: str) -> 'Result[T]':
        return cls(error=error)

def parse_table_data(data: Any) -> Result[Table]:
    """Parse table data with result pattern."""
    try:
        table = Table(
            table_id=data.get('id'),
            table_name=data.get('name')
        )
        return Result.success(table)
    except ValueError as e:
        return Result.failure(str(e))
```

### Logging

#### Structured Logging
```python
import logging
from typing import Optional

logger = logging.getLogger(__name__)

class LoggerMixin:
    """Mixin to provide logger to classes."""

    @property
    def logger(self) -> logging.Logger:
        """Get logger for this class."""
        return logging.getLogger(self.__class__.__module__ + '.' + self.__class__.__name__)

class DataParser(LoggerMixin):
    def parse(self, data: Any) -> Result[ParsedData]:
        self.logger.info(f"Starting parsing of {len(data)} items")

        try:
            result = self._do_parse(data)
            self.logger.info(f"Successfully parsed {len(result.items)} items")
            return Result.success(result)
        except Exception as e:
            self.logger.error(f"Failed to parse data: {e}", exc_info=True)
            return Result.failure(str(e))
```

#### Log Levels
- `DEBUG`: Detailed information for debugging
- `INFO`: General information about operations
- `WARNING`: Warning about potential issues
- `ERROR`: Error conditions that don't stop execution
- `CRITICAL`: Critical errors that may stop execution

### Documentation

#### Docstrings (Google Style)
```python
def analyze_dependencies(
    tables: Dict[int, Table],
    objects: Dict[int, DatabaseObject],
    table_deps: List[TableDependency],
    object_deps: List[ObjectDependency],
    config: AnalysisConfig
) -> AnalysisResult:
    """Analyze database dependencies to identify unused tables.

    This function performs a comprehensive analysis of database dependencies
    by building a dependency graph and identifying tables that are not
    referenced by any active database objects.

    Args:
        tables: Dictionary of table definitions keyed by table ID.
        objects: Dictionary of database objects keyed by object ID.
        table_deps: List of table-object dependency relationships.
        object_deps: List of object-object dependency relationships.
        config: Analysis configuration settings.

    Returns:
        AnalysisResult containing the analysis results and statistics.

    Raises:
        AnalysisError: If analysis fails due to invalid data or configuration.

    Example:
        >>> result = analyze_dependencies(tables, objects, deps, config)
        >>> print(f"Found {result.statistics.unused_tables} unused tables")
    """
```

#### Module Documentation
```python
"""Database dependency analysis module.

This module provides functionality for analyzing Microsoft Access database
dependencies from XML export files. It can identify unused tables and generate
comprehensive HTML reports.

Classes:
    DependencyAnalyzer: Core analysis engine
    AnalysisResult: Container for analysis results
    AnalysisStatistics: Statistical summary of analysis

Functions:
    analyze_database: Main entry point for database analysis
"""

__version__ = "1.0.0"
__author__ = "Database Dependency Analyzer Team"
```

### Testing Patterns

#### Unit Test Structure
```python
import pytest
from unittest.mock import Mock, patch

class TestDependencyAnalyzer:
    """Test cases for DependencyAnalyzer."""

    @pytest.fixture
    def sample_tables(self) -> Dict[int, Table]:
        """Provide sample table data for tests."""
        return {
            1: Table(table_id=1, table_name="Customers"),
            2: Table(table_id=2, table_name="Orders"),
        }

    @pytest.fixture
    def analyzer(self) -> DependencyAnalyzer:
        """Provide configured analyzer instance."""
        config = AnalysisConfig(...)
        return DependencyAnalyzer(config)

    def test_analyze_empty_dataset(self, analyzer: DependencyAnalyzer) -> None:
        """Test analysis with empty dataset."""
        result = analyzer.analyze({}, {}, [], [])

        assert result.tables == {}
        assert result.statistics.total_tables == 0

    def test_identify_unused_tables(self, analyzer: DependencyAnalyzer, sample_tables: Dict[int, Table]) -> None:
        """Test identification of unused tables."""
        # Tables with no dependencies should be marked unused
        objects = {}
        table_deps = []
        object_deps = []

        result = analyzer.analyze(sample_tables, objects, table_deps, object_deps)

        assert result.tables[1].is_used == False
        assert result.tables[2].is_used == False
        assert result.statistics.unused_tables == 2

    @patch('database_dependency_analyzer.analyzers.dependency_analyzer.logger')
    def test_error_handling(self, mock_logger: Mock, analyzer: DependencyAnalyzer) -> None:
        """Test error handling during analysis."""
        with pytest.raises(AnalysisError):
            analyzer.analyze(None, {}, [], [])  # type: ignore

        mock_logger.error.assert_called()
```

#### Test Organization
```
tests/
├── __init__.py
├── conftest.py              # Shared fixtures
├── test_models.py           # Data model tests
├── test_parsers.py          # XML parser tests
├── test_analyzer.py         # Analysis logic tests
├── test_generators.py       # Report generator tests
├── test_console.py          # CLI tests
├── integration/             # Integration tests
│   ├── test_full_workflow.py
│   └── test_large_dataset.py
└── fixtures/                # Test data
    ├── sample_tables.xml
    ├── sample_objects.xml
    └── sample_dependencies.xml
```

### Performance Patterns

#### Memory-Efficient Processing
```python
def process_large_dataset(data: List[Dict[str, Any]]) -> Iterator[ProcessedItem]:
    """Process large datasets with minimal memory usage."""
    for item in data:
        processed = self._process_item(item)
        yield processed
        # Allow garbage collection of intermediate data
        del item

def analyze_with_progress(
    data: List[Any],
    batch_size: int = 1000
) -> AnalysisResult:
    """Analyze data in batches to show progress."""
    results = []
    total_batches = (len(data) + batch_size - 1) // batch_size

    with tqdm(total=total_batches, desc="Analyzing") as pbar:
        for i in range(0, len(data), batch_size):
            batch = data[i:i + batch_size]
            batch_result = self._analyze_batch(batch)
            results.extend(batch_result)
            pbar.update(1)

    return self._combine_results(results)
```

#### Caching and Memoization
```python
from functools import lru_cache
from typing import Dict, Tuple

class AnalysisCache:
    """Cache for expensive analysis operations."""

    def __init__(self, max_size: int = 1000):
        self._cache: Dict[Tuple, Any] = {}
        self._max_size = max_size

    @lru_cache(maxsize=128)
    def get_dependency_chain(self, object_id: int) -> List[int]:
        """Get cached dependency chain for object."""
        # Expensive computation here
        return self._calculate_dependency_chain(object_id)

    def clear_cache(self) -> None:
        """Clear all cached results."""
        self._cache.clear()
        self.get_dependency_chain.cache_clear()
```

### Configuration Management

#### Configuration Classes
```python
from pydantic import BaseSettings, Field
from pathlib import Path

class XMLParserConfig(BaseSettings):
    """Configuration for XML parsing."""

    strict_namespaces: bool = Field(default=True, description="Require XML namespaces")
    max_parse_time: int = Field(default=300, description="Maximum parsing time in seconds")
    memory_limit_mb: int = Field(default=512, description="Memory limit for parsing")

    class Config:
        env_prefix = "XML_"

class AnalysisConfig(BaseSettings):
    """Main analysis configuration."""

    # Input files
    tables_file: Path
    objects_file: Path
    table_dependencies_file: Path
    object_dependencies_file: Path

    # Processing options
    max_workers: int = Field(default=4, description="Maximum worker threads")
    verbose: bool = Field(default=False, description="Enable verbose logging")

    # Output options
    output_file: Optional[Path] = Field(default=None, description="HTML output file")
    console_output: bool = Field(default=True, description="Enable console output")

    class Config:
        env_prefix = "DB_ANALYZER_"
```

### Security Considerations

#### Input Validation
```python
def validate_file_path(file_path: Path, allowed_extensions: List[str]) -> None:
    """Validate file path for security."""
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    if not file_path.is_file():
        raise ValueError(f"Path is not a file: {file_path}")

    if file_path.suffix.lower() not in allowed_extensions:
        raise ValueError(f"Invalid file extension: {file_path.suffix}")

    # Check for path traversal attempts
    resolved = file_path.resolve()
    if not str(resolved).startswith(str(Path.cwd())):
        raise SecurityError("Path traversal detected")

def sanitize_filename(filename: str) -> str:
    """Sanitize filename to prevent security issues."""
    # Remove dangerous characters
    safe_name = re.sub(r'[^\w\-_\.]', '', filename)
    return safe_name[:255]  # Limit length
```

### Asynchronous Patterns (Future Enhancement)

#### Async/Await Support
```python
import asyncio
from typing import Coroutine, Any

class AsyncAnalyzer:
    """Asynchronous analyzer for future performance improvements."""

    async def analyze_async(self, data: Any) -> AnalysisResult:
        """Analyze data asynchronously."""
        # Simulate async work
        await asyncio.sleep(0.1)
        return self._do_analysis(data)

    async def process_batch_async(self, batch: List[Any]) -> List[ProcessedItem]:
        """Process batch asynchronously."""
        tasks = [self._process_item_async(item) for item in batch]
        return await asyncio.gather(*tasks)

    async def _process_item_async(self, item: Any) -> ProcessedItem:
        """Process single item asynchronously."""
        # CPU-bound work in thread pool
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self._process_item_sync, item)
```

## Code Quality Tools

### Pre-commit Hooks
```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.4.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files

  - repo: https://github.com/psf/black
    rev: 22.10.0
    hooks:
      - id: black

  - repo: https://github.com/pycqa/isort
    rev: 5.10.1
    hooks:
      - id: isort

  - repo: https://github.com/pycqa/flake8
    rev: 5.0.5
    hooks:
      - id: flake8

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v0.991
    hooks:
      - id: mypy
```

### CI/CD Pipeline
```yaml
# .github/workflows/ci.yml
name: CI

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
      run: |
        python -m pip install --upgrade pip
        pip install -e .[dev]

    - name: Run tests
      run: |
        pytest --cov=database_dependency_analyzer --cov-report=xml

    - name: Upload coverage
      uses: codecov/codecov-action@v3
```

## Performance Benchmarks

### Benchmarking Patterns
```python
import time
from typing import Callable, Any

def benchmark_function(func: Callable, *args, **kwargs) -> Tuple[Any, float]:
    """Benchmark function execution time."""
    start_time = time.perf_counter()
    result = func(*args, **kwargs)
    end_time = time.perf_counter()

    execution_time = end_time - start_time
    return result, execution_time

def run_performance_tests():
    """Run performance benchmarks."""
    # Test with different dataset sizes
    dataset_sizes = [100, 1000, 10000]

    for size in dataset_sizes:
        data = generate_test_data(size)
        result, exec_time = benchmark_function(analyze_data, data)

        print(f"Dataset size {size}: {exec_time:.2f}s")
        assert exec_time < 5.0, f"Performance regression: {exec_time}s for {size} items"
```

## Maintenance Patterns

### Version Management
```python
# src/__init__.py
__version__ = "1.0.0"
__author__ = "Database Dependency Analyzer Team"
__description__ = "Analyze Microsoft Access database dependencies"

def get_version() -> str:
    """Get current version."""
    return __version__
```

### Deprecation Handling
```python
import warnings
from typing import Optional

def deprecated_function(old_name: str, new_name: str):
    """Decorator to mark functions as deprecated."""
    def decorator(func):
        def wrapper(*args, **kwargs):
            warnings.warn(
                f"{old_name} is deprecated, use {new_name} instead",
                DeprecationWarning,
                stacklevel=2
            )
            return func(*args, **kwargs)
        return wrapper
    return decorator

@deprecated_function("old_analyze", "analyze_dependencies")
def old_analyze(data: Any) -> Any:
    """Deprecated analysis function."""
    return analyze_dependencies(data)
```

This comprehensive coding standards document ensures consistency, maintainability, and quality across the entire Database Dependency Analyzer codebase.