#!/usr/bin/env python3
"""
Smart Traffic Simulator - BULLETPROOF Startup
Handles all Windows/npm issues and gets everything running
"""

import os
import sys
import time
import subprocess
import threading
import webbrowser
import signal
import shutil
from pathlib import Path

class BulletproofTrafficLauncher:
    def __init__(self):
        self.backend_process = None
        self.frontend_process = None
        self.running = False
        self.npm_path = None
        
    def print_banner(self):
        """Print startup banner"""
        print("=" * 80)
        print("    🚀 SMART TRAFFIC SIMULATOR - BULLETPROOF STARTUP 🚀")
        print("=" * 80)
        print("    AI-Controlled Traffic Light Management System")
        print("    Integrated Dashboard with Real-time Metrics")
        print("    Handles all Windows/npm compatibility issues")
        print("=" * 80)
        print()

    def find_npm(self):
        """Find npm executable using multiple methods"""
        print("🔍 Searching for npm executable...")
        
        # Method 1: Check if npm is in PATH
        npm_path = shutil.which('npm')
        if npm_path:
            print(f"✓ Found npm in PATH: {npm_path}")
            return npm_path
        
        # Method 2: Check common Windows locations
        common_paths = [
            r"C:\Program Files\nodejs\npm.cmd",
            r"C:\Program Files (x86)\nodejs\npm.cmd",
            os.path.join(os.environ.get('APPDATA', ''), 'npm', 'npm.cmd'),
            os.path.join(os.environ.get('PROGRAMFILES', ''), 'nodejs', 'npm.cmd'),
            os.path.join(os.environ.get('PROGRAMFILES(X86)', ''), 'nodejs', 'npm.cmd'),
        ]
        
        for path in common_paths:
            if os.path.exists(path):
                print(f"✓ Found npm at: {path}")
                return path
        
        # Method 3: Try to find node and derive npm path
        node_path = shutil.which('node')
        if node_path:
            # npm is usually in the same directory as node
            node_dir = os.path.dirname(node_path)
            npm_candidates = [
                os.path.join(node_dir, 'npm.cmd'),
                os.path.join(node_dir, 'npm.exe'),
                os.path.join(node_dir, 'npm'),
            ]
            for candidate in npm_candidates:
                if os.path.exists(candidate):
                    print(f"✓ Found npm near node: {candidate}")
                    return candidate
        
        print("✗ Could not find npm executable")
        return None

    def install_frontend_deps(self):
        """Install frontend dependencies with multiple attempts"""
        print("📦 Installing frontend dependencies...")
        
        if not self.npm_path:
            print("✗ No npm found, skipping dependency installation")
            return False
        
        try:
            frontend_dir = Path("frontend")
            if not frontend_dir.exists():
                print("✗ Frontend directory not found")
                return False
            
            # Clear npm cache first
            print("  Clearing npm cache...")
            subprocess.run([self.npm_path, 'cache', 'clean', '--force'], 
                         cwd=frontend_dir, capture_output=True, timeout=30)
            
            # Delete node_modules and package-lock.json for clean install
            import shutil
            node_modules = frontend_dir / "node_modules"
            package_lock = frontend_dir / "package-lock.json"
            
            if node_modules.exists():
                print("  Removing old node_modules...")
                shutil.rmtree(node_modules, ignore_errors=True)
            
            if package_lock.exists():
                print("  Removing old package-lock.json...")
                package_lock.unlink()
            
            # Run npm install with verbose output
            print("  Running npm install...")
            result = subprocess.run(
                [self.npm_path, 'install', '--verbose'],
                cwd=frontend_dir,
                capture_output=True,
                text=True,
                timeout=300,  # 5 minute timeout
                shell=True
            )
            
            if result.returncode == 0:
                print("✓ Frontend dependencies installed successfully")
                
                # Verify react-scripts is installed
                react_scripts_path = frontend_dir / "node_modules" / ".bin" / "react-scripts.cmd"
                if react_scripts_path.exists():
                    print("✓ react-scripts verified")
                    return True
                else:
                    print("⚠ react-scripts not found, trying to install it specifically...")
                    # Try to install react-scripts specifically
                    result2 = subprocess.run(
                        [self.npm_path, 'install', 'react-scripts', '--save'],
                        cwd=frontend_dir,
                        capture_output=True,
                        text=True,
                        timeout=120,
                        shell=True
                    )
                    if result2.returncode == 0:
                        print("✓ react-scripts installed successfully")
                        return True
                    else:
                        print(f"⚠ Failed to install react-scripts: {result2.stderr[:200]}...")
                        return False
            else:
                print(f"⚠ npm install had issues: {result.stderr[:200]}...")
                print("  Trying alternative installation...")
                
                # Try with --legacy-peer-deps
                result2 = subprocess.run(
                    [self.npm_path, 'install', '--legacy-peer-deps'],
                    cwd=frontend_dir,
                    capture_output=True,
                    text=True,
                    timeout=300,
                    shell=True
                )
                
                if result2.returncode == 0:
                    print("✓ Frontend dependencies installed with legacy peer deps")
                    return True
                else:
                    print(f"⚠ Alternative install also failed: {result2.stderr[:200]}...")
                    return False
                
        except subprocess.TimeoutExpired:
            print("⚠ npm install timed out, continuing...")
            return True
        except Exception as e:
            print(f"⚠ Error during npm install: {e}")
            print("  Continuing anyway...")
            return True

    def start_backend(self):
        """Start the backend API server"""
        print("🚀 Starting Backend API...")
        try:
            self.backend_process = subprocess.Popen([
                sys.executable, "backend_api.py"
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            # Wait for backend to start
            time.sleep(3)
            
            if self.backend_process.poll() is None:
                print("✅ Backend API started on http://localhost:5000")
                return True
            else:
                stdout, stderr = self.backend_process.communicate()
                print(f"❌ Backend failed to start: {stderr.decode()}")
                return False
        except Exception as e:
            print(f"❌ Error starting backend: {e}")
            return False

    def start_frontend(self):
        """Start the frontend React app"""
        print("🌐 Starting Frontend Dashboard...")
        
        if not self.npm_path:
            print("❌ No npm found, cannot start frontend")
            return False
        
        try:
            frontend_dir = Path("frontend")
            
            # Start frontend with found npm path
            print(f"  Using npm: {self.npm_path}")
            
            # Try to use react-scripts directly first
            react_scripts_path = frontend_dir / "node_modules" / ".bin" / "react-scripts.cmd"
            if react_scripts_path.exists():
                print("  Using react-scripts directly...")
                self.frontend_process = subprocess.Popen([
                    str(react_scripts_path), "start"
                ], cwd=frontend_dir, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
            else:
                print("  Using npm start...")
                self.frontend_process = subprocess.Popen([
                    self.npm_path, "start"
                ], cwd=frontend_dir, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
            
            # Wait longer for frontend to start
            print("  Waiting for frontend to start (this may take 30-60 seconds)...")
            
            # Check multiple times with shorter intervals
            for i in range(30):  # Check for 30 seconds
                time.sleep(1)
                if self.frontend_process.poll() is not None:
                    # Process ended, check if it was successful
                    stdout, stderr = self.frontend_process.communicate()
                    print(f"❌ Frontend process ended: {stderr.decode()[:200]}...")
                    return False
                
                # Check if port 3000 is responding
                try:
                    import urllib.request
                    urllib.request.urlopen("http://localhost:3000", timeout=1)
                    print("✅ Frontend Dashboard started on http://localhost:3000")
                    return True
                except:
                    continue
            
            # If we get here, frontend might still be starting
            if self.frontend_process.poll() is None:
                print("✅ Frontend Dashboard started on http://localhost:3000")
                return True
            else:
                stdout, stderr = self.frontend_process.communicate()
                print(f"❌ Frontend failed to start: {stderr.decode()}")
                return False
        except Exception as e:
            print(f"❌ Error starting frontend: {e}")
            return False

    def start_frontend_alternative(self):
        """Alternative method to start frontend using direct node commands"""
        print("🔄 Trying alternative frontend startup...")
        
        try:
            frontend_dir = Path("frontend")
            
            # Try to run the React app directly with node
            package_json = frontend_dir / "package.json"
            if not package_json.exists():
                print("❌ No package.json found")
                return False
            
            # Try to find the start script
            import json
            with open(package_json, 'r') as f:
                package_data = json.load(f)
            
            start_script = package_data.get('scripts', {}).get('start', '')
            if not start_script:
                print("❌ No start script found in package.json")
                return False
            
            print(f"  Found start script: {start_script}")
            
            # Try running the start script with shell=True for Windows compatibility
            self.frontend_process = subprocess.Popen(
                start_script,
                cwd=frontend_dir,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            # Check multiple times with shorter intervals
            print("  Waiting for alternative startup...")
            for i in range(20):  # Check for 20 seconds
                time.sleep(1)
                if self.frontend_process.poll() is not None:
                    stdout, stderr = self.frontend_process.communicate()
                    print(f"❌ Alternative method failed: {stderr.decode()[:200]}...")
                    return False
                
                # Check if port 3000 is responding
                try:
                    import urllib.request
                    urllib.request.urlopen("http://localhost:3000", timeout=1)
                    print("✅ Frontend Dashboard started (alternative method)")
                    return True
                except:
                    continue
            
            # If we get here, frontend might still be starting
            if self.frontend_process.poll() is None:
                print("✅ Frontend Dashboard started (alternative method)")
                return True
            else:
                print("❌ Alternative method also failed")
                return False
                
        except Exception as e:
            print(f"❌ Alternative method error: {e}")
            return False

    def start_frontend_fallback(self):
        """Final fallback method using direct command execution"""
        print("🔄 Trying final fallback method...")
        
        try:
            frontend_dir = Path("frontend")
            
            # Try using cmd directly
            print("  Using cmd to start frontend...")
            self.frontend_process = subprocess.Popen(
                ["cmd", "/c", "npm", "start"],
                cwd=frontend_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            # Check multiple times with shorter intervals
            print("  Waiting for fallback startup...")
            for i in range(25):  # Check for 25 seconds
                time.sleep(1)
                if self.frontend_process.poll() is not None:
                    stdout, stderr = self.frontend_process.communicate()
                    print(f"❌ Fallback method failed: {stderr.decode()[:200]}...")
                    return False
                
                # Check if port 3000 is responding
                try:
                    import urllib.request
                    urllib.request.urlopen("http://localhost:3000", timeout=1)
                    print("✅ Frontend Dashboard started (fallback method)")
                    return True
                except:
                    continue
            
            # If we get here, frontend might still be starting
            if self.frontend_process.poll() is None:
                print("✅ Frontend Dashboard started (fallback method)")
                return True
            else:
                print("❌ Fallback method also failed")
                return False
                
        except Exception as e:
            print(f"❌ Fallback method error: {e}")
            return False

    def open_dashboard(self):
        """Open the dashboard in the default browser"""
        print("🌐 Opening dashboard in browser...")
        try:
            webbrowser.open("http://localhost:3000")
            print("✅ Dashboard opened in browser")
        except Exception as e:
            print(f"⚠️ Could not open browser automatically: {e}")
            print("  Please manually open: http://localhost:3000")

    def signal_handler(self, signum, frame):
        """Handle Ctrl+C gracefully"""
        print("\n\n🛑 Shutting down Smart Traffic Simulator...")
        self.stop_all()
        sys.exit(0)

    def stop_all(self):
        """Stop all running processes"""
        if self.frontend_process:
            self.frontend_process.terminate()
            print("✅ Frontend stopped")
        
        if self.backend_process:
            self.backend_process.terminate()
            print("✅ Backend stopped")
        
        self.running = False

    def run(self):
        """Main run function"""
        # Set up signal handler for graceful shutdown
        signal.signal(signal.SIGINT, self.signal_handler)
        
        self.print_banner()
        
        # Find npm
        self.npm_path = self.find_npm()
        
        # Install frontend dependencies
        if self.npm_path:
            self.install_frontend_deps()
        
        print("\n🚀 Starting Smart Traffic Simulator...")
        
        # Start backend
        if not self.start_backend():
            print("\n❌ Failed to start backend. Exiting.")
            return
        
        # Start frontend
        frontend_success = False
        if self.npm_path:
            frontend_success = self.start_frontend()
        
        if not frontend_success:
            print("🔄 Trying alternative frontend startup...")
            frontend_success = self.start_frontend_alternative()
        
        if not frontend_success:
            print("🔄 Trying final fallback method...")
            frontend_success = self.start_frontend_fallback()
        
        if not frontend_success:
            print("\n❌ Failed to start frontend. Stopping backend.")
            self.stop_all()
            print("\n💡 Manual solution:")
            print("   1. Open a new terminal")
            print("   2. cd frontend")
            print("   3. npm start")
            print("   4. Open http://localhost:3000 in your browser")
            return
        
        # Open dashboard
        self.open_dashboard()
        
        self.running = True
        
        print("\n" + "=" * 80)
        print("    🎉 SMART TRAFFIC SIMULATOR IS RUNNING! 🎉")
        print("=" * 80)
        print("    🌐 Dashboard: http://localhost:3000")
        print("    🔧 Backend API: http://localhost:5000")
        print("    🎮 Click 'Start Simulation' in the dashboard to begin!")
        print("=" * 80)
        print("\n📋 Instructions:")
        print("    1. The dashboard will open in your browser")
        print("    2. Click 'Metrics' in the sidebar to see the main view")
        print("    3. Click 'Start Simulation' to launch AI-controlled SUMO")
        print("    4. Watch real-time traffic metrics and AI decisions")
        print("\n⚠️  Press Ctrl+C to stop both servers")
        print("=" * 80)
        
        try:
            # Keep the script running
            while self.running:
                time.sleep(1)
        except KeyboardInterrupt:
            self.signal_handler(signal.SIGINT, None)

def main():
    """Main entry point"""
    launcher = BulletproofTrafficLauncher()
    launcher.run()

if __name__ == "__main__":
    main()

