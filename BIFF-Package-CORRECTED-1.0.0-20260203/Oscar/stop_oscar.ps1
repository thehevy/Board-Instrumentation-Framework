# ==============================================================================
# BIFF Oscar - Stop Script for Windows
# ==============================================================================
# Purpose: Gracefully stop running Oscar instance(s)
# Usage:   .\stop_oscar.ps1
# ==============================================================================

# Color output helper
function Write-ColorOutput {
    param([string]$Message, [string]$Color = "White")
    Write-Host $Message -ForegroundColor $Color
}

# Banner
Write-Host ""
Write-ColorOutput "============================================================" "Cyan"
Write-ColorOutput "  BIFF Oscar - Stopping Data Broker" "Cyan"
Write-ColorOutput "============================================================" "Cyan"
Write-Host ""

$PidFile = Join-Path $PSScriptRoot ".oscar.pid"
$StoppedAny = $false

# Try to stop Oscar using PID file
if (Test-Path $PidFile) {
    $SavedPID = Get-Content $PidFile -ErrorAction SilentlyContinue
    if ($SavedPID) {
        try {
            $OscarProcess = Get-Process -Id $SavedPID -ErrorAction Stop
            Write-ColorOutput "[INFO] Stopping Oscar (PID: $SavedPID)..." "Yellow"
            Stop-Process -Id $SavedPID -Force
            Start-Sleep -Seconds 1
            Write-ColorOutput "[SUCCESS] Oscar stopped (PID: $SavedPID)" "Green"
            $StoppedAny = $true
        } catch {
            Write-ColorOutput "[WARNING] PID file exists but process not found (PID: $SavedPID)" "Yellow"
        }
    }
    Remove-Item $PidFile -Force -ErrorAction SilentlyContinue
}

# Fallback: Find Oscar by process name
$OscarProcesses = Get-Process -Name "python*" -ErrorAction SilentlyContinue | Where-Object {
    try {
        $_.MainModule.FileName -and (Get-Process -Id $_.Id).CommandLine -like "*Oscar.py*"
    } catch {
        $false
    }
}

if ($OscarProcesses) {
    foreach ($proc in $OscarProcesses) {
        Write-ColorOutput "[INFO] Found Oscar process (PID: $($proc.Id))" "Yellow"
        try {
            Stop-Process -Id $proc.Id -Force
            Write-ColorOutput "[SUCCESS] Oscar stopped (PID: $($proc.Id))" "Green"
            $StoppedAny = $true
        } catch {
            Write-ColorOutput "[ERROR] Failed to stop Oscar (PID: $($proc.Id)): $_" "Red"
        }
    }
}

if (-not $StoppedAny) {
    Write-ColorOutput "[INFO] No running Oscar instances found" "Yellow"
}

Write-Host ""
