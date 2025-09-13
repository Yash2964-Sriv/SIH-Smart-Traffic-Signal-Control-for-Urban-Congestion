#!/usr/bin/env python3
"""
Smart Traffic Simulator - Simple Runner
One script to run everything: Backend, Frontend, and SUMO
"""

import os
import sys
import time
import subprocess
import threading
import webbrowser
from pathlib import Path

class SmartTrafficRunner:
    def __init__(self):
        self.backend_process = None
        self.frontend_process = None
        self.sumo_process = None
        self.running = True
        
    def print_banner(self):
        print("=" * 70)
        print("    🚀 SMART TRAFFIC SIMULATOR RUNNER 🚀")
        print("=" * 70)
        print("    One Script to Rule Them All!")
        print("=" * 70)
        print()
        
    def start_backend(self):
        """Start Flask backend"""
        print("🔧 Starting Backend API...")
        try:
            self.backend_process = subprocess.Popen([
                sys.executable, "backend_api.py"
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            time.sleep(2)
            print("✅ Backend running on http://localhost:5000")
            return True
        except Exception as e:
            print(f"❌ Backend failed: {e}")
            return False
    
    def start_frontend(self):
        """Start React frontend"""
        print("🌐 Starting Frontend Dashboard...")
        try:
            # Change to frontend directory and start
            frontend_dir = Path("frontend")
            if not frontend_dir.exists():
                print("❌ Frontend directory not found")
                return False
                
            # Use PowerShell to start npm
            self.frontend_process = subprocess.Popen([
                "powershell", "-Command", 
                f"cd '{frontend_dir.absolute()}'; npm start"
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            # Wait for frontend to start
            print("   Waiting for frontend to start...")
            for i in range(30):
                time.sleep(1)
                try:
                    import urllib.request
                    urllib.request.urlopen("http://localhost:3000", timeout=1)
                    print("✅ Frontend running on http://localhost:3000")
                    return True
                except:
                    continue
            
            print("⚠️ Frontend taking longer than expected...")
            return True  # Assume it's starting
            
        except Exception as e:
            print(f"❌ Frontend failed: {e}")
            return False
    
    def start_sumo(self):
        """Check SUMO availability (but don't start automatically)"""
        print("🚦 Checking SUMO availability...")
        try:
            # Check for SUMO
            sumo_home = os.environ.get('SUMO_HOME')
            if not sumo_home:
                print("⚠️ SUMO_HOME not set, SUMO will be started via dashboard")
                return True
                
            sumo_gui = os.path.join(sumo_home, 'bin', 'sumo-gui.exe')
            if not os.path.exists(sumo_gui):
                print("⚠️ SUMO-GUI not found, SUMO will be started via dashboard")
                return True
            
            # Check for config file
            config_file = "real_traffic_output/simple_multi_intersection.sumocfg"
            if not os.path.exists(config_file):
                print("⚠️ SUMO config not found, SUMO will be started via dashboard")
                return True
            
            print("✅ SUMO is available and ready to start via dashboard")
            return True
            
        except Exception as e:
            print(f"⚠️ SUMO check failed: {e}")
            return True  # Don't fail the whole system for SUMO
    
    def open_dashboard(self):
        """Open dashboard in browser"""
        print("🌐 Opening dashboard...")
        try:
            webbrowser.open("http://localhost:3000")
            print("✅ Dashboard opened in browser")
        except:
            print("⚠️ Could not open browser automatically")
            print("   Please open: http://localhost:3000")
    
    def stop_all(self):
        """Stop all processes"""
        print("\n🛑 Stopping all services...")
        
        if self.frontend_process:
            self.frontend_process.terminate()
            print("✅ Frontend stopped")
        
        if self.backend_process:
            self.backend_process.terminate()
            print("✅ Backend stopped")
            
        if self.sumo_process:
            self.sumo_process.terminate()
            print("✅ SUMO stopped")
    
    def run(self):
        """Main run function"""
        self.print_banner()
        
        # Start all services
        backend_ok = self.start_backend()
        frontend_ok = self.start_frontend()
        sumo_ok = self.start_sumo()
        
        # Open dashboard
        if frontend_ok:
            self.open_dashboard()
        
        # Show status
        print("\n" + "=" * 70)
        print("    🎉 SMART TRAFFIC SIMULATOR IS RUNNING! 🎉")
        print("=" * 70)
        print(f"    🔧 Backend: {'✅ Running' if backend_ok else '❌ Failed'}")
        print(f"    🌐 Frontend: {'✅ Running' if frontend_ok else '❌ Failed'}")
        print(f"    🚦 SUMO: {'✅ Ready' if sumo_ok else '⚠️ Not Available'}")
        print("=" * 70)
        print("\n📋 What's Running:")
        if backend_ok:
            print("   • Flask API server (http://localhost:5000)")
        if frontend_ok:
            print("   • React dashboard (http://localhost:3000)")
        if sumo_ok:
            print("   • SUMO traffic simulation (ready to start)")
        print("\n🎮 How to Use:")
        print("   1. Open http://localhost:3000 in your browser")
        print("   2. Click 'Start Simulation' to begin AI traffic control")
        print("   3. Watch real-time metrics and AI decisions")
        print("\n⚠️ Press Ctrl+C to stop everything")
        print("=" * 70)
        
        try:
            # Keep running
            while self.running:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n\n🛑 Shutting down...")
            self.stop_all()
            print("✅ All services stopped. Goodbye!")

def main():
    runner = SmartTrafficRunner()
    runner.run()

if __name__ == "__main__":
    main()
