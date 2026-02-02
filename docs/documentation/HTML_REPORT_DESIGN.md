# HTML Report Generation Design

## Overview

The HTML report generator creates self-contained, responsive reports that visualize database dependency analysis results. The reports include interactive features, color-coded visualizations, and comprehensive statistics without requiring external dependencies.

## Report Structure

### Complete HTML Document Structure

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Database Dependency Analysis Report</title>
    <style>
        /* Embedded CSS styles */
    </style>
</head>
<body>
    <div class="container">
        <header class="report-header">
            <!-- Header with title and summary stats -->
        </header>

        <nav class="sidebar">
            <!-- Navigation and filters -->
        </nav>

        <main class="main-content">
            <!-- Main report content -->
        </main>
    </div>

    <script>
        /* Embedded JavaScript for interactivity */
    </script>
</body>
</html>
```

## Layout Components

### 1. Header Section

```html
<header class="report-header">
    <div class="header-content">
        <h1>Database Dependency Analysis Report</h1>
        <div class="summary-stats">
            <div class="stat-card">
                <div class="stat-number" id="total-tables">0</div>
                <div class="stat-label">Total Tables</div>
            </div>
            <div class="stat-card">
                <div class="stat-number used" id="used-tables">0</div>
                <div class="stat-label">Used Tables</div>
            </div>
            <div class="stat-card">
                <div class="stat-number unused" id="unused-tables">0</div>
                <div class="stat-label">Unused Tables</div>
            </div>
            <div class="stat-card">
                <div class="stat-number" id="total-objects">0</div>
                <div class="stat-label">Total Objects</div>
            </div>
        </div>
        <div class="report-meta">
            <span class="timestamp">Generated: <span id="timestamp"></span></span>
            <span class="processing-time">Processing Time: <span id="processing-time"></span></span>
        </div>
    </div>
</header>
```

### 2. Sidebar Navigation

```html
<nav class="sidebar">
    <div class="sidebar-section">
        <h3>Quick Stats</h3>
        <div class="usage-chart">
            <canvas id="usage-chart" width="200" height="200"></canvas>
            <div class="chart-legend">
                <div class="legend-item">
                    <span class="color-box used"></span>
                    <span>Used (<span id="used-percentage">0</span>%)</span>
                </div>
                <div class="legend-item">
                    <span class="color-box unused"></span>
                    <span>Unused (<span id="unused-percentage">0</span>%)</span>
                </div>
            </div>
        </div>
    </div>

    <div class="sidebar-section">
        <h3>Object Types</h3>
        <div class="object-type-stats">
            <div class="type-stat" data-type="Form">
                <span class="type-icon form-icon">📄</span>
                <span class="type-count" id="form-count">0</span>
                <span class="type-label">Forms</span>
            </div>
            <div class="type-stat" data-type="Query">
                <span class="type-icon query-icon">🔍</span>
                <span class="type-count" id="query-count">0</span>
                <span class="type-label">Queries</span>
            </div>
            <div class="type-stat" data-type="Macro">
                <span class="type-icon macro-icon">⚡</span>
                <span class="type-count" id="macro-count">0</span>
                <span class="type-label">Macros</span>
            </div>
            <div class="type-stat" data-type="Report">
                <span class="type-icon report-icon">📊</span>
                <span class="type-count" id="report-count">0</span>
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
</nav>
```

### 3. Main Content Area

```html
<main class="main-content">
    <div class="content-header">
        <h2>Table Dependencies</h2>
        <div class="view-controls">
            <button class="view-btn active" data-view="table">Table View</button>
            <button class="view-btn" data-view="cards">Card View</button>
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
</main>
```

## CSS Styling Design

### Color Scheme and Variables

```css
:root {
    /* Color Palette */
    --primary-color: #2563eb;
    --success-color: #16a34a;
    --danger-color: #dc2626;
    --warning-color: #ca8a04;
    --info-color: #0891b2;

    /* Object Type Colors */
    --form-color: #3b82f6;    /* Blue */
    --query-color: #f59e0b;  /* Orange */
    --macro-color: #dc2626;  /* Red */
    --report-color: #16a34a; /* Green */

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
```

### Responsive Design

```css
/* Desktop Layout */
@media (min-width: 1024px) {
    .container {
        display: grid;
        grid-template-columns: var(--sidebar-width) 1fr;
        grid-template-rows: var(--header-height) 1fr;
        grid-template-areas:
            "header header"
            "sidebar main";
    }
}

/* Tablet Layout */
@media (max-width: 1023px) and (min-width: 768px) {
    .container {
        display: grid;
        grid-template-columns: 250px 1fr;
        grid-template-rows: auto 1fr;
        grid-template-areas:
            "header header"
            "sidebar main";
    }
}

/* Mobile Layout */
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
}
```

### Component Styles

```css
/* Header Styles */
.report-header {
    grid-area: header;
    background: linear-gradient(135deg, var(--primary-color), #1d4ed8);
    color: white;
    padding: 2rem;
    box-shadow: var(--shadow);
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

.stat-number.used { color: var(--success-color); }
.stat-number.unused { color: var(--danger-color); }

/* Sidebar Styles */
.sidebar {
    grid-area: sidebar;
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

/* Table Styles */
.dependencies-table {
    width: 100%;
    border-collapse: collapse;
    margin-top: 1rem;
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

.table-card.used .card-header {
    border-left: 4px solid var(--used-color);
}

.table-card.unused .card-header {
    border-left: 4px solid var(--unused-color);
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
```

## JavaScript Interactivity

### Core Functionality

```javascript
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
                    this.filters.objectTypes.push(type);
                } else {
                    this.filters.objectTypes = this.filters.objectTypes.filter(t => t !== type);
                }
                this.updateDisplay();
            });
        });

        // Search
        document.getElementById('table-search').addEventListener('input', (e) => {
            this.filters.searchTerm = e.target.value.toLowerCase();
            this.updateDisplay();
        });

        // Sort
        document.getElementById('sort-select').addEventListener('change', (e) => {
            this.filters.sortBy = e.target.value;
            this.updateDisplay();
        });

        // View switching
        document.querySelectorAll('.view-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                this.switchView(e.target.dataset.view);
            });
        });
    }

    loadData() {
        // Data is embedded in the HTML as JSON
        const dataElement = document.getElementById('analysis-data');
        if (dataElement) {
            this.data = JSON.parse(dataElement.textContent);
            this.renderReport();
        }
    }

    updateDisplay() {
        const filteredTables = this.filterTables();
        const sortedTables = this.sortTables(filteredTables);

        if (this.currentView === 'table') {
            this.renderTableView(sortedTables);
        } else {
            this.renderCardView(sortedTables);
        }

        this.updateStats();
    }

    filterTables() {
        return Object.values(this.data.tables).filter(table => {
            // Status filter
            if (!this.filters.showUsed && table.is_used) return false;
            if (!this.filters.showUnused && !table.is_used) return false;

            // Search filter
            if (this.filters.searchTerm &&
                !table.table_name.toLowerCase().includes(this.filters.searchTerm)) {
                return false;
            }

            // Object type filter
            const hasMatchingObjects = table.referencing_objects.some(obj =>
                this.filters.objectTypes.includes(obj.object_type)
            );

            if (table.referencing_objects.length > 0 && !hasMatchingObjects) {
                return false;
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
                    return b.referencing_objects.length - a.referencing_objects.length;
                default:
                    return 0;
            }
        });
    }

    renderTableView(tables) {
        const tbody = document.getElementById('table-body');
        tbody.innerHTML = '';

        tables.forEach(table => {
            const row = this.createTableRow(table);
            tbody.appendChild(row);
        });
    }

    createTableRow(table) {
        const row = document.createElement('tr');

        const statusCell = document.createElement('td');
        const statusBadge = document.createElement('span');
        statusBadge.className = `table-status ${table.is_used ? 'used' : 'unused'}`;
        statusBadge.textContent = table.is_used ? 'Used' : 'Unused';
        statusCell.appendChild(statusBadge);

        const nameCell = document.createElement('td');
        nameCell.textContent = table.table_name;

        const refsCell = document.createElement('td');
        refsCell.textContent = table.referencing_objects.length;

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

    renderCardView(tables) {
        const container = document.getElementById('card-container');
        container.innerHTML = '';

        tables.forEach(table => {
            const card = this.createTableCard(table);
            container.appendChild(card);
        });
    }

    createTableCard(table) {
        const card = document.createElement('div');
        card.className = `table-card ${table.is_used ? 'used' : 'unused'}`;

        card.innerHTML = `
            <div class="card-header">
                <h3>${table.table_name}</h3>
                <span class="status-badge ${table.is_used ? 'used' : 'unused'}">
                    ${table.is_used ? 'Used' : 'Unused'}
                </span>
            </div>
            <div class="card-body">
                <p><strong>References:</strong> ${table.referencing_objects.length}</p>
                <div class="object-badges">
                    ${this.createObjectBadges(table.referencing_objects)}
                </div>
            </div>
        `;

        return card;
    }

    createObjectBadges(objects) {
        const typeCounts = {};
        objects.forEach(obj => {
            typeCounts[obj.object_type] = (typeCounts[obj.object_type] || 0) + 1;
        });

        return Object.entries(typeCounts)
            .map(([type, count]) => `<span class="object-badge ${type.toLowerCase()}">${type}: ${count}</span>`)
            .join('');
    }

    showTableDetails(table) {
        // Show modal or expandable details
        const modal = document.createElement('div');
        modal.className = 'details-modal';
        modal.innerHTML = `
            <div class="modal-content">
                <div class="modal-header">
                    <h3>References for ${table.table_name}</h3>
                    <button class="close-btn">&times;</button>
                </div>
                <div class="modal-body">
                    <ul class="references-list">
                        ${table.referencing_objects.map(obj =>
                            `<li class="reference-item ${obj.object_type.toLowerCase()}">
                                <strong>${obj.object_type}:</strong> ${obj.object_name}
                                ${!obj.active ? '<span class="inactive">(Inactive)</span>' : ''}
                            </li>`
                        ).join('')}
                    </ul>
                </div>
            </div>
        `;

        document.body.appendChild(modal);

        modal.querySelector('.close-btn').addEventListener('click', () => {
            document.body.removeChild(modal);
        });
    }

    updateStats() {
        // Update sidebar statistics
        const filteredTables = this.filterTables();
        const usedCount = filteredTables.filter(t => t.is_used).length;
        const unusedCount = filteredTables.filter(t => !t.is_used).length;

        document.getElementById('used-tables').textContent = usedCount;
        document.getElementById('unused-tables').textContent = unusedCount;
    }

    switchView(view) {
        this.currentView = view;

        // Update button states
        document.querySelectorAll('.view-btn').forEach(btn => {
            btn.classList.toggle('active', btn.dataset.view === view);
        });

        // Update view containers
        document.querySelectorAll('.view-container').forEach(container => {
            container.classList.toggle('active', container.id === `${view}-view`);
        });

        this.updateDisplay();
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new ReportController();
});
```

## Data Embedding

Analysis data is embedded in the HTML as JSON:

```html
<script type="application/json" id="analysis-data">
{
  "tables": {...},
  "objects": {...},
  "statistics": {...},
  "timestamp": "...",
  "processing_time": 0.5
}
</script>
```

## Chart Generation

Simple pie chart using Canvas API:

```javascript
function drawUsageChart(usedPercent, unusedPercent) {
    const canvas = document.getElementById('usage-chart');
    const ctx = canvas.getContext('2d');
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
```

## Performance Considerations

1. **Lazy Loading**: Only render visible table rows/cards
2. **Debounced Search**: Delay search updates to avoid excessive filtering
3. **Virtual Scrolling**: For very large datasets (>1000 tables)
4. **Memory Management**: Clean up event listeners and DOM elements

## Accessibility Features

1. **Semantic HTML**: Proper heading hierarchy and ARIA labels
2. **Keyboard Navigation**: Tab through interactive elements
3. **Screen Reader Support**: Descriptive alt texts and labels
4. **Color Contrast**: WCAG compliant color combinations
5. **Focus Management**: Proper focus indicators and management

## Browser Compatibility

- **Modern Browsers**: Full feature support (Chrome, Firefox, Safari, Edge)
- **Fallbacks**: Graceful degradation for older browsers
- **Mobile Support**: Touch-friendly interface on mobile devices
- **Print Styles**: Optimized layout for printing reports

## Dependency Visualization Component

### Tree View Structure

```html
<div class="dependency-section">
    <h2>Dependency Graph</h2>
    <div class="view-controls">
        <button class="view-btn active" data-view="tree">Tree View</button>
        <button class="view-btn" data-view="graph">Graph View</button>
    </div>
    <div id="dependency-container">
        <!-- Tree or graph will be rendered here -->
    </div>
</div>
```

### Tree View Implementation

```javascript
renderDependencyTree() {
    const container = document.getElementById('dependency-container');
    container.innerHTML = '';

    // Build dependency tree from objects and their dependencies
    const treeData = this.buildDependencyTree();
    const treeElement = this.createTreeElement(treeData);
    container.appendChild(treeElement);
}

buildDependencyTree() {
    // Create a tree structure from object dependencies
    const tree = { name: 'Root', children: [] };
    const processed = new Set();

    Object.values(this.data.objects).forEach(obj => {
        if (!processed.has(obj.object_id)) {
            const node = this.buildObjectNode(obj, processed);
            if (node) tree.children.push(node);
        }
    });

    return tree;
}

buildObjectNode(obj, processed) {
    if (processed.has(obj.object_id)) return null;
    processed.add(obj.object_id);

    const node = {
        name: `${obj.object_type}: ${obj.object_name}`,
        object_id: obj.object_id,
        children: []
    };

    // Find dependencies (objects that depend on this object)
    Object.values(this.data.object_dependencies || []).forEach(dep => {
        if (dep.target_object_id === obj.object_id && dep.active) {
            const dependentObj = this.data.objects[dep.source_object_id];
            if (dependentObj && !processed.has(dependentObj.object_id)) {
                const childNode = this.buildObjectNode(dependentObj, processed);
                if (childNode) node.children.push(childNode);
            }
        }
    });

    return node;
}

createTreeElement(node, level = 0) {
    const div = document.createElement('div');
    div.className = `tree-node level-${level}`;
    div.innerHTML = `
        <div class="tree-content">
            <span class="tree-toggle">${node.children.length > 0 ? '▶' : ''}</span>
            <span class="tree-label">${node.name}</span>
        </div>
    `;

    if (node.children.length > 0) {
        const childrenContainer = document.createElement('div');
        childrenContainer.className = 'tree-children';
        node.children.forEach(child => {
            childrenContainer.appendChild(this.createTreeElement(child, level + 1));
        });
        div.appendChild(childrenContainer);

        // Add toggle functionality
        const toggle = div.querySelector('.tree-toggle');
        toggle.addEventListener('click', () => {
            childrenContainer.classList.toggle('collapsed');
            toggle.textContent = childrenContainer.classList.contains('collapsed') ? '▶' : '▼';
        });
    }

    return div;
}
```

### Graph View Implementation

```javascript
renderDependencyGraph() {
    const container = document.getElementById('dependency-container');
    container.innerHTML = '<svg id="dependency-svg" width="100%" height="600"></svg>';

    // Simple force-directed graph using SVG
    const svg = d3.select('#dependency-svg');
    const width = container.clientWidth;
    const height = 600;

    // Prepare nodes and links
    const nodes = Object.values(this.data.objects).map(obj => ({
        id: obj.object_id,
        name: `${obj.object_type}: ${obj.object_name}`,
        group: obj.object_type
    }));

    const links = (this.data.object_dependencies || [])
        .filter(dep => dep.active)
        .map(dep => ({
            source: dep.source_object_id,
            target: dep.target_object_id
        }));

    // Create simulation
    const simulation = d3.forceSimulation(nodes)
        .force('link', d3.forceLink(links).id(d => d.id))
        .force('charge', d3.forceManyBody())
        .force('center', d3.forceCenter(width / 2, height / 2));

    // Draw links
    const link = svg.append('g')
        .selectAll('line')
        .data(links)
        .enter().append('line')
        .attr('stroke', '#999')
        .attr('stroke-opacity', 0.6);

    // Draw nodes
    const node = svg.append('g')
        .selectAll('circle')
        .data(nodes)
        .enter().append('circle')
        .attr('r', 8)
        .attr('fill', d => this.getObjectTypeColor(d.group))
        .call(d3.drag()
            .on('start', dragstarted)
            .on('drag', dragged)
            .on('end', dragended));

    // Add labels
    const label = svg.append('g')
        .selectAll('text')
        .data(nodes)
        .enter().append('text')
        .text(d => d.name)
        .attr('font-size', 10)
        .attr('dx', 12)
        .attr('dy', 4);

    simulation.on('tick', () => {
        link
            .attr('x1', d => d.source.x)
            .attr('y1', d => d.source.y)
            .attr('x2', d => d.target.x)
            .attr('y2', d => d.target.y);

        node
            .attr('cx', d => d.x)
            .attr('cy', d => d.y);

        label
            .attr('x', d => d.x)
            .attr('y', d => d.y);
    });

    function dragstarted(event, d) {
        if (!event.active) simulation.alphaTarget(0.3).restart();
        d.fx = d.x;
        d.fy = d.y;
    }

    function dragged(event, d) {
        d.fx = event.x;
        d.fy = event.y;
    }

    function dragended(event, d) {
        if (!event.active) simulation.alphaTarget(0);
        d.fx = null;
        d.fy = null;
    }
}

getObjectTypeColor(type) {
    const colors = {
        'Form': '#3b82f6',
        'Query': '#f59e0b',
        'Macro': '#dc2626',
        'Report': '#16a34a'
    };
    return colors[type] || '#6b7280';
}
```

## Enhanced Statistics Visualization

### Additional Charts

```html
<div class="stats-section">
    <h2>Detailed Statistics</h2>
    <div class="charts-grid">
        <div class="chart-container">
            <h3>Objects by Type</h3>
            <canvas id="object-type-chart" width="300" height="200"></canvas>
        </div>
        <div class="chart-container">
            <h3>Dependency Distribution</h3>
            <canvas id="dependency-chart" width="300" height="200"></canvas>
        </div>
        <div class="chart-container">
            <h3>Table Usage Over Time</h3>
            <canvas id="usage-trend-chart" width="300" height="200"></canvas>
        </div>
    </div>
</div>
```

### Chart Rendering Functions

```javascript
renderStatisticsCharts() {
    this.renderObjectTypeChart();
    this.renderDependencyChart();
    this.renderUsageTrendChart();
}

renderObjectTypeChart() {
    const canvas = document.getElementById('object-type-chart');
    const ctx = canvas.getContext('2d');
    const stats = this.data.statistics;

    const data = Object.entries(stats.objects_by_type).map(([type, count]) => ({
        label: type,
        value: count,
        color: this.getObjectTypeColor(type)
    }));

    this.drawBarChart(ctx, data, 'Object Types');
}

renderDependencyChart() {
    const canvas = document.getElementById('dependency-chart');
    const ctx = canvas.getContext('2d');
    const stats = this.data.statistics;

    const data = [
        { label: 'Active Dependencies', value: stats.active_dependencies, color: '#16a34a' },
        { label: 'Inactive Dependencies', value: stats.total_dependencies - stats.active_dependencies, color: '#dc2626' }
    ];

    this.drawBarChart(ctx, data, 'Dependencies');
}

renderUsageTrendChart() {
    // This would require historical data, for now show current usage
    const canvas = document.getElementById('usage-trend-chart');
    const ctx = canvas.getContext('2d');
    const stats = this.data.statistics;

    const data = [
        { label: 'Used Tables', value: stats.used_tables, color: '#16a34a' },
        { label: 'Unused Tables', value: stats.unused_tables, color: '#dc2626' }
    ];

    this.drawBarChart(ctx, data, 'Table Usage');
}

drawBarChart(ctx, data, title) {
    const canvas = ctx.canvas;
    const width = canvas.width;
    const height = canvas.height;
    const padding = 40;
    const chartWidth = width - 2 * padding;
    const chartHeight = height - 2 * padding;

    // Clear canvas
    ctx.clearRect(0, 0, width, height);

    // Find max value
    const maxValue = Math.max(...data.map(d => d.value));

    // Draw bars
    const barWidth = chartWidth / data.length;
    data.forEach((item, index) => {
        const barHeight = (item.value / maxValue) * chartHeight;
        const x = padding + index * barWidth;
        const y = height - padding - barHeight;

        ctx.fillStyle = item.color;
        ctx.fillRect(x, y, barWidth - 10, barHeight);

        // Draw label
        ctx.fillStyle = '#374151';
        ctx.font = '12px Arial';
        ctx.textAlign = 'center';
        ctx.fillText(item.label, x + (barWidth - 10) / 2, height - 10);

        // Draw value
        ctx.fillText(item.value.toString(), x + (barWidth - 10) / 2, y - 5);
    });

    // Draw title
    ctx.fillStyle = '#111827';
    ctx.font = '16px Arial';
    ctx.textAlign = 'center';
    ctx.fillText(title, width / 2, 20);
}
```

## Export Capabilities

### Export Controls

```html
<div class="export-section">
    <h2>Export Report</h2>
    <div class="export-buttons">
        <button id="export-pdf" class="export-btn">Export as PDF</button>
        <button id="export-csv" class="export-btn">Export as CSV</button>
        <button id="export-json" class="export-btn">Export as JSON</button>
        <button id="export-html" class="export-btn">Export as HTML</button>
    </div>
</div>
```

### Export Functions

```javascript
initializeExportListeners() {
    document.getElementById('export-pdf').addEventListener('click', () => this.exportAsPDF());
    document.getElementById('export-csv').addEventListener('click', () => this.exportAsCSV());
    document.getElementById('export-json').addEventListener('click', () => this.exportAsJSON());
    document.getElementById('export-html').addEventListener('click', () => this.exportAsHTML());
}

exportAsPDF() {
    // Use jsPDF for PDF generation
    const { jsPDF } = window.jspdf;
    const doc = new jsPDF();

    // Add title
    doc.setFontSize(20);
    doc.text('Database Dependency Analysis Report', 20, 30);

    // Add summary
    doc.setFontSize(12);
    const stats = this.data.statistics;
    doc.text(`Total Tables: ${stats.total_tables}`, 20, 50);
    doc.text(`Used Tables: ${stats.used_tables} (${stats.usage_percentage.toFixed(1)}%)`, 20, 60);
    doc.text(`Unused Tables: ${stats.unused_tables} (${stats.unused_percentage.toFixed(1)}%)`, 20, 70);

    // Add tables data
    let yPos = 90;
    doc.text('Tables:', 20, yPos);
    yPos += 10;

    Object.values(this.data.tables).forEach(table => {
        if (yPos > 270) {
            doc.addPage();
            yPos = 30;
        }
        doc.text(`${table.table_name}: ${table.is_used ? 'Used' : 'Unused'} (${table.referencing_objects.length} refs)`, 20, yPos);
        yPos += 10;
    });

    doc.save('dependency-analysis-report.pdf');
}

exportAsCSV() {
    const headers = ['Table Name', 'Status', 'Reference Count', 'Referencing Objects'];
    const rows = [headers];

    Object.values(this.data.tables).forEach(table => {
        const objects = table.referencing_objects.map(obj => `${obj.object_type}: ${obj.object_name}`).join('; ');
        rows.push([
            table.table_name,
            table.is_used ? 'Used' : 'Unused',
            table.referencing_objects.length.toString(),
            objects
        ]);
    });

    const csvContent = rows.map(row => row.map(field => `"${field}"`).join(',')).join('\n');
    this.downloadFile(csvContent, 'dependency-analysis-report.csv', 'text/csv');
}

exportAsJSON() {
    const jsonContent = JSON.stringify(this.data, null, 2);
    this.downloadFile(jsonContent, 'dependency-analysis-report.json', 'application/json');
}

exportAsHTML() {
    // Clone the current document and remove interactive elements
    const clonedDoc = document.documentElement.cloneNode(true);

    // Remove scripts and interactive elements
    clonedDoc.querySelectorAll('script').forEach(script => script.remove());
    clonedDoc.querySelectorAll('.export-section, .view-controls').forEach(el => el.remove());

    const htmlContent = `<!DOCTYPE html>\n${clonedDoc.outerHTML}`;
    this.downloadFile(htmlContent, 'dependency-analysis-report.html', 'text/html');
}

downloadFile(content, filename, mimeType) {
    const blob = new Blob([content], { type: mimeType });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
}
```

## Integration with Analysis Results

### Data Mapping

The HTML report integrates with the analysis results as follows:

- **AnalysisResult.tables**: Used to populate table views, cards, and export data
- **AnalysisResult.objects**: Used for dependency visualization and object type statistics
- **AnalysisResult.statistics**: Used for summary stats, charts, and sidebar metrics
- **AnalysisResult.timestamp**: Displayed in report header
- **AnalysisResult.processing_time**: Displayed in report header
- **TableDependency**: Used to show table references in details modals
- **ObjectDependency**: Used to build dependency trees and graphs
- **ObjectReference**: Used to display referencing objects with type badges

### Template Generation

The report generator will:

1. Serialize AnalysisResult to JSON
2. Embed the JSON in the HTML template
3. Populate static elements (header stats, sidebar counts)
4. Initialize JavaScript controller with the data
5. Render interactive components on page load

This ensures the report is self-contained and can be viewed offline with full functionality.