# BIFF Quick Start Guide

Get a complete BIFF instrumentation and visualization setup running in under 5 minutes!

## What You'll Get

By the end of this guide, you'll have:

- **Oscar** (data broker) routing metrics between components
- **Minion** (collector) gathering 4-6 live system metrics every 1-2 seconds
- **Marvin** (GUI dashboard) displaying real-time gauges and text widgets
- A complete XML configuration set you can customize

**Time to Working Dashboard**: < 5 minutes  
**User Input Required**: 3 choices (deployment type, collectors, output directory)

---

## Prerequisites

### Required

- **Python 3.7+** - For Minion and Oscar
- **Java 11+** - For Marvin GUI
- **Gradle** - For building Marvin
- **Existing BIFF Installation** - Oscar, Minion, and Marvin directories

### Check Your Environment

```bash
# Python
python --version  # or python3 --version
# Should show: Python 3.7 or higher

# Java
java -version
# Should show: openjdk version "11" or higher

# Gradle
gradle --version
# Should show: Gradle 6.0 or higher
```

**Don't have these?** See [Installation](#installation) below.

---

## Quick Start (5 Steps)

### Step 1: Navigate to BIFF Agents

```bash
cd Board-Instrumentation-Framework/biff-agents
```

### Step 2: Run the Quick Start Orchestrator

```bash
python -m biff_cli quickstart
```

You'll see:

```
============================================================
  BIFF Quick Start Orchestrator
============================================================

ℹ Checking your environment for BIFF prerequisites...

✓ Python 3.12.10 detected
✓ Java 11.0.12 detected
✓ Gradle 7.2 detected
✓ BIFF installation detected at: D:\github\Board-Instrumentation-Framework
✓ Ports available: 1100, 5100, 52001

✓ Environment validation passed!
```

### Step 3: Answer the Setup Wizard

The wizard will ask 3 questions:

**1. Deployment Type**
```
Select deployment type:
  1. Development (local testing)
  2. Production (server deployment)
  3. Docker/Kubernetes (containerized)
  
Enter choice (1-3) [1]:
```
→ Press `1` and Enter for local testing

**2. Collectors**
```
Select collectors to include:
  1. RandomVal  - Random values 0-100
  2. Timer      - Millisecond timer
  3. CPU        - CPU usage percentage
  4. Memory     - Memory usage stats
  5. Network    - Network traffic bytes
  6. Storage    - Disk usage percentage

Enter numbers (comma-separated) [1,2,3]:
```
→ Press Enter to accept defaults (RandomVal, Timer, CPU)  
→ Or type: `1,2,3,4` for RandomVal, Timer, CPU, Memory

**3. Output Directory**
```
Enter output directory [quickstart_configs]:
```
→ Press Enter to use default location

### Step 4: Review Generated Files

```
✓ Configuration files generated successfully!

Generated files:
  - D:\...\biff-agents\quickstart_configs\MinionConfig.xml
  - D:\...\biff-agents\quickstart_configs\OscarConfig.xml
  - D:\...\biff-agents\quickstart_configs\Application.xml
  - D:\...\biff-agents\quickstart_configs\Tab.QuickStart.xml
  - D:\...\biff-agents\quickstart_configs\Grid.QuickStart.xml

Quick Start - Use launcher script:
  cd scripts && start_all.bat
```

### Step 5: Launch BIFF

**Windows:**
```cmd
cd scripts
start_all.bat
```

**Linux/Mac:**
```bash
cd scripts
chmod +x start_all.sh stop_all.sh  # First time only
./start_all.sh
```

You'll see three windows open (Windows) or processes start in background (Linux):

1. **Oscar** - Data broker listening on port 1100
2. **Minion** - Collector sending metrics every 1-2 seconds
3. **Marvin** - GUI dashboard (builds on first run, then opens)

**⏱️ Wait 5-10 seconds** for Marvin GUI to appear.

---

## What You'll See

### Marvin Dashboard

A JavaFX window will open showing:

**Title**: "BIFF Quick Start - QuickStart"

**Widgets** (3-column layout):

| Row 1 | | |
|-------|-------|-------|
| **Random Value** | **Timer** | **CPU Usage** |
| Steel gauge 0-100 | Steel gauge 0-10000ms | Radial gauge 0-100% |
| Updates every 1s | Updates every 2s | Updates every 1s |

| Row 2 (if selected) | | |
|-------|-------|-------|
| **Memory** | **Network** | **Disk Usage** |
| Text display | Text display | Radial gauge 0-100% |
| "X MB / Y MB" | "bytes sent/recv" | Updates every 2s |

**What's Happening:**
- Gauges animate smoothly as new data arrives
- Text fields update with formatted strings
- All widgets refresh independently based on collector frequency

### Oscar Terminal/Log

```
Oscar Data Broker v1.0
Listening on port 1100 (Minion input)
Forwarding to port 52001 (Marvin output)

[INFO] Received data from Minion namespace: QuickStart
[INFO] Forwarding to Marvin: <Data><Namespace>QuickStart</Namespace>...
```

### Minion Terminal/Log

```
Minion Data Collector v1.0
Namespace: QuickStart
Connected to Oscar at localhost:1100

[INFO] Collector randomval.value: 42
[INFO] Collector timer.value: 1523
[INFO] Collector cpu.value: 23.5
[INFO] Sent data packet to Oscar
```

---

## Understanding the Components

### Minion (Data Collector)

**Config**: `quickstart_configs/MinionConfig.xml`

```xml
<Namespace>
  <Name>QuickStart</Name>
  <DefaultFrequency>1000</DefaultFrequency>  <!-- 1 second default -->
  <TargetConnection IP="localhost" PORT="1100"/>  <!-- Oscar's port -->
  
  <Collector ID="cpu.value">
    <Executable>Collectors\CPU.py</Executable>
    <Param>GetUsage</Param>
  </Collector>
</Namespace>
```

**What It Does:**
- Runs Python scripts in `Minion/Collectors/`
- Captures stdout and sends as UDP packets
- Wraps data in XML with namespace and ID
- Sends to Oscar on port 1100

### Oscar (Data Broker)

**Config**: `quickstart_configs/OscarConfig.xml`

```xml
<Oscar>
  <IncomingMinionConnection Port="1100"/>  <!-- Listen for Minion -->
  <TargetConnection Namespace="QuickStart" IP="localhost" PORT="52001"/>  <!-- Forward to Marvin -->
</Oscar>
```

**What It Does:**
- Receives UDP packets from Minion
- Inspects XML for `<Namespace>` tag
- Routes packets to appropriate Marvin instance(s)
- Can record sessions for playback

### Marvin (GUI Dashboard)

**Config**: `quickstart_configs/Application.xml`, `Tab.QuickStart.xml`, `Grid.QuickStart.xml`

```xml
<!-- Application.xml -->
<Marvin>
  <Application Scale="auto">
    <Network Port="52001"/>  <!-- Listen for Oscar -->
    <Tabs>
      <Tab ID="Tab.QuickStart"/>
    </Tabs>
  </Application>
</Marvin>

<!-- Grid.QuickStart.xml -->
<Widget row="1" column="1" File="Gauge/GaugeRadial.xml">
  <Title>CPU Usage</Title>
  <MinionSrc Namespace="QuickStart" ID="cpu.value"/>  <!-- Binds to Minion data -->
  <MinValue>0</MinValue>
  <MaxValue>100</MaxValue>
</Widget>
```

**What It Does:**
- Listens for UDP packets on port 52001
- Parses `<MinionSrc>` bindings to match incoming data
- Updates widgets when matching namespace+ID received
- Supports 40+ widget types and CSS styling

---

## Data Flow Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                                                                         │
│  ┌──────────────────┐                                                   │
│  │ Minion           │                                                   │
│  │ Port 5100        │                                                   │
│  │                  │                                                   │
│  │ ┌──────────────┐ │                                                   │
│  │ │ RandomVal.py │ │  Runs every 1s, prints "42"                      │
│  │ └──────────────┘ │                                                   │
│  │ ┌──────────────┐ │                                                   │
│  │ │ Timer.py     │ │  Runs every 2s, prints "1523"                    │
│  │ └──────────────┘ │                                                   │
│  │ ┌──────────────┐ │                                                   │
│  │ │ CPU.py       │ │  Runs every 1s, prints "23.5"                    │
│  │ └──────────────┘ │                                                   │
│  └──────────────────┘                                                   │
│           │                                                              │
│           │ UDP Packet:                                                 │
│           │ <Data><Namespace>QuickStart</Namespace>                     │
│           │       <ID>cpu.value</ID><Value>23.5</Value></Data>          │
│           ▼                                                              │
│  ┌──────────────────┐                                                   │
│  │ Oscar            │                                                   │
│  │ Port 1100        │  Receives from Minion                             │
│  │                  │  Routes by namespace                              │
│  │                  │  Forwards to Marvin(s)                            │
│  └──────────────────┘                                                   │
│           │                                                              │
│           │ UDP Packet (same format)                                    │
│           │                                                              │
│           ▼                                                              │
│  ┌──────────────────┐                                                   │
│  │ Marvin           │                                                   │
│  │ Port 52001       │  Receives from Oscar                              │
│  │                  │  Matches <MinionSrc Namespace="QuickStart"        │
│  │  ┌────────────┐  │            ID="cpu.value"/>                       │
│  │  │ CPU Gauge  │  │  Updates widget to 23.5                           │
│  │  │   23.5 %   │  │                                                   │
│  │  └────────────┘  │                                                   │
│  └──────────────────┘                                                   │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Customization

### Add More Collectors

Edit `quickstart_configs/MinionConfig.xml`:

```xml
<Collector ID="disk.usage" Frequency="5000">
  <Executable>D:\...\Minion\Collectors\CPU.py</Executable>
  <Param>GetDiskUsage</Param>
  <Param>C:\</Param>
</Collector>
```

Available collectors in `Minion/Collectors/`:
- `RandomVal.py` - Random numbers
- `Timer.py` - Millisecond timer
- `CPU.py` - CPU stats (usage, memory, disk, processes)
- `Network.py` - Network interface stats
- `SystemInfo_Linux.py` - Linux system info
- `Docker_Stats.py` - Docker container stats
- `Prometheus.py` - Prometheus endpoint scraper
- Many more! (30+ built-in)

### Add Widgets to Dashboard

Edit `quickstart_configs/Grid.QuickStart.xml`:

```xml
<Widget row="3" column="1" Height="300" Width="400" File="LED/LED.xml">
  <Title>Status</Title>
  <MinionSrc Namespace="QuickStart" ID="service.status"/>
  <OnValue>running</OnValue>
  <OffValue>stopped</OffValue>
</Widget>
```

Available widgets in `Marvin/Widget/`:
- Gauges: `Gauge/GaugeRadial.xml`, `Gauge/GaugeSimple.xml`
- Charts: `Chart/LineChart.xml`, `Chart/BarChart.xml`
- Indicators: `LED/LED.xml`, `Indicator/Indicator.xml`
- Text: `Text/Text.xml`, `Text/DynamicText.xml`
- 40+ widget types total

### Change Update Frequency

**In Minion config** (affects collection rate):
```xml
<Collector ID="cpu.value" Frequency="500">  <!-- 500ms = 2x per second -->
```

**In Marvin widget** (affects display rate):
```xml
<Widget>
  <MinionSrc Namespace="QuickStart" ID="cpu.value" UpdateInterval="250"/>  <!-- 4x per second -->
</Widget>
```

### Use Different Ports

**Minion → Oscar:**
- Change `<TargetConnection PORT="1100"/>` in MinionConfig.xml
- Change `<IncomingMinionConnection Port="1100"/>` in OscarConfig.xml

**Oscar → Marvin:**
- Change `<TargetConnection PORT="52001"/>` in OscarConfig.xml
- Change `<Network Port="52001"/>` in Application.xml

### Multiple Namespaces

Run multiple Minion instances with different namespaces:

```bash
# Terminal 1
python Minion.py -c WebServers.xml  # Namespace: WebServers

# Terminal 2
python Minion.py -c Databases.xml   # Namespace: Databases
```

Oscar routes by namespace to appropriate Marvin tabs.

---

## Troubleshooting

### Marvin GUI Doesn't Open

**Symptoms**: No window appears after 30 seconds

**Checks**:
```bash
# 1. Verify Java
java -version
# Should be 11 or higher

# 2. Check if Marvin built successfully
ls Marvin/build/libs/BIFF.Marvin.jar
# Should exist

# 3. Check Marvin log (Linux)
cat biff-agents/logs/marvin.log
# Look for errors

# 4. Try manual launch
cd Marvin
java -jar build/libs/BIFF.Marvin.jar -a ../biff-agents/quickstart_configs/Application.xml
```

**Common Issues**:
- **Java not installed**: Install OpenJDK 11+
- **DISPLAY not set (Linux)**: `export DISPLAY=:0`
- **Port 52001 in use**: Change port in Application.xml and OscarConfig.xml

### Widgets Show "Waiting for data..."

**Symptoms**: Marvin opens but widgets don't update

**Checks**:
```bash
# 1. Is Oscar running?
# Windows: Check Oscar terminal window
# Linux: ps aux | grep Oscar

# 2. Is Minion running?
# Windows: Check Minion terminal window
# Linux: ps aux | grep Minion

# 3. Check Oscar log
# Look for "Received data from Minion" messages

# 4. Check Minion log
# Look for "Sent data packet" messages

# 5. Verify ports match
grep PORT quickstart_configs/MinionConfig.xml  # Should be 1100
grep Port quickstart_configs/OscarConfig.xml   # Should be 1100 and 52001
grep Port quickstart_configs/Application.xml    # Should be 52001
```

**Common Issues**:
- **Firewall blocking UDP**: Temporarily disable to test
- **Wrong namespace**: Check `<Namespace>` in configs matches
- **Wrong collector ID**: Check `<ID>` matches between Minion and Marvin
- **Oscar not routing**: Check `<TargetConnection Namespace="...">` in OscarConfig.xml

### Launcher Script Fails

**Windows (`start_all.bat`):**

```
[ERROR] BIFF installation not detected
```
→ Run from `biff-agents/scripts/` directory
→ Verify `Oscar/`, `Minion/`, `Marvin/` exist in parent directory

```
[ERROR] Marvin build failed
```
→ Check Java: `java -version` (should be 11+)
→ Check Gradle: `gradle --version`
→ Try manual build: `cd Marvin && gradlew build`

**Linux (`start_all.sh`):**

```
[ERROR] Python not found
```
→ Install Python 3: `sudo apt install python3`
→ Or use `python3` explicitly in script

```
Permission denied: ./start_all.sh
```
→ Make executable: `chmod +x start_all.sh stop_all.sh`

### Collectors Not Running

**Symptoms**: Minion log shows "Collector failed" or no output

**Checks**:
```bash
# Test collector manually
cd Minion
python Collectors/CPU.py GetUsage
# Should print a number

# Check file paths
cat quickstart_configs/MinionConfig.xml
# <Executable> paths should exist
```

**Common Issues**:
- **Missing Python dependencies**: Some collectors need `psutil`, `docker`, etc.
- **Wrong Python version**: Some collectors require Python 3.8+
- **File permissions (Linux)**: `chmod +x Collectors/*.py`

### High CPU Usage

**Symptoms**: 100% CPU usage, system slow

**Cause**: Collectors with frequency set too high

**Solution**:
```xml
<!-- Change from 100ms to 1000ms -->
<Collector ID="cpu.value" Frequency="1000">
```

**Best Practices**:
- Use 1000ms (1s) or higher for most collectors
- Reserve < 500ms for critical metrics only
- Limit total collectors to 10-15 per Minion

---

## Stopping BIFF

### Windows

Close each terminal window, or press `Ctrl+C` in each.

### Linux/Mac

```bash
cd biff-agents/scripts
./stop_all.sh
```

Or manually:
```bash
kill $(cat ../logs/oscar.pid) $(cat ../logs/minion.pid) $(cat ../logs/marvin.pid)
```

---

## Next Steps

### Learn More

- **User Guide**: `BIFF Instrumentation Framework User Guide.pdf` (200+ pages)
- **Collector Development**: See `Minion/ReadMe.txt`
- **Widget Customization**: Browse `Marvin/Widget/` directory
- **Examples**: `*/Demonstration/` directories

### Customize Your Setup

1. **Add more collectors**: Explore `Minion/Collectors/`
2. **Create custom widgets**: Copy and modify existing widget XML
3. **Style the dashboard**: Edit CSS in `Marvin/Widget/Modena-BIFF.css`
4. **Create multiple tabs**: Add more `<Tab>` elements in Application.xml

### Advanced Use Cases

**Remote Monitoring:**
```xml
<!-- Minion on server 192.168.1.100 -->
<TargetConnection IP="192.168.1.50" PORT="1100"/>  <!-- Oscar on .50 -->

<!-- Oscar -->
<TargetConnection Namespace="Servers" IP="192.168.1.10" PORT="52001"/>  <!-- Marvin on .10 -->
```

**Multiple Environments:**
Run multiple Marvin instances on different ports to monitor dev/staging/prod:
```bash
java -jar BIFF.Marvin.jar -a dev_dashboard.xml     # Port 52001
java -jar BIFF.Marvin.jar -a staging_dashboard.xml # Port 52002
java -jar BIFF.Marvin.jar -a prod_dashboard.xml    # Port 52003
```

**Session Recording:**
```bash
# Record for playback
python Oscar.py -c OscarConfig.xml -r session.dat

# Playback later
python Oscar.py -p session.dat
```

---

## Need Help?

### Documentation

- [IMPLEMENTATION_PLAN.md](IMPLEMENTATION_PLAN.md) - Development roadmap
- [scripts/README.md](scripts/README.md) - Launcher script details
- [docs/Day5_Summary.md](docs/Day5_Summary.md) - Implementation details

### Troubleshooting Tips

1. **Start simple**: Use RandomVal/Timer first (no dependencies)
2. **Check one component at a time**: Oscar → Minion → Marvin
3. **Use verbose logging**: Add `-v` flag to Minion/Oscar
4. **Validate configs**: Run `python -m biff_cli validate minion quickstart_configs/MinionConfig.xml`

### Common Questions

**Q: Can I use this in production?**  
A: Yes! BIFF is used by Intel for production monitoring. Use environment variables for IPs and ports in containerized deployments.

**Q: How many collectors can I run?**  
A: 50-100 collectors per Minion is typical. Use multiple Minion instances for more.

**Q: Can Marvin display data from multiple Minions?**  
A: Yes! Use different namespaces and multiple `<MinionSrc>` bindings.

**Q: Does this work with Docker?**  
A: Yes! See `Minion/Collectors/Docker_Stats.py` for container monitoring.

**Q: Can I scrape Prometheus endpoints?**  
A: Yes! Use `Minion/Collectors/Prometheus.py`.

---

## Summary

You've learned how to:

✅ Generate a complete BIFF configuration in 2 minutes  
✅ Launch all components with a single script  
✅ Monitor live system metrics in a JavaFX dashboard  
✅ Customize collectors, widgets, and layouts  
✅ Troubleshoot common issues

**Congratulations!** You're now ready to build custom instrumentation dashboards with BIFF.

For advanced features like:
- Custom collector development
- Dynamic widget layouts
- Multi-server deployments
- Session recording/playback
- Task automation (remote actions)

Consult the full User Guide and explore the `Demonstration/` directories for examples.

---

**Feedback?** Found an issue with this guide? Please open an issue or submit a PR!

**Happy Monitoring! 📊**
