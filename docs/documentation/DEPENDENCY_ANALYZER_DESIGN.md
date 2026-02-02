# DependencyAnalyzer Class Design

## Overview

The `DependencyAnalyzer` class is a critical component of the Database Dependency Analyzer system. It is responsible for analyzing dependencies between database objects and tables to identify unused tables. This class will be implemented in the `src/database_dependency_analyzer/analyzers/dependency_analyzer.py` file.

## Core Responsibilities

1. **Dependency Graph Construction**: Build a graph of relationships between objects and tables
2. **Usage Analysis**: Determine which tables are used based on object references
3. **Transitive Dependency Handling**: Handle indirect dependencies through object chains
4. **Statistics Calculation**: Compute comprehensive statistics about the analysis
5. **Result Generation**: Produce a complete analysis result with all findings

## Class Structure

```python
class DependencyAnalyzer:
    def __init__(self, config: AnalysisConfig):
        """Initialize the dependency analyzer.
        
        Args:
            config: Analysis configuration.
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
    
    def analyze(self, tables: Dict[int, Table], 
                objects: Dict[int, DatabaseObject], 
                table_dependencies: List[TableDependency], 
                object_dependencies: List[ObjectDependency]) -> AnalysisResult:
        """Perform dependency analysis and return results.
        
        Args:
            tables: Dictionary of tables by ID
            objects: Dictionary of database objects by ID
            table_dependencies: List of table dependency relationships
            object_dependencies: List of object dependency relationships
            
        Returns:
            AnalysisResult containing the complete analysis findings
        """
        # Implementation will follow the algorithm below
```

## Algorithm Design

### Step 1: Build Dependency Graph
- Create a mapping of object-to-table relationships
- Create a mapping of object-to-object relationships
- Filter out inactive dependencies based on the 'active' flag

### Step 2: Mark Direct Usage
- For each active table dependency, mark the referenced table as used
- Track which objects are referencing each table

### Step 3: Handle Transitive Dependencies
- For object dependencies, identify chains of dependencies
- If object A depends on object B, and object B depends on a table, then object A indirectly depends on that table
- Propagate usage status through these chains

### Step 4: Calculate Statistics
- Count total tables, used tables, unused tables
- Count total objects and categorize by type
- Count total dependencies and active dependencies
- Calculate usage percentages

### Step 5: Generate Results
- Create AnalysisResult object with all findings
- Include processing time and timestamp
- Return comprehensive results

## Key Methods

### `analyze()` Method
The main entry point that orchestrates the entire analysis process.

### `_build_dependency_graph()` Method
Constructs the internal dependency graph from the input data.

### `_mark_used_tables()` Method
Identifies and marks tables that are directly or indirectly used.

### `_calculate_statistics()` Method
Computes all statistical metrics for the analysis.

### `_handle_transitive_dependencies()` Method
Processes object-to-object dependencies to identify indirect table usage.

## Performance Considerations

1. **Efficient Data Structures**: Use dictionaries and sets for O(1) lookups
2. **Lazy Evaluation**: Only process transitive dependencies when necessary
3. **Memory Management**: Avoid creating unnecessary intermediate data structures
4. **Parallel Processing**: Consider parallel processing for large datasets

## Error Handling

1. **Input Validation**: Validate all input parameters
2. **Graceful Degradation**: Handle missing or invalid data gracefully
3. **Logging**: Provide detailed logging for debugging and monitoring
4. **Exception Handling**: Catch and handle exceptions appropriately

## Integration Points

### Inputs
- `tables`: Dictionary of Table objects from the table parser
- `objects`: Dictionary of DatabaseObject objects from the object parser
- `table_dependencies`: List of TableDependency objects from the dependency parser
- `object_dependencies`: List of ObjectDependency objects from the dependency parser

### Outputs
- `AnalysisResult`: Complete analysis results for report generation

## Testing Strategy

1. **Unit Tests**: Test individual methods with mock data
2. **Integration Tests**: Test the complete analysis workflow
3. **Performance Tests**: Ensure acceptable performance with large datasets
4. **Edge Case Tests**: Test with empty inputs, circular dependencies, etc.

## Implementation Plan

1. Create the `DependencyAnalyzer` class in `src/database_dependency_analyzer/analyzers/dependency_analyzer.py`
2. Implement the core algorithm methods
3. Add comprehensive logging
4. Create unit tests in `tests/test_analyzer.py`
5. Integrate with the main analysis workflow

## Success Criteria

- ✅ Correctly identifies all unused tables
- ✅ Handles transitive dependencies through object chains
- ✅ Respects dependency active flags
- ✅ Performance acceptable for large datasets (< 5 seconds)
- ✅ Comprehensive statistics calculation
- ✅ Full test coverage (>90%)
- ✅ Clear documentation and logging