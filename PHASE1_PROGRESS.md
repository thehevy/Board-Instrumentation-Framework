# Phase 1 Progress: Quick Start Orchestrator

## Week 3, Day 2: Enhanced Environment Detection ✅ COMPLETE

**Date**: January 29, 2026

**Commit**: `f7512ae - Phase 1 Day 2: Enhanced environment detection and setup wizard`

### Summary

Completed interactive setup wizard and enhanced environment detection. Users now get a fully guided experience from validation through configuration selection.

### What Was Built

#### 1. Enhanced Environment Validator (138 additional LOC)

**New Features**:

- **BIFF Installation Detection** (`detect_biff_installation()`):
  - Searches current directory and up to 3 parent levels
  - Identifies Marvin/, Minion/, Oscar/ component directories
  - Extracts version information:
    - Marvin: Parses `build.gradle` for version string
    - Minion: Reads `Helpers/_Version.py` for `__version__`
  - Reports found installations with component paths and versions
  - Example output: "✓ BIFF installation found at D:\github\Board-Instrumentation-Framework"

- **Network Connectivity Checks** (`check_network_connectivity()`):
  - Tests internet connectivity via socket to 8.8.8.8:53 (Google DNS)
  - Detects Windows Firewall status (advises on UDP port rules)
  - Optional check (not blocking - use `check_network=True`)
  - Timeout protection (3 seconds)

- **Java Requirement Relaxed**:
  - Changed from blocking issue → warning
  - Rationale: Only Marvin requires Java; Minion and Oscar work without it
  - Allows users to set up data collection before building GUI
  - Warning: "⚠ Java not found in PATH. Required only if running Marvin GUI"

**API Updates**:

```python
def validate_all(self, check_network: bool = False, biff_root: Optional[Path] = None):
    """
    Args:
        check_network: If True, perform network connectivity checks
        biff_root: Optional path to BIFF installation root for path detection
    Returns:
        Dict with java, python, ports, system, biff_paths, network, ready
    """
```

#### 2. Setup Wizard (`setup_wizard.py` - 127 LOC)

**Interactive Features**:

- **Deployment Type Selection**:
  - Single-Machine (Local): All components on localhost
  - Network Deployment: Minion remote, Oscar/Marvin on server
  - Container/K8s: Docker or Kubernetes deployment
  - Multi-Deployment: Compare multiple environments side-by-side
  - Shows descriptions for each option

- **Existing Installation Handling**:
  - Detects if running from BIFF repo
  - Prompts: "Use this installation? (Otherwise will create standalone setup)"
  - If yes: Uses existing components (no duplication)
  - If no: Creates standalone configuration directory

- **Deployment Configuration**:
  - Local: Auto-configures localhost, ports 1100/52001
  - Remote: Prompts for Oscar IP, custom ports
  - Container: Uses environment variables ($(MinionNamespace), $(OscarIP))
  - Multi: Asks for number of environments to compare

- **Collector Presets**:
  - demo: RandomVal, Timer, CPU (great for testing)
  - monitoring: CPU, Memory, Network, Storage (production ready)
  - minimal: RandomVal only (fastest setup)
  - custom: Coming soon (manual selection)

- **Output Directory Selection**:
  - Default: `./biff-quickstart/`
  - Checks if directory exists
  - Prompts for overwrite confirmation
  - Creates directory structure

- **Configuration Summary**:
  - Shows all selections before proceeding
  - Final confirmation: "Proceed with this configuration? [Y/n]"
  - Handles Ctrl+C gracefully

**Architecture**:

```python
class SetupWizard:
    def __init__(self, validation_results: Dict)
    def run(self) -> Dict  # Returns config for generators
    
    # Private helper methods
    def _select_deployment_type()
    def _handle_existing_installation()
    def _configure_deployment()
    def _select_collectors()
    def _select_output_directory()
    def _confirm_configuration() -> bool
```

#### 3. CLI Integration Updates

**handle_quickstart()** now follows this workflow:

1. **Environment Validation**:
   - Run EnvironmentValidator with BIFF path detection
   - Display validation results (info/warnings/issues)
   - Exit with code 1 if blocking issues found
   - Continue with warnings (Java optional)

2. **Interactive Wizard**:
   - Launch SetupWizard with validation results
   - Guide user through configuration
   - Handle KeyboardInterrupt (Ctrl+C)
   - Return config dict

3. **Config Generation** (next phase):
   - Generate MinionConfig.xml
   - Generate OscarConfig.xml
   - Generate Marvin Application.xml
   - Create launcher scripts

### User Experience

**Full Workflow**:

```powershell
$ biff quickstart

============================================================
  BIFF Quick Start Orchestrator
============================================================

ℹ Checking your environment for BIFF prerequisites...

ℹ ✓ Python 3.12 detected (minimum: 3.9)
ℹ ✓ Port 1100 available
ℹ ✓ Port 52001 available
ℹ ℹ psutil not installed - skipping detailed resource checks
ℹ ✓ BIFF installation found at D:\github\Board-Instrumentation-Framework
  - Marvin: 2023.06.15
  - Minion: 19.02

⚠ ⚠ Java not found in PATH. Required only if running Marvin GUI

✓ ✓ Environment validation passed!

============================================================
  BIFF Quick Start Setup Wizard
============================================================

ℹ Choose your deployment type:

  1. Single-Machine (Local)
     All components on localhost - fastest setup

  2. Network Deployment
     Minion on one machine, Oscar/Marvin on another

  3. Container/K8s
     Docker or Kubernetes deployment

  4. Multi-Deployment
     Compare multiple environments side-by-side

Select deployment type:
  1. Single-Machine (Local)
  2. Network Deployment
  3. Container/K8s
  4. Multi-Deployment

Enter number: 1

✓ Selected: Single-Machine (Local)

ℹ Existing BIFF installation detected at:
  D:\github\Board-Instrumentation-Framework

Use this installation? (Otherwise will create standalone setup) [Y/n]: y

✓ Will use existing BIFF installation

ℹ Single-machine setup - using localhost for all components

Minion namespace (groups collectors) [QuickStart]: Demo

ℹ Select collectors to include:

Available presets:
  - demo: RandomVal, Timer, CPU
  - monitoring: CPU, Memory, Network, Storage
  - minimal: RandomVal

Choose collector preset:
  1. demo
  2. monitoring
  3. minimal
  4. custom

Enter number: 1

✓ Selected collectors: RandomVal, Timer, CPU

ℹ Output directory configuration:

Output directory for generated files [D:\github\Board-Instrumentation-Framework\biff-agents\biff-quickstart]: 

============================================================
  Configuration Summary
============================================================

Deployment Type:  local
Output Directory: D:\github\Board-Instrumentation-Framework\biff-agents\biff-quickstart
Minion Namespace: Demo
Oscar Address:    localhost:1100
Marvin Port:      52001
Collectors:       RandomVal, Timer, CPU
BIFF Root:        D:\github\Board-Instrumentation-Framework

Proceed with this configuration? [Y/n]: y

✓ Configuration complete!

ℹ Next steps:
ℹ   - Generating Minion configuration...
ℹ   - Generating Oscar configuration...
ℹ   - Generating Marvin application...

⚠ Config generation coming in next phase
```

### Technical Decisions

1. **Java as Warning, Not Blocker**:
   - Allows Minion/Oscar-only setups
   - Users can collect data before building GUI
   - Aligns with container deployment (Minion only)

2. **Three-Level Parent Search**:
   - Finds BIFF repo even when running from subdirectories
   - Prevents false negatives (e.g., running from biff-agents/)
   - Avoids infinite loops (stops at 3 levels)

3. **Wizard Returns Config Dict**:
   - Decouples UI from generation logic
   - Makes testing easier (mock wizard results)
   - Enables non-interactive mode in future (--preset flag)

4. **Graceful Failure Handling**:
   - KeyboardInterrupt → warning, exit code 0
   - EOF (pipe input) → caught by wizard
   - Validation failure → suggestions, exit code 1

### Known Limitations

1. **Setup Wizard Requires Interactive Terminal**:
   - Cannot use echo/pipe for input (EOF errors)
   - Future: Add `--non-interactive` flag with defaults
   - Workaround: Use `--preset` flag (coming next phase)

2. **BIFF Detection Heuristic**:
   - Looks for Marvin/, Minion/, Oscar/ directories
   - May false-positive on similarly named folders
   - Could add .biff marker file for certainty

3. **Network Check Basic**:
   - Only tests Google DNS (8.8.8.8:53)
   - Doesn't verify actual Oscar connectivity
   - Future: Add Oscar IP reachability test

### Metrics

- **LOC Added**: 
  - environment_validator.py: +138 LOC (254 → 392 total)
  - setup_wizard.py: +127 LOC (new file)
  - main.py: +32 LOC (integration)
  - **Total**: +297 LOC

- **Test Coverage**:
  - environment_validator.py: 42% (219 statements, 128 untested)
  - setup_wizard.py: 10% (127 statements, 114 untested - needs interactive tests)
  - Overall: 35% (down from 46% due to untested wizard)

- **Tests**: 28 passing (0 new - wizard needs mocked input tests)

- **Commits**: 1 (f7512ae)

### Next Steps (Week 3, Days 3-5)

**Config Generation** - The final piece of Quick Start:

1. **MinionConfigGenerator** (Day 3):
   - Generate MinionConfig.xml based on wizard config
   - Include selected collectors (RandomVal, Timer, CPU, etc.)
   - Support localhost and remote Oscar IP
   - Add aliases for parameterization

2. **OscarConfigGenerator** (Day 3):
   - Generate OscarConfig.xml with upstream/downstream connections
   - Configure Minion listener (port 1100)
   - Configure Marvin targets (port 52001)
   - Support multiple namespaces

3. **MarvinApplicationGenerator** (Day 4):
   - Generate Grid.QuickStart.xml with gauges/charts
   - Bind widgets to Minion collectors via <MinionSrc>
   - Create Tab.QuickStart.xml
   - Generate Application.xml entry point

4. **Integration & Testing** (Day 5):
   - End-to-end test: quickstart → configs → launch → verify data
   - Create launcher scripts (start_all.bat / start_all.sh)
   - Test on clean system (no existing BIFF)
   - Documentation (QUICKSTART.md)

**Success Criteria for Week 3**:
- ✅ Day 1: Environment validation (COMPLETE)
- ✅ Day 2: Setup wizard (COMPLETE)
- ⏳ Day 3: Minion/Oscar config generation
- ⏳ Day 4: Marvin config generation
- ⏳ Day 5: End-to-end working demo

## Week 3, Day 1: Environment Validation ✅ COMPLETE

**Date**: January 29, 2026

**Commit**: `0df86d2 - Phase 1 Day 1: Environment validation implemented`

### Summary

Successfully implemented comprehensive environment validation for BIFF Quick Start. Users can now run `biff quickstart` to verify their system meets all prerequisites before attempting deployment.

### What Was Built

#### 1. Environment Validator (`environment_validator.py` - 254 LOC)

**Core Features**:

- **Java Detection**: Parses `java -version` output, handles both OpenJDK and Oracle formats
  - Detects Java 10+ (Marvin requirement)
  - Distinguishes between "1.8.x" (old) and "11.x" (new) version formats
  - Reports insufficient versions with upgrade recommendations

- **Python Detection**: Validates Python 3.9+ requirement
  - Uses `sys.version_info` for accurate version checking
  - No subprocess overhead

- **Port Availability**: Tests UDP ports 1100 (Oscar) and 52001 (Marvin)
  - Creates actual socket bindings to verify availability
  - Warns about conflicts with existing BIFF instances

- **System Resources** (optional): Uses psutil if installed
  - CPU core count, memory (total/available), disk space
  - Skips gracefully if psutil not available

- **Gradle Detection**: Two-tier check
  - First checks for `Marvin/gradlew` (bundled wrapper - preferred)
  - Falls back to system `gradle` command
  - Warns if neither found (not critical - gradlew included in BIFF)

- **Fix Suggestions**: Platform-specific guidance
  - Windows: Java download links, PATH instructions
  - Linux: `apt`/`dnf` commands for package managers
  - Port conflict: Shows how to find existing processes

**Architecture**:

```python
class EnvironmentValidator:
    def __init__(self):
        self.issues = []      # Blocking problems
        self.warnings = []    # Non-critical issues
        self.info = []        # Success messages
    
    def validate_all(self) -> Dict[str, any]:
        """Run all checks, return results dict"""
        return {
            "java": {...},
            "python": {...},
            "ports": {...},
            "system": {...},
            "ready": len(self.issues) == 0
        }
    
    def suggest_fixes(self) -> List[str]:
        """Generate actionable fix commands"""
```

#### 2. CLI Integration (`main.py` updates)

**Before**:

```python
def handle_quickstart(args):
    print_header("Quick Start Orchestrator")
    print_info("This feature is under development")
    return 0
```

**After**:

```python
def handle_quickstart(args):
    print_header("BIFF Quick Start Orchestrator")
    print_info("Checking your environment for BIFF prerequisites...")
    
    validator = EnvironmentValidator()
    results = validator.validate_all()
    
    # Display results with color-coded output
    for info in validator.info:
        print_info(info)
    
    for warning in validator.warnings:
        print_warning(warning)
    
    for issue in validator.issues:
        print_error(issue)
    
    if not results["ready"]:
        print_error("Environment validation failed!")
        fixes = validator.suggest_fixes()
        for fix in fixes:
            print(f"  {fix}")
        return 1
    
    print_success("✓ Environment validation passed!")
    # TODO: Launch interactive setup wizard
    return 0
```

#### 3. Test Coverage (`test_environment_validator.py` - 13 tests)

**Test Scenarios**:

1. Java Detection:
   - Valid Java 11+ detected → passes
   - Java 8 detected → fails with upgrade message
   - Java not found → fails with install instructions

2. Port Availability:
   - Ports 1100, 52001 available → passes
   - Port in use → warns with conflict resolution

3. Gradle Detection:
   - System `gradle` found → passes
   - No Gradle found → warns (non-blocking)

4. Fix Suggestions:
   - Java missing → install links
   - Port conflict → process finder commands

5. Full Validation:
   - Returns dict with expected keys
   - `ready` flag reflects blocking issues

**Coverage**:

- `environment_validator.py`: 62% (88 of 143 statements)
- Overall project: 46% (up from 37%)
- All 28 tests passing (15 existing + 13 new)

### User Experience

**Example Session** (Python 3.12, no Java):

```powershell
$ biff quickstart

============================================================
  BIFF Quick Start Orchestrator
============================================================

ℹ Checking your environment for BIFF prerequisites...

ℹ ✓ Python 3.12 detected (minimum: 3.9)
ℹ ✓ Port 1100 available
ℹ ✓ Port 52001 available
ℹ ℹ psutil not installed - skipping detailed resource checks

✗ ✗ Java not found in PATH. Marvin requires Java 10+

✗ Environment validation failed!

ℹ Suggested fixes:
  Install Java 11+ from: https://adoptium.net/
  After installation, add Java to PATH
```

### Technical Decisions

1. **No External Dependencies**: Uses only stdlib (subprocess, socket, sys, platform)
   - `psutil` is optional enhancement
   - Zero installation friction for basic functionality

2. **Platform-Agnostic**: Works on Windows, Linux, macOS
   - Handles Windows `gradlew.bat` vs Unix `gradlew`
   - Platform-specific fix suggestions

3. **Graceful Degradation**: Continues even if optional checks fail
   - psutil not installed → skips resource checks
   - Gradle not found → warns but doesn't block

4. **Detailed Feedback**: Three-tier messaging system
   - ℹ Info: Successful checks
   - ⚠ Warnings: Non-blocking issues
   - ✗ Issues: Blocking problems

### Integration Points

**Current**:

- `biff quickstart` command entry point
- Validates before proceeding to config generation

**Next** (Day 2+):

- Pass validation results to setup wizard
- Use port availability data for config generation
- Suggest Java version in generated READMEs

### Known Limitations

1. **Java Version Parsing**: Regex-based, may not handle exotic formats
   - Works with OpenJDK, Oracle JDK, Azul Zulu
   - May fail on unusual vendor formats

2. **Port Binding**: Tests UDP only
   - Creates temporary socket to verify availability
   - May miss complex firewall scenarios

3. **Gradle Detection**: Checks PATH only
   - Doesn't search custom install locations
   - Acceptable - gradlew included in BIFF repo

### Next Steps (Day 2)

1. **Network Connectivity** (optional enhancement):
   - Ping test for Oscar IP (if remote deployment)
   - Firewall detection (Windows Defender, iptables)

2. **BIFF Path Detection**:
   - Search for existing `Marvin/`, `Minion/`, `Oscar/` directories
   - Offer to use existing installation vs fresh setup

3. **Interactive Setup Wizard**:
   - Prompt for deployment type (local, remote, container)
   - Collect user preferences (port numbers, namespace)
   - Generate configs based on validated environment

4. **Documentation**:
   - Add troubleshooting guide for common failures
   - Document environment validator API for other agents

### Metrics

- **LOC Added**: 254 (environment_validator.py) + 160 (tests) = 414 LOC
- **Test Coverage**: 62% (environment_validator), 46% (project)
- **Tests Added**: 13 (all passing)
- **CLI Commands**: 1 functional (`biff quickstart` with validation)
- **Commit**: 0df86d2 (pushed to GitHub fork)

### Success Criteria ✅

- ✅ Java 10+ detection working
- ✅ Python 3.9+ detection working
- ✅ Port availability checks working
- ✅ Gradle detection working
- ✅ Fix suggestions generated
- ✅ CLI integration complete
- ✅ Unit tests passing
- ✅ Cross-platform compatible

**Result**: Day 1 objectives fully achieved. Ready to proceed with Day 2 enhancements.
