@echo off
echo ================================================================================
echo 🚀 SMART TRAFFIC SIMULATOR - DASHBOARD LAUNCHER
echo ================================================================================
echo Starting complete dashboard with frontend and backend...
echo ================================================================================

echo.
echo 🔍 Checking Python installation...
python --version
if %errorlevel% neq 0 (
    echo ❌ Python not found! Please install Python first.
    pause
    exit /b 1
)

echo.
echo 🔍 Checking Node.js installation...
node --version
if %errorlevel% neq 0 (
    echo ❌ Node.js not found! Please install Node.js first.
    pause
    exit /b 1
)

echo.
echo 🚀 Starting complete dashboard...
python start_complete_dashboard.py

echo.
echo 🎉 Dashboard launcher completed!
pause