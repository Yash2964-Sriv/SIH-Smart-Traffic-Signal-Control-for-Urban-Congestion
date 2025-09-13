# Smart Traffic Simulator - Complete Workflow

## 🚀 Overview

This is a complete end-to-end workflow for smart traffic light control that processes real-world traffic data, runs both baseline and AI-controlled simulations, and provides comprehensive comparison analysis with Omniverse visualization.

## 🔄 Workflow Architecture

```
Real World Data → Preprocess → SUMO Baseline → SUMO AI-Controlled → Export to Omniverse → Side-by-Side Comparison
```

### Component Flow:
1. **Data Collection**: CCTV cameras, OSM data, Maps APIs
2. **Preprocessing**: YOLOv8/Detectron2 + OpenCV + SUMO tools
3. **SUMO Baseline**: Fixed traffic light timing simulation
4. **SUMO AI-Controlled**: AI-driven traffic light control
5. **Omniverse Export**: USD scene creation for visualization
6. **Comparison**: Side-by-side analysis with metrics and plots

## 📁 Project Structure

```
Smart_Traffic_Simulator/
├── data_pipeline/           # Real-world data collection
│   ├── camera_collector.py  # CCTV feed processing
│   ├── osm_collector.py     # OpenStreetMap data
│   └── maps_api_collector.py # Maps API integration
├── preprocessing/           # Data preprocessing
│   ├── vehicle_detector.py  # YOLOv8 vehicle detection
│   └── sumo_converter.py    # SUMO network generation
├── simulation/              # SUMO simulations
│   ├── sumo_baseline.py     # Fixed timing simulation
│   └── sumo_ai_controller.py # AI-controlled simulation
├── omniverse/              # Omniverse visualization
│   └── usd_scene_builder.py # USD scene creation
├── comparison/             # Analysis and comparison
│   └── metrics_analyzer.py  # Metrics analysis and plots
├── workflow/               # Workflow integration
│   └── smart_traffic_workflow.py # Main workflow orchestrator
├── config/                 # Configuration files
│   └── workflow_config.json # Workflow configuration
├── main_workflow.py        # Main entry point
└── requirements.txt        # Python dependencies
```

## 🛠️ Installation & Setup

### Prerequisites
- Python 3.8+
- NVIDIA GPU (recommended for AI processing)
- SUMO (Simulation of Urban Mobility)
- Docker (optional, for containerized deployment)

### 1. Install Python Dependencies
```bash
pip install -r requirements.txt
```

### 2. Install SUMO
**Windows:**
```bash
# Download from https://sumo.dlr.de/docs/Downloads.php
# Or use conda:
conda install -c conda-forge sumo
```

**Linux:**
```bash
sudo apt-get install sumo sumo-tools
```

### 3. Install YOLOv8
```bash
pip install ultralytics
```

### 4. Configure the System
Edit `config/workflow_config.json`:
```json
{
  "intersection": {
    "lat": 28.6139,  # Your intersection latitude
    "lon": 77.2090,  # Your intersection longitude
    "radius": 100    # Search radius in meters
  },
  "camera": {
    "enabled": true,
    "url": "rtsp://your_camera_ip:port/stream"
  },
  "maps_api": {
    "enabled": true,
    "api_key": "your_google_maps_api_key"
  }
}
```

## 🚀 Usage

### Quick Start
```bash
python main_workflow.py
```

### Interactive Mode
```bash
python main_workflow.py --interactive
```

### Custom Configuration
```bash
# Edit config/workflow_config.json
python main_workflow.py
```

## 📊 Workflow Steps

### Step 1: Data Collection
- **Camera Data**: Real-time vehicle detection from CCTV feeds
- **OSM Data**: Road network and intersection geometry
- **Maps API**: Traffic patterns and historical data

### Step 2: Preprocessing
- **Vehicle Detection**: YOLOv8 for vehicle detection and tracking
- **Network Generation**: Convert OSM data to SUMO network format
- **Demand Generation**: Create vehicle demand from real data

### Step 3: SUMO Baseline Simulation
- **Fixed Timing**: Traditional traffic light control
- **Metrics Collection**: Waiting time, queue length, throughput
- **Output Generation**: Simulation results and statistics

### Step 4: AI-Controlled Simulation
- **Neural Network**: PyTorch-based traffic light controller
- **Real-time Control**: Dynamic signal timing based on traffic conditions
- **Performance Tracking**: AI decision metrics and rewards

### Step 5: Omniverse Visualization
- **USD Scene Creation**: Photorealistic 3D intersection model
- **Vehicle Animation**: Real-time vehicle movement visualization
- **Traffic Light States**: Dynamic signal visualization

### Step 6: Comparison Analysis
- **Metrics Comparison**: Side-by-side performance analysis
- **Statistical Analysis**: Significance testing and improvement metrics
- **Visualization**: Charts, graphs, and radar plots

## 📈 Output Files

### Simulation Results
- `workflow_output/baseline_simulation/` - Baseline simulation results
- `workflow_output/ai_simulation/` - AI-controlled simulation results
- `workflow_output/sumo_network/` - SUMO network files

### Visualization
- `workflow_output/omniverse/` - USD scene files for Omniverse
- `workflow_output/omniverse/complete_scene.usd` - Complete 3D scene

### Analysis
- `workflow_output/comparison/` - Analysis results and plots
- `workflow_output/comparison/analysis_results.json` - Detailed metrics
- `workflow_output/final_report.html` - Comprehensive HTML report

## 🔧 Configuration Options

### Camera Settings
```json
"camera": {
  "enabled": true,
  "url": "rtsp://localhost:8554/stream",
  "model_path": "yolov8n.pt",
  "fps": 30,
  "resolution": [1920, 1080]
}
```

### AI Model Settings
```json
"ai": {
  "model_path": "yolov8n.pt",
  "device": "auto",
  "confidence_threshold": 0.5,
  "nms_threshold": 0.4
}
```

### Simulation Settings
```json
"simulation": {
  "duration": 3600,
  "step_length": 1,
  "warmup_time": 300,
  "vehicle_count": 100
}
```

## 📊 Metrics and Analysis

### Key Performance Indicators
- **Average Waiting Time**: Time vehicles spend waiting at signals
- **Queue Length**: Number of vehicles waiting in queues
- **Throughput**: Vehicles processed per hour
- **Efficiency Score**: Overall traffic flow efficiency
- **Fuel Consumption**: Estimated fuel usage
- **Emissions**: CO2 and other pollutant emissions

### Comparison Metrics
- **Improvement Percentage**: AI vs Baseline performance
- **Statistical Significance**: Confidence in improvements
- **Efficiency Trends**: Performance over time
- **Congestion Levels**: Traffic density analysis

## 🎯 Use Cases

### 1. Traffic Light Optimization
- Compare traditional fixed timing with AI-controlled systems
- Analyze performance improvements in real-world scenarios
- Generate reports for traffic management authorities

### 2. Research and Development
- Test new AI algorithms for traffic control
- Validate simulation models against real data
- Conduct performance benchmarking

### 3. Urban Planning
- Evaluate intersection designs
- Assess traffic flow improvements
- Plan infrastructure upgrades

### 4. Education and Training
- Demonstrate traffic control concepts
- Train traffic management personnel
- Showcase AI applications in transportation

## 🔍 Troubleshooting

### Common Issues

1. **SUMO Not Found**
   ```bash
   # Add SUMO to PATH or specify tools_path in config
   export SUMO_HOME=/path/to/sumo
   export PATH=$PATH:$SUMO_HOME/bin
   ```

2. **Camera Connection Failed**
   ```bash
   # Check camera URL and network connectivity
   # Ensure camera supports RTSP streaming
   ```

3. **GPU Not Detected**
   ```bash
   # Install CUDA toolkit and PyTorch with CUDA support
   pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118
   ```

4. **Memory Issues**
   ```bash
   # Reduce simulation duration or vehicle count
   # Use smaller AI models (yolov8n instead of yolov8x)
   ```

### Debug Mode
```bash
# Enable debug logging
export LOG_LEVEL=DEBUG
python main_workflow.py
```

## 📚 API Reference

### CameraCollector
```python
collector = CameraCollector(camera_url, model_path)
await collector.start_collection(websocket_url)
```

### VehicleDetector
```python
detector = VehicleDetector(model_path)
detections = detector.detect_vehicles(frame)
```

### SUMOBaselineSimulation
```python
simulation = SUMOBaselineSimulation()
results = simulation.run_baseline_simulation(output_dir, duration)
```

### SUMOAIController
```python
controller = SUMOAIController()
controller.start_simulation(config_file)
```

### USDSceneBuilder
```python
builder = USDSceneBuilder(output_dir)
usd_file = builder.create_intersection_scene(network_file)
```

### MetricsAnalyzer
```python
analyzer = MetricsAnalyzer(output_dir)
results = analyzer.analyze_simulation_metrics(baseline_data, ai_data)
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- Create an issue on GitHub
- Check the troubleshooting section
- Review the logs in `smart_traffic_workflow.log`

## 🔮 Future Enhancements

- [ ] Real-time dashboard
- [ ] Multi-intersection support
- [ ] Advanced AI models (RL, Deep Learning)
- [ ] Mobile app integration
- [ ] Cloud deployment support
- [ ] API endpoints for external integration
