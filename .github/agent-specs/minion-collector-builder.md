# Minion Collector Builder Agent - Detailed Specification

## Executive Summary

The Minion Collector Builder Agent accelerates the most common BIFF development task: creating custom collectors that gather metrics from Linux systems (particularly Rocky Linux/RHEL in enterprise environments). It transforms the collector creation process from a 30-60 minute task requiring deep framework knowledge into a guided 5-minute workflow with built-in best practices.

**Target Time Savings**: 80% reduction in collector creation time
**Primary Value**: Production-ready collectors with proper error handling, dependencies, and testing

---

## User Personas

### Primary: System Administrator / DevOps Engineer

- **Background**: Manages Linux servers (Rocky/RHEL), familiar with shell commands
- **Goal**: Monitor custom application metrics or system-specific resources
- **Pain Points**:
  - Doesn't know Python well (more comfortable with bash)
  - Unsure how to structure collector functions
  - Doesn't understand Minion's stdout capture convention
  - Confused about frequency vs. scheduling
  - No idea how to handle missing dependencies gracefully
- **Success Metric**: Working collector gathering custom metric within 10 minutes

### Secondary: Python Developer

- **Background**: Software engineer building instrumented applications
- **Goal**: Expose application metrics to BIFF dashboard
- **Pain Points**:
  - Wants to use existing Python libraries (requests, psutil)
  - Needs guidance on parameter passing
  - Wants robust error handling
  - Unclear on testing methodology
- **Success Metric**: Reliable collector that handles errors without crashing Minion

### Tertiary: Enterprise Integration Specialist

- **Background**: Integrating BIFF with monitoring infrastructure
- **Goal**: Pull data from existing systems (Prometheus, InfluxDB, APIs)
- **Pain Points**:
  - Complex authentication mechanisms
  - Rate limiting and caching strategies
  - Handling transient failures
- **Success Metric**: Production-grade collector with retry logic and monitoring

---

## Collector Architecture Context

### How Collectors Work

```python
# Minion's Execution Model
1. Minion reads MinionConfig.xml
2. For each <Collector>:
   - Extract <Executable> path and <Param> values
   - Spawn subprocess or call Python function
   - Capture stdout
   - Transmit captured value as XML packet to Oscar

# Example Flow
<Collector ID="cpu.usage" Frequency="1000">
    <Executable>Collectors\CPU.py</Executable>
    <Param>GetCPU_Percentage</Param>
</Collector>

↓ Minion spawns: python Collectors\CPU.py GetCPU_Percentage
↓ Collector prints: "42.5"
↓ Minion captures stdout: "42.5"
↓ Minion sends XML: <Oscar><Namespace>NS</Namespace><ID>cpu.usage</ID><Value>42.5</Value></Oscar>
```

### Collector Types & Patterns

```yaml
collector_patterns:
  shell_wrapper:
    description: "Wraps Linux commands (df, free, netstat)"
    dependencies: None
    complexity: Low
    example: "Parse 'df -h' output for disk usage"
    
  file_parser:
    description: "Reads /proc, /sys, log files"
    dependencies: None (stdlib only)
    complexity: Medium
    example: "/proc/meminfo, /sys/class/net/eth0/statistics"
    
  psutil_based:
    description: "Uses psutil library for system metrics"
    dependencies: psutil (pip install)
    complexity: Low
    example: "CPU per core, memory details, process info"
    
  api_poller:
    description: "HTTP/REST API calls"
    dependencies: requests
    complexity: Medium
    example: "Prometheus exporter, application /metrics endpoint"
    
  custom_protocol:
    description: "Binary protocols, databases, message queues"
    dependencies: Varies
    complexity: High
    example: "Redis, SNMP, MQTT subscribers"
```

---

## Agent Capabilities

### 1. Interactive Collector Design Wizard

#### Metric Discovery

```python
class MetricDiscoveryWizard:
    def start(self):
        """Guide user through defining what to collect"""
        questions = [
            {
                "q": "What do you want to monitor?",
                "options": [
                    "System resource (CPU, memory, disk, network)",
                    "Application metric (custom app, service status)",
                    "External service (API, database, message queue)",
                    "File content (log file, config file, /proc /sys)",
                    "Command output (shell command, script result)"
                ],
                "handler": self.handle_metric_type_selection
            },
            {
                "q": "How often should it be collected?",
                "guidance": """
                - Real-time (< 1 second): High CPU cost, use sparingly
                - Frequent (1-5 seconds): Standard metrics
                - Normal (5-30 seconds): Most metrics
                - Periodic (30+ seconds): Slow-changing data
                """,
                "validator": lambda x: 100 <= int(x) <= 300000,
                "unit": "milliseconds"
            },
            {
                "q": "What should the metric ID be called?",
                "guidance": "Use dot notation: category.subcategory.metric",
                "examples": ["cpu.core0.usage", "app.requests.per_sec", "disk.sda.read_bytes"],
                "validator": self.validate_metric_id
            }
        ]
```

#### Data Source Template Selection

```
Agent: You selected "System resource". What specific resource?

1) CPU usage (overall or per-core)
2) Memory (usage, available, swap)
3) Disk (space, I/O operations, throughput)
4) Network (bandwidth, packets, errors)
5) Other (I'll describe it)

User: 3

Agent: Disk metrics. Which aspect?

1) Disk space (free/used/percentage)
2) Disk I/O operations (reads/writes per second)
3) Disk throughput (bytes read/written per second)
4) Disk latency (average request time)

User: 1

Agent: Perfect! Do you want to:

1) Monitor all disks
2) Monitor specific disk (e.g., /dev/sda1, /home)

User: 2

Agent: Which disk/mount point? (e.g., /, /home, /dev/sda1)

User: /

Agent: Great! I'll create a collector for root filesystem usage.

Would you prefer:
1) Use 'df' command (no dependencies, good for Rocky Linux)
2) Use psutil library (requires: pip install psutil, more detailed)

User: 1

Agent: Excellent choice for Rocky Linux. Creating collector...
```

---

### 1.5. Actor Creation Wizard

#### Remote Command Execution Pattern

```python
class ActorBuilder:
    """Create Actors for remote command execution from Marvin GUI"""
    
    def create_actor(self):
        print("\n🎭 Actor Creator")
        print("Actors execute commands remotely when triggered from Marvin\n")
        
        actor_id = input("Actor ID (e.g., RestartService): ")
        description = input("Description: ")
        
        # Execution type
        exec_type = self.prompt_choice(
            "Execution type:",
            ["Shell script", "Python script", "Single command"]
        )
        
        if exec_type == 0:  # Shell script
            script_path = input("Script path (e.g., scripts/restart.sh): ")
            executable = script_path
            
            # Generate script template
            script_template = f"""#!/bin/bash
# Actor: {actor_id}
# {description}

# Parameters: $1, $2, etc.

echo "Executing {actor_id}"

# TODO: Implement action here

exit 0
"""
            self.write_file(script_path, script_template)
            os.chmod(script_path, 0o755)
            
        elif exec_type == 1:  # Python script
            script_path = input("Python script (e.g., scripts/deploy.py): ")
            executable = f"python3 {script_path}"
        else:  # Single command
            command = input("Command (e.g., systemctl restart myservice): ")
            executable = command
        
        # Parameters
        params = []
        print("\nParameters (empty to finish):")
        while True:
            param = input("  Parameter: ")
            if not param:
                break
            params.append(param)
        
        # Generate Actor XML
        param_xml = "\n".join([f'    <Param>{p}</Param>' for p in params])
        actor_xml = f"""<Actor ID="{actor_id}">
    <Executable>{executable}</Executable>
{param_xml}
</Actor>"""
        
        # Generate Marvin task to trigger actor
        marvin_task_params = "\n".join([
            f'        <Param>VALUE_{i+1}</Param>'
            for i in range(len(params))
        ])
        
        marvin_task = f"""<TaskList ID="Execute_{actor_id}">
    <TaskItem Type="Minion">
        <Actor Namespace="YOUR_NAMESPACE" ID="{actor_id}" />
{marvin_task_params}
    </TaskItem>
</TaskList>

<!-- Button to trigger actor -->
<Widget File="Button.xml" Task="Execute_{actor_id}">
    <Title>{description}</Title>
</Widget>"""
        
        print(f"\n✓ Created actor: {actor_id}")
        print(f"\n📄 Minion config (add to Namespace):")
        print(actor_xml)
        print(f"\n📄 Marvin config (add to Application):")
        print(marvin_task)
        
        return {"actor_xml": actor_xml, "marvin_task": marvin_task}
```

#### Bulk Regex Modifier Creation

```python
class ModifierBuilder:
    """Create modifiers that apply to multiple metrics via regex patterns"""
    
    def create_bulk_modifier(self):
        print("\n🔧 Bulk Modifier Creator")
        print("Apply transformations to all metrics matching pattern\n")
        
        print("Wildcard patterns:")
        print("  • P(.*) matches P50, P90, P99, etc.")
        print("  • cpu_(.*) matches cpu_0, cpu_1, cpu_2, etc.")
        print("  • *_queue_* matches tx_queue_0, rx_queue_5, etc.\n")
        
        pattern = input("Metric ID pattern: ")
        
        # Show example matches
        examples = self.generate_example_matches(pattern)
        print(f"\nExample matches for '{pattern}':")
        for ex in examples[:5]:
            print(f"  • {ex}")
        
        # Transformation
        transform_type = self.prompt_choice(
            "\nTransformation:",
            ["Precision (decimal places)", "Normalize (multiply)", "Both"]
        )
        
        transform_xml = ""
        if transform_type in [0, 2]:
            precision = input("  Decimal places: ")
            transform_xml += f"    <Precision>{precision}</Precision>\n"
        
        if transform_type in [1, 2]:
            factor = input("  Normalization factor: ")
            transform_xml += f"    <Normalize>{factor}</Normalize>\n"
        
        modifier_xml = f"""<Modifier ID="{pattern}">
{transform_xml}</Modifier>"""
        
        print(f"\n✓ Created bulk modifier")
        print(f"   Applies to ~{len(examples)} matching metrics")
        print(modifier_xml)
        
        return modifier_xml
    
    def generate_example_matches(self, pattern):
        """Generate example metric names matching wildcard pattern"""
        if pattern.startswith("P(") and pattern.endswith(")"):
            return ["P50", "P90", "P95", "P99", "P999"]
        elif "cpu_" in pattern:
            return [f"cpu_{i}_usage" for i in range(8)]
        elif "_queue_" in pattern:
            return [f"tx_queue_{i}" for i in range(16)]
        elif pattern.endswith("(.*)"):
            base = pattern.replace("(.*)", "")
            return [f"{base}0", f"{base}1", f"{base}2", f"{base}total"]
        else:
            return [pattern.replace("*", "0"), pattern.replace("*", "1")]
```

---

### 2. Code Generation Engine

#### Template Library

**Shell Command Wrapper Template**

```python
##############################################################################
#  Copyright (c) 2026 Generated by BIFF Collector Builder Agent
# 
# Licensed under the Apache License, Version 2.0 (the "License");
##############################################################################
#    File Abstract: 
#       Collector for {{description}}
#       Generated: {{timestamp}}
#       Platform: Linux (Rocky/RHEL)
##############################################################################

import subprocess
import re

def {{function_name}}({{parameters}}):
    """
    {{description}}
    
    Args:
        {{parameter_docs}}
    
    Returns:
        String value suitable for BIFF transmission
        
    Example:
        {{example_usage}}
    """
    try:
        # Execute command
        result = subprocess.run(
            {{command_array}},
            capture_output=True,
            text=True,
            timeout=5,
            check=False
        )
        
        if result.returncode != 0:
            return "ERROR: Command failed - " + result.stderr.strip()
        
        # Parse output
        {{parsing_logic}}
        
        return str({{return_value}})
        
    except subprocess.TimeoutExpired:
        return "ERROR: Command timeout"
    except Exception as ex:
        return f"ERROR: {type(ex).__name__} - {str(ex)}"


# Test harness - run directly to test collector
if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print(f"Usage: python {sys.argv[0]} {{function_name}} [params]")
        sys.exit(1)
    
    func_name = sys.argv[1]
    params = sys.argv[2:]
    
    if func_name == "{{function_name}}":
        result = {{function_name}}(*params)
        print(result)
    else:
        print(f"ERROR: Unknown function: {func_name}")
```

**File Parser Template**

```python
##############################################################################
#  Collector for {{description}}
#  Reads: {{file_path}}
##############################################################################

import re

def {{function_name}}({{parameters}}):
    """
    Parses {{file_path}} for {{metric_description}}
    
    Returns:
        Extracted value as string
    """
    try:
        with open("{{file_path}}", "r") as f:
            content = f.read()
        
        # Pattern: {{pattern_description}}
        pattern = r"{{regex_pattern}}"
        match = re.search(pattern, content)
        
        if match:
            value = match.group({{group_index}})
            {{transformation_logic}}
            return str(value)
        else:
            return "ERROR: Pattern not found in file"
            
    except FileNotFoundError:
        return "ERROR: File not found - {{file_path}}"
    except PermissionError:
        return "ERROR: Permission denied - {{file_path}}"
    except Exception as ex:
        return f"ERROR: {type(ex).__name__} - {str(ex)}"
```

**psutil-Based Template**

```python
##############################################################################
#  Collector for {{description}}
#  Requires: pip install psutil
##############################################################################

try:
    import psutil
except ImportError:
    psutil = None

def _check_psutil():
    """Check if psutil is available"""
    if psutil is None:
        return False, "ERROR: psutil not installed (pip install psutil)"
    return True, None

def {{function_name}}({{parameters}}):
    """
    {{description}}
    Uses psutil library for accurate system metrics.
    
    Installation: pip install psutil
    """
    available, error = _check_psutil()
    if not available:
        return error
    
    try:
        {{psutil_logic}}
        return str({{return_value}})
        
    except Exception as ex:
        return f"ERROR: {type(ex).__name__} - {str(ex)}"
```

**API Poller Template**

```python
##############################################################################
#  Collector for {{description}}
#  Requires: pip install requests
##############################################################################

try:
    import requests
except ImportError:
    requests = None
    
import json

def _check_requests():
    """Check if requests library is available"""
    if requests is None:
        return False, "ERROR: requests not installed (pip install requests)"
    return True, None

def {{function_name}}(api_url{{additional_params}}):
    """
    Polls {{api_description}}
    
    Args:
        api_url: Full URL to API endpoint
        {{param_descriptions}}
    """
    available, error = _check_requests()
    if not available:
        return error
    
    try:
        response = requests.get(
            api_url,
            timeout={{timeout}},
            {{auth_section}}
        )
        response.raise_for_status()
        
        data = response.json()
        
        # Extract metric
        {{extraction_logic}}
        
        return str({{return_value}})
        
    except requests.Timeout:
        return "ERROR: API request timeout"
    except requests.RequestException as ex:
        return f"ERROR: API request failed - {str(ex)}"
    except (KeyError, ValueError) as ex:
        return f"ERROR: Failed to parse response - {str(ex)}"
    except Exception as ex:
        return f"ERROR: {type(ex).__name__} - {str(ex)}"
```

#### Concrete Examples

**Example 1: Root Filesystem Usage (df command)**

```python
# Generated by Collector Builder Agent
# Monitors: Root filesystem (/) disk usage percentage

import subprocess
import re

def GetRootDiskUsagePercent():
    """
    Gets disk usage percentage for root filesystem (/)
    
    Returns:
        Percentage used as string (e.g., "45")
    """
    try:
        result = subprocess.run(
            ["df", "-h", "/"],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if result.returncode != 0:
            return "ERROR: df command failed"
        
        # Parse output - looking for usage percentage
        # Example output:
        # Filesystem      Size  Used Avail Use% Mounted on
        # /dev/sda1       50G   20G   28G  42% /
        lines = result.stdout.strip().split('\n')
        if len(lines) < 2:
            return "ERROR: Unexpected df output"
        
        data_line = lines[1]
        pattern = r'(\d+)%'
        match = re.search(pattern, data_line)
        
        if match:
            percentage = match.group(1)
            return percentage
        else:
            return "ERROR: Could not parse percentage"
            
    except subprocess.TimeoutExpired:
        return "ERROR: df command timeout"
    except Exception as ex:
        return f"ERROR: {str(ex)}"


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "GetRootDiskUsagePercent":
        print(GetRootDiskUsagePercent())
```

**Example 2: Network Interface Bytes Read (/sys parsing)**

```python
# Generated by Collector Builder Agent
# Monitors: Network bytes received on specified interface

def GetNetworkRxBytes(interface="eth0"):
    """
    Gets total bytes received on network interface
    
    Args:
        interface: Network interface name (default: eth0)
        
    Returns:
        Total bytes received as string
    """
    file_path = f"/sys/class/net/{interface}/statistics/rx_bytes"
    
    try:
        with open(file_path, "r") as f:
            value = f.read().strip()
        
        # Validate it's a number
        int(value)  # Will raise ValueError if not
        return value
        
    except FileNotFoundError:
        return f"ERROR: Interface {interface} not found"
    except PermissionError:
        return f"ERROR: Permission denied reading {file_path}"
    except ValueError:
        return f"ERROR: Invalid value in {file_path}"
    except Exception as ex:
        return f"ERROR: {str(ex)}"


if __name__ == "__main__":
    import sys
    interface = sys.argv[2] if len(sys.argv) > 2 else "eth0"
    if len(sys.argv) > 1 and sys.argv[1] == "GetNetworkRxBytes":
        print(GetNetworkRxBytes(interface))
```

---

### 3. Configuration Generator

#### Minion Config XML Generator

```python
class MinionConfigGenerator:
    def generate_collector_xml(self, collector_spec):
        """Generate XML snippet for MinionConfig.xml"""
        
        # Build parameter list
        param_xml = ""
        for param in collector_spec.parameters:
            param_xml += f"            <Param>{param['value']}</Param>\n"
        
        xml = f"""
        <Collector ID="{collector_spec.metric_id}" Frequency="{collector_spec.frequency}">
            <Executable>Collectors\\{collector_spec.filename}</Executable>
            <Param>{collector_spec.function_name}</Param>
{param_xml.rstrip()}
        </Collector>
"""
        return xml.strip()
    
    def insert_into_config(self, config_path, namespace_name, collector_xml):
        """Insert collector into existing config file"""
        # Parse XML
        # Find namespace
        # Add collector before </Namespace>
        # Write back
        pass
```

#### Example Generated Config Snippet

```xml
<!-- Generated by Collector Builder Agent -->
<!-- Metric: Root filesystem usage percentage -->
<!-- Created: 2026-01-28 14:30:00 -->

<Collector ID="disk.root.usage_percent" Frequency="5000">
    <Executable>Collectors\DiskUsage.py</Executable>
    <Param>GetRootDiskUsagePercent</Param>
</Collector>

<!-- To test this collector manually:
     cd Minion
     python Collectors\DiskUsage.py GetRootDiskUsagePercent
     Expected output: Numeric percentage (e.g., "45")
-->
```

---

### 4. Dependency Management

#### Dependency Detection

```python
class DependencyAnalyzer:
    KNOWN_DEPENDENCIES = {
        "psutil": {
            "install": "pip install psutil",
            "check": "import psutil; psutil.cpu_percent(0.1)",
            "purpose": "System and process metrics",
            "fallback": "Use /proc and /sys files instead"
        },
        "requests": {
            "install": "pip install requests",
            "check": "import requests",
            "purpose": "HTTP API calls",
            "fallback": "Use urllib.request (stdlib, more complex)"
        },
        "docker": {
            "install": "pip install docker",
            "check": "import docker; docker.from_env()",
            "purpose": "Docker container metrics",
            "fallback": "Parse 'docker stats' command output"
        }
    }
    
    def check_dependency(self, dep_name):
        """Check if dependency is available"""
        if dep_name not in self.KNOWN_DEPENDENCIES:
            return {"available": False, "error": "Unknown dependency"}
        
        dep_info = self.KNOWN_DEPENDENCIES[dep_name]
        
        try:
            # Try to import and run check
            exec(dep_info["check"])
            return {"available": True}
        except Exception as ex:
            return {
                "available": False,
                "error": str(ex),
                "install_command": dep_info["install"],
                "fallback": dep_info["fallback"]
            }
```

#### Rocky Linux Specific Guidance

```yaml
rocky_linux_guidance:
  package_manager: "dnf or yum"
  
  python_installation:
    - "dnf install python3"
    - "dnf install python3-pip"
    
  common_issues:
    psutil_compile_error:
      cause: "Missing gcc or python3-devel"
      solution: "dnf install gcc python3-devel"
      
    permission_denied_proc:
      cause: "SELinux enforcement"
      solution: "Run as root or adjust SELinux context"
      
    pip_not_found:
      cause: "pip not in PATH"
      solution: "Use python3 -m pip install <package>"
```

---

### 5. Testing & Validation Framework

#### Built-in Test Harness

```python
# Every generated collector includes this test section

if __name__ == "__main__":
    """
    Test harness - run collector directly to verify functionality
    
    Usage:
        python Collectors/MyCollector.py FunctionName [param1] [param2]
    
    Examples:
        python Collectors/DiskUsage.py GetRootDiskUsagePercent
        python Collectors/Network.py GetInterfaceRxBytes eth0
    """
    import sys
    
    if len(sys.argv) < 2:
        print("Available functions:")
        {{list_available_functions}}
        sys.exit(1)
    
    func_name = sys.argv[1]
    params = sys.argv[2:]
    
    # Call requested function
    if func_name == "{{function_name}}":
        result = {{function_name}}(*params)
        print(result)
        
        # Validation
        if result.startswith("ERROR"):
            sys.exit(1)
    else:
        print(f"ERROR: Unknown function: {func_name}")
        sys.exit(1)
```

#### Integration Test Generator

```python
class CollectorTestGenerator:
    def generate_test_config(self, collector_spec):
        """Create minimal MinionConfig.xml for testing collector"""
        
        config = f"""<?xml version="1.0"?>
<!-- Test Configuration for {collector_spec.metric_id} -->
<Minion>
    <Namespace>
        <Name>TestNamespace</Name>
        <DefaultFrequency>1000</DefaultFrequency>
        <TargetConnection IP="localhost" PORT="9999"/>
        
        <!-- Collector under test -->
        {collector_spec.xml}
    </Namespace>
</Minion>
"""
        return config
    
    def create_test_script(self, collector_spec):
        """Generate bash script to test collector in isolation"""
        
        script = f"""#!/bin/bash
# Test script for {collector_spec.metric_id}
echo "Testing {collector_spec.filename}..."

# Test 1: Direct execution
echo -n "Direct execution test: "
OUTPUT=$(python Collectors/{collector_spec.filename} {collector_spec.function_name} {" ".join(collector_spec.default_params)})
if [[ $? -eq 0 ]] && [[ ! $OUTPUT =~ ^ERROR ]]; then
    echo "✓ PASS"
    echo "  Output: $OUTPUT"
else
    echo "✗ FAIL"
    echo "  Output: $OUTPUT"
    exit 1
fi

# Test 2: Run with Minion (5 seconds)
echo -n "Minion integration test: "
timeout 5 python Minion.py -c test_configs/{collector_spec.metric_id}.xml &
MINION_PID=$!
sleep 6
kill $MINION_PID 2>/dev/null
echo "✓ PASS (check Minion output above)"

echo "All tests passed!"
"""
        return script
```

---

### 6. Error Handling Best Practices

#### Error Return Conventions

```python
# BIFF collectors should ALWAYS return a string
# Error strings should be prefixed with "ERROR:"

# ✓ GOOD - Clear error with context
return "ERROR: Permission denied - /proc/cpuinfo"

# ✓ GOOD - Graceful degradation
return "0"  # Return zero instead of error for missing optional data

# ✗ BAD - Exception propagates to Minion
raise Exception("Something went wrong")  # Don't do this!

# ✗ BAD - Empty return
return None  # Should return string "ERROR: ..." instead
```

#### Timeout Handling

```python
# For subprocess commands
result = subprocess.run(
    command,
    timeout=5,  # Always set timeout
    capture_output=True,
    text=True
)

# For API calls
response = requests.get(url, timeout=10)

# For file operations on NFS/slow disks
import signal

def timeout_handler(signum, frame):
    raise TimeoutError("File read timeout")

signal.signal(signal.SIGALRM, timeout_handler)
signal.alarm(5)  # 5 second timeout
try:
    with open(slow_file) as f:
        data = f.read()
finally:
    signal.alarm(0)  # Disable alarm
```

---

### 7. Documentation Generator

#### Collector Documentation Template

```markdown
# {{collector_name}}

**Purpose**: {{description}}

**Platform**: {{platform}} ({{tested_on}})

**Dependencies**: {{dependencies or "None (stdlib only)"}}

## Installation

{{installation_instructions}}

## Functions

### {{function_name}}({{parameters}})

{{function_description}}

**Parameters**:
{{parameter_list}}

**Returns**: {{return_description}}

**Example Output**: `{{example_output}}`

**Example Configuration**:
```xml
{{example_xml_config}}
```

**Testing**:

```bash
# Direct test
python Collectors/{{filename}} {{function_name}} {{example_params}}

# Expected output: {{expected_output}}
```

## Error Handling

This collector returns `ERROR: ...` prefix for all error conditions:

- `ERROR: Permission denied` - Insufficient privileges
- `ERROR: File not found` - Missing system file
- `ERROR: Command failed` - Subprocess error
- `ERROR: Timeout` - Operation took too long

## Troubleshooting

{{troubleshooting_section}}

## See Also

{{related_collectors}}

```

---

## Interactive Workflow Example

```

Agent: I'll help you create a custom collector. What would you like to monitor?

User: I want to monitor how many users are logged into the server

Agent: Great! That's a straightforward metric. I can think of a few approaches:

1) Parse 'who' command output (count lines)
2) Parse 'w' command output (count users)
3) Read /var/run/utmp file directly

For Rocky Linux, I recommend option 1 (simplest, no dependencies).

Shall I proceed with 'who' command?

User: yes

Agent: Perfect. A few questions:

1. What should the metric ID be?
   Suggestion: "system.users.logged_in"

User: that's good

Agent: 2. How often should it update? (in milliseconds)

- 5000 = every 5 seconds
- 30000 = every 30 seconds

User: 10000

Agent: 3. Which namespace in your MinionConfig.xml?
   Found existing namespaces: ["SystemMetrics", "AppMonitoring"]
   Or create new namespace?

User: SystemMetrics

Agent: Excellent! Creating collector...

✓ Generated: Minion/Collectors/UserCount.py

- Function: GetLoggedInUserCount()
- Error handling: ✓
- Test harness: ✓
  
✓ Generated XML configuration snippet

✓ Added to MinionConfig.xml in namespace "SystemMetrics"

Testing collector...
  Running: python Collectors/UserCount.py GetLoggedInUserCount
  Output: "3"
  ✓ Test passed!

Your collector is ready!

To test with Minion:
  cd Minion
  python Minion.py -c MinionConfig.xml -v

The collector will send "system.users.logged_in = 3" every 10 seconds.

Would you like to:

1) Create a Marvin widget to display this metric
2) Create another collector
3) View the generated code

```

---

## Platform-Specific Considerations

### Rocky Linux / RHEL

#### Common System Paths
```python
ROCKY_SYSTEM_PATHS = {
    "cpu_info": "/proc/cpuinfo",
    "memory_info": "/proc/meminfo",
    "network_stats": "/sys/class/net/{interface}/statistics/",
    "disk_stats": "/proc/diskstats",
    "uptime": "/proc/uptime",
    "load_average": "/proc/loadavg",
}

ROCKY_COMMANDS = {
    "disk_usage": "df -h",
    "memory_usage": "free -m",
    "cpu_usage": "top -bn1 | grep 'Cpu(s)'",
    "network_connections": "ss -s",
    "process_count": "ps aux | wc -l",
}
```

### SELinux Considerations

```python
def check_selinux_context():
    """Guide user if SELinux blocks collector"""
    
    try:
        result = subprocess.run(
            ["getenforce"],
            capture_output=True,
            text=True
        )
        
        if "Enforcing" in result.stdout:
            return """
SELinux is in Enforcing mode. If you get permission errors:

1. Run Minion with proper context:
   sudo semanage fcontext -a -t bin_t "/path/to/Minion/Minion.py"
   sudo restorecon -v /path/to/Minion/Minion.py

2. Or allow necessary permissions:
   sudo audit2allow -a -M minion_collector
   sudo semodule -i minion_collector.pp

3. Or run as root (not recommended for production)
"""
    except:
        return "Could not check SELinux status"
```

---

## Advanced Features

### 1. Collector Optimization

#### Caching Strategy Generator

```python
# For expensive operations, agent can add caching

class CachedCollector:
    """Template for collectors that cache results"""
    
    _cache = {}
    _cache_timeout = 60  # seconds
    
    def get_expensive_metric(self):
        """
        Expensive operation (API call, slow command)
        Cache result for 60 seconds
        """
        current_time = time.time()
        cache_key = "expensive_metric"
        
        # Check cache
        if cache_key in self._cache:
            cached_time, cached_value = self._cache[cache_key]
            if current_time - cached_time < self._cache_timeout:
                return cached_value
        
        # Perform expensive operation
        result = self._do_expensive_operation()
        
        # Update cache
        self._cache[cache_key] = (current_time, result)
        
        return result
```

#### Batch Collection

```python
# For multiple related metrics from same source

def GetAllNetworkStats(interface="eth0"):
    """
    Collects multiple network metrics in one operation
    Returns comma-separated: rx_bytes,tx_bytes,rx_packets,tx_packets
    """
    base_path = f"/sys/class/net/{interface}/statistics/"
    metrics = ["rx_bytes", "tx_bytes", "rx_packets", "tx_packets"]
    
    values = []
    for metric in metrics:
        try:
            with open(base_path + metric) as f:
                values.append(f.read().strip())
        except:
            values.append("0")
    
    return ",".join(values)

# Configuration uses this with multiple collectors sharing same source
# Minion will call once, but distribute to multiple IDs
```

### 2. Dynamic Collector Generation

#### Auto-Discovery Collectors

```python
# Agent can generate collectors that discover resources

def GeneratePerCoreCollector(num_cores):
    """
    Generates collector with one function per CPU core
    """
    functions = []
    for core_num in range(num_cores):
        functions.append(f"""
def GetCore{core_num}Usage():
    '''Get CPU usage for core {core_num}'''
    if not Is_PSUTIL_Installed():
        return "ERROR: psutil required"
    
    stats = psutil.cpu_percent(0.25, percpu=True)
    if len(stats) > {core_num}:
        return str(stats[{core_num}])
    return "0"
""")
    
    return "\n".join(functions)
```

---

## Success Metrics

### Quantitative

- **Time to Working Collector**: < 5 minutes (vs. 30-60 minutes manual)
- **Error Rate**: < 5% (generated collectors work on first try)
- **Code Quality**: 100% include error handling and test harness
- **Documentation Coverage**: 100% auto-generated docs

### Qualitative

- **User Confidence**: Non-Python users can create collectors
- **Best Practices**: All collectors follow BIFF conventions
- **Maintainability**: Generated code is readable and well-commented
- **Platform Awareness**: Rocky Linux specific guidance included

### Validation Tests

```python
class CollectorBuilderValidator:
    def test_generated_collector(self, collector_file):
        """Validate generated collector meets standards"""
        
        with open(collector_file) as f:
            code = f.read()
        
        checks = [
            ("Has docstring", '"""' in code),
            ("Has error handling", "try:" in code and "except" in code),
            ("Returns string", "return str(" in code or 'return "' in code),
            ("Has test harness", 'if __name__ == "__main__"' in code),
            ("No uncaught exceptions", "raise " not in code or "except" in code),
            ("Has timeout for subprocess", "timeout=" in code if "subprocess" in code else True),
        ]
        
        for check_name, result in checks:
            assert result, f"Failed check: {check_name}"
```

---

## Implementation Phases

### Phase 1: Core Templates (Week 1)

- Shell command wrapper template
- File parser template
- Basic code generation
- XML config generation
- Test harness inclusion

**Deliverable**: Can generate simple collectors (df, /proc files, commands)

### Phase 2: Enhanced Features (Week 2)

- psutil template
- API poller template
- Dependency detection
- Rocky Linux specific guidance
- Interactive wizard

**Deliverable**: Handles all common collector types with proper dependency management

### Phase 3: Advanced Capabilities (Week 3)

- Caching strategy generation
- Batch collection patterns
- Auto-discovery collectors
- SELinux guidance
- Performance optimization

**Deliverable**: Production-grade collectors with enterprise features

---

## Integration Points

### With Quick Start Orchestrator

- Quick Start creates basic collectors
- Collector Builder extends with custom metrics

### With Debugging Agent

- Collector Builder generates with debug logging hooks
- Debugging Agent can test collectors in isolation

### With GUI Composer

- After collector creation, offer to create matching widget
- Pass metric ID to GUI Composer for visualization

---

## Example Success Story

> **Before Collector Builder Agent**:
> DevOps engineer spends 45 minutes reading CPU.py example, copying code, figuring out how parameters work, debugging why Minion doesn't see their collector, fixing path issues, adding error handling after crash, and finally getting it working.

> **With Collector Builder Agent**:
>
> ```
> User: "I need to monitor disk usage on /"
> Agent: [asks 3 questions, generates code in 30 seconds]
> User: [tests collector, works immediately]
> Total time: 3 minutes
> ```

**Result**: 90% time savings, production-ready code, proper error handling included, developer confidence increased.
