# Minion_Complex_Example Template Analysis

**Source**: Production Intel Vision Demo Configuration  
**Analysis Date**: February 5, 2026  
**Purpose**: Identify patterns for Collector Builder templates

---

## Overview

Analyzed **30+ collector files** and configuration patterns from real Intel production deployment. Identified **8 distinct collector patterns** that should become templates, including 3 production-proven patterns not yet in our builder.

---

## Current Templates (Implemented) ✅

### 1. **psutil System Metrics** ✅
- **Status**: Implemented
- **Use Cases**: CPU, memory, disk, network stats
- **Production Usage**: Not found in Vision demo (uses custom collectors instead)

### 2. **Shell Command Wrapper** ✅
- **Status**: Implemented
- **Production Example**: `EthtoolParser.py` - Wraps `ethtool` command
- **Pattern**: Subprocess → parse output → return value
- **Frequency**: Every 4 seconds (MyNetDevFreq)

### 3. **File Parser** ✅
- **Status**: Implemented
- **Production Examples**: 
  - `FileCollector.py` - Generic file reading with lock support
  - `DynamicCollector` with `<File>` tag - Zero-instrumentation pattern
- **Pattern**: Read file → parse → extract metrics
- **Vision Demo Usage**: 15 DynamicCollector instances reading test result files

### 4. **API Poller** ✅
- **Status**: Implemented
- **Production Example**: `Prometheus.py` - Prometheus API queries
- **Pattern**: HTTP request → parse JSON → extract time series
- **Complexity**: High - supports complex query syntax

### 5. **Python Plugin** ✅
- **Status**: Implemented
- **Production Examples**:
  - `Docker_Stats.py` - Monitors Docker containers
  - `LinuxNetwork.py` - Network device statistics via sysfs/ioctl
- **Pattern**: Entry point function → framework interface → dynamic collector registration

---

## New Templates Needed (From Production) 🆕

### 6. **DynamicCollector File Watcher** 🆕
**Priority**: P0 (used 15+ times in Vision demo)

**Pattern Discovered**:
```xml
<DynamicCollector Prefix="post.1." Frequency="1000">
    <File>testdata/test_results_1.txt</File>
    <Precision>0</Precision>
</DynamicCollector>
```

**Why It's Special**:
- **Zero instrumentation** - No Python code needed
- File format: `metric.name=value` (one per line)
- Prefix automatically applied to all metrics
- File watched continuously, metrics auto-discovered
- **15 instances** in Vision demo alone

**Template Implementation Needed**:
```python
def generate_dynamic_file_collector(metric_prefix: str, file_path: str, 
                                    frequency: int = 1000, precision: int = 0):
    """Generate DynamicCollector XML that watches a file"""
    return f'''<DynamicCollector Prefix="{metric_prefix}." Frequency="{frequency}">
    <File>{file_path}</File>
    <Precision>{precision}</Precision>
</DynamicCollector>'''
```

**Use Cases**:
- Test harness output files
- Application log metrics
- Third-party tool outputs
- CI/CD pipeline metrics

---

### 7. **Plugin with Framework Interface** 🆕
**Priority**: P1 (production-proven pattern)

**Pattern Discovered** (from `Docker_Stats.py`):
```python
def docker_stats_collector(frameworkInterface):
    """Entry point with framework interface"""
    Logger = frameworkInterface.Logger
    
    # Discover metrics dynamically
    for metric_id in discovered_metrics:
        if not frameworkInterface.DoesCollectorExist(metric_id):
            frameworkInterface.AddCollector(metric_id)
        frameworkInterface.SetCollectorValue(metric_id, value)
    
    return "HelenKeller"  # Special return: don't send anything
```

**Key Features**:
- **Dynamic metric discovery** - Metrics created at runtime
- **Framework integration** - Access to logger, collector management
- **Thread spawning** - `SpawnThread="True"` for long-running collectors
- **Special return value** - "HelenKeller" = suppress transmission

**Configuration Pattern**:
```xml
<Plugin>
    <PythonFile>Collectors/Docker_Stats.py</PythonFile>
    <EntryPoint SpawnThread="True">docker_stats_collector</EntryPoint>
</Plugin>
```

**Why Template It**:
- 40% of production collectors use this pattern
- Requires understanding framework interface API
- Benefits from code generation (boilerplate heavy)

---

### 8. **Network Statistics Collector** 🆕
**Priority**: P2 (domain-specific but highly valuable)

**Pattern**: `LinuxNetwork.py` (755 LOC!)

**Complexity**:
- Uses Linux `ioctl` system calls
- Reads from `/sys/class/net/` sysfs
- Extracts 100+ metrics per network interface
- Queue statistics (rx_queue_0, tx_queue_1, etc.)
- Driver-specific stats via ethtool

**Template Opportunity**:
- Simplified version for common network metrics
- Interface: device name, metric selection (basic/full)
- Auto-handles queue enumeration
- Includes normalization (bytes → Mbps)

**Production Config**:
```xml
<Plugin>
    <PythonFile>Collectors/LinuxNetwork.py</PythonFile>
    <EntryPoint SpawnThread="True">CollectDeviceStatistics</EntryPoint>
    <Param>device=ens1np0</Param>
    <Param>source=sysfs|Driver</Param>
</Plugin>
<Modifier ID="port.1.netdev.ens1np0.tx_queue(_*)" >
    <Normalize>0.00000782</Normalize>  <!-- Bytes/sec → Mbps -->
    <Precision>0</Precision>
</Modifier>
```

**Why Template It**:
- Network monitoring is extremely common
- Complex sysfs/ioctl code error-prone
- Automatic modifier generation (normalization)
- 5 instances in Vision demo (5 network ports)

---

## Advanced Patterns (Not Yet Templates)

### 9. **Aggregate Collectors with Repeat**
**Pattern**: Sum metrics across multiple sources

```xml
<Collector ID="post.Tb.TX.Test.Total">
    <Operator>Addition</Operator>
    <Repeat Count="5" StartValue="1">
        <Input DefaultValue="0">post.$(CurrentValueAlias).test_total_tx</Input>
    </Repeat>
    <Precision>0</Precision>
</Collector>
```

**Use Case**: Total throughput across N ports

**Template Needed**: `biff collector create-aggregate`

---

### 10. **ExternalFile Templates with Parameters**
**Pattern**: Reusable collector configs with parameterization

```xml
<ExternalFile PORT_NUM="1" Eth="ens1np0">netdev_stats.xml</ExternalFile>
<ExternalFile PORT_NUM="2" Eth="ens6np0">netdev_stats.xml</ExternalFile>
```

**Inside netdev_stats.xml**:
```xml
<DynamicCollector Prefix="port.$(PORT_NUM).">
    <Plugin>
        <Param>device=$(Eth)</Param>
    </Plugin>
</DynamicCollector>
```

**Use Case**: Deploy same collector pattern with different parameters

**Template Needed**: `biff collector create-template`

---

### 11. **Bulk Regex Modifiers**
**Pattern**: Apply normalization to pattern-matched metrics

```xml
<Modifier ID="port.1.netdev.ens1np0.tx_queue(_*)" >
    <Normalize>0.00000782</Normalize>
</Modifier>
<Modifier ID="port.1.netdev.ens1np0.rx_queue(_*)" >
    <Normalize>0.00000782</Normalize>
</Modifier>
```

**Why It's Powerful**:
- Matches all queue stats (tx_queue_0, tx_queue_1, ..., tx_queue_N)
- Single definition → N transformations
- Vision demo: 10 modifier patterns handle 200+ metrics

**Template Needed**: `biff collector add-modifier --bulk`

---

## Template Priority Matrix

| Template | Priority | Complexity | Vision Usage | User Impact |
|----------|----------|------------|--------------|-------------|
| **DynamicCollector File** | **P0** | Low | 15 instances | Very High |
| **Plugin Framework Interface** | **P1** | Medium | 40% of collectors | High |
| **Aggregate/Repeat** | **P1** | Low | 6 instances | Medium |
| **ExternalFile Template** | **P1** | Medium | 10 instances | High |
| **Bulk Regex Modifier** | **P1** | Low | Critical pattern | Very High |
| **Network Stats** | P2 | High | 5 instances | Medium |
| Shell Command (exists) | - | Low | ✅ Implemented | - |
| File Parser (exists) | - | Low | ✅ Implemented | - |
| API Poller (exists) | - | Medium | ✅ Implemented | - |

---

## Recommended Implementation Order

### Phase 2 Week 5 (Current) - Basic Collectors
- ✅ Shell Command Wrapper
- ✅ File Parser  
- ✅ psutil System Metrics
- ✅ API Poller
- ✅ Python Plugin

### Phase 2 Week 6 - Production Patterns
1. **DynamicCollector File Watcher** (Day 1)
   - XML generation only, no Python code
   - Wizard: file path, prefix, frequency
   - Output: `<DynamicCollector>` XML

2. **Plugin Framework Interface Template** (Days 2-3)
   - Generate entry point function with framework interface
   - Include dynamic collector registration boilerplate
   - Add logger integration
   - Example: Docker-style dynamic discovery

3. **Bulk Regex Modifier** (Day 4)
   - Interactive: pattern, normalization, precision
   - Generate `<Modifier ID="pattern">` XML
   - Show matched collector examples
   - Test against existing collectors

4. **Aggregate Collector with Repeat** (Day 5)
   - Wizard: operator (Addition/Average/Max/Min)
   - Input pattern, count, start value
   - Generate `<Collector>` with `<Repeat>` XML

### Phase 2 Week 7 - Advanced Templates
1. **ExternalFile Template** (Days 1-2)
   - Create template file with parameters
   - Generate instantiation in main config
   - Parameter substitution wizard

2. **Network Statistics** (Days 3-4)
   - Simplified template for common scenarios
   - Device selection, metric level (basic/full)
   - Auto-generate modifiers for normalization

3. **Testing & Documentation** (Day 5)

---

## Key Insights from Production Analysis

### 1. **Zero-Instrumentation Pattern is King**
- Vision demo uses **DynamicCollector** 15 times
- No Python code = faster development, fewer bugs
- File watching = perfect for test harnesses

### 2. **Dynamic Discovery is Critical**
- Docker collector discovers containers at runtime
- Network collector discovers queues dynamically
- Pattern: Unknown metric count at config time

### 3. **Template Reuse is Essential**
- `netdev_stats.xml` instantiated 5 times with parameters
- `test_results.xml` instantiated 5 times
- Pattern: Write once, deploy many

### 4. **Normalization is Everywhere**
- Bytes/sec → Mbps (network)
- Raw counts → rates (test results)
- Pattern: `<Modifier>` + `<Normalize>` ubiquitous

### 5. **Aggregation is Common**
- Total TX across 5 ports
- Total RX across 5 ports
- Pattern: N inputs → 1 output via operator

---

## Production Collector Catalog

**Total Collectors Analyzed**: 30 files

**Categorized by Pattern**:

| Pattern | Count | Files |
|---------|-------|-------|
| Plugin Framework | 12 | Docker_Stats, LinuxNetwork, Prometheus, JsonCollector, etc. |
| DynamicCollector File | 15 | (XML config, not files) |
| Shell/File Parser | 5 | EthtoolParser, FileCollector, etc. |
| Aggregate/Operator | 6 | (XML config, not files) |
| External Template | 10 | netdev_stats.xml, test_results.xml (5 instances each) |

---

## Next Steps

1. ✅ **Document findings** (this file)
2. 🔲 **Implement P0**: DynamicCollector File Watcher template
3. 🔲 **Implement P1**: Plugin Framework Interface template
4. 🔲 **Implement P1**: Bulk Regex Modifier
5. 🔲 **Update Implementation Plan** with production patterns
6. 🔲 **Create unit tests** using Vision demo as test fixtures

---

## Validation Strategy

**Test Against Production**:
1. Generate collectors using new templates
2. Compare output to Vision demo patterns
3. Validate XML structure matches production
4. Test with actual Minion runtime
5. Measure time savings vs manual creation

**Success Criteria**:
- Templates generate production-equivalent XML
- Wizard completes in < 2 minutes per collector
- Generated code matches production patterns
- 80% time savings vs manual creation

---

## References

- **Source Config**: `BIFF_FINDINGS/Minion_Complex_Example/Vision-SUT.xml`
- **Collector Files**: `BIFF_FINDINGS/Minion_Complex_Example/Collectors/*.py`
- **Template Configs**: `netdev_stats.xml`, `test_results.xml`
- **Production Docs**: Intel Vision Demo (69 XML files total)
