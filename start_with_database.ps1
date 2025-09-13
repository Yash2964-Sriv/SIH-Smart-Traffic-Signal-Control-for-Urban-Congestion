# Smart Traffic Simulator - Start All Services with Database
# This script starts the backend, frontend, and database services (MongoDB + Redis)

Write-Host "🚀 Starting Smart Traffic Simulator with Database..." -ForegroundColor Green
Write-Host "===============================================" -ForegroundColor Green

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

# Check if Docker is available
$dockerAvailable = $false
try {
    docker --version | Out-Null
    $dockerAvailable = $true
    Write-Host "🐳 Docker detected - will use Docker for databases" -ForegroundColor Green
} catch {
    Write-Host "⚠️ Docker not available - will use development mode (no databases)" -ForegroundColor Yellow
}

# Kill any existing processes on our ports
Write-Host "🧹 Cleaning up existing processes..." -ForegroundColor Yellow
Get-Process | Where-Object { $_.ProcessName -eq "python" -or $_.ProcessName -eq "node" } | Stop-Process -Force -ErrorAction SilentlyContinue
Start-Sleep -Seconds 2

# Start databases if Docker is available
if ($dockerAvailable) {
    Write-Host "🗄️ Starting databases with Docker..." -ForegroundColor Cyan
    
    # Start MongoDB
    Write-Host "📊 Starting MongoDB..." -ForegroundColor Cyan
    docker run -d --name smart-traffic-mongo -p 27017:27017 -e MONGO_INITDB_ROOT_USERNAME=admin -e MONGO_INITDB_ROOT_PASSWORD=password mongo:latest
    
    # Start Redis
    Write-Host "🔴 Starting Redis..." -ForegroundColor Cyan
    docker run -d --name smart-traffic-redis -p 6379:6379 redis:latest
    
    # Wait for databases to start
    if (Wait-ForService -Port 27017 -ServiceName "MongoDB" -TimeoutSeconds 15) {
        Write-Host "✅ MongoDB is ready!" -ForegroundColor Green
    } else {
        Write-Host "❌ MongoDB failed to start" -ForegroundColor Red
    }
    
    if (Wait-ForService -Port 6379 -ServiceName "Redis" -TimeoutSeconds 15) {
        Write-Host "✅ Redis is ready!" -ForegroundColor Green
    } else {
        Write-Host "❌ Redis failed to start" -ForegroundColor Red
    }
    
    # Update backend to use databases
    Write-Host "🔧 Updating backend to use databases..." -ForegroundColor Yellow
    $databaseFile = "backend\database.py"
    $content = Get-Content $databaseFile
    $content = $content -replace "DEV_MODE = True", "DEV_MODE = False"
    $content | Set-Content $databaseFile
} else {
    Write-Host "🔧 Using development mode (no databases)" -ForegroundColor Yellow
}

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
Write-Host "===============================================" -ForegroundColor Green
Write-Host "📊 Backend API: http://127.0.0.1:8000" -ForegroundColor White
Write-Host "📚 API Docs: http://127.0.0.1:8000/docs" -ForegroundColor White
Write-Host "🌐 Frontend: http://localhost:3000" -ForegroundColor White
if ($dockerAvailable) {
    Write-Host "🗄️ MongoDB: mongodb://admin:password@localhost:27017" -ForegroundColor White
    Write-Host "🔴 Redis: redis://localhost:6379" -ForegroundColor White
}
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
    
    # Stop Docker containers if they exist
    if ($dockerAvailable) {
        Write-Host "🐳 Stopping Docker containers..." -ForegroundColor Yellow
        docker stop smart-traffic-mongo smart-traffic-redis 2>$null
        docker rm smart-traffic-mongo smart-traffic-redis 2>$null
    }
    
    # Kill any remaining processes
    Get-Process | Where-Object { $_.ProcessName -eq "python" -or $_.ProcessName -eq "node" } | Stop-Process -Force -ErrorAction SilentlyContinue
    
    Write-Host "✅ All services stopped" -ForegroundColor Green
    exit 0
}
