@echo off
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0Build-Weather.ps1" -Install
pause
