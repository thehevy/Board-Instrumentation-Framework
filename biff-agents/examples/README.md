# BIFF Agents - Example Dashboards

This directory contains 5 complete example dashboard configurations showcasing different use cases and widget combinations for the BIFF Agents Marvin GUI Composer.

## Examples Overview

### 1. Server Monitoring Dashboard
**Config:** `01_server_monitoring_config.xml`  
**Dashboard:** `dashboards/01_server_monitoring/`

Comprehensive server health monitoring with:
- CPU usage gauges (usage, load averages)
- Memory monitoring (used, available, percentage)
- Network interface statistics (rx/tx bytes)
- Disk usage tracking (root and home partitions)
- System information (hostname, uptime, temperature)
- Control buttons (restart service, clear cache)

**Widgets Used:** Gauge, Chart, Text, Button, LED  
**Use Case:** Linux server monitoring and administration

---

### 2. Application Performance Dashboard
**Config:** `02_application_performance_config.xml`  
**Dashboard:** `dashboards/02_application_performance/`

Application metrics and performance tracking with:
- HTTP request rates and totals
- Response time percentiles (P50, P95, P99)
- Error rate monitoring (4xx, 5xx)
- Database connection pools and query times
- Cache hit rates and memory usage
- Message queue length and processing rates

**Widgets Used:** Chart, Gauge, Text  
**Use Case:** Web application APM (Application Performance Monitoring)

---

### 3. IoT Sensors Dashboard
**Config:** `03_iot_sensors_config.xml`  
**Dashboard:** `dashboards/03_iot_sensors/`

IoT device monitoring and control with:
- Temperature sensors (indoor, outdoor, server room)
- Humidity monitoring
- Motion detection indicators
- Power consumption tracking
- Device control buttons (HVAC, lights)

**Widgets Used:** Gauge, LED, Chart, Button  
**Use Case:** Smart home/building automation, environmental monitoring

---

### 4. Network Operations Dashboard
**Config:** `04_network_operations_config.xml`  
**Dashboard:** `dashboards/04_network_operations/`

Network infrastructure monitoring with:
- Interface bandwidth utilization
- Packet rates (rx/tx, errors, drops)
- TCP/UDP connection statistics
- Firewall packet counts
- DNS query rates and cache performance
- Gateway ping latency and packet loss

**Widgets Used:** Chart, Gauge, Text, LED  
**Use Case:** Network operations center (NOC), ISP monitoring

---

### 5. Container & Microservices Dashboard
**Config:** `05_containers_config.xml`  
**Dashboard:** `dashboards/05_containers/`

Docker container monitoring and orchestration with:
- Container CPU and memory usage per service
- Container network throughput
- Container status indicators
- Container control buttons (restart, scale up/down)

**Widgets Used:** Gauge, Chart, LED, Button  
**Use Case:** Microservices architecture, container orchestration

---

## Usage

### Generate All Examples
```bash
python examples/generate_examples.py
```

This will create all 5 example dashboards in the `examples/dashboards/` directory.

### Generate Individual Examples
You can also use the composers directly:

```bash
# Using CLI
python -m biff_agents_marvin compose monitoring -c examples/01_server_monitoring_config.xml -o my_dashboard

# Using Python
from biff_agents_marvin.composers.monitoring_composer import MonitoringDashboardComposer
composer = MonitoringDashboardComposer('examples/01_server_monitoring_config.xml')
composer.generate_dashboard('my_dashboard')
```

### Deploy to Marvin

1. **Copy dashboard files:**
   ```bash
   cp -r examples/dashboards/01_server_monitoring /path/to/marvin/workspace/
   ```

2. **Update Oscar connection (if needed):**
   Edit `App.Config.xml` and update the IP/Port:
   ```xml
   <OscarConnection IP="your-oscar-ip" Port="5100"/>
   ```

3. **Launch Marvin:**
   ```bash
   cd /path/to/marvin/workspace/01_server_monitoring
   java -jar ../../BIFF.Marvin.jar -i App.Config.xml
   ```

---

## Customization

### Modify Widget Layouts
Each generated dashboard can be customized by editing the XML files:

- **App.Config.xml** - Main application configuration, tab structure
- **Tab.*.xml** - Individual tab layouts with widget positions

### Adjust Data Sources
Modify the Minion config files to:
- Change collector frequencies
- Add/remove metrics
- Update collector parameters
- Configure actors for control buttons

### Widget Positioning
Widget positions use a grid system:
```xml
<Widget row="0" column="0" rowSpan="2" columnSpan="2">
```
- `row/column`: Starting position (0-indexed)
- `rowSpan/columnSpan`: Widget size

---

## Widget Types Reference

| Widget | Description | Best For |
|--------|-------------|----------|
| **Gauge** | Circular/radial display with zones | CPU, memory, percentages |
| **Chart** | Time-series line chart | Trends, throughput, rates |
| **LED** | Status indicator with conditions | Boolean states, alerts |
| **Button** | Interactive control | Actions, task execution |
| **Text** | Multi-line text display | Labels, multiple metrics |
| **Memory Bar** | Horizontal bar with zones | Memory usage visualization |
| **Network Chart** | Optimized for throughput | Network bandwidth, I/O |
| **System Info** | Multi-source text panel | System details, metadata |

---

## Configuration Patterns

### Memory Zones (Good/Warning/Critical)
```xml
<Zones>
    <Zone Color="Green" Begin="0" End="70"/>    <!-- 0-70% Good -->
    <Zone Color="Yellow" Begin="70" End="90"/>  <!-- 70-90% Warning -->
    <Zone Color="Red" Begin="90" End="100"/>    <!-- 90-100% Critical -->
</Zones>
```

### LED Conditions
```xml
<OnCondition>&gt;90</OnCondition>  <!-- Trigger when > 90 -->
<Color>Red</Color>
```

### Button Tasks (Minion Actor)
```xml
<Task Type="MinionTaskLauncher">
    <Namespace>ServerMonitoring</Namespace>
    <ID>restart_service</ID>
    <Param>force=true</Param>
</Task>
```

### Chart History Size
```xml
<History>100</History>  <!-- Keep last 100 data points -->
```

---

## Requirements

### Minion Side
- Minion collectors configured for your environment
- Appropriate permissions for system metrics (may need sudo for some collectors)
- Network connectivity to Oscar

### Marvin Side
- Java 10+ installed
- BIFF.Marvin.jar built
- Widget XML files in Widget/ directory
- Network connectivity to Oscar

### Oscar Side (Optional)
- Oscar running and configured
- Port 1100 listening for Minion data
- Forwarding to Marvin port(s)

---

## Troubleshooting

### No Data Appearing
1. Check Minion is running: `python Minion.py -c config.xml -v`
2. Verify Oscar connection in App.Config.xml
3. Check collector executable paths in Minion config
4. Review Marvin console for connection status

### Widgets Not Displaying
1. Ensure Widget/ directory exists in Marvin workspace
2. Check widget file paths in Tab.*.xml
3. Verify namespace and ID match Minion config

### Permission Errors
Some collectors require elevated permissions:
```bash
sudo python Minion.py -c config.xml
```

---

## Next Steps

- **Customize layouts** - Adjust widget positions and sizes
- **Add more collectors** - Expand metrics collection
- **Create actors** - Enable interactive control
- **Combine examples** - Mix widgets from different examples
- **Production deployment** - Set up auto-start and monitoring

For more information, see the [BIFF User Guide](../../docs/) or run:
```bash
python -m biff_agents_marvin --help
```
