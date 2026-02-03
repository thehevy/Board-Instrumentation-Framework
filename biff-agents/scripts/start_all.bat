@echo off
REM ===========================================================================
REM BIFF Quick Start Launcher - Windows
REM Launches Oscar, Minion, and Marvin in sequence
REM ===========================================================================

setlocal enabledelayedexpansion

echo.
echo ============================================================
echo   BIFF Quick Start Launcher
echo ============================================================
echo.

REM Check if config directory exists
if not exist "quickstart_configs" (
    echo [ERROR] Config directory not found: quickstart_configs
    echo.
    echo Please run 'python -m biff_cli quickstart' first to generate configs.
    echo.
    pause
    exit /b 1
)

REM Load configuration paths
set "MINION_CONFIG=quickstart_configs\MinionConfig.xml"
set "OSCAR_CONFIG=quickstart_configs\OscarConfig.xml"
set "MARVIN_CONFIG=quickstart_configs\Application.xml"

REM Check if configs exist
if not exist "%MINION_CONFIG%" (
    echo [ERROR] Minion config not found: %MINION_CONFIG%
    pause
    exit /b 1
)

if not exist "%OSCAR_CONFIG%" (
    echo [ERROR] Oscar config not found: %OSCAR_CONFIG%
    pause
    exit /b 1
)

if not exist "%MARVIN_CONFIG%" (
    echo [ERROR] Marvin config not found: %MARVIN_CONFIG%
    pause
    exit /b 1
)

REM Detect BIFF installation
set "BIFF_ROOT="
if exist "..\..\Oscar\Oscar.py" (
    set "BIFF_ROOT=..\..\"
    echo [INFO] Using existing BIFF installation at: %BIFF_ROOT%
) else if exist "..\Oscar\Oscar.py" (
    set "BIFF_ROOT=.."
    echo [INFO] Using existing BIFF installation at: %BIFF_ROOT%
) else (
    echo [WARNING] BIFF installation not detected
    echo [INFO] Assuming standalone mode
    echo.
    echo [ERROR] Standalone mode requires Oscar/Minion/Marvin directories
    echo Please run 'biff quickstart' with existing BIFF installation
    pause
    exit /b 1
)

echo.
echo [INFO] Starting BIFF components...
echo.

REM Start Oscar (data broker)
echo [1/3] Starting Oscar (data broker)...
cd /d "%BIFF_ROOT%\Oscar"
set "OSCAR_ABS_CONFIG=%CD%\..\biff-agents\%OSCAR_CONFIG%"
start "BIFF Oscar" cmd /k "python Oscar.py -c "%OSCAR_ABS_CONFIG%" || pause"
cd /d "%~dp0\.."
echo       [OK] Oscar started in new window
timeout /t 3 /nobreak >nul

REM Start Minion (data collector)
echo [2/3] Starting Minion (data collector)...
cd /d "%BIFF_ROOT%\Minion"
set "MINION_ABS_CONFIG=%CD%\..\biff-agents\%MINION_CONFIG%"
start "BIFF Minion" cmd /k "python Minion.py -c "%MINION_ABS_CONFIG%" || pause"
cd /d "%~dp0\.."
echo       [OK] Minion started in new window
timeout /t 2 /nobreak >nul

REM Build Marvin if needed
echo [3/3] Starting Marvin (GUI)...
cd /d "%BIFF_ROOT%\Marvin"

if not exist "build\libs\BIFF.Marvin.jar" (
    echo       [INFO] Building Marvin (first-time setup)...
    call gradlew.bat build -q
    if errorlevel 1 (
        echo       [ERROR] Marvin build failed
        echo.
        echo Check that Java and Gradle are installed:
        echo   java -version
        echo   gradle --version
        echo.
        pause
        exit /b 1
    )
    echo       [OK] Marvin built successfully
)

REM Start Marvin
set "MARVIN_ABS_CONFIG=%CD%\..\biff-agents\%MARVIN_CONFIG%"
echo       [INFO] Launching Marvin GUI...
start "BIFF Marvin" cmd /k "java -jar build\libs\BIFF.Marvin.jar -a "%MARVIN_ABS_CONFIG%" || pause"
cd /d "%~dp0\.."

timeout /t 2 /nobreak >nul

echo.
echo ============================================================
echo   All BIFF components started!
echo ============================================================
echo.
echo You should see 3 windows:
echo   - Oscar (data broker) - routing data
echo   - Minion (collector) - sending metrics
echo   - Marvin (GUI) - displaying dashboard
echo.
echo To stop: Close each window or press Ctrl+C
echo.
echo Dashboard should appear in a few seconds...
echo.
pause
