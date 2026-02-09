@echo off
REM =============================================================================
REM BIFF Marvin Configuration Validator - Windows Launcher
REM Pre-flight validation for Marvin XML configurations
REM =============================================================================

REM Check if Python is available
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Python not found. Please install Python 3.7 or later.
    exit /b 1
)

REM Check if config file argument provided
if "%~1"=="" (
    echo Usage: validate_config.bat ^<config.xml^> [options]
    echo.
    echo Options:
    echo   -v, --verbose         Show detailed information
    echo   -a, --alias-cascade   Analyze alias cascading
    echo.
    echo Examples:
    echo   validate_config.bat Application.xml
    echo   validate_config.bat -v App.Config.xml
    echo   validate_config.bat -a --verbose ExperienceKit\App.Config.xml
    exit /b 1
)

python "%~dp0validate_config.py" %*
exit /b %ERRORLEVEL%
