@echo off
cd /d "%~dp0"
if exist ".venv\Scripts\python.exe" (
  ".venv\Scripts\python.exe" integrations\ksp_updates.py update
) else (
  py -3 integrations\ksp_updates.py update
)
pause
