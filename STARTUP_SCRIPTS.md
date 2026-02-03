# BIFF Component Startup Scripts

This directory contains intelligent startup scripts for all BIFF components that automatically handle instance management.

## Features

✅ **Automatic Instance Detection**: Identifies running instances by configuration file  
✅ **Smart Cleanup**: Stops existing instances with the same config before starting new ones  
✅ **Multi-Instance Support**: Multiple instances can run concurrently with different configs  
✅ **Cross-Platform**: Both PowerShell and Batch scripts provided  

## Quick Start

### Starting Individual Components

**Minion** (Data Collector):
```powershell
cd Minion
.\start_minion.ps1 -ConfigFile MinionConfig.xml
# OR
start_minion.bat MinionConfig.xml
```

**Oscar** (Data Broker):
```powershell
cd Oscar
.\start_oscar.ps1 -ConfigFile OscarConfig.xml -Background
# OR
start_oscar.bat OscarConfig.xml
```

**Marvin** (GUI):
```powershell
cd Marvin
.\start_marvin.ps1 -ConfigFile StarterApplication.xml -JavaArgs @("-vvvv")
# OR
start_marvin.bat StarterApplication.xml -vvvv
```

### Starting Quickstart Demo

The quickstart generates configurations in `biff-agents/biff-quickstart-test/`. To start all components:

```powershell
.\quickstart_demo.bat
```

Or individually:
```powershell
cd biff-agents
.\quickstart_start_oscar.bat    # Starts Oscar with quickstart config
.\quickstart_start_minion.bat   # Starts Minion with quickstart config
.\quickstart_start_marvin.bat   # Starts Marvin with quickstart config
```

## How It Works

### Instance Identification

Each startup script identifies running instances by matching:
1. **Process name** (python.exe for Minion/Oscar, java.exe for Marvin)
2. **Script/JAR name** (Minion.py, Oscar.py, BIFF.Marvin.jar)
3. **Configuration file path** (full absolute path)

This allows multiple instances with different configs to run simultaneously.

### Cleanup Process

When you start a component:
1. Script searches for processes matching the executable AND config file
2. If found, stops only those specific instances
3. Waits 1-2 seconds for graceful shutdown
4. Starts new instance with the same config

### Example: Multiple Instances

```powershell
# Terminal 1 - Production environment
cd Minion
.\start_minion.ps1 -ConfigFile configs\production.xml

# Terminal 2 - Testing environment (runs concurrently)
cd Minion
.\start_minion.ps1 -ConfigFile configs\testing.xml

# Both run simultaneously because configs differ
```

```powershell
# Terminal 3 - Restart production (stops only production instance)
cd Minion
.\start_minion.ps1 -ConfigFile configs\production.xml
# Testing instance continues running
```

## Script Reference

### Minion Scripts

**Location**: `Minion/`

**PowerShell**:
```powershell
.\start_minion.ps1 -ConfigFile <path> [-Args @("-v", "-other")]
```

**Batch**:
```batch
start_minion.bat <config.xml> [args]
```

**Arguments**:
- `-c <config>` - Configuration file (automatically added)
- `-v` - Verbose logging
- Additional collector-specific args

### Oscar Scripts

**Location**: `Oscar/`

**PowerShell**:
```powershell
.\start_oscar.ps1 -ConfigFile <path> [-Background] [-Verbose]
```

**Batch**:
```batch
start_oscar.bat [config.xml] [-Verbose]
```

**Arguments**:
- `-i <config>` - Configuration file (automatically added)
- `-Background` - Run detached (PowerShell only)
- `-Verbose` - Enable verbose logging
- `-NoGUI` - Disable Oscar GUI

### Marvin Scripts

**Location**: `Marvin/`

**PowerShell**:
```powershell
.\start_marvin.ps1 -ConfigFile <path> [-JavaArgs @("-vvvv", "-log", "file.html")]
```

**Batch**:
```batch
start_marvin.bat <config.xml> [java args]
```

**Java Arguments**:
- `-i <config>` - Configuration file (automatically added)
- `-vvvv` - Maximum verbosity (4 levels)
- `-log <file>` - Log to HTML file
- `-ns` - Namespace-related option

## Prerequisites

### Minion/Oscar
- Python 3.7+ in PATH
- `python` or `python3` command available

### Marvin
- Java 10+ in PATH
- `java` command available
- BIFF.Marvin.jar built in `build/libs/`

**If Java not in PATH**:
```powershell
.\setup_java.ps1     # PowerShell
# OR
setup_java.bat       # Command Prompt
```

## Troubleshooting

### "Java not found in PATH"
Run `setup_java.ps1` or `setup_java.bat` in the repository root.

### "Python not found in PATH"
Install Python 3.7+ and ensure it's added to PATH during installation.

### "Configuration file not found"
Provide absolute path or path relative to component directory:
```powershell
.\start_minion.ps1 -ConfigFile ..\biff-agents\biff-quickstart-test\MinionConfig.xml
```

### Multiple instances not stopping
Check if config path differs between invocations:
```powershell
# These are treated as DIFFERENT instances:
.\start_minion.ps1 -ConfigFile MinionConfig.xml
.\start_minion.ps1 -ConfigFile .\MinionConfig.xml
.\start_minion.ps1 -ConfigFile C:\full\path\MinionConfig.xml

# Use consistent paths (script resolves to absolute internally)
```

### Background process management (Oscar)
```powershell
# Check Oscar status
cd Oscar
.\status_oscar.ps1

# Stop Oscar
.\stop_oscar.ps1

# View logs
Get-Content OscarLog.txt -Wait -Tail 20
```

## Integration with Quickstart

The quickstart orchestrator generates configurations in `biff-agents/biff-quickstart-test/`:
- `OscarConfig.xml` - Oscar broker configuration
- `MinionConfig.xml` - Minion collector configuration  
- `ApplicationConfig.xml` - Marvin GUI configuration

The wrapper scripts in `biff-agents/` automatically reference these:
- `quickstart_start_oscar.bat` → Calls `Oscar/start_oscar.bat` with quickstart config
- `quickstart_start_minion.bat` → Calls `Minion/start_minion.bat` with quickstart config
- `quickstart_start_marvin.bat` → Calls `Marvin/start_marvin.bat` with quickstart config

## Manual Process Management

If startup scripts don't stop an instance, use manual commands:

### Find Process by Config
```powershell
# Minion/Oscar
Get-WmiObject Win32_Process -Filter "name='python.exe'" | 
    Where-Object { $_.CommandLine -like "*Minion.py*" -and $_.CommandLine -like "*MyConfig.xml*" } | 
    Select-Object ProcessId, CommandLine

# Marvin
Get-WmiObject Win32_Process -Filter "name='java.exe'" | 
    Where-Object { $_.CommandLine -like "*BIFF.Marvin.jar*" -and $_.CommandLine -like "*MyConfig.xml*" } | 
    Select-Object ProcessId, CommandLine
```

### Stop Specific Process
```powershell
Stop-Process -Id <PID> -Force
```

## See Also

- [QUICKSTART.md](../QUICKSTART.md) - Full quickstart guide
- [Oscar/SCRIPTS_README.md](../Oscar/SCRIPTS_README.md) - Oscar-specific script documentation
- [BIFF User Guide](../BIFF%20Instrumentation%20Framework%20User%20Guide.pdf) - Complete documentation
