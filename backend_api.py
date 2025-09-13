#!/usr/bin/env python3
"""
Simple Backend API for Smart Traffic Simulator
Integrates with existing AI/SUMO system
"""

import os
import sys
import time
import json
import threading
import subprocess
import shutil
from datetime import datetime
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from werkzeug.utils import secure_filename
import numpy as np

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import AI controller
try:
    from ai_controller.simple_working_ai_controller import SimpleWorkingAIController
except ImportError:
    print("⚠️ AI Controller not found, using mock data")
    SimpleWorkingAIController = None

app = Flask(__name__)
CORS(app)

class TrafficAPI:
    """Main API class for traffic control"""
    
    def __init__(self):
        self.controller = None
        self.simulation_running = False
        self.metrics_history = []
        self.ai_decisions = []
        self.start_time = None
        self.uploaded_video_path = None
        self.unified_ai_controller = None
        
        # Configuration
        self.config_file = "real_traffic_output/visible_traffic_lights.sumocfg"
        self.junction_ids = ["I1", "I2"]
        
        # Video upload settings
        self.upload_folder = "uploaded_videos"
        self.allowed_extensions = {'mp4', 'avi', 'mov', 'webm', 'mkv'}
        
        # Create upload folder if it doesn't exist
        os.makedirs(self.upload_folder, exist_ok=True)
        
        print("Traffic API initialized with video upload support")
    
    def allowed_file(self, filename):
        """Check if file extension is allowed"""
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in self.allowed_extensions
    
    def upload_video(self, file):
        """Upload and process video file"""
        try:
            if file and self.allowed_file(file.filename):
                filename = secure_filename(file.filename)
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"{timestamp}_{filename}"
                filepath = os.path.join(self.upload_folder, filename)
                file.save(filepath)
                
                self.uploaded_video_path = filepath
                print(f"Video uploaded successfully: {filepath}")
                
                return {
                    "success": True,
                    "message": "Video uploaded successfully",
                    "filepath": filepath,
                    "filename": filename
                }
            else:
                return {
                    "success": False,
                    "message": "Invalid file format. Allowed: mp4, avi, mov, webm, mkv"
                }
        except Exception as e:
            print(f"Video upload error: {e}")
            return {
                "success": False,
                "message": f"Upload failed: {str(e)}"
            }
    
    def start_live_simulation(self, video_path=None):
        """Start live SUMO simulation with uploaded video"""
        try:
            # Use uploaded video or default
            video_to_use = video_path or self.uploaded_video_path or "Traffic_videos/stock-footage-drone-shot-way-intersection.webm"
            
            print(f"Starting live simulation with video: {video_to_use}")
            
            # Import unified AI controller
            try:
                from unified_ai_controller import UnifiedAIController
                self.unified_ai_controller = UnifiedAIController(video_to_use)
            except ImportError:
                print("Unified AI Controller not found, using fallback")
                return self._fallback_simulation()
            
            # Start simulation in background thread
            simulation_thread = threading.Thread(target=self._run_live_simulation)
            simulation_thread.daemon = True
            simulation_thread.start()
            
            return {
                "success": True,
                "message": "Live simulation started",
                "video_path": video_to_use,
                "simulation_id": f"sim_{int(time.time())}"
            }
            
        except Exception as e:
            print(f"Live simulation error: {e}")
            return {
                "success": False,
                "message": f"Simulation failed: {str(e)}"
            }
    
    def _run_live_simulation(self):
        """Run the live simulation with AI control"""
        try:
            print("🎬 Starting live video analysis and SUMO simulation...")
            
            # Run unified AI analysis
            results = self.unified_ai_controller.start_unified_analysis()
            
            if results:
                print("✅ Live simulation completed successfully")
                self.simulation_running = True
                self.start_time = datetime.now()
                
                # Store results for dashboard
                self.metrics_history.append({
                    "timestamp": datetime.now().isoformat(),
                    "results": results
                })
            else:
                print("❌ Live simulation failed")
                
        except Exception as e:
            print(f"❌ Live simulation error: {e}")
    
    def _fallback_simulation(self):
        """Fallback simulation when unified AI is not available"""
        try:
            # Create a simple simulation using existing components
            print("Using fallback simulation method...")
            
            # Start SUMO with basic configuration
            subprocess.Popen([
                "sumo-gui", 
                "-c", self.config_file,
                "--start", "--quit-on-end"
            ])
            
            return {
                "success": True,
                "message": "Fallback simulation started",
                "note": "Using basic SUMO simulation"
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"Fallback simulation failed: {str(e)}"
            }
    
    def get_live_metrics(self):
        """Get live simulation metrics"""
        if not self.simulation_running:
            return {
                "simulation_running": False,
                "message": "No simulation running"
            }
        
        # Get latest metrics
        latest_metrics = self.metrics_history[-1] if self.metrics_history else {}
        
        return {
            "simulation_running": True,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "duration": str(datetime.now() - self.start_time) if self.start_time else "0:00:00",
            "metrics": latest_metrics.get("results", {}),
            "ai_performance": latest_metrics.get("results", {}).get("unified_metrics", {}),
            "comparison_data": latest_metrics.get("results", {}).get("comparison_analysis", {})
        }
    
    def start_simulation(self):
        """Open SUMO GUI (user needs to click Run to start AI control)"""
        try:
            # Check if simulation is already running
            if self.simulation_running:
                # Check if controller is still valid
                if self.controller:
                    try:
                        # Try to check if SUMO is still running
                        import traci
                        traci.simulation.getTime()
                        return {"success": False, "status": "already_running", "message": "Simulation already running"}
                    except:
                        # SUMO is not running, reset state
                        print("SUMO not running, resetting state")
                        self.simulation_running = False
                        self.controller = None
                        self.start_time = None
                else:
                    # Controller is None, reset state
                    self.simulation_running = False
                    self.start_time = None
            
            # Start new simulation
            if SimpleWorkingAIController:
                self.controller = SimpleWorkingAIController(
                    junction_ids=self.junction_ids,
                    sumo_config=self.config_file
                )
                
                # Open SUMO GUI but don't auto-start
                if self.controller.start_simulation(gui=True, auto_start=False):
                    self.simulation_running = True  # Mark as ready
                    self.start_time = datetime.now()
                    
                    # Start monitoring thread (will wait for user to click Run)
                    monitor_thread = threading.Thread(target=self._monitor_simulation)
                    monitor_thread.daemon = True
                    monitor_thread.start()
                    
                    return {"success": True, "status": "sumo_opened", "message": "SUMO GUI opened - Click 'Run' to start simulation"}
                else:
                    return {"success": False, "status": "error", "message": "Failed to start SUMO GUI"}
            else:
                # Mock simulation for testing
                self.simulation_running = True
                self.start_time = datetime.now()
                return {"success": True, "status": "mock_running", "message": "Mock simulation started"}
                
        except Exception as e:
            error_msg = str(e).encode('ascii', 'ignore').decode('ascii')
            print(f"Error starting simulation: {error_msg}")
            # Reset state on error
            self.simulation_running = False
            self.controller = None
            self.start_time = None
            return {"success": False, "status": "error", "message": f"Error: {error_msg}"}
    
    def start_ai_control(self):
        """Start AI control (call this when user clicks Run in SUMO)"""
        try:
            if self.controller and self.simulation_running:
                return self.controller.start_ai_control()
            return False
        except Exception as e:
            print(f"Error starting AI control: {e}")
            return False
    
    def stop_simulation(self):
        """Stop SUMO simulation"""
        try:
            if self.simulation_running and self.controller:
                self.controller.close_simulation()
            
            # Always reset state
            self.simulation_running = False
            self.start_time = None
            self.controller = None
            
            print("Simulation state reset")
            return True
        except Exception as e:
            print(f"Error stopping simulation: {e}")
            # Still reset state even if there's an error
            self.simulation_running = False
            self.start_time = None
            self.controller = None
            return False
    
    def _monitor_simulation(self):
        """Monitor simulation and collect metrics"""
        ai_control_started = False
        connection_retries = 0
        max_retries = 5
        
        while self.simulation_running and self.controller:
            try:
                # Check if simulation is actually running (user clicked Run in SUMO)
                try:
                    import traci
                    current_time = traci.simulation.getTime()
                    if not ai_control_started and current_time > 0:
                        # User clicked Run in SUMO, start AI control
                        self.controller.start_ai_control()
                        ai_control_started = True
                        print("User started SUMO simulation - AI control activated!")
                        connection_retries = 0  # Reset retry counter on success
                except Exception as e:
                    # SUMO not running yet or connection lost
                    connection_retries += 1
                    if connection_retries > max_retries:
                        print(f"Lost connection to SUMO after {max_retries} retries")
                        break
                    time.sleep(1)  # Wait before retry
                    continue
                
                # Get current metrics from AI controller
                if ai_control_started:
                    try:
                        metrics = self.controller.get_metrics()
                        if metrics:
                            self.metrics_history.append({
                                'timestamp': datetime.now().isoformat(),
                                'metrics': metrics
                            })
                    except Exception as e:
                        print(f"Error getting metrics: {e}")
                        connection_retries += 1
                        if connection_retries > max_retries:
                            break
                
                time.sleep(2)  # Update every 2 seconds
            except Exception as e:
                print(f"Error monitoring simulation: {e}")
                connection_retries += 1
                if connection_retries > max_retries:
                    break
                time.sleep(1)
    
    def get_metrics(self):
        """Get current simulation metrics"""
        if self.simulation_running and self.controller:
            try:
                metrics = self.controller.get_metrics()
                if metrics:
                    return {
                        'total_vehicles': metrics.get('total_vehicles', 0),
                        'total_waiting_time': metrics.get('total_waiting_time', 0),
                        'total_queue_length': metrics.get('total_queue_length', 0),
                        'avg_speed': metrics.get('avg_speed', 0),
                        'intersections': metrics.get('intersections', {}),
                        'timestamp': datetime.now().isoformat()
                    }
            except Exception as e:
                print(f"Error getting metrics: {e}")
        
        # Return mock data if simulation not running
        return {
            'total_vehicles': 0,
            'total_waiting_time': 0,
            'total_queue_length': 0,
            'avg_speed': 0,
            'intersections': {},
            'timestamp': datetime.now().isoformat()
        }
    
    def get_ai_decisions(self):
        """Get recent AI decisions"""
        return {
            'decisions': self.ai_decisions[-10:],  # Last 10 decisions
            'total_decisions': len(self.ai_decisions)
        }

# Initialize API
traffic_api = TrafficAPI()

@app.route('/')
def index():
    """API status"""
    return jsonify({
        'status': 'Smart Traffic Simulator API',
        'version': '1.0.0',
        'simulation_running': traffic_api.simulation_running
    })

@app.route('/api/status')
def get_status():
    """Get simulation status"""
    return jsonify({
        'simulation_running': traffic_api.simulation_running,
        'start_time': traffic_api.start_time.isoformat() if traffic_api.start_time else None,
        'uptime': (datetime.now() - traffic_api.start_time).total_seconds() if traffic_api.start_time else 0
    })

@app.route('/api/metrics')
def get_metrics():
    """Get current metrics"""
    return jsonify(traffic_api.get_metrics())

@app.route('/api/upload-video', methods=['POST'])
def upload_video():
    """Upload video file for analysis"""
    try:
        if 'video' not in request.files:
            return jsonify({
                'success': False,
                'message': 'No video file provided'
            })
        
        file = request.files['video']
        if file.filename == '':
            return jsonify({
                'success': False,
                'message': 'No file selected'
            })
        
        result = traffic_api.upload_video(file)
        return jsonify(result)
        
    except Exception as e:
        error_msg = str(e).encode('ascii', 'ignore').decode('ascii')
        return jsonify({
            'success': False,
            'message': f'Upload error: {error_msg}'
        })

@app.route('/api/start-live-simulation', methods=['POST'])
def start_live_simulation():
    """Start live SUMO simulation with uploaded video"""
    try:
        data = request.get_json() or {}
        video_path = data.get('video_path')
        
        result = traffic_api.start_live_simulation(video_path)
        return jsonify(result)
        
    except Exception as e:
        error_msg = str(e).encode('ascii', 'ignore').decode('ascii')
        return jsonify({
            'success': False,
            'message': f'Simulation error: {error_msg}'
        })

@app.route('/api/live-metrics')
def get_live_metrics():
    """Get live simulation metrics"""
    try:
        metrics = traffic_api.get_live_metrics()
        return jsonify(metrics)
    except Exception as e:
        error_msg = str(e).encode('ascii', 'ignore').decode('ascii')
        return jsonify({
            'success': False,
            'message': f'Metrics error: {error_msg}'
        })

@app.route('/api/start', methods=['POST'])
def start_simulation():
    """Start simulation"""
    try:
        result = traffic_api.start_simulation()
        return jsonify(result)
    except Exception as e:
        error_msg = str(e).encode('ascii', 'ignore').decode('ascii')
        return jsonify({
            'success': False, 
            'status': 'error', 
            'message': f'API Error: {error_msg}'
        })

@app.route('/api/stop', methods=['POST'])
def stop_simulation():
    """Stop simulation"""
    success = traffic_api.stop_simulation()
    return jsonify({
        'success': success,
        'message': 'Simulation stopped' if success else 'Failed to stop simulation'
    })

@app.route('/api/start-ai', methods=['POST'])
def start_ai_control():
    """Start AI control (call when user clicks Run in SUMO)"""
    success = traffic_api.start_ai_control()
    return jsonify({
        'success': success,
        'message': 'AI control started' if success else 'Failed to start AI control'
    })

@app.route('/api/ai/decisions')
def get_ai_decisions():
    """Get AI decisions"""
    return jsonify(traffic_api.get_ai_decisions())

@app.route('/favicon.ico')
def favicon():
    """Serve favicon"""
    try:
        return send_from_directory('frontend/public', 'favicon.ico')
    except:
        return '', 204  # No content

@app.route('/manifest.json')
def manifest():
    """Serve manifest.json"""
    try:
        return send_from_directory('frontend/public', 'manifest.json')
    except:
        return '', 204  # No content

if __name__ == '__main__':
    print("Starting Smart Traffic Simulator API...")
    print("API will be available at: http://localhost:5000")
    print("Frontend should connect to: http://localhost:3000")
    print("Use the 'Start Simulation' button in the dashboard to begin!")
    
    app.run(host='0.0.0.0', port=5000, debug=True)
