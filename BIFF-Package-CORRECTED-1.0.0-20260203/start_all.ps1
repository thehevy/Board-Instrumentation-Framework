# =============================================================================
# Start All BIFF Components
# =============================================================================
# Starts Oscar (background) and Marvin (foreground)
# Minion must be started separately as it's typically on remote systems
# =============================================================================

param(
    [string]$MarvinConfig = "Configs\Application.xml",
    [string]$OscarConfig = "Configs\OscarConfig.xml",
    [switch]$Help
)

if ($Help) {
    Write-Host @"
============================================================
  Start All BIFF Components
============================================================

USAGE:
  .\start_all.ps1 [-MarvinConfig <path>] [-OscarConfig <path>]

OPTIONS:
  -MarvinConfig <path>   Marvin configuration file
  -OscarConfig <path>    Oscar configuration file
  -Help                  Show this help message

EXAMPLE:
  .\start_all.ps1
  .\start_all.ps1 -MarvinConfig Configs\MyMarvin.xml

"@
    exit 0
}

Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "  Starting BIFF Components" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# Start Oscar in background
Write-Host "[1/2] Starting Oscar (background)..." -ForegroundColor Yellow
Push-Location Oscar
& .\start_oscar.ps1 -ConfigFile "..\$OscarConfig" -Background
Pop-Location

Start-Sleep -Seconds 3

# Start Marvin in foreground
Write-Host ""
Write-Host "[2/2] Starting Marvin (foreground)..." -ForegroundColor Yellow
Write-Host "      Close Marvin window to stop" -ForegroundColor Cyan
Write-Host ""
Push-Location Marvin
& .\start_marvin.ps1 -ConfigFile "..\$MarvinConfig"
Pop-Location
