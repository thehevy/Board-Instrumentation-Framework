# BIFF Project Session Summary - February 2-4, 2026

## Session Overview
Successfully deployed and tested Board Instrumentation Framework (BIFF) in a distributed environment, discovered and fixed Python 3.12 compatibility issues, and validated data flow from Linux Minion to Windows Oscar.

---

## Project Architecture Understanding

### What is BIFF?
A **3-tier instrumentation and visualization framework** for real-time system monitoring and data visualization:

1. **Minion** (Python) - Data collection agents with 30+ pluggable collectors
2. **Oscar** (Python) - UDP data broker/router and session recorder  
3. **Marvin** (JavaFX 10+) - Configurable GUI with 40+ widget types

### Data Flow
```
Minion collectors → UDP → Oscar (port 1100) → UDP → Marvin (ports 52001+)
```

### Key Concepts
- **Namespaces**: Organize collectors into logical groups
- **Collectors**: Python scripts/functions that gather metrics
- **Dynamic Loading**: Minion can import Python collectors as modules (faster) or execute as external processes
- **Alias System**: XML variable substitution using `$(ALIAS_NAME)` syntax
- **Widget Binding**: Marvin widgets bind to data via `<MinionSrc Namespace="..." ID="..."/>`

---

## Deployment Tested

### Architecture
```
┌─────────────────────────────────────────────────────────────┐
│ Linux Server (nd-gnr-gb-1 / 10.166.84.131)                  │
│ - Python 3.12.12                                            │
│ - Minion: /opt/Board-Instrumentation-Framework/Build/       │
│ - Sends UDP → 10.166.84.131:1100                           │
└─────────────────────────────────────────────────────────────┘
                              ↓ UDP
┌─────────────────────────────────────────────────────────────┐
│ Windows Desktop (10.166.84.131)                             │
│ - Oscar + Marvin: D:\github\Board-Instrumentation-Framework\│
│ - Oscar listening on port 1100                              │
└─────────────────────────────────────────────────────────────┘
```

### Working Configuration
- **Minion Namespace**: LocalTest
- **Collectors**: 
  - `randomval.value` - Random values 0-100 every 1s
  - `cpu.usage` - CPU percentage every 2s
  - `randomval2.value` - Random values 50-200 every 1.5s
- **Target**: UDP to 10.166.84.131:1100 (Oscar on Windows)
- **Status**: ✅ Data flowing successfully

---

## Critical Issues Found & Fixed

### Issue 1: Python 3.12 Incompatibility (CRITICAL)
**Problem**: Minion fails to start on Python 3.12+
```python
# File: Minion/Helpers/DynamicPython.py, Line 30
import imp  # ❌ Module removed in Python 3.12
```

**Fix**: Remove unused import
```python
# Removed: import imp
# Module was never actually used in the code
```

**Status**: ✅ Fixed and verified working

---

### Issue 2: Invalid Escape Sequence
**Problem**: Syntax warning that will become an error
```python
# File: Minion/Minion.py, Line 57
cursors=('/-\|'),('.o0o')  # ⚠️ Invalid escape
```

**Fix**: Use raw string
```python
cursors=(r'/-\|'),('.o0o')
```

**Status**: ✅ Fixed

---

### Issue 3: UTF-8 BOM in Collector Files
**Problem**: Files contain Byte Order Mark, causing exec format errors
```bash
$ file RandomVal.py
RandomVal.py: Python script, Unicode text, UTF-8 (with BOM) text executable
```

**Fix**: Remove BOM
```bash
sed -i '1s/^\xEF\xBB\xBF//' RandomVal.py CPU.py
```

**Files Affected**: 
- `Minion/Collectors/RandomVal.py`
- `Minion/Collectors/CPU.py`

**Status**: ✅ Fixed

---

### Issue 4: Missing Shebangs in Collectors
**Problem**: Collector scripts missing `#!/usr/bin/env python3`

**Fix**: Added to key collectors (RandomVal.py, CPU.py, Timer.py)

**Status**: ✅ Partial fix (3 files), recommend adding to all 30+ collectors

---

### Issue 5: Missing Execute Permissions
**Problem**: Collectors don't have `+x` permission

**Fix**: 
```bash
chmod +x Minion/Collectors/*.py
```

**Status**: ✅ Fixed on Linux server

---

### Issue 6: Incorrect Function Names in Templates
**Problem**: biff-agents quickstart generates invalid collector configs

**Incorrect**:
```xml
<Collector ID="cpu.value">
  <Param>GetUsage</Param>  <!-- ❌ Function doesn't exist -->
</Collector>
```

**Correct**:
```xml
<Collector ID="cpu.usage">
  <Param>GetCPU_Percentage</Param>  <!-- ✅ Actual function -->
</Collector>
```

**Affected Files**:
- `biff-agents/biff_agents_core/generators/minion_generator.py`
- `biff-agents/quickstart_configs/MinionConfig.xml`

**Status**: ⚠️ Documented, needs fix in source

---

### Issue 7: Timer Collector State Management
**Problem**: Timer.py requires complex initialization, fails with basic config

**Error**: `Timer {default} does not exist`

**Root Cause**: Timer uses class-based state management (`TimerInfo` class) requiring specific initialization sequences not documented

**Workaround**: Use simpler collectors (RandomVal, CPU) for testing

**Status**: ⚠️ Needs documentation or simplified implementation

---

## Files Created/Modified

### On Linux Server (/opt/Board-Instrumentation-Framework/)

**New Files**:
- `Build/` - Git-ignored folder for local Minion instance
- `Build/MinionConfig.xml` - Working collector configuration
- `Build/start_minion.sh` - Production-grade launcher with nohup, CPU affinity, logging
- `Build/stop_minion.sh` - Clean shutdown script
- `Build/README.md` - Setup documentation
- `Build/FINDINGS_SUMMARY.md` - Detailed technical findings for dev team
- `.gitignore` - Added `Build/` directory

**Modified Files**:
- `Minion/Helpers/DynamicPython.py` - Removed `import imp`
- `Minion/Minion.py` - Fixed escape sequence
- `Minion/Collectors/RandomVal.py` - Removed BOM, added shebang
- `Minion/Collectors/CPU.py` - Removed BOM, added shebang
- `Minion/Collectors/Timer.py` - Added shebang
- `Minion/Collectors/*.py` - Added execute permissions
- `.github/copilot-instructions.md` - Updated with biff-agents info, platform considerations

---

## Production Launcher Pattern Implemented

Enhanced `start_minion.sh` with production features based on user's existing `launchMinion.sh`:

```bash
# Auto-cleanup (prevent duplicate processes)
pkill -f Minion.py

# Get last CPU core for affinity
cpu_core=$(lscpu | grep "On-line" | sed -e 's#.*-\(\)#\1#')

# Launch with CPU affinity, background execution, logging
nohup taskset -c "${cpu_core}" python3 Minion.py -i config.xml >> log 2>&1 &
```

**Features**:
- ✅ CPU affinity optimization
- ✅ Background execution (survives terminal closure)
- ✅ Status logging to file
- ✅ PID tracking
- ✅ Clean shutdown script

---

## Key Learnings About BIFF

### Collector Configuration Pattern
Collectors must specify function name as first parameter:

```xml
<Collector ID="randomval.value">
  <Executable>Collectors/RandomVal.py</Executable>
  <Param>GetBoundedRandomValue</Param>  <!-- Function name -->
  <Param>0</Param>                      <!-- min -->
  <Param>100</Param>                    <!-- max -->
</Collector>
```

### Available CPU Collector Functions
- `GetCPU_Percentage()` - Overall CPU usage ✅
- `GetCPU_Core_Percentage(which)` - Single core
- `GetCPU_Core_PercentageList(startCore, count)` - Multiple cores

**NOT**: `GetUsage()` or `GetMemory()` (don't exist)

### Testing Strategy
- **Legacy components** (Minion/Oscar/Marvin): No automated tests
- **Validation**: Use demonstration configs in `*/Demonstration/` directories
- **biff-agents**: Has pytest suite with 34+ tests

### File Encoding Requirements
- Must be UTF-8 **without BOM**
- Use `pathlib.Path()` for cross-platform compatibility
- Scripts need shebangs for external execution
- Python 3.12+ removes deprecated modules (`imp`, etc.)

---

## biff-agents Modern CLI Toolkit

Recent addition to BIFF (Phase 1 complete):

**Purpose**: Reduce BIFF setup time from 30-60 minutes to <5 minutes

**Features**:
- Quick Start Orchestrator - Generate complete configs
- Config Generators - Programmatic XML creation
- Validators - Syntax and semantic checking
- Environment Validator - Pre-flight checks

**Location**: `biff-agents/` subdirectory

**Status**: Production ready, but has template bugs (wrong CPU function names)

---

## Commands Reference

### Linux Server

```bash
# Start Minion (production launcher)
cd /opt/Board-Instrumentation-Framework/Build
./start_minion.sh

# View logs
tail -f minion_status.log

# Stop Minion
./stop_minion.sh

# Check if running
ps aux | grep Minion.py
```

### Windows Desktop

```powershell
# Start Oscar
cd D:\github\Board-Instrumentation-Framework
python Oscar\Oscar.py -c Oscar\OscarConfig.xml

# Build Marvin (if needed)
cd Marvin
.\gradlew buildDeps    # First time only
.\gradlew build
```

### biff-agents Quick Start

```bash
cd biff-agents
python -m biff_cli quickstart
```

---

## Important File Locations

### Configuration Files
- **Minion**: `Build/MinionConfig.xml` (working), `Minion/Demonstration/` (examples)
- **Oscar**: `Oscar/OscarConfig.xml`
- **Marvin**: `Marvin/Starter_Application/StarterApplication.xml`

### Source Code
- **Minion**: `Minion/Minion.py` (entry), `Minion/Helpers/` (core), `Minion/Collectors/` (30+ collectors)
- **Oscar**: `Oscar/Oscar.py`, `Oscar/Helpers/`
- **Marvin**: `Marvin/src/main/java/kutch/biff/marvin/`
- **biff-agents**: `biff-agents/biff_agents_core/`, `biff-agents/biff_cli/`

### Documentation
- **User Guide**: `BIFF Instrumentation Framework User Guide.pdf` (200+ pages)
- **AI Instructions**: `.github/copilot-instructions.md` (comprehensive dev guide)
- **Findings**: `Build/FINDINGS_SUMMARY.md` (technical bug report for devs)
- **Quick Start**: `biff-agents/QUICKSTART.md`

---

## Known Working Collector Configurations

### RandomVal (Random Number Generator)
```xml
<Collector ID="randomval.value" Frequency="1000">
  <Executable>/opt/Board-Instrumentation-Framework/Minion/Collectors/RandomVal.py</Executable>
  <Param>GetBoundedRandomValue</Param>
  <Param>0</Param>    <!-- min -->
  <Param>100</Param>  <!-- max -->
</Collector>
```

### CPU Usage
```xml
<Collector ID="cpu.usage" Frequency="2000">
  <Executable>/opt/Board-Instrumentation-Framework/Minion/Collectors/CPU.py</Executable>
  <Param>GetCPU_Percentage</Param>
</Collector>
```

**Note**: Requires `psutil` library: `pip install psutil`

---

## Next Steps / Outstanding Issues

### For Development Team
1. **CRITICAL**: Commit Python 3.12 fixes to main repo
2. **HIGH**: Fix biff-agents templates (CPU function names)
3. **HIGH**: Remove BOM from all collector files
4. **MEDIUM**: Add shebangs to remaining collectors
5. **MEDIUM**: Document Timer.py usage or simplify
6. **LOW**: Add Python 3.12+ to CI/CD testing

### For This Deployment
1. ✅ Minion running successfully on Linux
2. ✅ Oscar receiving data on Windows
3. ⏳ Build and test Marvin GUI (optional)
4. ⏳ Create dashboard configurations in Marvin
5. ⏳ Add more collectors as needed (Network, Docker, Prometheus, etc.)

---

## Troubleshooting Tips

### Minion Won't Start
- Check Python version: `python3 --version` (need 3.7+, tested on 3.12.12)
- Verify fixes applied: `grep "import imp" Minion/Helpers/DynamicPython.py` (should be empty)
- Check logs: `tail -f Build/minion_status.log`

### Oscar Not Receiving Data
- Verify Oscar listening: `netstat -ano | findstr :1100` (Windows)
- Check firewall: UDP port 1100 must be open
- Verify Minion target IP in `Build/MinionConfig.xml`
- Check Oscar logs for connection messages

### Collector Returns Empty String
- Function name missing or incorrect in `<Param>`
- Check function exists: `grep "^def " Minion/Collectors/<file>.py`
- View demo configs: `Minion/Demonstration/DemoConfig.xml`

### Gradle Issues (Marvin)
- Requires JDK 10+ (tested with JDK 17)
- Build Enzo first: `cd Marvin/Dependencies/Enzo && ./gradlew build`
- Then: `cd ../.. && ./gradlew copyEnzoJar && ./gradlew build`

---

## Testing Validation Status

- ✅ Python 3.12.12 compatibility verified
- ✅ Dynamic loading of collectors working
- ✅ UDP communication across network validated
- ✅ Production launcher patterns tested
- ✅ Distributed deployment (Linux → Windows) confirmed
- ✅ Oscar receiving and processing data
- ⏳ Marvin GUI visualization (pending)
- ❌ Timer collector (state management issues)

---

## Repository Structure

```
Board-Instrumentation-Framework/
├── .github/
│   └── copilot-instructions.md      # AI dev guide (updated)
├── Build/                            # Local test instance (git-ignored)
│   ├── MinionConfig.xml
│   ├── start_minion.sh
│   ├── stop_minion.sh
│   ├── README.md
│   └── FINDINGS_SUMMARY.md          # Bug report for devs
├── Minion/                           # Data collector
│   ├── Minion.py                    # Entry point
│   ├── Collectors/                  # 30+ built-in collectors
│   ├── Helpers/                     # Core logic
│   └── Demonstration/               # Example configs
├── Oscar/                            # Data broker
│   ├── Oscar.py
│   ├── OscarConfig.xml
│   └── Helpers/
├── Marvin/                           # GUI dashboard
│   ├── build.gradle
│   ├── src/main/java/kutch/biff/marvin/
│   ├── Widget/                      # 40+ widget types
│   └── Dependencies/Enzo/          # Custom gauge library
└── biff-agents/                     # Modern CLI toolkit
    ├── biff_cli/                    # Command-line interface
    ├── biff_agents_core/            # Generators, validators
    ├── tests/                       # Pytest suite
    └── quickstart_configs/          # Generated outputs
```

---

## Contact Points / Key Decisions

### Why Build/ Directory?
- Provides local sandbox for testing without affecting git repo
- Added to `.gitignore` for safe experimentation
- Contains production-ready launcher scripts

### Why Not Fix All Collectors?
- Fixed 3 critical collectors (RandomVal, CPU, Timer) as proof-of-concept
- Remaining 27+ collectors should be batch-fixed by dev team
- Pattern is clear: Remove BOM + Add shebang

### Why Enhanced Launcher?
- Based on user's existing production patterns (`launchMinion.sh`)
- Prevents common issues (duplicate processes, terminal dependency)
- Production-ready for deployment

---

## Session Timeline

**Day 1 (Feb 2)**:
- Set up Build/ folder with local Minion instance
- Discovered Python 3.12 `imp` module issue
- Fixed BOM and shebang issues
- Got basic Minion running

**Day 2 (Feb 2-3)**:
- Corrected collector function names
- Established distributed deployment (Linux → Windows)
- Enhanced launcher with production features
- Validated data flow to Oscar
- Documented all findings

**Day 3-4 (Feb 4)**:
- User applied fixes, tested deployment
- Verified working configuration
- Prepared documentation for future sessions

---

## For Future AI Sessions

### Quick Context
This is a **legacy framework** (circa 2016) being modernized with Python 3.12+ support and modern tooling (biff-agents). The codebase is production-proven but lacks automated tests for legacy components.

### Key Files to Read First
1. `.github/copilot-instructions.md` - Comprehensive architecture guide
2. `Build/FINDINGS_SUMMARY.md` - Bug report with all fixes
3. This session summary - What happened and why

### What's Working
- Minion on Python 3.12.12 (with fixes applied)
- Distributed deployment pattern
- RandomVal and CPU collectors
- Production launcher with nohup/CPU affinity

### What Needs Work
- Timer collector documentation
- biff-agents template corrections
- Remaining collectors (BOM removal + shebangs)
- CI/CD for Python 3.12+

### Testing Approach
Run demonstration configs, not unit tests. Example:
```bash
cd Minion/Demonstration
python3 ../Minion.py -i DemoConfig.xml
```

---

**Session Summary Document Version**: 1.0  
**Date**: February 4, 2026  
**Status**: Deployment working, fixes documented, ready for upstream contribution
