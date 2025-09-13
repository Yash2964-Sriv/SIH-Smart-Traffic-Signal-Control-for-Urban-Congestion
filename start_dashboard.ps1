# Smart Traffic Simulator Dashboard Launcher
# PowerShell script for Windows

Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host "🚀 SMART TRAFFIC SIMULATOR - DASHBOARD LAUNCHER" -ForegroundColor Yellow
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host "Starting Backend API and Frontend Dashboard..." -ForegroundColor Green
Write-Host "================================================================================" -ForegroundColor Cyan

# Check if Python is installed
Write-Host "`n🔍 Checking Python installation..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✅ Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Python not found! Please install Python first." -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Check if Node.js is installed
Write-Host "`n🔍 Checking Node.js installation..." -ForegroundColor Yellow
try {
    $nodeVersion = node --version 2>&1
    Write-Host "✅ Node.js found: $nodeVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Node.js not found! Please install Node.js first." -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Start Backend API
Write-Host "`n🔧 Starting Backend API Server..." -ForegroundColor Yellow
Start-Process -FilePath "python" -ArgumentList "backend_api.py" -WindowStyle Minimized
Start-Sleep -Seconds 3
Write-Host "✅ Backend API started on http://localhost:5000" -ForegroundColor Green

# Start Frontend
Write-Host "`n🎨 Starting Frontend Development Server..." -ForegroundColor Yellow
Set-Location "frontend"
Start-Process -FilePath "npm" -ArgumentList "start" -WindowStyle Normal
Set-Location ".."
Write-Host "✅ Frontend started on http://localhost:3000" -ForegroundColor Green

# Wait a moment for services to start
Write-Host "`n⏳ Waiting for services to start..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

# Open dashboard
Write-Host "`n🌐 Opening Dashboard in Browser..." -ForegroundColor Yellow
Start-Process "http://localhost:3000"

# Show instructions
Write-Host "`n================================================================================" -ForegroundColor Cyan
Write-Host "📋 DASHBOARD USAGE INSTRUCTIONS" -ForegroundColor Yellow
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host "🌐 Dashboard URL: http://localhost:3000" -ForegroundColor Green
Write-Host "🔧 Backend API: http://localhost:5000" -ForegroundColor Green
Write-Host "`n🎯 How to Use:" -ForegroundColor Yellow
Write-Host "1. 📱 Click 'Live Video Simulation' in the sidebar" -ForegroundColor White
Write-Host "2. 📹 Upload a real traffic video (MP4, AVI, MOV, WEBM, MKV)" -ForegroundColor White
Write-Host "3. 🚦 Click 'Start Live Simulation' to begin AI analysis" -ForegroundColor White
Write-Host "4. 🎮 Watch SUMO GUI open with your replicated traffic" -ForegroundColor White
Write-Host "5. 📊 Monitor live metrics and AI performance" -ForegroundColor White
Write-Host "`n🎬 Features Available:" -ForegroundColor Yellow
Write-Host "   • Real-time video upload and analysis" -ForegroundColor White
Write-Host "   • Live SUMO simulation with AI control" -ForegroundColor White
Write-Host "   • Real-time metrics and comparison" -ForegroundColor White
Write-Host "   • AI efficiency improvements tracking" -ForegroundColor White
Write-Host "   • Live traffic signal optimization" -ForegroundColor White
Write-Host "`n🛑 To stop all services: Close the terminal windows" -ForegroundColor Red
Write-Host "================================================================================" -ForegroundColor Cyan

Write-Host "`n🎉 Dashboard launcher completed!" -ForegroundColor Green
Write-Host "Both frontend and backend should now be running." -ForegroundColor Green
Read-Host "Press Enter to exit"


