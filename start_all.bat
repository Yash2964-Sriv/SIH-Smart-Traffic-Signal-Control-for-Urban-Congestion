@echo off
title Smart Traffic Simulator
color 0A

echo ================================================
echo   SMART TRAFFIC SIMULATOR - COMPLETE SYSTEM
echo ================================================
echo Starting the complete dashboard system...
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python and try again
    pause
    exit /b 1
)

REM Check if Node.js is available
node --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Node.js is not installed or not in PATH
    echo Please install Node.js and try again
    pause
    exit /b 1
)

REM Start the Python launcher
echo Starting Smart Traffic Simulator...
python start_all.py

pause