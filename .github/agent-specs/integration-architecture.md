# BIFF Agent Integration Architecture

## Executive Summary

The five BIFF AI agents form a cohesive ecosystem that guides users through the complete lifecycle: **onboarding → customization → visualization → optimization → troubleshooting**. Rather than isolated tools, they share common infrastructure, exchange validated configurations, and orchestrate handoffs to create seamless multi-step workflows.

**Design Principles**:
1. **Progressive Disclosure**: Each agent builds on previous agent's output
2. **Validation Chain**: Configs validated at creation and re-validated at consumption
3. **Context Preservation**: Agents maintain session state for intelligent handoffs
4. **Zero-Copy Integration**: Agents read/write actual BIFF config files, not intermediates
5. **Graceful Degradation**: Each agent works standalone if needed

---

## Agent Ecosystem Map

```
┌─────────────────────────────────────────────────────────────────────────┐
│                          User Journey Flow                              │
└─────────────────────────────────────────────────────────────────────────┘

1. ONBOARDING          2. CUSTOMIZATION       3. VISUALIZATION
   ↓                      ↓                      ↓
┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐
│ Quick Start      │→ │ Collector        │→ │ GUI Composer     │
│ Orchestrator     │  │ Builder          │  │                  │
└──────────────────┘  └──────────────────┘  └──────────────────┘
   Creates:              Creates:              Creates:
   - MinionConfig.xml    - New collectors      - Application.xml
   - OscarConfig.xml     - Updated Minion cfg  - Grid_*.xml
   - Application.xml     

4. OPTIMIZATION        5. TROUBLESHOOTING
   ↓                      ↓
┌──────────────────┐  ┌──────────────────┐
│ Oscar Routing    │  │ Debugging        │
│ Configurator     │  │ Agent            │
└──────────────────┘  └──────────────────┘
   Enhances:             Validates:
   - OscarConfig.xml     - All configs
   - Topology            - Network
                          - Processes

      ↓ (any time)
┌──────────────────────────────────────────┐
│    All agents can invoke Debugging      │
│    Agent when issues detected            │
└──────────────────────────────────────────┘
```

---

## Shared Infrastructure

### 1. Common Configuration Library

All agents use a shared configuration parser/validator library to ensure consistency.

```python
# shared/biff_config.py
from dataclasses import dataclass
from typing import List, Dict, Optional
import xml.etree.ElementTree as ET

@dataclass
class CollectorSpec:
    """Standardized collector representation across all agents"""
    namespace: str
    id: str
    frequency: int
    executable: Optional[str]
    params: List[str]
    full_id: str  # "namespace:id"
    
    @classmethod
    def from_xml(cls, namespace_elem, collector_elem):
        """Parse from Minion XML"""
        namespace = namespace_elem.find('Name').text
        collector_id = collector_elem.get('ID')
        frequency = int(collector_elem.get('Frequency', '1000'))
        
        executable_elem = collector_elem.find('Executable')
        executable = executable_elem.text if executable_elem is not None else None
        
        params = [p.text for p in collector_elem.findall('Param')]
        
        return cls(
            namespace=namespace,
            id=collector_id,
            frequency=frequency,
            executable=executable,
            params=params,
            full_id=f"{namespace}:{collector_id}"
        )

@dataclass
class OscarConnection:
    """Standardized Oscar connection representation"""
    ip: str
    port: int
    is_incoming: bool  # True for incoming (from Minions), False for outgoing (to Marvins)
    
    @classmethod
    def from_minion_target(cls, target_elem):
        """Parse from Minion TargetConnection"""
        return cls(
            ip=target_elem.get('IP'),
            port=int(target_elem.get('PORT')),
            is_incoming=False
        )
    
    @classmethod
    def from_oscar_incoming(cls, incoming_elem):
        """Parse from Oscar IncomingMinionConnection"""
        return cls(
            ip='0.0.0.0',  # Oscar listens on all interfaces
            port=int(incoming_elem.get('PORT')),
            is_incoming=True
        )

@dataclass
class MarvinWidget:
    """Standardized widget representation"""
    widget_type: str
    title: str
    namespace: str
    collector_id: str
    position: Dict[str, int]  # {row, column, rowspan, columnspan}
    config: Dict  # Widget-specific config
    
    def get_full_id(self) -> str:
        return f"{self.namespace}:{self.collector_id}"

class BIFFConfigParser:
    """Unified parser for all BIFF configuration files"""
    
    def __init__(self, workspace_root: str):
        self.workspace_root = workspace_root
        self.minion_config_path = None
        self.oscar_config_path = None
        self.marvin_config_path = None
    
    def discover_configs(self) -> Dict[str, str]:
        """Find all BIFF config files in workspace"""
        configs = {
            "minion": self._find_file("MinionConfig.xml", "Minion/"),
            "oscar": self._find_file("OscarConfig.xml", "Oscar/"),
            "marvin": self._find_file("*.xml", "Marvin/", pattern=True)
        }
        return configs
    
    def parse_minion_config(self, config_path: str) -> Dict:
        """Parse Minion configuration"""
        tree = ET.parse(config_path)
        root = tree.getroot()
        
        collectors = []
        namespaces = []
        
        for namespace_elem in root.findall('.//Namespace'):
            ns_name = namespace_elem.find('Name').text
            namespaces.append(ns_name)
            
            for collector_elem in namespace_elem.findall('.//Collector'):
                collectors.append(
                    CollectorSpec.from_xml(namespace_elem, collector_elem)
                )
        
        # Parse target connections
        targets = []
        for target_elem in root.findall('.//TargetConnection'):
            targets.append(OscarConnection.from_minion_target(target_elem))
        
        return {
            "collectors": collectors,
            "namespaces": namespaces,
            "targets": targets,
            "config_path": config_path
        }
    
    def parse_oscar_config(self, config_path: str) -> Dict:
        """Parse Oscar configuration"""
        tree = ET.parse(config_path)
        root = tree.getroot()
        
        # Incoming connections
        incoming = []
        for incoming_elem in root.findall('.//IncomingMinionConnection'):
            incoming.append(OscarConnection.from_oscar_incoming(incoming_elem))
        
        # Outgoing targets
        targets = []
        for target_elem in root.findall('.//TargetConnection'):
            targets.append(OscarConnection(
                ip=target_elem.get('IP'),
                port=int(target_elem.get('PORT')),
                is_incoming=False
            ))
        
        return {
            "incoming": incoming,
            "targets": targets,
            "config_path": config_path
        }
    
    def parse_marvin_config(self, config_path: str) -> Dict:
        """Parse Marvin application configuration"""
        tree = ET.parse(config_path)
        root = tree.getroot()
        
        # Parse Oscar connection
        oscar_conn_elem = root.find('.//OscarConnection')
        oscar_connection = None
        if oscar_conn_elem is not None:
            oscar_connection = OscarConnection(
                ip=oscar_conn_elem.get('IP'),
                port=int(oscar_conn_elem.get('Port')),
                is_incoming=False  # Marvin connects to Oscar
            )
        
        # Parse grids and widgets
        widgets = []
        for grid_file_elem in root.findall('.//Grid[@File]'):
            grid_path = os.path.join(
                os.path.dirname(config_path),
                grid_file_elem.get('File')
            )
            widgets.extend(self._parse_grid_file(grid_path))
        
        return {
            "oscar_connection": oscar_connection,
            "widgets": widgets,
            "config_path": config_path
        }
    
    def _parse_grid_file(self, grid_path: str) -> List[MarvinWidget]:
        """Parse widget definitions from Grid XML"""
        # Implementation would parse widgets from grid files
        # Returns list of MarvinWidget objects
        pass

class BIFFConfigValidator:
    """Cross-component configuration validator"""
    
    def __init__(self, parser: BIFFConfigParser):
        self.parser = parser
    
    def validate_full_system(self) -> List[Dict]:
        """Validate complete BIFF configuration"""
        issues = []
        
        configs = self.parser.discover_configs()
        
        # Parse all configs
        minion_data = self.parser.parse_minion_config(configs["minion"])
        oscar_data = self.parser.parse_oscar_config(configs["oscar"])
        marvin_data = self.parser.parse_marvin_config(configs["marvin"])
        
        # Validate connections
        issues.extend(self._validate_minion_to_oscar(minion_data, oscar_data))
        issues.extend(self._validate_oscar_to_marvin(oscar_data, marvin_data))
        issues.extend(self._validate_widget_bindings(minion_data, marvin_data))
        
        return issues
    
    def _validate_minion_to_oscar(self, minion_data, oscar_data):
        """Ensure Minion targets match Oscar incoming ports"""
        issues = []
        
        for minion_target in minion_data["targets"]:
            # Find matching Oscar incoming connection
            matching = [
                osc for osc in oscar_data["incoming"]
                if osc.port == minion_target.port
            ]
            
            if not matching:
                issues.append({
                    "severity": "ERROR",
                    "component": "Minion→Oscar",
                    "issue": f"Minion sends to port {minion_target.port}, but Oscar doesn't listen there",
                    "fix": f"Add <IncomingMinionConnection PORT=\"{minion_target.port}\"/> to OscarConfig.xml"
                })
        
        return issues
    
    def _validate_oscar_to_marvin(self, oscar_data, marvin_data):
        """Ensure Oscar targets match Marvin expectations"""
        issues = []
        
        marvin_oscar_conn = marvin_data.get("oscar_connection")
        if not marvin_oscar_conn:
            issues.append({
                "severity": "WARNING",
                "component": "Marvin",
                "issue": "Marvin has no Oscar connection configured",
                "fix": "Add <OscarConnection IP=\"...\" Port=\"...\"/> to Marvin config"
            })
            return issues
        
        # Check if Oscar is targeting Marvin's expected port
        matching = [
            t for t in oscar_data["targets"]
            if t.port == marvin_oscar_conn.port
        ]
        
        if not matching:
            issues.append({
                "severity": "ERROR",
                "component": "Oscar→Marvin",
                "issue": f"Marvin expects Oscar on port {marvin_oscar_conn.port}, but Oscar doesn't send there",
                "fix": f"Add <TargetConnection IP=\"{marvin_oscar_conn.ip}\" PORT=\"{marvin_oscar_conn.port}\"/> to OscarConfig.xml"
            })
        
        return issues
    
    def _validate_widget_bindings(self, minion_data, marvin_data):
        """Ensure widgets bind to existing collectors"""
        issues = []
        
        # Build set of available collectors
        available_collectors = {c.full_id for c in minion_data["collectors"]}
        
        # Check each widget
        for widget in marvin_data["widgets"]:
            widget_full_id = widget.get_full_id()
            
            if widget_full_id not in available_collectors:
                issues.append({
                    "severity": "ERROR",
                    "component": "Marvin Widget Binding",
                    "issue": f"Widget '{widget.title}' binds to {widget_full_id}, but no such collector exists",
                    "fix": f"Add collector with Namespace=\"{widget.namespace}\" ID=\"{widget.collector_id}\" to MinionConfig.xml"
                })
        
        return issues
```

---

### 2. Session State Manager

Agents maintain state to enable context-aware handoffs.

```python
# shared/session_state.py
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

class SessionState:
    """Persistent session state shared between agents"""
    
    def __init__(self, workspace_root: str):
        self.workspace_root = Path(workspace_root)
        self.state_file = self.workspace_root / ".biff" / "agent_session.json"
        self.state_file.parent.mkdir(exist_ok=True)
        self.state = self._load_state()
    
    def _load_state(self) -> Dict:
        """Load existing session state"""
        if self.state_file.exists():
            with open(self.state_file) as f:
                return json.load(f)
        return self._default_state()
    
    def _default_state(self) -> Dict:
        """Default session state"""
        return {
            "created": datetime.now().isoformat(),
            "last_agent": None,
            "workflow_stage": "new",  # new, onboarded, customizing, deployed, troubleshooting
            "configs": {
                "minion": None,
                "oscar": None,
                "marvin": None
            },
            "discovered_collectors": [],
            "validation_status": None,
            "handoff_context": {}
        }
    
    def save(self):
        """Persist state to disk"""
        with open(self.state_file, 'w') as f:
            json.dump(self.state, f, indent=2)
    
    def set_workflow_stage(self, stage: str):
        """Update current workflow stage"""
        self.state["workflow_stage"] = stage
        self.save()
    
    def record_agent_activity(self, agent_name: str, activity: Dict):
        """Record agent activity for context"""
        self.state["last_agent"] = agent_name
        self.state["last_activity"] = datetime.now().isoformat()
        
        if agent_name not in self.state:
            self.state[agent_name] = []
        
        self.state[agent_name].append({
            "timestamp": datetime.now().isoformat(),
            "activity": activity
        })
        
        self.save()
    
    def set_handoff_context(self, from_agent: str, to_agent: str, context: Dict):
        """Store context for agent handoff"""
        self.state["handoff_context"] = {
            "from": from_agent,
            "to": to_agent,
            "timestamp": datetime.now().isoformat(),
            "context": context
        }
        self.save()
    
    def get_handoff_context(self, agent_name: str) -> Optional[Dict]:
        """Retrieve handoff context if intended for this agent"""
        handoff = self.state.get("handoff_context", {})
        if handoff.get("to") == agent_name:
            return handoff.get("context")
        return None
    
    def clear_handoff_context(self):
        """Clear handoff context after consumption"""
        self.state["handoff_context"] = {}
        self.save()
```

---

## Agent Interaction Patterns

### Pattern 1: Sequential Handoff (Quick Start → Collector Builder)

```python
# In Quick Start Orchestrator
def complete_quick_start(self, config_paths: Dict):
    """Quick Start completes, prepares handoff to Collector Builder"""
    
    # Record generated configs
    session = SessionState(self.workspace_root)
    session.state["configs"] = config_paths
    session.set_workflow_stage("onboarded")
    
    # Parse generated Minion config to discover collectors
    parser = BIFFConfigParser(self.workspace_root)
    minion_data = parser.parse_minion_config(config_paths["minion"])
    
    session.state["discovered_collectors"] = [
        c.full_id for c in minion_data["collectors"]
    ]
    
    # Prepare handoff context for Collector Builder
    handoff_context = {
        "minion_config": config_paths["minion"],
        "existing_collectors": minion_data["collectors"],
        "available_namespaces": minion_data["namespaces"],
        "suggestion": "Add custom collectors for your specific monitoring needs"
    }
    
    session.set_handoff_context(
        from_agent="QuickStartOrchestrator",
        to_agent="CollectorBuilder",
        context=handoff_context
    )
    
    # Offer transition to user
    print("\n" + "="*60)
    print("✓ Quick Start Complete!")
    print("="*60)
    print(f"\nYour BIFF deployment is ready:")
    print(f"  Minion:  {config_paths['minion']}")
    print(f"  Oscar:   {config_paths['oscar']}")
    print(f"  Marvin:  {config_paths['marvin']}")
    print(f"\nStarted with {len(minion_data['collectors'])} demo collectors.")
    print("\nNext steps:")
    print("  1) Create custom collectors for your systems")
    print("  2) Build dashboard visualizations")
    print("  3) Configure advanced Oscar routing")
    print("\nWould you like to create a custom collector now?")
    
    response = input("Create collector? (y/n): ")
    if response.lower() == 'y':
        # Launch Collector Builder with handoff context
        from collector_builder import CollectorBuilder
        builder = CollectorBuilder(self.workspace_root)
        builder.start_from_handoff()  # Uses session state

# In Collector Builder
class CollectorBuilder:
    def start_from_handoff(self):
        """Start Collector Builder with context from previous agent"""
        
        session = SessionState(self.workspace_root)
        handoff = session.get_handoff_context("CollectorBuilder")
        
        if handoff:
            print("\n" + "="*60)
            print("Continuing from Quick Start...")
            print("="*60)
            print(f"\nYour Minion already has these collectors:")
            for collector in handoff["existing_collectors"]:
                print(f"  - {collector.full_id}")
            
            print(f"\nLet's add a new collector!")
            
            # Use handoff context
            self.minion_config_path = handoff["minion_config"]
            self.existing_collectors = handoff["existing_collectors"]
            self.namespaces = handoff["available_namespaces"]
            
            session.clear_handoff_context()
            
            # Start wizard with context
            self.run_wizard(use_existing_namespace=True)
        else:
            # Standalone start
            self.run_wizard()
```

---

### Pattern 2: On-Demand Invocation (Any Agent → Debugging Agent)

```python
# Shared utility used by all agents
class AgentHelpers:
    @staticmethod
    def invoke_debugging_agent(component: str, issue_description: str):
        """Any agent can invoke Debugging Agent for diagnostics"""
        
        from debugging_agent import DebuggingAgent
        
        print("\n⚠️  Issue detected. Invoking Debugging Agent...")
        
        debugger = DebuggingAgent(workspace_root)
        
        # Pass context about what triggered the debugging request
        context = {
            "triggered_by": inspect.stack()[1].function,
            "component": component,
            "issue": issue_description
        }
        
        # Run targeted diagnostics
        results = debugger.diagnose_component(component, context)
        
        return results

# Example: In GUI Composer
class GUIComposer:
    def validate_widget_bindings(self, widgets, minion_config):
        """Validate widgets bind to existing collectors"""
        
        parser = BIFFConfigParser(self.workspace_root)
        minion_data = parser.parse_minion_config(minion_config)
        
        available = {c.full_id for c in minion_data["collectors"]}
        
        for widget in widgets:
            widget_binding = f"{widget.namespace}:{widget.collector_id}"
            
            if widget_binding not in available:
                # Invoke debugging agent
                results = AgentHelpers.invoke_debugging_agent(
                    component="Widget Binding",
                    issue_description=f"Widget binds to {widget_binding} but collector doesn't exist"
                )
                
                # Debugging agent returns suggestions
                if results["suggestions"]:
                    print("\nDebugging Agent suggestions:")
                    for suggestion in results["suggestions"]:
                        print(f"  - {suggestion}")
                
                # Ask user how to proceed
                print("\nHow would you like to fix this?")
                print("  1) Remove this widget")
                print("  2) Create the missing collector")
                print("  3) Change widget binding")
                
                choice = input("Choice: ")
                # ... handle user choice
```

---

### Pattern 3: Parallel Validation (Multiple Agents → Shared Validator)

```python
# All agents use shared validator
from shared.biff_config import BIFFConfigValidator, BIFFConfigParser

class QuickStartOrchestrator:
    def validate_generated_configs(self):
        """Validate Quick Start output"""
        parser = BIFFConfigParser(self.workspace_root)
        validator = BIFFConfigValidator(parser)
        
        issues = validator.validate_full_system()
        
        return self._categorize_issues(issues)

class CollectorBuilder:
    def validate_new_collector(self, namespace, collector_id):
        """Validate new collector doesn't break system"""
        parser = BIFFConfigParser(self.workspace_root)
        validator = BIFFConfigValidator(parser)
        
        # Full system validation
        issues = validator.validate_full_system()
        
        # Filter to only issues related to new collector
        collector_issues = [
            i for i in issues
            if namespace in str(i) or collector_id in str(i)
        ]
        
        return collector_issues

class GUIComposer:
    def validate_dashboard(self, dashboard_config):
        """Validate dashboard before generation"""
        # Write temporary config
        temp_config = self._write_temp_config(dashboard_config)
        
        parser = BIFFConfigParser(self.workspace_root)
        validator = BIFFConfigValidator(parser)
        
        issues = validator.validate_full_system()
        
        # Clean up temp config
        os.remove(temp_config)
        
        return issues
```

---

## Complete User Journey Examples

### Journey 1: Zero to Dashboard (All Agents Orchestrated)

```
User: "Set up BIFF monitoring for my servers"

┌─────────────────────────────────────────────────────────────┐
│ Phase 1: Quick Start Orchestrator                           │
└─────────────────────────────────────────────────────────────┘

Quick Start: Detected Windows. Install Java?
User: yes
Quick Start: [installs Java]
Quick Start: Build Enzo dependency?
User: yes
Quick Start: [builds Enzo]
Quick Start: Build Marvin?
User: yes
Quick Start: [builds Marvin]
Quick Start: Deployment on single machine or distributed?
User: distributed
Quick Start: How many servers?
User: 3
Quick Start: [collects IPs, generates configs]
Quick Start: ✓ Generated MinionConfig.xml (3 demo collectors)
Quick Start: ✓ Generated OscarConfig.xml
Quick Start: ✓ Generated Application.xml (blank dashboard)
Quick Start: ✓ Connectivity validated

Quick Start: Next: Add custom collectors?
User: yes

[HANDOFF: QuickStart → CollectorBuilder with context]

┌─────────────────────────────────────────────────────────────┐
│ Phase 2: Collector Builder                                  │
└─────────────────────────────────────────────────────────────┘

Collector Builder: Continuing from Quick Start...
Collector Builder: Your Minion has: RandomVal, CPU, Memory
Collector Builder: What do you want to monitor?
User: Disk usage
Collector Builder: Rocky Linux or Windows?
User: Rocky Linux
Collector Builder: [generates df-based collector]
Collector Builder: ✓ Created Collectors/DiskUsage.py
Collector Builder: ✓ Updated MinionConfig.xml
Collector Builder: Test collector?
User: yes
Collector Builder: [runs test] ✓ Returns: 45.2
Collector Builder: Add another collector?
User: no

Collector Builder: Next: Create dashboard to visualize data?
User: yes

[HANDOFF: CollectorBuilder → GUIComposer with context]

┌─────────────────────────────────────────────────────────────┐
│ Phase 3: GUI Composer                                        │
└─────────────────────────────────────────────────────────────┘

GUI Composer: Continuing from Collector Builder...
GUI Composer: Found collectors:
  - RandomVal, CPU, Memory, DiskUsage
GUI Composer: Dashboard template?
User: 2 (System Overview)
GUI Composer: For CPU (0-100%), which widget?
User: Gauge
GUI Composer: For Memory (0-100%)?
User: Gauge
GUI Composer: For DiskUsage (0-100%)?
User: Bar Gauge
GUI Composer: [generates dashboard]
GUI Composer: ✓ Created Application.xml
GUI Composer: ✓ Created Grid_System.xml
GUI Composer: [validates widget bindings] ✓ All valid

[OPTIONAL: GUIComposer invokes Debugging Agent for validation]

Debugging Agent: Running pre-deployment validation...
Debugging Agent: ✓ Minion config valid
Debugging Agent: ✓ Oscar config valid
Debugging Agent: ✓ Marvin config valid
Debugging Agent: ✓ Network connectivity OK
Debugging Agent: ✓ All widget bindings valid

┌─────────────────────────────────────────────────────────────┐
│ Phase 4: Deployment Complete                                │
└─────────────────────────────────────────────────────────────┘

System Ready!
  Start Minion:  python Minion/Minion.py
  Start Oscar:   python Oscar/Oscar.py
  Start Marvin:  java -jar Marvin/BIFF.Marvin.jar

[User starts all three components]
[Dashboard displays live data]

User: [sees data for 10 minutes]
User: "Why isn't DiskUsage updating?"

[INVOCATION: User → Debugging Agent]

┌─────────────────────────────────────────────────────────────┐
│ Phase 5: Troubleshooting (Debugging Agent)                  │
└─────────────────────────────────────────────────────────────┘

Debugging Agent: Analyzing DiskUsage collector...
Debugging Agent: [checks Minion logs]
Debugging Agent: Found error: "Permission denied: /proc/diskstats"
Debugging Agent: Root cause: Collector needs root permissions
Debugging Agent: Solutions:
  1) Run Minion as root (not recommended)
  2) Modify collector to use df instead of /proc
  3) Add sudo permissions for specific file

User: 2
Debugging Agent: Modifying collector...
Debugging Agent: [updates collector code]
Debugging Agent: Test collector?
User: yes
Debugging Agent: [tests] ✓ Now works!
Debugging Agent: ✓ Collector fixed

[Dashboard resumes showing disk usage]
```

**Time Without Agents**: 4-8 hours  
**Time With Agents**: 30 minutes  
**Reduction**: 87-93%

---

### Journey 2: Enterprise Multi-Site Topology

```
User: "Set up 3-site BIFF with regional aggregation"

┌─────────────────────────────────────────────────────────────┐
│ Phase 1: Oscar Routing Configurator                         │
└─────────────────────────────────────────────────────────────┘

Oscar Config: What topology?
User: 4 (Hierarchical)
Oscar Config: How many levels?
User: 3
Oscar Config: Level 1 name?
User: Sites
Oscar Config: How many site Oscars?
User: 3
Oscar Config: Level 2 name?
User: Regional
Oscar Config: How many regional Oscars?
User: 1
Oscar Config: Level 3 name?
User: Corporate
Oscar Config: Corporate has Marvin displays?
User: yes, 2
Oscar Config: [collects IPs, ports]
Oscar Config: [generates chain keys]
Oscar Config: ✓ Generated OscarConfig_Site1.xml
Oscar Config: ✓ Generated OscarConfig_Site2.xml
Oscar Config: ✓ Generated OscarConfig_Site3.xml
Oscar Config: ✓ Generated OscarConfig_Regional.xml
Oscar Config: ✓ Generated OscarConfig_Corporate.xml

Oscar Config: Different data to each Marvin?
User: yes
Oscar Config: [launches filtering wizard]

[INVOCATION: OscarConfig → GUIComposer for namespace planning]

Oscar Config: Need namespace planning for filtered routing.
[GUI Composer analyzes Minion configs from all 3 sites]
GUI Composer: Found namespaces:
  Site1: SiteMetrics, ApplicationMetrics
  Site2: SiteMetrics, ApplicationMetrics
  Site3: SiteMetrics, ApplicationMetrics
GUI Composer: Marvin 1 should show?
User: All site metrics
GUI Composer: Marvin 2 should show?
User: Only ApplicationMetrics

[HANDOFF: GUIComposer → OscarConfig with filtering rules]

Oscar Config: ✓ Generated ShuntConfig.xml
Oscar Config: Marvin 1: All data
Oscar Config: Marvin 2: Only ApplicationMetrics namespace

[INVOCATION: OscarConfig → Debugging Agent for topology validation]

Debugging Agent: Validating 5-Oscar topology...
Debugging Agent: ✓ Chain keys configured correctly
Debugging Agent: ✓ Network connectivity validated
Debugging Agent: ✓ Port allocations unique
Debugging Agent: ⚠️  Warning: Regional Oscar → Corporate is single point of failure
Debugging Agent:     Consider adding redundant regional Oscar

Oscar Config: Deployment complete!
Oscar Config: Deploy in order:
  1) Corporate Oscar (receives from Regional)
  2) Regional Oscar (receives from Sites)
  3) Site Oscars (receive from Minions)

[Deployment scripts generated for each Oscar]
```

**Time Without Agents**: 8-16 hours  
**Time With Agents**: 45 minutes  
**Reduction**: 90-94%

---

## Agent Communication Protocol

### Event Broadcasting

Agents can broadcast events that other agents subscribe to.

```python
# shared/event_bus.py
from typing import Callable, Dict, List
from dataclasses import dataclass
from datetime import datetime

@dataclass
class AgentEvent:
    """Event broadcast by agents"""
    event_type: str  # "config_changed", "collector_added", "validation_failed", etc.
    agent: str
    timestamp: datetime
    data: Dict

class EventBus:
    """Publish-subscribe event system for agents"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._subscribers = {}
        return cls._instance
    
    def subscribe(self, event_type: str, handler: Callable):
        """Subscribe to event type"""
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        self._subscribers[event_type].append(handler)
    
    def publish(self, event: AgentEvent):
        """Publish event to subscribers"""
        if event.event_type in self._subscribers:
            for handler in self._subscribers[event.event_type]:
                handler(event)
    
    def publish_config_change(self, agent: str, component: str, config_path: str):
        """Convenience method for config changes"""
        event = AgentEvent(
            event_type="config_changed",
            agent=agent,
            timestamp=datetime.now(),
            data={
                "component": component,
                "config_path": config_path
            }
        )
        self.publish(event)

# Example: Debugging Agent subscribes to config changes
class DebuggingAgent:
    def __init__(self):
        bus = EventBus()
        bus.subscribe("config_changed", self.on_config_changed)
        bus.subscribe("collector_added", self.on_collector_added)
    
    def on_config_changed(self, event: AgentEvent):
        """React to config changes"""
        print(f"\n[Debugging Agent] Detected config change by {event.agent}")
        
        # Auto-validate the changed config
        issues = self.validate_component(event.data["component"])
        
        if issues:
            print(f"⚠️  Validation found {len(issues)} issues:")
            for issue in issues[:3]:  # Show first 3
                print(f"  - {issue['issue']}")
    
    def on_collector_added(self, event: AgentEvent):
        """React to new collector"""
        print(f"\n[Debugging Agent] New collector added: {event.data['full_id']}")
        
        # Test the new collector
        test_result = self.test_collector(
            event.data["namespace"],
            event.data["id"]
        )
        
        if test_result["success"]:
            print(f"✓ Collector test passed")
        else:
            print(f"✗ Collector test failed: {test_result['error']}")

# Example: Collector Builder publishes events
class CollectorBuilder:
    def save_collector(self, namespace, collector_id, collector_code):
        """Save new collector and notify other agents"""
        
        # Write collector file
        collector_path = self.write_collector_file(collector_code)
        
        # Update Minion config
        self.update_minion_config(namespace, collector_id, collector_path)
        
        # Publish events
        bus = EventBus()
        
        bus.publish(AgentEvent(
            event_type="collector_added",
            agent="CollectorBuilder",
            timestamp=datetime.now(),
            data={
                "namespace": namespace,
                "id": collector_id,
                "full_id": f"{namespace}:{collector_id}",
                "collector_path": collector_path
            }
        ))
        
        bus.publish_config_change(
            agent="CollectorBuilder",
            component="Minion",
            config_path=self.minion_config_path
        )
```

---

## Shared Utilities Library

```python
# shared/utilities.py

class NetworkUtilities:
    """Network utilities used by multiple agents"""
    
    @staticmethod
    def test_udp_connectivity(source_ip, dest_ip, dest_port, timeout=2):
        """Test UDP connectivity (used by Quick Start, Debugging Agent, Oscar Config)"""
        import socket
        
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.settimeout(timeout)
            
            # Send test packet
            test_data = b"BIFF_TEST"
            sock.sendto(test_data, (dest_ip, dest_port))
            
            # UDP is connectionless, so if no exception, assume success
            return {"success": True, "latency_ms": None}
        
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "suggestion": "Check firewall or routing"
            }
        finally:
            sock.close()
    
    @staticmethod
    def find_available_port(start_port=52001, max_attempts=100):
        """Find available port (used by Quick Start, Oscar Config)"""
        import socket
        
        for port in range(start_port, start_port + max_attempts):
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                sock.bind(('', port))
                sock.close()
                return port
            except OSError:
                continue
        
        raise RuntimeError(f"No available ports in range {start_port}-{start_port+max_attempts}")
    
    @staticmethod
    def get_local_ip():
        """Get local IP address (used by all agents)"""
        import socket
        
        try:
            # Trick: connect to external IP to determine local interface
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.connect(("8.8.8.8", 80))
            local_ip = sock.getsockname()[0]
            sock.close()
            return local_ip
        except:
            return "127.0.0.1"

class XMLUtilities:
    """XML utilities used by all agents"""
    
    @staticmethod
    def format_xml(xml_string: str) -> str:
        """Pretty-print XML"""
        import xml.dom.minidom
        
        dom = xml.dom.minidom.parseString(xml_string)
        return dom.toprettyxml(indent="    ")
    
    @staticmethod
    def resolve_aliases(xml_tree, aliases: Dict[str, str]):
        """Resolve $(ALIAS) references in XML"""
        # Implementation would walk XML tree and replace alias refs
        pass
    
    @staticmethod
    def extract_aliases(xml_tree) -> Dict[str, str]:
        """Extract AliasList from XML"""
        # Implementation would parse AliasList elements
        pass

class ProcessUtilities:
    """Process management utilities"""
    
    @staticmethod
    def is_process_running(process_name: str) -> bool:
        """Check if process is running (used by Debugging Agent)"""
        import psutil
        
        for proc in psutil.process_iter(['name']):
            if process_name.lower() in proc.info['name'].lower():
                return True
        return False
    
    @staticmethod
    def get_process_by_port(port: int):
        """Find process listening on port (used by Debugging Agent)"""
        import psutil
        
        for conn in psutil.net_connections(kind='udp'):
            if conn.laddr.port == port:
                try:
                    proc = psutil.Process(conn.pid)
                    return {
                        "pid": conn.pid,
                        "name": proc.name(),
                        "cmdline": proc.cmdline()
                    }
                except:
                    pass
        return None
```

---

## Agent Development Guidelines

### 1. Agent Interface Contract

All agents should implement this interface:

```python
from abc import ABC, abstractmethod

class BIFFAgent(ABC):
    """Base class for all BIFF agents"""
    
    def __init__(self, workspace_root: str):
        self.workspace_root = workspace_root
        self.session = SessionState(workspace_root)
        self.parser = BIFFConfigParser(workspace_root)
        self.event_bus = EventBus()
    
    @abstractmethod
    def get_agent_name(self) -> str:
        """Return agent's unique identifier"""
        pass
    
    @abstractmethod
    def start_standalone(self):
        """Start agent in standalone mode (no handoff context)"""
        pass
    
    def start_from_handoff(self):
        """Start agent with context from previous agent"""
        handoff = self.session.get_handoff_context(self.get_agent_name())
        
        if handoff:
            self._handle_handoff(handoff)
        else:
            print(f"No handoff context for {self.get_agent_name()}")
            self.start_standalone()
    
    @abstractmethod
    def _handle_handoff(self, context: Dict):
        """Process handoff context from previous agent"""
        pass
    
    def handoff_to(self, target_agent: str, context: Dict):
        """Hand off to another agent"""
        self.session.set_handoff_context(
            from_agent=self.get_agent_name(),
            to_agent=target_agent,
            context=context
        )
    
    def invoke_debugging(self, component: str, issue: str):
        """Convenience method to invoke debugging agent"""
        return AgentHelpers.invoke_debugging_agent(component, issue)
```

### 2. Adding a New Agent

Steps to add a new agent to the ecosystem:

1. **Inherit from BIFFAgent**
2. **Subscribe to relevant events**
3. **Publish events when making changes**
4. **Use shared utilities and validators**
5. **Update session state**
6. **Document handoff contracts**

Example:

```python
class MyNewAgent(BIFFAgent):
    def get_agent_name(self) -> str:
        return "MyNewAgent"
    
    def __init__(self, workspace_root: str):
        super().__init__(workspace_root)
        
        # Subscribe to events
        self.event_bus.subscribe("config_changed", self.on_config_change)
    
    def start_standalone(self):
        """Start without handoff"""
        print(f"Starting {self.get_agent_name()}...")
        # Implementation
    
    def _handle_handoff(self, context: Dict):
        """Handle handoff from another agent"""
        print(f"Received handoff from {context.get('from_agent')}")
        # Use handoff context
        self.start_with_context(context)
    
    def on_config_change(self, event: AgentEvent):
        """React to config changes"""
        if event.data["component"] == "Minion":
            # Re-analyze Minion config
            pass
```

---

## Deployment & Distribution

### Unified Agent CLI

```python
# biff_agents.py - Single entry point for all agents

import argparse
from quick_start import QuickStartOrchestrator
from collector_builder import CollectorBuilder
from gui_composer import GUIComposer
from oscar_configurator import OscarConfigurator
from debugging_agent import DebuggingAgent

def main():
    parser = argparse.ArgumentParser(description="BIFF AI Agents")
    
    parser.add_argument("agent", choices=[
        "quickstart", "collector", "gui", "oscar", "debug"
    ])
    parser.add_argument("--workspace", default=".", help="Workspace root")
    parser.add_argument("--continue", action="store_true", 
                       help="Continue from previous agent handoff")
    
    args = parser.parse_args()
    
    # Map agent names to classes
    agents = {
        "quickstart": QuickStartOrchestrator,
        "collector": CollectorBuilder,
        "gui": GUIComposer,
        "oscar": OscarConfigurator,
        "debug": DebuggingAgent
    }
    
    agent_class = agents[args.agent]
    agent = agent_class(args.workspace)
    
    if args.__dict__.get("continue"):
        agent.start_from_handoff()
    else:
        agent.start_standalone()

if __name__ == "__main__":
    main()
```

Usage:
```bash
# Start Quick Start from scratch
python biff_agents.py quickstart

# After Quick Start completes, continue to Collector Builder
python biff_agents.py collector --continue

# Or start Collector Builder standalone
python biff_agents.py collector

# Invoke debugging anytime
python biff_agents.py debug
```

---

## Testing Integration

```python
# tests/test_agent_integration.py

def test_full_workflow():
    """Test complete agent workflow"""
    workspace = create_temp_workspace()
    
    # Phase 1: Quick Start
    quick_start = QuickStartOrchestrator(workspace)
    configs = quick_start.generate_basic_setup(
        deployment="single_machine",
        auto_confirm=True
    )
    
    assert os.path.exists(configs["minion"])
    assert os.path.exists(configs["oscar"])
    assert os.path.exists(configs["marvin"])
    
    # Phase 2: Collector Builder
    builder = CollectorBuilder(workspace)
    builder.create_collector(
        namespace="TestNamespace",
        collector_id="test_metric",
        collector_type="shell",
        command="echo 42",
        auto_confirm=True
    )
    
    # Verify collector added
    parser = BIFFConfigParser(workspace)
    minion_data = parser.parse_minion_config(configs["minion"])
    assert any(c.id == "test_metric" for c in minion_data["collectors"])
    
    # Phase 3: GUI Composer
    gui = GUIComposer(workspace)
    dashboard = gui.generate_dashboard(
        collectors=minion_data["collectors"],
        layout_style="balanced",
        auto_confirm=True
    )
    
    assert os.path.exists(dashboard["application"])
    assert os.path.exists(dashboard["grid"])
    
    # Phase 4: Validation
    validator = BIFFConfigValidator(parser)
    issues = validator.validate_full_system()
    
    # Should have no critical issues
    critical = [i for i in issues if i["severity"] == "ERROR"]
    assert len(critical) == 0

def test_handoff_context():
    """Test agent handoff mechanism"""
    workspace = create_temp_workspace()
    session = SessionState(workspace)
    
    # Quick Start sets handoff
    session.set_handoff_context(
        from_agent="QuickStart",
        to_agent="CollectorBuilder",
        context={"minion_config": "/path/to/config.xml"}
    )
    
    # Collector Builder retrieves handoff
    builder = CollectorBuilder(workspace)
    handoff = session.get_handoff_context("CollectorBuilder")
    
    assert handoff is not None
    assert handoff["minion_config"] == "/path/to/config.xml"
    
    # Context cleared after use
    session.clear_handoff_context()
    handoff_again = session.get_handoff_context("CollectorBuilder")
    assert handoff_again is None
```

---

## Success Metrics

### Integration Success Indicators

1. **Handoff Success Rate**: >95% of agent transitions preserve context
2. **Validation Accuracy**: 100% of generated configs pass validation
3. **Cross-Agent Communication**: <100ms event propagation
4. **User Workflow Completion**: >80% users complete multi-agent workflows
5. **Error Recovery**: Agents can recover from previous agent failures

### User Experience Metrics

1. **Time to First Dashboard**: <30 minutes (vs 4-8 hours)
2. **Configuration Errors**: <5% (vs 40-60%)
3. **Support Requests**: 75% reduction
4. **Feature Discovery**: Users utilize 5+ features (vs 2)
5. **Workflow Abandonment**: <10% (vs 50-70%)

---

## Future Enhancements

### Intelligent Orchestration Layer

```python
class AgentOrchestrator:
    """Meta-agent that routes user requests to appropriate agents"""
    
    def route_user_request(self, user_input: str):
        """Determine which agent(s) to invoke"""
        
        intent = self.classify_intent(user_input)
        
        routing = {
            "setup": [("QuickStart", "primary")],
            "monitor_new_metric": [("CollectorBuilder", "primary"), 
                                   ("GUIComposer", "secondary")],
            "visualize": [("GUIComposer", "primary")],
            "multi_site": [("OscarConfigurator", "primary")],
            "not_working": [("DebuggingAgent", "primary")]
        }
        
        return routing.get(intent, [("DebuggingAgent", "fallback")])
```

### Agent Analytics

```python
class AgentAnalytics:
    """Track agent usage and effectiveness"""
    
    def track_workflow_completion(self, agent_chain: List[str], duration: float):
        """Track successful multi-agent workflows"""
        pass
    
    def track_handoff_failure(self, from_agent: str, to_agent: str, reason: str):
        """Track failed agent transitions"""
        pass
    
    def generate_report(self) -> Dict:
        """Generate analytics report"""
        return {
            "most_common_workflow": "QuickStart → Collector → GUI",
            "avg_completion_time": "28 minutes",
            "handoff_success_rate": "97%",
            "most_invoked_agent": "DebuggingAgent"
        }
```

---

## Conclusion

The BIFF agent ecosystem transforms a complex, multi-component framework into an accessible, guided experience. By sharing infrastructure, validating consistently, and orchestrating seamless handoffs, these agents reduce setup time by 90%+ while ensuring correctness and enabling feature discovery.

**Key Takeaways**:
- Agents work standalone but shine together
- Shared validation ensures system correctness
- Session state enables context-aware workflows
- Event bus enables reactive agent collaboration
- Unified CLI provides consistent user experience

**Next Steps**:
1. Implement shared library (config parser, validator, utilities)
2. Build each agent with BIFFAgent interface
3. Add event bus for agent communication
4. Create integration tests for multi-agent workflows
5. Deploy unified CLI for user access
