"""
Tests for the Flask web application.
"""

import json
import os
import tempfile
import pytest
from io import BytesIO

# Import the Flask app
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from database_dependency_analyzer.web.app import app, allowed_file, create_app


class TestAllowedFile:
    """Tests for the allowed_file function."""
    
    def test_valid_xml_extension(self):
        """Test that XML files are allowed."""
        assert allowed_file('tables.xml') is True
        assert allowed_file('objects.xml') is True
        assert allowed_file('data.XML') is True
        assert allowed_file('test.XmL') is True
    
    def test_invalid_extension(self):
        """Test that non-XML files are rejected."""
        assert allowed_file('data.json') is False
        assert allowed_file('data.txt') is False
        assert allowed_file('data.csv') is False
        assert allowed_file('data.py') is False
    
    def test_no_extension(self):
        """Test that files without extensions are rejected."""
        assert allowed_file('data') is False
        assert allowed_file('noextension') is False
    
    def test_hidden_files(self):
        """Test that hidden files are handled correctly."""
        assert allowed_file('.hidden.xml') is True
        assert allowed_file('.hidden') is False


class TestFlaskApp:
    """Tests for Flask application routes."""
    
    @pytest.fixture
    def client(self):
        """Create a test client for the Flask app."""
        app.config['TESTING'] = True
        with app.test_client() as client:
            yield client
    
    def test_index_route(self, client):
        """Test the index route returns the upload page."""
        response = client.get('/')
        assert response.status_code == 200
        assert b'Database Dependency Analyzer' in response.data
    
    def test_health_check(self, client):
        """Test the health check endpoint."""
        response = client.get('/health')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'healthy'
    
    def test_upload_without_files(self, client):
        """Test upload endpoint returns error when no files provided."""
        response = client.post('/upload')
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
    
    def test_upload_missing_files(self, client):
        """Test upload endpoint returns error when some files are missing."""
        # Create test XML content
        xml_content = b'''<?xml version="1.0"?>
        <Analysis_Tables>
            <Table name="TestTable"/>
        </Analysis_Tables>
        '''
        
        data = {
            'tables': (BytesIO(xml_content), 'tables.xml'),
            'objects': (BytesIO(xml_content), 'objects.xml'),
            # Missing table_dependencies and object_dependencies
        }
        
        response = client.post('/upload', data=data, content_type='multipart/form-data')
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
        assert 'Missing required file' in data['error']
    
    def test_upload_invalid_file_type(self, client):
        """Test upload endpoint rejects non-XML files."""
        data = {
            'tables': (BytesIO(b'not xml'), 'tables.json'),
            'objects': (BytesIO(b'not xml'), 'objects.json'),
            'table_dependencies': (BytesIO(b'not xml'), 'table_deps.json'),
            'object_dependencies': (BytesIO(b'not xml'), 'object_deps.json'),
        }
        
        response = client.post('/upload', data=data, content_type='multipart/form-data')
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'Invalid file type' in data['error']
    
    def test_session_not_found(self, client):
        """Test that accessing non-existent session returns error."""
        response = client.get('/session/nonexistent-session/data')
        assert response.status_code == 404
        data = json.loads(response.data)
        assert 'error' in data
    
    def test_api_analyze_no_data(self, client):
        """Test API analyze endpoint without JSON data."""
        # Without content-type header, Flask returns 415
        response = client.post('/api/analyze')
        # Accept either 400 (no data) or 415 (no content-type)
        assert response.status_code in [400, 415]
    
    def test_api_analyze_missing_paths(self, client):
        """Test API analyze endpoint with missing file paths."""
        response = client.post(
            '/api/analyze',
            json={'tables': '/path/to/tables.xml'},
            content_type='application/json'
        )
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
    
    def test_api_analyze_file_not_found(self, client):
        """Test API analyze endpoint with non-existent file paths."""
        response = client.post(
            '/api/analyze',
            json={
                'tables': '/nonexistent/tables.xml',
                'objects': '/nonexistent/objects.xml',
                'table_dependencies': '/nonexistent/table_deps.xml',
                'object_dependencies': '/nonexistent/object_deps.xml',
            },
            content_type='application/json'
        )
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'File not found' in data['error']


class TestFullUploadFlow:
    """Integration tests for the full upload and analysis flow."""
    
    @pytest.fixture
    def client(self):
        """Create a test client for the Flask app."""
        app.config['TESTING'] = True
        with app.test_client() as client:
            yield client
    
    @pytest.fixture
    def sample_xml_files(self):
        """Create sample XML files for testing."""
        tables_xml = b'''<?xml version="1.0"?>
        <Analysis_Tables>
            <Table>
                <TableID>1</TableID>
                <TableName>Users</TableName>
            </Table>
            <Table>
                <TableID>2</TableID>
                <TableName>Orders</TableName>
            </Table>
            <Table>
                <TableID>3</TableID>
                <TableName>Products</TableName>
            </Table>
        </Analysis_Tables>
        '''
        
        objects_xml = b'''<?xml version="1.0"?>
        <Analysis_Objects>
            <Object>
                <ObjectID>1</ObjectID>
                <ObjectName>sp_GetUser</ObjectName>
                <Type>Query</Type>
            </Object>
            <Object>
                <ObjectID>2</ObjectID>
                <ObjectName>fn_GetOrderTotal</ObjectName>
                <Type>Query</Type>
            </Object>
            <Object>
                <ObjectID>3</ObjectID>
                <ObjectName>vw_ActiveOrders</ObjectName>
                <Type>Query</Type>
            </Object>
        </Analysis_Objects>
        '''
        
        table_deps_xml = b'''<?xml version="1.0"?>
        <Analysis_TableDependencies>
            <Dependency>
                <SourceTable>Users</SourceTable>
                <TargetTable>Orders</TargetTable>
            </Dependency>
            <Dependency>
                <SourceTable>Orders</SourceTable>
                <TargetTable>Products</TargetTable>
            </Dependency>
        </Analysis_TableDependencies>
        '''
        
        object_deps_xml = b'''<?xml version="1.0"?>
        <Analysis_ObjectDependencies>
            <Dependency>
                <SourceObject>sp_GetUser</SourceObject>
                <TargetTable>Users</TargetTable>
            </Dependency>
            <Dependency>
                <SourceObject>fn_GetOrderTotal</SourceObject>
                <TargetTable>Orders</TargetTable>
            </Dependency>
            <Dependency>
                <SourceObject>fn_GetOrderTotal</SourceObject>
                <TargetTable>Products</TargetTable>
            </Dependency>
            <Dependency>
                <SourceObject>vw_ActiveOrders</SourceObject>
                <TargetTable>Orders</TargetTable>
            </Dependency>
        </Analysis_ObjectDependencies>
        '''
        
        return {
            'tables': tables_xml,
            'objects': objects_xml,
            'table_dependencies': table_deps_xml,
            'object_dependencies': object_deps_xml,
        }
    
    def test_successful_upload_and_analysis(self, client, sample_xml_files):
        """Test successful file upload and analysis."""
        data = {
            'tables': (BytesIO(sample_xml_files['tables']), 'tables.xml'),
            'objects': (BytesIO(sample_xml_files['objects']), 'objects.xml'),
            'table_dependencies': (BytesIO(sample_xml_files['table_dependencies']), 'table_deps.xml'),
            'object_dependencies': (BytesIO(sample_xml_files['object_dependencies']), 'object_deps.xml'),
        }
        
        response = client.post('/upload', data=data, content_type='multipart/form-data')
        
        assert response.status_code == 200
        result = json.loads(response.data)
        assert result['success'] is True
        assert 'session_id' in result
        assert 'statistics' in result
        assert 'usage_summary' in result
    
    def test_view_session_results(self, client, sample_xml_files):
        """Test viewing session results page."""
        # First upload files
        data = {
            'tables': (BytesIO(sample_xml_files['tables']), 'tables.xml'),
            'objects': (BytesIO(sample_xml_files['objects']), 'objects.xml'),
            'table_dependencies': (BytesIO(sample_xml_files['table_dependencies']), 'table_deps.xml'),
            'object_dependencies': (BytesIO(sample_xml_files['object_dependencies']), 'object_deps.xml'),
        }
        
        upload_response = client.post('/upload', data=data, content_type='multipart/form-data')
        result = json.loads(upload_response.data)
        session_id = result['session_id']
        
        # View session page
        page_response = client.get(f'/session/{session_id}')
        assert page_response.status_code == 200
        assert b'Analysis Results' in page_response.data
        
        # Get session data
        data_response = client.get(f'/session/{session_id}/data')
        assert data_response.status_code == 200
        data_result = json.loads(data_response.data)
        assert 'html_report' in data_result
        assert 'statistics' in data_result


class TestCreateApp:
    """Tests for the create_app factory function."""
    
    def test_create_app_returns_flask_instance(self):
        """Test that create_app returns a Flask instance."""
        app_instance = create_app()
        assert app_instance is not None
        assert hasattr(app_instance, 'route')
    
    def test_app_has_required_routes(self):
        """Test that the app has all required routes registered."""
        app_instance = create_app()
        routes = [rule.rule for rule in app_instance.url_map.iter_rules()]
        
        assert '/' in routes
        assert '/upload' in routes
        assert '/health' in routes
        assert '/session/<session_id>' in routes
        assert '/session/<session_id>/data' in routes
        assert '/api/analyze' in routes
