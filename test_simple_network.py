#!/usr/bin/env python3
"""
Test script for the simple multi-intersection network
"""

import os
import sys
import subprocess
import time

def test_network():
    """Test if the simple network works"""
    print("🧪 Testing Simple Multi-Intersection Network")
    print("=" * 50)
    
    # Check if SUMO is available
    sumo_paths = [
        r"C:\Program Files (x86)\Eclipse\Sumo\bin\sumo-gui.exe",
        r"C:\Program Files\Eclipse\Sumo\bin\sumo-gui.exe",
        "sumo-gui"
    ]
    
    sumo_path = None
    for path in sumo_paths:
        if os.path.exists(path):
            sumo_path = path
            break
    
    if not sumo_path:
        try:
            result = subprocess.run(["where", "sumo-gui"], capture_output=True, text=True)
            if result.returncode == 0:
                sumo_path = "sumo-gui"
        except:
            pass
    
    if not sumo_path:
        print("❌ SUMO not found!")
        return False
    
    print(f"✅ SUMO found: {sumo_path}")
    
    # Test network file
    config_file = "real_traffic_output/simple_multi_intersection.sumocfg"
    if not os.path.exists(config_file):
        print(f"❌ Config file not found: {config_file}")
        return False
    
    print(f"✅ Config file found: {config_file}")
    
    try:
        print("\n🚀 Launching SUMO GUI for testing...")
        print("   - If SUMO opens successfully, the network is working")
        print("   - Close SUMO when you're done testing")
        
        # Launch SUMO GUI
        if os.path.exists(sumo_path):
            cmd = [sumo_path, "-c", config_file, "--start"]
        else:
            cmd = ["sumo-gui", "-c", config_file, "--start"]
        
        process = subprocess.Popen(cmd)
        
        print("✅ SUMO GUI launched successfully!")
        print("   Check if the simulation is running properly...")
        
        # Wait for user to close SUMO
        input("\nPress Enter after you've tested SUMO and closed it...")
        
        return True
        
    except Exception as e:
        print(f"❌ Error launching SUMO: {e}")
        return False

if __name__ == "__main__":
    test_network()

