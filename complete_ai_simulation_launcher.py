#!/usr/bin/env python3
"""
Complete AI Simulation Launcher
Starts SUMO first, then connects AI controller
"""

import os
import sys
import time
import subprocess
import threading
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class CompleteAISimulationLauncher:
    """Complete AI simulation launcher with proper sequencing"""
    
    def __init__(self):
        self.sumo_process = None
        self.ai_controller_process = None
        self.sumo_ready = False
        
    def start_sumo(self):
        """Start SUMO simulation"""
        logger.info("Starting SUMO simulation...")
        
        try:
            # Start SUMO with the video replication configuration
            self.sumo_process = subprocess.Popen([
                "sumo-gui", 
                "-c", "video_replication_simulation.sumocfg",
                "--remote-port", "8813"
            ])
            
            logger.info("SUMO started, waiting for initialization...")
            
            # Wait for SUMO to be ready
            time.sleep(5)
            self.sumo_ready = True
            logger.info("SUMO is ready for AI connection")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start SUMO: {e}")
            return False
    
    def start_ai_controller(self):
        """Start AI controller after SUMO is ready"""
        if not self.sumo_ready:
            logger.error("SUMO not ready, cannot start AI controller")
            return False
        
        logger.info("Starting AI controller...")
        
        try:
            # Start AI controller
            self.ai_controller_process = subprocess.Popen([
                "python", "simple_working_ai_simulation.py"
            ])
            
            logger.info("AI controller started successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start AI controller: {e}")
            return False
    
    def monitor_processes(self):
        """Monitor both processes"""
        logger.info("Monitoring simulation processes...")
        
        try:
            while True:
                # Check if SUMO is still running
                if self.sumo_process and self.sumo_process.poll() is not None:
                    logger.info("SUMO process ended")
                    break
                
                # Check if AI controller is still running
                if self.ai_controller_process and self.ai_controller_process.poll() is not None:
                    logger.info("AI controller process ended")
                    break
                
                time.sleep(1)
                
        except KeyboardInterrupt:
            logger.info("Simulation interrupted by user")
        except Exception as e:
            logger.error(f"Error monitoring processes: {e}")
    
    def cleanup(self):
        """Clean up processes"""
        logger.info("Cleaning up processes...")
        
        if self.ai_controller_process:
            self.ai_controller_process.terminate()
            try:
                self.ai_controller_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.ai_controller_process.kill()
        
        if self.sumo_process:
            self.sumo_process.terminate()
            try:
                self.sumo_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.sumo_process.kill()
        
        logger.info("Cleanup completed")
    
    def run_complete_simulation(self):
        """Run the complete AI simulation"""
        logger.info("Starting complete AI simulation...")
        
        try:
            # Step 1: Start SUMO
            if not self.start_sumo():
                logger.error("Failed to start SUMO")
                return False
            
            # Step 2: Start AI controller
            if not self.start_ai_controller():
                logger.error("Failed to start AI controller")
                self.cleanup()
                return False
            
            # Step 3: Monitor processes
            self.monitor_processes()
            
            logger.info("Simulation completed successfully!")
            return True
            
        except Exception as e:
            logger.error(f"Simulation failed: {e}")
            return False
        
        finally:
            self.cleanup()

def main():
    """Main function"""
    print("Complete AI Traffic Simulation Launcher")
    print("=" * 40)
    print("This will:")
    print("1. Start SUMO with video replication configuration")
    print("2. Wait for SUMO to initialize")
    print("3. Start AI controller to control traffic lights")
    print("4. Monitor the simulation")
    print()
    
    # Check if required files exist
    required_files = [
        "video_replication_simulation.sumocfg",
        "real_traffic_output/visible_traffic_lights.net.xml",
        "real_traffic_output/video_replication_routes.rou.xml",
        "simple_working_ai_simulation.py"
    ]
    
    missing_files = [f for f in required_files if not os.path.exists(f)]
    if missing_files:
        print(f"Missing required files: {missing_files}")
        print("Please run the video analysis first: python video_analysis_and_replication.py")
        return
    
    # Ask user if they want to proceed
    response = input("Do you want to start the complete AI simulation? (y/n): ")
    if response.lower() != 'y':
        print("Simulation cancelled.")
        return
    
    # Create and run launcher
    launcher = CompleteAISimulationLauncher()
    success = launcher.run_complete_simulation()
    
    if success:
        print("\n✅ AI simulation completed successfully!")
        print("Check 'simple_ai_performance.json' for performance metrics.")
    else:
        print("\n❌ Simulation failed. Check the logs for details.")

if __name__ == "__main__":
    main()
