# Oscar Management Scripts for Windows

## Overview

This directory contains automated management scripts for running Oscar (BIFF Data Broker) on Windows. These scripts provide background process management, automatic Python detection, and status monitoring.

## Quick Start

```powershell
# Start Oscar in background
.\start_oscar.bat

# Check Oscar status
.\status_oscar.bat

# Stop Oscar
.\stop_oscar.bat
```

## Scripts

### start_oscar.bat / start_oscar.ps1
Starts Oscar in background mode with automatic configuration.

**Features:**
- Automatic Python detection (searches 8 common installation paths)
- Background process execution (non-blocking terminal)
- Configuration file validation
- Duplicate instance detection with interactive resolution
- PID file creation for process tracking
- Startup verification with error capture

**Usage:**
```powershell
# Basic usage (default config)
.\start_oscar.bat

# Custom configuration file
.\start_oscar.ps1 -ConfigFile "..\biff-agents\quickstart_configs\OscarConfig.xml"

# Verbose logging
.\start_oscar.ps1 -Verbose

# Disable GUI
.\start_oscar.ps1 -NoGUI

# Show help
.\start_oscar.ps1 -Help
```

**Python Search Order:**
1. `python` in PATH
2. `python3` in PATH
3. `C:\Program Files\Python312\python.exe`
4. `C:\Program Files\Python311\python.exe`
5. `C:\Program Files\Python310\python.exe`
6. `%LOCALAPPDATA%\Programs\Python\Python312\python.exe`
7. `%LOCALAPPDATA%\Programs\Python\Python311\python.exe`
8. `%LOCALAPPDATA%\Programs\Python\Python310\python.exe`

### stop_oscar.bat / stop_oscar.ps1
Gracefully stops running Oscar instance(s).

**Features:**
- Finds Oscar by PID file (most reliable)
- Falls back to process name search
- Handles multiple instances
- Automatic PID file cleanup
- Force stop with error handling

**Usage:**
```powershell
.\stop_oscar.bat
```

### status_oscar.bat / status_oscar.ps1
Displays runtime status and diagnostics.

**Features:**
- Process detection and information
- CPU and memory usage reporting
- Runtime duration calculation
- Log file status and recent entries
- Network port monitoring (port 1100)
- Management command suggestions

**Usage:**
```powershell
.\status_oscar.bat
```

**Sample Output:**
```
============================================================
  BIFF Oscar - Status Check
============================================================

[STATUS] Oscar is running

Process Information:
  PID:          18744
  CPU:          2.34s
  Memory:       45.67 MB
  Start Time:   2/2/2026 5:10 PM
  Running For:  00:05:23

Log File:
  Location:     D:\github\...\Oscar\OscarLog.txt
  Size:         12.45 KB
  Last Updated: 2/2/2026 5:15 PM

Recent Log Entries (last 5 lines):
  [Recent log content displayed]

Network Status:
  Port 1100:    LISTENING

Management Commands:
  Stop:         .\stop_oscar.ps1
  Restart:      .\stop_oscar.ps1; .\start_oscar.ps1
  View Logs:    Get-Content OscarLog.txt -Wait -Tail 20
```

## File Descriptions

| File | Type | Purpose |
|------|------|---------|
| `start_oscar.bat` | Batch | Wrapper for `start_oscar.ps1` |
| `start_oscar.ps1` | PowerShell | Main startup logic |
| `stop_oscar.bat` | Batch | Wrapper for `stop_oscar.ps1` |
| `stop_oscar.ps1` | PowerShell | Shutdown logic |
| `status_oscar.bat` | Batch | Wrapper for `status_oscar.ps1` |
| `status_oscar.ps1` | PowerShell | Status checking logic |
| `.oscar.pid` | Runtime | Process ID tracking (auto-generated) |
| `OscarLog.txt` | Runtime | Oscar output log (auto-generated) |

## Configuration

### Default Configuration
By default, scripts use `OscarConfig.xml` in the Oscar directory.

### Custom Configuration
Specify a different config file:
```powershell
.\start_oscar.ps1 -ConfigFile "path\to\custom\OscarConfig.xml"
```

### Environment-Based Configuration
For automated deployments, use environment variables in your config:
```xml
<!-- OscarConfig.xml -->
<Oscar>
  <Upstreams>
    <Connection IP="${MINION_IP}" PORT="1100"/>
  </Upstreams>
</Oscar>
```

## Troubleshooting

### Problem: "Python not found"
**Symptoms:** Script reports it cannot find Python

**Solutions:**
1. Install Python 3.7+ from https://www.python.org/downloads/
2. During installation, check "Add Python to PATH"
3. Restart terminal after installation
4. Verify: `python --version`

**Alternative:**
Manually specify Python path in `start_oscar.ps1` (line 67):
```powershell
$PythonCmd = "C:\Path\To\Your\python.exe"
```

### Problem: "Configuration file not found"
**Symptoms:** Script cannot find `OscarConfig.xml`

**Solutions:**
1. Ensure you're running scripts from Oscar directory: `cd Oscar`
2. Check if `OscarConfig.xml` exists: `dir *.xml`
3. Specify absolute path: `.\start_oscar.ps1 -ConfigFile "C:\Full\Path\OscarConfig.xml"`
4. Use quickstart config: `.\start_oscar.ps1 -ConfigFile "..\biff-agents\quickstart_configs\OscarConfig.xml"`

### Problem: "Oscar may already be running"
**Symptoms:** Warning about existing instance during startup

**Solutions:**
1. Accept prompt to stop and restart (type `y`)
2. Or manually stop first: `.\stop_oscar.bat`
3. Check status: `.\status_oscar.bat`
4. If stale PID, delete `.oscar.pid` and retry

### Problem: Port 1100 already in use
**Symptoms:** Oscar fails to start, mentions port conflict

**Solutions:**
1. Check what's using port: `netstat -ano | findstr :1100`
2. Stop conflicting process (usually another Oscar): `.\stop_oscar.bat`
3. Or kill by PID: `Stop-Process -Id <PID> -Force`
4. Modify config to use different port

### Problem: PowerShell execution policy blocks scripts
**Symptoms:** "cannot be loaded because running scripts is disabled"

**Solutions:**
1. Use `.bat` wrappers instead of `.ps1` files directly
2. Or run once: `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`
3. Or bypass temporarily: `powershell -ExecutionPolicy Bypass -File .\start_oscar.ps1`

## Integration with BIFF Deployment

### Full Stack Startup

**Linux Minion → Windows Oscar → Windows Marvin:**

```powershell
# 1. Start Oscar (Windows)
cd Oscar
.\start_oscar.bat

# 2. Start Minion (Linux - separate terminal/machine)
ssh user@linux-server
cd /opt/Board-Instrumentation-Framework/Minion
python3 Minion.py -c MinionConfig.xml

# 3. Start Marvin (Windows)
cd Marvin
java -jar build\libs\BIFF.Marvin.jar -i MarvinConfig.xml
```

### Quickstart Deployment

Use biff-agents quickstart configs:
```powershell
.\start_oscar.ps1 -ConfigFile "..\biff-agents\quickstart_configs\OscarConfig.xml"
```

### Production Deployment

For production environments:
1. Configure Oscar to listen on specific IPs/ports
2. Set up firewall rules for port 1100
3. Consider Windows Service for auto-start (see Advanced Usage)
4. Enable log rotation
5. Set up monitoring (use `status_oscar.ps1` in scheduled task)

## Log Management

### View Real-Time Logs
```powershell
Get-Content OscarLog.txt -Wait -Tail 20
```

### Search Logs
```powershell
Select-String -Path OscarLog.txt -Pattern "error|warning" -Context 2
```

### Archive Old Logs
```powershell
Move-Item OscarLog.txt "OscarLog_$(Get-Date -Format 'yyyyMMdd_HHmmss').txt"
```

### Clear Logs
```powershell
Clear-Content OscarLog.txt
```

## Advanced Usage

### Run Multiple Oscar Instances
Requires separate directories and configs:
```powershell
# Oscar Instance 1
cd Oscar
.\start_oscar.ps1 -ConfigFile OscarConfig_1.xml

# Oscar Instance 2
cd ..\Oscar2
.\start_oscar.ps1 -ConfigFile OscarConfig_2.xml
```

### Automated Monitoring
Create scheduled task to check Oscar status:
```powershell
$action = New-ScheduledTaskAction -Execute "PowerShell.exe" `
    -Argument "-ExecutionPolicy Bypass -File C:\BIFF\Oscar\status_oscar.ps1"
$trigger = New-ScheduledTaskTrigger -Once -At (Get-Date) -RepetitionInterval (New-TimeSpan -Minutes 5)
Register-ScheduledTask -TaskName "BIFF Oscar Monitor" -Action $action -Trigger $trigger
```

### Windows Service Installation (Production)
For always-on production deployments:

**Using NSSM (Non-Sucking Service Manager):**
```powershell
# Download NSSM from https://nssm.cc/

# Install service
nssm install BIFFOscar "C:\Program Files\Python312\python.exe" `
    "Oscar.py -i OscarConfig.xml"
nssm set BIFFOscar AppDirectory "C:\BIFF\Oscar"
nssm set BIFFOscar DisplayName "BIFF Oscar Data Broker"
nssm set BIFFOscar Description "Board Instrumentation Framework data routing service"

# Start service
nssm start BIFFOscar

# Manage service
nssm stop BIFFOscar
nssm restart BIFFOscar
nssm remove BIFFOscar confirm
```

### Remote Management
Manage Oscar on remote Windows machines:
```powershell
# Run remotely via PSSession
$session = New-PSSession -ComputerName REMOTE-PC
Invoke-Command -Session $session -FilePath ".\start_oscar.ps1"
Invoke-Command -Session $session -FilePath ".\status_oscar.ps1"
```

## Comparison with Manual Execution

### Traditional Method (Manual)
```powershell
python Oscar.py -i OscarConfig.xml
# Blocks terminal, must stay open
```

**Limitations:**
- Blocks terminal session
- Must remember exact Python command
- No automatic Python detection
- No status checking mechanism
- Difficult to stop gracefully
- No PID tracking

### Automated Scripts (Recommended)
```powershell
.\start_oscar.bat
# Runs in background, terminal free
```

**Benefits:**
- ✅ Non-blocking background execution
- ✅ Automatic Python detection
- ✅ Built-in status monitoring
- ✅ Graceful shutdown
- ✅ PID file tracking
- ✅ Error detection and reporting
- ✅ User-friendly batch wrappers

## Requirements

- **Operating System:** Windows 7/10/11
- **PowerShell:** 5.1+ (included in Windows)
- **Python:** 3.7+ (3.10+ recommended)
- **Oscar:** BIFF Oscar component
- **Permissions:** Standard user (no admin required)

## Related Documentation

- Oscar Configuration: `ReadMe.txt`
- BIFF Architecture: `../README.md`
- Quickstart Guide: `../biff-agents/QUICKSTART.md`
- Python 3.12+ Compatibility: `../PYTHON312_FIXES.md`
- Windows Deployment: `../OSCAR_WINDOWS_DEPLOYMENT_FINDINGS.md`

## Support

For issues or questions:
1. Check troubleshooting section above
2. Review Oscar logs: `OscarLog.txt`
3. Verify network connectivity: `netstat -an | findstr :1100`
4. Check GitHub Issues: Board-Instrumentation-Framework repository

## Version History

- **2026-02-02**: Initial release
  - start_oscar.ps1 + batch wrapper
  - stop_oscar.ps1 + batch wrapper
  - status_oscar.ps1 + batch wrapper
  - Comprehensive documentation
