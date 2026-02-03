@echo off
REM BIFF Oscar - Stop Script Wrapper
powershell -ExecutionPolicy Bypass -File "%~dp0stop_oscar.ps1" %*
