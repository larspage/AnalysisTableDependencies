# Data Models and Interfaces

## Overview

This document defines the data structures and interfaces used throughout the Database Dependency Analyzer. All models are designed for type safety, validation, and efficient processing of large datasets.

## Core Data Models

### Table Model

Represents a database table with its usage information.

```python
@dataclass(frozen=True)
class Table:
    """Represents a database table and its usage information."""

    table_id: int
    table_name: str
    is_used: bool = False
    referencing_objects: List['ObjectReference'] = field(default_factory=list)

    def __post_init__(self):
        """Validate table data after initialization."""
        if not isinstance(self.table_id, int) or self.table_id <= 0:
            raise ValueError(f"Invalid table_id: {self.table_id}")
        if not self.table_name or not self.table_name.strip():
            raise ValueError(f"Invalid table_name: {self.table_name}")

    @property
    def status(self) -> str:
        """Return human-readable status."""
        return "Used" if self.is_used else "Unused"

    def add_reference(self, obj_ref: 'ObjectReference') -> None:
        """Add an object reference to this table."""
        if obj_ref not in self.referencing_objects:
            self.referencing_objects.append(obj_ref)
            # Update usage status if we have active references
            if obj_ref.active:
                object.__setattr__(self, 'is_used', True)
```

### ObjectReference Model

Represents a reference from an object to a table.

```python
@dataclass(frozen=True)
class ObjectReference:
    """Represents a reference from a database object to a table."""

    object_id: int
    object_name: str
    object_type: str  # Form, Query, Macro, Report
    active: bool = True

    VALID_OBJECT_TYPES = {'Form', 'Query', 'Macro', 'Report'}

    def __post_init__(self):
        """Validate object reference data."""
        if not isinstance(self.object_id, int) or self.object_id <= 0:
            raise ValueError(f"Invalid object_id: {self.object_id}")
        if not self.object_name or not self.object_name.strip():
            raise ValueError(f"Invalid object_name: {self.object_name}")
        if self.object_type not in self.VALID_OBJECT_TYPES:
            raise ValueError(f"Invalid object_type: {self.object_type}. "
                           f"Must be one of {self.VALID_OBJECT_TYPES}")

    @property
    def display_name(self) -> str:
        """Return formatted display name with type."""
        return f"{self.object_type}: {self.object_name}"

    @property
    def css_class(self) -> str:
        """Return CSS class for styling based on object type."""
        return f"object-{self.object_type.lower()}"
```

### DatabaseObject Model

Represents a database object (Form, Query, Macro, Report).

```python
@dataclass(frozen=True)
class DatabaseObject:
    """Represents a database object (Form, Query, Macro, Report)."""

    object_id: int
    object_name: str
    object_type: str

    VALID_OBJECT_TYPES = {'Form', 'Query', 'Macro', 'Report'}

    def __post_init__(self):
        """Validate database object data."""
        if not isinstance(self.object_id, int) or self.object_id <= 0:
            raise ValueError(f"Invalid object_id: {self.object_id}")
        if not self.object_name or not self.object_name.strip():
            raise ValueError(f"Invalid object_name: {self.object_name}")
        if self.object_type not in self.VALID_OBJECT_TYPES:
            raise ValueError(f"Invalid object_type: {self.object_type}. "
                           f"Must be one of {self.VALID_OBJECT_TYPES}")

    @property
    def css_class(self) -> str:
        """Return CSS class for styling."""
        return f"object-{self.object_type.lower()}"
```

### Dependency Relationship Models

```python
@dataclass(frozen=True)
class TableDependency:
    """Represents a dependency from an object to a table."""

    object_id: int
    table_id: int
    active: bool = True

    def __post_init__(self):
        """Validate dependency data."""
        if not isinstance(self.object_id, int) or self.object_id <= 0:
            raise ValueError(f"Invalid object_id: {self.object_id}")
        if not isinstance(self.table_id, int) or self.table_id <= 0:
            raise ValueError(f"Invalid table_id: {self.table_id}")

@dataclass(frozen=True)
class ObjectDependency:
    """Represents a dependency from one object to another."""

    source_object_id: int
    target_object_id: int
    active: bool = True

    def __post_init__(self):
        """Validate dependency data."""
        if not isinstance(self.source_object_id, int) or self.source_object_id <= 0:
            raise ValueError(f"Invalid source_object_id: {self.source_object_id}")
        if not isinstance(self.target_object_id, int) or self.target_object_id <= 0:
            raise ValueError(f"Invalid target_object_id: {self.target_object_id}")
```

## Analysis Results Model

```python
@dataclass
class AnalysisResult:
    """Contains the complete results of a dependency analysis."""

    tables: Dict[int, Table]
    objects: Dict[int, DatabaseObject]
    statistics: 'AnalysisStatistics'
    processing_time: float
    timestamp: datetime = field(default_factory=datetime.now)

    def get_unused_tables(self) -> List[Table]:
        """Return list of unused tables."""
        return [table for table in self.tables.values() if not table.is_used]

    def get_used_tables(self) -> List[Table]:
        """Return list of used tables."""
        return [table for table in self.tables.values() if table.is_used]

    def get_table_by_name(self, name: str) -> Optional[Table]:
        """Find table by name (case-insensitive)."""
        for table in self.tables.values():
            if table.table_name.lower() == name.lower():
                return table
        return None
```

## Statistics Model

```python
@dataclass(frozen=True)
class AnalysisStatistics:
    """Statistical summary of the analysis results."""

    total_tables: int
    used_tables: int
    unused_tables: int
    total_objects: int
    objects_by_type: Dict[str, int]
    total_dependencies: int
    active_dependencies: int

    @property
    def usage_percentage(self) -> float:
        """Return percentage of tables that are used."""
        if self.total_tables == 0:
            return 0.0
        return (self.used_tables / self.total_tables) * 100

    @property
    def unused_percentage(self) -> float:
        """Return percentage of tables that are unused."""
        if self.total_tables == 0:
            return 0.0
        return (self.unused_tables / self.total_tables) * 100

    def summary_text(self) -> str:
        """Return formatted summary text."""
        return (f"Analysis Summary:\n"
                f"  Total Tables: {self.total_tables}\n"
                f"  Used Tables: {self.used_tables} ({self.usage_percentage:.1f}%)\n"
                f"  Unused Tables: {self.unused_tables} ({self.unused_percentage:.1f}%)\n"
                f"  Total Objects: {self.total_objects}\n"
                f"  Dependencies: {self.active_dependencies}/{self.total_dependencies} active")
```

## Configuration Model

```python
@dataclass
class AnalysisConfig:
    """Configuration for the dependency analysis."""

    # Input files
    tables_file: Path
    objects_file: Path
    table_dependencies_file: Path
    object_dependencies_file: Path

    # Output options
    output_file: Optional[Path] = None
    console_output: bool = True
    verbose: bool = False

    # Processing options
    ignore_inactive_dependencies: bool = True
    max_workers: int = 4
    memory_limit_mb: int = 512

    def __post_init__(self):
        """Validate configuration."""
        required_files = [
            self.tables_file,
            self.objects_file,
            self.table_dependencies_file,
            self.object_dependencies_file
        ]

        for file_path in required_files:
            if not file_path.exists():
                raise FileNotFoundError(f"Required file not found: {file_path}")

        if self.output_file and self.output_file.exists():
            if not self.output_file.is_file():
                raise ValueError(f"Output path is not a file: {self.output_file}")

    @classmethod
    def from_args(cls, args: argparse.Namespace) -> 'AnalysisConfig':
        """Create config from command line arguments."""
        return cls(
            tables_file=Path(args.tables_file),
            objects_file=Path(args.objects_file),
            table_dependencies_file=Path(args.table_dependencies_file),
            object_dependencies_file=Path(args.object_dependencies_file),
            output_file=Path(args.output) if args.output else None,
            console_output=not args.quiet,
            verbose=args.verbose,
            ignore_inactive_dependencies=not args.include_inactive,
            max_workers=args.max_workers,
            memory_limit_mb=args.memory_limit
        )
```

## Interface Definitions

### Parser Interface

```python
class XMLParser(ABC):
    """Abstract base class for XML parsers."""

    def __init__(self, config: AnalysisConfig):
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)

    @abstractmethod
    def parse(self, file_path: Path) -> Any:
        """Parse the XML file and return structured data."""
        pass

    @abstractmethod
    def validate(self, data: Any) -> bool:
        """Validate the parsed data."""
        pass

class TableParser(XMLParser):
    """Parser for Analysis_Tables.xml"""

    def parse(self, file_path: Path) -> Dict[int, Table]:
        """Parse table definitions."""
        # Implementation details...

    def validate(self, tables: Dict[int, Table]) -> bool:
        """Validate table data."""
        # Implementation details...

class ObjectParser(XMLParser):
    """Parser for Analysis_Objects.xml"""

    def parse(self, file_path: Path) -> Dict[int, DatabaseObject]:
        """Parse object definitions."""
        # Implementation details...

    def validate(self, objects: Dict[int, DatabaseObject]) -> bool:
        """Validate object data."""
        # Implementation details...

class DependencyParser(XMLParser):
    """Parser for dependency XML files"""

    def parse_table_dependencies(self, file_path: Path) -> List[TableDependency]:
        """Parse table dependency relationships."""
        # Implementation details...

    def parse_object_dependencies(self, file_path: Path) -> List[ObjectDependency]:
        """Parse object dependency relationships."""
        # Implementation details...
```

### Analyzer Interface

```python
class DependencyAnalyzer(ABC):
    """Abstract base class for dependency analyzers."""

    def __init__(self, config: AnalysisConfig):
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)

    @abstractmethod
    def analyze(self,
                tables: Dict[int, Table],
                objects: Dict[int, DatabaseObject],
                table_deps: List[TableDependency],
                object_deps: List[ObjectDependency]) -> AnalysisResult:
        """Perform dependency analysis."""
        pass

class TableUsageAnalyzer(DependencyAnalyzer):
    """Analyzes table usage based on dependencies."""

    def analyze(self, tables, objects, table_deps, object_deps) -> AnalysisResult:
        """Analyze which tables are used and by which objects."""
        # Implementation details...
```

### Generator Interface

```python
class ReportGenerator(ABC):
    """Abstract base class for report generators."""

    def __init__(self, config: AnalysisConfig):
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)

    @abstractmethod
    def generate(self, result: AnalysisResult) -> str:
        """Generate report content."""
        pass

class HTMLReportGenerator(ReportGenerator):
    """Generates HTML reports."""

    def generate(self, result: AnalysisResult) -> str:
        """Generate complete HTML report."""
        # Implementation details...

class ConsoleOutputGenerator(ReportGenerator):
    """Generates console output."""

    def generate(self, result: AnalysisResult) -> str:
        """Generate formatted console output."""
        # Implementation details...
```

## Error Handling

### Custom Exceptions

```python
class AnalysisError(Exception):
    """Base exception for analysis errors."""
    pass

class XMLParseError(AnalysisError):
    """Raised when XML parsing fails."""
    pass

class ValidationError(AnalysisError):
    """Raised when data validation fails."""
    pass

class FileNotFoundError(AnalysisError):
    """Raised when required files are not found."""
    pass
```

## Type Hints and Validation

All models include comprehensive type hints and validation:

- Input validation in `__post_init__` methods
- Type-safe properties and methods
- Clear error messages for invalid data
- Immutable dataclasses where appropriate (using `frozen=True`)

## Usage Examples

```python
# Create a table
table = Table(
    table_id=1,
    table_name="Customers",
    is_used=True,
    referencing_objects=[
        ObjectReference(100, "CustomerForm", "Form", True),
        ObjectReference(200, "CustomerQuery", "Query", True)
    ]
)

# Create analysis result
result = AnalysisResult(
    tables={1: table},
    objects={},
    statistics=AnalysisStatistics(
        total_tables=1,
        used_tables=1,
        unused_tables=0,
        total_objects=2,
        objects_by_type={"Form": 1, "Query": 1},
        total_dependencies=2,
        active_dependencies=2
    ),
    processing_time=0.5
)

# Access computed properties
print(f"Usage: {result.statistics.usage_percentage:.1f}%")
print(f"Status: {table.status}")