#!/usr/bin/env python3
"""
Dashboard Integration API
Provides functions that can be called from the dashboard
"""

import os
import sys
import json
import subprocess
import threading
import time
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DashboardIntegrationAPI:
    """API for dashboard integration"""
    
    def __init__(self):
        self.simulation_process = None
        self.simulation_running = False
        self.performance_file = "complete_ai_performance.json"
    
    def start_ai_simulation(self):
        """Start AI simulation - called from dashboard"""
        logger.info("Starting AI simulation from dashboard...")
        
        try:
            # Start the complete AI system in a separate process
            self.simulation_process = subprocess.Popen([
                "python", "complete_ai_dashboard_system.py"
            ])
            
            self.simulation_running = True
            logger.info("AI simulation started successfully from dashboard")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start AI simulation: {e}")
            return False
    
    def stop_ai_simulation(self):
        """Stop AI simulation - called from dashboard"""
        logger.info("Stopping AI simulation from dashboard...")
        
        try:
            if self.simulation_process:
                self.simulation_process.terminate()
                self.simulation_process.wait(timeout=10)
            
            self.simulation_running = False
            logger.info("AI simulation stopped successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to stop AI simulation: {e}")
            return False
    
    def get_simulation_status(self):
        """Get simulation status - called from dashboard"""
        status = {
            'running': self.simulation_running,
            'process_running': self.simulation_process and self.simulation_process.poll() is None if self.simulation_process else False,
            'timestamp': time.time()
        }
        
        # Update running status based on process
        if self.simulation_process and self.simulation_process.poll() is not None:
            self.simulation_running = False
        
        return status
    
    def get_performance_data(self):
        """Get performance data - called from dashboard"""
        try:
            if os.path.exists(self.performance_file):
                with open(self.performance_file, 'r') as f:
                    return json.load(f)
            return None
        except Exception as e:
            logger.error(f"Error reading performance data: {e}")
            return None
    
    def is_simulation_ready(self):
        """Check if simulation is ready to start"""
        required_files = [
            "video_replication_simulation.sumocfg",
            "real_traffic_output/visible_traffic_lights.net.xml",
            "real_traffic_output/video_replication_routes.rou.xml",
            "ai_models/DDQL_Replay_600.pkl"
        ]
        
        missing_files = [f for f in required_files if not os.path.exists(f)]
        return len(missing_files) == 0, missing_files

# Global instance for dashboard access
dashboard_api = DashboardIntegrationAPI()

def start_simulation():
    """Function to start simulation - called from dashboard"""
    return dashboard_api.start_ai_simulation()

def stop_simulation():
    """Function to stop simulation - called from dashboard"""
    return dashboard_api.stop_ai_simulation()

def get_status():
    """Function to get status - called from dashboard"""
    return dashboard_api.get_simulation_status()

def get_performance():
    """Function to get performance - called from dashboard"""
    return dashboard_api.get_performance_data()

def is_ready():
    """Function to check if ready - called from dashboard"""
    return dashboard_api.is_simulation_ready()

def main():
    """Test the API"""
    print("Dashboard Integration API Test")
    print("=" * 30)
    
    # Check if ready
    ready, missing = is_ready()
    if ready:
        print("✅ System is ready for AI simulation")
        
        # Test start simulation
        if start_simulation():
            print("✅ AI simulation started successfully")
            
            # Wait a bit
            time.sleep(5)
            
            # Check status
            status = get_status()
            print(f"Status: {status}")
            
            # Stop simulation
            if stop_simulation():
                print("✅ AI simulation stopped successfully")
        else:
            print("❌ Failed to start AI simulation")
    else:
        print(f"❌ System not ready. Missing files: {missing}")

if __name__ == "__main__":
    main()
