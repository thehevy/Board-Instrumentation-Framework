@echo off
REM =============================================================================
REM Start All BIFF Components
REM =============================================================================

setlocal

set MARVIN_CONFIG=Configs\Application.xml
set OSCAR_CONFIG=Configs\OscarConfig.xml

echo.
echo ============================================================
echo   Starting BIFF Components
echo ============================================================
echo.

REM Start Oscar in background
echo [1/2] Starting Oscar (background)...
cd Oscar
start /B "BIFF Oscar" cmd /c "start_oscar.bat ..\%OSCAR_CONFIG%"
cd ..

timeout /t 3 /nobreak >nul

REM Start Marvin in foreground
echo.
echo [2/2] Starting Marvin (foreground)...
echo       Close Marvin window to stop
echo.
cd Marvin
call start_marvin.bat ..\%MARVIN_CONFIG%
cd ..

endlocal
