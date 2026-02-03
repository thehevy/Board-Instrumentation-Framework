@echo off
REM =============================================================================
REM Start Minion with automatic cleanup of existing instances
REM =============================================================================
REM Usage: start_minion.bat <config.xml> [additional args]
REM Example: start_minion.bat MinionConfig.xml -v
REM
REM This script:
REM 1. Checks if Minion is already running with the same config
REM 2. Stops the existing instance if found
REM 3. Launches new instance with specified config
REM =============================================================================

setlocal enabledelayedexpansion

REM Check if config file provided
if "%~1"=="" (
    echo ERROR: Configuration file required
    echo Usage: start_minion.bat ^<config.xml^> [additional args]
    exit /b 1
)

set CONFIG_FILE=%~1
set ADDITIONAL_ARGS=%~2 %~3 %~4 %~5 %~6 %~7 %~8 %~9

REM Get absolute path to config file
for %%F in ("%CONFIG_FILE%") do set CONFIG_PATH=%%~fF

if not exist "%CONFIG_PATH%" (
    echo ERROR: Configuration file not found: %CONFIG_PATH%
    exit /b 1
)

REM Check for Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found in PATH
    exit /b 1
)

REM Check for Minion.py
if not exist "Minion.py" (
    echo ERROR: Minion.py not found in current directory
    echo Run this script from the Minion directory
    exit /b 1
)

echo Checking for existing Minion instance with config: %CONFIG_PATH%

REM Kill existing instance with same config using PowerShell
powershell -Command "$procs = Get-WmiObject Win32_Process -Filter \"name='python.exe'\" | Where-Object { $_.CommandLine -like '*Minion.py*' -and $_.CommandLine -like '*%CONFIG_PATH:\=\\%*' }; if ($procs) { $procs | ForEach-Object { Write-Host \"Stopping existing Minion instance (PID: $($_.ProcessId))\"; Stop-Process -Id $_.ProcessId -Force }; Start-Sleep -Seconds 1 } else { Write-Host \"No existing instance found\" }"

echo.
echo Starting Minion with config: %CONFIG_PATH%
echo Additional args: %ADDITIONAL_ARGS%
echo.

REM Launch Minion
python Minion.py -i "%CONFIG_PATH%" %ADDITIONAL_ARGS%

endlocal
