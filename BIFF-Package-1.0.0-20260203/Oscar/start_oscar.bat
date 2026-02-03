@echo off
REM BIFF Oscar - Background Startup Wrapper
powershell -ExecutionPolicy Bypass -File "%~dp0start_oscar.ps1" %*
