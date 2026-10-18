@echo off
cd /d "%~dp0"
rem Use bundled IANA timezone data on Windows without changing calculation rules.
set "PYTHONTZPATH=%~dp0vendor\zoneinfo"
where py >nul 2>nul
if %errorlevel%==0 (
  py run_tests.py
) else (
  python run_tests.py
)
pause
