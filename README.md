# Smart Traffic Simulator

A real-time AI-powered traffic control system with digital twin visualization using NVIDIA Omniverse, SUMO simulation, and live camera integration.

## 🎯 Project Overview

This system creates a digital twin of real traffic intersections, uses AI to optimize traffic light timing, and provides real-time comparison between AI-controlled and traditional timer-based traffic management.

## 🧩 Tech Stack

### Digital Twin & Visualization
- **NVIDIA Omniverse Platform** - 3D visualization and digital twin
- **Isaac Sim** - ROS 2 bridge and sensor integration
- **OpenStreetMap** - Road geometry and intersection data

### Traffic Simulation & AI
- **SUMO (Simulation of Urban MObility)** - Traffic micro-simulation
- **PyTorch + Stable-Baselines3** - AI for adaptive traffic control
- **YOLOv8** - Vehicle detection from camera feeds

### Backend & Middleware
- **ROS 2 (Humble)** - Real-time communication middleware
- **FastAPI** - AI decisions and metrics API
- **Redis** - Real-time message queue
- **Node.js + Express** - Web backend

### Frontend
- **React + Tailwind CSS** - Web interface
- **WebRTC/HLS** - Live video streaming
- **Recharts** - Real-time metrics visualization

### Infrastructure
- **Docker** - Containerized deployment
- **MongoDB Atlas** - Data storage
- **NGINX** - Reverse proxy

## 🚀 Quick Start

### Prerequisites
- Windows 10/11
- NVIDIA GeForce RTX GPU
- Docker Desktop
- Python 3.9+
- Node.js 18+

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/01HARSHIT1/smarttraffic.git
cd smarttraffic
```

2. **Install Python dependencies**
```bash
pip install -r requirements.txt
```

3. **Install Node.js dependencies**
```bash
cd frontend
npm install
cd ../backend
npm install
```

4. **Set up Docker containers**
```bash
docker-compose up -d
```

5. **Start the development servers**
```bash
# Terminal 1: Backend API
python backend_api.py

# Terminal 2: Frontend
cd frontend && npm start

# Terminal 3: SUMO Simulation
python start_ai_traffic_control.py
```

## 📁 Project Structure

```
smarttraffic/
├── backend/                 # FastAPI backend
├── frontend/               # React frontend
├── simulation/             # SUMO simulation and AI
├── omniverse/             # Omniverse digital twin
├── ai_controller/         # AI traffic control logic
├── camera_integration/    # Camera feed processing
├── docker/               # Docker configurations
├── docs/                 # Documentation
└── data/                 # Traffic data and models
```

## 🔧 Configuration

1. **Camera Configuration** - Update `config/camera_config.yaml`
2. **SUMO Configuration** - Modify `simulation/sumo_config/`
3. **AI Model Parameters** - Edit `ai_controller/config.py`
4. **Omniverse Settings** - Configure `omniverse/settings.json`

## 📊 Features

- **Real-time Traffic Analysis** - Live camera feed processing
- **AI Traffic Control** - Adaptive signal timing optimization
- **Digital Twin Visualization** - Photorealistic 3D simulation
- **Performance Comparison** - AI vs traditional timer metrics
- **Live Dashboard** - Real-time KPIs and analytics
- **Historical Analysis** - Traffic pattern analysis and reporting

## 🤖 AI Features

- **Adaptive Signal Timing** - Real-time optimization based on traffic density
- **Queue Length Prediction** - ML-based traffic flow forecasting
- **Multi-intersection Coordination** - Coordinated signal timing across junctions
- **Performance Metrics** - Wait time, throughput, and emission optimization

## 📈 Metrics & KPIs

- **Average Wait Time** - Per vehicle and per phase
- **Queue Length** - Real-time queue monitoring
- **Throughput** - Vehicles per hour per lane
- **Delay Reduction** - AI vs traditional timer comparison
- **Emission Proxy** - Environmental impact assessment

## 🔄 Development Workflow

1. **Setup Phase** - Environment and dependencies
2. **Core Simulation** - SUMO integration and basic traffic logic
3. **AI Integration** - Traffic control algorithms
4. **Camera Integration** - Real-time feed processing
5. **Omniverse Setup** - Digital twin visualization
6. **Web Interface** - Dashboard and controls
7. **Testing & Optimization** - Performance tuning
8. **Deployment** - Production setup

## 📝 License

MIT License - see LICENSE file for details

## 🤝 Contributing

Please read CONTRIBUTING.md for details on our code of conduct and the process for submitting pull requests.

## 📞 Support

For support and questions, please open an issue in the repository.
