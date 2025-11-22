@echo off
REM Gerald Desktop Manager - Windows Launcher
REM Double-click this file to start Gerald on Windows

echo ================================================
echo   Gerald Desktop Manager
echo   Starting...
echo ================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH
    echo Please install Python 3.10 or higher
    pause
    exit /b 1
)

REM Run Gerald
python run_gerald.py

pause
