@echo off
REM BIFF Oscar - Status Check Wrapper
powershell -ExecutionPolicy Bypass -File "%~dp0status_oscar.ps1" %*
