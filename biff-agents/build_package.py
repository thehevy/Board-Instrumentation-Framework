#!/usr/bin/env python3
"""
BIFF Package Builder - Create Standalone Distribution
========================================================
Creates a complete, deployable BIFF package with all components.

Usage:
    python build_package.py [options]
    
Options:
    --output-dir <path>      Output directory name (default: BIFF-Package)
    --config-source <path>   Copy configs from directory
    --skip-build            Skip Marvin build (use existing JAR)
    --help                  Show this help message
"""

import os
import sys
import shutil
import subprocess
import argparse
from datetime import datetime
from pathlib import Path

class PackageBuilder:
    def __init__(self, args):
        self.args = args
        # Get repo root (parent of biff-agents directory)
        self.repo_root = Path(__file__).parent.parent.resolve()
        self.version = self._get_version()
        self.timestamp = datetime.now().strftime("%Y%m%d")
        self.package_name = f"{args.output_dir}-{self.version}-{self.timestamp}"
        self.package_path = self.repo_root / self.package_name
        
    def _get_version(self):
        """Extract version from Marvin properties file."""
        version_file = self.repo_root / "Marvin" / "src" / "main" / "resources" / "kutch" / "biff" / "marvin" / "version" / "Marvin.version.properties"
        if version_file.exists():
            with open(version_file, 'r') as f:
                for line in f:
                    if line.startswith("version="):
                        return line.strip().split("=")[1]
        return "1.0.0"
    
    def print_status(self, message, status_type="INFO"):
        """Print colored status message."""
        colors = {
            "INFO": "\033[96m",  # Cyan
            "SUCCESS": "\033[92m",  # Green
            "WARNING": "\033[93m",  # Yellow
            "ERROR": "\033[91m",  # Red
            "RESET": "\033[0m"
        }
        print(f"{colors.get(status_type, '')}{[status_type]} {message}{colors['RESET']}")
    
    def check_prerequisites(self):
        """Check build prerequisites and environment."""
        self.print_status("Checking prerequisites...", "INFO")
        
        issues = []
        
        # Check Java
        try:
            result = subprocess.run(["java", "-version"], capture_output=True, check=True, text=True)
            self.print_status("[OK] Java found in PATH", "SUCCESS")
        except (subprocess.CalledProcessError, FileNotFoundError):
            issues.append("Java not in PATH")
            self.print_status("[X] Java not found", "ERROR")
        
        # Check JAVA_HOME
        if not os.environ.get("JAVA_HOME"):
            issues.append("JAVA_HOME not set")
            self.print_status("[!] JAVA_HOME not set", "WARNING")
        else:
            self.print_status(f"[OK] JAVA_HOME = {os.environ.get('JAVA_HOME')}", "SUCCESS")
        
        # Check GRADLE_OPTS (warn only)
        if not os.environ.get("GRADLE_OPTS"):
            self.print_status("[!] GRADLE_OPTS not set (may fail behind proxy)", "WARNING")
        else:
            self.print_status("[OK] GRADLE_OPTS configured", "SUCCESS")
        
        # Check Python
        self.print_status(f"[OK] Python {sys.version.split()[0]}", "SUCCESS")
        
        if issues and not self.args.skip_build:
            print("\n" + "="*60)
            print("PREREQUISITE ISSUES FOUND:")
            print("="*60)
            for issue in issues:
                print(f"  • {issue}")
            print("\nFIXES:")
            print("  1. Configure Java environment:")
            print("     PowerShell: .\\setup_java.ps1")
            print("     Batch:      setup_java.bat")
            print("\n  2. If behind corporate proxy, set GRADLE_OPTS:")
            print('     $env:GRADLE_OPTS="-Dhttp.proxyHost=proxy-dmz.intel.com -Dhttp.proxyPort=912 -Dhttps.proxyHost=proxy-dmz.intel.com -Dhttps.proxyPort=912"')
            print("\n  3. Or skip build and use existing JAR:")
            print("     python biff-agents\\build_package.py --skip-build")
            print("="*60)
            print()
            
            response = input("Continue anyway? (y/N): ")
            if response.lower() != 'y':
                return False
        
        return True
    
    def build_marvin(self):
        """Build Marvin JAR with Gradle."""
        if self.args.skip_build:
            self.print_status("Skipping build (using existing JAR)", "WARNING")
            return True
        
        self.print_status("Building Marvin...", "INFO")
        
        # Check for Java
        try:
            result = subprocess.run(["java", "-version"], capture_output=True, check=True, text=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            self.print_status("Java not in PATH. Run setup_java.ps1 or setup_java.bat first", "ERROR")
            print("\nTo configure Java:")
            print("  PowerShell: .\\setup_java.ps1")
            print("  Batch:      setup_java.bat")
            return False
        
        # Check for GRADLE_OPTS if behind proxy
        if not os.environ.get("GRADLE_OPTS"):
            self.print_status("GRADLE_OPTS not set - may fail behind corporate proxy", "WARNING")
            print("\nIf behind proxy, set before running:")
            print('  $env:GRADLE_OPTS="-Dhttp.proxyHost=proxy.example.com -Dhttp.proxyPort=8080"')
        
        # Build Enzo
        self.print_status("Building Enzo dependency...", "INFO")
        enzo_dir = self.repo_root / "Marvin" / "Dependencies" / "Enzo"
        gradlew = self.repo_root / "Marvin" / "gradlew.bat" if sys.platform == "win32" else self.repo_root / "Marvin" / "gradlew"
        
        result = subprocess.run([str(gradlew), "build"], cwd=enzo_dir, capture_output=True, text=True)
        if result.returncode != 0:
            self.print_status("Enzo build failed", "ERROR")
            print("\nGradle Error Output:")
            print(result.stderr if result.stderr else result.stdout)
            print("\nCommon fixes:")
            print("  1. Set JAVA_HOME: Run setup_java.ps1")
            print("  2. Configure proxy: Set GRADLE_OPTS (see above)")
            print("  3. Clean build: cd Marvin\\Dependencies\\Enzo && ..\\..\\gradlew clean build")
            return False
        
        # Copy Enzo JAR
        self.print_status("Copying Enzo JAR...", "INFO")
        marvin_dir = self.repo_root / "Marvin"
        result = subprocess.run([str(gradlew), "copyEnzoJar"], cwd=marvin_dir, capture_output=True, text=True)
        if result.returncode != 0:
            self.print_status("Copy Enzo JAR failed", "ERROR")
            print("\nError Output:")
            print(result.stderr if result.stderr else result.stdout)
            return False
        
        # Build Marvin
        self.print_status("Building Marvin...", "INFO")
        result = subprocess.run([str(gradlew), "build"], cwd=marvin_dir, capture_output=True, text=True)
        if result.returncode != 0:
            self.print_status("Marvin build failed", "ERROR")
            print("\nError Output:")
            print(result.stderr if result.stderr else result.stdout)
            return False
        
        self.print_status("Build completed successfully", "SUCCESS")
        return True
    
    def create_structure(self):
        """Create package directory structure."""
        self.print_status("Creating package structure...", "INFO")
        
        # Remove existing if present
        if self.package_path.exists():
            self.print_status(f"Removing existing {self.package_name}", "WARNING")
            shutil.rmtree(self.package_path)
        
        # Create directories
        dirs = [
            self.package_path,
            self.package_path / "Marvin",
            self.package_path / "Oscar",
            self.package_path / "Minion",
            self.package_path / "Configs",
            self.package_path / "Documentation"
        ]
        
        for dir_path in dirs:
            dir_path.mkdir(parents=True, exist_ok=True)
        
        return True
    
    def copy_marvin(self):
        """Copy Marvin files."""
        self.print_status("Packaging Marvin...", "INFO")
        
        marvin_src = self.repo_root / "Marvin"
        marvin_dst = self.package_path / "Marvin"
        
        # Copy JAR
        jar_src = marvin_src / "build" / "libs" / "BIFF.Marvin.jar"
        if not jar_src.exists():
            self.print_status("BIFF.Marvin.jar not found. Run without --skip-build", "ERROR")
            return False
        shutil.copy2(jar_src, marvin_dst)
        
        # Copy Widget directory
        shutil.copytree(marvin_src / "Widget", marvin_dst / "Widget", dirs_exist_ok=True)
        
        # Copy startup scripts
        for script in ["start_marvin.ps1", "start_marvin.bat"]:
            src = marvin_src / script
            if src.exists():
                shutil.copy2(src, marvin_dst)
        
        return True
    
    def copy_oscar(self):
        """Copy Oscar files."""
        self.print_status("Packaging Oscar...", "INFO")
        
        oscar_src = self.repo_root / "Oscar"
        oscar_dst = self.package_path / "Oscar"
        
        # Copy main file
        shutil.copy2(oscar_src / "Oscar.py", oscar_dst)
        
        # Copy directories
        for dir_name in ["Helpers", "Data", "Util"]:
            src_dir = oscar_src / dir_name
            if src_dir.exists():
                shutil.copytree(src_dir, oscar_dst / dir_name, dirs_exist_ok=True)
        
        # Copy scripts
        for script in ["start_oscar.ps1", "start_oscar.bat", "status_oscar.ps1", "stop_oscar.ps1"]:
            src = oscar_src / script
            if src.exists():
                shutil.copy2(src, oscar_dst)
        
        return True
    
    def copy_minion(self):
        """Copy Minion files."""
        self.print_status("Packaging Minion...", "INFO")
        
        minion_src = self.repo_root / "Minion"
        minion_dst = self.package_path / "Minion"
        
        # Copy main file
        shutil.copy2(minion_src / "Minion.py", minion_dst)
        
        # Copy directories
        for dir_name in ["Collectors", "Helpers", "Util"]:
            src_dir = minion_src / dir_name
            if src_dir.exists():
                shutil.copytree(src_dir, minion_dst / dir_name, dirs_exist_ok=True)
        
        # Copy scripts
        for script in ["start_minion.ps1", "start_minion.bat"]:
            src = minion_src / script
            if src.exists():
                shutil.copy2(src, minion_dst)
        
        return True
    
    def copy_configs(self):
        """Copy configuration files to component folders."""
        self.print_status("Packaging configurations...", "INFO")
        
        if self.args.config_source:
            config_src = Path(self.args.config_source)
            if config_src.exists():
                self.print_status(f"Copying configs from: {config_src}", "INFO")
                
                # Distribute configs to component folders
                config_mapping = {
                    "Application.xml": self.package_path / "Marvin",
                    "OscarConfig.xml": self.package_path / "Oscar",
                    "MinionConfig.xml": self.package_path / "Minion"
                }
                
                for xml_file in config_src.glob("*.xml"):
                    # Map specific configs to components, others go to Marvin (grids/tabs)
                    if xml_file.name in config_mapping:
                        shutil.copy2(xml_file, config_mapping[xml_file.name])
                    else:
                        # Supporting files (Grid, Tab) go to Marvin folder
                        shutil.copy2(xml_file, self.package_path / "Marvin")
            else:
                self.print_status(f"Config source not found: {config_src}", "WARNING")
        else:
            # Copy demo configs as templates to component folders
            oscar_demo = self.repo_root / "Oscar" / "OscarConfig.xml"
            if oscar_demo.exists():
                shutil.copy2(oscar_demo, self.package_path / "Oscar")
            
            minion_demo = self.repo_root / "Minion" / "Demonstration" / "DemoConfig.xml"
            if minion_demo.exists():
                shutil.copy2(minion_demo, self.package_path / "Minion" / "MinionConfig.xml")
            
            marvin_demo = self.repo_root / "Marvin" / "Starter_Application" / "StarterApplication.xml"
            if marvin_demo.exists():
                shutil.copy2(marvin_demo, configs_dst / "MarvinConfig.xml")
        
        return True
    
    def copy_documentation(self):
        """Copy documentation files."""
        self.print_status("Copying documentation...", "INFO")
        
        docs_dst = self.package_path / "Documentation"
        
        # Copy user guide PDF
        pdf_src = self.repo_root / "BIFF Instrumentation Framework User Guide.pdf"
        if pdf_src.exists():
            shutil.copy2(pdf_src, docs_dst)
        
        # Copy README files
        for readme in ["README.md", "STARTUP_SCRIPTS.md"]:
            src = self.repo_root / readme
            if src.exists():
                shutil.copy2(src, docs_dst)
        
        # Copy license
        license_src = self.repo_root / "license.txt"
        if license_src.exists():
            shutil.copy2(license_src, self.package_path)
        
        return True
    
    def copy_setup_scripts(self):
        """Copy environment setup scripts."""
        self.print_status("Copying environment setup...", "INFO")
        
        for script in ["setup_java.ps1", "setup_java.bat"]:
            src = self.repo_root / script
            if src.exists():
                shutil.copy2(src, self.package_path)
        
        return True
    
    def create_unified_scripts(self):
        """Create start_all scripts."""
        self.print_status("Creating unified startup scripts...", "INFO")
        
        # Detect actual Marvin config filename in Marvin folder
        marvin_config = "Application.xml"
        marvin_dir = self.package_path / "Marvin"
        if marvin_dir.exists():
            # Look for common Marvin config names
            for config_name in ["Application.xml", "ApplicationConfig.xml", "MarvinConfig.xml", "App.Config.xml"]:
                if (marvin_dir / config_name).exists():
                    marvin_config = config_name
                    self.print_status(f"Detected Marvin config: {config_name}", "INFO")
                    break
        
        # PowerShell version
        ps1_content = f'''# =============================================================================
# Start All BIFF Components
# =============================================================================
# Starts Oscar (background) and Marvin (foreground)
# Minion must be started separately as it's typically on remote systems
# =============================================================================

param(
    [string]$MarvinConfig = "Marvin\\{marvin_config}",
    [string]$OscarConfig = "Oscar\\OscarConfig.xml",
    [string]$MinionConfig = "Minion\\MinionConfig.xml",
    [switch]$Help
)

if ($Help) {{
    Write-Host @"
============================================================
  Start All BIFF Components
============================================================

USAGE:
  .\\start_all.ps1 [-MarvinConfig <path>] [-OscarConfig <path>] [-MinionConfig <path>]

OPTIONS:
  -MarvinConfig <path>   Marvin configuration file (default: Marvin\\Application.xml)
  -OscarConfig <path>    Oscar configuration file (default: Oscar\\OscarConfig.xml)
  -MinionConfig <path>   Minion configuration file (default: Minion\\MinionConfig.xml)
  -Help                  Show this help message

EXAMPLE:
  .\\start_all.ps1
  .\\start_all.ps1 -MarvinConfig Marvin\\MyConfig.xml

"@
    exit 0
}}

Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "  Starting BIFF Components" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# Start Oscar in background
Write-Host "[1/2] Starting Oscar (background)..." -ForegroundColor Yellow
Push-Location Oscar
& .\\start_oscar.ps1 -ConfigFile "OscarConfig.xml" -Background
Pop-Location

Start-Sleep -Seconds 3

# Start Marvin in foreground
Write-Host ""
Write-Host "[2/2] Starting Marvin (foreground)..." -ForegroundColor Yellow
Write-Host "      Close Marvin window to stop" -ForegroundColor Cyan
Write-Host ""
Push-Location Marvin
& .\\start_marvin.ps1 -ConfigFile "{marvin_config}"
Pop-Location
'''
        
        (self.package_path / "start_all.ps1").write_text(ps1_content, encoding='utf-8')
        
        # Batch version
        bat_content = f'''@echo off
REM =============================================================================
REM Start All BIFF Components
REM =============================================================================

setlocal

set MARVIN_CONFIG=Configs\\{marvin_config}
set OSCAR_CONFIG=Configs\\OscarConfig.xml

echo.
echo ============================================================
echo   Starting BIFF Components
echo ============================================================
echo.

REM Start Oscar in background
echo [1/2] Starting Oscar (background)...
cd Oscar
start /B "BIFF Oscar" cmd /c "start_oscar.bat ..\\%OSCAR_CONFIG%"
cd ..

timeout /t 3 /nobreak >nul

REM Start Marvin in foreground
echo.
echo [2/2] Starting Marvin (foreground)...
echo       Close Marvin window to stop
echo.
cd Marvin
call start_marvin.bat ..\\%MARVIN_CONFIG%
cd ..

endlocal
'''
        
        (self.package_path / "start_all.bat").write_text(bat_content, encoding='utf-8')
        
        return True
    
    def create_readme(self):
        """Create comprehensive deployment README."""
        self.print_status("Creating deployment README...", "INFO")
        
        readme_content = f'''# BIFF Deployment Package

**Version**: {self.version}  
**Build Date**: {self.timestamp}  
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
.\\start_all.ps1
# OR
start_all.bat
```

**Option B: Start Components Individually**
```powershell
# Start Oscar (data broker) in background
cd Oscar
.\\start_oscar.ps1 -ConfigFile ..\\Configs\\OscarConfig.xml -Background

# Start Marvin (GUI) in foreground
cd Marvin
.\\start_marvin.ps1 -ConfigFile ..\\Configs\\MarvinConfig.xml

# Start Minion (collector) - typically on data source systems
cd Minion
.\\start_minion.ps1 -ConfigFile ..\\Configs\\MinionConfig.xml
```

### 3. Verify Operation

1. **Oscar Status**: `cd Oscar; .\\status_oscar.ps1`
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
Version: {self.version}  
Build: {self.timestamp}  
Built with BIFF Package Builder
'''
        
        (self.package_path / "README.md").write_text(readme_content, encoding='utf-8')
        
        return True
    
    def print_summary(self):
        """Print package summary."""
        print()
        print("=" * 60)
        print("  Package Created Successfully!")
        print("=" * 60)
        print()
        print(f"Package Location: {self.package_name}")
        print()
        print("Contents:")
        
        # Get JAR size
        jar_path = self.package_path / "Marvin" / "BIFF.Marvin.jar"
        if jar_path.exists():
            jar_size_mb = jar_path.stat().st_size / (1024 * 1024)
            print(f"  - Marvin GUI ({jar_size_mb:.1f} MB)")
        else:
            print(f"  - Marvin GUI (NOT FOUND)")
        
        print("  - Oscar Broker (Python)")
        print("  - Minion Collector (Python)")
        print("  - Startup Scripts (PowerShell + Batch)")
        print("  - Configuration Templates")
        print("  - Documentation")
        print()
        print("Next Steps:")
        print(f"  1. Copy '{self.package_name}' to deployment location")
        print("  2. Edit Configs/*.xml for your environment")
        print("  3. Run setup_java.ps1 (if Java not in PATH)")
        print("  4. Run start_all.ps1 or start_all.bat")
        print()
        print(f"Full instructions: {self.package_name}\\README.md")
        print()
    
    def build(self):
        """Execute full build process."""
        print()
        print("=" * 60)
        print("  BIFF Package Builder")
        print("=" * 60)
        print()
        print(f"Package: {self.package_name}")
        print(f"Version: {self.version}")
        print()
        
        # Check prerequisites first
        if not self.check_prerequisites():
            self.print_status("Prerequisite check failed. Aborting.", "ERROR")
            return False
        
        print()
        
        steps = [
            ("Build Marvin", self.build_marvin),
            ("Create Structure", self.create_structure),
            ("Copy Marvin", self.copy_marvin),
            ("Copy Oscar", self.copy_oscar),
            ("Copy Minion", self.copy_minion),
            ("Copy Configs", self.copy_configs),
            ("Copy Documentation", self.copy_documentation),
            ("Copy Setup Scripts", self.copy_setup_scripts),
            ("Create Unified Scripts", self.create_unified_scripts),
            ("Create README", self.create_readme)
        ]
        
        for step_name, step_func in steps:
            if not step_func():
                self.print_status(f"{step_name} failed", "ERROR")
                return False
        
        self.print_summary()
        return True


def main():
    parser = argparse.ArgumentParser(
        description="BIFF Package Builder - Create Standalone Distribution",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--output-dir", default="BIFF-Package",
                       help="Output directory name (default: BIFF-Package)")
    parser.add_argument("--config-source", default="",
                       help="Copy configs from directory (e.g., biff-agents/biff-quickstart-test)")
    parser.add_argument("--skip-build", action="store_true",
                       help="Skip Marvin build (use existing JAR)")
    
    args = parser.parse_args()
    
    builder = PackageBuilder(args)
    success = builder.build()
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
