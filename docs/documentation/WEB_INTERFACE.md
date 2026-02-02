# Web Interface Documentation

## Overview

The Database Dependency Analyzer includes a Flask-based web interface that provides an interactive way to:
- Upload XML files for analysis
- View analysis results with statistics
- Download HTML reports
- Access analysis via REST API

## Installation

Add Flask to your dependencies:
```bash
pip install flask werkzeug
```

Or use the project's virtual environment:
```bash
./venv/bin/pip install flask werkzeug
```

## Running the Web Server

### Development Mode

```bash
cd src/database_dependency_analyzer
python -m web.app
```

The server will start on `http://localhost:5000` by default.

### Custom Configuration

```python
from database_dependency_analyzer.web import run_server

# Run with custom host and port
run_server(host='0.0.0.0', port=8080, debug=True)
```

## Web Interface

### Upload Page (`/`)

The main page allows you to upload four XML files:
- **Tables XML**: Analysis_Tables.xml containing table definitions
- **Objects XML**: Analysis_Objects.xml containing database objects
- **Table Dependencies XML**: Analysis_TableDependencies.xml
- **Object Dependencies XML**: Analysis_ObjectDependencies.xml

### Results Page (`/session/{session_id}`)

After uploading files, you'll be redirected to a results page showing:
- Summary statistics (total tables, used/unused tables, total objects)
- Tabbed interface for viewing:
  - Full HTML report
  - Usage table
  - Statistics
- Download report button

### Error Page (`/error`)

Displayed when sessions expire or errors occur.

## REST API

### Upload Files

**Endpoint:** `POST /upload`

**Content-Type:** `multipart/form-data`

**Parameters:**
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| tables | File | Yes | Tables XML file |
| objects | File | Yes | Objects XML file |
| table_dependencies | File | Yes | Table dependencies XML |
| object_dependencies | File | Yes | Object dependencies XML |

**Response:**
```json
{
  "success": true,
  "session_id": "uuid-string",
  "statistics": {
    "total_tables": 10,
    "used_tables": 7,
    "unused_tables": 3,
    "total_objects": 15,
    "unused_object_count": 2,
    "table_dependency_count": 25,
    "object_dependency_count": 30
  },
  "usage_summary": {
    "unused_object_count": 2,
    "objects": [...]
  }
}
```

### Get Session Data

**Endpoint:** `GET /session/{session_id}/data`

**Response:** Full analysis results including HTML report.

### Download Report

**Endpoint:** `GET /session/{session_id}/download`

Downloads the HTML report as a file.

### API Analysis Endpoint

**Endpoint:** `POST /api/analyze`

**Content-Type:** `application/json`

**Parameters:**
```json
{
  "tables": "/path/to/tables.xml",
  "objects": "/path/to/objects.xml",
  "table_dependencies": "/path/to/table_deps.xml",
  "object_dependencies": "/path/to/object_deps.xml"
}
```

### Health Check

**Endpoint:** `GET /health`

**Response:**
```json
{
  "status": "healthy"
}
```

## Project Structure

```
src/database_dependency_analyzer/web/
├── __init__.py          # Module exports
├── app.py               # Flask application and routes
└── templates/
    ├── index.html       # Upload page
    ├── results.html     # Results display page
    └── error.html       # Error page
```

## Testing

Run the web interface tests:
```bash
./venv/bin/python -m pytest tests/test_web.py -v
```

All 17 tests verify:
- File upload handling
- Error handling for missing/invalid files
- Session management
- API endpoints
- Full upload and analysis flow

## Configuration

### Maximum File Size

Default: 50MB

```python
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024
```

### Allowed Extensions

Default: XML files only

```python
ALLOWED_EXTENSIONS = {'xml'}
```

## Security Notes

- Temporary files are automatically cleaned up after analysis
- File uploads are validated for type and content
- Sessions are stored in memory (use Redis/database for production)
- Input sanitization is applied to filenames
