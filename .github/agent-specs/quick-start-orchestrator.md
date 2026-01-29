# Quick Start Orchestrator Agent - Detailed Specification

## Executive Summary

The Quick Start Orchestrator is an AI-powered assistant that guides users from zero to a working BIFF installation with all three components (Minion, Oscar, Marvin) communicating successfully. It handles the most critical user friction point: getting started with a 3-tier UDP-based system where misconfigured ports or IPs result in silent failures.

**Target Time to Working System**: 5-10 minutes (vs. 1-2 hours manual)

---

## User Personas

### Primary: First-Time BIFF User

- **Background**: DevOps engineer or system administrator
- **Goal**: Evaluate BIFF for infrastructure monitoring
- **Pain Points**:
  - Doesn't understand 3-tier architecture initially
  - Unfamiliar with UDP-based communication
  - Overwhelmed by 200+ page PDF documentation
  - Unsure which ports/IPs to use
- **Success Metric**: See live data flowing from collector → visualization within 10 minutes

### Secondary: Developer Adding BIFF to Existing Stack

- **Background**: Software developer integrating BIFF into application
- **Goal**: Quick proof-of-concept with custom metrics
- **Pain Points**:
  - Needs to fit BIFF into existing port allocation
  - May run all components on one machine initially
  - Wants minimal example to extend
- **Success Metric**: Working demo they can customize

---

## System Architecture Context

### Component Dependencies

```
┌─────────────────────────────────────────────────────────┐
│ Minion (Python 3.3+)                                    │
│ - Collectors/RandomVal.py (stdlib only)                 │
│ - MinionConfig.xml                                      │
└──────────────┬──────────────────────────────────────────┘
               │ UDP Port 1100 (configurable)
               ▼
┌─────────────────────────────────────────────────────────┐
│ Oscar (Python 3.3+)                                     │
│ - OscarConfig.xml                                       │
│ - Listens: 1100, Sends: 52001+                        │
└──────────────┬──────────────────────────────────────────┘
               │ UDP Port 52001 (configurable)
               ▼
┌─────────────────────────────────────────────────────────┐
│ Marvin (Java 10+, JavaFX)                              │
│ - Dependencies/Enzo (gauge library)                     │
│ - StarterApplication.xml                                │
│ - Widget/ directory                                     │
└─────────────────────────────────────────────────────────┘
```

### Critical Success Factors

1. **Build Order**: Enzo → Marvin (Enzo must build first)
2. **IP/Port Consistency**: Same values in Minion target, Oscar incoming/target, Marvin listen
3. **Directory Structure**: Marvin JAR must be co-located with Widget/ directory
4. **UDP Connectivity**: Firewalls must allow traffic on chosen ports
5. **Working Directory**: Components must run from correct directories

---

## Agent Capabilities

### 1. Environment Detection & Validation

#### Prerequisites Check

```yaml
checks:
  java:
    command: "java -version"
    regex: "version \"([0-9]+)"
    min_version: 10
    error_message: "Java 10+ required. Install from https://adoptium.net/"
    
  python:
    command: "python --version"
    regex: "Python ([0-9]+\.[0-9]+)"
    min_version: 3.3
    error_message: "Python 3.3+ required. Install from https://www.python.org/"
    
  gradle:
    command: "gradlew.bat --version" # Windows
    fallback: "./gradlew --version"   # Linux
    regex: "Gradle ([0-9]+)"
    optional: true # Bundled gradlew is fine
    
  git:
    command: "git --version"
    optional: true # Only needed for clone
    message: "Git detected - can clone repo if needed"
```

#### Network Port Availability

```python
ports_to_check = [
    {"port": 1100, "purpose": "Oscar incoming (from Minion)", "protocol": "UDP"},
    {"port": 52001, "purpose": "Marvin listening (from Oscar)", "protocol": "UDP"},
    {"port": 52002, "purpose": "Marvin alternate (optional)", "protocol": "UDP"},
]

for port_config in ports_to_check:
    if is_port_in_use(port_config["port"], port_config["protocol"]):
        offer_alternative_port()
```

#### Directory Structure Validation

```
Expected structure:
Board-Instrumentation-Framework/
├── Marvin/
│   ├── build.gradle
│   ├── gradlew.bat (Windows) / gradlew (Linux)
│   ├── Dependencies/
│   │   └── Enzo/
│   │       └── build.gradle
│   └── Widget/
├── Minion/
│   ├── Minion.py
│   └── Collectors/
└── Oscar/
    ├── Oscar.py
    └── OscarConfig.xml
```

---

### 2. Configuration Generation

#### Deployment Mode Selection

```python
class DeploymentModeSelector:
    MODES = {
        "local": "All components on one machine (localhost)",
        "network": "Components on separate machines",
        "container": "Docker/Kubernetes deployment (environment variables)",
        "multi_deployment": "Multiple parallel deployments for comparison"
    }
    
    def select_mode(self):
        print("\n🚀 BIFF Deployment Mode\n")
        for i, (key, desc) in enumerate(self.MODES.items(), 1):
            print(f"  {i}) {desc}")
        
        choice = int(input("\nChoice: ")) - 1
        mode = list(self.MODES.keys())[choice]
        
        if mode == "container":
            return self.setup_container_deployment()
        elif mode == "multi_deployment":
            return self.setup_multi_deployment()
        else:
            return self.setup_traditional_deployment(mode)
    
    def setup_container_deployment(self):
        """Generate Docker/K8s ready configs with environment variables"""
        print("\n📦 Container Deployment\n")
        print("Generates configs using environment variables:")
        print("  • $(MinionNamespace) - Minion namespace identifier")
        print("  • $(OscarIP) - Oscar server IP")
        print("  • $(OscarPort) - Oscar listening port\n")
        
        # Generate Minion config with env vars
        minion_config = """<Minion>
    <Namespace>
        <Name>$(MinionNamespace)</Name>
        <TargetConnection IP="$(OscarIP)" PORT="$(OscarPort)"/>
        <!-- Add collectors here -->
    </Namespace>
</Minion>"""
        
        # Generate launch script
        launch_script = """#!/bin/bash
export MinionNamespace=${1:-DefaultNamespace}
export OscarIP=${2:-localhost}
export OscarPort=${3:-10020}

# Optional: CPU affinity for performance isolation
lastCore=$(($(nproc --all)-1))
nohup taskset -c $lastCore python3 Minion.py -i config.xml >/dev/null 2>&1 &"""
        
        # Generate Dockerfile
        dockerfile = """FROM python:3.9
ENV MinionNamespace=default
ENV OscarIP=oscar-service
ENV OscarPort=10020
COPY Minion/ /biff/
WORKDIR /biff
CMD ["python3", "Minion.py", "-i", "config.xml"]"""
        
        return {
            "minion_config": minion_config,
            "launch_script": launch_script,
            "dockerfile": dockerfile,
            "mode": "container"
        }
    
    def setup_multi_deployment(self):
        """Generate project structure for A/B testing or multi-environment comparison"""
        print("\n🏗️ Multi-Deployment Project\n")
        print("Compare multiple deployments side-by-side in one dashboard\n")
        
        deployments = []
        while True:
            name = input(f"Deployment {len(deployments)+1} name (or Enter to finish): ")
            if not name:
                break
            namespace = input(f"  Namespace: ")
            deployments.append({"name": name, "namespace": namespace})
        
        # Generate separate Minion config per deployment
        # Generate Marvin config with tabs per deployment
        return {
            "deployments": deployments,
            "mode": "multi_deployment"
        }
```

#### Port & IP Strategy

```python
class NetworkConfig:
    def __init__(self):
        self.deployment_mode = self.detect_deployment_mode()
        
    def detect_deployment_mode(self):
        """
        Single Machine: All components on localhost
        Multi-Machine: User specifies IPs for each component
        """
        if self.all_components_local():
            return {
                "minion_target_ip": "localhost",
                "oscar_listen_ip": "0.0.0.0",  # Listen on all interfaces
                "oscar_target_ip": "localhost",
                "marvin_listen_port": 52001,
                "oscar_minion_port": 1100,
            }
        else:
            return self.interactive_network_setup()
```

#### MinionConfig.xml Template

```xml
<?xml version="1.0"?>
<!-- Generated by Quick Start Orchestrator -->
<Minion SingleThreading="false">
    <AliasList>
        <Alias OSCAR_IP="{{oscar_ip}}"/>
        <Alias OSCAR_PORT="{{oscar_port}}"/>
        <Alias UPDATE_FREQ="1000"/>
    </AliasList>
    
    <Namespace>
        <Name>QuickStart</Name>
        <DefaultFrequency>$(UPDATE_FREQ)</DefaultFrequency>
        <TargetConnection IP="$(OSCAR_IP)" PORT="$(OSCAR_PORT)"/>
        
        <!-- Simple random value collector - no dependencies -->
        <Collector ID="demo.value1" Frequency="500">
            <Executable>Collectors\RandomVal.py</Executable>
            <Param>GetBoundedRandomValue</Param>
            <Param>0</Param>
            <Param>100</Param>
        </Collector>
        
        <Collector ID="demo.value2" Frequency="1000">
            <Executable>Collectors\RandomVal.py</Executable>
            <Param>GetBoundedRandomValue</Param>
            <Param>20</Param>
            <Param>80</Param>
        </Collector>
        
        <Collector ID="demo.percentage" Frequency="750">
            <Executable>Collectors\RandomVal.py</Executable>
            <Param>GetBoundedRandomValue</Param>
            <Param>0</Param>
            <Param>100</Param>
        </Collector>
    </Namespace>
</Minion>
```

#### OscarConfig.xml Template

```xml
<?xml version="1.0" encoding="utf-8"?>
<!-- Generated by Quick Start Orchestrator -->
<Oscar ID="QuickStartOscar">
    <IncomingMinionConnection PORT="{{minion_port}}"/>
    
    <!-- Points towards Marvin -->
    <TargetConnection IP="{{marvin_ip}}" PORT="{{marvin_port}}"/>
</Oscar>
```

#### QuickStartApp.xml Template (Marvin)

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!-- Generated by Quick Start Orchestrator -->
<Marvin>
    <AliasList>
        <Alias NS="QuickStart"/>
    </AliasList>
    
    <Application>
        <Title>BIFF Quick Start Demo</Title>
        <Width>1280</Width>
        <Height>720</Height>
        <OscarConnection IP="{{oscar_ip}}" Port="{{marvin_listen_port}}"/>
    </Application>
    
    <TabPane side="top">
        <Tab Name="Quick Start Demo">
            <Grid File="QuickStartGrid.xml"/>
        </Tab>
    </TabPane>
</Marvin>
```

#### QuickStartGrid.xml Template

```xml
<?xml version="1.0" encoding="UTF-8"?>
<MarvinExternalFile>
    <AliasList>
        <Alias NS="QuickStart"/>
    </AliasList>
    
    <Grid Align="Center" hgap="10" vgap="10">
        <!-- Row 1: Title -->
        <GridPos row="0" column="0" columnspan="3">
            <Text>
                <Title>BIFF Quick Start Demo - Live Data</Title>
                <FontSize>32</FontSize>
            </Text>
        </GridPos>
        
        <!-- Row 2: Three Gauges -->
        <GridPos row="1" column="0">
            <Gauge>
                <Title>Demo Value 1</Title>
                <Width>300</Width>
                <Height>300</Height>
                <MinionSrc Namespace="$(NS)" ID="demo.value1"/>
                <MinValue>0</MinValue>
                <MaxValue>100</MaxValue>
            </Gauge>
        </GridPos>
        
        <GridPos row="1" column="1">
            <Gauge>
                <Title>Demo Value 2</Title>
                <Width>300</Width>
                <Height>300</Height>
                <MinionSrc Namespace="$(NS)" ID="demo.value2"/>
                <MinValue>0</MinValue>
                <MaxValue>100</MaxValue>
            </Gauge>
        </GridPos>
        
        <GridPos row="1" column="2">
            <Gauge>
                <Title>Demo Percentage</Title>
                <Width>300</Width>
                <Height>300</Height>
                <MinionSrc Namespace="$(NS)" ID="demo.percentage"/>
                <MinValue>0</MinValue>
                <MaxValue>100</MaxValue>
                <Unit>%</Unit>
            </Gauge>
        </GridPos>
        
        <!-- Row 3: Instructions -->
        <GridPos row="2" column="0" columnspan="3">
            <Text>
                <Title>✓ Success! All components are communicating.</Title>
                <FontSize>18</FontSize>
                <Style>-fx-text-fill: green;</Style>
            </Text>
        </GridPos>
    </Grid>
</MarvinExternalFile>
```

---

### 3. Build Orchestration

#### Build Sequence Manager

```python
class BuildOrchestrator:
    def __init__(self, workspace_root):
        self.workspace = workspace_root
        self.build_log = []
        
    def execute(self):
        """Execute build steps in correct order"""
        steps = [
            self.build_enzo,
            self.copy_enzo_jar,
            self.build_marvin,
            self.verify_artifacts,
            self.setup_deployment_directory,
        ]
        
        for step in steps:
            result = step()
            if not result.success:
                return self.handle_build_failure(step, result)
                
        return BuildResult(success=True, artifacts=self.locate_artifacts())
    
    def build_enzo(self):
        """Build the Enzo gauge library dependency"""
        enzo_dir = os.path.join(self.workspace, "Marvin", "Dependencies", "Enzo")
        
        if platform.system() == "Windows":
            cmd = ["gradlew.bat", "build"]
        else:
            cmd = ["./gradlew", "build"]
            
        return self.run_command(cmd, cwd=enzo_dir, timeout=300)
    
    def copy_enzo_jar(self):
        """Copy built Enzo JAR to Marvin dependencies"""
        marvin_dir = os.path.join(self.workspace, "Marvin")
        
        if platform.system() == "Windows":
            cmd = ["gradlew.bat", "copyEnzoJar"]
        else:
            cmd = ["./gradlew", "copyEnzoJar"]
            
        return self.run_command(cmd, cwd=marvin_dir, timeout=60)
    
    def build_marvin(self):
        """Build the Marvin application JAR"""
        marvin_dir = os.path.join(self.workspace, "Marvin")
        
        if platform.system() == "Windows":
            cmd = ["gradlew.bat", "build"]
        else:
            cmd = ["./gradlew", "build"]
            
        return self.run_command(cmd, cwd=marvin_dir, timeout=300)
```

#### Artifact Verification

```python
class ArtifactVerifier:
    REQUIRED_ARTIFACTS = {
        "marvin_jar": {
            "path": "Marvin/build/libs/BIFF.Marvin.jar",
            "size_min": 1_000_000,  # Should be > 1MB
            "error": "Marvin JAR not found or too small"
        },
        "enzo_jar": {
            "path": "Marvin/Dependencies/Enzo-0.3.6a.jar",
            "size_min": 100_000,
            "error": "Enzo JAR not found"
        },
        "widget_dir": {
            "path": "Marvin/Widget",
            "type": "directory",
            "min_subdirs": 10,  # Should have 10+ widget type folders
            "error": "Widget directory incomplete"
        }
    }
    
    def verify(self, workspace_root):
        for name, spec in self.REQUIRED_ARTIFACTS.items():
            full_path = os.path.join(workspace_root, spec["path"])
            if not self.check_artifact(full_path, spec):
                raise BuildError(spec["error"])
```

---

### 4. Deployment Setup

#### Deployment Directory Structure

```
QuickStart_Deployment/
├── start_all.bat           # Windows launcher
├── start_all.sh            # Linux launcher
├── Minion/
│   ├── Minion.py
│   ├── QuickStartConfig.xml
│   ├── Collectors/
│   └── Helpers/
├── Oscar/
│   ├── Oscar.py
│   ├── QuickStartConfig.xml
│   ├── Helpers/
│   └── Data/
└── Marvin/
    ├── BIFF.Marvin.jar
    ├── QuickStartApp.xml
    ├── QuickStartGrid.xml
    └── Widget/
```

#### Launcher Scripts

**start_all.bat (Windows)**

```batch
@echo off
echo Starting BIFF Quick Start Demo...
echo.

REM Start Oscar
echo [1/3] Starting Oscar (data broker)...
start "Oscar" cmd /k "cd Oscar && python Oscar.py -c QuickStartConfig.xml"
timeout /t 2 /nobreak >nul

REM Start Minion
echo [2/3] Starting Minion (data collector)...
start "Minion" cmd /k "cd Minion && python Minion.py -c QuickStartConfig.xml"
timeout /t 2 /nobreak >nul

REM Start Marvin
echo [3/3] Starting Marvin (GUI)...
cd Marvin
java -jar BIFF.Marvin.jar -a QuickStartApp.xml

echo.
echo Quick Start Demo stopped. You can close the Oscar and Minion windows.
pause
```

**start_all.sh (Linux)**

```bash
#!/bin/bash
echo "Starting BIFF Quick Start Demo..."
echo

# Start Oscar in background
echo "[1/3] Starting Oscar (data broker)..."
cd Oscar
python3 Oscar.py -c QuickStartConfig.xml &
OSCAR_PID=$!
cd ..
sleep 2

# Start Minion in background
echo "[2/3] Starting Minion (data collector)..."
cd Minion
python3 Minion.py -c QuickStartConfig.xml &
MINION_PID=$!
cd ..
sleep 2

# Start Marvin in foreground
echo "[3/3] Starting Marvin (GUI)..."
cd Marvin
java -jar BIFF.Marvin.jar -a QuickStartApp.xml

# Cleanup when Marvin exits
echo
echo "Stopping background processes..."
kill $OSCAR_PID $MINION_PID 2>/dev/null
echo "Quick Start Demo stopped."
```

---

### 5. Connectivity Validation

#### UDP Test Framework

```python
class ConnectivityTester:
    def test_minion_to_oscar(self, minion_config, oscar_config):
        """Verify Minion can send to Oscar"""
        test_packet = self.create_test_packet("QuickStart", "test.connectivity", "42")
        
        # Start Oscar listener
        oscar_received = threading.Event()
        oscar_thread = threading.Thread(
            target=self.oscar_listener,
            args=(oscar_config["port"], oscar_received)
        )
        oscar_thread.start()
        
        # Send from Minion
        minion_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        minion_socket.sendto(
            test_packet.encode(),
            (oscar_config["ip"], oscar_config["port"])
        )
        
        # Wait for receipt
        if oscar_received.wait(timeout=5):
            return TestResult(success=True, message="✓ Minion → Oscar connectivity OK")
        else:
            return TestResult(
                success=False,
                message="✗ Oscar did not receive packet from Minion",
                suggestions=[
                    "Check firewall allows UDP port {port}".format(port=oscar_config["port"]),
                    "Verify IP address is correct: {ip}".format(ip=oscar_config["ip"]),
                    "Ensure Oscar is running"
                ]
            )
    
    def test_oscar_to_marvin(self, oscar_config, marvin_config):
        """Verify Oscar can send to Marvin"""
        # Similar to above, but Oscar → Marvin
        pass
    
    def test_end_to_end(self):
        """Full pipeline test: Minion → Oscar → Marvin"""
        # Send test data through full pipeline
        # Verify Marvin receives it
        pass
```

#### Firewall Guidance

```python
class FirewallHelper:
    def check_windows_firewall(self, ports):
        """Check Windows Firewall rules"""
        cmd = 'netsh advfirewall firewall show rule name=all | findstr "{port}"'
        # Parse output to see if UDP ports are allowed
        
    def generate_windows_firewall_commands(self, ports):
        """Generate PowerShell commands to allow ports"""
        commands = []
        for port in ports:
            commands.append(
                f'netsh advfirewall firewall add rule '
                f'name="BIFF {port["purpose"]}" '
                f'dir=in action=allow protocol=UDP localport={port["port"]}'
            )
        return commands
    
    def check_linux_firewall(self, ports):
        """Check iptables/firewalld"""
        # Check if firewalld is running
        # Check if iptables rules block ports
        pass
```

---

### 6. Interactive User Experience

#### Conversation Flow

```
Agent: Hello! I'll help you get BIFF up and running. Let me check your system...

[Runs prerequisite checks]

Agent: ✓ Java 11 detected
       ✓ Python 3.9 detected
       ✓ Build tools ready
       
       I can set up a working BIFF demo with all three components.
       
       Question: Will you run all components on this machine, or across multiple machines?
       1) Single machine (localhost)
       2) Multiple machines
       
User: 1

Agent: Perfect! I'll use localhost for all connections.
       
       Checking network ports...
       ⚠ Port 1100 is in use by another process
       
       Would you like to use port 1101 instead?
       
User: yes

Agent: Great! I'll configure:
       - Minion → Oscar: port 1101
       - Oscar → Marvin: port 52001
       
       Starting build process...
       
       [1/3] Building Enzo library... ⏳
       [1/3] Building Enzo library... ✓ (45 seconds)
       
       [2/3] Copying Enzo JAR... ✓ (2 seconds)
       
       [3/3] Building Marvin... ⏳
       [3/3] Building Marvin... ✓ (67 seconds)
       
Agent: Build complete! Creating deployment directory...
       
       Created: QuickStart_Deployment/
       - Configuration files generated
       - Launcher scripts created
       
       Testing connectivity...
       ✓ Port 1101 available for Oscar
       ✓ Port 52001 available for Marvin
       
Agent: Ready to launch! I've created:
       
       Windows: QuickStart_Deployment/start_all.bat
       Linux:   QuickStart_Deployment/start_all.sh
       
       Run the script to see three gauges displaying live random data.
       
       Next steps:
       1. Run the launcher script
       2. Wait for Marvin GUI to appear (~5 seconds)
       3. Look for gauges updating with live data
       
       Would you like me to:
       - Run it now
       - Explain what each component does
       - Show you how to add your own collectors
```

---

### 7. Error Handling & Troubleshooting

#### Common Failure Scenarios

**Build Failure: Enzo**

```python
class EnzoBuildFailure(BuildError):
    def diagnose(self, build_log):
        if "permission denied" in build_log.lower():
            return Diagnosis(
                cause="Gradle wrapper not executable",
                solution="Run: chmod +x Marvin/Dependencies/Enzo/gradlew",
                platform="Linux/Mac"
            )
        elif "java_home" in build_log.lower():
            return Diagnosis(
                cause="JAVA_HOME not set",
                solution="Set JAVA_HOME environment variable to JDK 10+ location"
            )
        elif "network" in build_log.lower() or "timeout" in build_log.lower():
            return Diagnosis(
                cause="Cannot download Gradle dependencies",
                solution=[
                    "Check internet connection",
                    "Configure proxy if behind corporate firewall",
                    "Try running build again (may be transient network issue)"
                ]
            )
```

**Runtime Failure: No Data in Marvin**

```python
class NoDataDiagnosis:
    def check_minion_running(self):
        """Is Minion process active?"""
        
    def check_minion_sending(self):
        """Is Minion actually sending packets?"""
        # Check Minion logs for "Sent packet" messages
        
    def check_oscar_receiving(self):
        """Is Oscar receiving from Minion?"""
        # Check Oscar GUI or logs
        
    def check_oscar_forwarding(self):
        """Is Oscar forwarding to Marvin?"""
        
    def check_marvin_listening(self):
        """Is Marvin listening on correct port?"""
        # Check Marvin About dialog
        
    def check_namespace_id_match(self):
        """Do namespace:ID values match across configs?"""
        # Parse all three configs and compare
```

#### Diagnostic Commands

```yaml
diagnostics:
  windows:
    check_port_in_use: 'netstat -ano | findstr ":{port}"'
    check_process: 'tasklist | findstr "{process}"'
    check_firewall: 'netsh advfirewall firewall show rule name=all'
    
  linux:
    check_port_in_use: 'netstat -ulnp | grep {port}'
    check_process: 'ps aux | grep {process}'
    check_firewall: 'firewall-cmd --list-all'
    capture_udp: 'tcpdump -i any -n udp port {port}'
```

---

### 8. Success Criteria & Metrics

#### Quantitative Metrics

- **Time to First Data**: < 10 minutes from agent start to seeing live gauges
- **Build Success Rate**: > 95% on clean systems with prerequisites
- **Port Conflict Resolution**: Automatic alternative port selection
- **Configuration Correctness**: 100% (namespace:ID consistency across all 3 configs)

#### Qualitative Metrics

- **User Confidence**: User understands what each component does
- **Next Steps**: User knows how to add custom collectors/widgets
- **Troubleshooting**: User can diagnose basic issues independently

#### Validation Tests

```python
class QuickStartValidator:
    def validate_deployment(self, deployment_dir):
        """Ensure generated deployment is valid"""
        checks = [
            self.validate_xml_syntax(),
            self.validate_namespace_consistency(),
            self.validate_port_configuration(),
            self.validate_file_paths(),
            self.validate_launcher_scripts(),
        ]
        return all(checks)
    
    def run_integration_test(self):
        """Actually run the deployment and verify data flow"""
        # Start all components
        # Wait for startup
        # Verify Marvin receives data within 30 seconds
        # Shutdown cleanly
```

---

## Implementation Phases

### Phase 1: MVP (Week 1-2)

- Environment detection (Java, Python)
- Single-machine localhost setup only
- Basic configuration generation (hardcoded ports)
- Marvin build orchestration
- Static deployment directory creation

**Deliverable**: Working demo on Windows localhost

### Phase 2: Enhanced (Week 3-4)

- Port conflict detection & resolution
- Multi-machine network configuration
- Interactive port/IP selection
- Connectivity validation tests
- Linux support

**Deliverable**: Production-ready for common scenarios

### Phase 3: Advanced (Week 5-6)

- Firewall diagnostics & guidance
- Build failure recovery
- Runtime diagnostics (no data troubleshooting)
- Custom configuration options
- Recording/playback setup

**Deliverable**: Handles edge cases and advanced setups

---

## Technical Requirements

### Runtime Environment

- Python 3.6+ (for agent itself)
- Access to system commands (java, python, netstat, etc.)
- File system write access
- Network socket creation permissions

### External Dependencies

```
# Python packages for agent
socket          # UDP testing
subprocess      # Running build commands
xml.etree       # Config generation/validation
pathlib         # Cross-platform paths
platform        # OS detection
psutil          # Port checking (optional, fallback to netstat)
```

### Configuration Schema

```json
{
  "deployment_name": "QuickStart",
  "workspace_root": "D:\\github\\Board-Instrumentation-Framework",
  "deployment_target": "D:\\BIFF_Demo",
  "network": {
    "topology": "single_machine|multi_machine",
    "minion": {
      "target_ip": "localhost",
      "target_port": 1100
    },
    "oscar": {
      "listen_port": 1100,
      "target_ip": "localhost",
      "target_port": 52001
    },
    "marvin": {
      "listen_port": 52001
    }
  },
  "collectors": [
    {"namespace": "QuickStart", "id": "demo.value1", "type": "RandomVal"},
    {"namespace": "QuickStart", "id": "demo.value2", "type": "RandomVal"}
  ],
  "widgets": [
    {"type": "Gauge", "minion_src": "QuickStart:demo.value1"},
    {"type": "Gauge", "minion_src": "QuickStart:demo.value2"}
  ]
}
```

---

## Testing Strategy

### Unit Tests

- Configuration generator produces valid XML
- Port availability checker works correctly
- Build orchestrator sequences commands correctly
- File path manipulation is cross-platform safe

### Integration Tests

- Full build from clean workspace
- Generated deployment actually runs
- All three components start successfully
- Data flows from Minion → Oscar → Marvin

### User Acceptance Tests

1. **Fresh Developer**: Can they get working system in < 15 minutes?
2. **Port Conflict**: Does agent handle in-use ports gracefully?
3. **Build Failure**: Are error messages actionable?
4. **Multi-Machine**: Can they set up distributed deployment?

---

## Future Enhancements

### Beyond Quick Start

- **Custom Collector Wizard**: Help create first custom collector
- **Real Metrics Integration**: Guide connecting to actual data sources (psutil, Prometheus)
- **Production Hardening**: Service installation, logging configuration
- **Docker Deployment**: Container-based quick start
- **Cloud Deployment**: AWS/Azure quick start templates

### Integration Points

- Hand off to **Collector Builder Agent** after quick start succeeds
- Hand off to **GUI Composer Agent** for custom dashboard
- Hand off to **Debugging Agent** if connectivity fails

---

## Documentation Requirements

### User-Facing

- Quick Start guide pointing to agent
- Video walkthrough of agent in action
- FAQ for common issues agent encounters

### Developer-Facing

- Agent architecture documentation
- Configuration template customization guide
- Adding new deployment topologies
- Extending diagnostics framework

---

## Success Story Example

> **Before Quick Start Agent**:
> User spends 2 hours reading PDF, manually editing 5 XML files, building components in wrong order, troubleshooting silent UDP failures, eventually gives up or asks for help on forums.

> **With Quick Start Agent**:
>
> ```
> User: "I want to try BIFF"
> Agent: "I'll set that up for you. [checks system] Building... [3 minutes] Done! Run start_all.bat"
> User: [runs script, sees live gauges after 10 seconds]
> User: "Wow, that was easy! How do I add my CPU metrics?"
> Agent: "I can help with that..." [hands off to Collector Builder Agent]
> ```

**Result**: 5-minute onboarding vs. 2-hour struggle. Dramatically improves BIFF adoption rate.
