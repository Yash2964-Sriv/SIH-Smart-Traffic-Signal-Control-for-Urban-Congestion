#!/usr/bin/env python3
"""
Manual Dashboard Startup Script
Starts backend and provides instructions for frontend
"""

import os
import sys
import time
import subprocess
import threading
import webbrowser
from datetime import datetime

def print_banner():
    """Print startup banner"""
    print("=" * 80)
    print("🚀 SMART TRAFFIC SIMULATOR - MANUAL DASHBOARD LAUNCHER")
    print("=" * 80)
    print("Starting Backend API and providing frontend instructions...")
    print("=" * 80)

def start_backend():
    """Start the backend API server"""
    print("\n🔧 Starting Backend API Server...")
    
    try:
        # Start backend in background
        backend_process = subprocess.Popen([
            sys.executable, "backend_api.py"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        # Wait a moment and check if it started
        time.sleep(3)
        
        if backend_process.poll() is None:
            print("✅ Backend API started on http://localhost:5000")
            return backend_process
        else:
            print("❌ Backend API failed to start")
            return None
            
    except Exception as e:
        print(f"❌ Failed to start backend: {e}")
        return None

def test_backend():
    """Test if backend is working"""
    print("\n🧪 Testing Backend API...")
    
    try:
        import requests
        response = requests.get("http://localhost:5000/api/metrics", timeout=5)
        if response.status_code == 200:
            print("✅ Backend API is responding correctly")
            return True
        else:
            print("❌ Backend API not responding properly")
            return False
    except Exception as e:
        print(f"❌ Backend API test failed: {e}")
        return False

def show_frontend_instructions():
    """Show frontend startup instructions"""
    print("\n" + "="*80)
    print("🎨 FRONTEND STARTUP INSTRUCTIONS")
    print("="*80)
    print("To start the frontend dashboard, please run these commands:")
    print()
    print("1. Open a NEW command prompt/terminal")
    print("2. Navigate to the frontend directory:")
    print("   cd frontend")
    print()
    print("3. Install dependencies (if not already done):")
    print("   npm install")
    print()
    print("4. Start the frontend server:")
    print("   npm start")
    print()
    print("5. Wait for the browser to open automatically")
    print("   Or manually open: http://localhost:3000")
    print()
    print("🎯 Once both are running:")
    print("   • Backend API: http://localhost:5000")
    print("   • Frontend Dashboard: http://localhost:3000")
    print("   • Click 'Live Video Simulation' to upload videos")
    print("="*80)

def show_dashboard_features():
    """Show dashboard features"""
    print("\n🎬 DASHBOARD FEATURES AVAILABLE:")
    print("="*50)
    print("📹 Video Upload: Upload real traffic videos")
    print("🎮 Live Simulation: Start SUMO with AI control")
    print("📊 Real-time Metrics: Live performance monitoring")
    print("🤖 AI Control: Intelligent traffic signal management")
    print("📈 Live Comparison: AI vs Real traffic analysis")
    print("⚡ Efficiency Tracking: See AI improvements")
    print("🎯 Pattern Recognition: Vehicle detection and tracking")
    print("="*50)

def monitor_backend(backend_process):
    """Monitor backend process"""
    print("\n🔄 Monitoring Backend API...")
    print("Backend is running. Press Ctrl+C to stop.")
    
    try:
        while True:
            time.sleep(5)
            
            # Check if backend is still running
            if backend_process.poll() is not None:
                print("❌ Backend process stopped")
                break
            
            print("✅ Backend API running...")
            
    except KeyboardInterrupt:
        print("\n🛑 Stopping Backend API...")
        backend_process.terminate()
        print("✅ Backend stopped")

def main():
    """Main function"""
    print_banner()
    
    # Start backend
    backend_process = start_backend()
    if not backend_process:
        print("❌ Failed to start backend. Exiting.")
        return
    
    # Test backend
    if not test_backend():
        print("⚠️  Backend may not be working properly")
    
    # Show frontend instructions
    show_frontend_instructions()
    
    # Show dashboard features
    show_dashboard_features()
    
    # Open browser to backend API
    try:
        webbrowser.open("http://localhost:5000")
        print("\n🌐 Backend API opened in browser")
    except:
        print("\n⚠️  Could not open browser automatically")
    
    # Monitor backend
    monitor_backend(backend_process)

if __name__ == "__main__":
    main()


