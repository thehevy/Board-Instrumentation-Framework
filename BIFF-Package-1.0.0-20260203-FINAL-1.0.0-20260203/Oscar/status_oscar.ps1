# ==============================================================================
# BIFF Oscar - Status Check Script for Windows
# ==============================================================================
# Purpose: Display runtime status and diagnostics for Oscar
# Usage:   .\status_oscar.ps1
# ==============================================================================

# Color output helper
function Write-ColorOutput {
    param([string]$Message, [string]$Color = "White")
    Write-Host $Message -ForegroundColor $Color
}

# Format bytes to human-readable
function Format-Bytes {
    param([double]$Bytes)
    $sizes = "B","KB","MB","GB","TB"
    $order = 0
    while ($Bytes -ge 1024 -and $order -lt $sizes.Length - 1) {
        $Bytes = $Bytes / 1024
        $order++
    }
    return "{0:N2} {1}" -f $Bytes, $sizes[$order]
}

# Banner
Write-Host ""
Write-ColorOutput "============================================================" "Cyan"
Write-ColorOutput "  BIFF Oscar - Status Check" "Cyan"
Write-ColorOutput "============================================================" "Cyan"
Write-Host ""

$PidFile = Join-Path $PSScriptRoot ".oscar.pid"
$LogFile = Join-Path $PSScriptRoot "OscarLog.txt"
$OscarProcess = $null

# Try to find Oscar by PID file
if (Test-Path $PidFile) {
    $SavedPID = Get-Content $PidFile -ErrorAction SilentlyContinue
    if ($SavedPID) {
        try {
            $OscarProcess = Get-Process -Id $SavedPID -ErrorAction Stop
        } catch {
            Write-ColorOutput "[WARNING] PID file exists but process not found" "Yellow"
            Remove-Item $PidFile -Force -ErrorAction SilentlyContinue
        }
    }
}

# Fallback: Find Oscar by process search
if (-not $OscarProcess) {
    $OscarProcesses = Get-Process -Name "python*" -ErrorAction SilentlyContinue | Where-Object {
        try {
            (Get-Process -Id $_.Id).CommandLine -like "*Oscar.py*"
        } catch {
            $false
        }
    }
    if ($OscarProcesses) {
        $OscarProcess = $OscarProcesses[0]
    }
}

# Display status
if ($OscarProcess) {
    Write-ColorOutput "[STATUS] Oscar is running" "Green"
    Write-Host ""
    
    # Process information
    Write-ColorOutput "Process Information:" "Cyan"
    Write-Host "  PID:          $($OscarProcess.Id)"
    Write-Host "  CPU:          $($OscarProcess.CPU)s"
    Write-Host "  Memory:       $(Format-Bytes ($OscarProcess.WorkingSet64))"
    Write-Host "  Start Time:   $($OscarProcess.StartTime)"
    
    $Runtime = (Get-Date) - $OscarProcess.StartTime
    Write-Host "  Running For:  $($Runtime.ToString('hh\:mm\:ss'))"
    Write-Host ""
    
    # Log file information
    if (Test-Path $LogFile) {
        $LogInfo = Get-Item $LogFile
        Write-ColorOutput "Log File:" "Cyan"
        Write-Host "  Location:     $LogFile"
        Write-Host "  Size:         $(Format-Bytes ($LogInfo.Length))"
        Write-Host "  Last Updated: $($LogInfo.LastWriteTime)"
        Write-Host ""
        
        # Show recent log entries
        Write-ColorOutput "Recent Log Entries (last 5 lines):" "Cyan"
        Get-Content $LogFile -Tail 5 | ForEach-Object {
            Write-Host "  $_"
        }
        Write-Host ""
    }
    
    # Network status
    $Port1100 = Get-NetTCPConnection -LocalPort 1100 -State Listen -ErrorAction SilentlyContinue
    Write-ColorOutput "Network Status:" "Cyan"
    if ($Port1100) {
        Write-Host "  Port 1100:    LISTENING" -ForegroundColor Green
    } else {
        Write-Host "  Port 1100:    NOT LISTENING" -ForegroundColor Yellow
    }
    Write-Host ""
    
    # Management commands
    Write-ColorOutput "Management Commands:" "Cyan"
    Write-Host "  Stop:         .\stop_oscar.ps1"
    Write-Host "  Restart:      .\stop_oscar.ps1; .\start_oscar.ps1"
    Write-Host "  View Logs:    Get-Content OscarLog.txt -Wait -Tail 20"
    Write-Host ""
    
} else {
    Write-ColorOutput "[STATUS] Oscar is not running" "Yellow"
    Write-Host ""
    Write-Host "Start Oscar with:"
    Write-Host "  .\start_oscar.ps1"
    Write-Host ""
}
