# Phase 2 Week 4: Collector Discovery & Management

**Agent**: Collector Builder  
**Timeline**: Week 4 (Days 1-5)  
**Status**: 🚧 IN PROGRESS

---

## Overview

Week 4 focuses on **collector discovery and listing** - enabling users to explore the 30+ built-in collectors and understand what each one does before adding them to configurations.

### Goals

1. **Discover collectors** - Scan `Minion/Collectors/` directory
2. **Parse metadata** - Extract parameters, descriptions, and examples from Python files
3. **List/search collectors** - CLI commands to browse available collectors
4. **Show collector details** - Display usage, parameters, and examples

### Why This Matters

Currently, users must:
- Browse filesystem manually to find collectors
- Open Python files to read docstrings
- Guess at parameter formats
- Trial-and-error to test collectors

**After Week 4**, users can:
- Run `biff collector list` to see all available collectors
- Run `biff collector info CPU` to see detailed usage
- Search collectors by category: `biff collector search docker`
- Test collectors before adding: `biff collector test CPU GetUsage`

---

## Daily Breakdown

### Day 1: Collector Discovery (4 hours)

**Goal**: Scan filesystem and parse collector metadata

**Tasks**:
1. Create `CollectorDiscovery` class
   - Scan `Minion/Collectors/` directory for `.py` files
   - Filter out `__init__.py` and test files
   - Return list of collector names

2. Create `CollectorMetadataParser`
   - Parse module docstrings
   - Extract function signatures
   - Parse parameter types and defaults
   - Extract usage examples from docstrings

3. Add CLI command `biff collector list`
   - Show table: Name, Description, Parameters
   - Support filtering by keyword
   - Colorized output

**Deliverables**:
- `biff_agents_core/utils/collector_discovery.py` (~200 LOC)
- `tests/test_collector_discovery.py` (~100 LOC)
- CLI integration in `biff_cli/main.py`

**Tests**:
- Test scanning Minion/Collectors directory
- Test parsing collector docstrings
- Test filtering by keyword
- Test handling missing collectors

### Day 2: Collector Details (3 hours)

**Goal**: Show comprehensive collector information

**Tasks**:
1. Create `CollectorInfoFormatter`
   - Format collector details for terminal display
   - Show: Name, description, parameters, return type, examples
   - Syntax highlighting for code examples

2. Add CLI command `biff collector info <name>`
   - Display full collector documentation
   - Show example usage in XML
   - Show example test command

3. Add collector categories/tags
   - System: CPU, Memory, Storage, Network
   - Containers: Docker, Kubernetes
   - Monitoring: Prometheus, Collectd, InfluxDB
   - Custom: User-defined collectors

**Deliverables**:
- Enhanced `CollectorDiscovery` with categorization
- `biff collector info` command
- Formatted output with examples

**Tests**:
- Test info display for various collectors
- Test handling unknown collectors
- Test category filtering

### Day 3: Collector Search (2 hours)

**Goal**: Enable keyword search across collectors

**Tasks**:
1. Implement search functionality
   - Search by name, description, category
   - Fuzzy matching for typos
   - Relevance scoring

2. Add CLI command `biff collector search <query>`
   - Show ranked results
   - Highlight matching terms
   - Show snippet of description

3. Add collector recommendations
   - Suggest collectors based on deployment type
   - "Frequently used together" suggestions

**Deliverables**:
- Search implementation in `CollectorDiscovery`
- `biff collector search` command
- Recommendation engine

**Tests**:
- Test search with various queries
- Test fuzzy matching
- Test relevance scoring

### Day 4: Collector Testing (4 hours)

**Goal**: Test collectors before adding to config

**Tasks**:
1. Create `CollectorTester` class
   - Execute collector script
   - Capture stdout/stderr
   - Validate output format
   - Detect errors

2. Add CLI command `biff collector test <name> [params...]`
   - Run collector with given parameters
   - Show output and execution time
   - Validate return value
   - Show warnings for issues

3. Add validation rules
   - Check if output is numeric/string/JSON
   - Warn if execution takes > 5 seconds
   - Error if script crashes
   - Suggest parameter fixes

**Deliverables**:
- `biff_agents_core/utils/collector_tester.py` (~150 LOC)
- `biff collector test` command
- Validation and error reporting

**Tests**:
- Test running valid collectors
- Test handling collector errors
- Test parameter validation
- Test timeout handling

### Day 5: Integration & Documentation (3 hours)

**Goal**: Integrate with quickstart, write docs

**Tasks**:
1. Enhance quickstart wizard
   - Show collector descriptions in wizard
   - Allow browsing collectors interactively
   - Show recommended collectors by deployment type

2. Create collector builder documentation
   - Add COLLECTOR_BUILDER.md guide
   - Update QUICKSTART.md with collector management
   - Add examples for custom collectors

3. Testing and polish
   - End-to-end test of all collector commands
   - Fix any bugs found
   - Improve error messages

**Deliverables**:
- Updated quickstart wizard
- `COLLECTOR_BUILDER.md` documentation
- Bug fixes and polish

**Tests**:
- Integration tests for full workflow
- CLI output validation

---

## Technical Design

### CollectorDiscovery Class

```python
class CollectorDiscovery:
    """Discover and parse collectors in BIFF installation"""
    
    def __init__(self, biff_root: Path):
        self.collectors_dir = biff_root / "Minion" / "Collectors"
        self._cache = {}
    
    def list_collectors(self) -> List[CollectorInfo]:
        """Scan and return all collectors"""
        
    def get_collector(self, name: str) -> CollectorInfo:
        """Get details for specific collector"""
        
    def search(self, query: str) -> List[CollectorInfo]:
        """Search collectors by keyword"""
        
    def get_by_category(self, category: str) -> List[CollectorInfo]:
        """Filter collectors by category"""
```

### CollectorInfo Dataclass

```python
@dataclass
class CollectorInfo:
    name: str                      # "CPU"
    file_path: Path                # "/path/to/CPU.py"
    description: str               # "System CPU metrics"
    functions: List[FunctionInfo]  # Available functions
    category: str                  # "system"
    examples: List[str]            # Usage examples
    dependencies: List[str]        # Required packages
```

### CLI Commands

```bash
# List all collectors
biff collector list
biff collector list --category system
biff collector list --format json

# Search collectors
biff collector search docker
biff collector search "cpu usage"

# Show collector details
biff collector info CPU
biff collector info RandomVal --examples

# Test collector
biff collector test CPU GetUsage
biff collector test RandomVal 0 100
```

---

## Success Metrics

**Quantitative**:
- [ ] 30+ collectors discovered automatically
- [ ] 100% of collectors have parsed metadata
- [ ] < 100ms to list all collectors
- [ ] < 50ms to get single collector info
- [ ] 90% test coverage on discovery code

**Qualitative**:
- [ ] Users can find collectors without filesystem browsing
- [ ] Collector descriptions are clear and helpful
- [ ] Search returns relevant results
- [ ] Test command catches common errors

---

## Dependencies

- **BIFF Installation**: Requires `Minion/Collectors/` directory
- **Python AST**: For parsing Python files
- **Rich/Colorama**: For terminal formatting (optional)

---

## Risks & Mitigations

**Risk**: Collector files have inconsistent docstrings  
**Mitigation**: Create documentation standards, parse best-effort

**Risk**: Some collectors require dependencies (psutil, docker)  
**Mitigation**: Mark dependencies clearly, catch import errors gracefully

**Risk**: Collectors may hang or crash  
**Mitigation**: Add timeout to test command, catch exceptions

---

## Related Work

- Phase 1: Quick Start Orchestrator (generates configs, but doesn't help explore collectors)
- User Guide: Documents collectors, but requires reading 200 pages
- Demonstration configs: Show examples, but not discoverable

**Week 4 bridges the gap** between "I have BIFF" and "I know what collectors exist and how to use them."

---

## Next Week Preview

**Week 5**: Collector integration
- Add collectors to existing configs
- Remove collectors from configs
- Update collector parameters
- Generate collector skeleton code

---

## Let's Start Day 1! 🚀

Creating `CollectorDiscovery` class to scan and parse collectors...
