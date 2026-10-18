@echo off
cd /d "%~dp0"
rem Use bundled IANA timezone data on Windows without changing calculation rules.
set "PYTHONTZPATH=%~dp0vendor\zoneinfo"
where py >nul 2>nul
if %errorlevel%==0 (
  py operator_ui.py
) else (
  python operator_ui.py
)
if errorlevel 1 (
  echo.
  echo Could not launch. Install Python 3.10+ with Tkinter from python.org.
  pause
)
