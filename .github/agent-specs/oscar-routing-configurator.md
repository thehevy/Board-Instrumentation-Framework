# Oscar Routing Configurator Agent - Detailed Specification

## Executive Summary

The Oscar Routing Configurator Agent addresses Oscar's hidden complexity: while basic setups work with minimal config, Oscar's powerful routing, recording, shunting, and multi-source capabilities are underutilized because users don't understand them. This agent makes advanced Oscar features accessible, enabling enterprise topologies that were previously "expert-only" configurations.

**Target Time Savings**: 90% reduction in complex Oscar setup time (30 min vs 5+ hours)
**Primary Value**: Unlock Oscar's advanced features for production deployments

---

## User Personas

### Primary: Basic User (Needs Simple Setup)

- **Current State**: Uses default Oscar config from Quick Start
- **Goal**: Just route Minion data to Marvin
- **Pain Points**:
  - Doesn't know Oscar even has advanced features
  - Config intimidating even for basic changes
  - Unsure what ports to use
- **Success Metric**: Configure Oscar for multi-machine deployment in 5 minutes

### Secondary: Enterprise Architect (Needs Advanced Topology)

- **Current State**: Has multiple Minions, multiple Marvins, needs routing
- **Goal**: Complex topologies with filtering and recording
- **Pain Points**:
  - Documentation doesn't cover multi-source scenarios
  - Shunting/filtering syntax unclear
  - Recording configuration trial-and-error
  - Chaining Oscars not documented
- **Success Metric**: Production topology with 10+ Minions → 3 Oscars → 5 Marvins

### Tertiary: Data Engineer (Needs Recording & Playback)

- **Current State**: Wants to record sessions for analysis or testing
- **Goal**: Record live data for playback or offline analysis
- **Pain Points**:
  - Recording format undocumented
  - Playback loop controls confusing
  - Batch conversion obscure feature
  - Time-based playback difficult
- **Success Metric**: Record 1-hour session, play back at 2x speed for demo

---

## Oscar Architecture Context

### Oscar's Role in BIFF

```
Oscar is the data broker & router:

1. Data Routing:
   Minion 1 ─┐
   Minion 2 ─┼─> Oscar ─┬─> Marvin 1
   Minion 3 ─┘           ├─> Marvin 2
                         └─> Marvin 3

2. Data Recording:
   Minion ─> Oscar (recording) ─> MarvinData.biff file
                                   ↓ (later)
                            Oscar (playback) ─> Marvin

3. Data Filtering (Shunting):
   Minion ─> Oscar [filters specific namespace:ID] ─> Marvin

4. Oscar Chaining:
   Minion ─> Oscar 1 ─> Oscar 2 ─> Marvin
   (e.g., site-to-site aggregation)

5. Task Routing:
   Marvin ─> Oscar ─> Minion (remote task execution)
```

### Configuration Model

```xml
<Oscar ID="MyOscar">
    <!-- Incoming from Minions -->
    <IncomingMinionConnection PORT="1100">
        <!-- Optional: Accept from chained Oscar -->
        <Oscar IP="upstream.oscar.com" Port="6200" Key="secret"/>
    </IncomingMinionConnection>
    
    <!-- Incoming from Marvins (tasks, heartbeats) -->
    <IncomingMarvinConnection PORT="1101"/>
    
    <!-- Outgoing to Marvins -->
    <TargetConnection IP="marvin1.local" PORT="52001"/>
    <TargetConnection IP="marvin2.local" PORT="52002"/>
    
    <!-- Recording -->
    <RecordFile>Session_2026-01-28.biff</RecordFile>
    
    <!-- Filtering (Shunting) -->
    <Shunting File="ShuntConfig.xml"/>
</Oscar>
```

---

## Agent Capabilities

### 1. Topology Wizard

#### Deployment Pattern Selection

```python
class TopologyWizard:
    PATTERNS = {
        "single_machine": {
            "description": "All components on one machine",
            "components": "1 Minion, 1 Oscar, 1 Marvin",
            "complexity": "Low",
            "use_case": "Development, testing, small deployments"
        },
        "distributed_basic": {
            "description": "Components on different machines",
            "components": "N Minions (separate machines) → 1 Oscar → 1 Marvin",
            "complexity": "Medium",
            "use_case": "Monitor multiple servers from central dashboard"
        },
        "multi_dashboard": {
            "description": "Multiple viewers for same data",
            "components": "N Minions → 1 Oscar → M Marvins",
            "complexity": "Medium",
            "use_case": "NOC with multiple displays, team dashboards"
        },
        "hierarchical": {
            "description": "Chained Oscars for site aggregation",
            "components": "Minions → Site Oscar → Regional Oscar → Central Marvin",
            "complexity": "High",
            "use_case": "Multi-site enterprise monitoring"
        },
        "recording_replay": {
            "description": "Oscar records for later playback",
            "components": "Minion → Oscar (recording) → File → Oscar (playback) → Marvin",
            "complexity": "Medium",
            "use_case": "Demo recordings, data analysis, testing"
        },
        "filtered_routing": {
            "description": "Oscar routes different data to different Marvins",
            "components": "Minions → Oscar [filtering] → Marvin 1 (subset), Marvin 2 (subset)",
            "complexity": "High",
            "use_case": "Role-based dashboards, security filtering"
        }
    }
    
    def select_pattern(self):
        """Interactive pattern selection"""
        
        print("Oscar Deployment Patterns:")
        for idx, (pattern_id, info) in enumerate(self.PATTERNS.items(), 1):
            print(f"{idx}) {info['description']}")
            print(f"   Components: {info['components']}")
            print(f"   Use Case: {info['use_case']}")
            print()
        
        selection = input("Select pattern (1-6): ")
        pattern_id = list(self.PATTERNS.keys())[int(selection) - 1]
        
        return pattern_id, self.PATTERNS[pattern_id]
```

#### Network Configuration Builder

```python
class NetworkConfigBuilder:
    def build_distributed_config(self, minion_ips, oscar_ip, marvin_ips):
        """Generate Oscar config for distributed deployment"""
        
        config = {
            "oscar_id": "CentralOscar",
            "incoming_minion_port": 1100,
            "incoming_marvin_port": 1101,
            "targets": []
        }
        
        # Add target for each Marvin
        for idx, marvin_ip in enumerate(marvin_ips, 1):
            config["targets"].append({
                "ip": marvin_ip,
                "port": 52000 + idx,  # 52001, 52002, etc.
                "label": f"Marvin{idx}"
            })
        
        return config
    
    def validate_network_topology(self, config):
        """Ensure network topology makes sense"""
        
        issues = []
        
        # Check 1: Oscar accessible from all Minions
        for minion_ip in config.get("minion_ips", []):
            if not self.can_reach(minion_ip, config["oscar_ip"], config["incoming_minion_port"]):
                issues.append({
                    "severity": "CRITICAL",
                    "issue": f"Minion at {minion_ip} cannot reach Oscar at {config['oscar_ip']}:{config['incoming_minion_port']}",
                    "fix": "Check firewall, routing, or use different Oscar IP"
                })
        
        # Check 2: Oscar can reach all Marvins
        for target in config["targets"]:
            if not self.can_reach(config["oscar_ip"], target["ip"], target["port"]):
                issues.append({
                    "severity": "CRITICAL",
                    "issue": f"Oscar cannot reach Marvin at {target['ip']}:{target['port']}",
                    "fix": "Check firewall or adjust target IP"
                })
        
        return issues
```

---

### 2. Recording & Playback Configurator

#### Recording Setup

```python
class RecordingConfigurator:
    def setup_recording(self, output_file, options=None):
        """Configure Oscar for recording mode"""
        
        options = options or {}
        
        config = {
            "record_file": output_file,
            "auto_timestamp": options.get("auto_timestamp", True),
            "max_file_size": options.get("max_file_size", None),  # None = unlimited
            "compression": options.get("compression", False)
        }
        
        # Generate filename with timestamp if requested
        if config["auto_timestamp"]:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            base, ext = os.path.splitext(output_file)
            config["record_file"] = f"{base}_{timestamp}{ext}"
        
        # Add to Oscar config XML
        xml = f'<RecordFile>{config["record_file"]}</RecordFile>'
        
        return config, xml
    
    def estimate_file_size(self, collector_count, frequency_avg, duration_hours):
        """Estimate recording file size"""
        
        # Average packet size: ~500 bytes (XML overhead)
        avg_packet_size = 500
        
        # Packets per second
        packets_per_sec = collector_count * (1000 / frequency_avg)
        
        # Total size
        total_packets = packets_per_sec * duration_hours * 3600
        size_bytes = total_packets * avg_packet_size
        
        return {
            "packets_per_second": packets_per_sec,
            "total_packets": total_packets,
            "size_mb": size_bytes / (1024 * 1024),
            "size_gb": size_bytes / (1024 * 1024 * 1024)
        }
```

#### Playback Configuration

```python
class PlaybackConfigurator:
    def setup_playback(self, input_file, options=None):
        """Configure Oscar for playback mode"""
        
        options = options or {}
        
        playback_config = {
            "input_file": input_file,
            "speed": options.get("speed", 1.0),  # 1.0 = realtime, 2.0 = 2x speed
            "loop": options.get("loop", False),
            "loop_start": options.get("loop_start", 0),
            "loop_end": options.get("loop_end", None),
            "exit_after": options.get("exit_after", False)
        }
        
        # Build command line
        cmd_parts = [
            "python Oscar.py",
            "-c OscarConfig.xml",
            f"-playback {input_file}"
        ]
        
        if playback_config["speed"] != 1.0:
            cmd_parts.append(f"-playbackspeed {playback_config['speed']}")
        
        if playback_config["loop"]:
            cmd_parts.append("-autorun loop")
            if playback_config["loop_start"]:
                cmd_parts.append(f"-autorunloopstart {playback_config['loop_start']}")
            if playback_config["loop_end"]:
                cmd_parts.append(f"-autorunloopend {playback_config['loop_end']}")
        
        if playback_config["exit_after"]:
            cmd_parts.append("-exitafterautorun")
        
        return playback_config, " ".join(cmd_parts)
    
    def analyze_recording(self, recording_file):
        """Analyze recording file contents"""
        
        # Parse recording file to extract metadata
        # (Recording format is binary, would need Oscar's parser)
        
        return {
            "duration": "Unknown (requires Oscar parser)",
            "packet_count": "Unknown",
            "namespaces": ["Use Oscar GUI to inspect"],
            "file_size_mb": os.path.getsize(recording_file) / (1024 * 1024)
        }
```

---

### 3. Shunting (Filtering) Configurator

#### Filter Rule Builder

```python
class ShuntingConfigurator:
    def create_filter_rules(self, rules):
        """Generate shunting configuration"""
        
        shunt_config = {
            "rules": rules,
            "xml_file": "ShuntConfig.xml"
        }
        
        return shunt_config
    
    def build_namespace_filter(self, namespace_pattern, target_ips):
        """Filter specific namespace to specific Marvins"""
        
        rule = {
            "type": "namespace",
            "pattern": namespace_pattern,  # Can use wildcards
            "targets": target_ips,
            "action": "forward_only_to_targets"
        }
        
        return rule
    
    def build_id_filter(self, namespace, id_pattern, action="include"):
        """Filter specific IDs within namespace"""
        
        rule = {
            "type": "id",
            "namespace": namespace,
            "id_pattern": id_pattern,  # Can use wildcards
            "action": action  # "include" or "exclude"
        }
        
        return rule
    
    def generate_shunt_xml(self, rules):
        """Generate ShuntConfig.xml"""
        
        xml_parts = ['<?xml version="1.0" encoding="utf-8"?>']
        xml_parts.append('<Shunting>')
        
        for rule in rules:
            if rule["type"] == "namespace":
                # Namespace-based routing
                xml_parts.append(f'    <Namespace name="{rule["pattern"]}">')
                for target in rule["targets"]:
                    xml_parts.append(f'        <Target IP="{target["ip"]}" Port="{target["port"]}"/>')
                xml_parts.append('    </Namespace>')
            
            elif rule["type"] == "id":
                # ID-based filtering
                xml_parts.append(f'    <Filter namespace="{rule["namespace"]}" id="{rule["id_pattern"]}" action="{rule["action"]}"/>')
        
        xml_parts.append('</Shunting>')
        
        return '\n'.join(xml_parts)
```

#### Example Shunting Scenarios

```python
class ShuntingExamples:
    def example_role_based_dashboards(self):
        """Different teams see different metrics"""
        
        return {
            "scenario": "Role-based dashboards",
            "description": "Operations team sees all metrics, Management sees only KPIs",
            "rules": [
                {
                    "namespace": "SystemMetrics",
                    "targets": ["ops-marvin:52001"]  # Operations dashboard
                },
                {
                    "namespace": "ApplicationKPI",
                    "targets": ["ops-marvin:52001", "mgmt-marvin:52002"]  # Both
                },
                {
                    "namespace": "DetailedLogs",
                    "targets": ["ops-marvin:52001"]  # Operations only
                }
            ]
        }
    
    def example_security_filtering(self):
        """Hide sensitive metrics from certain displays"""
        
        return {
            "scenario": "Security filtering",
            "description": "Public dashboard doesn't show security metrics",
            "rules": [
                {
                    "namespace": "PublicMetrics",
                    "targets": ["public-marvin:52003", "internal-marvin:52001"]
                },
                {
                    "namespace": "SecurityMetrics",
                    "targets": ["internal-marvin:52001"]  # Internal only
                }
            ]
        }
```

---

### 4. Oscar Chaining Configurator

#### Hierarchical Setup

```python
class OscarChainingConfigurator:
    def setup_chain(self, levels):
        """Configure multi-level Oscar hierarchy"""
        
        # Example: Site → Regional → Corporate
        # levels = [
        #   {"name": "Site1", "upstream": "Regional"},
        #   {"name": "Regional", "upstream": "Corporate"},
        #   {"name": "Corporate", "upstream": None}
        # ]
        
        configs = {}
        
        for level in levels:
            config = {
                "oscar_id": level["name"],
                "incoming_minion_port": 1100,
                "targets": []
            }
            
            if level["upstream"]:
                # This Oscar forwards to upstream Oscar
                upstream = self.find_level(levels, level["upstream"])
                config["targets"].append({
                    "ip": upstream["ip"],
                    "port": upstream.get("oscar_port", 6200),
                    "is_oscar": True,
                    "key": level.get("chain_key", "AutoKey")
                })
            else:
                # Top-level Oscar forwards to Marvin(s)
                config["targets"] = level.get("marvins", [])
            
            configs[level["name"]] = config
        
        return configs
    
    def generate_chain_xml(self, config):
        """Generate OscarConfig.xml for chained Oscar"""
        
        xml_parts = [f'<Oscar ID="{config["oscar_id"]}">']
        
        # Incoming connection with Oscar authentication
        xml_parts.append(f'    <IncomingMinionConnection PORT="{config["incoming_minion_port"]}">')
        
        # If this Oscar accepts from downstream Oscars, add keys
        if config.get("accept_from_oscars"):
            for downstream in config["accept_from_oscars"]:
                xml_parts.append(f'        <Oscar IP="{downstream["ip"]}" Port="{downstream["port"]}" Key="{downstream["key"]}"/>')
        
        xml_parts.append('    </IncomingMinionConnection>')
        
        # Targets (upstream Oscar or Marvins)
        for target in config["targets"]:
            if target.get("is_oscar"):
                # Forwarding to another Oscar
                xml_parts.append(f'    <OscarConnection IP="{target["ip"]}" Port="{target["port"]}" Key="{target["key"]}"/>')
            else:
                # Forwarding to Marvin
                xml_parts.append(f'    <TargetConnection IP="{target["ip"]}" PORT="{target["port"]}"/>')
        
        xml_parts.append('</Oscar>')
        
        return '\n'.join(xml_parts)
```

---

### 5. Dynamic Connection Management

#### Auto-Discovery Setup

```python
class DynamicConnectionConfigurator:
    def setup_dynamic_marvin_connections(self):
        """Configure Oscar to accept connections from any Marvin"""
        
        config = {
            "dynamic_mode": True,
            "bullhorn_key": self.generate_bullhorn_key(),
            "auto_add_marvins": True
        }
        
        xml = f'''
    <DynamicMarvinConnections>
        <BullhornKey>{config["bullhorn_key"]}</BullhornKey>
        <AutoAccept>true</AutoAccept>
    </DynamicMarvinConnections>
'''
        
        guidance = """
Dynamic connections allow Marvins to register with Oscar automatically.

Marvin configuration:
    <OscarBullhorn IP="{oscar_ip}" Port="1100" Key="{key}"/>

When Marvin starts, it announces itself to Oscar, which adds it as a target.
Useful for environments where Marvin instances come and go.
"""
        
        return config, xml, guidance
    
    def generate_bullhorn_key(self):
        """Generate secure key for bullhorn authentication"""
        import secrets
        return secrets.token_urlsafe(32)
```

---

### 6. Performance & Resource Configuration

#### Throughput Optimization

```python
class PerformanceConfigurator:
    def configure_high_throughput(self, estimated_packets_per_sec):
        """Configure Oscar for high data rates"""
        
        config = {
            "use_governor": False,  # Governor throttles, disable for high throughput
            "receive_buffer_size": 65536,  # Larger buffer
            "max_queue_size": 10000
        }
        
        if estimated_packets_per_sec > 100:
            config["use_governor"] = True
            config["governor_threshold_kb"] = 4096
            config["governor_backoff_ms"] = 5
            
            warning = """
High data rate detected (>100 packets/sec).

Recommendations:
1. Enable Governor to prevent Oscar overload
2. Increase receive buffer size
3. Consider reducing Minion collector frequency
4. Monitor Oscar CPU usage
"""
            return config, warning
        
        return config, None
    
    def configure_resource_limits(self, max_memory_mb, max_cpu_percent):
        """Set resource limits for Oscar process"""
        
        # Would require OS-specific implementation
        # Linux: cgroups, systemd limits
        # Windows: Job objects
        
        limits = {
            "memory_mb": max_memory_mb,
            "cpu_percent": max_cpu_percent,
            "implementation": "OS-specific"
        }
        
        return limits
```

---

### 7. Firewall & Network Helper

#### Windows Firewall Configuration

```python
class WindowsFirewallHelper:
    def generate_firewall_rules(self, oscar_config):
        """Generate PowerShell commands for Windows Firewall"""
        
        rules = []
        
        # Incoming from Minions
        rules.append({
            "name": "BIFF Oscar - Incoming Minion Data",
            "port": oscar_config["incoming_minion_port"],
            "direction": "in",
            "command": f'netsh advfirewall firewall add rule name="BIFF Oscar - Incoming Minion Data" dir=in action=allow protocol=UDP localport={oscar_config["incoming_minion_port"]}'
        })
        
        # Incoming from Marvins (tasks)
        if "incoming_marvin_port" in oscar_config:
            rules.append({
                "name": "BIFF Oscar - Incoming Marvin Tasks",
                "port": oscar_config["incoming_marvin_port"],
                "direction": "in",
                "command": f'netsh advfirewall firewall add rule name="BIFF Oscar - Incoming Marvin Tasks" dir=in action=allow protocol=UDP localport={oscar_config["incoming_marvin_port"]}'
            })
        
        # Outgoing to Marvins
        for target in oscar_config.get("targets", []):
            rules.append({
                "name": f"BIFF Oscar - Outgoing to Marvin ({target['ip']})",
                "port": target["port"],
                "direction": "out",
                "command": f'netsh advfirewall firewall add rule name="BIFF Oscar - Outgoing to {target["ip"]}" dir=out action=allow protocol=UDP remoteip={target["ip"]} remoteport={target["port"]}'
            })
        
        return rules
```

---

## Interactive Workflow Example

```
Agent: I'll help configure Oscar for your deployment. What topology do you need?

1) Single machine (localhost) - Development/Testing
2) Distributed basic - Multiple servers → Central Oscar → Dashboard
3) Multi-dashboard - Same data to multiple Marvins
4) Hierarchical - Chained Oscars (site → regional → corporate)
5) Recording/Replay - Record sessions for later
6) Custom

User: 2

Agent: Distributed basic topology selected.

How many Minions will send data to Oscar?

User: 3

Agent: 3 Minions. What are their IP addresses?
  Minion 1 IP:

User: 192.168.1.101

Agent: Minion 2 IP:

User: 192.168.1.102

Agent: Minion 3 IP:

User: 192.168.1.103

Agent: Great! Where is Oscar running?
  Oscar IP:

User: 192.168.1.100

Agent: Oscar will listen on port 1100 (default). Change it?

User: no

Agent: How many Marvin dashboards?

User: 1

Agent: Marvin 1 IP:

User: 192.168.1.100

Agent: Same machine as Oscar (192.168.1.100). Marvin will listen on port 52001.

Generating Oscar configuration...

✓ Created: Oscar/OscarConfig.xml

Configuration summary:
  Oscar ID: CentralOscar
  Listens on: 192.168.1.100:1100 (for Minions)
  Forwards to: 192.168.1.100:52001 (Marvin)

Next steps:
1. Update each Minion's MinionConfig.xml:
   <TargetConnection IP="192.168.1.100" PORT="1100"/>

2. Update Marvin's application config:
   <OscarConnection IP="192.168.1.100" Port="52001"/>

3. Firewall rules needed (Windows):
   [Generates PowerShell commands...]

Would you like me to:
  a) Test connectivity
  b) Set up recording
  c) Add filtering rules
  d) Done
```

---

## Success Metrics

### Quantitative

- **Configuration Time**: < 10 minutes for distributed setup (vs. 2+ hours trial-and-error)
- **Configuration Correctness**: 100% valid XML, matching IPs/ports
- **Feature Utilization**: 50%+ users utilize advanced features (vs. <5% currently)
- **Support Requests**: 60% reduction in Oscar-related questions

### Qualitative

- **Feature Awareness**: Users discover Oscar capabilities they didn't know existed
- **Enterprise Adoption**: Complex topologies become deployable
- **Recording Usage**: Recording/playback becomes standard workflow
- **Chaining Success**: Multi-site deployments feasible

---

## Implementation Phases

### Phase 1: Basic Topology (Week 1)

- Distributed setup wizard
- Port/IP configuration
- Basic XML generation
- Network validation

**Deliverable**: Can configure common Oscar topologies

### Phase 2: Advanced Features (Week 2)

- Recording/playback configuration
- Shunting (filtering) setup
- Firewall rule generation
- Performance tuning

**Deliverable**: Advanced Oscar features accessible

### Phase 3: Enterprise Features (Week 3)

- Oscar chaining
- Dynamic connections
- High-throughput optimization
- Multi-Oscar orchestration

**Deliverable**: Enterprise-ready Oscar deployments

---

## Integration Points

### With Quick Start Orchestrator

- Quick Start uses this for Oscar config generation

### With Debugging Agent

- Debugging Agent uses topology validator

### With Collector Builder

- Advises on Oscar capacity when adding collectors

---

## Example Success Story

> **Before Oscar Routing Configurator**:
> Enterprise architect spends 8 hours reading sparse documentation, trial-and-error with shunting XML syntax, debugging why chained Oscars won't authenticate, finally gets 3-site topology working after 3 days.

**With Oscar Routing Configurator**:

**Result**: 95% time savings, enterprise topologies become standard practice, Oscar's power unlocked.
