@echo off
REM =============================================================================
REM BIFF Package Builder - Wrapper Script
REM =============================================================================
REM Calls the Python-based package builder
REM =============================================================================

python biff-agents\build_package.py %*
