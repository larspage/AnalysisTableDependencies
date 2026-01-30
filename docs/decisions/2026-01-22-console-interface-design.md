# Console Interface Design

## Context

The Database Dependency Analyzer requires a command-line interface that allows users to:
- Specify input XML files (tables, objects, dependencies)
- Configure analysis options (memory limits, worker threads, etc.)
- Control output format (console vs HTML reports)
- Get progress feedback during analysis
- Handle errors gracefully

The interface needs to be intuitive for database administrators and developers while supporting advanced configuration options.

## Decision

Implement a modular console interface with the following components:

1. **ArgumentParser**: Uses Python's argparse for robust CLI parsing
2. **ConfigManager**: Handles configuration loading from args, env vars, and files
3. **OutputFormatter**: Formats analysis results for console display
4. **ProgressTracker**: Provides progress indication using tqdm
5. **Main CLI Entry Point**: Orchestrates the analysis workflow

### CLI Interface Design

```bash
db-analyzer [OPTIONS] TABLES_FILE OBJECTS_FILE TABLE_DEPS_FILE OBJECT_DEPS_FILE

Options:
  -o, --output FILE        Output HTML report file
  -v, --verbose           Enable verbose logging
  -q, --quiet            Suppress console output
  --max-workers INT       Maximum worker threads (default: 4)
  --memory-limit INT      Memory limit in MB (default: 512)
  --include-inactive      Include inactive dependencies
```

### Key Design Decisions

1. **Positional Arguments**: Required input files as positional args for clarity
2. **Standard Options**: Use common CLI patterns (-v, -q, -o)
3. **Progressive Enhancement**: Core functionality works without advanced options
4. **Error Handling**: Clear error messages without exposing internals
5. **Progress Feedback**: Visual progress bars for long operations

## Consequences

### Positive
- **User-Friendly**: Intuitive interface following CLI conventions
- **Extensible**: Easy to add new options and features
- **Robust**: Comprehensive error handling and validation
- **Modular**: Components can be reused or tested independently
- **Accessible**: Clear help text and error messages

### Negative
- **Dependency**: Adds tqdm dependency for progress bars
- **Complexity**: Multiple components increase initial complexity
- **Maintenance**: More code to maintain and test

### Risks
- **Performance**: Progress tracking adds minor overhead
- **Compatibility**: tqdm may not work in all terminal environments
- **User Expectations**: Advanced users may expect additional options

## Alternatives Considered

### Single Script Approach
- **Pros**: Simpler, fewer files
- **Cons**: Harder to test, less maintainable
- **Decision**: Rejected due to testability and modularity concerns

### Configuration File Only
- **Pros**: More options without CLI complexity
- **Cons**: Less convenient for one-off analyses
- **Decision**: Rejected, CLI still needed for basic usage

### Interactive Mode
- **Pros**: Guided user experience
- **Cons**: Complex implementation, not script-friendly
- **Decision**: Rejected, batch processing is primary use case

## Implementation Notes

- Uses argparse for robust argument parsing
- Supports environment variable configuration
- Progress bars automatically disable in non-interactive environments
- Error messages avoid exposing internal implementation details
- Modular design allows for future enhancements (GUI, web interface)

## Future Considerations

- Add support for configuration files (YAML/JSON)
- Implement subcommands for different analysis modes
- Add shell completion support
- Consider internationalization for error messages</content>
</xai:function_call">The file docs/decisions/2026-01-22-console-interface-design.md has been created successfully.