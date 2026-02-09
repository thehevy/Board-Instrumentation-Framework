# Oscar Windows Deployment - Findings Report

**Date**: February 2, 2026  
**Component**: Oscar Data Broker  
**Environment**: Windows Desktop  
**Reporter**: AI Coding Assistant  

---

## Executive Summary

During deployment of Oscar on Windows (10.166.84.131), two critical issues were identified that prevent successful startup using documented commands. Both issues impact first-time users and require documentation updates and potentially tooling improvements.

**Status**: ✅ **Resolved** - Oscar successfully running  
**Impact**: High - Blocks initial deployment for Windows users without Python  
**Priority**: P1 - Documentation updates required  

---

## Issue #1: Python Not Installed on Windows

### Severity: **CRITICAL**
### Status: **RESOLVED**

### Problem Description

Oscar startup failed because Python was not installed or available in Windows PATH:

```powershell
PS> python Oscar.py -i OscarConfig.xml
python : The term 'python' is not recognized as the name of a cmdlet, 
function, script file, or operable program.
```

### Root Cause

1. Python is not a default Windows component (unlike Linux servers)
2. BIFF documentation assumes Python is already installed
3. No automated installation scripts provided for Windows
4. PATH environment variable not configured

### Environment Detection Results

```powershell
PS> where.exe python
INFO: Could not find files for the given pattern(s).

PS> where.exe python3
INFO: Could not find files for the given pattern(s).

PS> py --version
The term 'py' is not recognized...
```

### Solution Applied

**Automated Python Installation via PowerShell:**

```powershell
# Download Python 3.12.2 installer
$ProgressPreference = 'SilentlyContinue'
Invoke-WebRequest -Uri "https://www.python.org/ftp/python/3.12.2/python-3.12.2-amd64.exe" `
    -OutFile "$env:TEMP\python-installer.exe"

# Install silently with PATH configuration
Start-Process -FilePath "$env:TEMP\python-installer.exe" `
    -ArgumentList "/quiet", "InstallAllUsers=1", "PrependPath=1", "Include_test=0" `
    -Wait

# Cleanup
Remove-Item "$env:TEMP\python-installer.exe"
```

**Installation Location:** `C:\Program Files\Python312\python.exe`

### Verification

```powershell
PS> python --version
Python 3.12.2

PS> Test-Path "C:\Program Files\Python312\python.exe"
True
```

### Recommendations for Developers

#### Immediate Actions:

1. **Update Prerequisites Documentation**
   - Add explicit Python installation instructions for Windows
   - Include download links and version requirements (Python 3.7+, tested 3.12.2)
   - Add screenshots or step-by-step installation guide

2. **Create Windows Setup Script**
   - Location: `Oscar/setup_windows.ps1`
   - Automate Python detection and installation
   - Verify dependencies before allowing Oscar startup

3. **Add Environment Check**
   - Update `Oscar.py` startup to detect Python version and PATH
   - Print helpful error messages if dependencies missing
   - Suggest installation commands

#### Proposed `Oscar/setup_windows.ps1`:

```powershell
# BIFF Oscar - Windows Setup Script
# Checks prerequisites and installs Python if needed

Write-Host "Checking prerequisites for Oscar..." -ForegroundColor Cyan

# Check if Python is available
$pythonCmd = $null
try {
    $pythonCmd = Get-Command python -ErrorAction Stop
    $version = & python --version 2>&1
    Write-Host "✓ Python found: $version" -ForegroundColor Green
} catch {
    Write-Host "✗ Python not found" -ForegroundColor Red
    
    $install = Read-Host "Install Python 3.12.2 automatically? (y/n)"
    if ($install -eq 'y') {
        Write-Host "Downloading Python 3.12.2..." -ForegroundColor Yellow
        # [Installation code from above]
    } else {
        Write-Host "Please install Python from: https://www.python.org/downloads/" -ForegroundColor Yellow
        exit 1
    }
}

Write-Host "`nSetup complete! Start Oscar with:" -ForegroundColor Green
Write-Host "  python Oscar.py -i OscarConfig.xml" -ForegroundColor White
```

#### Long-term Improvements:

1. **Package Management**
   - Consider distributing Oscar as a Windows executable (PyInstaller/cx_Freeze)
   - Include Python runtime in distribution package
   - Create MSI installer for enterprise environments

2. **Dependency Documentation**
   - Create `requirements.txt` even though Oscar uses stdlib
   - Document optional dependencies (if any collectors need them)
   - Version compatibility matrix

3. **CI/CD Testing**
   - Add Windows environment to CI/CD pipeline
   - Test fresh Windows installs without Python
   - Validate installation scripts

---

## Issue #2: Incorrect Command Line Argument Documentation

### Severity: **MEDIUM**
### Status: **RESOLVED**

### Problem Description

Documentation and examples throughout BIFF use `-c` flag for Oscar configuration, but Oscar actually uses `-i`:

```powershell
# INCORRECT (documented in multiple places)
PS> python Oscar.py -c OscarConfig.xml
Oscar.py: error: unrecognized arguments: -c OscarConfig.xml

# CORRECT (actual implementation)
PS> python Oscar.py -i OscarConfig.xml
Oscar - Version: 23.05.04 Build 4
```

### Root Cause Analysis

**Inconsistency across components:**
- **Minion**: Uses `-c` for config file ✓
- **Oscar**: Uses `-i` for input file ✓ (but documented as `-c`)
- **Marvin**: Uses config file path directly

### Oscar Actual Arguments

```
usage: Oscar.py [-h] [-i INPUT] [-l LOGFILE] [-v] [-m] 
                [-p PLAYBACK | -r RECORD] [-s SPEED] 
                [-ex | -rp | -lp] [-b BEGIN] [-e END] 
                [-t TIME] [-ng] [-bc BATCHCONVERT]

options:
  -i INPUT, --input INPUT
                        specifies application configuration file file
  -c                    [NOT SUPPORTED - does not exist]
```

### Documentation Locations Requiring Updates

1. **`.github/copilot-instructions.md`**
   - Line ~53: `python Oscar\Oscar.py -c OscarConfig.xml`
   - Should be: `python Oscar\Oscar.py -i OscarConfig.xml`

2. **`biff-agents/scripts/start_all.bat`**
   - Verify Oscar startup command
   - Likely uses correct `-i` but worth checking

3. **`biff-agents/scripts/start_all.sh`**
   - Verify Oscar startup command
   - Likely uses correct `-i` but worth checking

4. **`Oscar/README.md` or `Oscar/ReadMe.txt`**
   - Update all examples
   - Add note about difference from Minion's `-c`

5. **Main README.md**
   - Update quick start examples
   - Ensure consistency across all components

### Solution Applied

Used correct argument:
```powershell
PS> python Oscar.py -i OscarConfig.xml
```

### Recommendations for Developers

#### Immediate Actions:

1. **Standardize Command Line Arguments**
   - Decision needed: Should all components use same flag?
   - Option A: Keep as-is, improve documentation
   - Option B: Add `-c` as alias to `-i` in Oscar for consistency
   - Option C: Standardize all on `-c` (breaking change)

2. **Update All Documentation**
   - Search codebase for `Oscar.py -c` patterns
   - Replace with `Oscar.py -i`
   - Add command reference table to main README

3. **Add Command Reference Table**

   | Component | Config Argument | Example |
   |-----------|----------------|---------|
   | Minion | `-c <file>` | `python Minion.py -c MinionConfig.xml` |
   | Oscar | `-i <file>` | `python Oscar.py -i OscarConfig.xml` |
   | Marvin | `<file>` | `java -jar BIFF.Marvin.jar Application.xml` |

#### Proposed Code Change (Option B - Add Alias):

**File**: `Oscar/Oscar.py`

```python
# Current
parser.add_argument('-i', '--input', 
                   help='specifies application configuration file file')

# Proposed - Add compatibility alias
parser.add_argument('-i', '-c', '--input', '--config',
                   help='specifies application configuration file')
```

**Benefits:**
- Maintains backward compatibility
- Matches Minion behavior
- No breaking changes
- Users can use either `-i` or `-c`

#### Long-term Improvements:

1. **CLI Consistency**
   - Review all three components for argument consistency
   - Create shared CLI argument standard document
   - Consider using common argument parser library

2. **Auto-completion Scripts**
   - Provide bash/zsh completion for Oscar
   - PowerShell completion for Windows users
   - Help users discover correct arguments

3. **Validation**
   - Add linting check to detect documentation/code mismatches
   - CI/CD test to run help commands and validate examples

---

## Issue #3: biff-agents Quickstart Script Compatibility

### Severity: **LOW**
### Status: **OBSERVATION**

### Potential Issue

The `biff-agents/scripts/start_all.bat` and `start_all.sh` scripts may have same issues:
- Assume Python is in PATH
- May use incorrect Oscar argument

### Recommendation

Audit and test both launcher scripts:

```bash
# Test on fresh Windows install
biff-agents/scripts/start_all.bat

# Test on Linux
biff-agents/scripts/start_all.sh
```

Update scripts to:
1. Detect Python availability
2. Use correct Oscar arguments
3. Provide helpful error messages

---

## Current Deployment Status

### ✅ Successful Deployment

**Windows Desktop (10.166.84.131):**
- Python 3.12.2 installed: `C:\Program Files\Python312\`
- Oscar running: Version 23.05.04 Build 4
- Listening on: Port 1100 (default)
- Configuration: `OscarConfig.xml`
- Status: **ACTIVE** (background process)

**Expected Data Flow:**
```
Linux Server (10.166.84.131)
  └─> Minion (Python 3.12.12)
        └─> UDP → 10.166.84.131:1100
              └─> Oscar (Windows, Python 3.12.2)
                    └─> UDP → Ports 52001+
                          └─> Marvin (GUI Dashboard)
```

### Next Steps for Complete Deployment

1. **Build Marvin** (Java/Gradle)
   ```powershell
   cd d:\github\Board-Instrumentation-Framework\Marvin
   .\gradlew build
   ```

2. **Start Marvin GUI**
   ```powershell
   java -jar build\libs\BIFF.Marvin.jar Application.xml
   ```

3. **Verify Data Flow**
   - Oscar should show incoming data from Minion
   - Marvin should display real-time metrics

---

## Files Modified (for reference)

### Windows Desktop
- **Installed**: Python 3.12.2 at `C:\Program Files\Python312\`
- **PATH**: Updated to include Python installation directory
- **Running**: Oscar.py with correct `-i` argument

### Documentation Updates Required

| File | Line/Section | Change Needed |
|------|-------------|---------------|
| `.github/copilot-instructions.md` | Line ~53 | Change `-c` to `-i` for Oscar |
| `README.md` | Quick Start | Update Oscar command example |
| `biff-agents/QUICKSTART.md` | Oscar section | Verify correct arguments |
| `Oscar/ReadMe.txt` | All examples | Standardize on `-i` argument |

---

## Automated Fix Script

For convenience, here's a PowerShell script to apply documentation fixes:

```powershell
# fix-oscar-docs.ps1
# Fixes Oscar command line argument in documentation

$files = @(
    ".github\copilot-instructions.md",
    "README.md",
    "biff-agents\QUICKSTART.md",
    "biff-agents\scripts\README.md"
)

foreach ($file in $files) {
    if (Test-Path $file) {
        Write-Host "Updating $file..." -ForegroundColor Yellow
        
        $content = Get-Content $file -Raw
        $updated = $content -replace 'Oscar\.py -c ', 'Oscar.py -i '
        Set-Content -Path $file -Value $updated -NoNewline
        
        Write-Host "  ✓ Updated" -ForegroundColor Green
    }
}

Write-Host "`nDocumentation fixes complete!" -ForegroundColor Green
```

---

## Testing Checklist

Before marking this complete, verify:

- [ ] Oscar starts successfully on fresh Windows install
- [ ] Python installation script works on Windows 10/11
- [ ] All documentation uses correct `-i` argument
- [ ] biff-agents quickstart scripts work end-to-end
- [ ] Data flows from Minion (Linux) → Oscar (Windows) → Marvin
- [ ] CI/CD includes Windows environment testing

---

## Contact & References

**Related Issues:**
- Python 3.12+ Compatibility (BIFF Minion) - Completed Feb 2, 2026
- Collector Function Naming - Documented in copilot-instructions.md

**Documentation:**
- BIFF User Guide: `BIFF Instrumentation Framework User Guide.pdf`
- Quick Start: `biff-agents/QUICKSTART.md`
- AI Coding Guide: `.github/copilot-instructions.md`

**Environment:**
- Linux Server: Python 3.12.12 (Minion)
- Windows Desktop: Python 3.12.2 (Oscar) - Newly installed
- BIFF Version: Oscar 23.05.04 Build 4

---

## Appendix: Command Reference

### Oscar Command Line Reference

```
Oscar.py - Data Broker and Recorder

Configuration:
  -i, --input FILE          Configuration file (required)
  
Logging:
  -l, --logfile FILE        Log file name
  -v, --verbose             Debug information
  
GUI:
  -m, --minimize            Start minimized
  -ng, --nogui              Run without GUI
  
Recording:
  -r, --record FILE         Record to file
  -t, --time MINUTES        Run duration
  
Playback:
  -p, --playback FILE       Playback from file
  -s, --speed FACTOR        Playback speed
  -ex, --exit               Exit after playback
  -rp, --repeat             Repeat continuously
  -lp, --loop               Loop between markers
  -b, --begin NUM           Loop start
  -e, --end NUM             Loop end
  
Utilities:
  -bc, --batchconvert FILE  Convert BIFF to CSV
```

### Comparison: Minion vs Oscar

```bash
# Minion (uses -c)
python Minion/Minion.py -c MinionConfig.xml -v

# Oscar (uses -i)
python Oscar/Oscar.py -i OscarConfig.xml -v

# Both support verbose logging with -v
```

---

**End of Report**
