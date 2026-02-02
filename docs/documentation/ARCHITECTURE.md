# Database Dependency Analyzer - System Architecture

## Overview

The Database Dependency Analyzer is a production-grade utility for analyzing Microsoft Access database dependencies. It parses XML exports from Access databases to identify unused tables and generates comprehensive HTML reports.

## Core Requirements

- **Input**: 4 XML files exported from Microsoft Access Analysis tables
- **Output**: HTML report with dependency visualization and console summary
- **Performance**: Handle 500+ tables and 6000+ objects efficiently
- **Robustness**: Proper XML namespace handling and error recovery

## System Architecture

### High-Level Components

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   XML Parser    │───▶│  Data Models    │───▶│ Dependency      │
│   (Namespace    │    │  (Validation)   │    │ Analyzer        │
│    Aware)       │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                                          │
                                                          ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│ HTML Report     │◀───│ Statistics      │◀───│ Console Output  │
│ Generator       │    │ Calculator      │    │ Formatter       │
│ (Responsive)    │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### Component Details

#### 1. XML Parser Module
**Responsibility**: Parse all 4 XML files with proper namespace handling

**Key Features**:
- Namespace-aware parsing using `xml.etree.ElementTree`
- Error handling for malformed XML
- Progress indication for large files
- Memory-efficient streaming for large datasets

**Files**:
- `src/parsers/xml_parser.py` - Base XML parsing utilities
- `src/parsers/table_parser.py` - Analysis_Tables.xml parsing
- `src/parsers/object_parser.py` - Analysis_Objects.xml parsing
- `src/parsers/dependency_parser.py` - Dependency XML parsing

#### 2. Data Model Module
**Responsibility**: Define and validate data structures

**Key Classes**:
```python
@dataclass
class Table:
    table_id: int
    table_name: str
    is_used: bool = False
    referencing_objects: List[ObjectReference] = field(default_factory=list)

@dataclass
class DatabaseObject:
    object_id: int
    object_name: str
    object_type: str  # Form, Query, Macro, Report

@dataclass
class AnalysisResult:
    tables: Dict[int, Table]
    objects: Dict[int, DatabaseObject]
    statistics: AnalysisStatistics
```

#### 3. Dependency Analyzer Module
**Responsibility**: Core business logic for identifying unused tables

**Algorithm**:
1. Load all tables, objects, and dependencies
2. Build dependency graph (objects → tables)
3. Mark tables as used if they have active dependencies
4. Handle transitive dependencies through object-to-object relationships
5. Calculate statistics

**Key Features**:
- Respects "Active" flag in dependencies
- Handles indirect dependencies through query chains
- Performance optimized for large datasets

**Files**:
- `src/analyzers/dependency_analyzer.py` - Core analysis logic
- `src/analyzers/statistics_calculator.py` - Statistics computation ✅
- `src/analyzers/usage_tracker.py` - Table usage tracking ✅

#### 4. HTML Report Generator Module
**Responsibility**: Create responsive, self-contained HTML reports

**Features**:
- Single HTML file output (no external dependencies)
- Responsive design with sidebar and main content
- Color-coded table status (green=used, red=unused)
- Object type color coding
- Interactive filtering and sorting
- Modern CSS with gradient headers

#### 5. Console Output Module
**Responsibility**: Provide clear command-line interface and progress feedback

**Features**:
- Progress bars for long operations
- Clear summary statistics
- Error messages with helpful suggestions
- Verbose/debug output options

## Technology Stack

### Primary Implementation (Python)
- **Language**: Python 3.8+
- **XML Parsing**: `xml.etree.ElementTree` with namespace support
- **Data Structures**: `dataclasses` and `typing` for type safety
- **Testing**: `pytest` with fixtures
- **Code Quality**: `black`, `isort`, `flake8`
- **Documentation**: `sphinx`

### Alternative Implementation (Node.js/TypeScript)
- **Language**: TypeScript
- **XML Parsing**: `xml2js` or `fast-xml-parser`
- **Build Tool**: `esbuild`
- **Testing**: `jest`

## Project Structure

```
database_dependency_analyzer/
├── src/
│   ├── main.py                    # CLI entry point
│   ├── config.py                  # Configuration management
│   ├── parsers/                   # XML parsing modules
│   ├── models/                    # Data model definitions
│   ├── analyzers/                 # Core analysis logic
│   ├── generators/                # Output generation
│   └── utils/                     # Utilities and helpers
├── tests/                         # Comprehensive test suite
├── docs/                          # Documentation
├── requirements.txt               # Python dependencies
├── package.json                   # Node.js dependencies (alt)
├── Dockerfile                     # Containerization
└── pyproject.toml                 # Python project config
```

## Agent Task Breakdown

### Agent Roles for Parallel Development

#### 1. XML Parser Agent
**Focus**: Robust XML parsing with namespace handling
**Deliverables**:
- Namespace-aware XML parser
- Error handling and validation
- Progress indication
- Memory-efficient processing

#### 2. Data Model Agent
**Focus**: Type-safe data structures and validation
**Deliverables**:
- Complete data model definitions
- Input validation logic
- Data transformation utilities
- Type hints and documentation

#### 3. Dependency Analyzer Agent
**Focus**: Core business logic and algorithms
**Deliverables**:
- Dependency graph construction
- Unused table detection algorithm
- Statistics calculation
- Performance optimization

#### 4. HTML Generator Agent
**Focus**: Report generation and styling
**Deliverables**:
- Responsive HTML templates
- CSS styling with modern design
- Interactive JavaScript (optional)
- Self-contained output files

#### 5. Console Output Agent
**Focus**: Command-line interface and user experience
**Deliverables**:
- CLI argument parsing
- Progress indicators
- Error messaging
- Help documentation

#### 6. Test Engineer Agent
**Focus**: Comprehensive testing and quality assurance
**Deliverables**:
- Unit tests for all modules
- Integration tests
- Performance benchmarks
- Test fixtures with sample data

## Implementation Phases

### Phase 1: Core Functionality (Must Have)
1. XML parsing for all 4 file types
2. Basic data model implementation
3. Dependency analysis algorithm
4. Console output with summary
5. Simple HTML report generation

### Phase 2: Enhanced Reporting (Should Have)
1. Responsive HTML design
2. Color-coded visualizations
3. Interactive filtering
4. Comprehensive statistics
5. Error handling improvements

### Phase 3: Advanced Features (Nice to Have)
1. Dependency chain visualization
2. Export to CSV/JSON
3. Performance optimizations
4. Configuration file support
5. Plugin architecture

## Success Criteria

- ✅ Handles all 4 XML files without errors
- ✅ Correctly identifies unused tables
- ✅ Generates valid, responsive HTML reports
- ✅ Performance acceptable for large databases (< 5 seconds)
- ✅ Code is modular and well-documented
- ✅ Comprehensive test coverage
- ✅ Clear error messages and user guidance

## Quality Standards

### Code Quality
- Type hints on all public functions
- Comprehensive docstrings
- PEP 8 compliance
- 80%+ test coverage
- No linting errors

### Performance
- Memory efficient for large datasets
- Fast analysis (< 5 seconds for 500 tables)
- Scalable architecture
- Progress feedback for long operations

### Reliability
- Robust error handling
- Input validation
- Graceful degradation
- Clear error messages

## Deployment

### Python Package
- Installable via pip
- Command-line interface
- Docker container available
- Cross-platform compatibility

### Usage
```bash
# Install
pip install database-dependency-analyzer

# Run analysis
db-analyzer Analysis_Tables.xml Analysis_Objects.xml \
           Analysis_TableDependencies.xml Analysis_ObjectDependencies.xml \
           --output report.html --verbose
```

## Future Enhancements

- Web interface (Flask/FastAPI backend)
- Database comparison (diff between exports)
- Automated cleanup recommendations
- Integration with CI/CD pipelines
- Support for other database formats