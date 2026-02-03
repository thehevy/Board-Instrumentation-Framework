# BIFF Deployment Package

**Version**: 1.0.0  
**Build Date**: 20260203  
**Components**: Marvin (GUI), Oscar (Data Broker), Minion (Data Collector)

## Quick Start

### 1. Prerequisites

**Java 10+** (for Marvin):
- Download: https://adoptium.net/
- Verify: `java -version`
- If not in PATH, run: `setup_java.ps1` or `setup_java.bat`

**Python 3.7+** (for Oscar and Minion):
- Download: https://www.python.org/downloads/
- Verify: `python --version`

### 2. Start Components

**Option A: Start GUI and Broker Together**
```powershell
.\start_all.ps1
# OR
start_all.bat
```

**Option B: Start Components Individually**
```powershell
# Start Oscar (data broker) in background
cd Oscar
.\start_oscar.ps1 -ConfigFile ..\Configs\OscarConfig.xml -Background

# Start Marvin (GUI) in foreground
cd Marvin
.\start_marvin.ps1 -ConfigFile ..\Configs\MarvinConfig.xml

# Start Minion (collector) - typically on data source systems
cd Minion
.\start_minion.ps1 -ConfigFile ..\Configs\MinionConfig.xml
```

### 3. Verify Operation

1. **Oscar Status**: `cd Oscar; .\status_oscar.ps1`
2. **Marvin**: GUI window should appear
3. **Data Flow**: Widgets in Marvin should display live data from Minion

## Network Configuration

### Default Ports

| Component | Port  | Direction | Purpose |
|-----------|-------|-----------|---------|
| Oscar     | 1100  | Incoming  | Receives data from Minions |
| Marvin    | 52001 | Incoming  | Receives data from Oscar |

### Network Flow

```
Minion → UDP:1100 → Oscar → UDP:52001 → Marvin
```

See complete documentation in `Documentation/` directory.

## Support

**Documentation**: See `Documentation/` directory  
**Project**: https://github.com/intel/Board-Instrumentation-Framework  
**User Guide**: `Documentation/BIFF Instrumentation Framework User Guide.pdf`  

## License

See `license.txt`

---

**Package Information**  
Version: 1.0.0  
Build: 20260203  
Built with BIFF Package Builder
