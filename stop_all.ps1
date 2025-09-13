# Smart Traffic Simulator - Stop All Services Script

Write-Host "🛑 Stopping Smart Traffic Simulator..." -ForegroundColor Red
Write-Host "====================================" -ForegroundColor Red

# Stop Python processes
Write-Host "🐍 Stopping Python Backend..." -ForegroundColor Yellow
Get-Process | Where-Object { $_.ProcessName -eq "python" } | Stop-Process -Force -ErrorAction SilentlyContinue

# Stop Node.js processes
Write-Host "⚛️ Stopping React Frontend..." -ForegroundColor Yellow
Get-Process | Where-Object { $_.ProcessName -eq "node" } | Stop-Process -Force -ErrorAction SilentlyContinue

# Stop Docker containers if they exist
Write-Host "🐳 Stopping Docker containers..." -ForegroundColor Yellow
docker stop smart-traffic-mongo smart-traffic-redis 2>$null
docker rm smart-traffic-mongo smart-traffic-redis 2>$null

# Kill any remaining processes on our ports
Write-Host "🧹 Cleaning up remaining processes..." -ForegroundColor Yellow
netstat -ano | findstr ":8000" | ForEach-Object {
    $pid = ($_ -split '\s+')[-1]
    if ($pid -match '^\d+$') {
        Stop-Process -Id $pid -Force -ErrorAction SilentlyContinue
    }
}

netstat -ano | findstr ":3000" | ForEach-Object {
    $pid = ($_ -split '\s+')[-1]
    if ($pid -match '^\d+$') {
        Stop-Process -Id $pid -Force -ErrorAction SilentlyContinue
    }
}

Write-Host "✅ All services stopped successfully!" -ForegroundColor Green
Write-Host "Press any key to continue..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
