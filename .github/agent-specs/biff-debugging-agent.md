# BIFF Debugging Agent - Detailed Specification

## Executive Summary

The BIFF Debugging Agent dramatically reduces support burden by diagnosing the #1 source of user issues: **silent failures in UDP communication**. In a 3-tier system where components communicate over UDP without connection acknowledgment, pinpointing why data isn't flowing is complex and time-consuming. This agent transforms hours of manual troubleshooting into minutes of automated diagnosis.

**Primary Value**: Turns "Why isn't my dashboard showing data?" from a 1-2 hour investigation into a 5-minute automated diagnosis with actionable solutions.

**Support Burden Reduction**: 70-80% decrease in common troubleshooting requests

---

## Problem Space Analysis

### Why BIFF Debugging is Hard

#### Silent UDP Failures

```
Problem: UDP is connectionless
Result: No error messages when packets are dropped

Minion sends data →  [FIREWALL BLOCKS]  → Oscar never receives
                     ↑ NO ERROR MESSAGE

User sees: Empty widgets in Marvin
Reality: Oscar never got the data
Symptom: Complete silence
```

#### Multi-Component Complexity

```
Data Flow: Minion → Oscar → Marvin
Failure Points: 7 places where things can silently fail

1. Minion: Collector crashes/errors
2. Minion: Wrong target IP/port in config
3. Network: Firewall blocks UDP port
4. Oscar: Not running or crashed
5. Oscar: Wrong listen port configured
6. Oscar: Not forwarding to Marvin IP/port
7. Marvin: Wrong listen port or not running

Each failure looks identical to the user: No data in widgets
```

#### Configuration Consistency Nightmare

```xml
<!-- Three files must have matching values -->

<!-- MinionConfig.xml -->
<TargetConnection IP="192.168.1.100" PORT="1100"/>

<!-- OscarConfig.xml -->
<IncomingMinionConnection PORT="1100"/>  <!-- Must match! -->
<TargetConnection IP="localhost" PORT="52001"/>

<!-- MarvinApp.xml -->
<OscarConnection IP="192.168.1.100" Port="52001"/>  <!-- Must match! -->

<!-- Widget definition -->
<MinionSrc Namespace="MyNamespace" ID="my.metric"/>  <!-- Must match collector! -->
```

---

## User Personas

### Primary: First-Time BIFF User (75% of support requests)

- **Symptom**: "Widgets show no data"
- **Actual Causes**:
  - Wrong namespace:ID in widget
  - Firewall blocking UDP
  - Components not running
  - Port mismatch in configs
- **Current Resolution Time**: 1-2 hours of forum posts
- **With Agent**: 5 minutes automated diagnosis

### Secondary: System Administrator (20% of support requests)

- **Symptom**: "It worked yesterday, now it doesn't"
- **Actual Causes**:
  - Firewall rule changed
  - Oscar crashed and didn't restart
  - Network configuration changed
  - Collector dependency missing after system update
- **Current Resolution Time**: 30-60 minutes investigation
- **With Agent**: 5-10 minutes pinpoint cause

### Tertiary: Enterprise Deployment (5% of support requests)

- **Symptom**: "Intermittent data loss"
- **Actual Causes**:
  - Network congestion dropping UDP packets
  - Oscar overwhelmed (too many Minions)
  - Port conflict with other services
- **Current Resolution Time**: Hours of packet capture analysis
- **With Agent**: 20 minutes performance diagnosis

---

## Agent Capabilities

### 0. Configuration Validation Extensions

#### Environment Variable Validation

```python
class EnvironmentValidator:
    """Validate environment-based configurations"""
    
    def validate_env_config(self, config_path):
        print("\n🌍 Environment Variable Configuration Check\n")
        
        # Parse config for environment variable references
        env_vars_used = self.extract_env_var_references(config_path)
        
        if not env_vars_used:
            print("✓ No environment variables used in configuration")
            return True
        
        print(f"Found {len(env_vars_used)} environment variable references:\n")
        
        issues = []
        for var_name in env_vars_used:
            var_value = os.environ.get(var_name)
            
            if var_value is None:
                issues.append(f"❌ {var_name}: NOT SET")
                print(f"  ❌ {var_name}: Not set in environment")
            else:
                print(f"  ✓ {var_name}: {var_value}")
        
        if issues:
            print("\n⚠️ Missing environment variables detected\n")
            print("To fix, export these variables before running:")
            for issue in issues:
                var_name = issue.split(":")[0].replace("❌ ", "")
                print(f"  export {var_name}=VALUE")
            print("\nOr use launch script that sets them automatically.")
            return False
        else:
            print("\n✓ All environment variables are set")
            return True
    
    def extract_env_var_references(self, config_path):
        """Extract all $(VAR_NAME) references from XML config"""
        import re
        with open(config_path, 'r') as f:
            content = f.read()
        
        # Find all $(VAR_NAME) patterns
        pattern = r'\$\(([A-Z_][A-Z0-9_]*)\)'
        matches = re.findall(pattern, content)
        return list(set(matches))  # Remove duplicates
```

#### Actor Execution Validation

```python
class ActorValidator:
    """Validate Actor configurations and test remote execution"""
    
    def validate_actors(self, config_path):
        print("\n🎭 Actor Configuration Validation\n")
        
        actors = self.parse_actors(config_path)
        
        if not actors:
            print("No actors defined in configuration")
            return True
        
        print(f"Found {len(actors)} actor(s):\n")
        
        all_valid = True
        for actor in actors:
            print(f"Actor: {actor['id']}")
            print(f"  Executable: {actor['executable']}")
            
            # Check if executable exists and is executable
            if actor['executable'].endswith('.sh') or actor['executable'].endswith('.py'):
                if os.path.exists(actor['executable']):
                    if os.access(actor['executable'], os.X_OK):
                        print(f"  ✓ Script exists and is executable")
                    else:
                        print(f"  ⚠️ Script exists but is not executable")
                        print(f"     Fix: chmod +x {actor['executable']}")
                        all_valid = False
                else:
                    print(f"  ❌ Script not found: {actor['executable']}")
                    all_valid = False
            else:
                # Check if command exists
                import shutil
                cmd = actor['executable'].split()[0]
                if shutil.which(cmd):
                    print(f"  ✓ Command found: {cmd}")
                else:
                    print(f"  ❌ Command not found in PATH: {cmd}")
                    all_valid = False
            
            print()
        
        return all_valid
```

#### Regex Modifier Validation

```python
class ModifierValidator:
    """Validate regex-based modifier patterns"""
    
    def validate_regex_modifiers(self, config_path):
        print("\n🔧 Regex Modifier Validation\n")
        
        modifiers = self.parse_modifiers(config_path)
        regex_modifiers = [m for m in modifiers if self.is_regex_pattern(m['id'])]
        
        if not regex_modifiers:
            print("No regex modifiers detected")
            return True
        
        print(f"Found {len(regex_modifiers)} regex modifier(s):\n")
        
        for mod in regex_modifiers:
            print(f"Pattern: {mod['id']}")
            
            # Generate example matches
            examples = self.generate_example_matches(mod['id'])
            print(f"  Example matches:")
            for ex in examples[:3]:
                print(f"    • {ex}")
            
            # Show transformations
            if 'precision' in mod:
                print(f"  Transformation: Precision = {mod['precision']}")
            if 'normalize' in mod:
                print(f"  Transformation: Normalize × {mod['normalize']}")
            print()
        
        return True
    
    def is_regex_pattern(self, pattern):
        """Check if pattern contains regex wildcards"""
        return '(*)' in pattern or '(.*)' in pattern or '*' in pattern
```

---

### 1. Component Health Checker

#### Process Verification

```python
class ComponentHealthChecker:
    def check_all_components(self, workspace_root):
        """Verify all BIFF components are running"""
        
        results = {
            "minion": self.check_minion(),
            "oscar": self.check_oscar(),
            "marvin": self.check_marvin(),
        }
        
        return HealthReport(results)
    
    def check_minion(self):
        """Check if Minion process is running"""
        # Platform-specific process check
        if platform.system() == "Windows":
            cmd = 'tasklist | findstr "python.*Minion.py"'
        else:
            cmd = 'ps aux | grep "[M]inion.py"'
        
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        
        if result.stdout.strip():
            return {
                "status": "✓ Running",
                "pid": self.extract_pid(result.stdout),
                "details": result.stdout.strip()
            }
        else:
            return {
                "status": "✗ Not Running",
                "suggestion": "Start Minion: cd Minion && python Minion.py -c MinionConfig.xml",
                "impact": "HIGH - No data will be collected"
            }
    
    def check_oscar(self):
        """Check if Oscar process is running"""
        # Similar to check_minion
        pass
    
    def check_marvin(self):
        """Check if Marvin GUI is running"""
        # Check for Java process running BIFF.Marvin.jar
        pass
```

#### Configuration File Validation

```python
class ConfigValidator:
    def validate_all_configs(self, workspace_root):
        """Validate XML syntax and structure of all configs"""
        
        configs = [
            ("Minion", "Minion/MinionConfig.xml"),
            ("Oscar", "Oscar/OscarConfig.xml"),
            ("Marvin", "Marvin/Application.xml"),
        ]
        
        results = {}
        for component, config_path in configs:
            full_path = os.path.join(workspace_root, config_path)
            results[component] = self.validate_xml(full_path)
        
        return results
    
    def validate_xml(self, file_path):
        """Check if XML is well-formed"""
        try:
            tree = ET.parse(file_path)
            return {
                "status": "✓ Valid XML",
                "file": file_path
            }
        except ET.ParseError as e:
            return {
                "status": "✗ XML Parse Error",
                "error": str(e),
                "line": e.position[0],
                "suggestion": f"Fix XML syntax error at line {e.position[0]}",
                "impact": "CRITICAL - Component cannot start"
            }
        except FileNotFoundError:
            return {
                "status": "✗ File Not Found",
                "file": file_path,
                "suggestion": "Create configuration file or check path",
                "impact": "CRITICAL - Component cannot start"
            }
```

---

### 2. Network Connectivity Analyzer

#### Port Availability Check

```python
class PortChecker:
    def check_udp_ports(self, config_analysis):
        """Verify required UDP ports are available and listening"""
        
        required_ports = {
            "oscar_incoming": config_analysis.oscar_minion_port,
            "marvin_listening": config_analysis.marvin_port,
        }
        
        results = {}
        for name, port in required_ports.items():
            results[name] = self.check_port_listening(port, "UDP")
        
        return results
    
    def check_port_listening(self, port, protocol="UDP"):
        """Check if port is listening"""
        
        if platform.system() == "Windows":
            cmd = f'netstat -ano | findstr ":{port}" | findstr "{protocol}"'
        else:
            cmd = f'netstat -ulnp | grep ":{port}"'
        
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        
        if result.stdout.strip():
            return {
                "status": "✓ Port Listening",
                "port": port,
                "details": result.stdout.strip()
            }
        else:
            return {
                "status": "✗ Port Not Listening",
                "port": port,
                "suggestion": f"Ensure Oscar/Marvin is running and configured for port {port}",
                "impact": "HIGH - Data cannot be received"
            }
    
    def check_port_conflicts(self, port):
        """Check if port is in use by another process"""
        # Check if port is bound but not by BIFF component
        pass
```

#### Firewall Detection

```python
class FirewallChecker:
    def check_windows_firewall(self, ports):
        """Check Windows Firewall rules for UDP ports"""
        
        results = {}
        for port in ports:
            cmd = f'netsh advfirewall firewall show rule name=all | findstr /C:"LocalPort" | findstr /C:"{port}"'
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            
            if result.stdout.strip():
                results[port] = {
                    "status": "✓ Firewall Rule Exists",
                    "port": port
                }
            else:
                results[port] = {
                    "status": "⚠ No Firewall Rule Found",
                    "port": port,
                    "suggestion": f"Add firewall rule:\nnetsh advfirewall firewall add rule name=\"BIFF Port {port}\" dir=in action=allow protocol=UDP localport={port}",
                    "impact": "HIGH - Remote data may be blocked"
                }
        
        return results
    
    def check_linux_firewall(self, ports):
        """Check iptables/firewalld rules"""
        
        # Check if firewalld is running
        firewalld_active = subprocess.run(
            ["systemctl", "is-active", "firewalld"],
            capture_output=True,
            text=True
        ).returncode == 0
        
        if firewalld_active:
            return self.check_firewalld_rules(ports)
        else:
            return self.check_iptables_rules(ports)
```

#### UDP Connectivity Test

```python
class UDPConnectivityTester:
    def test_minion_to_oscar(self, minion_config, oscar_config):
        """Send test packet from Minion location to Oscar"""
        
        # Create test XML packet
        test_packet = """<?xml version="1.0" encoding="utf-8"?>
<Oscar>
    <Version>1.0</Version>
    <Namespace>DebugTest</Namespace>
    <ID>connectivity.test</ID>
    <Value>42</Value>
    <Time>1234567890</Time>
</Oscar>"""
        
        # Send from Minion's expected location
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        
        try:
            target_ip = minion_config["target_ip"]
            target_port = minion_config["target_port"]
            
            sock.sendto(
                test_packet.encode('utf-8'),
                (target_ip, target_port)
            )
            
            return {
                "status": "✓ Packet Sent",
                "target": f"{target_ip}:{target_port}",
                "note": "Check Oscar logs/GUI to confirm receipt"
            }
            
        except socket.error as e:
            return {
                "status": "✗ Send Failed",
                "error": str(e),
                "suggestion": self.diagnose_socket_error(e),
                "impact": "CRITICAL - Cannot communicate with Oscar"
            }
        finally:
            sock.close()
    
    def diagnose_socket_error(self, error):
        """Translate socket error to actionable advice"""
        error_str = str(error).lower()
        
        if "permission denied" in error_str:
            return "Permission denied - may need admin/root privileges for raw sockets"
        elif "network is unreachable" in error_str:
            return "Network unreachable - check IP address and network connectivity"
        elif "connection refused" in error_str:
            return "Connection refused - target port may be blocked or service not running"
        else:
            return f"Socket error: {error}"
```

---

### 3. Configuration Consistency Validator

#### Cross-Component Config Analysis

```python
class ConfigConsistencyChecker:
    def analyze_data_flow(self, workspace_root):
        """Parse all configs and verify data flow path is consistent"""
        
        # Parse Minion config
        minion_config = self.parse_minion_config(workspace_root)
        
        # Parse Oscar config
        oscar_config = self.parse_oscar_config(workspace_root)
        
        # Parse Marvin config
        marvin_config = self.parse_marvin_config(workspace_root)
        
        # Check consistency
        issues = []
        
        # Check 1: Minion target = Oscar listen
        if minion_config["target_port"] != oscar_config["listen_port"]:
            issues.append({
                "type": "PORT_MISMATCH",
                "severity": "CRITICAL",
                "description": f"Minion sends to port {minion_config['target_port']}, but Oscar listens on {oscar_config['listen_port']}",
                "fix": f"Change one to match: MinionConfig.xml <TargetConnection PORT=\"{oscar_config['listen_port']}\"/> OR OscarConfig.xml <IncomingMinionConnection PORT=\"{minion_config['target_port']}\"/>"
            })
        
        # Check 2: Oscar target = Marvin listen
        if oscar_config["target_port"] != marvin_config["listen_port"]:
            issues.append({
                "type": "PORT_MISMATCH",
                "severity": "CRITICAL",
                "description": f"Oscar sends to port {oscar_config['target_port']}, but Marvin listens on {marvin_config['listen_port']}",
                "fix": f"Change one to match: OscarConfig.xml <TargetConnection PORT=\"{marvin_config['listen_port']}\"/> OR MarvinApp.xml <OscarConnection Port=\"{oscar_config['target_port']}\"/>"
            })
        
        # Check 3: IP addresses make sense
        if minion_config["target_ip"] == "localhost" and oscar_config["machine"] != "local":
            issues.append({
                "type": "IP_WARNING",
                "severity": "WARNING",
                "description": "Minion configured for localhost but Oscar may be on different machine",
                "fix": "Verify Minion and Oscar are on same machine, or update IP address"
            })
        
        return ConsistencyReport(issues)
```

#### Namespace & ID Mapping

```python
class NamespaceIDValidator:
    def validate_namespace_id_mapping(self, workspace_root):
        """Ensure widget MinionSrc matches actual collectors"""
        
        # Extract all collector namespace:ID pairs from Minion configs
        collectors = self.extract_collector_ids(workspace_root)
        
        # Extract all MinionSrc namespace:ID pairs from Marvin widgets
        widget_sources = self.extract_widget_sources(workspace_root)
        
        # Find mismatches
        issues = []
        for widget_src in widget_sources:
            ns = widget_src["namespace"]
            id = widget_src["id"]
            key = f"{ns}:{id}"
            
            if key not in collectors:
                issues.append({
                    "type": "WIDGET_NO_COLLECTOR",
                    "severity": "HIGH",
                    "widget": widget_src["widget_type"],
                    "file": widget_src["file"],
                    "namespace": ns,
                    "id": id,
                    "description": f"Widget expects data from {ns}:{id} but no collector produces this",
                    "fix": f"Add collector with ID=\"{id}\" in namespace \"{ns}\" to MinionConfig.xml",
                    "similar_collectors": self.find_similar_collector_ids(collectors, id)
                })
        
        return NamespaceIDReport(issues)
    
    def find_similar_collector_ids(self, collectors, target_id):
        """Find collectors with similar IDs (likely typos)"""
        # Use fuzzy string matching to find close matches
        import difflib
        
        all_ids = [c.split(':')[1] for c in collectors]
        similar = difflib.get_close_matches(target_id, all_ids, n=3, cutoff=0.6)
        
        return similar
```

---

### 4. Log Analysis Engine

#### Minion Log Parser

```python
class MinionLogAnalyzer:
    ERROR_PATTERNS = {
        "collector_error": {
            "pattern": r"ERROR.*Collector.*\[(.*?)\]",
            "severity": "HIGH",
            "diagnosis": lambda m: f"Collector '{m.group(1)}' is failing",
            "action": "Check collector script for errors, test manually"
        },
        "permission_denied": {
            "pattern": r"Permission denied.*\[(.*?)\]",
            "severity": "HIGH",
            "diagnosis": lambda m: f"Permission denied accessing {m.group(1)}",
            "action": "Run as root or adjust file permissions"
        },
        "network_error": {
            "pattern": r"Network is unreachable|Connection refused",
            "severity": "CRITICAL",
            "diagnosis": lambda m: "Cannot reach Oscar",
            "action": "Check Oscar IP address, verify Oscar is running, check firewall"
        },
        "dependency_missing": {
            "pattern": r"ModuleNotFoundError|ImportError.*'(.*?)'",
            "severity": "CRITICAL",
            "diagnosis": lambda m: f"Missing Python module: {m.group(1)}",
            "action": lambda m: f"Install missing dependency: pip install {m.group(1)}"
        }
    }
    
    def analyze_log(self, log_path):
        """Parse Minion log and extract issues"""
        
        try:
            with open(log_path, 'r') as f:
                log_content = f.readlines()
        except FileNotFoundError:
            return {"error": "Minion log not found - Minion may not have run yet"}
        
        issues = []
        for line_num, line in enumerate(log_content, 1):
            for pattern_name, pattern_info in self.ERROR_PATTERNS.items():
                match = re.search(pattern_info["pattern"], line)
                if match:
                    diagnosis = pattern_info["diagnosis"](match) if callable(pattern_info["diagnosis"]) else pattern_info["diagnosis"]
                    action = pattern_info["action"](match) if callable(pattern_info["action"]) else pattern_info["action"]
                    
                    issues.append({
                        "line": line_num,
                        "type": pattern_name,
                        "severity": pattern_info["severity"],
                        "log_entry": line.strip(),
                        "diagnosis": diagnosis,
                        "action": action
                    })
        
        return LogAnalysisReport(issues)
```

#### Oscar Log Parser

```python
class OscarLogAnalyzer:
    def analyze_log(self, log_path):
        """Parse Oscar log for routing and data flow issues"""
        
        patterns = {
            "received_from_minion": r"Received.*from.*:([\d]+)",
            "forwarded_to_marvin": r"Forwarded.*to.*:([\d]+)",
            "connection_error": r"Connection.*error|refused|timeout",
            "queue_overflow": r"Queue.*full|overflow|dropped",
        }
        
        stats = {
            "packets_received": 0,
            "packets_forwarded": 0,
            "errors": []
        }
        
        # Count packet flow
        with open(log_path, 'r') as f:
            for line in f:
                if re.search(patterns["received_from_minion"], line):
                    stats["packets_received"] += 1
                if re.search(patterns["forwarded_to_marvin"], line):
                    stats["packets_forwarded"] += 1
                if re.search(patterns["connection_error"], line):
                    stats["errors"].append(line.strip())
        
        # Diagnose issues
        if stats["packets_received"] == 0:
            return {
                "issue": "Oscar receiving no data from Minion",
                "diagnosis": "Minion not sending, wrong port, or firewall blocking",
                "action": "Check Minion is running and sending to correct port"
            }
        elif stats["packets_forwarded"] == 0:
            return {
                "issue": "Oscar receiving data but not forwarding to Marvin",
                "diagnosis": "Marvin not reachable or wrong target configuration",
                "action": "Check Marvin IP/port in OscarConfig.xml"
            }
        elif stats["packets_forwarded"] < stats["packets_received"] * 0.5:
            return {
                "issue": "Significant packet loss",
                "diagnosis": "Network issues or Marvin cannot keep up",
                "action": "Check network connectivity, reduce data rate, check Marvin performance"
            }
        else:
            return {
                "status": "✓ Oscar forwarding data normally",
                "stats": stats
            }
```

---

### 5. Collector Testing Framework

#### Direct Collector Test

```python
class CollectorTester:
    def test_collector(self, collector_spec):
        """Test collector directly without Minion"""
        
        collector_path = collector_spec["path"]
        function_name = collector_spec["function"]
        params = collector_spec["params"]
        
        cmd = ["python", collector_path, function_name] + params
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=10,
                cwd=collector_spec["working_dir"]
            )
            
            if result.returncode == 0:
                output = result.stdout.strip()
                
                # Check if output is an error
                if output.startswith("ERROR"):
                    return {
                        "status": "✗ Collector Returned Error",
                        "output": output,
                        "diagnosis": "Collector script encountered an error",
                        "action": "Fix the error in the collector script"
                    }
                else:
                    return {
                        "status": "✓ Collector Working",
                        "output": output,
                        "note": "Collector can be called directly and returns data"
                    }
            else:
                return {
                    "status": "✗ Collector Failed",
                    "returncode": result.returncode,
                    "stderr": result.stderr,
                    "diagnosis": "Collector script crashed or exited with error",
                    "action": "Check collector script for syntax errors or exceptions"
                }
                
        except subprocess.TimeoutExpired:
            return {
                "status": "✗ Collector Timeout",
                "diagnosis": "Collector took too long to execute (>10 seconds)",
                "action": "Optimize collector or increase timeout, check for infinite loops"
            }
        except FileNotFoundError:
            return {
                "status": "✗ Collector Not Found",
                "path": collector_path,
                "diagnosis": "Collector script file does not exist",
                "action": "Check path in MinionConfig.xml <Executable> tag"
            }
```

---

### 6. Interactive Diagnosis Workflow

#### Guided Troubleshooting Session

```
Agent: I'll help diagnose your BIFF issue. What's happening?

1) Widgets show no data
2) Some widgets work, others don't
3) Data was working, now stopped
4) Intermittent data / data drops
5) Other issue

User: 1

Agent: No data in widgets. Let me check the system...

[Running diagnostics...]

Component Status:
  ✗ Minion: Not running
  ✓ Oscar: Running (PID 12345)
  ✓ Marvin: Running (PID 67890)

🔴 CRITICAL ISSUE FOUND:
Minion is not running. No data can be collected.

Would you like me to:
1) Start Minion now
2) Check why Minion isn't running
3) Show how to start Minion manually

User: 2

Agent: Checking Minion startup issues...

Found Minion log with recent errors:
  Line 145: ERROR: ModuleNotFoundError: No module named 'psutil'
  
🔴 ROOT CAUSE:
Minion failed to start because 'psutil' library is missing.

This collector requires psutil:
  - Collector ID: cpu.usage
  - File: Collectors/CPU.py

Solution:
  1) Install psutil: pip install psutil
  2) OR remove/comment out the CPU collector in MinionConfig.xml
  3) OR use alternative collector that doesn't need psutil

Which would you like to do?

User: 1

Agent: Running: pip install psutil

[Installation output...]

✓ psutil installed successfully

Starting Minion...

✓ Minion started (PID 23456)

Testing data flow...
  ✓ Minion collecting data
  ✓ Minion sending to Oscar (port 1100)
  ✓ Oscar receiving packets
  ✓ Oscar forwarding to Marvin (port 52001)
  
⏳ Waiting for Marvin to receive data... (checking every 2 seconds)

✓ SUCCESS! Marvin is receiving data.

Your widgets should now display live data. 

Issue resolved! The problem was:
  - Missing psutil dependency
  - Minion failed to start silently
  
Prevention:
  - Check logs after starting components
  - Test collectors independently before adding to config
```

---

### 7. Performance Diagnostics

#### Data Rate Analysis

```python
class PerformanceAnalyzer:
    def analyze_data_rates(self, oscar_log, duration_seconds=60):
        """Analyze packet throughput and identify bottlenecks"""
        
        packets_received = []  # (timestamp, source)
        packets_forwarded = []  # (timestamp, destination)
        
        # Parse log timestamps
        with open(oscar_log) as f:
            for line in f:
                timestamp = self.extract_timestamp(line)
                if "Received" in line:
                    packets_received.append(timestamp)
                elif "Forwarded" in line:
                    packets_forwarded.append(timestamp)
        
        # Calculate rates
        receive_rate = len(packets_received) / duration_seconds
        forward_rate = len(packets_forwarded) / duration_seconds
        
        # Diagnose
        if receive_rate > 100:  # packets per second
            return {
                "status": "⚠ High Data Rate",
                "receive_rate": f"{receive_rate:.1f} packets/sec",
                "diagnosis": "High packet rate may cause Oscar overload",
                "suggestion": "Consider reducing collector frequency or batching data"
            }
        
        if forward_rate < receive_rate * 0.9:
            return {
                "status": "⚠ Packet Loss",
                "receive_rate": f"{receive_rate:.1f} packets/sec",
                "forward_rate": f"{forward_rate:.1f} packets/sec",
                "loss_percent": f"{(1 - forward_rate/receive_rate) * 100:.1f}%",
                "diagnosis": "Oscar is dropping packets",
                "suggestion": "Network congestion or Marvin cannot keep up - reduce data rate"
            }
        
        return {
            "status": "✓ Normal Data Flow",
            "receive_rate": f"{receive_rate:.1f} packets/sec",
            "forward_rate": f"{forward_rate:.1f} packets/sec"
        }
```

#### Resource Utilization Check

```python
class ResourceChecker:
    def check_component_resources(self):
        """Check CPU/memory usage of BIFF components"""
        
        try:
            import psutil
        except ImportError:
            return {"error": "psutil required for resource checking"}
        
        components = ["Minion.py", "Oscar.py", "BIFF.Marvin.jar"]
        
        results = {}
        for component in components:
            for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'cpu_percent', 'memory_percent']):
                try:
                    cmdline = ' '.join(proc.info['cmdline'] or [])
                    if component in cmdline:
                        results[component] = {
                            "pid": proc.info['pid'],
                            "cpu_percent": proc.cpu_percent(interval=1),
                            "memory_percent": proc.info['memory_percent'],
                            "status": self.evaluate_usage(proc.info['cpu_percent'], proc.info['memory_percent'])
                        }
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
        
        return results
    
    def evaluate_usage(self, cpu_percent, memory_percent):
        """Evaluate if resource usage is problematic"""
        if cpu_percent > 80:
            return "⚠ High CPU usage - may impact performance"
        elif memory_percent > 50:
            return "⚠ High memory usage - may need optimization"
        else:
            return "✓ Normal resource usage"
```

---

## Common Issue Patterns & Solutions

### Issue Database

```yaml
common_issues:
  no_data_in_widgets:
    symptoms:
      - "Widgets show blank/zero/no value"
      - "Dashboard empty"
    diagnosis_steps:
      1: "Check if all three components running"
      2: "Verify network connectivity (ports, firewall)"
      3: "Validate configuration consistency"
      4: "Check namespace:ID matching"
    common_causes:
      - cause: "Minion not running"
        fix: "Start Minion: cd Minion && python Minion.py -c MinionConfig.xml"
        frequency: "35%"
        
      - cause: "Wrong namespace or ID in widget"
        fix: "Update <MinionSrc Namespace=\"...\" ID=\"...\"/> to match collector"
        frequency: "25%"
        
      - cause: "Firewall blocking UDP"
        fix: "Add firewall rules for ports 1100 and 52001"
        frequency: "20%"
        
      - cause: "Port mismatch in configs"
        fix: "Ensure Minion target = Oscar listen = Marvin Oscar connection"
        frequency: "15%"
        
      - cause: "Collector failing"
        fix: "Test collector directly, check dependencies"
        frequency: "5%"
  
  intermittent_data:
    symptoms:
      - "Data appears then disappears"
      - "Widgets update sometimes"
    common_causes:
      - cause: "Network packet loss"
        fix: "Check network quality, reduce data rate"
        
      - cause: "Oscar overwhelmed"
        fix: "Reduce collector frequency, optimize collectors"
        
      - cause: "Process crashes and restarts"
        fix: "Check logs for crashes, fix errors"
  
  worked_yesterday:
    symptoms:
      - "Was working, now broken"
      - "No changes made but stopped working"
    common_causes:
      - cause: "System update broke dependencies"
        fix: "Reinstall Python packages (pip install -r requirements.txt)"
        
      - cause: "Firewall rules changed"
        fix: "Re-add firewall rules"
        
      - cause: "Oscar crashed and didn't restart"
        fix: "Restart Oscar, consider service/autostart configuration"
```

---

## Diagnostic Report Format

### Comprehensive Health Report

```
═══════════════════════════════════════════════════════
  BIFF System Diagnostic Report
  Generated: 2026-01-28 14:30:00
═══════════════════════════════════════════════════════

COMPONENT STATUS
────────────────────────────────────────────────────────
  ✓ Minion:  Running (PID 12345)
  ✓ Oscar:   Running (PID 23456)
  ✓ Marvin:  Running (PID 34567)

CONFIGURATION VALIDATION
────────────────────────────────────────────────────────
  ✓ Minion config: Valid XML
  ✓ Oscar config:  Valid XML
  ✓ Marvin config: Valid XML

NETWORK CONNECTIVITY
────────────────────────────────────────────────────────
  ✓ Port 1100 (Oscar):  Listening
  ✓ Port 52001 (Marvin): Listening
  ✓ Firewall: Rules configured
  ✓ Minion → Oscar: Test packet received
  ✓ Oscar → Marvin: Test packet received

CONFIGURATION CONSISTENCY
────────────────────────────────────────────────────────
  ✓ Minion target matches Oscar listen (port 1100)
  ✓ Oscar target matches Marvin listen (port 52001)

DATA FLOW ANALYSIS
────────────────────────────────────────────────────────
  ✓ Minion collecting: 15 collectors active
  ✓ Oscar receiving:   ~12 packets/second
  ✓ Oscar forwarding:  ~12 packets/second
  ✓ Marvin updating:   Last data received 2 seconds ago

ISSUES FOUND: 1 Warning
────────────────────────────────────────────────────────
  ⚠ WARNING: Widget namespace mismatch
    Widget: Gauge in Grid.xml
    Expects: SystemStats:cpu.usage
    Available: SystemMetrics:cpu.usage
    Fix: Change widget <MinionSrc Namespace="SystemMetrics" ID="cpu.usage"/>

OVERALL STATUS: ✓ HEALTHY (1 minor issue)
════════════════════════════════════════════════════════
```

---

## Success Metrics

### Quantitative

- **Diagnosis Time**: < 5 minutes (vs. 1-2 hours manual)
- **Root Cause Accuracy**: > 90%
- **Issue Resolution Rate**: > 80% can be fixed with agent guidance
- **False Positives**: < 10%

### Qualitative

- **Actionable Fixes**: Every diagnosis includes specific fix commands
- **User Understanding**: Users learn the system while troubleshooting
- **Self-Service**: Reduces need for forum/support requests
- **Confidence**: Users can validate fixes worked

---

## Implementation Phases

### Phase 1: Core Diagnostics (Week 1-2)

- Component health checks
- Port availability checks
- Configuration validation
- Basic log parsing

**Deliverable**: Can diagnose 80% of common issues (component not running, port problems)

### Phase 2: Advanced Analysis (Week 3)

- Configuration consistency checking
- Namespace:ID validation
- Network connectivity testing
- Collector testing framework

**Deliverable**: Can diagnose complex configuration mismatches

### Phase 3: Performance & Integration (Week 4)

- Performance analysis
- Resource utilization monitoring
- Interactive diagnosis workflow
- Integration with Quick Start Orchestrator

**Deliverable**: Production-ready diagnostic tool with guided troubleshooting

---

## Integration Points

### With Quick Start Orchestrator

- Quick Start runs diagnostics during setup
- Validates deployment before completion

### With Collector Builder

- Tests new collectors automatically
- Validates collector works before adding to config

### Standalone Mode

- Users can run diagnostics anytime
- Continuous monitoring mode for production systems

---

## Example Success Story

> **Before Debugging Agent**:
> User posts to forum: "Widgets show no data, please help"
>
> 12 hours later: "Did you start Oscar?"
> User: "Yes"
>
> 6 hours later: "Check your namespace IDs"
> User: "They look right to me"
>
> Next day: "Can you share your configs?"
> User: [shares 3 config files]
>
> 4 hours later: "Port 1100 vs 1101 mismatch"
> **Total time: 2 days, multiple forum posts**

> **With Debugging Agent**:
>
> ```
> User: "Widgets show no data"
> Agent: [runs diagnostics in 30 seconds]
> Agent: "Port mismatch found: Minion sends to 1101, Oscar listens on 1100"
> Agent: "Fix: Change OscarConfig.xml port to 1101"
> User: [makes change]
> Agent: [retests] "Issue resolved! Data flowing normally."
> **Total time: 3 minutes**
> ```

**Result**: 99% time savings, self-service resolution, user learns the system.
