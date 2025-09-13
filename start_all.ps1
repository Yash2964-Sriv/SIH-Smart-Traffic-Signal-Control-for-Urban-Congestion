# Smart Traffic Simulator - Start All Services Script
# This script starts the backend, frontend, and database services

Write-Host "🚀 Starting Smart Traffic Simulator..." -ForegroundColor Green
Write-Host "=================================" -ForegroundColor Green

# Function to check if a port is in use
function Test-Port {
    param([int]$Port)
    try {
        $connection = New-Object System.Net.Sockets.TcpClient
        $connection.Connect("127.0.0.1", $Port)
        $connection.Close()
        return $true
    }
    catch {
        return $false
    }
}

# Function to wait for a service to be ready
function Wait-ForService {
    param([int]$Port, [string]$ServiceName, [int]$TimeoutSeconds = 30)
    
    Write-Host "⏳ Waiting for $ServiceName to start on port $Port..." -ForegroundColor Yellow
    
    $timeout = (Get-Date).AddSeconds($TimeoutSeconds)
    while ((Get-Date) -lt $timeout) {
        if (Test-Port -Port $Port) {
            Write-Host "✅ $ServiceName is ready!" -ForegroundColor Green
            return $true
        }
        Start-Sleep -Seconds 2
    }
    
    Write-Host "❌ $ServiceName failed to start within $TimeoutSeconds seconds" -ForegroundColor Red
    return $false
}

# Check if we're in the right directory
if (-not (Test-Path "backend\main.py")) {
    Write-Host "❌ Error: Please run this script from the Smart_Traffic_Simulator root directory" -ForegroundColor Red
    exit 1
}

# Kill any existing processes on our ports
Write-Host "🧹 Cleaning up existing processes..." -ForegroundColor Yellow
Get-Process | Where-Object { $_.ProcessName -eq "python" -or $_.ProcessName -eq "node" } | Stop-Process -Force -ErrorAction SilentlyContinue
Start-Sleep -Seconds 2

# Start Backend (FastAPI)
Write-Host "🐍 Starting Python Backend..." -ForegroundColor Cyan
$backendJob = Start-Job -ScriptBlock {
    Set-Location $using:PWD\backend
    python main.py
}

# Wait for backend to start
if (Wait-ForService -Port 8000 -ServiceName "Backend API" -TimeoutSeconds 15) {
    Write-Host "✅ Backend API is running on http://127.0.0.1:8000" -ForegroundColor Green
} else {
    Write-Host "❌ Failed to start Backend API" -ForegroundColor Red
    Stop-Job $backendJob
    Remove-Job $backendJob
    exit 1
}

# Start Frontend (React)
Write-Host "⚛️ Starting React Frontend..." -ForegroundColor Cyan
$frontendJob = Start-Job -ScriptBlock {
    Set-Location $using:PWD\frontend
    npm start
}

# Wait for frontend to start
if (Wait-ForService -Port 3000 -ServiceName "React Frontend" -TimeoutSeconds 30) {
    Write-Host "✅ React Frontend is running on http://localhost:3000" -ForegroundColor Green
} else {
    Write-Host "❌ Failed to start React Frontend" -ForegroundColor Red
    Write-Host "💡 Try running 'npm start' manually in the frontend directory" -ForegroundColor Yellow
}

# Display status
Write-Host ""
Write-Host "🎉 Smart Traffic Simulator is running!" -ForegroundColor Green
Write-Host "=================================" -ForegroundColor Green
Write-Host "📊 Backend API: http://127.0.0.1:8000" -ForegroundColor White
Write-Host "📚 API Docs: http://127.0.0.1:8000/docs" -ForegroundColor White
Write-Host "🌐 Frontend: http://localhost:3000" -ForegroundColor White
Write-Host ""
Write-Host "Press Ctrl+C to stop all services" -ForegroundColor Yellow

# Keep script running and monitor services
try {
    while ($true) {
        # Check if backend is still running
        if (-not (Test-Port -Port 8000)) {
            Write-Host "⚠️ Backend API stopped unexpectedly" -ForegroundColor Red
        }
        
        # Check if frontend is still running
        if (-not (Test-Port -Port 3000)) {
            Write-Host "⚠️ React Frontend stopped unexpectedly" -ForegroundColor Red
        }
        
        Start-Sleep -Seconds 10
    }
}
catch {
    Write-Host ""
    Write-Host "🛑 Stopping all services..." -ForegroundColor Yellow
    
    # Stop jobs
    Stop-Job $backendJob -ErrorAction SilentlyContinue
    Stop-Job $frontendJob -ErrorAction SilentlyContinue
    
    # Remove jobs
    Remove-Job $backendJob -ErrorAction SilentlyContinue
    Remove-Job $frontendJob -ErrorAction SilentlyContinue
    
    # Kill any remaining processes
    Get-Process | Where-Object { $_.ProcessName -eq "python" -or $_.ProcessName -eq "node" } | Stop-Process -Force -ErrorAction SilentlyContinue
    
    Write-Host "✅ All services stopped" -ForegroundColor Green
    exit 0
}
