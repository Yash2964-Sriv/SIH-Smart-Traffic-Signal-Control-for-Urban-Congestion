#!/usr/bin/env python3
"""
Test AI Simulation - Verify all components work correctly
"""

import os
import sys
import subprocess
import time
from pathlib import Path

def test_files_exist():
    """Test that all required files exist"""
    print("Testing file existence...")
    
    required_files = [
        "fixed_ai_simulation.sumocfg",
        "real_traffic_output/visible_traffic_lights.net.xml",
        "real_traffic_output/enhanced_multi_intersection.rou.xml",
        "ai_traffic_controller.py",
        "master_ai_rl_trainer.py",
        "launch_ai_simulation.bat"
    ]
    
    missing_files = []
    for file_path in required_files:
        if not os.path.exists(file_path):
            missing_files.append(file_path)
    
    if missing_files:
        print(f"Missing files: {missing_files}")
        return False
    else:
        print("All required files exist!")
        return True

def test_sumo_config():
    """Test SUMO configuration"""
    print("Testing SUMO configuration...")
    
    try:
        # Test if SUMO can validate the configuration
        result = subprocess.run([
            "sumo", "-c", "fixed_ai_simulation.sumocfg", 
            "--no-step-log", "--quit-on-end"
        ], capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            print("SUMO configuration is valid!")
            return True
        else:
            print(f"SUMO configuration error: {result.stderr}")
            return False
    except subprocess.TimeoutExpired:
        print("SUMO configuration test timed out")
        return False
    except FileNotFoundError:
        print("SUMO not found in PATH")
        return False
    except Exception as e:
        print(f"Error testing SUMO configuration: {e}")
        return False

def test_python_imports():
    """Test Python imports"""
    print("Testing Python imports...")
    
    try:
        import numpy as np
        import json
        import time
        from datetime import datetime
        print("Basic imports successful!")
        return True
    except ImportError as e:
        print(f"Import error: {e}")
        return False

def main():
    """Main test function"""
    print("AI Simulation Test Suite")
    print("=" * 30)
    
    tests = [
        ("File Existence", test_files_exist),
        ("Python Imports", test_python_imports),
        ("SUMO Configuration", test_sumo_config)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        if test_func():
            passed += 1
            print(f"PASSED")
        else:
            print(f"FAILED")
    
    print(f"\nTest Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("\nAll tests passed! The AI simulation should work correctly.")
        print("\nTo run the simulation:")
        print("1. Double-click 'launch_ai_simulation.bat'")
        print("2. Or run: python ai_traffic_controller.py")
    else:
        print(f"\n{total - passed} tests failed. Please fix the issues before running the simulation.")

if __name__ == "__main__":
    main()
