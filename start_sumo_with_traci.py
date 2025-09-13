#!/usr/bin/env python3
"""
Start SUMO with TraCI server properly configured
"""

import subprocess
import time
import os

def start_sumo_with_traci():
    """Start SUMO GUI with TraCI server"""
    print("🚀 Starting SUMO GUI with TraCI server...")
    
    # Find SUMO
    sumo_home = os.environ.get('SUMO_HOME')
    if sumo_home:
        sumo_binary = os.path.join(sumo_home, 'bin', 'sumo-gui.exe')
    else:
        sumo_binary = 'sumo-gui.exe'
    
    # Start SUMO with proper TraCI configuration
    cmd = [
        sumo_binary,
        '-c', 'working_traffic.sumocfg',
        '--remote-port', '8813',
        '--start'
    ]
    
    print(f"🚀 Launching: {' '.join(cmd)}")
    
    try:
        # Start SUMO process
        process = subprocess.Popen(cmd)
        print("✅ SUMO GUI started!")
        print("🎮 SUMO GUI is now running")
        print("⏳ Waiting for TraCI server to initialize...")
        
        # Wait for TraCI server to start
        time.sleep(8)
        
        print("✅ TraCI server should be ready on port 8813")
        print("🎯 You can now connect to SUMO via TraCI")
        
        return process
        
    except Exception as e:
        print(f"❌ Failed to start SUMO: {e}")
        return None

if __name__ == "__main__":
    start_sumo_with_traci()