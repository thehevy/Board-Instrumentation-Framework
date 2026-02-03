@echo off
REM =============================================================================
REM Quickstart - Start Minion with Generated Configuration
REM =============================================================================

cd /d "%~dp0..\Minion"
call start_minion.bat "%~dp0biff-quickstart-test\MinionConfig.xml"
