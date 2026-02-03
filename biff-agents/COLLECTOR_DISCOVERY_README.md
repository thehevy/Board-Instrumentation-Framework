# BIFF Collector Discovery System

Comprehensive collector discovery, search, and template generation system for the Board Instrumentation Framework (BIFF).

## Features

### 🔍 Collector Discovery
- Automatic discovery of all BIFF collectors
- Metadata extraction (functions, parameters, dependencies, examples)
- Category-based organization (11 categories)
- 30+ built-in collectors supported

### 🔎 Advanced Search
- **Full-text search** with relevance scoring
- **Advanced filters** (category, dependency, function name, minimum functions)
- **Function name search** (exact or partial matching)
- **Regex search** for complex patterns
- **Multi-criteria search** combining multiple filters

### 📝 XML Template Generation
- Generate ready-to-use collector XML snippets
- Complete namespace configurations
- Template validation and customization
- Parameter handling (required vs optional)
- Batch template generation

### ✅ Validation & Testing
- XML configuration validation
- Dependency checking
- Interactive collector testing
- Error detection and reporting

### 💻 CLI Commands
- List collectors by category
- Search collectors with multiple modes
- Generate XML templates
- Test collectors interactively
- Create namespace configurations

## Installation

```bash
cd biff-agents
pip install -e .
```

## Quick Start

### List All Collectors

```bash
# List all collectors
biff collector list

# List by category
biff collector list --category system
```

### Search for Collectors

```bash
# Full-text search
biff collector search "cpu usage monitoring"

# Filter by category
biff collector search --category system --min-functions 5

# Search by function name
biff collector search --function GetUsage

# Regex search
biff collector search --regex "^Docker.*" --search-in name
```

### View Collector Details

```bash
# Show detailed information
biff collector info CPU

# Shows:
# - Description
# - Category
# - Functions with parameters
# - Dependencies (✓ installed / ✗ missing)
# - Examples
```

### Test Collectors

```bash
# Test with default function
biff collector test RandomVal

# Test specific function with parameters
biff collector test RandomVal GetBoundedRandomValue 0 100

# Output shows:
# - Function being tested
# - Parameters used
# - Dependency check results
# - Execution output or errors
```

### Generate XML Templates

```bash
# Generate collector template
biff collector template RandomVal GetBoundedRandomValue

# Custom frequency and ID
biff collector template CPU GetCPU_Percentage \
  --id my.cpu.collector \
  --frequency 500

# Include all parameters with defaults
biff collector template CPU GetCPU_Percentage --all-params

# Validate template
biff collector template CPU GetCPU_Percentage --validate

# Save to file
biff collector template CPU GetCPU_Percentage -o cpu_config.xml
```

### Generate Namespace Configurations

```bash
# Create complete namespace with multiple collectors
biff collector namespace SystemMonitoring \
  --collectors CPU:GetCPU_Percentage Memory:GetMemory \
  --ip 192.168.1.100 \
  --port 5100 \
  --frequency 1000 \
  -o system_namespace.xml
```

## Usage Examples

### Workflow 1: Find and Configure a Collector

```bash
# 1. Search for CPU collectors
biff collector search "cpu monitoring"

# 2. Get detailed information
biff collector info Linux_CPU

# 3. Test it works
biff collector test Linux_CPU GetSystemAverageCPU

# 4. Generate template
biff collector template Linux_CPU GetSystemAverageCPU \
  --frequency 500 \
  -o linux_cpu.xml
```

### Workflow 2: Create Multi-Collector Namespace

```bash
# 1. Find system collectors with multiple functions
biff collector search --category system --min-functions 5

# 2. Create namespace with selected collectors
biff collector namespace ProductionMonitoring \
  --collectors \
    Linux_CPU:GetSystemAverageCPU \
    LinuxNetwork:GetBandwidth \
    SystemInfo_Linux:GetCPUInfo_Model_Linux \
  --ip 10.0.1.50 \
  --port 5100 \
  -o production_config.xml

# 3. Integrate into Minion configuration
cat production_config.xml >> MinionConfig.xml
```

### Workflow 3: Discover Docker Collectors

```bash
# 1. Find all Docker-related collectors
biff collector search --regex "^Docker" --search-in name

# 2. Check dependencies
biff collector info Docker_Stats

# 3. Install missing dependencies if needed
pip install docker

# 4. Test Docker collector
biff collector test Docker_Stats GetContainerCount

# 5. Generate template
biff collector template Docker_Stats GetContainerCount \
  --frequency 2000 \
  -o docker_monitoring.xml
```

## Python API

### CollectorDiscovery Class

```python
from pathlib import Path
from biff_agents_core.utils.collector_discovery import CollectorDiscovery

# Initialize with BIFF root directory
discovery = CollectorDiscovery(Path('/path/to/Board-Instrumentation-Framework'))

# List all collectors
collectors = discovery.list_collectors()
for collector in collectors:
    print(f"{collector.name}: {collector.description}")

# Search collectors
results = discovery.full_text_search('cpu monitoring', max_results=5)
for collector, score in results:
    print(f"{collector.name} (score: {score:.1f})")

# Filter collectors
system_collectors = discovery.search_collectors(
    by_category='system',
    min_functions=3,
    has_function='Get'
)

# Generate XML template
xml = discovery.generate_collector_xml(
    'CPU',
    'GetCPU_Percentage',
    frequency=500
)

# Validate XML
valid, errors = discovery.validate_collector_config(xml)
if not valid:
    for error in errors:
        print(f"Error: {error}")

# Customize template
custom_xml = discovery.customize_template(
    xml,
    new_id='cpu.production',
    new_frequency=1000,
    param_values={0: '10'}  # Set first parameter
)

# Generate namespace
config = discovery.generate_namespace_config(
    'MyNamespace',
    [('CPU', 'GetCPU_Percentage'), ('Memory', 'GetMemory')],
    target_ip='192.168.1.100',
    target_port=5100
)
```

## Search Modes

### 1. Full-Text Search
Searches across names, descriptions, functions, and parameters with weighted scoring.

```bash
biff collector search "cpu usage monitoring"
```

**Scoring weights:**
- Collector name: 5.0
- Function names: 3.0
- Description: 2.0
- Category: 1.5
- Function descriptions: 1.0
- Examples: 0.8
- Parameter descriptions: 0.5

### 2. Advanced Filters
Combine multiple criteria for precise results.

```bash
biff collector search \
  --category system \
  --dependency psutil \
  --function GetUsage \
  --min-functions 3
```

### 3. Function Name Search
Find collectors by function name.

```bash
# Partial match (default)
biff collector search --function Percentage

# Exact match
biff collector search --function GetCPU_Percentage --exact
```

### 4. Regex Search
Use patterns for complex searches.

```bash
# Find collectors starting with "Docker"
biff collector search --regex "^Docker" --search-in name

# Find functions matching pattern
biff collector search --regex "Get\\w+Usage" --search-in functions
```

## Collector Categories

- **system**: CPU, memory, storage, OS info
- **containers**: Docker, container stats
- **virtualization**: LibVirt, ESXi
- **monitoring**: Prometheus, InfluxDB, Collectd
- **testing**: RandomVal, Timer, test utilities
- **networking**: Network interfaces, bandwidth
- **data**: JSON, CSV file collectors
- **scripting**: PowerShell integration
- **demo**: Example collectors
- **meta**: Minion self-monitoring
- **other**: Miscellaneous collectors

## Template Structure

Generated templates follow BIFF Minion XML structure:

```xml
<Collector ID="CPU.GetCPU_Percentage" Frequency="1000">
  <Executable>Collectors\CPU.py</Executable>
  <Param>GetCPU_Percentage</Param>
  <!-- Add collector-specific parameters here -->
</Collector>
```

Namespace structure:

```xml
<Namespace>
  <Name>MyNamespace</Name>
  <DefaultFrequency>1000</DefaultFrequency>
  <TargetConnection IP="localhost" PORT="5100"/>
  
  <Collector ID="..." Frequency="...">
    ...
  </Collector>
</Namespace>
```

## Testing

### Run All Tests

```bash
cd biff-agents
python -m pytest tests/ -v
```

### Test Coverage

- **144 tests** total
- **85% coverage** on collector_discovery.py
- **15 integration tests** covering end-to-end workflows
- **Performance tests** ensure <2s discovery, <1s search

### Test Categories

- Unit tests (discovery, search, templates)
- Integration tests (workflows, CLI)
- Performance tests (scalability)
- Data integrity tests (consistency)
- Error handling tests (edge cases)

## Performance

- **Discovery**: <2 seconds for all collectors
- **Search**: <1 second for complex queries
- **Template Generation**: <0.2 seconds per template
- **Batch Operations**: 10+ templates in <2 seconds

## Development

### Project Structure

```
biff-agents/
├── biff_agents_core/
│   └── utils/
│       └── collector_discovery.py  # Core discovery system
├── biff_cli/
│   └── main.py                     # CLI commands
├── tests/
│   ├── test_collector_discovery.py
│   ├── test_collector_search.py
│   ├── test_collector_templates.py
│   └── test_integration.py
└── README.md
```

### Adding New Features

1. Add methods to `CollectorDiscovery` class
2. Add CLI commands in `biff_cli/main.py`
3. Add tests in `tests/`
4. Update documentation

## Troubleshooting

### Collector Not Found

```bash
# Check if collector exists
biff collector list | grep CollectorName

# Search for similar names
biff collector search CollectorName
```

### Missing Dependencies

```bash
# Check dependencies
biff collector info CollectorName

# Install suggested packages
pip install package_name
```

### Template Validation Errors

```bash
# Validate template
biff collector template CollectorName --validate

# Common issues:
# - Missing Frequency attribute
# - Missing Executable element
# - Invalid parameter values
```

## FAQ

**Q: How do I find collectors for a specific use case?**
A: Use full-text search: `biff collector search "your use case"`

**Q: Can I customize generated templates?**
A: Yes, use `--id`, `--frequency`, and `--all-params` flags, or use the Python API's `customize_template()` method.

**Q: How do I test a collector before deploying?**
A: Use `biff collector test CollectorName FunctionName params...`

**Q: Can I generate configs for multiple collectors at once?**
A: Yes, use `biff collector namespace` with `--collectors` flag.

**Q: What if a collector has missing dependencies?**
A: Run `biff collector info CollectorName` to see missing deps and install command.

## Contributing

This is part of the BIFF project. For contributing guidelines, see the main BIFF repository.

## License

See LICENSE file in Board-Instrumentation-Framework repository.

## Links

- [BIFF Main Repository](https://github.com/intel/Board-Instrumentation-Framework)
- [BIFF User Guide](../BIFF%20Instrumentation%20Framework%20User%20Guide.pdf)
- [Collector Documentation](../Minion/Collectors/)

---

**Version**: Phase 2 Week 4 Complete  
**Test Coverage**: 85% (144 passing tests)  
**Supported Collectors**: 30+  
**CLI Commands**: 11
