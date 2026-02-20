"""
Flask web application for Database Dependency Analyzer.

Provides an interactive web interface for:
- Uploading XML files for analysis
- Using sample files for quick analysis
- Viewing dependency diagrams
- Exploring analysis results
- Saving and managing reports
"""

import os
import json
import tempfile
import uuid
import xml.etree.ElementTree as ET
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Optional

from flask import Flask, render_template, request, jsonify, send_file, after_this_request

# Configuration
ALLOWED_EXTENSIONS = {'xml'}
MAX_CONTENT_LENGTH = 50 * 1024 * 1024  # 50MB max

# Get the project root directory (parent of src/)
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
SAMPLE_FILES_DIR = PROJECT_ROOT / 'SampleXMLFiles'
SAVED_REPORTS_DIR = PROJECT_ROOT / 'saved_reports'

# Ensure saved_reports directory exists
SAVED_REPORTS_DIR.mkdir(exist_ok=True)

# Create Flask app
app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH

# Analysis results storage (in production, use a proper cache/database)
analysis_sessions: dict = {}


def allowed_file(filename: str) -> bool:
    """Check if file extension is allowed."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def perform_analysis(tables_path: str, objects_path: str, 
                     table_deps_path: str, object_deps_path: str) -> dict:
    """
    Perform full analysis on uploaded XML files.
    
    Args:
        tables_path: Path to tables XML file
        objects_path: Path to objects XML file
        table_deps_path: Path to table dependencies XML file
        object_deps_path: Path to object dependencies XML file
    
    Returns:
        Dictionary containing analysis results
    """
    import xml.etree.ElementTree as ET
    from collections import defaultdict
    
    def parse_tables_simple(file_path: str) -> dict:
        """Parse tables from XML."""
        tree = ET.parse(file_path)
        root = tree.getroot()
        
        tables = {}
        # Try multiple element names to support different XML formats
        elements = root.findall('.//Analysis_Tables')
        if not elements:
            elements = root.findall('.//Table')
        if not elements:
            elements = root.findall('.//{urn:schemas-microsoft-com:officedata}Table')
        
        for elem in elements:
            table_id = elem.get('TableID') or elem.findtext('TableID')
            table_name = elem.get('TableName') or elem.findtext('TableName')
            
            if table_id and table_name:
                tables[int(table_id)] = {
                    'table_id': int(table_id),
                    'table_name': table_name,
                    'is_used': False,
                    'referencing_objects': []
                }
        
        return tables
    
    def parse_objects_simple(file_path: str) -> dict:
        """Parse objects from XML."""
        tree = ET.parse(file_path)
        root = tree.getroot()
        
        objects = {}
        # Try multiple element names to support different XML formats
        elements = root.findall('.//Analysis_Objects')
        if not elements:
            elements = root.findall('.//Object')
        if not elements:
            elements = root.findall('.//{urn:schemas-microsoft-com:officedata}Object')
        
        for elem in elements:
            obj_id = elem.get('ObjectID') or elem.findtext('ObjectID')
            obj_name = elem.get('ObjectName') or elem.findtext('ObjectName')
            # Try both 'Type' and 'ObjectType' field names
            obj_type = elem.get('Type') or elem.findtext('Type') or elem.get('ObjectType') or elem.findtext('ObjectType')
            
            if obj_id and obj_name:
                objects[int(obj_id)] = {
                    'object_id': int(obj_id),
                    'object_name': obj_name,
                    'object_type': obj_type or 'unknown'
                }
        
        return objects
    
    def parse_table_deps_simple(file_path: str) -> list:
        """Parse table dependencies from XML."""
        tree = ET.parse(file_path)
        root = tree.getroot()
        
        deps = []
        # Try multiple element names to support different XML formats
        elements = root.findall('.//Analysis_TableDependencies')
        if not elements:
            elements = root.findall('.//Dependency')
        if not elements:
            elements = root.findall('.//{urn:schemas-microsoft-com:officedata}Dependency')
        
        for elem in elements:
            obj_id = elem.get('ObjectID') or elem.findtext('ObjectID')
            table_id = elem.get('TableID') or elem.findtext('TableID')
            active = elem.get('Active') or elem.findtext('Active') or '1'
            
            if obj_id and table_id:
                deps.append({
                    'object_id': int(obj_id),
                    'table_id': int(table_id),
                    'active': str(active).lower() not in ('false', '0', 'no')
                })
        
        return deps
    
    def parse_object_deps_simple(file_path: str) -> list:
        """Parse object dependencies from XML."""
        tree = ET.parse(file_path)
        root = tree.getroot()
        
        deps = []
        # Try multiple element names to support different XML formats
        elements = root.findall('.//Analysis_ObjectDependencies')
        if not elements:
            elements = root.findall('.//Dependency')
        if not elements:
            elements = root.findall('.//{urn:schemas-microsoft-com:officedata}Dependency')
        
        for elem in elements:
            # Try both naming conventions: SourceObjectID/TargetObjectID and ParentObjectID/ChildObjectID
            source_id = elem.get('SourceObjectID') or elem.findtext('SourceObjectID') or elem.get('ParentObjectID') or elem.findtext('ParentObjectID')
            target_id = elem.get('TargetObjectID') or elem.findtext('TargetObjectID') or elem.get('ChildObjectID') or elem.findtext('ChildObjectID')
            active = elem.get('Active') or elem.findtext('Active') or '1'
            
            if source_id and target_id:
                deps.append({
                    'source_object_id': int(source_id),
                    'target_object_id': int(target_id),
                    'active': str(active).lower() not in ('false', '0', 'no')
                })
        
        return deps
    
    tables = parse_tables_simple(tables_path)
    objects = parse_objects_simple(objects_path)
    table_dependencies = parse_table_deps_simple(table_deps_path)
    object_dependencies = parse_object_deps_simple(object_deps_path)
    
    # Build object-to-table mapping (for table usage tracking)
    object_to_tables = defaultdict(list)
    for dep in table_dependencies:
        if dep['active']:
            object_to_tables[dep['object_id']].append(dep['table_id'])
    
    # Build reverse mapping: count how many objects reference each object
    # This shows if a query is used by macros, forms, or reports
    referenced_by_count = defaultdict(int)
    referenced_by_objects = defaultdict(list)
    for dep in object_dependencies:
        if dep['active']:
            target_id = dep['target_object_id']
            source_id = dep['source_object_id']
            referenced_by_count[target_id] += 1
            if source_id in objects:
                referenced_by_objects[target_id].append({
                    'object_id': source_id,
                    'object_name': objects.get(source_id, {}).get('object_name', f'Object_{source_id}'),
                    'object_type': objects.get(source_id, {}).get('object_type', 'unknown')
                })
    
    # Mark used tables
    used_table_ids = set()
    for obj_id, table_ids in object_to_tables.items():
        for table_id in table_ids:
            if table_id in tables:
                used_table_ids.add(table_id)
                tables[table_id]['is_used'] = True
                tables[table_id]['referencing_objects'].append({
                    'object_id': obj_id,
                    'object_name': objects.get(obj_id, {}).get('object_name', f'Object_{obj_id}'),
                    'object_type': objects.get(obj_id, {}).get('object_type', 'unknown')
                })
    
    # Calculate statistics
    total_tables = len(tables)
    used_tables = len(used_table_ids)
    unused_tables = total_tables - used_tables
    total_objects = len(objects)
    
    # Find unused objects (objects that are not referenced by any other object)
    unused_object_count = sum(1 for obj_id in objects if obj_id not in referenced_by_count)
    
    # Count dependencies
    table_dependency_count = len(table_dependencies)
    object_dependency_count = len(object_dependencies)
    
    # Get unused table names sorted alphabetically
    unused_table_names = sorted([
        t['table_name'] for t in tables.values() if not t['is_used']
    ], key=str.lower)
    
    statistics = {
        'total_tables': total_tables,
        'used_tables': used_tables,
        'unused_tables': unused_tables,
        'total_objects': total_objects,
        'unused_object_count': unused_object_count,
        'table_dependency_count': table_dependency_count,
        'object_dependency_count': object_dependency_count,
        'unused_table_names': unused_table_names
    }
    
    # Usage summary
    usage_summary = {
        'unused_object_count': unused_object_count,
        'objects': [
            {
                'name': obj['object_name'],
                'object_type': obj['object_type'],
                'is_used': obj_id in referenced_by_count,
                'dependency_count': referenced_by_count.get(obj_id, 0),
                'referenced_by': referenced_by_objects.get(obj_id, [])
            }
            for obj_id, obj in objects.items()
        ]
    }
    
    # Generate simple HTML report
    html_content = generate_simple_html_report(tables, objects, statistics)
    
    return {
        'analysis_result': {
            'tables': tables,
            'objects': objects,
            'statistics': statistics
        },
        'statistics': statistics,
        'usage_summary': usage_summary,
        'html_report': html_content
    }


def generate_simple_html_report(tables: dict, objects: dict, statistics: dict) -> str:
    """Generate a simple HTML report for the analysis results."""
    html = f'''<!DOCTYPE html>
<html>
<head>
    <title>Database Dependency Analysis Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background: #1a1a2e; color: #fff; }}
        h1 {{ color: #00d4ff; }}
        h2 {{ color: #7c3aed; margin-top: 30px; }}
        .stats {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 15px; margin: 20px 0; }}
        .stat {{ background: #16213e; padding: 15px; border-radius: 8px; text-align: center; }}
        .stat-value {{ font-size: 2em; color: #00d4ff; font-weight: bold; }}
        .stat-label {{ color: #94a3b8; font-size: 0.9em; }}
        table {{ width: 100%; border-collapse: collapse; margin-top: 15px; }}
        th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #334155; }}
        th {{ color: #94a3b8; }}
        .unused {{ color: #ef4444; }}
        .used {{ color: #22c55e; }}
        .badge {{ padding: 4px 10px; border-radius: 20px; font-size: 0.8em; }}
        .badge-unused {{ background: rgba(239, 68, 68, 0.2); color: #ef4444; }}
        .badge-used {{ background: rgba(34, 197, 94, 0.2); color: #22c55e; }}
    </style>
</head>
<body>
    <h1>Database Dependency Analysis Report</h1>
    
    <h2>Summary Statistics</h2>
    <div class="stats">
        <div class="stat">
            <div class="stat-value">{statistics['total_tables']}</div>
            <div class="stat-label">Total Tables</div>
        </div>
        <div class="stat">
            <div class="stat-value">{statistics['used_tables']}</div>
            <div class="stat-label">Used Tables</div>
        </div>
        <div class="stat">
            <div class="stat-value">{statistics['unused_tables']}</div>
            <div class="stat-label">Unused Tables</div>
        </div>
        <div class="stat">
            <div class="stat-value">{statistics['total_objects']}</div>
            <div class="stat-label">Total Objects</div>
        </div>
    </div>
    
    <h2>Tables</h2>
    <table>
        <thead>
            <tr>
                <th>Table ID</th>
                <th>Table Name</th>
                <th>Status</th>
                <th>Referencing Objects</th>
            </tr>
        </thead>
        <tbody>
'''
    
    for table_id, table in sorted(tables.items()):
        status_class = 'badge-used' if table['is_used'] else 'badge-unused'
        status_text = 'Used' if table['is_used'] else 'Unused'
        ref_count = len(table['referencing_objects'])
        ref_names = ', '.join([r['object_name'] for r in table['referencing_objects']]) if ref_count > 0 else 'None'
        
        html += f'''
            <tr>
                <td>{table_id}</td>
                <td>{table['table_name']}</td>
                <td><span class="badge {status_class}">{status_text}</span></td>
                <td>{ref_count} ({ref_names})</td>
            </tr>
'''
    
    html += '''
        </tbody>
    </table>
    
    <h2>Objects</h2>
    <table>
        <thead>
            <tr>
                <th>Object ID</th>
                <th>Object Name</th>
                <th>Type</th>
            </tr>
        </thead>
        <tbody>
'''
    
    for obj_id, obj in sorted(objects.items()):
        html += f'''
            <tr>
                <td>{obj_id}</td>
                <td>{obj['object_name']}</td>
                <td>{obj['object_type']}</td>
            </tr>
'''
    
    html += '''
        </tbody>
    </table>
    
</body>
</html>
'''
    
    return html


@app.route('/')
def index():
    """Render the main upload page."""
    return render_template('index.html')


@app.route('/upload', methods=['POST'])
def upload_files():
    """
    Handle XML file uploads and perform analysis.
    
    Expects multipart form data with:
    - tables: Tables XML file
    - objects: Objects XML file
    - table_dependencies: Table dependencies XML file
    - object_dependencies: Object dependencies XML file
    """
    # Validate all files are present
    required_files = ['tables', 'objects', 'table_dependencies', 'object_dependencies']
    uploaded_files = {}
    
    for file_key in required_files:
        if file_key not in request.files:
            return jsonify({
                'error': f'Missing required file: {file_key}'
            }), 400
        
        file = request.files[file_key]
        if file.filename == '':
            return jsonify({
                'error': f'No file selected for: {file_key}'
            }), 400
        
        if file and allowed_file(file.filename):
            uploaded_files[file_key] = file
        else:
            return jsonify({
                'error': f'Invalid file type for: {file_key}. Only XML files are allowed.'
            }), 400
    
    # Create temporary directory for uploaded files
    session_id = str(uuid.uuid4())
    temp_dir = tempfile.mkdtemp(prefix=f'analysis_{session_id}_')
    file_paths = {}
    
    try:
        # Save uploaded files
        for file_key, file in uploaded_files.items():
            filename = secure_filename(file.filename)
            file_path = os.path.join(temp_dir, f'{file_key}.xml')
            file.save(file_path)
            file_paths[file_key] = file_path
        
        # Perform analysis
        results = perform_analysis(
            file_paths['tables'],
            file_paths['objects'],
            file_paths['table_dependencies'],
            file_paths['object_dependencies']
        )
        
        # Store results in session
        analysis_sessions[session_id] = {
            'results': results,
            'temp_dir': temp_dir,
            'created_at': str(uuid.uuid1().time)
        }
        
        return jsonify({
            'success': True,
            'session_id': session_id,
            'statistics': results['statistics'],
            'usage_summary': results['usage_summary']
        })
    
    except Exception as e:
        # Cleanup on error
        import shutil
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
        
        return jsonify({
            'error': f'Analysis failed: {str(e)}'
        }), 500


@app.route('/session/<session_id>')
def view_session(session_id: str):
    """Render the analysis results page for a session."""
    if session_id not in analysis_sessions:
        return render_template('error.html', error='Session not found or expired'), 404
    
    return render_template('results.html', session_id=session_id)


@app.route('/session/<session_id>/data')
def get_session_data(session_id: str):
    """Get analysis data for a session as JSON."""
    if session_id not in analysis_sessions:
        return jsonify({'error': 'Session not found or expired'}), 404
    
    return jsonify(analysis_sessions[session_id]['results'])


@app.route('/session/<session_id>/report')
def get_session_report(session_id: str):
    """Get HTML report for a session."""
    if session_id not in analysis_sessions:
        return jsonify({'error': 'Session not found or expired'}), 404
    
    return jsonify({
        'html': analysis_sessions[session_id]['results']['html_report']
    })


@app.route('/session/<session_id>/download')
def download_report(session_id: str):
    """Download HTML report as a file."""
    if session_id not in analysis_sessions:
        return jsonify({'error': 'Session not found or expired'}), 404
    
    results = analysis_sessions[session_id]['results']
    html_content = results['html_report']
    
    # Create a temporary file for download
    temp_file = tempfile.NamedTemporaryFile(
        mode='w',
        suffix='.html',
        prefix='dependency_analysis_',
        delete=False
    )
    temp_file.write(html_content)
    temp_file.close()
    
    @after_this_request
    def cleanup(response):
        """Delete temp file after sending."""
        try:
            os.unlink(temp_file.name)
        except Exception:
            pass
        return response
    
    return send_file(
        temp_file.name,
        mimetype='text/html',
        as_attachment=True,
        download_name='dependency_analysis_report.html'
    )


@app.route('/api/analyze', methods=['POST'])
def api_analyze():
    """
    API endpoint for programmatic analysis.
    
    Accepts JSON body with paths to XML files:
    {
        "tables": "/path/to/tables.xml",
        "objects": "/path/to/objects.xml",
        "table_dependencies": "/path/to/table_deps.xml",
        "object_dependencies": "/path/to/object_deps.xml"
    }
    """
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No JSON data provided'}), 400
    
    required_paths = ['tables', 'objects', 'table_dependencies', 'object_dependencies']
    for path_key in required_paths:
        if path_key not in data:
            return jsonify({'error': f'Missing required path: {path_key}'}), 400
        if not os.path.exists(data[path_key]):
            return jsonify({'error': f'File not found: {data[path_key]}'}), 400
    
    try:
        results = perform_analysis(
            data['tables'],
            data['objects'],
            data['table_dependencies'],
            data['object_dependencies']
        )
        
        return jsonify({
            'success': True,
            'statistics': results['statistics'],
            'usage_summary': results['usage_summary'],
            'analysis_result': results['analysis_result']
        })
    
    except Exception as e:
        return jsonify({
            'error': f'Analysis failed: {str(e)}'
        }), 500


@app.route('/health')
def health_check():
    """Health check endpoint."""
    return jsonify({'status': 'healthy'})


@app.route('/use-samples', methods=['POST'])
def use_sample_files():
    """
    Analyze using the sample XML files included with the project.
    
    This provides a quick way to see the analyzer in action without
    uploading custom files.
    """
    # Check if sample files exist
    sample_files = {
        'tables': SAMPLE_FILES_DIR / 'Analysis_Tables.xml',
        'objects': SAMPLE_FILES_DIR / 'Analysis_Objects.xml',
        'table_dependencies': SAMPLE_FILES_DIR / 'Analysis_TableDependencies.xml',
        'object_dependencies': SAMPLE_FILES_DIR / 'Analysis_ObjectDependencies.xml'
    }
    
    for file_key, file_path in sample_files.items():
        if not file_path.exists():
            return jsonify({
                'error': f'Sample file not found: {file_path.name}'
            }), 404
    
    try:
        # Perform analysis using sample files
        results = perform_analysis(
            str(sample_files['tables']),
            str(sample_files['objects']),
            str(sample_files['table_dependencies']),
            str(sample_files['object_dependencies'])
        )
        
        # Create session for results
        session_id = str(uuid.uuid4())
        analysis_sessions[session_id] = {
            'results': results,
            'temp_dir': None,  # No temp dir for sample files
            'created_at': datetime.now().isoformat(),
            'source': 'sample_files'
        }
        
        return jsonify({
            'success': True,
            'session_id': session_id,
            'statistics': results['statistics'],
            'usage_summary': results['usage_summary']
        })
    
    except Exception as e:
        return jsonify({
            'error': f'Analysis failed: {str(e)}'
        }), 500


@app.route('/save-report', methods=['POST'])
def save_report():
    """
    Save a report with a custom name for later reference.
    
    Expects JSON body:
    {
        "session_id": "uuid",
        "name": "My Report Name"
    }
    """
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No JSON data provided'}), 400
    
    session_id = data.get('session_id')
    report_name = data.get('name', '').strip()
    
    if not session_id:
        return jsonify({'error': 'Missing session_id'}), 400
    
    if session_id not in analysis_sessions:
        return jsonify({'error': 'Session not found or expired'}), 404
    
    if not report_name:
        report_name = f"Report_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    # Sanitize report name for filesystem
    safe_name = "".join(c for c in report_name if c.isalnum() or c in (' ', '-', '_')).strip()
    safe_name = safe_name[:100]  # Limit length
    
    # Create unique filename
    report_id = str(uuid.uuid4())[:8]
    filename = f"{safe_name}_{report_id}.json"
    filepath = SAVED_REPORTS_DIR / filename
    
    # Get session data
    session_data = analysis_sessions[session_id]
    
    # Prepare report data
    report_data = {
        'id': report_id,
        'name': report_name,
        'created_at': datetime.now().isoformat(),
        'source': session_data.get('source', 'uploaded_files'),
        'statistics': session_data['results']['statistics'],
        'analysis_result': session_data['results']['analysis_result'],
        'html_report': session_data['results']['html_report']
    }
    
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2)
        
        return jsonify({
            'success': True,
            'report_id': report_id,
            'filename': filename,
            'message': f'Report saved as "{report_name}"'
        })
    
    except Exception as e:
        return jsonify({
            'error': f'Failed to save report: {str(e)}'
        }), 500


@app.route('/saved-reports')
def list_saved_reports():
    """Render the saved reports page."""
    return render_template('saved_reports.html')


@app.route('/api/saved-reports')
def get_saved_reports():
    """Get list of all saved reports as JSON."""
    reports = []
    
    for filepath in SAVED_REPORTS_DIR.glob('*.json'):
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
                reports.append({
                    'id': data.get('id', filepath.stem),
                    'name': data.get('name', filepath.stem),
                    'created_at': data.get('created_at', ''),
                    'source': data.get('source', 'unknown'),
                    'filename': filepath.name,
                    'statistics': data.get('statistics', {})
                })
        except (json.JSONDecodeError, IOError):
            # Skip invalid files
            continue
    
    # Sort by creation date, newest first
    reports.sort(key=lambda x: x.get('created_at', ''), reverse=True)
    
    return jsonify({'reports': reports})


@app.route('/saved-reports/<report_id>')
def view_saved_report(report_id: str):
    """View a saved report."""
    # Find the report file
    for filepath in SAVED_REPORTS_DIR.glob(f'*_{report_id}.json'):
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Create a temporary session for viewing
            session_id = str(uuid.uuid4())
            analysis_sessions[session_id] = {
                'results': {
                    'statistics': data.get('statistics', {}),
                    'analysis_result': data.get('analysis_result', {}),
                    'html_report': data.get('html_report', ''),
                    'usage_summary': {
                        'unused_object_count': data.get('statistics', {}).get('unused_object_count', 0),
                        'objects': []
                    }
                },
                'temp_dir': None,
                'created_at': data.get('created_at', ''),
                'source': 'saved_report'
            }
            
            return render_template('results.html', session_id=session_id)
        
        except (json.JSONDecodeError, IOError):
            pass
    
    return render_template('error.html', error='Report not found'), 404


@app.route('/saved-reports/<report_id>/download')
def download_saved_report(report_id: str):
    """Download a saved report as HTML."""
    for filepath in SAVED_REPORTS_DIR.glob(f'*_{report_id}.json'):
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            html_content = data.get('html_report', '')
            if not html_content:
                return jsonify({'error': 'Report has no HTML content'}), 404
            
            # Create temp file for download
            temp_file = tempfile.NamedTemporaryFile(
                mode='w',
                suffix='.html',
                prefix=f'{data.get("name", "report")}_',
                delete=False
            )
            temp_file.write(html_content)
            temp_file.close()
            
            @after_this_request
            def cleanup(response):
                try:
                    os.unlink(temp_file.name)
                except Exception:
                    pass
                return response
            
            safe_name = "".join(c for c in data.get('name', 'report') if c.isalnum() or c in (' ', '-', '_'))
            return send_file(
                temp_file.name,
                mimetype='text/html',
                as_attachment=True,
                download_name=f'{safe_name}.html'
            )
        
        except (json.JSONDecodeError, IOError):
            pass
    
    return jsonify({'error': 'Report not found'}), 404


@app.route('/saved-reports/<report_id>/delete', methods=['DELETE'])
def delete_saved_report(report_id: str):
    """Delete a saved report."""
    for filepath in SAVED_REPORTS_DIR.glob(f'*_{report_id}.json'):
        try:
            os.unlink(filepath)
            return jsonify({
                'success': True,
                'message': 'Report deleted successfully'
            })
        except IOError as e:
            return jsonify({
                'error': f'Failed to delete report: {str(e)}'
            }), 500
    
    return jsonify({'error': 'Report not found'}), 404


def create_app() -> Flask:
    """Create and configure the Flask application."""
    return app


def run_server(host: str = '0.0.0.0', port: int = 5000, debug: bool = False):
    """Run the Flask development server."""
    app.run(host=host, port=port, debug=debug)


if __name__ == '__main__':
    run_server(debug=True)
