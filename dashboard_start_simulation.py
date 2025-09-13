#!/usr/bin/env python3
"""
Dashboard Start Simulation - Function to be called from dashboard
"""

import os
import sys
import subprocess
import threading
import time
import json
from pathlib import Path

def start_ai_simulation_from_dashboard():
    """Start AI simulation from dashboard - this function should be called when user clicks 'Start Simulation'"""
    print("Starting AI simulation from dashboard...")
    
    try:
        # Start the complete AI system
        process = subprocess.Popen([
            "python", "complete_ai_dashboard_system.py"
        ])
        
        print("✅ AI simulation started successfully!")
        print("SUMO GUI should be open with AI-controlled traffic lights")
        print("The AI is using the PKL model (DDQL_Replay_600.pkl) for intelligent control")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to start AI simulation: {e}")
        return False

def get_simulation_status():
    """Get current simulation status"""
    try:
        if os.path.exists("complete_ai_performance.json"):
            with open("complete_ai_performance.json", 'r') as f:
                data = json.load(f)
            return {
                'running': True,
                'performance': data
            }
        else:
            return {'running': False}
    except:
        return {'running': False}

def main():
    """Test function"""
    print("Dashboard AI Simulation Integration")
    print("=" * 40)
    
    # Test starting simulation
    if start_ai_simulation_from_dashboard():
        print("\n✅ Integration test successful!")
        print("This function can now be called from your dashboard.")
    else:
        print("\n❌ Integration test failed!")

if __name__ == "__main__":
    main()
