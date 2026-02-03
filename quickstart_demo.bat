@echo off
REM =============================================================================
REM Quickstart Demo - Start All BIFF Components
REM =============================================================================
REM This script demonstrates starting all three BIFF components with the
REM quickstart-generated configurations. Each component automatically stops
REM any existing instance with the same configuration before starting.
REM =============================================================================

setlocal

set QUICKSTART_DIR=%~dp0biff-quickstart-test

if not exist "%QUICKSTART_DIR%" (
    echo ERROR: Quickstart configurations not found
    echo Run: python -m biff_agents.quickstart first
    exit /b 1
)

echo ============================================================
echo   Starting BIFF Quickstart Demo
echo ============================================================
echo.
echo This will start:
echo   1. Oscar (data broker) - background
echo   2. Minion (data collector) - background
echo   3. Marvin (GUI) - foreground
echo.
pause

REM Start Oscar in background
echo.
echo [1/3] Starting Oscar...
cd Oscar
start /B "BIFF Oscar" cmd /c "..\biff-agents\quickstart_start_oscar.bat"
cd ..
timeout /t 3 /nobreak >nul

REM Start Minion in background
echo [2/3] Starting Minion...
cd Minion
start /B "BIFF Minion" cmd /c "..\biff-agents\quickstart_start_minion.bat"
cd ..
timeout /t 2 /nobreak >nul

REM Start Marvin in foreground (will block until GUI closes)
echo [3/3] Starting Marvin GUI...
echo.
echo NOTE: Close Marvin window to shut down this demo
echo.
cd biff-agents
call quickstart_start_marvin.bat

endlocal
