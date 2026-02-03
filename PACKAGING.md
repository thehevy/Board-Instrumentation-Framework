# BIFF Packaging Guide

This guide explains how to create standalone deployment packages of BIFF.

## Overview

The BIFF packaging system creates a complete, self-contained distribution that can be deployed to any Windows system without the full repository.

## Quick Start

```powershell
# Build complete package with default configs
.\build_package.ps1

# Build with custom configs (e.g., from quickstart)
.\build_package.ps1 -ConfigSource biff-agents\biff-quickstart-test

# Build without rebuilding Marvin (use existing JAR)
.\build_package.ps1 -SkipBuild

# Custom output directory
.\build_package.ps1 -OutputDir MyDeployment
```

## Package Contents

The generated package includes everything needed to run BIFF:

```
BIFF-Package-<version>-<date>/
├── Marvin/                   # GUI Application
│   ├── BIFF.Marvin.jar      # 38+ MB JavaFX application
│   ├── Widget/              # 40+ widget types with styles
│   ├── start_marvin.ps1     # PowerShell launcher
│   └── start_marvin.bat     # Batch launcher
│
├── Oscar/                    # Data Broker
│   ├── Oscar.py             # Main executable
│   ├── Helpers/             # Core modules (Configuration, DataHandler, etc.)
│   ├── Data/                # Connection point abstractions
│   ├── Util/                # Utility modules
│   ├── start_oscar.ps1      # PowerShell launcher with background mode
│   ├── start_oscar.bat      # Batch launcher
│   ├── status_oscar.ps1     # Status checker
│   └── stop_oscar.ps1       # Stop script
│
├── Minion/                   # Data Collector
│   ├── Minion.py            # Main executable
│   ├── Collectors/          # 30+ built-in collectors
│   ├── Helpers/             # Core modules (Collector, Namespace, etc.)
│   ├── Util/                # Utility modules
│   ├── start_minion.ps1     # PowerShell launcher
│   └── start_minion.bat     # Batch launcher
│
├── Configs/                  # Configuration Templates
│   ├── MarvinConfig.xml     # Marvin application configuration
│   ├── OscarConfig.xml      # Oscar broker configuration
│   └── MinionConfig.xml     # Minion collector configuration
│
├── Documentation/            # Reference Materials
│   ├── BIFF Instrumentation Framework User Guide.pdf
│   ├── STARTUP_SCRIPTS.md   # Startup script documentation
│   └── PROJECT_README.md    # Repository README
│
├── start_all.ps1            # Unified startup (Oscar + Marvin)
├── start_all.bat            # Unified startup (Batch version)
├── setup_java.ps1           # Java environment configuration
├── setup_java.bat           # Java environment (Batch)
├── license.txt              # License information
└── README.md                # Deployment guide with network config
```

## Build Process

### Prerequisites

**For Building**:
- Java 10+ in PATH (or run `setup_java.ps1` first)
- Gradle wrapper (included in repository)
- PowerShell 5.1+ (Windows built-in)

**For Using Package**:
- Java 10+ (Marvin only)
- Python 3.7+ (Oscar and Minion)

### Build Steps

The packaging script automates:

1. **Marvin Build** (unless `-SkipBuild`):
   - Builds Enzo dependency library
   - Copies Enzo JAR to Marvin lib directory
   - Builds Marvin with Gradle
   - Produces `BIFF.Marvin.jar` (~38 MB)

2. **Directory Creation**:
   - Creates package root directory
   - Creates component subdirectories
   - Creates Configs and Documentation folders

3. **File Copying**:
   - **Marvin**: JAR + Widget directory + startup scripts
   - **Oscar**: Python sources + modules + startup/management scripts
   - **Minion**: Python sources + collectors + modules + startup scripts
   - **Configs**: Templates from specified source or demo configs
   - **Documentation**: User guide + README files
   - **Root**: Unified startup scripts + Java setup scripts

4. **Script Generation**:
   - `start_all.ps1` - PowerShell unified launcher
   - `start_all.bat` - Batch unified launcher
   - `README.md` - Complete deployment guide with network config

5. **Packaging Complete**:
   - Displays package size and contents
   - Shows next steps for deployment

## Usage Scenarios

### Scenario 1: Development Package

Create package from current development state:

```powershell
# Ensure latest build
cd Marvin
.\gradlew build
cd ..

# Create package
.\build_package.ps1 -OutputDir BIFF-Dev
```

### Scenario 2: Quickstart Package

Create package with quickstart-generated configs:

```powershell
# Run quickstart to generate configs
python -m biff_agents.quickstart

# Package with quickstart configs
.\build_package.ps1 -ConfigSource biff-agents\biff-quickstart-test -OutputDir BIFF-Quickstart
```

### Scenario 3: Production Package

Create package for production deployment:

```powershell
# Build with specific version
cd Marvin
.\gradlew build -PupdateReleaseInfo
cd ..

# Create package with production configs
.\build_package.ps1 -ConfigSource production-configs -OutputDir BIFF-Production-v2.1
```

### Scenario 4: Quick Rebuild

Repackage without rebuilding (faster for config changes):

```powershell
.\build_package.ps1 -SkipBuild -ConfigSource new-configs
```

## Configuration Management

### Default Configs

If no `-ConfigSource` specified, uses demo configurations:
- `Oscar/Demonstration/DemoOscar.xml` or `Oscar/OscarConfig.xml`
- `Minion/Demonstration/DemoConfig.xml`
- `Marvin/Starter_Application/StarterApplication.xml`

### Custom Configs

Specify directory containing XML configs:

```powershell
.\build_package.ps1 -ConfigSource path\to\configs
```

All `.xml` files are copied to `Configs/` in package.

### Post-Package Configuration

Recipients can edit configs in package:
- `Configs/OscarConfig.xml` - Adjust ports, IP addresses
- `Configs/MinionConfig.xml` - Configure collectors, namespaces
- `Configs/MarvinConfig.xml` - Define widgets, grids, tabs

## Deployment

### Deploy to Local System

```powershell
# Build package
.\build_package.ps1

# Test locally
cd BIFF-Package-*
.\start_all.ps1
```

### Deploy to Remote System

```powershell
# Build package
.\build_package.ps1 -OutputDir BIFF-Deploy

# Compress
Compress-Archive -Path BIFF-Deploy-* -DestinationPath BIFF-Deploy.zip

# Transfer to remote system (RDP, USB, network share, etc.)

# On remote system:
Expand-Archive BIFF-Deploy.zip -DestinationPath C:\Apps
cd C:\Apps\BIFF-Deploy-*
.\setup_java.ps1  # If Java not in PATH
.\start_all.ps1
```

### Deploy to Multiple Systems

**Distributed Architecture**:

```
[Server 1] Minion → 
[Server 2] Minion → [Central Server] Oscar → [Workstation] Marvin
[Server 3] Minion → 
```

**Steps**:

1. **Build package once**:
   ```powershell
   .\build_package.ps1 -OutputDir BIFF-Multi
   ```

2. **Deploy to each Minion server**:
   - Copy `BIFF-Multi/Minion/` directory only
   - Copy `BIFF-Multi/Configs/MinionConfig.xml`
   - Edit config: Set Oscar IP/port

3. **Deploy to Oscar server**:
   - Copy `BIFF-Multi/Oscar/` directory
   - Copy `BIFF-Multi/Configs/OscarConfig.xml`
   - Edit config: Set Marvin IP/port

4. **Deploy to Marvin workstation**:
   - Copy `BIFF-Multi/Marvin/` directory
   - Copy `BIFF-Multi/Configs/MarvinConfig.xml`
   - Copy `BIFF-Multi/setup_java.*` scripts
   - Edit config: Set Oscar connection

## Package Verification

### Check Package Integrity

```powershell
$pkg = "BIFF-Package-1.0.0-20260203"

# Verify Marvin JAR exists and is not corrupted
Test-Path "$pkg\Marvin\BIFF.Marvin.jar"
(Get-Item "$pkg\Marvin\BIFF.Marvin.jar").Length -gt 30MB

# Verify Widget directory
Test-Path "$pkg\Marvin\Widget"
(Get-ChildItem "$pkg\Marvin\Widget" -Recurse).Count -gt 50

# Verify Oscar/Minion Python files
Test-Path "$pkg\Oscar\Oscar.py"
Test-Path "$pkg\Minion\Minion.py"

# Verify collectors
(Get-ChildItem "$pkg\Minion\Collectors\*.py").Count -gt 20

# Verify startup scripts
Test-Path "$pkg\start_all.ps1"
Test-Path "$pkg\Marvin\start_marvin.ps1"
Test-Path "$pkg\Oscar\start_oscar.ps1"
Test-Path "$pkg\Minion\start_minion.ps1"

# Verify documentation
Test-Path "$pkg\README.md"
Test-Path "$pkg\Documentation\BIFF Instrumentation Framework User Guide.pdf"
```

### Test Package

```powershell
# Quick smoke test
cd BIFF-Package-*

# Check Java (Marvin prerequisite)
java -version

# Check Python (Oscar/Minion prerequisite)
python --version

# Start components
.\start_all.ps1
```

## Advanced Features

### Version Management

Package name includes version from Marvin:
- Source: `Marvin/src/main/resources/kutch/biff/marvin/version/Marvin.version.properties`
- Format: `BIFF-Package-<version>-<YYYYMMDD>`
- Example: `BIFF-Package-1.0.0-20260203`

### Incremental Packaging

Fast repackaging for configuration changes:

```powershell
# Initial build (slow: ~15 seconds)
.\build_package.ps1

# Make config changes in repository
# ...

# Repackage without rebuilding Marvin (fast: ~2 seconds)
.\build_package.ps1 -SkipBuild -ConfigSource updated-configs
```

### Custom Package Structure

Modify `build_package.ps1` for custom requirements:

```powershell
# Add custom files after Step 8
Copy-Item "MyCustom\Files" "$packageName\Custom\" -Recurse

# Add custom documentation
Copy-Item "MyGuide.pdf" "$packageName\Documentation\"

# Add custom scripts
Copy-Item "my_script.ps1" "$packageName\"
```

## Troubleshooting

### Build Fails

**Enzo build error**:
```powershell
# Check Java
java -version

# Set JAVA_HOME if needed
.\setup_java.ps1

# Check proxy (if behind corporate firewall)
$env:GRADLE_OPTS="-Dhttp.proxyHost=proxy.example.com -Dhttp.proxyPort=8080"
```

**Marvin build error**:
```powershell
# Clean and rebuild
cd Marvin
.\gradlew clean build
cd ..
```

### JAR Not Found

```powershell
# Verify JAR location
Test-Path Marvin\build\libs\BIFF.Marvin.jar

# If missing, build manually
cd Marvin
.\gradlew buildDeps
.\gradlew build
cd ..
```

### Package Too Large

Typical sizes:
- Marvin JAR: ~38 MB
- Widget directory: ~5 MB
- Oscar/Minion: ~1 MB
- Total package: ~45-50 MB

Reduce size:
- Exclude documentation: Comment out Step 8 in `build_package.ps1`
- Exclude unused widgets: Remove from `Marvin/Widget/` before packaging
- Exclude unused collectors: Remove from `Minion/Collectors/` before packaging

### Permissions Error

Run PowerShell as Administrator if copying fails:
```powershell
Start-Process powershell -Verb RunAs -ArgumentList "-ExecutionPolicy Bypass -File build_package.ps1"
```

## Best Practices

### Versioning
- Update version in `Marvin.version.properties` before building
- Use semantic versioning: MAJOR.MINOR.PATCH
- Tag releases in Git: `git tag -a v1.0.0 -m "Release 1.0.0"`

### Configuration Management
- Store production configs separately from repository
- Use `-ConfigSource` to include production configs in package
- Document config changes in package README.md

### Testing
- Test package on clean system (VM recommended)
- Verify all components start successfully
- Validate data flow: Minion → Oscar → Marvin
- Test with multiple Minion instances

### Documentation
- Update package README.md with environment-specific details
- Document network topology and port assignments
- Include troubleshooting steps for common issues
- Provide contact information for support

### Distribution
- Compress package for transfer: `Compress-Archive`
- Calculate checksum: `Get-FileHash BIFF-Package.zip`
- Store build artifacts: Save package for each release
- Version control: Tag repository at build time

## Integration with CI/CD

### Automated Builds

```powershell
# Example CI/CD pipeline script
param([string]$Version)

# Update version
$versionFile = "Marvin\src\main\resources\kutch\biff\marvin\version\Marvin.version.properties"
(Get-Content $versionFile) -replace "version=.*", "version=$Version" | Set-Content $versionFile

# Build package
.\build_package.ps1 -OutputDir "BIFF-Release-$Version"

# Compress
Compress-Archive -Path "BIFF-Release-$Version" -DestinationPath "BIFF-Release-$Version.zip"

# Calculate hash
Get-FileHash "BIFF-Release-$Version.zip" | Select-Object Hash | Out-File "BIFF-Release-$Version.sha256"

# Upload to artifact server
# ...
```

## See Also

- [STARTUP_SCRIPTS.md](STARTUP_SCRIPTS.md) - Startup script documentation
- [QUICKSTART.md](biff-agents/QUICKSTART.md) - Quickstart guide
- [README.md](README.md) - Project overview
- User Guide PDF - Complete reference manual
