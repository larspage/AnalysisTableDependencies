# Database Dependency Analyzer

A Python utility for analyzing Microsoft Access database dependencies. This tool parses XML exports from Access databases to identify unused tables and generates comprehensive HTML reports.

## Features

- Parses 4 XML files exported from Microsoft Access Analysis tables
- Identifies unused tables through dependency analysis
- Generates responsive HTML reports with dependency visualization
- Command-line interface with progress feedback
- **Interactive web interface** with file upload and REST API
- Handles large databases (500+ tables, 6000+ objects) efficiently

## Installation

```bash
pip install database-dependency-analyzer
```

For web interface features:
```bash
pip install flask werkzeug
```

## Usage

### Command Line

```bash
db-analyzer Analysis_Tables.xml Analysis_Objects.xml \
           Analysis_TableDependencies.xml Analysis_ObjectDependencies.xml \
           --output report.html --verbose
```

### Web Interface

Start the web server:
```bash
cd src/database_dependency_analyzer
python -m web.app
```

Then open http://localhost:5000 in your browser.

### REST API

Upload files for analysis:
```bash
curl -X POST -F "tables=@tables.xml" \
             -F "objects=@objects.xml" \
             -F "table_dependencies=@table_deps.xml" \
             -F "object_dependencies=@object_deps.xml" \
             http://localhost:5000/upload
```

Programmatic analysis:
```bash
curl -X POST http://localhost:5000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "tables": "/path/to/tables.xml",
    "objects": "/path/to/objects.xml",
    "table_dependencies": "/path/to/table_deps.xml",
    "object_dependencies": "/path/to/object_deps.xml"
  }'
```

## Requirements

- Python 3.8+
- XML files exported from Microsoft Access
- Flask (optional, for web interface)

## Documentation

- [Architecture](ARCHITECTURE.md) - System design overview
- [Implementation Phases](IMPLEMENTATION_PHASES.md) - Development roadmap
- [Web Interface](WEB_INTERFACE.md) - Web UI documentation
- [Test Plan](TEST_PLAN.md) - Testing strategy
- [API Documentation](API.md) - REST API reference

## Development

This project uses a modular architecture with separate modules for:
- **Parsers** - XML file parsing (`src/database_dependency_analyzer/parsers/`)
- **Analyzers** - Dependency analysis (`src/database_dependency_analyzer/analyzers/`)
- **Generators** - Report generation (`src/database_dependency_analyzer/generators/`)
- **Web** - Flask web interface (`src/database_dependency_analyzer/web/`)

### Running Tests

```bash
# Run all tests
./run_tests.sh

# Run specific test file
./venv/bin/python -m pytest tests/test_web.py -v
```

### Project Structure

```
src/database_dependency_analyzer/
├── parsers/          # XML parsing modules
│   ├── xml_parser.py
│   ├── table_parser.py
│   ├── object_parser.py
│   └── dependency_parser.py
├── analyzers/        # Analysis logic
│   ├── dependency_analyzer.py
│   ├── statistics_calculator.py
│   └── usage_tracker.py
├── generators/       # Report generation
│   └── html_generator.py
├── models/           # Data models
│   ├── table.py
│   ├── object.py
│   ├── dependency.py
│   └── analysis_result.py
├── web/              # Flask web interface
│   ├── app.py
│   └── templates/
│       ├── index.html
│       ├── results.html
│       └── error.html
└── console/          # CLI interface
    ├── argument_parser.py
    └── output_formatter.py
```

## License

[Add license information]
