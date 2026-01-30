# XML Parsing Strategy

## Overview

Microsoft Access XML exports include namespace declarations that must be handled properly for reliable parsing. This document outlines the strategy for parsing the 4 XML files with robust namespace handling and error recovery.

## XML File Structure Analysis

### Analysis_Tables.xml
```xml
<?xml version="1.0" encoding="utf-8"?>
<dataroot xmlns:od="urn:schemas-microsoft-com:officedata">
  <Analysis_Tables>
    <TableID>1</TableID>
    <TableName>Customers</TableName>
  </Analysis_Tables>
  <Analysis_Tables>
    <TableID>2</TableID>
    <TableName>Orders</TableName>
  </Analysis_Tables>
</dataroot>
```

### Analysis_Objects.xml
```xml
<?xml version="1.0" encoding="utf-8"?>
<dataroot xmlns:od="urn:schemas-microsoft-com:officedata">
  <Analysis_Objects>
    <ObjectID>100</ObjectID>
    <ObjectName>CustomerForm</ObjectName>
    <ObjectType>Form</ObjectType>
  </Analysis_Objects>
</dataroot>
```

### Analysis_TableDependencies.xml
```xml
<?xml version="1.0" encoding="utf-8"?>
<dataroot xmlns:od="urn:schemas-microsoft-com:officedata">
  <Analysis_TableDependencies>
    <ObjectID>100</ObjectID>
    <TableID>1</TableID>
    <Active>true</Active>
  </Analysis_TableDependencies>
</dataroot>
```

### Analysis_ObjectDependencies.xml
```xml
<?xml version="1.0" encoding="utf-8"?>
<dataroot xmlns:od="urn:schemas-microsoft-com:officedata">
  <Analysis_ObjectDependencies>
    <SourceObjectID>100</SourceObjectID>
    <TargetObjectID>200</TargetObjectID>
    <Active>true</Active>
  </Analysis_ObjectDependencies>
</dataroot>
```

## Namespace Handling Strategy

### Core Principles

1. **Namespace-Aware Parsing**: Use `xml.etree.ElementTree` with namespace handling
2. **Fallback Mechanisms**: Support both namespaced and non-namespaced XML
3. **Error Recovery**: Graceful handling of malformed XML
4. **Performance**: Efficient parsing for large files (500+ tables, 6000+ objects)

### Namespace Map

```python
# Common namespace mappings found in Access XML exports
NAMESPACE_MAP = {
    'od': 'urn:schemas-microsoft-com:officedata',
    'xsi': 'http://www.w3.org/2001/XMLSchema-instance',
    'xsd': 'http://www.w3.org/2001/XMLSchema'
}
```

## Parser Architecture

### Base XML Parser Class

```python
class BaseXMLParser:
    """Base class for XML parsing with namespace handling."""

    def __init__(self, config: AnalysisConfig):
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)
        self.namespace_map = {
            'od': 'urn:schemas-microsoft-com:officedata'
        }

    def parse_file(self, file_path: Path) -> ET.ElementTree:
        """Parse XML file with error handling."""
        try:
            # Register namespaces to avoid ns0: prefixes
            for prefix, uri in self.namespace_map.items():
                ET.register_namespace(prefix, uri)

            tree = ET.parse(file_path)
            self._validate_root(tree.getroot())
            return tree

        except ET.ParseError as e:
            raise XMLParseError(f"Failed to parse {file_path}: {e}")
        except FileNotFoundError:
            raise FileNotFoundError(f"XML file not found: {file_path}")

    def _validate_root(self, root: ET.Element) -> None:
        """Validate root element structure."""
        if root.tag != 'dataroot':
            self.logger.warning(f"Unexpected root tag: {root.tag}")

    def find_elements(self, root: ET.Element, path: str) -> List[ET.Element]:
        """Find elements with namespace-aware path resolution."""
        # Try namespaced path first
        namespaced_path = path
        if not path.startswith('{'):
            # Add namespace prefix if not present
            namespaced_path = f"{{{self.namespace_map['od']}}}{path}"

        elements = root.findall(namespaced_path)

        # Fallback to non-namespaced if no elements found
        if not elements:
            elements = root.findall(path)
            if elements:
                self.logger.info(f"Found elements using non-namespaced path: {path}")

        return elements

    def get_text(self, element: ET.Element, tag: str, default: str = "") -> str:
        """Get text content from element with namespace handling."""
        # Try namespaced tag first
        namespaced_tag = f"{{{self.namespace_map['od']}}}{tag}"
        child = element.find(namespaced_tag)

        if child is None:
            # Try non-namespaced
            child = element.find(tag)

        return child.text.strip() if child is not None and child.text else default

    def get_int(self, element: ET.Element, tag: str, default: int = 0) -> int:
        """Get integer value from element."""
        text = self.get_text(element, tag)
        try:
            return int(text) if text else default
        except ValueError:
            self.logger.warning(f"Invalid integer value for {tag}: {text}")
            return default

    def get_bool(self, element: ET.Element, tag: str, default: bool = True) -> bool:
        """Get boolean value from element."""
        text = self.get_text(element, tag).lower()
        if text in ('true', '1', 'yes'):
            return True
        elif text in ('false', '0', 'no'):
            return False
        else:
            self.logger.warning(f"Invalid boolean value for {tag}: {text}")
            return default
```

## Specific Parser Implementations

### Table Parser

```python
class TableParser(BaseXMLParser):
    """Parser for Analysis_Tables.xml"""

    def parse(self, file_path: Path) -> Dict[int, Table]:
        """Parse table definitions."""
        tree = self.parse_file(file_path)
        root = tree.getroot()

        tables = {}
        table_elements = self.find_elements(root, 'Analysis_Tables')

        for elem in table_elements:
            try:
                table = self._parse_table_element(elem)
                if table.table_id not in tables:
                    tables[table.table_id] = table
                else:
                    self.logger.warning(f"Duplicate table ID: {table.table_id}")
            except (ValueError, KeyError) as e:
                self.logger.error(f"Failed to parse table element: {e}")
                continue

        self.logger.info(f"Parsed {len(tables)} tables")
        return tables

    def _parse_table_element(self, elem: ET.Element) -> Table:
        """Parse individual table element."""
        table_id = self.get_int(elem, 'TableID')
        table_name = self.get_text(elem, 'TableName')

        if not table_id or not table_name:
            raise ValueError("Missing required table fields")

        return Table(
            table_id=table_id,
            table_name=table_name
        )
```

### Object Parser

```python
class ObjectParser(BaseXMLParser):
    """Parser for Analysis_Objects.xml"""

    def parse(self, file_path: Path) -> Dict[int, DatabaseObject]:
        """Parse object definitions."""
        tree = self.parse_file(file_path)
        root = tree.getroot()

        objects = {}
        object_elements = self.find_elements(root, 'Analysis_Objects')

        for elem in object_elements:
            try:
                obj = self._parse_object_element(elem)
                if obj.object_id not in objects:
                    objects[obj.object_id] = obj
                else:
                    self.logger.warning(f"Duplicate object ID: {obj.object_id}")
            except (ValueError, KeyError) as e:
                self.logger.error(f"Failed to parse object element: {e}")
                continue

        self.logger.info(f"Parsed {len(objects)} objects")
        return objects

    def _parse_object_element(self, elem: ET.Element) -> DatabaseObject:
        """Parse individual object element."""
        object_id = self.get_int(elem, 'ObjectID')
        object_name = self.get_text(elem, 'ObjectName')
        object_type = self.get_text(elem, 'ObjectType')

        if not object_id or not object_name or not object_type:
            raise ValueError("Missing required object fields")

        return DatabaseObject(
            object_id=object_id,
            object_name=object_name,
            object_type=object_type
        )
```

### Dependency Parsers

```python
class DependencyParser(BaseXMLParser):
    """Parser for dependency XML files"""

    def parse_table_dependencies(self, file_path: Path) -> List[TableDependency]:
        """Parse table dependency relationships."""
        tree = self.parse_file(file_path)
        root = tree.getroot()

        dependencies = []
        dep_elements = self.find_elements(root, 'Analysis_TableDependencies')

        for elem in dep_elements:
            try:
                dep = self._parse_table_dependency_element(elem)
                dependencies.append(dep)
            except (ValueError, KeyError) as e:
                self.logger.error(f"Failed to parse table dependency: {e}")
                continue

        self.logger.info(f"Parsed {len(dependencies)} table dependencies")
        return dependencies

    def _parse_table_dependency_element(self, elem: ET.Element) -> TableDependency:
        """Parse individual table dependency element."""
        object_id = self.get_int(elem, 'ObjectID')
        table_id = self.get_int(elem, 'TableID')
        active = self.get_bool(elem, 'Active', True)

        if not object_id or not table_id:
            raise ValueError("Missing required dependency fields")

        return TableDependency(
            object_id=object_id,
            table_id=table_id,
            active=active
        )

    def parse_object_dependencies(self, file_path: Path) -> List[ObjectDependency]:
        """Parse object dependency relationships."""
        tree = self.parse_file(file_path)
        root = tree.getroot()

        dependencies = []
        dep_elements = self.find_elements(root, 'Analysis_ObjectDependencies')

        for elem in dep_elements:
            try:
                dep = self._parse_object_dependency_element(elem)
                dependencies.append(dep)
            except (ValueError, KeyError) as e:
                self.logger.error(f"Failed to parse object dependency: {e}")
                continue

        self.logger.info(f"Parsed {len(dependencies)} object dependencies")
        return dependencies

    def _parse_object_dependency_element(self, elem: ET.Element) -> ObjectDependency:
        """Parse individual object dependency element."""
        source_id = self.get_int(elem, 'SourceObjectID')
        target_id = self.get_int(elem, 'TargetObjectID')
        active = self.get_bool(elem, 'Active', True)

        if not source_id or not target_id:
            raise ValueError("Missing required dependency fields")

        return ObjectDependency(
            source_object_id=source_id,
            target_object_id=target_id,
            active=active
        )
```

## Error Handling and Validation

### Custom Exceptions

```python
class XMLParseError(Exception):
    """Raised when XML parsing fails."""
    pass

class ValidationError(Exception):
    """Raised when parsed data fails validation."""
    pass
```

### Validation Strategies

1. **Schema Validation**: Validate against expected XML structure
2. **Data Type Validation**: Ensure correct data types for fields
3. **Reference Validation**: Check that referenced IDs exist
4. **Completeness Validation**: Ensure required fields are present

```python
def validate_analysis_data(self,
                          tables: Dict[int, Table],
                          objects: Dict[int, DatabaseObject],
                          table_deps: List[TableDependency],
                          object_deps: List[ObjectDependency]) -> None:
    """Validate complete analysis dataset."""

    # Check for orphaned dependencies
    for dep in table_deps:
        if dep.table_id not in tables:
            self.logger.warning(f"Table dependency references unknown table: {dep.table_id}")
        if dep.object_id not in objects:
            self.logger.warning(f"Table dependency references unknown object: {dep.object_id}")

    for dep in object_deps:
        if dep.source_object_id not in objects:
            self.logger.warning(f"Object dependency references unknown source: {dep.source_object_id}")
        if dep.target_object_id not in objects:
            self.logger.warning(f"Object dependency references unknown target: {dep.target_object_id}")

    # Validate object types
    valid_types = {'Form', 'Query', 'Macro', 'Report'}
    for obj in objects.values():
        if obj.object_type not in valid_types:
            raise ValidationError(f"Invalid object type: {obj.object_type}")
```

## Performance Optimizations

### Memory Management

1. **Streaming Parsing**: For very large files, consider iterative parsing
2. **Lazy Loading**: Parse only when needed
3. **Garbage Collection**: Clean up large data structures after processing

### Progress Tracking

```python
def parse_with_progress(self, file_path: Path, description: str) -> Any:
    """Parse file with progress indication."""
    with tqdm(desc=description, unit='elements') as pbar:
        # Implementation with progress updates
        pass
```

## Testing Strategy

### Test Fixtures

Create sample XML files with:
- Namespaced and non-namespaced variants
- Malformed XML for error testing
- Edge cases (empty files, missing fields)
- Large datasets for performance testing

### Unit Tests

```python
def test_namespace_handling():
    """Test parsing of namespaced XML."""
    # Test with namespace prefixes
    # Test fallback to non-namespaced

def test_error_recovery():
    """Test graceful handling of malformed XML."""
    # Test missing files
    # Test invalid XML structure
    # Test missing required fields

def test_performance():
    """Test parsing performance with large datasets."""
    # Benchmark parsing time
    # Memory usage monitoring
```

## Configuration Options

```python
@dataclass
class XMLConfig:
    """Configuration for XML parsing."""

    strict_namespaces: bool = True  # Require namespaces or allow fallback
    validate_schema: bool = True    # Validate against expected schema
    max_parse_time: int = 300       # Maximum parsing time in seconds
    memory_limit_mb: int = 512      # Memory limit for parsing
    log_parse_errors: bool = True   # Log individual parse errors
```

## Usage Examples

```python
# Initialize parsers
config = AnalysisConfig(...)
table_parser = TableParser(config)
object_parser = ObjectParser(config)
dep_parser = DependencyParser(config)

# Parse all files
tables = table_parser.parse(config.tables_file)
objects = object_parser.parse(config.objects_file)
table_deps = dep_parser.parse_table_dependencies(config.table_dependencies_file)
object_deps = dep_parser.parse_object_dependencies(config.object_dependencies_file)

# Validate data
validate_analysis_data(tables, objects, table_deps, object_deps)
```

## Troubleshooting Guide

### Common Issues

1. **Namespace Errors**: Access XML may have different namespace prefixes
   - Solution: Update `NAMESPACE_MAP` or disable strict namespace checking

2. **Encoding Issues**: Files may have different encodings
   - Solution: Try UTF-8, UTF-16, or Windows-1252 encodings

3. **Memory Issues**: Large files may exceed memory limits
   - Solution: Implement streaming parsing or increase memory limits

4. **Schema Variations**: Different Access versions may export different schemas
   - Solution: Add version detection and schema adaptation

### Debug Information

Enable verbose logging to see:
- Namespace resolution attempts
- Element parsing details
- Validation warnings
- Performance metrics