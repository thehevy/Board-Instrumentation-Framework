@echo off
REM Test BIFF path detection only (no launch)

echo Testing BIFF installation detection...
echo.

set "BIFF_ROOT="
if exist "..\..\Oscar\Oscar.py" (
    set "BIFF_ROOT=..\..\"
    echo [OK] Found BIFF at: %BIFF_ROOT%
    echo      Oscar: %BIFF_ROOT%\Oscar\Oscar.py
    echo      Minion: %BIFF_ROOT%\Minion\Minion.py
    echo      Marvin: %BIFF_ROOT%\Marvin\gradlew.bat
) else if exist "..\Oscar\Oscar.py" (
    set "BIFF_ROOT=.."
    echo [OK] Found BIFF at: %BIFF_ROOT%
) else (
    echo [ERROR] BIFF installation not found
    exit /b 1
)

echo.
echo Testing config files...
if exist "..\quickstart_configs\MinionConfig.xml" (
    echo [OK] MinionConfig.xml exists
) else (
    echo [ERROR] MinionConfig.xml not found
)

if exist "..\quickstart_configs\OscarConfig.xml" (
    echo [OK] OscarConfig.xml exists
) else (
    echo [ERROR] OscarConfig.xml not found
)

if exist "..\quickstart_configs\Application.xml" (
    echo [OK] Application.xml exists
) else (
    echo [ERROR] Application.xml not found
)

echo.
echo Path detection test complete!
pause
