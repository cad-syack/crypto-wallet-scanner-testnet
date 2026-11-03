@echo off
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
  echo Create the virtual environment and install requirements first.
  echo See README.md for instructions.
  pause
  exit /b 1
)
".venv\Scripts\python.exe" app.py
