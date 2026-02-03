@echo off
REM =============================================================================
REM Quickstart - Start Oscar with Generated Configuration
REM =============================================================================

cd /d "%~dp0..\Oscar"
call start_oscar.bat "%~dp0biff-quickstart-test\OscarConfig.xml"
