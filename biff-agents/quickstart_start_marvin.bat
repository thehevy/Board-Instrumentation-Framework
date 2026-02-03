@echo off
REM =============================================================================
REM Quickstart - Start Marvin with Generated Configuration
REM =============================================================================

cd /d "%~dp0..\Marvin"
call start_marvin.bat "%~dp0biff-quickstart-test\ApplicationConfig.xml" -vvvv
