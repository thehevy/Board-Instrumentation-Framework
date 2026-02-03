"""
Build Orchestrator for BIFF Marvin Component

Handles the automated build sequence:
1. Build Enzo gauge library (Marvin dependency)
2. Copy Enzo JAR to Marvin dependencies
3. Build Marvin application JAR
4. Verify all artifacts are created correctly

This implements the critical build order required by Marvin's dependency structure.
"""

import os
import subprocess
import platform
from pathlib import Path
from typing import Dict, Optional, Tuple


class BuildResult:
    """Result of a build operation"""
    def __init__(self, success: bool, message: str = "", output: str = "", error: str = ""):
        self.success = success
        self.message = message
        self.output = output
        self.error = error


class BuildOrchestrator:
    """
    Orchestrates the complete Marvin build process with correct dependency ordering.
    
    Build sequence:
    1. Build Enzo (gauge library)
    2. Copy Enzo JAR to Marvin/Dependencies/
    3. Build Marvin application
    4. Verify artifacts exist and are valid
    """
    
    def __init__(self, workspace_root: str):
        """
        Initialize build orchestrator.
        
        Args:
            workspace_root: Path to Board-Instrumentation-Framework root directory
        """
        self.workspace = Path(workspace_root)
        self.marvin_dir = self.workspace / "Marvin"
        self.enzo_dir = self.marvin_dir / "Dependencies" / "Enzo"
        self.build_log = []
        
    def execute(self, verbose: bool = False) -> BuildResult:
        """
        Execute complete build sequence.
        
        Args:
            verbose: Print detailed progress messages
            
        Returns:
            BuildResult with overall success status
        """
        steps = [
            ("Building dependencies (Enzo)", self.build_dependencies),
            ("Building Marvin application", self.build_marvin),
            ("Verifying artifacts", self.verify_artifacts),
        ]
        
        for step_name, step_func in steps:
            if verbose:
                print(f"  [{step_name}...]", end="", flush=True)
            
            result = step_func()
            
            if not result.success:
                if verbose:
                    print(f" ✗ FAILED")
                    print(f"    Error: {result.message}")
                    if result.error:
                        print(f"    Details: {result.error[:200]}")
                return result
            
            if verbose:
                print(f" ✓")
                
        return BuildResult(
            success=True,
            message="Marvin build completed successfully",
            output="\n".join(self.build_log)
        )
    
    def build_dependencies(self) -> BuildResult:
        """Build Enzo and copy JAR in one step using buildDeps task"""
        gradlew = self._get_gradlew_command()
        cmd = [gradlew, "buildDeps"]
        
        return self._run_command(cmd, cwd=self.marvin_dir, timeout=300)
    
    def build_enzo(self) -> BuildResult:
        """Build the Enzo gauge library dependency"""
        if not self.enzo_dir.exists():
            return BuildResult(
                success=False,
                message=f"Enzo directory not found: {self.enzo_dir}"
            )
        
        gradlew = self._get_gradlew_command()
        cmd = [gradlew, "build"]
        
        return self._run_command(cmd, cwd=self.enzo_dir, timeout=300)
    
    def copy_enzo_jar(self) -> BuildResult:
        """Copy built Enzo JAR to Marvin dependencies"""
        gradlew = self._get_gradlew_command()
        cmd = [gradlew, "copyEnzoJar"]
        
        return self._run_command(cmd, cwd=self.marvin_dir, timeout=60)
    
    def build_marvin(self) -> BuildResult:
        """Build the Marvin application JAR"""
        gradlew = self._get_gradlew_command()
        cmd = [gradlew, "build"]
        
        return self._run_command(cmd, cwd=self.marvin_dir, timeout=300)
    
    def verify_artifacts(self) -> BuildResult:
        """Verify that all required build artifacts exist"""
        artifacts = {
            "Marvin JAR": self.marvin_dir / "build" / "libs" / "BIFF.Marvin.jar",
            "Enzo JAR": self.marvin_dir / "Dependencies" / "Enzo-0.3.6a.jar",
            "Widget directory": self.marvin_dir / "Widget",
        }
        
        missing = []
        for name, path in artifacts.items():
            if not path.exists():
                missing.append(f"{name}: {path}")
            elif path.is_file() and path.stat().st_size < 1000:
                missing.append(f"{name}: file too small ({path.stat().st_size} bytes)")
        
        if missing:
            return BuildResult(
                success=False,
                message="Build artifacts missing or invalid:\n  " + "\n  ".join(missing)
            )
        
        return BuildResult(
            success=True,
            message="All build artifacts verified"
        )
    
    def get_marvin_jar_path(self) -> Optional[Path]:
        """Get the path to the built Marvin JAR file"""
        jar_path = self.marvin_dir / "build" / "libs" / "BIFF.Marvin.jar"
        return jar_path if jar_path.exists() else None
    
    def is_build_needed(self) -> bool:
        """Check if Marvin needs to be built (JAR missing or stale)"""
        jar_path = self.get_marvin_jar_path()
        if not jar_path:
            return True
        
        # Check if any source files are newer than JAR
        src_dir = self.marvin_dir / "src"
        if not src_dir.exists():
            return True
        
        jar_mtime = jar_path.stat().st_mtime
        
        # Check a few key source files
        key_files = [
            src_dir / "main" / "java" / "kutch" / "biff" / "marvin" / "Marvin.java",
            self.marvin_dir / "build.gradle",
        ]
        
        for key_file in key_files:
            if key_file.exists() and key_file.stat().st_mtime > jar_mtime:
                return True
        
        return False
    
    def _get_gradlew_command(self) -> str:
        """Get the correct gradlew command for the current platform"""
        if platform.system() == "Windows":
            return "gradlew.bat"
        else:
            return "./gradlew"
    
    def _run_command(self, cmd: list, cwd: Path, timeout: int = 300) -> BuildResult:
        """
        Run a command and capture output.
        
        Args:
            cmd: Command and arguments
            cwd: Working directory
            timeout: Timeout in seconds
            
        Returns:
            BuildResult with command execution status
        """
        try:
            result = subprocess.run(
                cmd,
                cwd=str(cwd),
                capture_output=True,
                text=True,
                timeout=timeout
            )
            
            log_entry = f"{' '.join(cmd)} in {cwd}: exit code {result.returncode}"
            self.build_log.append(log_entry)
            
            if result.returncode == 0:
                return BuildResult(
                    success=True,
                    message=f"Command succeeded: {' '.join(cmd)}",
                    output=result.stdout
                )
            else:
                return BuildResult(
                    success=False,
                    message=f"Command failed with exit code {result.returncode}",
                    output=result.stdout,
                    error=result.stderr
                )
                
        except subprocess.TimeoutExpired:
            return BuildResult(
                success=False,
                message=f"Command timed out after {timeout} seconds"
            )
        except FileNotFoundError:
            return BuildResult(
                success=False,
                message=f"Command not found: {cmd[0]}"
            )
        except Exception as e:
            return BuildResult(
                success=False,
                message=f"Unexpected error: {str(e)}"
            )


class MarvinLauncher:
    """
    Launches Marvin GUI application.
    
    Handles finding the JAR, ensuring Widget directory is accessible,
    and constructing the correct java command.
    """
    
    def __init__(self, workspace_root: str):
        """
        Initialize Marvin launcher.
        
        Args:
            workspace_root: Path to Board-Instrumentation-Framework root directory
        """
        self.workspace = Path(workspace_root)
        self.marvin_dir = self.workspace / "Marvin"
    
    def launch(self, config_file: str, background: bool = False) -> Tuple[bool, str]:
        """
        Launch Marvin GUI.
        
        Args:
            config_file: Path to Marvin Application.xml file
            background: Run in background (non-blocking)
            
        Returns:
            Tuple of (success, message)
        """
        # Find JAR
        jar_path = self.marvin_dir / "build" / "libs" / "BIFF.Marvin.jar"
        if not jar_path.exists():
            return False, f"Marvin JAR not found: {jar_path}"
        
        # Verify Widget directory exists
        widget_dir = self.marvin_dir / "Widget"
        if not widget_dir.exists():
            return False, f"Widget directory not found: {widget_dir}"
        
        # Construct command
        cmd = [
            "java",
            "-jar",
            str(jar_path),
            "-a",
            str(config_file)
        ]
        
        try:
            if background:
                # Launch in background
                subprocess.Popen(
                    cmd,
                    cwd=str(self.marvin_dir),
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
                return True, "Marvin launched in background"
            else:
                # Launch in foreground (blocks)
                result = subprocess.run(
                    cmd,
                    cwd=str(self.marvin_dir)
                )
                return True, f"Marvin exited with code {result.returncode}"
                
        except FileNotFoundError:
            return False, "Java not found. Ensure Java 10+ is installed and in PATH."
        except Exception as e:
            return False, f"Failed to launch Marvin: {str(e)}"
