"""
Run Real Traffic Simulation
Easy script to run SUMO simulation with your real traffic data
"""

import subprocess
import os
import sys
from pathlib import Path

def run_real_traffic_simulation():
    """Run SUMO simulation with real traffic data"""
    print("🚦 Running Real Traffic Simulation")
    print("=" * 35)
    
    # Check if files exist
    config_file = "real_traffic_output/real_traffic_simulation.sumocfg"
    network_file = "real_traffic_output/real_traffic_network.net.xml"
    routes_file = "real_traffic_output/real_traffic_routes.rou.xml"
    
    if not os.path.exists(config_file):
        print(f"❌ Configuration file not found: {config_file}")
        return False
    
    if not os.path.exists(network_file):
        print(f"❌ Network file not found: {network_file}")
        return False
    
    if not os.path.exists(routes_file):
        print(f"❌ Routes file not found: {routes_file}")
        return False
    
    print("✅ All files found, starting simulation...")
    
    # Run SUMO command line simulation first
    print("\n1️⃣ Running SUMO command line simulation...")
    try:
        result = subprocess.run([
            r"C:\Program Files (x86)\Eclipse\Sumo\bin\sumo.exe",
            "-c", config_file
        ], capture_output=True, text=True, timeout=60)
        
        if result.returncode == 0:
            print("✅ SUMO simulation completed successfully!")
            print("   Simulation output:")
            print(result.stdout)
        else:
            print("❌ SUMO simulation failed:")
            print(result.stderr)
            return False
            
    except subprocess.TimeoutExpired:
        print("⏰ SUMO simulation timed out")
        return False
    except Exception as e:
        print(f"❌ Error running SUMO: {e}")
        return False
    
    # Launch SUMO GUI
    print("\n2️⃣ Launching SUMO GUI...")
    try:
        subprocess.Popen([
            r"C:\Program Files (x86)\Eclipse\Sumo\bin\sumo-gui.exe",
            "-c", config_file
        ])
        print("✅ SUMO GUI launched successfully!")
        print("   You should see the GUI window with your traffic simulation")
        return True
        
    except Exception as e:
        print(f"❌ Error launching SUMO GUI: {e}")
        return False

def show_analysis_summary():
    """Show analysis summary from the processed video"""
    print("\n📊 Real Traffic Analysis Summary")
    print("=" * 35)
    
    analysis_file = "real_traffic_output/real_traffic_analysis.json"
    
    if os.path.exists(analysis_file):
        try:
            import json
            with open(analysis_file, 'r') as f:
                data = json.load(f)
            
            print(f"📹 Video Information:")
            print(f"   File: {data['video_info']['path']}")
            print(f"   Resolution: {data['video_info']['resolution'][0]}x{data['video_info']['resolution'][1]}")
            print(f"   Duration: {data['video_info']['duration']:.2f} seconds")
            print(f"   FPS: {data['video_info']['fps']}")
            
            print(f"\n🚗 Vehicle Detection:")
            print(f"   Frames processed: {data['processing_stats']['frames_processed']}")
            print(f"   Total vehicles: {data['processing_stats']['total_vehicles']}")
            print(f"   Lanes detected: {', '.join(data['processing_stats']['lanes_detected'])}")
            
            print(f"\n🚦 SUMO Files Generated:")
            print(f"   Network: real_traffic_output/real_traffic_network.net.xml")
            print(f"   Routes: real_traffic_output/real_traffic_routes.rou.xml")
            print(f"   Config: real_traffic_output/real_traffic_simulation.sumocfg")
            
        except Exception as e:
            print(f"❌ Error reading analysis file: {e}")
    else:
        print("❌ Analysis file not found")

def main():
    """Main function"""
    print("🎬 Real Traffic Video to SUMO Replication")
    print("=" * 45)
    
    # Show analysis summary
    show_analysis_summary()
    
    # Run simulation
    success = run_real_traffic_simulation()
    
    if success:
        print(f"\n🎉 Real traffic simulation completed successfully!")
        print(f"📁 Check the 'real_traffic_output' directory for all files")
        print(f"🖥️  SUMO GUI should be running with your traffic data")
    else:
        print(f"\n❌ Simulation failed. Check the error messages above.")

if __name__ == "__main__":
    main()
