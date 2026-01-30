"""HTML report generator for database dependency analysis results."""

import json
from datetime import datetime
from typing import Dict, Any

from ..models.analysis_result import AnalysisResult


class HTMLGenerator:
    """Generates self-contained HTML reports for database dependency analysis.

    This class creates responsive, interactive HTML reports that can be viewed
    offline with embedded CSS and JavaScript. The reports include visualizations,
    filtering capabilities, and export functionality.
    """

    def __init__(self, analysis_result: AnalysisResult):
        """Initialize the HTML generator with analysis results.

        Args:
            analysis_result: The complete analysis results to generate report for.
        """
        self.analysis_result = analysis_result

    def generate_html(self) -> str:
        """Generate the complete HTML report as a string.

        Returns:
            Complete HTML document as a string with embedded CSS and JavaScript.
        """
        # Serialize data for embedding
        embedded_data = self._serialize_data()

        # Generate HTML components
        html_parts = [
            self._generate_html_head(),
            self._generate_html_body(embedded_data),
            self._generate_embedded_scripts()
        ]

        return '\n'.join(html_parts)

    def _serialize_data(self) -> Dict[str, Any]:
        """Serialize analysis result data for JSON embedding.

        Returns:
            Dictionary containing serialized analysis data.
        """
        # Convert tables to serializable format
        tables_data = {}
        for table_id, table in self.analysis_result.tables.items():
            tables_data[str(table_id)] = {
                'table_id': table.table_id,
                'table_name': table.table_name,
                'is_used': table.is_used,
                'referencing_objects': [
                    {
                        'object_id': ref.object_id,
                        'object_name': ref.object_name,
                        'object_type': ref.object_type,
                        'active': ref.active
                    }
                    for ref in table.referencing_objects
                ]
            }

        # Convert objects to serializable format
        objects_data = {}
        for obj_id, obj in self.analysis_result.objects.items():
            objects_data[str(obj_id)] = {
                'object_id': obj.object_id,
                'object_name': obj.object_name,
                'object_type': obj.object_type
            }

        # Convert statistics
        stats = self.analysis_result.statistics
        stats_data = {
            'total_tables': stats.total_tables,
            'used_tables': stats.used_tables,
            'unused_tables': stats.unused_tables,
            'total_objects': stats.total_objects,
            'objects_by_type': stats.objects_by_type,
            'total_dependencies': stats.total_dependencies,
            'active_dependencies': stats.active_dependencies,
            'usage_percentage': stats.usage_percentage,
            'unused_percentage': stats.unused_percentage
        }

        return {
            'tables': tables_data,
            'objects': objects_data,
            'statistics': stats_data,
            'timestamp': self.analysis_result.timestamp.isoformat(),
            'processing_time': self.analysis_result.processing_time
        }

    def _generate_html_head(self) -> str:
        """Generate the HTML head section with metadata and embedded CSS.

        Returns:
            HTML head section as string.
        """
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Database Dependency Analysis Report</title>
    <style>
{self._generate_embedded_css()}
    </style>
</head>"""

    def _generate_html_body(self, embedded_data: Dict[str, Any]) -> str:
        """Generate the HTML body with report structure.

        Args:
            embedded_data: Serialized analysis data for embedding.

        Returns:
            HTML body section as string.
        """
        return f"""<body>
    <div class="container">
        {self._generate_header()}
        {self._generate_sidebar()}
        {self._generate_main_content()}
    </div>

    <script type="application/json" id="analysis-data">
{json.dumps(embedded_data, indent=2)}
    </script>
</body>
</html>"""

    def _generate_header(self) -> str:
        """Generate the report header section.

        Returns:
            HTML header section as string.
        """
        stats = self.analysis_result.statistics
        timestamp = self.analysis_result.timestamp.isoformat()
        processing_time = f"{self.analysis_result.processing_time:.2f}"

        return f"""        <header class="report-header">
            <div class="header-content">
                <h1>Database Dependency Analysis Report</h1>
                <div class="summary-stats">
                    <div class="stat-card">
                        <div class="stat-number" id="total-tables">{stats.total_tables}</div>
                        <div class="stat-label">Total Tables</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number used" id="used-tables">{stats.used_tables}</div>
                        <div class="stat-label">Used Tables</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number unused" id="unused-tables">{stats.unused_tables}</div>
                        <div class="stat-label">Unused Tables</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number" id="total-objects">{stats.total_objects}</div>
                        <div class="stat-label">Total Objects</div>
                    </div>
                </div>
                <div class="report-meta">
                    <span class="timestamp">Generated: <span id="timestamp">{timestamp}</span></span>
                    <span class="processing-time">Processing Time: <span id="processing-time">{processing_time}s</span></span>
                </div>
            </div>
        </header>"""

    def _generate_sidebar(self) -> str:
        """Generate the sidebar navigation section.

        Returns:
            HTML sidebar section as string.
        """
        stats = self.analysis_result.statistics
        usage_percentage = stats.usage_percentage
        unused_percentage = stats.unused_percentage

        return f"""        <nav class="sidebar">
            <div class="sidebar-section">
                <h3>Quick Stats</h3>
                <div class="usage-chart">
                    <canvas id="usage-chart" width="200" height="200"></canvas>
                    <div class="chart-legend">
                        <div class="legend-item">
                            <span class="color-box used"></span>
                            <span>Used (<span id="used-percentage">{usage_percentage:.1f}</span>%)</span>
                        </div>
                        <div class="legend-item">
                            <span class="color-box unused"></span>
                            <span>Unused (<span id="unused-percentage">{unused_percentage:.1f}</span>%)</span>
                        </div>
                    </div>
                </div>
            </div>

            <div class="sidebar-section">
                <h3>Object Types</h3>
                <div class="object-type-stats">
                    <div class="type-stat" data-type="Form">
                        <span class="type-icon form-icon">📄</span>
                        <span class="type-count" id="form-count">{stats.objects_by_type.get('Form', 0)}</span>
                        <span class="type-label">Forms</span>
                    </div>
                    <div class="type-stat" data-type="Query">
                        <span class="type-icon query-icon">🔍</span>
                        <span class="type-count" id="query-count">{stats.objects_by_type.get('Query', 0)}</span>
                        <span class="type-label">Queries</span>
                    </div>
                    <div class="type-stat" data-type="Macro">
                        <span class="type-icon macro-icon">⚡</span>
                        <span class="type-count" id="macro-count">{stats.objects_by_type.get('Macro', 0)}</span>
                        <span class="type-label">Macros</span>
                    </div>
                    <div class="type-stat" data-type="Report">
                        <span class="type-icon report-icon">📊</span>
                        <span class="type-count" id="report-count">{stats.objects_by_type.get('Report', 0)}</span>
                        <span class="type-label">Reports</span>
                    </div>
                </div>
            </div>

            <div class="sidebar-section">
                <h3>Filters</h3>
                <div class="filter-controls">
                    <label class="filter-option">
                        <input type="checkbox" id="show-used" checked>
                        Show Used Tables
                    </label>
                    <label class="filter-option">
                        <input type="checkbox" id="show-unused" checked>
                        Show Unused Tables
                    </label>
                    <div class="filter-group">
                        <label>Object Types:</label>
                        <label class="filter-option">
                            <input type="checkbox" class="object-filter" data-type="Form" checked>
                            Forms
                        </label>
                        <label class="filter-option">
                            <input type="checkbox" class="object-filter" data-type="Query" checked>
                            Queries
                        </label>
                        <label class="filter-option">
                            <input type="checkbox" class="object-filter" data-type="Macro" checked>
                            Macros
                        </label>
                        <label class="filter-option">
                            <input type="checkbox" class="object-filter" data-type="Report" checked>
                            Reports
                        </label>
                    </div>
                </div>
            </div>
        </nav>"""

    def _generate_main_content(self) -> str:
        """Generate the main content area.

        Returns:
            HTML main content section as string.
        """
        return f"""        <main class="main-content">
            {self._generate_usage_table_section()}
            {self._generate_dependency_diagram_section()}

            <div class="content-header">
                <h2>Table Dependencies</h2>
                <div class="header-actions">
                    <button id="export-btn" class="export-btn">Export CSV</button>
                    <div class="view-controls">
                        <button class="view-btn active" data-view="table">Table View</button>
                        <button class="view-btn" data-view="cards">Card View</button>
                    </div>
                </div>
            </div>

            <div class="search-container">
                <input type="text" id="table-search" placeholder="Search tables...">
                <select id="sort-select">
                    <option value="name">Sort by Name</option>
                    <option value="status">Sort by Status</option>
                    <option value="references">Sort by References</option>
                </select>
            </div>

            <!-- Table View -->
            <div id="table-view" class="view-container active">
                <table class="dependencies-table">
                    <thead>
                        <tr>
                            <th>Status</th>
                            <th>Table Name</th>
                            <th>References</th>
                            <th>Object Types</th>
                            <th>Details</th>
                        </tr>
                    </thead>
                    <tbody id="table-body">
                        <!-- Table rows will be inserted here -->
                    </tbody>
                </table>
            </div>

            <!-- Card View -->
            <div id="card-view" class="view-container">
                <div id="card-container" class="card-grid">
                    <!-- Table cards will be inserted here -->
                </div>
            </div>
        </main>"""

    def _generate_usage_table_section(self) -> str:
        """Generate the usage status table section.

        Returns:
            HTML usage table section as string.
        """
        return '''
            <section class="usage-table-section">
                <h2>Table Usage Status</h2>
                <div class="usage-table-container">
                    <table class="usage-table">
                        <thead>
                            <tr>
                                <th>Status</th>
                                <th>Table Name</th>
                                <th>Referencing Objects</th>
                                <th>Object Types</th>
                            </tr>
                        </thead>
                        <tbody id="usage-table-body">
                            <!-- Rows will be inserted here -->
                        </tbody>
                    </table>
                </div>
            </section>
        '''

    def _generate_dependency_diagram_section(self) -> str:
        """Generate the dependency diagram section.

        Returns:
            HTML dependency diagram section as string.
        """
        return '''
            <section class="dependency-diagram-section">
                <h2>Table Dependency Diagram</h2>
                <div class="diagram-controls">
                    <label><input type="checkbox" id="show-tables" checked> Tables</label>
                    <label><input type="checkbox" id="show-forms" checked> Forms</label>
                    <label><input type="checkbox" id="show-queries" checked> Queries</label>
                    <label><input type="checkbox" id="show-macros" checked> Macros</label>
                    <label><input type="checkbox" id="show-reports" checked> Reports</label>
                </div>
                <div id="dependency-diagram" class="dependency-diagram">
                    <!-- SVG diagram rendered here -->
                </div>
            </section>
        '''

    def _generate_embedded_css(self) -> str:
        """Generate embedded CSS styles for the report.

        Returns:
            CSS styles as string.
        """
        return """:root {
    /* Color Palette */
    --primary-color: #2563eb;
    --success-color: #16a34a;
    --danger-color: #dc2626;
    --warning-color: #ca8a04;
    --info-color: #0891b2;

    /* Object Type Colors */
    --form-color: #3b82f6;
    --query-color: #f59e0b;
    --macro-color: #dc2626;
    --report-color: #16a34a;

    /* Status Colors */
    --used-color: #16a34a;
    --unused-color: #dc2626;

    /* Layout */
    --sidebar-width: 300px;
    --header-height: 200px;
    --border-radius: 8px;
    --shadow: 0 2px 4px rgba(0, 0, 0, 0.1);

    /* Typography */
    --font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    --font-size-base: 14px;
    --font-size-lg: 18px;
    --font-size-xl: 24px;
}

/* Global Styles */
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: var(--font-family);
    font-size: var(--font-size-base);
    line-height: 1.5;
    color: #374151;
    background: #f9fafb;
}

/* Modal Styles */
.modal-overlay {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(0, 0, 0, 0.5);
    display: flex;
    justify-content: center;
    align-items: center;
    z-index: 1000;
}

.modal-content {
    background: white;
    border-radius: var(--border-radius);
    max-width: 600px;
    max-height: 80vh;
    width: 90%;
    box-shadow: 0 10px 25px rgba(0, 0, 0, 0.2);
    overflow: hidden;
}

.modal-header {
    padding: 1.5rem;
    border-bottom: 1px solid #e5e7eb;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.modal-header h2 {
    margin: 0;
    color: #111827;
}

.modal-close {
    background: none;
    border: none;
    font-size: 1.5rem;
    cursor: pointer;
    color: #6b7280;
    padding: 0.25rem;
    border-radius: 0.25rem;
}

.modal-close:hover {
    background: #f3f4f6;
    color: #374151;
}

.modal-body {
    padding: 1.5rem;
    overflow-y: auto;
    max-height: calc(80vh - 80px);
}

.detail-section {
    margin-bottom: 1.5rem;
}

.detail-section h3 {
    margin-bottom: 0.75rem;
    color: #374151;
    font-size: var(--font-size-lg);
}

.status-badge {
    padding: 0.25rem 0.75rem;
    border-radius: 9999px;
    font-size: 0.875rem;
    font-weight: 500;
}

.status-badge.used {
    background: #dcfce7;
    color: var(--success-color);
}

.status-badge.unused {
    background: #fef2f2;
    color: var(--danger-color);
}

.references-list {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
}

.reference-item {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    padding: 0.75rem;
    border: 1px solid #e5e7eb;
    border-radius: var(--border-radius);
    background: #f9fafb;
}

.object-icon {
    font-size: 1.2rem;
}

.object-name {
    flex: 1;
    font-weight: 500;
}

.object-type {
    padding: 0.25rem 0.5rem;
    background: #e5e7eb;
    border-radius: 0.25rem;
    font-size: 0.75rem;
    font-weight: 500;
    color: #374151;
}

.object-status {
    padding: 0.25rem 0.5rem;
    border-radius: 0.25rem;
    font-size: 0.75rem;
    font-weight: 500;
}

.object-status.active {
    background: #dcfce7;
    color: var(--success-color);
}

.object-status.inactive {
    background: #fef2f2;
    color: var(--danger-color);
}

/* Layout */
.container {
    min-height: 100vh;
}

/* Header Styles */
.report-header {
    background: linear-gradient(135deg, var(--primary-color), #1d4ed8);
    color: white;
    padding: 2rem;
    box-shadow: var(--shadow);
}

.header-content h1 {
    font-size: var(--font-size-xl);
    font-weight: bold;
    margin-bottom: 1.5rem;
}

.summary-stats {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
    gap: 1rem;
    margin: 1.5rem 0;
}

.stat-card {
    background: rgba(255, 255, 255, 0.1);
    padding: 1rem;
    border-radius: var(--border-radius);
    text-align: center;
    backdrop-filter: blur(10px);
}

.stat-number {
    font-size: var(--font-size-xl);
    font-weight: bold;
    margin-bottom: 0.5rem;
}

.stat-number.used { color: #86efac; }
.stat-number.unused { color: #fca5a5; }

.report-meta {
    margin-top: 1rem;
    font-size: 0.9rem;
    opacity: 0.9;
}

/* Sidebar Styles */
.sidebar {
    background: #f8fafc;
    border-right: 1px solid #e2e8f0;
    padding: 1.5rem;
    overflow-y: auto;
}

.sidebar-section {
    margin-bottom: 2rem;
}

.sidebar-section h3 {
    margin-bottom: 1rem;
    color: #374151;
    font-size: var(--font-size-lg);
}

/* Usage Chart */
.usage-chart {
    text-align: center;
}

.chart-legend {
    margin-top: 1rem;
}

.legend-item {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 0.5rem;
    margin-bottom: 0.5rem;
    font-size: 0.9rem;
}

.color-box {
    width: 12px;
    height: 12px;
    border-radius: 2px;
}

.color-box.used { background: var(--used-color); }
.color-box.unused { background: var(--unused-color); }

/* Object Type Stats */
.object-type-stats {
    display: flex;
    flex-direction: column;
    gap: 0.75rem;
}

.type-stat {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    padding: 0.5rem;
    border-radius: var(--border-radius);
    background: white;
    border: 1px solid #e5e7eb;
}

.type-icon {
    font-size: 1.2rem;
}

.type-count {
    font-weight: bold;
    min-width: 2rem;
}

/* Filter Controls */
.filter-controls {
    display: flex;
    flex-direction: column;
    gap: 0.75rem;
}

.filter-option {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    cursor: pointer;
}

.filter-group {
    margin-top: 0.5rem;
}

.filter-group label {
    font-weight: 500;
    margin-bottom: 0.5rem;
    display: block;
}

/* Main Content */
.main-content {
    padding: 2rem;
}

.content-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 1.5rem;
}

.content-header h2 {
    font-size: var(--font-size-lg);
    color: #111827;
}

.header-actions {
    display: flex;
    align-items: center;
    gap: 1rem;
}

.export-btn {
    background: var(--success-color);
    color: white;
    border: none;
    padding: 0.5rem 1rem;
    border-radius: var(--border-radius);
    cursor: pointer;
    font-size: 0.9rem;
    font-weight: 500;
    transition: background-color 0.2s ease;
}

.export-btn:hover {
    background: #16a34a;
}

.view-controls {
    display: flex;
    gap: 0.5rem;
}

.view-btn {
    padding: 0.5rem 1rem;
    border: 1px solid #d1d5db;
    background: white;
    border-radius: var(--border-radius);
    cursor: pointer;
    transition: all 0.2s ease;
}

.view-btn.active {
    background: var(--primary-color);
    color: white;
    border-color: var(--primary-color);
}

.view-btn:hover {
    border-color: var(--primary-color);
}

/* Search Container */
.search-container {
    display: flex;
    gap: 1rem;
    margin-bottom: 1rem;
    align-items: center;
}

#table-search {
    flex: 1;
    padding: 0.5rem;
    border: 1px solid #d1d5db;
    border-radius: var(--border-radius);
    font-size: var(--font-size-base);
}

#sort-select {
    padding: 0.5rem;
    border: 1px solid #d1d5db;
    border-radius: var(--border-radius);
    background: white;
    font-size: var(--font-size-base);
}

/* Table Styles */
.dependencies-table {
    width: 100%;
    border-collapse: collapse;
    margin-top: 1rem;
    background: white;
    border-radius: var(--border-radius);
    overflow: hidden;
    box-shadow: var(--shadow);
}

.dependencies-table th,
.dependencies-table td {
    padding: 0.75rem;
    text-align: left;
    border-bottom: 1px solid #e5e7eb;
}

.dependencies-table th {
    background: #f9fafb;
    font-weight: 600;
    color: #374151;
}

.table-status {
    display: inline-block;
    padding: 0.25rem 0.75rem;
    border-radius: 9999px;
    font-size: 0.875rem;
    font-weight: 500;
}

.table-status.used {
    background: #dcfce7;
    color: var(--used-color);
}

.table-status.unused {
    background: #fef2f2;
    color: var(--unused-color);
}

/* Card View Styles */
.card-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
    gap: 1rem;
    margin-top: 1rem;
}

.table-card {
    background: white;
    border: 1px solid #e5e7eb;
    border-radius: var(--border-radius);
    padding: 1.5rem;
    box-shadow: var(--shadow);
    transition: box-shadow 0.2s ease;
}

.table-card:hover {
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
}

.table-card.used {
    border-left: 4px solid var(--used-color);
}

.table-card.unused {
    border-left: 4px solid var(--unused-color);
}

.card-status {
    display: inline-block;
    padding: 0.25rem 0.75rem;
    border-radius: 9999px;
    font-size: 0.875rem;
    font-weight: 500;
    margin-bottom: 0.5rem;
}

.table-card.used .card-status {
    background: #dcfce7;
    color: var(--used-color);
}

.table-card.unused .card-status {
    background: #fef2f2;
    color: var(--unused-color);
}

.card-title {
    font-size: 1.1rem;
    font-weight: 600;
    margin-bottom: 0.5rem;
    color: #111827;
}

.card-refs {
    font-size: 0.9rem;
    color: #6b7280;
    margin-bottom: 0.75rem;
}

.card-types {
    display: flex;
    flex-wrap: wrap;
    gap: 0.5rem;
    margin-bottom: 1rem;
}

.object-badge {
    display: inline-block;
    padding: 0.25rem 0.5rem;
    border-radius: 0.25rem;
    font-size: 0.75rem;
    font-weight: 500;
}

.object-badge.form {
    background: #dbeafe;
    color: var(--form-color);
}

.object-badge.query {
    background: #fef3c7;
    color: var(--query-color);
}

.object-badge.macro {
    background: #fee2e2;
    color: var(--macro-color);
}

.object-badge.report {
    background: #dcfce7;
    color: var(--report-color);
}
}

.table-card.unused {
    border-left: 4px solid var(--unused-color);
}

.card-status {
    display: inline-block;
    padding: 0.25rem 0.75rem;
    border-radius: 9999px;
    font-size: 0.875rem;
    font-weight: 500;
    margin-bottom: 0.75rem;
}

.table-card.used .card-status {
    background: #dcfce7;
    color: var(--used-color);
}

.table-card.unused .card-status {
    background: #fef2f2;
    color: var(--unused-color);
}

.card-title {
    font-size: var(--font-size-lg);
    font-weight: 600;
    color: #111827;
    margin-bottom: 0.5rem;
}

.card-refs {
    color: #6b7280;
    font-size: 0.9rem;
    margin-bottom: 0.75rem;
}

.card-types {
    display: flex;
    flex-wrap: wrap;
    gap: 0.5rem;
    margin-bottom: 1rem;
}

.details-btn {
    background: var(--primary-color);
    color: white;
    border: none;
    padding: 0.5rem 1rem;
    border-radius: var(--border-radius);
    cursor: pointer;
    font-size: 0.9rem;
    transition: background-color 0.2s ease;
}

.details-btn:hover {
    background: #1d4ed8;
}

/* View Container Styles */
.view-container {
    display: none;
}

.view-container.active {
    display: block;
}

/* Object Badge Styles */
.object-badge {
    display: inline-block;
    padding: 0.25rem 0.5rem;
    border-radius: 0.25rem;
    font-size: 0.75rem;
    font-weight: 500;
    margin-right: 0.25rem;
    margin-bottom: 0.25rem;
}

.object-badge.form {
    background: #dbeafe;
    color: var(--form-color);
}

.object-badge.query {
    background: #fef3c7;
    color: var(--query-color);
}

.object-badge.macro {
    background: #fee2e2;
    color: var(--macro-color);
}

.object-badge.report {
    background: #dcfce7;
    color: var(--report-color);
}
    font-weight: 500;
}

.status-badge.used {
    background: #dcfce7;
    color: var(--used-color);
}

.status-badge.unused {
    background: #fef2f2;
    color: var(--unused-color);
}

.object-badges {
    display: flex;
    flex-wrap: wrap;
    gap: 0.5rem;
    margin-top: 1rem;
}

.object-badge {
    display: inline-block;
    padding: 0.25rem 0.5rem;
    border-radius: 4px;
    font-size: 0.75rem;
    font-weight: 500;
}

.object-badge.form { background: #dbeafe; color: var(--form-color); }
.object-badge.query { background: #fef3c7; color: var(--query-color); }
.object-badge.macro { background: #fee2e2; color: var(--macro-color); }
.object-badge.report { background: #dcfce7; color: var(--report-color); }

/* Responsive Design */
@media (min-width: 1024px) {
    .container {
        display: grid;
        grid-template-columns: var(--sidebar-width) 1fr;
        grid-template-rows: var(--header-height) 1fr;
        grid-template-areas:
            "header header"
            "sidebar main";
    }

    .report-header {
        grid-area: header;
    }

    .sidebar {
        grid-area: sidebar;
    }

    .main-content {
        grid-area: main;
    }
}

@media (max-width: 1023px) and (min-width: 768px) {
    .container {
        display: grid;
        grid-template-columns: 250px 1fr;
        grid-template-rows: auto 1fr;
        grid-template-areas:
            "header header"
            "sidebar main";
    }

    .report-header {
        grid-area: header;
    }

    .sidebar {
        grid-area: sidebar;
    }

    .main-content {
        grid-area: main;
    }
}

@media (max-width: 767px) {
    .container {
        display: flex;
        flex-direction: column;
    }

    .sidebar {
        position: fixed;
        top: 0;
        left: -100%;
        width: 280px;
        height: 100vh;
        z-index: 1000;
        transition: left 0.3s ease;
    }

    .sidebar.open {
        left: 0;
    }

    .summary-stats {
        grid-template-columns: repeat(2, 1fr);
    }

    .search-container {
        flex-direction: column;
        align-items: stretch;
    }

    .card-grid {
        grid-template-columns: 1fr;
    }
}

/* Utility Classes */
.view-container {
    display: none;
}

.view-container.active {
    display: block;
}

.details-btn {
    padding: 0.25rem 0.5rem;
    background: var(--primary-color);
    color: white;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    font-size: 0.875rem;
}

.details-btn:hover {
    background: #1d4ed8;
}

/* Usage Table Styles */
.usage-table-section {
    margin: 2rem 0;
    padding: 1.5rem;
    background: white;
    border-radius: var(--border-radius);
    box-shadow: var(--shadow);
}

.usage-table-section h2 {
    margin-bottom: 1rem;
    color: #111827;
    font-size: var(--font-size-lg);
}

.usage-table-container {
    overflow-x: auto;
}

.usage-table {
    width: 100%;
    border-collapse: collapse;
}

.usage-table th,
.usage-table td {
    padding: 0.75rem;
    text-align: left;
    border-bottom: 1px solid #e5e7eb;
}

.usage-table th {
    background: #f9fafb;
    font-weight: 600;
    color: #374151;
}

.usage-table tbody tr.row-used {
    background: #f0fdf4;
}

.usage-table tbody tr.row-unused {
    background: #fef2f2;
}

.status-indicator {
    margin-right: 0.5rem;
    font-size: 0.75rem;
}

.status-indicator.used { color: var(--used-color); }
.status-indicator.unused { color: var(--unused-color); }

.object-list {
    list-style: none;
    padding: 0;
    margin: 0;
}

.object-list li {
    padding: 0.25rem 0;
    font-size: 0.875rem;
}

.object-list .object-type-badge {
    display: inline-block;
    padding: 0.125rem 0.5rem;
    border-radius: 0.25rem;
    font-size: 0.7rem;
    font-weight: 500;
    margin-right: 0.5rem;
    min-width: 60px;
    text-align: center;
}

.object-list .object-type-badge.form {
    background: #dbeafe;
    color: var(--form-color);
}

.object-list .object-type-badge.query {
    background: #fef3c7;
    color: var(--query-color);
}

.object-list .object-type-badge.macro {
    background: #fee2e2;
    color: var(--macro-color);
}

.object-list .object-type-badge.report {
    background: #dcfce7;
    color: var(--report-color);
}

.type-count-badge {
    display: inline-block;
    padding: 0.25rem 0.5rem;
    border-radius: 0.25rem;
    font-size: 0.75rem;
    margin-right: 0.25rem;
}

.type-count-badge.form {
    background: #dbeafe;
    color: var(--form-color);
}

.type-count-badge.query {
    background: #fef3c7;
    color: var(--query-color);
}

.type-count-badge.macro {
    background: #fee2e2;
    color: var(--macro-color);
}

.type-count-badge.report {
    background: #dcfce7;
    color: var(--report-color);
}

/* Dependency Diagram Styles */
.dependency-diagram-section {
    margin: 2rem 0;
    padding: 1.5rem;
    background: white;
    border-radius: var(--border-radius);
    box-shadow: var(--shadow);
}

.dependency-diagram-section h2 {
    margin-bottom: 1rem;
    color: #111827;
    font-size: var(--font-size-lg);
}

.diagram-controls {
    display: flex;
    flex-wrap: wrap;
    gap: 1rem;
    margin-bottom: 1rem;
    padding: 0.75rem;
    background: #f9fafb;
    border-radius: var(--border-radius);
}

.diagram-controls label {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    cursor: pointer;
    font-size: 0.875rem;
}

.dependency-diagram {
    width: 100%;
    min-height: 200px;
    overflow-x: auto;
    border: 1px solid #e5e7eb;
    border-radius: var(--border-radius);
    background: #fafafa;
}

.dependency-diagram svg {
    display: block;
    margin: 0 auto;
}

.diagram-node {
    cursor: pointer;
    transition: opacity 0.2s ease;
}

.diagram-node:hover {
    opacity: 0.8;
}

.diagram-link {
    stroke-linecap: round;
}

.diagram-link.active {
    stroke: var(--used-color);
}

.diagram-link.inactive {
    stroke: var(--unused-color);
    stroke-dasharray: 5, 5;
}

.no-data-message {
    text-align: center;
    padding: 2rem;
    color: #6b7280;
    font-style: italic;
}
"""

    def _generate_embedded_scripts(self) -> str:
        """Generate embedded JavaScript with placeholders for interactivity.

        Returns:
            JavaScript code as string.
        """
        return """    <script>
        // Placeholder for interactive functionality
        // This will be implemented in a future phase

        class ReportController {
            constructor() {
                this.data = null;
                this.filters = {
                    showUsed: true,
                    showUnused: true,
                    objectTypes: ['Form', 'Query', 'Macro', 'Report'],
                    searchTerm: '',
                    sortBy: 'name'
                };
                this.currentView = 'table';

                this.initializeEventListeners();
                this.loadData();
            }

            initializeEventListeners() {
                // View switching
                document.querySelectorAll('.view-btn').forEach(btn => {
                    btn.addEventListener('click', (e) => {
                        const view = e.target.dataset.view;
                        this.switchView(view);
                    });
                });

                // Filter controls
                document.getElementById('show-used').addEventListener('change', (e) => {
                    this.filters.showUsed = e.target.checked;
                    this.updateDisplay();
                });

                document.getElementById('show-unused').addEventListener('change', (e) => {
                    this.filters.showUnused = e.target.checked;
                    this.updateDisplay();
                });

                // Object type filters
                document.querySelectorAll('.object-filter').forEach(checkbox => {
                    checkbox.addEventListener('change', (e) => {
                        const type = e.target.dataset.type;
                        if (e.target.checked) {
                            if (!this.filters.objectTypes.includes(type)) {
                                this.filters.objectTypes.push(type);
                            }
                        } else {
                            this.filters.objectTypes = this.filters.objectTypes.filter(t => t !== type);
                        }
                        this.updateDisplay();
                    });
                });

                // Search functionality
                document.getElementById('table-search').addEventListener('input', (e) => {
                    this.filters.searchTerm = e.target.value.toLowerCase();
                    this.updateDisplay();
                });

                // Sorting
                document.getElementById('sort-select').addEventListener('change', (e) => {
                    this.filters.sortBy = e.target.value;
                    this.updateDisplay();
                });

                // Export functionality
                document.getElementById('export-btn').addEventListener('click', () => {
                    this.exportToCSV();
                });
            }

            loadData() {
                // Load embedded data
                const dataElement = document.getElementById('analysis-data');
                if (dataElement) {
                    this.data = JSON.parse(dataElement.textContent);
                    this.renderReport();
                }
            }

            renderReport() {
                this.renderTableView();
                this.renderUsageChart();
                this.updateStats();
                console.log('Report rendered with', Object.keys(this.data.tables).length, 'tables');
            }

            renderTableView(tables = null) {
                const tbody = document.getElementById('table-body');
                if (!tbody) return;

                const tablesToRender = tables || Object.values(this.data.tables);
                tbody.innerHTML = '';

                tablesToRender.forEach(table => {
                    const row = this.createTableRow(table);
                    tbody.appendChild(row);
                });
            }

            createTableRow(table) {
                // Placeholder for table row creation
                const row = document.createElement('tr');

                // Status cell
                const statusCell = document.createElement('td');
                const statusBadge = document.createElement('span');
                statusBadge.className = `table-status ${table.is_used ? 'used' : 'unused'}`;
                statusBadge.textContent = table.is_used ? 'Used' : 'Unused';
                statusCell.appendChild(statusBadge);

                // Name cell
                const nameCell = document.createElement('td');
                nameCell.textContent = table.table_name;

                // References cell
                const refsCell = document.createElement('td');
                refsCell.textContent = table.referencing_objects.length;

                // Types cell
                const typesCell = document.createElement('td');
                const typeCounts = {};
                table.referencing_objects.forEach(obj => {
                    typeCounts[obj.object_type] = (typeCounts[obj.object_type] || 0) + 1;
                });

                Object.entries(typeCounts).forEach(([type, count]) => {
                    const badge = document.createElement('span');
                    badge.className = `object-badge ${type.toLowerCase()}`;
                    badge.textContent = `${type}: ${count}`;
                    typesCell.appendChild(badge);
                });

                // Details cell
                const detailsCell = document.createElement('td');
                if (table.referencing_objects.length > 0) {
                    const detailsBtn = document.createElement('button');
                    detailsBtn.className = 'details-btn';
                    detailsBtn.textContent = 'Show Details';
                    detailsBtn.addEventListener('click', () => this.showTableDetails(table));
                    detailsCell.appendChild(detailsBtn);
                }

                row.appendChild(statusCell);
                row.appendChild(nameCell);
                row.appendChild(refsCell);
                row.appendChild(typesCell);
                row.appendChild(detailsCell);

                return row;
            }

            renderUsageChart(tables = null) {
                const canvas = document.getElementById('usage-chart');
                if (!canvas) return;

                const ctx = canvas.getContext('2d');
                const tablesToChart = tables || Object.values(this.data.tables);
                const totalTables = tablesToChart.length;
                const usedCount = tablesToChart.filter(t => t.is_used).length;
                const usedPercent = totalTables > 0 ? (usedCount / totalTables) * 100 : 0;
                const unusedPercent = 100 - usedPercent;

                // Clear canvas
                ctx.clearRect(0, 0, canvas.width, canvas.height);

                // Simple pie chart placeholder
                const centerX = canvas.width / 2;
                const centerY = canvas.height / 2;
                const radius = 80;

                // Draw used slice (green)
                ctx.beginPath();
                ctx.moveTo(centerX, centerY);
                ctx.arc(centerX, centerY, radius, -Math.PI/2, -Math.PI/2 + (usedPercent/100) * 2 * Math.PI);
                ctx.closePath();
                ctx.fillStyle = '#16a34a';
                ctx.fill();

                // Draw unused slice (red)
                ctx.beginPath();
                ctx.moveTo(centerX, centerY);
                ctx.arc(centerX, centerY, radius, -Math.PI/2 + (usedPercent/100) * 2 * Math.PI, -Math.PI/2 + 2 * Math.PI);
                ctx.closePath();
                ctx.fillStyle = '#dc2626';
                ctx.fill();

                // Draw center circle for donut effect
                ctx.beginPath();
                ctx.arc(centerX, centerY, 40, 0, 2 * Math.PI);
                ctx.fillStyle = 'white';
                ctx.fill();
            }

            showTableDetails(table) {
                // Create modal overlay
                const modal = document.createElement('div');
                modal.className = 'modal-overlay';
                modal.innerHTML = `
                    <div class="modal-content">
                        <div class="modal-header">
                            <h2>Table Details: ${table.table_name}</h2>
                            <button class="modal-close">&times;</button>
                        </div>
                        <div class="modal-body">
                            <div class="detail-section">
                                <h3>Basic Information</h3>
                                <p><strong>Status:</strong> <span class="status-badge ${table.is_used ? 'used' : 'unused'}">${table.is_used ? 'Used' : 'Unused'}</span></p>
                                <p><strong>Total References:</strong> ${table.referencing_objects.length}</p>
                            </div>
                            ${table.referencing_objects.length > 0 ? `
                            <div class="detail-section">
                                <h3>Referencing Objects</h3>
                                <div class="references-list">
                                    ${table.referencing_objects.map(obj => `
                                        <div class="reference-item">
                                            <span class="object-icon ${obj.object_type.toLowerCase()}">${this.getObjectIcon(obj.object_type)}</span>
                                            <span class="object-name">${obj.object_name}</span>
                                            <span class="object-type">${obj.object_type}</span>
                                            <span class="object-status ${obj.active ? 'active' : 'inactive'}">${obj.active ? 'Active' : 'Inactive'}</span>
                                        </div>
                                    `).join('')}
                                </div>
                            </div>
                            ` : ''}
                        </div>
                    </div>
                `;

                // Close modal functionality
                modal.querySelector('.modal-close').addEventListener('click', () => {
                    document.body.removeChild(modal);
                });
                modal.addEventListener('click', (e) => {
                    if (e.target === modal) {
                        document.body.removeChild(modal);
                    }
                });

                document.body.appendChild(modal);
            }

            getObjectIcon(type) {
                const icons = {
                    'Form': '📄',
                    'Query': '🔍',
                    'Macro': '⚡',
                    'Report': '📊'
                };
                return icons[type] || '📋';
            }

            exportToCSV() {
                const filteredTables = this.filterTables();
                const sortedTables = this.sortTables(filteredTables);

                // CSV header
                let csv = 'Table Name,Status,References,Object Types\n';

                // CSV rows
                sortedTables.forEach(table => {
                    const status = table.is_used ? 'Used' : 'Unused';
                    const refs = table.referencing_objects.length;

                    const typeCounts = {};
                    table.referencing_objects.forEach(obj => {
                        typeCounts[obj.object_type] = (typeCounts[obj.object_type] || 0) + 1;
                    });

                    const types = Object.entries(typeCounts)
                        .map(([type, count]) => `${type}:${count}`)
                        .join('; ');

                    // Escape commas and quotes in table name
                    const escapedName = table.table_name.replace(/"/g, '""');

                    csv += `"${escapedName}",${status},${refs},"${types}"\n`;
                });

                // Download CSV
                const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
                const link = document.createElement('a');
                const url = URL.createObjectURL(blob);
                link.setAttribute('href', url);
                link.setAttribute('download', 'table_dependencies.csv');
                link.style.visibility = 'hidden';
                document.body.appendChild(link);
                link.click();
                document.body.removeChild(link);
            }

            updateDisplay() {
                const filteredTables = this.filterTables();
                const sortedTables = this.sortTables(filteredTables);

                if (this.currentView === 'table') {
                    this.renderTableView(sortedTables);
                } else {
                    this.renderCardView(sortedTables);
                }

                this.updateStats(filteredTables);
            }

            updateStats(filteredTables = null) {
                const tables = filteredTables || Object.values(this.data.tables);
                const usedCount = tables.filter(t => t.is_used).length;
                const unusedCount = tables.filter(t => !t.is_used).length;

                // Update header stats
                const totalEl = document.getElementById('total-tables');
                const usedEl = document.getElementById('used-tables');
                const unusedEl = document.getElementById('unused-tables');

                if (totalEl) totalEl.textContent = tables.length;
                if (usedEl) usedEl.textContent = usedCount;
                if (unusedEl) unusedEl.textContent = unusedCount;

                // Update sidebar chart
                this.renderUsageChart(tables);
            }

            filterTables() {
                return Object.values(this.data.tables).filter(table => {
                    // Filter by usage status
                    if (!this.filters.showUsed && table.is_used) return false;
                    if (!this.filters.showUnused && !table.is_used) return false;

                    // Filter by object types
                    const hasMatchingType = table.referencing_objects.some(obj =>
                        this.filters.objectTypes.includes(obj.object_type)
                    );
                    if (table.referencing_objects.length > 0 && !hasMatchingType) return false;

                    // Filter by search term
                    if (this.filters.searchTerm) {
                        const searchLower = this.filters.searchTerm.toLowerCase();
                        const nameMatch = table.table_name.toLowerCase().includes(searchLower);
                        const refMatch = table.referencing_objects.some(obj =>
                            obj.object_name.toLowerCase().includes(searchLower)
                        );
                        if (!nameMatch && !refMatch) return false;
                    }

                    return true;
                });
            }

            sortTables(tables) {
                return tables.sort((a, b) => {
                    switch (this.filters.sortBy) {
                        case 'name':
                            return a.table_name.localeCompare(b.table_name);
                        case 'status':
                            if (a.is_used === b.is_used) {
                                return a.table_name.localeCompare(b.table_name);
                            }
                            return a.is_used ? -1 : 1;
                        case 'references':
                            const aRefs = a.referencing_objects.length;
                            const bRefs = b.referencing_objects.length;
                            if (aRefs === bRefs) {
                                return a.table_name.localeCompare(b.table_name);
                            }
                            return bRefs - aRefs;
                        default:
                            return a.table_name.localeCompare(b.table_name);
                    }
                });
            }

            renderCardView(tables) {
                const container = document.getElementById('card-container');
                if (!container) return;

                container.innerHTML = '';

                tables.forEach(table => {
                    const card = this.createTableCard(table);
                    container.appendChild(card);
                });
            }

            createTableCard(table) {
                const card = document.createElement('div');
                card.className = `table-card ${table.is_used ? 'used' : 'unused'}`;

                const statusBadge = document.createElement('div');
                statusBadge.className = 'card-status';
                statusBadge.textContent = table.is_used ? 'Used' : 'Unused';

                const title = document.createElement('h3');
                title.className = 'card-title';
                title.textContent = table.table_name;

                const refs = document.createElement('div');
                refs.className = 'card-refs';
                refs.textContent = `${table.referencing_objects.length} references`;

                const types = document.createElement('div');
                types.className = 'card-types';
                const typeCounts = {};
                table.referencing_objects.forEach(obj => {
                    typeCounts[obj.object_type] = (typeCounts[obj.object_type] || 0) + 1;
                });

                Object.entries(typeCounts).forEach(([type, count]) => {
                    const badge = document.createElement('span');
                    badge.className = `object-badge ${type.toLowerCase()}`;
                    badge.textContent = `${type}: ${count}`;
                    types.appendChild(badge);
                });

                const detailsBtn = document.createElement('button');
                detailsBtn.className = 'details-btn';
                detailsBtn.textContent = 'View Details';
                detailsBtn.addEventListener('click', () => this.showTableDetails(table));

                card.appendChild(statusBadge);
                card.appendChild(title);
                card.appendChild(refs);
                card.appendChild(types);
                card.appendChild(detailsBtn);

                return card;
            }

            switchView(view) {
                // Update button states
                document.querySelectorAll('.view-btn').forEach(btn => {
                    btn.classList.remove('active');
                });
                document.querySelector(`[data-view="${view}"]`).classList.add('active');

                // Update view containers
                document.querySelectorAll('.view-container').forEach(container => {
                    container.classList.remove('active');
                });
                document.getElementById(`${view}-view`).classList.add('active');

                this.currentView = view;
                this.updateDisplay();
            }

            // ========== Usage Table Methods ==========

            renderUsageTable() {
                const tbody = document.getElementById('usage-table-body');
                if (!tbody) return;

                const tables = Object.values(this.data.tables);
                tbody.innerHTML = '';

                tables.forEach(table => {
                    const row = this.createUsageTableRow(table);
                    tbody.appendChild(row);
                });
            }

            createUsageTableRow(table) {
                const row = document.createElement('tr');
                row.className = table.is_used ? 'row-used' : 'row-unused';

                // Status column
                const statusCell = document.createElement('td');
                statusCell.innerHTML = table.is_used
                    ? '<span class="status-indicator used">●</span> Used'
                    : '<span class="status-indicator unused">●</span> Unused';

                // Table name column
                const nameCell = document.createElement('td');
                nameCell.textContent = table.table_name;

                // Referencing objects column
                const refsCell = document.createElement('td');
                if (table.referencing_objects.length > 0) {
                    const objectList = document.createElement('ul');
                    objectList.className = 'object-list';
                    table.referencing_objects.forEach(obj => {
                        const item = document.createElement('li');
                        item.innerHTML = `<span class="object-type-badge ${obj.object_type.toLowerCase()}">${obj.object_type}</span> ${obj.object_name}`;
                        objectList.appendChild(item);
                    });
                    refsCell.appendChild(objectList);
                } else {
                    refsCell.textContent = '—';
                }

                // Object types summary column
                const typesCell = document.createElement('td');
                const typeCounts = {};
                table.referencing_objects.forEach(obj => {
                    typeCounts[obj.object_type] = (typeCounts[obj.object_type] || 0) + 1;
                });
                Object.entries(typeCounts).forEach(([type, count]) => {
                    const badge = document.createElement('span');
                    badge.className = `type-count-badge ${type.toLowerCase()}`;
                    badge.textContent = `${type}: ${count}`;
                    typesCell.appendChild(badge);
                });

                row.appendChild(statusCell);
                row.appendChild(nameCell);
                row.appendChild(refsCell);
                row.appendChild(typesCell);

                return row;
            }

            // ========== Dependency Diagram Methods ==========

            initDependencyDiagram() {
                this.diagramFilters = {
                    tables: true,
                    forms: true,
                    queries: true,
                    macros: true,
                    reports: true
                };

                // Initialize filter event listeners
                document.querySelectorAll('.diagram-controls input[type="checkbox"]').forEach(checkbox => {
                    checkbox.addEventListener('change', (e) => {
                        const type = e.target.id.replace('show-', '');
                        this.diagramFilters[type] = e.target.checked;
                        this.renderDependencyDiagram();
                    });
                });

                this.renderDependencyDiagram();
            }

            renderDependencyDiagram() {
                const container = document.getElementById('dependency-diagram');
                if (!container) return;

                const nodes = this.buildDiagramNodes();
                const links = this.buildDiagramLinks();

                if (nodes.length === 0) {
                    container.innerHTML = '<p class="no-data-message">No dependencies to display.</p>';
                    return;
                }

                const svg = this.createDiagramSVG(nodes, links);
                container.innerHTML = '';
                container.appendChild(svg);
            }

            buildDiagramNodes() {
                const nodes = [];
                let yOffset = 30;

                // Add tables
                if (this.diagramFilters.tables) {
                    Object.values(this.data.tables).forEach(table => {
                        nodes.push({
                            id: `table-${table.table_id}`,
                            label: table.table_name,
                            type: 'table',
                            status: table.is_used ? 'used' : 'unused',
                            x: 100,
                            y: yOffset
                        });
                        yOffset += 50;
                    });
                }

                // Add objects (Forms, Queries, Macros, Reports)
                const objectTypes = ['Form', 'Query', 'Macro', 'Report'];
                const objectXPositions = {
                    'Form': 350,
                    'Query': 500,
                    'Macro': 650,
                    'Report': 800
                };

                objectTypes.forEach(objType => {
                    if (!this.diagramFilters[objType.toLowerCase() + 's']) return;

                    const filterType = objType.toLowerCase() + 's';
                    if (!this.diagramFilters[filterType]) return;

                    Object.values(this.data.objects).forEach(obj => {
                        if (obj.object_type === objType) {
                            nodes.push({
                                id: `${objType.toLowerCase()}-${obj.object_id}`,
                                label: obj.object_name,
                                type: objType.toLowerCase(),
                                status: 'active',
                                x: objectXPositions[objType],
                                y: yOffset
                            });
                            yOffset += 40;
                        }
                    });
                });

                return nodes;
            }

            buildDiagramLinks() {
                const links = [];

                // Table → Object links
                Object.values(this.data.tables).forEach(table => {
                    table.referencing_objects.forEach(ref => {
                        const targetType = ref.object_type.toLowerCase();
                        const targetId = `${targetType}-${ref.object_id}`;
                        links.push({
                            source: `table-${table.table_id}`,
                            target: targetId,
                            active: ref.active
                        });
                    });
                });

                return links;
            }

            createDiagramSVG(nodes, links) {
                const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
                const width = 900;
                const height = Math.max(250, nodes.length * 45 + 60);
                svg.setAttribute('width', width.toString());
                svg.setAttribute('height', height.toString());
                svg.setAttribute('viewBox', `0 0 ${width} ${height}`);

                // Draw links first (behind nodes)
                links.forEach(link => {
                    const source = nodes.find(n => n.id === link.source);
                    const target = nodes.find(n => n.id === link.target);
                    if (source && target) {
                        const line = document.createElementNS('http://www.w3.org/2000/svg', 'line');
                        line.setAttribute('x1', source.x.toString());
                        line.setAttribute('y1', source.y.toString());
                        line.setAttribute('x2', target.x.toString());
                        line.setAttribute('y2', target.y.toString());
                        line.setAttribute('stroke', link.active ? '#16a34a' : '#dc2626');
                        line.setAttribute('stroke-width', '2');
                        line.setAttribute('class', link.active ? 'diagram-link active' : 'diagram-link inactive');
                        svg.appendChild(line);
                    }
                });

                // Draw nodes
                nodes.forEach(node => {
                    const g = document.createElementNS('http://www.w3.org/2000/svg', 'g');
                    g.setAttribute('class', 'diagram-node');

                    // Node rectangle
                    const rect = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
                    const textWidth = Math.max(100, node.label.length * 8);
                    rect.setAttribute('x', (node.x - textWidth / 2).toString());
                    rect.setAttribute('y', (node.y - 12).toString());
                    rect.setAttribute('width', textWidth.toString());
                    rect.setAttribute('height', '24');
                    rect.setAttribute('rx', '4');
                    rect.setAttribute('fill', this.getDiagramNodeColor(node.type));
                    if (node.status === 'unused') {
                        rect.setAttribute('stroke', '#dc2626');
                        rect.setAttribute('stroke-width', '2');
                    }
                    g.appendChild(rect);

                    // Node label
                    const text = document.createElementNS('http://www.w3.org/2000/svg', 'text');
                    text.setAttribute('x', node.x.toString());
                    text.setAttribute('y', (node.y + 4).toString());
                    text.setAttribute('text-anchor', 'middle');
                    text.setAttribute('fill', 'white');
                    text.setAttribute('font-size', '11');
                    text.setAttribute('font-weight', '500');
                    text.textContent = node.label.length > 15 ? node.label.substring(0, 14) + '…' : node.label;
                    g.appendChild(text);

                    svg.appendChild(g);
                });

                return svg;
            }

            getDiagramNodeColor(type) {
                const colors = {
                    'table': '#2563eb',
                    'form': '#3b82f6',
                    'query': '#f59e0b',
                    'macro': '#dc2626',
                    'report': '#16a34a'
                };
                return colors[type] || '#6b7280';
            }
        }

        // Initialize when DOM is loaded
        document.addEventListener('DOMContentLoaded', () => {
            const controller = new ReportController();
            // Initialize usage table
            controller.renderUsageTable();
            // Initialize dependency diagram
            controller.initDependencyDiagram();
        });
    </script>"""""