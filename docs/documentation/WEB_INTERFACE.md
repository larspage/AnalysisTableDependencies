# Web Interface Documentation

## Overview

The Database Dependency Analyzer includes a Flask-based web interface that provides an interactive way to:
- Upload XML files for analysis
- View analysis results with statistics
- Download HTML reports
- Access analysis via REST API
- Explore dependencies as an interactive 3D force-directed graph

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

### 3D Graph Page (`/session/{session_id}/graph`)

An interactive 3D force-directed graph of all database object dependencies.
Launched via the **3D Graph** button on the Results page.

**Features:**
- **Ego-network view** — always shows one primary node centred, surrounded by its direct (L1) and second-level (L2) connections only. Everything else is hidden to reduce clutter.
- **Gold primary node** — the currently selected node is highlighted in gold and pinned at the centre.
- **Click to navigate** — clicking any visible node makes it the new primary; the camera flies smoothly to it and the subgraph refreshes around it.
- **Search combo box** — type-ahead search with type filter pills (All / Tables / Queries / Forms / Macros / Reports). Shows a dropdown of up to 20 matching nodes with colour-coded type dots and connection counts. Supports keyboard navigation (↑ ↓ Enter Escape).
- **Hover tooltip** — shows node name, type, total connections, and ego level.
- **Labels toggle** — turns on floating 3D name labels (SpriteText) for all visible nodes.
- **Home button** — returns to the default starting node (median-connectivity node).
- **Legend** — colour key for node types and ego levels.

**Node colour scheme:**

| Node | Colour |
|------|--------|
| Primary (selected) | Gold `#fbbf24` |
| Table (used) | Blue `#2563eb` |
| Table (unused) | Grey `#6b7280` |
| Queries | Amber `#f59e0b` |
| Forms | Blue `#3b82f6` |
| Macros | Red `#dc2626` |
| Reports | Green `#16a34a` |

**API endpoints added:**

| Endpoint | Description |
|----------|-------------|
| `GET /session/{id}/graph` | Renders the 3D graph page |
| `GET /session/{id}/graph-data` | Returns `{ nodes, links, meta }` JSON for the graph. Orphan nodes (no connections) are excluded. Node IDs are prefixed (`t_` for tables, `o_` for objects) to avoid numeric collisions. |

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
