#!/usr/bin/env python3
"""
Complete Dashboard Startup Script
Starts both frontend and backend with proper error handling
"""

import os
import sys
import time
import subprocess
import threading
import signal
import webbrowser
from datetime import datetime

class DashboardLauncher:
    def __init__(self):
        self.frontend_process = None
        self.backend_process = None
        self.running = True
        
    def print_banner(self):
        """Print startup banner"""
        print("=" * 80)
        print("🚀 SMART TRAFFIC SIMULATOR - COMPLETE DASHBOARD LAUNCHER")
        print("=" * 80)
        print("Starting Frontend, Backend, and all services...")
        print("=" * 80)
    
    def check_requirements(self):
        """Check if all requirements are met"""
        print("\n🔍 Checking Requirements...")
        
        # Check if we're in the right directory
        if not os.path.exists("frontend") or not os.path.exists("backend_api.py"):
            print("❌ Not in the correct directory. Please run from Smart_Traffic_Simulator root.")
            return False
        
        # Check if frontend package.json exists
        if not os.path.exists("frontend/package.json"):
            print("❌ Frontend package.json not found")
            return False
        
        # Check if backend API exists
        if not os.path.exists("backend_api.py"):
            print("❌ Backend API not found")
            return False
        
        print("✅ All requirements met!")
        return True
    
    def install_frontend_dependencies(self):
        """Install frontend dependencies"""
        print("\n📦 Installing Frontend Dependencies...")
        
        try:
            os.chdir("frontend")
            result = subprocess.run(["npm", "install"], 
                                 capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0:
                print("✅ Frontend dependencies installed successfully")
                os.chdir("..")
                return True
            else:
                print(f"❌ Frontend dependency installation failed: {result.stderr}")
                os.chdir("..")
                return False
                
        except subprocess.TimeoutExpired:
            print("❌ Frontend dependency installation timed out")
            os.chdir("..")
            return False
        except Exception as e:
            print(f"❌ Frontend dependency installation error: {e}")
            os.chdir("..")
            return False
    
    def start_backend(self):
        """Start the backend API server"""
        print("\n🔧 Starting Backend API Server...")
        
        try:
            self.backend_process = subprocess.Popen([
                sys.executable, "backend_api.py"
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            
            # Wait a moment and check if it started
            time.sleep(3)
            
            if self.backend_process.poll() is None:
                print("✅ Backend API started on http://localhost:5000")
                return True
            else:
                print("❌ Backend API failed to start")
                return False
                
        except Exception as e:
            print(f"❌ Failed to start backend: {e}")
            return False
    
    def start_frontend(self):
        """Start the frontend development server"""
        print("\n🎨 Starting Frontend Development Server...")
        
        try:
            os.chdir("frontend")
            
            # Start frontend in background
            self.frontend_process = subprocess.Popen([
                "npm", "start"
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            
            os.chdir("..")
            
            # Wait for frontend to start
            print("⏳ Waiting for frontend to start...")
            time.sleep(10)
            
            # Check if frontend is running
            if self.frontend_process.poll() is None:
                print("✅ Frontend started on http://localhost:3000")
                return True
            else:
                print("❌ Frontend failed to start")
                return False
                
        except Exception as e:
            print(f"❌ Failed to start frontend: {e}")
            os.chdir("..")
            return False
    
    def test_services(self):
        """Test if services are running"""
        print("\n🧪 Testing Services...")
        
        import requests
        
        # Test backend
        try:
            response = requests.get("http://localhost:5000/api/metrics", timeout=5)
            if response.status_code == 200:
                print("✅ Backend API is responding")
            else:
                print("❌ Backend API not responding properly")
                return False
        except Exception as e:
            print(f"❌ Backend API test failed: {e}")
            return False
        
        # Test frontend
        try:
            response = requests.get("http://localhost:3000", timeout=5)
            if response.status_code == 200:
                print("✅ Frontend is responding")
            else:
                print("❌ Frontend not responding properly")
                return False
        except Exception as e:
            print(f"❌ Frontend test failed: {e}")
            return False
        
        return True
    
    def open_dashboard(self):
        """Open dashboard in browser"""
        print("\n🌐 Opening Dashboard in Browser...")
        
        try:
            webbrowser.open("http://localhost:3000")
            print("✅ Dashboard opened in browser")
        except Exception as e:
            print(f"⚠️  Could not open browser automatically: {e}")
            print("   Please manually open: http://localhost:3000")
    
    def show_instructions(self):
        """Show usage instructions"""
        print("\n" + "="*80)
        print("📋 DASHBOARD USAGE INSTRUCTIONS")
        print("="*80)
        print("🌐 Dashboard URL: http://localhost:3000")
        print("🔧 Backend API: http://localhost:5000")
        print("\n🎯 How to Use:")
        print("1. 📱 Click 'Live Video Simulation' in the sidebar")
        print("2. 📹 Upload a real traffic video (MP4, AVI, MOV, WEBM, MKV)")
        print("3. 🚦 Click 'Start Live Simulation' to begin AI analysis")
        print("4. 🎮 Watch SUMO GUI open with your replicated traffic")
        print("5. 📊 Monitor live metrics and AI performance")
        print("\n🎬 Features Available:")
        print("   • Real-time video upload and analysis")
        print("   • Live SUMO simulation with AI control")
        print("   • Real-time metrics and comparison")
        print("   • AI efficiency improvements tracking")
        print("   • Live traffic signal optimization")
        print("\n🛑 To stop all services: Press Ctrl+C")
        print("="*80)
    
    def monitor_processes(self):
        """Monitor running processes"""
        print("\n🔄 Monitoring services...")
        print("Press Ctrl+C to stop all services")
        
        try:
            while self.running:
                time.sleep(5)
                
                # Check if processes are still running
                if self.backend_process and self.backend_process.poll() is not None:
                    print("❌ Backend process stopped")
                    break
                
                if self.frontend_process and self.frontend_process.poll() is not None:
                    print("❌ Frontend process stopped")
                    break
                
                print("✅ All services running...")
                
        except KeyboardInterrupt:
            self.stop_services()
    
    def stop_services(self):
        """Stop all services"""
        print("\n🛑 Stopping all services...")
        self.running = False
        
        if self.backend_process:
            self.backend_process.terminate()
            print("✅ Backend stopped")
        
        if self.frontend_process:
            self.frontend_process.terminate()
            print("✅ Frontend stopped")
        
        print("🎉 All services stopped!")
    
    def run(self):
        """Main launcher function"""
        self.print_banner()
        
        # Check requirements
        if not self.check_requirements():
            return False
        
        # Install frontend dependencies
        if not self.install_frontend_dependencies():
            print("⚠️  Frontend dependencies installation failed, but continuing...")
        
        # Start backend
        if not self.start_backend():
            print("❌ Failed to start backend")
            return False
        
        # Start frontend
        if not self.start_frontend():
            print("❌ Failed to start frontend")
            self.stop_services()
            return False
        
        # Test services
        if not self.test_services():
            print("⚠️  Some services may not be working properly")
        
        # Open dashboard
        self.open_dashboard()
        
        # Show instructions
        self.show_instructions()
        
        # Monitor processes
        self.monitor_processes()
        
        return True

def main():
    """Main function"""
    launcher = DashboardLauncher()
    
    # Handle Ctrl+C gracefully
    def signal_handler(sig, frame):
        print("\n🛑 Received interrupt signal...")
        launcher.stop_services()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    
    # Run launcher
    success = launcher.run()
    
    if success:
        print("\n🎉 Dashboard launcher completed successfully!")
    else:
        print("\n❌ Dashboard launcher failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()


