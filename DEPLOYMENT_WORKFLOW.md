# Complete BIFF Deployment Workflow Example

This guide demonstrates the complete workflow from quickstart generation to packaged deployment.

## Step 1: Environment Setup

```powershell
# Configure Java environment (one-time setup)
.\setup_java.ps1

# Verify Java
java -version  # Should show Java 10+

# Configure Gradle proxy if behind corporate firewall
$env:GRADLE_OPTS="-Dhttp.proxyHost=proxy-dmz.intel.com -Dhttp.proxyPort=912 -Dhttps.proxyHost=proxy-dmz.intel.com -Dhttps.proxyPort=912"
```

## Step 2: Generate Quickstart Configuration

```powershell
# Run quickstart orchestrator to generate configurations
python -m biff_agents.quickstart

# Follow prompts:
#   - Install Python packages? (y/n): y
#   - Deployment type: local
#   - Collector preset: demo
#   - Build Marvin? (y/n): y
#   - Launch components? (y/n): n  # We'll package first
```

**Generated Files:**
- `biff-agents/biff-quickstart-test/OscarConfig.xml`
- `biff-agents/biff-quickstart-test/MinionConfig.xml`
- `biff-agents/biff-quickstart-test/ApplicationConfig.xml`
- `Marvin/build/libs/BIFF.Marvin.jar` (if built)

## Step 3: Build Deployment Package

```powershell
# Build complete package with quickstart configs
python biff-agents\build_package.py --config-source biff-agents\biff-quickstart-test

# Or use existing JAR (skip rebuild)
python biff-agents\build_package.py --skip-build --config-source biff-agents\biff-quickstart-test
```

**Output:** `BIFF-Package-<version>-<date>/` directory

## Step 4: Test Package Locally

```powershell
cd BIFF-Package-1.0.0-20260203

# Review configurations
Get-Content Configs\OscarConfig.xml
Get-Content Configs\MinionConfig.xml
Get-Content Configs\MarvinConfig.xml

# Start all components
.\start_all.ps1

# Or start individually:
# cd Oscar && .\start_oscar.ps1 -ConfigFile ..\Configs\OscarConfig.xml -Background
# cd Minion && .\start_minion.ps1 -ConfigFile ..\Configs\MinionConfig.xml
# cd Marvin && .\start_marvin.ps1 -ConfigFile ..\Configs\MarvinConfig.xml
```

## Step 5: Deploy to Remote System

```powershell
# Compress package
Compress-Archive -Path BIFF-Package-* -DestinationPath BIFF-Deploy.zip

# Calculate checksum
Get-FileHash BIFF-Deploy.zip -Algorithm SHA256

# Transfer to remote system (RDP, USB, network share)
Copy-Item BIFF-Deploy.zip \\remote-server\share\

# On remote system:
Expand-Archive BIFF-Deploy.zip -DestinationPath C:\Apps
cd C:\Apps\BIFF-Package-*
.\setup_java.ps1
.\start_all.ps1
```

## Alternative Workflows

### Workflow A: Demo Package (No Build)

Use existing JAR with demo configurations:

```powershell
# Use pre-built Marvin JAR with demo configs
python biff-agents\build_package.py --skip-build

# Output includes Demonstration configs from Oscar/Minion
```

### Workflow B: Production Package

```powershell
# 1. Create production configs in separate directory
mkdir production-configs
# Copy and customize configs...

# 2. Build production package
python biff-agents\build_package.py \
  --config-source production-configs \
  --output-dir BIFF-Production

# 3. Version and archive
$version = "2.1.0"
Rename-Item BIFF-Production-* BIFF-Production-$version
Compress-Archive BIFF-Production-$version BIFF-Production-$version.zip
```

### Workflow C: Multi-System Deployment

Deploy components separately to different servers:

```powershell
# 1. Build complete package
python biff-agents\build_package.py --config-source multi-system-configs

# 2. Extract components
$pkg = "BIFF-Package-1.0.0-20260203"

# 3. Deploy Minion to data source servers
Copy-Item $pkg\Minion server1:C:\Apps\Minion
Copy-Item $pkg\Configs\MinionConfig.xml server1:C:\Apps\Minion\
# Edit config to point to Oscar server
ssh server1 "cd C:\Apps\Minion && .\start_minion.ps1 -ConfigFile MinionConfig.xml"

# 4. Deploy Oscar to central broker server
Copy-Item $pkg\Oscar central:C:\Apps\Oscar
Copy-Item $pkg\Configs\OscarConfig.xml central:C:\Apps\Oscar\
# Edit config to specify Marvin IP
ssh central "cd C:\Apps\Oscar && .\start_oscar.ps1 -ConfigFile OscarConfig.xml -Background"

# 5. Deploy Marvin to visualization workstation
Copy-Item $pkg\Marvin workstation:C:\Apps\Marvin
Copy-Item $pkg\Configs\MarvinConfig.xml workstation:C:\Apps\Marvin\
Copy-Item $pkg\setup_java.ps1 workstation:C:\Apps\
# Start GUI
```

## Troubleshooting Workflow Issues

### Issue: Quickstart Build Fails

```powershell
# Ensure Java environment
.\setup_java.ps1
java -version

# Set proxy if needed
$env:GRADLE_OPTS="-Dhttp.proxyHost=proxy -Dhttp.proxyPort=8080"

# Try manual build
cd Marvin
.\gradlew clean buildDeps
.\gradlew build
cd ..
```

### Issue: Package Build Fails

```powershell
# Check prerequisites
python biff-agents\build_package.py

# If Java issues, configure environment
.\setup_java.ps1

# If proxy issues, set GRADLE_OPTS
$env:GRADLE_OPTS="-Dhttp.proxyHost=proxy -Dhttp.proxyPort=8080"

# If still fails, use existing JAR
python biff-agents\build_package.py --skip-build
```

### Issue: Packaged Components Won't Start

```powershell
# Check Java (Marvin requirement)
java -version

# Check Python (Oscar/Minion requirement)
python --version

# Check configurations
Get-Content Configs\OscarConfig.xml
# Verify ports and IPs match network topology

# Check logs
Get-Content Oscar\OscarLog.txt
Get-Content Minion\MinionLog.txt

# Check network connectivity
Test-NetConnection -ComputerName oscar-server -Port 1100
Test-NetConnection -ComputerName marvin-workstation -Port 52001
```

## Complete Example Script

Save as `deploy-biff.ps1`:

```powershell
#!/usr/bin/env pwsh
# Complete BIFF deployment automation

param(
    [string]$DeploymentType = "local",
    [string]$OutputName = "BIFF-Deploy"
)

Write-Host "BIFF Complete Deployment Workflow" -ForegroundColor Cyan
Write-Host "=================================" -ForegroundColor Cyan
Write-Host ""

# Step 1: Setup environment
Write-Host "[1/5] Setting up environment..." -ForegroundColor Yellow
.\setup_java.ps1

# Step 2: Generate configs
Write-Host "[2/5] Generating configurations..." -ForegroundColor Yellow
python -m biff_agents.quickstart <<EOF
y
$DeploymentType
demo
n
n
EOF

# Step 3: Build package
Write-Host "[3/5] Building deployment package..." -ForegroundColor Yellow
python biff-agents\build_package.py \
  --config-source biff-agents\biff-quickstart-test \
  --output-dir $OutputName

# Step 4: Compress
Write-Host "[4/5] Compressing package..." -ForegroundColor Yellow
$pkgDir = Get-ChildItem -Directory "$OutputName-*" | Select-Object -First 1
Compress-Archive -Path $pkgDir.FullName -DestinationPath "$($pkgDir.Name).zip" -Force

# Step 5: Summary
Write-Host "[5/5] Deployment package ready!" -ForegroundColor Green
Write-Host ""
Write-Host "Package: $($pkgDir.Name).zip" -ForegroundColor Cyan
Write-Host "Size: $((Get-Item "$($pkgDir.Name).zip").Length / 1MB | ForEach-Object { "{0:N1} MB" -f $_ })" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "  1. Transfer $($pkgDir.Name).zip to target system" -ForegroundColor White
Write-Host "  2. Extract and run .\start_all.ps1" -ForegroundColor White
```

## See Also

- [QUICKSTART.md](../QUICKSTART.md) - Quickstart orchestrator guide
- [PACKAGING.md](../PACKAGING.md) - Packaging system documentation
- [STARTUP_SCRIPTS.md](../STARTUP_SCRIPTS.md) - Component startup documentation
- [README.md](../README.md) - Project overview
