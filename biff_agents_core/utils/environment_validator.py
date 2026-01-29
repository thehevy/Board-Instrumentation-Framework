"""
Environment detection and validation for BIFF prerequisites.

Checks for Java 10+, Python 3.9+, port availability, and system requirements.
"""

import subprocess
import platform
import socket
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Tuple


class EnvironmentValidator:
    """Validate system environment for BIFF deployment"""
    
    def __init__(self):
        self.issues = []
        self.warnings = []
        self.info = []
    
    def validate_all(self) -> Dict[str, any]:
        """Run all validation checks"""
        results = {
            "java": self.check_java_version(),
            "python": self.check_python_version(),
            "ports": self.check_ports_available([1100, 52001]),
            "system": self.check_system_resources(),
            "issues": self.issues,
            "warnings": self.warnings,
            "info": self.info,
            "ready": len(self.issues) == 0
        }
        return results
    
    def check_java_version(self) -> Dict[str, any]:
        """Check if Java 10+ is installed"""
        try:
            result = subprocess.run(
                ["java", "-version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            # Java prints version to stderr
            version_output = result.stderr
            
            # Parse version (format: "openjdk version "11.0.2"" or "java version "1.8.0_291"")
            if "version" in version_output:
                # Extract version number
                import re
                match = re.search(r'version "([^"]+)"', version_output)
                if match:
                    version_str = match.group(1)
                    
                    # Handle both "11.x.x" and "1.8.x" formats
                    if version_str.startswith("1."):
                        major = int(version_str.split(".")[1])
                    else:
                        major = int(version_str.split(".")[0])
                    
                    if major >= 10:
                        self.info.append(f"✓ Java {major} detected (minimum: 10)")
                        return {"installed": True, "version": version_str, "sufficient": True}
                    else:
                        self.issues.append(f"✗ Java {major} detected, but Marvin requires Java 10+ (recommended: Java 11)")
                        return {"installed": True, "version": version_str, "sufficient": False}
            
            self.warnings.append("⚠ Java installed but version could not be determined")
            return {"installed": True, "version": "unknown", "sufficient": False}
            
        except FileNotFoundError:
            self.issues.append("✗ Java not found in PATH. Marvin requires Java 10+")
            return {"installed": False, "version": None, "sufficient": False}
        except subprocess.TimeoutExpired:
            self.warnings.append("⚠ Java check timed out")
            return {"installed": None, "version": None, "sufficient": False}
    
    def check_python_version(self) -> Dict[str, any]:
        """Check if Python 3.9+ is installed"""
        import sys
        
        major = sys.version_info.major
        minor = sys.version_info.minor
        
        if major >= 3 and minor >= 9:
            self.info.append(f"✓ Python {major}.{minor} detected (minimum: 3.9)")
            return {"installed": True, "version": f"{major}.{minor}", "sufficient": True}
        else:
            self.issues.append(f"✗ Python {major}.{minor} detected, but biff-agents requires Python 3.9+")
            return {"installed": True, "version": f"{major}.{minor}", "sufficient": False}
    
    def check_ports_available(self, ports: List[int]) -> Dict[str, any]:
        """Check if UDP ports are available"""
        available = []
        in_use = []
        
        for port in ports:
            if self.is_port_available(port):
                available.append(port)
                self.info.append(f"✓ Port {port} available")
            else:
                in_use.append(port)
                self.warnings.append(f"⚠ Port {port} already in use (may conflict with BIFF components)")
        
        return {
            "available": available,
            "in_use": in_use,
            "all_available": len(in_use) == 0
        }
    
    def is_port_available(self, port: int, protocol: str = "UDP") -> bool:
        """Check if a specific port is available"""
        try:
            if protocol.upper() == "UDP":
                sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            else:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            
            sock.bind(("", port))
            sock.close()
            return True
        except OSError:
            return False
    
    def check_system_resources(self) -> Dict[str, any]:
        """Check system resources (CPU, memory, disk)"""
        try:
            import psutil
            
            cpu_count = psutil.cpu_count()
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage("/")
            
            # Recommendations:
            # - 2+ CPU cores
            # - 4GB+ RAM
            # - 1GB+ free disk
            
            results = {
                "cpu_cores": cpu_count,
                "memory_total_gb": memory.total / (1024**3),
                "memory_available_gb": memory.available / (1024**3),
                "disk_free_gb": disk.free / (1024**3)
            }
            
            if cpu_count >= 2:
                self.info.append(f"✓ {cpu_count} CPU cores available")
            else:
                self.warnings.append(f"⚠ Only {cpu_count} CPU core(s). Recommended: 2+")
            
            if memory.available / (1024**3) >= 4:
                self.info.append(f"✓ {memory.available / (1024**3):.1f} GB RAM available")
            else:
                self.warnings.append(f"⚠ Only {memory.available / (1024**3):.1f} GB RAM available. Recommended: 4GB+")
            
            if disk.free / (1024**3) >= 1:
                self.info.append(f"✓ {disk.free / (1024**3):.1f} GB disk space available")
            else:
                self.warnings.append(f"⚠ Only {disk.free / (1024**3):.1f} GB disk space. Recommended: 1GB+")
            
            return results
            
        except ImportError:
            self.info.append("ℹ psutil not installed - skipping detailed resource checks")
            return {"available": False}
    
    def check_gradle(self) -> Dict[str, any]:
        """Check if Gradle is available (for Marvin builds)"""
        # Check for gradlew first (bundled with Marvin)
        marvin_gradlew = Path("Marvin/gradlew.bat" if platform.system() == "Windows" else "Marvin/gradlew")
        
        if marvin_gradlew.exists():
            self.info.append("✓ Gradle wrapper (gradlew) found in Marvin directory")
            return {"installed": True, "bundled": True}
        
        # Check for system Gradle
        if shutil.which("gradle"):
            try:
                result = subprocess.run(
                    ["gradle", "--version"],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                
                if "Gradle" in result.stdout:
                    self.info.append("✓ Gradle found in PATH")
                    return {"installed": True, "bundled": False}
            except:
                pass
        
        self.warnings.append("⚠ Gradle not found - Marvin builds may require manual setup")
        return {"installed": False}
    
    def suggest_fixes(self) -> List[str]:
        """Generate fix suggestions for detected issues"""
        fixes = []
        
        if any("Java not found" in issue for issue in self.issues):
            if platform.system() == "Windows":
                fixes.append("Install Java 11+ from: https://adoptium.net/")
                fixes.append("After installation, add Java to PATH")
            else:
                fixes.append("Install Java 11+:")
                fixes.append("  Ubuntu/Debian: sudo apt install openjdk-11-jdk")
                fixes.append("  RHEL/Rocky: sudo dnf install java-11-openjdk")
        
        if any("Python" in issue and "requires" in issue for issue in self.issues):
            fixes.append("Upgrade Python to 3.9+:")
            fixes.append("  Download from: https://www.python.org/downloads/")
        
        if any("Port" in warning and "in use" in warning for warning in self.warnings):
            fixes.append("Ports in use:")
            fixes.append("  - Check for existing BIFF components: ps aux | grep -E '(Minion|Oscar|Marvin)'")
            fixes.append("  - Or configure BIFF to use different ports in configs")
        
        return fixes
    
    def print_summary(self):
        """Print validation summary"""
        print("\n" + "="*60)
        print("BIFF Environment Validation")
        print("="*60 + "\n")
        
        for info in self.info:
            print(info)
        
        if self.warnings:
            print()
            for warning in self.warnings:
                print(warning)
        
        if self.issues:
            print()
            for issue in self.issues:
                print(issue)
            
            print("\n" + "="*60)
            print("FIXES NEEDED:")
            print("="*60 + "\n")
            
            fixes = self.suggest_fixes()
            for fix in fixes:
                print(fix)
            
            print("\n✗ Environment validation FAILED")
        else:
            print("\n✓ Environment validation PASSED - Ready for BIFF deployment!")
        
        print("="*60 + "\n")
