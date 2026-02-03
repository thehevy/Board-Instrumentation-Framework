# =============================================================================
# Start Minion with automatic cleanup of existing instances
# =============================================================================
# Usage: .\start_minion.ps1 -ConfigFile <config.xml> [-Args @("-v")]
# Example: .\start_minion.ps1 -ConfigFile MinionConfig.xml -Args @("-v")
#
# This script:
# 1. Checks if Minion is already running with the same config
# 2. Stops the existing instance if found
# 3. Launches new instance with specified config
# =============================================================================

param(
    [Parameter(Mandatory=$true)]
    [string]$ConfigFile,
    
    [Parameter(Mandatory=$false)]
    [string[]]$Args = @()
)

# Get absolute path to config file
$configPath = (Resolve-Path $ConfigFile -ErrorAction SilentlyContinue).Path
if (-not $configPath) {
    Write-Host "ERROR: Configuration file not found: $ConfigFile" -ForegroundColor Red
    exit 1
}

# Check for Python
try {
    python --version 2>&1 | Out-Null
    if ($LASTEXITCODE -ne 0) {
        throw "Python not found"
    }
} catch {
    Write-Host "ERROR: Python not found in PATH" -ForegroundColor Red
    exit 1
}

# Check for Minion.py
if (-not (Test-Path "Minion.py")) {
    Write-Host "ERROR: Minion.py not found in current directory" -ForegroundColor Red
    Write-Host "Run this script from the Minion directory" -ForegroundColor Yellow
    exit 1
}

Write-Host "Checking for existing Minion instance with config: $configPath" -ForegroundColor Cyan

# Find and kill existing instance with same config
$existingProcesses = Get-WmiObject Win32_Process -Filter "name='python.exe'" | Where-Object {
    $_.CommandLine -like "*Minion.py*" -and $_.CommandLine -like "*$configPath*"
}

if ($existingProcesses) {
    foreach ($proc in $existingProcesses) {
        Write-Host "Stopping existing Minion instance (PID: $($proc.ProcessId))" -ForegroundColor Yellow
        Stop-Process -Id $proc.ProcessId -Force
    }
    Start-Sleep -Seconds 1
    Write-Host "Existing instance stopped" -ForegroundColor Green
} else {
    Write-Host "No existing instance found" -ForegroundColor Green
}

Write-Host ""
Write-Host "Starting Minion with config: $configPath" -ForegroundColor Cyan
Write-Host "Additional args: $Args" -ForegroundColor Cyan
Write-Host ""

# Launch Minion
$allArgs = @("-i", $configPath) + $Args
& python Minion.py $allArgs
