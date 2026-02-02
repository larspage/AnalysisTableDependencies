# Database Dependency Analyzer

A Python utility for analyzing Microsoft Access database dependencies. This tool parses XML exports from Access databases to identify unused tables and generates comprehensive HTML reports.

## Features

- Parses 4 XML files exported from Microsoft Access Analysis tables
- Identifies unused tables through dependency analysis
- Generates responsive HTML reports with dependency visualization
- Command-line interface with progress feedback
- Handles large databases (500+ tables, 6000+ objects) efficiently

## Installation

```bash
pip install database-dependency-analyzer
```

## Usage

```bash
db-analyzer Analysis_Tables.xml Analysis_Objects.xml \
           Analysis_TableDependencies.xml Analysis_ObjectDependencies.xml \
           --output report.html --verbose
```

## Requirements

- Python 3.8+
- XML files exported from Microsoft Access

## Development

This project uses a modular architecture with separate modules for parsing, analysis, and report generation.

## License

[Add license information]