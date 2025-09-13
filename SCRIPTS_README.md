# Smart Traffic Simulator - Startup Scripts

This directory contains scripts to easily start and stop all services for the Smart Traffic Simulator.

## 🚀 Quick Start

### Option 1: Simple Start (Development Mode)
```powershell
# Run the simple batch file
start_all.bat

# Or run the PowerShell script
.\start_all.ps1
```

### Option 2: Start with Database (Production Mode)
```powershell
# Start with MongoDB and Redis (requires Docker)
.\start_with_database.ps1
```

### Option 3: Stop All Services
```powershell
# Stop all running services
.\stop_all.ps1
```

## 📋 Available Scripts

### 1. `start_all.bat` / `start_all.ps1`
- **Purpose**: Start backend and frontend in development mode
- **Database**: No database (uses mock data)
- **Requirements**: Python, Node.js, npm
- **Services**:
  - Backend API: http://127.0.0.1:8000
  - Frontend: http://localhost:3000

### 2. `start_with_database.ps1`
- **Purpose**: Start all services including databases
- **Database**: MongoDB + Redis (via Docker)
- **Requirements**: Python, Node.js, npm, Docker
- **Services**:
  - Backend API: http://127.0.0.1:8000
  - Frontend: http://localhost:3000
  - MongoDB: mongodb://admin:password@localhost:27017
  - Redis: redis://localhost:6379

### 3. `stop_all.ps1`
- **Purpose**: Stop all running services
- **Cleans up**: Python processes, Node.js processes, Docker containers

## 🔧 Manual Commands

If you prefer to start services manually:

### Backend Only
```powershell
cd backend
python main.py
```

### Frontend Only
```powershell
cd frontend
npm start
```

### Database Only (with Docker)
```powershell
# MongoDB
docker run -d --name smart-traffic-mongo -p 27017:27017 -e MONGO_INITDB_ROOT_USERNAME=admin -e MONGO_INITDB_ROOT_PASSWORD=password mongo:latest

# Redis
docker run -d --name smart-traffic-redis -p 6379:6379 redis:latest
```

## 🐛 Troubleshooting

### Frontend Won't Start
1. Check if port 3000 is available: `netstat -an | findstr :3000`
2. Try clearing npm cache: `npm cache clean --force`
3. Delete node_modules and reinstall: `rm -rf node_modules && npm install`

### Backend Won't Start
1. Check if port 8000 is available: `netstat -an | findstr :8000`
2. Verify Python dependencies: `pip install -r requirements.txt`
3. Check for Python processes: `Get-Process python`

### Database Issues
1. Check if Docker is running: `docker --version`
2. Check container status: `docker ps -a`
3. View container logs: `docker logs smart-traffic-mongo`

## 📊 Service Status

After starting, you can verify services are running:

- **Backend Health**: http://127.0.0.1:8000/health
- **API Documentation**: http://127.0.0.1:8000/docs
- **Frontend**: http://localhost:3000

## 🔄 Development Workflow

1. **Start Development**: `.\start_all.ps1`
2. **Make Changes**: Edit code in your IDE
3. **Test Changes**: Refresh browser (frontend) or check API docs (backend)
4. **Stop Services**: `.\stop_all.ps1` or Ctrl+C

## 📝 Notes

- The scripts automatically detect if Docker is available
- Development mode uses mock data (no database required)
- Production mode requires Docker for databases
- All scripts include error handling and cleanup
- Services are monitored and will show warnings if they stop unexpectedly
