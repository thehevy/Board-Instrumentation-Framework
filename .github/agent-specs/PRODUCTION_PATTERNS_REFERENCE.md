# BIFF Production Patterns - Complete Reference

**Last Updated**: January 2026  
**Sources**: 4 real-world Intel deployments (2022-2023)

---

## Pattern Categories

1. [Configuration Patterns](#configuration-patterns) (Patterns 1-5)
2. [Data Collection Patterns](#data-collection-patterns) (Patterns 6-10)
3. [Visualization Patterns](#visualization-patterns) (Patterns 11-15)
4. [Deployment Patterns](#deployment-patterns) (Patterns 16-21)

---

## Configuration Patterns

### Pattern 1: ExternalFile Templates

**Source**: Intel Vision Demo 2023  
**Use Case**: Reusable collector configurations with parameters

```xml
<!-- Template: test_results.xml -->
<MarvinExternalFile>
    <Collector ID="port.$(PORT_NUM).test.result">
        <Executable>Collectors\FileCollector.py</Executable>
        <Param>ReadValue</Param>
        <Param>test_results_$(PORT_NUM).txt</Param>
    </Collector>
</MarvinExternalFile>

<!-- Usage: Instantiate template 5 times -->
<ExternalFile PORT_NUM="1">test_results.xml</ExternalFile>
<ExternalFile PORT_NUM="2">test_results.xml</ExternalFile>
<ExternalFile PORT_NUM="3">test_results.xml</ExternalFile>
<ExternalFile PORT_NUM="4">test_results.xml</ExternalFile>
<ExternalFile PORT_NUM="5">test_results.xml</ExternalFile>
```

**Benefits**:

- DRY principle for repeated configurations
- Easy to add/remove instances
- Centralized template updates

**Agent Support**: Collector Builder generates templates

---

### Pattern 2: Multi-Level Aliases

**Source**: Intel Vision Demo 2023  
**Use Case**: Design system with colors, fonts, calculations

```xml
<!-- DefinitionFiles/colors.xml -->
<AliasList>
    <Alias ColorBackground="#1a1a1a"/>
    <Alias ColorPrimary="#00ff00"/>
    <Alias ColorDanger="#ff0000"/>
    <Alias ColorWarning="#ffaa00"/>
</AliasList>

<!-- DefinitionFiles/calculations.xml -->
<AliasList>
    <Alias BytesPerSec2MBPS="0.00000762939"/>
    <Alias MsToSec="0.001"/>
</AliasList>

<!-- Main config imports both -->
<AliasList>
    <Import>DefinitionFiles/colors.xml</Import>
    <Import>DefinitionFiles/calculations.xml</Import>
    <Alias NUM_PORTS="5"/>
</AliasList>

<!-- Usage -->
<Style>-fx-background-color: $(ColorBackground); -fx-text-fill: $(ColorPrimary);</Style>
<Normalize>$(BytesPerSec2MBPS)</Normalize>
```

**Benefits**:

- Consistent branding across dashboards
- Centralized constant management
- Team-shared design tokens

**Agent Support**: GUI Composer generates design system files

---

### Pattern 3: Modifier Normalization

**Source**: Intel Vision Demo 2023  
**Use Case**: Unit conversions (bytes→MB, ms→sec)

```xml
<Modifier ID="netdev.tx.bytes">
    <Normalize>0.00000762939</Normalize>  <!-- Bytes/sec → Mbps -->
</Modifier>

<Modifier ID="latency.ms">
    <Normalize>0.001</Normalize>  <!-- ms → seconds -->
    <Precision>3</Precision>
</Modifier>
```

**Benefits**:

- Display-friendly units
- Consistent across widgets
- No collector changes needed

**Agent Support**: Collector Builder adds modifiers when creating collectors

---

### Pattern 4: Environment Variables

**Source**: SPR/IPU Demo 2022  
**Use Case**: Docker/Kubernetes deployments, CI/CD pipelines

```xml
<!-- MinionConfig.xml uses environment variables -->
<Namespace>
    <Name>$(MinionNamespace)</Name>
    <TargetConnection IP="$(OscarIP)" PORT="$(OscarPort)"/>
</Namespace>
```

```bash
# launchMinion.sh sets variables
export MinionNamespace=production-east
export OscarIP=10.0.0.5
export OscarPort=10020

python3 Minion.py -i MinionConfig.xml
```

**Benefits**:

- Same config across environments
- Secrets not in Git
- Container-ready
- CI/CD friendly

**Agent Support**: Quick Start generates environment-based configs

---

### Pattern 5: Regex Modifiers

**Source**: SPR/IPU Demo 2022  
**Use Case**: Bulk transformations for pattern-matching metrics

```xml
<!-- Single modifier applies to ALL percentile metrics -->
<Modifier ID="P(.*)">
    <Precision>2</Precision>
</Modifier>
<!-- Matches: P50, P90, P95, P99, P999, etc. -->

<!-- Apply to all CPU core metrics -->
<Modifier ID="cpu_(.*)_usage">
    <Precision>1</Precision>
</Modifier>
<!-- Matches: cpu_0_usage, cpu_1_usage, ..., cpu_127_usage -->

<!-- Apply to all network queues -->
<Modifier ID="*_queue_*">
    <Normalize>0.000000001</Normalize>  <!-- bytes → GB -->
</Modifier>
<!-- Matches: tx_queue_0, rx_queue_5, etc. -->
```

**Benefits**:

- One modifier → hundreds of metrics
- Easy to maintain
- Scales to large systems

**Agent Support**: Collector Builder creates bulk modifiers

---

## Data Collection Patterns

### Pattern 6: DynamicCollector File Watchers

**Source**: Intel Vision Demo 2023  
**Use Case**: Zero-instrumentation monitoring (read existing files)

```xml
<DynamicCollector>
    <File>test_parameters.log</File>
    <Frequency>2000</Frequency>
</DynamicCollector>
```

**File Format** (test_parameters.log):

```
<Oscar>
    <Namespace>test.results</Namespace>
    <ID>throughput.mbps</ID>
    <Value>1234.56</Value>
</Oscar>
<Oscar>
    <Namespace>test.results</Namespace>
    <ID>latency.ms</ID>
    <Value>15.2</Value>
</Oscar>
```

**Benefits**:

- No code changes to monitored app
- App writes metrics to file
- Minion reads and transmits
- Decoupled monitoring

**Agent Support**: Collector Builder generates file watcher configs

---

### Pattern 7: Aggregate Collectors with Operators

**Source**: Intel Vision Demo 2023  
**Use Case**: Sum metrics across multiple sources

```xml
<Collector ID="total.throughput">
    <Operator>Addition</Operator>
    <Repeat Count="5">
        <CollectorID>port.#.throughput</CollectorID>
    </Repeat>
</Collector>
<!-- Sums: port.1.throughput + port.2.throughput + ... + port.5.throughput -->

<Collector ID="average.latency">
    <Operator>Average</Operator>
    <CollectorID>node1.latency</CollectorID>
    <CollectorID>node2.latency</CollectorID>
    <CollectorID>node3.latency</CollectorID>
</Collector>
```

**Supported Operators**: Addition, Subtraction, Multiplication, Division, Average, Min, Max

**Benefits**:

- Derived metrics without code
- Real-time aggregation
- Multi-instance totals

**Agent Support**: Collector Builder offers aggregation wizard

---

### Pattern 8: Plugin Entry Points

**Source**: Intel Vision Demo 2023, SPR/IPU Demo 2022  
**Use Case**: Multiple collectors from single Python script

```python
# scripts/cpu_metrics.py

def get_usage():
    \"\"\"Return overall CPU usage percentage\"\"\"
    return str(psutil.cpu_percent())

def get_frequency():
    \"\"\"Return current CPU frequency in MHz\"\"\"
    freq = psutil.cpu_freq()
    return str(freq.current)

def get_core_count():
    \"\"\"Return number of CPU cores\"\"\"
    return str(psutil.cpu_count())
```

```xml
<!-- Call different functions from same script -->
<Collector ID="cpu.usage">
    <Plugin>scripts/cpu_metrics.py</Plugin>
    <EntryPoint>get_usage</EntryPoint>
    <Frequency>1000</Frequency>
</Collector>

<Collector ID="cpu.frequency">
    <Plugin>scripts/cpu_metrics.py</Plugin>
    <EntryPoint>get_frequency</EntryPoint>
    <Frequency>5000</Frequency>
</Collector>

<Collector ID="cpu.cores">
    <Plugin>scripts/cpu_metrics.py</Plugin>
    <EntryPoint>get_core_count</EntryPoint>
    <Frequency>60000</Frequency>
</Collector>
```

**Benefits**:

- Code organization (related metrics together)
- Shared dependencies
- Reduced file count

**Agent Support**: Collector Builder generates plugin-based collectors

---

### Pattern 9: Actor Pattern

**Source**: SPR/IPU Demo 2022  
**Use Case**: Remote command execution from Marvin GUI

```xml
<!-- Minion: Define Actor -->
<Actor ID="RestartService">
    <Executable>systemctl restart myapp.service</Executable>
</Actor>

<Actor ID="ClearLogs">
    <Executable>scripts/clearLogs.sh</Executable>
    <Param>/var/log/myapp</Param>
</Actor>

<Actor ID="ScaleDeployment">
    <Executable>scripts/scaleK8s.sh</Executable>
    <!-- Parameters passed from Marvin -->
</Actor>
```

```xml
<!-- Marvin: Trigger Actor with button -->
<Widget File="Button.xml" Task="Execute_RestartService">
    <Title>Restart Service</Title>
</Widget>

<TaskList ID="Execute_RestartService">
    <TaskItem Type="Minion">
        <Actor Namespace="production-cluster" ID="RestartService" />
    </TaskItem>
</TaskList>

<!-- Actor with parameters from prompt -->
<Prompt ID="NumInstances" Type="InputBox">
    <Title>Number of Instances</Title>
</Prompt>

<TaskList ID="Execute_ScaleDeployment">
    <TaskItem Type="Minion">
        <Actor Namespace="k8s-controller" ID="ScaleDeployment" />
        <Param>@NumInstances</Param>  <!-- Insert prompt result -->
    </TaskItem>
</TaskList>
```

**Benefits**:

- Remote orchestration
- GUI-driven automation
- Parameter passing from dashboard
- Operator-friendly controls

**Agent Support**: Collector Builder creates Actors, GUI Composer creates trigger buttons

---

### Pattern 10: CPU Affinity

**Source**: SPR/IPU Demo 2022  
**Use Case**: Performance isolation in benchmarking

```bash
#!/bin/bash
# launchMinion.sh

# Pin Minion to last CPU core to avoid interfering with workload
lastCore=$(($(nproc --all)-1))

nohup taskset -c $lastCore python3 Minion.py -i $1 >/dev/null 2>&1 &
```

**Benefits**:

- Monitoring doesn't affect measured workload
- Consistent observer overhead
- Accurate performance measurements
- Essential for benchmarks

**Agent Support**: Quick Start generates performance-isolated launcher scripts

---

## Visualization Patterns

### Pattern 11: GridMacro for Reusable Widget Templates

**Source**: Intel Vision Demo 2023  
**Use Case**: Repeated widget layouts with variations

```xml
<!-- Define reusable template -->
<GridMacro Name="NetworkPortPanel">
    <Grid>
        <GridPos row="0" column="0">
            <Gauge>
                <Title>Port $(PORT_NUM) TX</Title>
                <MinionSrc Namespace="network" ID="port.$(PORT_NUM).tx.mbps"/>
                <MinValue>0</MinValue>
                <MaxValue>$(MAX_BANDWIDTH)</MaxValue>
            </Gauge>
        </GridPos>
        <GridPos row="1" column="0">
            <Gauge>
                <Title>Port $(PORT_NUM) RX</Title>
                <MinionSrc Namespace="network" ID="port.$(PORT_NUM).rx.mbps"/>
                <MinValue>0</MinValue>
                <MaxValue>$(MAX_BANDWIDTH)</MaxValue>
            </Gauge>
        </GridPos>
    </Grid>
</GridMacro>

<!-- Instantiate template with different parameters -->
<InvokeGridMacro MacroName="NetworkPortPanel" PORT_NUM="1" MAX_BANDWIDTH="10000"/>
<InvokeGridMacro MacroName="NetworkPortPanel" PORT_NUM="2" MAX_BANDWIDTH="10000"/>
<InvokeGridMacro MacroName="NetworkPortPanel" PORT_NUM="3" MAX_BANDWIDTH="10000"/>
```

**Benefits**:

- DRY for widget layouts
- Easy to add/remove instances
- Consistent styling
- Parameter variations

**Agent Support**: GUI Composer generates GridMacro definitions

---

### Pattern 12: DynamicGrid

**Source**: Intel Vision Demo 2023, Intel Vision 2022  
**Use Case**: Auto-adjust widget count based on data

```xml
<DynamicGrid>
    <MinionSrc Namespace="discovery" ID="server.count"/>
    <GenerateWidget>
        <Gauge>
            <Title>Server #</Title>
            <MinionSrc Namespace="cluster" ID="server.#.cpu"/>
        </Gauge>
    </GenerateWidget>
</DynamicGrid>
```

**Behavior**:

- `server.count` changes from 3 → 5
- Dashboard automatically adds 2 more gauge widgets
- `#` replaced with 1, 2, 3, 4, 5

**Benefits**:

- Auto-scaling dashboards
- Dynamic infrastructure monitoring
- No manual config updates

**Agent Support**: GUI Composer generates DynamicGrid configs

---

### Pattern 13: StyleOverride Themes

**Source**: Intel Vision Demo 2023  
**Use Case**: Consistent branding and dark/light modes

```xml
<!-- Define theme -->
<StyleOverride ID="IntelTheme">
    <Style>
        -fx-background-color: #0071c5;
        -fx-text-fill: white;
        -fx-font-family: "Intel Clear";
    </Style>
</StyleOverride>

<!-- Apply to application -->
<Application StyleOverride="IntelTheme">
    ...
</Application>

<!-- Override per widget -->
<Gauge StyleOverride="HighlightStyle">
    ...
</Gauge>
```

**Benefits**:

- Consistent branding
- Easy theme switching
- Centralized style management

**Agent Support**: GUI Composer applies themes

---

### Pattern 14: Multi-Deployment Comparison

**Source**: SPR/IPU Demo 2022, Intel Vision 2022  
**Use Case**: A/B testing, multi-region monitoring

```xml
<Marvin>
    <Application Scale="auto">
        <Tabs>
            <Tab ID="Tab.Baseline" />
            <Tab ID="Tab.Optimized" />
            <Tab ID="Tab.Production" />
        </Tabs>
    </Application>
    
    <!-- Each tab shows different deployment -->
    <Tab ID="Tab.Baseline" TabTitle="Baseline (Bare Metal)" 
         File="Tab.Deployment.xml" 
         Namespace="baseline-metrics" 
         Deployment="baseline"/>
    
    <Tab ID="Tab.Optimized" TabTitle="Optimized (K8s + IPU)" 
         File="Tab.Deployment.xml" 
         Namespace="optimized-metrics" 
         Deployment="optimized"/>
    
    <Tab ID="Tab.Production" TabTitle="Production (East Region)" 
         File="Tab.Deployment.xml" 
         Namespace="production-east" 
         Deployment="production"/>
</Marvin>
```

**Benefits**:

- Side-by-side comparison
- Same dashboard for multiple environments
- A/B testing visualization
- Multi-region monitoring

**Agent Support**: GUI Composer generates multi-deployment dashboards

---

### Pattern 15: MarvinAutoConnect

**Source**: Intel Vision 2022  
**Use Case**: Zero-configuration Oscar discovery

```xml
<Application AutoConnect="true">
    <!-- Marvin discovers Oscar via UDP broadcast -->
</Application>
```

**Benefits**:

- No IP configuration needed
- Works across network changes
- Plug-and-play setup

**Agent Support**: Quick Start offers AutoConnect mode

---

## Deployment Patterns

### Pattern 16: Container Deployment

**Source**: SPR/IPU Demo 2022  
**Use Case**: Docker, Kubernetes, cloud deployments

**Dockerfile**:

```dockerfile
FROM python:3.9

ENV MinionNamespace=default
ENV OscarIP=oscar-service
ENV OscarPort=10020

COPY Minion/ /biff/
WORKDIR /biff

CMD ["python3", "Minion.py", "-i", "config.xml"]
```

**Kubernetes DaemonSet**:

```yaml
apiVersion: apps/v1
kind: DaemonSet
metadata:
  name: biff-minion
spec:
  selector:
    matchLabels:
      app: biff-minion
  template:
    spec:
      hostNetwork: true
      containers:
      - name: minion
        image: biff-minion:latest
        env:
        - name: MinionNamespace
          valueFrom:
            fieldRef:
              fieldPath: spec.nodeName  # Use node name as namespace
        - name: OscarIP
          value: "oscar-service.monitoring.svc.cluster.local"
        - name: OscarPort
          value: "10020"
```

**Benefits**:

- Cloud-native deployments
- Auto-scaling monitoring
- Infrastructure as code

**Agent Support**: Quick Start generates container configs

---

### Pattern 17: Infrastructure Automation

**Source**: SPR/IPU Demo 2022  
**Use Case**: Ansible/Terraform integration

**Ansible Playbook**:

```yaml
---
- name: Deploy BIFF Monitoring
  hosts: monitoring_servers
  tasks:
    - name: Copy BIFF files
      copy:
        src: Minion/
        dest: /opt/biff/
    
    - name: Start Minion
      shell: |
        cd /opt/biff
        export MinionNamespace={{ inventory_hostname }}
        export OscarIP={{ oscar_server }}
        export OscarPort=10020
        ./launchMinion.sh config.xml
```

**Benefits**:

- Automated deployment
- Configuration management
- Consistent across fleet

**Agent Support**: Quick Start generates Ansible templates

---

### Pattern 18: Launch Scripts with Affinity

**Source**: SPR/IPU Demo 2022  
**Use Case**: Production deployment with process management

```bash
#!/bin/bash
# launchMinion.sh

ConfigFile=$1
export MinionNamespace=$2
export OscarIP=$3
export OscarPort=$4

# Kill any existing Minion
pkill -f Minion.py

# CPU affinity for performance isolation
lastCore=$(($(nproc --all)-1))

# Launch with nohup for background execution
nohup taskset -c $lastCore python3 Minion.py -i $ConfigFile >/dev/null 2>&1 &

echo "Minion launched on core $lastCore"
echo "PID: $(pgrep -f Minion.py)"
```

**Usage**:

```bash
./launchMinion.sh config.xml production-east 10.0.0.5 10020
```

**Benefits**:

- Process lifecycle management
- CPU affinity for benchmarks
- Environment variable injection
- Production-ready

**Agent Support**: Quick Start generates production launch scripts

---

### Pattern 19: Multi-Namespace Architecture

**Source**: All deployments  
**Use Case**: Logical separation of metrics

```
Single Oscar routes multiple namespaces:

Minion (namespace: production-web) → \
Minion (namespace: production-db)  → → Oscar → Marvin
Minion (namespace: production-api) → /

Marvin dashboard shows tabs:
- Tab 1: Web Servers (namespace: production-web)
- Tab 2: Databases (namespace: production-db)
- Tab 3: API Servers (namespace: production-api)
```

**Benefits**:

- Logical grouping
- Access control
- Multi-tenant monitoring

**Agent Support**: All agents support namespaces

---

### Pattern 20: Prometheus Integration

**Source**: Production collectors  
**Use Case**: Pull data from existing Prometheus endpoints

```xml
<Collector ID="prometheus.cpu.usage">
    <Executable>Collectors\Prometheus.py</Executable>
    <Param>Query</Param>
    <Param>http://prometheus:9090</Param>
    <Param>node_cpu_seconds_total</Param>
</Collector>
```

**Benefits**:

- Leverage existing instrumentation
- No duplicate metric collection
- Unified visualization

**Agent Support**: Collector Builder offers Prometheus template

---

### Pattern 21: Tab Parameters

**Source**: Intel Vision 2022  
**Use Case**: Reusable tab definitions with variations

```xml
<!-- Define reusable tab -->
<Tab ID="Tab.Server" TabTitle="Server: $(ServerName)" 
     File="Tab.ServerMetrics.xml" 
     ServerName="?" 
     ServerNamespace="?"/>

<!-- Instantiate with different parameters -->
<InvokeTab TabID="Tab.Server" ServerName="Web01" ServerNamespace="web.server1"/>
<InvokeTab TabID="Tab.Server" ServerName="Web02" ServerNamespace="web.server2"/>
<InvokeTab TabID="Tab.Server" ServerName="DB01" ServerNamespace="db.server1"/>
```

**Benefits**:

- DRY for tab layouts
- Consistent multi-server dashboards
- Easy to add servers

**Agent Support**: GUI Composer generates parameterized tabs

---

## Pattern Selection Guide

### By Use Case

| Use Case | Recommended Patterns |
|----------|---------------------|
| **Container Deployment** | Pattern 4 (Environment Variables), Pattern 16 (Container Configs) |
| **High-Scale Monitoring** | Pattern 5 (Regex Modifiers), Pattern 12 (DynamicGrid) |
| **Zero-Instrumentation** | Pattern 6 (File Watchers) |
| **Remote Control** | Pattern 9 (Actors) |
| **Performance Testing** | Pattern 10 (CPU Affinity), Pattern 14 (Multi-Deployment) |
| **Multi-Environment** | Pattern 14 (Multi-Deployment), Pattern 19 (Multi-Namespace) |
| **Production Deployment** | Pattern 4, 16, 17, 18 (Full deployment stack) |

### By Complexity

| Level | Patterns |
|-------|----------|
| **Beginner** | 1, 3, 6, 15, 19 |
| **Intermediate** | 2, 7, 8, 11, 13, 21 |
| **Advanced** | 4, 5, 9, 10, 12, 14, 16, 17, 18, 20 |

---

## References

- **Pattern Sources**: 4 real-world Intel deployments (2022-2023)
- **Validation**: All patterns production-proven in HPC environments
- **Documentation**: BIFF Instrumentation Framework User Guide (200+ pages)
- **Agent Integration**: All patterns supported by BIFF agent specifications

**For Implementation**: See individual agent specifications for code generators and wizards.
