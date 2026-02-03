# ==============================================================================
# BIFF Oscar - Background Startup Script for Windows
# ==============================================================================
# Purpose: Start Oscar data broker in background with automatic Python detection
# Usage:   .\start_oscar.ps1 [-ConfigFile path] [-Verbose] [-NoGUI] [-Help]
# ==============================================================================

param(
    [string]$ConfigFile = "OscarConfig.xml",
    [switch]$Verbose,
    [switch]$NoGUI,
    [switch]$Help
)

# Display help and exit
if ($Help) {
    Write-Host @"
============================================================
  BIFF Oscar - Background Startup Script
============================================================

USAGE:
  .\start_oscar.ps1 [OPTIONS]

OPTIONS:
  -ConfigFile <path>    Configuration file (default: OscarConfig.xml)
  -Verbose              Enable verbose logging
  -NoGUI                Disable Oscar GUI
  -Help                 Show this help message

EXAMPLES:
  .\start_oscar.ps1
      Start with default configuration

  .\start_oscar.ps1 -ConfigFile ../biff-agents/quickstart_configs/OscarConfig.xml
      Start with custom configuration

  .\start_oscar.ps1 -Verbose
      Start with verbose logging enabled

  .\start_oscar.ps1 -NoGUI
      Start without GUI

MANAGEMENT:
  Status:   .\status_oscar.ps1
  Stop:     .\stop_oscar.ps1
  Logs:     Get-Content OscarLog.txt -Wait -Tail 20

"@
    exit 0
}

# Color output helper
function Write-ColorOutput {
    param([string]$Message, [string]$Color = "White")
    Write-Host $Message -ForegroundColor $Color
}

# Banner
Write-Host ""
Write-ColorOutput "============================================================" "Cyan"
Write-ColorOutput "  BIFF Oscar - Starting Data Broker" "Cyan"
Write-ColorOutput "============================================================" "Cyan"
Write-Host ""

# Check for Python
Write-ColorOutput "[INFO] Searching for Python..." "Yellow"

$PythonPaths = @(
    "python",
    "python3",
    "C:\Program Files\Python312\python.exe",
    "C:\Program Files\Python311\python.exe",
    "C:\Program Files\Python310\python.exe",
    "$env:LOCALAPPDATA\Programs\Python\Python312\python.exe",
    "$env:LOCALAPPDATA\Programs\Python\Python311\python.exe",
    "$env:LOCALAPPDATA\Programs\Python\Python310\python.exe"
)

$PythonCmd = $null
foreach ($path in $PythonPaths) {
    try {
        $result = & $path --version 2>&1
        if ($LASTEXITCODE -eq 0) {
            $PythonCmd = $path
            Write-ColorOutput "[INFO] Python found: $result" "Green"
            break
        }
    } catch {
        continue
    }
}

if (-not $PythonCmd) {
    Write-ColorOutput "[ERROR] Python not found!" "Red"
    Write-Host ""
    Write-Host "Please install Python 3.7+ from:"
    Write-Host "  https://www.python.org/downloads/"
    Write-Host ""
    Write-Host "Make sure to check 'Add Python to PATH' during installation."
    exit 1
}

# Validate configuration file
if (-not (Test-Path $ConfigFile)) {
    Write-ColorOutput "[ERROR] Configuration file not found: $ConfigFile" "Red"
    Write-Host ""
    Write-Host "Available configuration files:"
    Get-ChildItem -Filter "*.xml" | ForEach-Object {
        Write-Host "  - $($_.Name)"
    }
    Write-Host ""
    exit 1
}

$ConfigFile = Resolve-Path $ConfigFile
Write-ColorOutput "[INFO] Configuration: $ConfigFile" "Green"

# Check for existing Oscar instance
$PidFile = Join-Path $PSScriptRoot ".oscar.pid"
$ExistingOscar = $null

if (Test-Path $PidFile) {
    $SavedPID = Get-Content $PidFile -ErrorAction SilentlyContinue
    if ($SavedPID) {
        try {
            $ExistingOscar = Get-Process -Id $SavedPID -ErrorAction Stop
            Write-ColorOutput "[WARNING] Oscar may already be running (PID: $SavedPID)" "Yellow"
            Write-Host ""
            $response = Read-Host "Stop existing instance and restart? (y/n)"
            if ($response -eq "y" -or $response -eq "Y") {
                Stop-Process -Id $SavedPID -Force
                Start-Sleep -Seconds 2
                Remove-Item $PidFile -Force -ErrorAction SilentlyContinue
                Write-ColorOutput "[INFO] Existing instance stopped" "Green"
            } else {
                Write-ColorOutput "[INFO] Startup cancelled" "Yellow"
                exit 0
            }
        } catch {
            # PID file exists but process is dead - clean up
            Write-ColorOutput "[INFO] Cleaning up stale PID file" "Yellow"
            Remove-Item $PidFile -Force -ErrorAction SilentlyContinue
        }
    }
}

# Build command arguments
$OscarArgs = @("Oscar.py", "-i", $ConfigFile)
if ($Verbose) {
    $OscarArgs += "-v"
}
if ($NoGUI) {
    $OscarArgs += "--nogui"
}

# Start Oscar in background
Write-ColorOutput "[INFO] Starting Oscar in background..." "Yellow"

try {
    $ProcessInfo = New-Object System.Diagnostics.ProcessStartInfo
    $ProcessInfo.FileName = $PythonCmd
    $ProcessInfo.Arguments = $OscarArgs -join " "
    $ProcessInfo.WorkingDirectory = $PSScriptRoot
    $ProcessInfo.UseShellExecute = $false
    $ProcessInfo.CreateNoWindow = $true
    $ProcessInfo.RedirectStandardOutput = $true
    $ProcessInfo.RedirectStandardError = $true

    $Process = New-Object System.Diagnostics.Process
    $Process.StartInfo = $ProcessInfo
    
    # Start process
    [void]$Process.Start()
    
    # Save PID
    $Process.Id | Out-File $PidFile -Encoding ASCII
    
    # Wait briefly to check for immediate failures
    Start-Sleep -Seconds 2
    
    if ($Process.HasExited) {
        Write-ColorOutput "[ERROR] Oscar failed to start!" "Red"
        Write-Host ""
        $errorOutput = $Process.StandardError.ReadToEnd()
        if ($errorOutput) {
            Write-Host $errorOutput
        }
        Remove-Item $PidFile -Force -ErrorAction SilentlyContinue
        exit 1
    }
    
    # Success!
    Write-Host ""
    Write-ColorOutput "============================================================" "Green"
    Write-ColorOutput "  Oscar Started Successfully!" "Green"
    Write-ColorOutput "============================================================" "Green"
    Write-Host ""
    Write-Host "  Process ID:    $($Process.Id)"
    Write-Host "  Configuration: $(Split-Path $ConfigFile -Leaf)"
    Write-Host "  Port:          1100 (default)"
    Write-Host ""
    Write-ColorOutput "Management Commands:" "Cyan"
    Write-Host "  Status:  .\status_oscar.ps1"
    Write-Host "  Stop:    .\stop_oscar.ps1"
    Write-Host "  Logs:    Get-Content OscarLog.txt -Wait -Tail 20"
    Write-Host ""
    
} catch {
    Write-ColorOutput "[ERROR] Failed to start Oscar: $_" "Red"
    Remove-Item $PidFile -Force -ErrorAction SilentlyContinue
    exit 1
}
