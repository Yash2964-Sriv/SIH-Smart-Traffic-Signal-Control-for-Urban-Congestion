#!/usr/bin/env python3
"""
Dashboard AI Integration - Connect dashboard to AI simulation
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

class DashboardAIIntegration:
    """Dashboard integration for AI simulation"""
    
    def __init__(self):
        self.sumo_process = None
        self.ai_process = None
        self.simulation_running = False
        self.dashboard_config = {
            'sumo_config': 'video_replication_simulation.sumocfg',
            'ai_controller': 'integrated_ai_controller.py',
            'sumo_port': 8813,
            'simulation_duration': 600  # 10 minutes
        }
    
    def start_sumo_simulation(self):
        """Start SUMO simulation"""
        try:
            logger.info("Starting SUMO simulation...")
            self.sumo_process = subprocess.Popen([
                "sumo-gui", 
                "-c", self.dashboard_config['sumo_config'],
                "--remote-port", str(self.dashboard_config['sumo_port'])
            ])
            
            # Wait for SUMO to initialize
            time.sleep(5)
            logger.info("SUMO simulation started successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start SUMO: {e}")
            return False
    
    def start_ai_controller(self):
        """Start AI controller"""
        try:
            logger.info("Starting AI controller...")
            self.ai_process = subprocess.Popen([
                "python", self.dashboard_config['ai_controller']
            ])
            
            logger.info("AI controller started successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start AI controller: {e}")
            return False
    
    def start_simulation(self):
        """Start complete AI simulation from dashboard"""
        logger.info("Starting AI simulation from dashboard...")
        
        try:
            # Start SUMO
            if not self.start_sumo_simulation():
                return False
            
            # Start AI controller
            if not self.start_ai_controller():
                self.stop_simulation()
                return False
            
            self.simulation_running = True
            logger.info("AI simulation started successfully from dashboard")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start simulation: {e}")
            return False
    
    def stop_simulation(self):
        """Stop the simulation"""
        logger.info("Stopping AI simulation...")
        
        try:
            if self.ai_process:
                self.ai_process.terminate()
                self.ai_process.wait(timeout=5)
            
            if self.sumo_process:
                self.sumo_process.terminate()
                self.sumo_process.wait(timeout=5)
            
            self.simulation_running = False
            logger.info("Simulation stopped successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error stopping simulation: {e}")
            return False
    
    def get_simulation_status(self):
        """Get current simulation status"""
        return {
            'running': self.simulation_running,
            'sumo_running': self.sumo_process and self.sumo_process.poll() is None if self.sumo_process else False,
            'ai_running': self.ai_process and self.ai_process.poll() is None if self.ai_process else False,
            'timestamp': time.time()
        }
    
    def get_performance_data(self):
        """Get performance data from simulation"""
        try:
            if os.path.exists('integrated_ai_performance.json'):
                with open('integrated_ai_performance.json', 'r') as f:
                    return json.load(f)
            return None
        except Exception as e:
            logger.error(f"Error reading performance data: {e}")
            return None

def create_dashboard_launcher():
    """Create a dashboard launcher script"""
    launcher_script = '''#!/usr/bin/env python3
"""
Dashboard AI Simulation Launcher
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from dashboard_ai_integration import DashboardAIIntegration

def main():
    print("Dashboard AI Simulation Launcher")
    print("=" * 35)
    
    integration = DashboardAIIntegration()
    
    print("Starting AI simulation...")
    if integration.start_simulation():
        print("✅ AI simulation started successfully!")
        print("SUMO GUI should be open with AI-controlled traffic lights")
        print("The simulation will run for 10 minutes")
        
        # Keep running until user stops
        try:
            while integration.simulation_running:
                status = integration.get_simulation_status()
                if not status['sumo_running'] or not status['ai_running']:
                    break
                time.sleep(1)
        except KeyboardInterrupt:
            print("\\nStopping simulation...")
            integration.stop_simulation()
        
        # Show final performance
        performance = integration.get_performance_data()
        if performance:
            print("\\n📊 Final Performance Report:")
            print(f"Total Vehicles: {performance.get('total_vehicles_processed', 0)}")
            print(f"Average Queue Length: {performance.get('average_queue_length', 0):.2f}")
            print(f"Efficiency Score: {performance.get('average_efficiency_score', 0):.2f}%")
            print(f"AI Decisions Made: {performance.get('ai_decisions_made', 0)}")
    else:
        print("❌ Failed to start AI simulation")

if __name__ == "__main__":
    main()
'''
    
    with open('dashboard_ai_launcher.py', 'w') as f:
        f.write(launcher_script)
    
    logger.info("Dashboard launcher created: dashboard_ai_launcher.py")

def main():
    """Main function"""
    print("Dashboard AI Integration Setup")
    print("=" * 30)
    
    # Create dashboard launcher
    create_dashboard_launcher()
    
    # Test integration
    integration = DashboardAIIntegration()
    
    print("\\nTo start AI simulation from dashboard:")
    print("1. Run: python dashboard_ai_launcher.py")
    print("2. Or integrate with your existing dashboard")
    print("\\nThe AI will control traffic lights based on the real traffic video!")

if __name__ == "__main__":
    main()
