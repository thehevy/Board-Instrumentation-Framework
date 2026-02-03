@echo off
REM =============================================================================
REM Start Marvin with automatic cleanup of existing instances
REM =============================================================================
REM Usage: start_marvin.bat <config.xml> [additional java args]
REM Example: start_marvin.bat App.Config.xml -vvvv
REM
REM This script:
REM 1. Checks if Marvin is already running with the same config
REM 2. Stops the existing instance if found
REM 3. Launches new instance with specified config
REM =============================================================================

setlocal enabledelayedexpansion

REM Check if config file provided
if "%~1"=="" (
    echo ERROR: Configuration file required
    echo Usage: start_marvin.bat ^<config.xml^> [additional args]
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

REM Check for Java
java -version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Java not found in PATH
    echo Run setup_java.bat or setup_java.ps1 first
    exit /b 1
)

REM Check for JAR file
if not exist "build\libs\BIFF.Marvin.jar" (
    echo ERROR: BIFF.Marvin.jar not found in build\libs\
    echo Run gradlew build first
    exit /b 1
)

echo Checking for existing Marvin instance with config: %CONFIG_PATH%

REM Kill existing instance with same config using PowerShell
powershell -Command "$procs = Get-WmiObject Win32_Process -Filter \"name='java.exe'\" | Where-Object { $_.CommandLine -like '*BIFF.Marvin.jar*' -and $_.CommandLine -like '*%CONFIG_PATH:\=\\%*' }; if ($procs) { $procs | ForEach-Object { Write-Host \"Stopping existing Marvin instance (PID: $($_.ProcessId))\"; Stop-Process -Id $_.ProcessId -Force }; Start-Sleep -Seconds 2 } else { Write-Host \"No existing instance found\" }"

echo.
echo Starting Marvin with config: %CONFIG_PATH%
echo Additional args: %ADDITIONAL_ARGS%
echo.

REM Launch Marvin
cd build\libs
java -Xss1G -Xms1G -jar BIFF.Marvin.jar -i "%CONFIG_PATH%" %ADDITIONAL_ARGS%

endlocal
