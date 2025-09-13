#!/usr/bin/env python3
"""
Test SUMO Launch - Verify Everything Works
"""

import os
import subprocess
import time

def test_sumo_launch():
    """Test SUMO launch and verify it works"""
    print("🧪 Testing SUMO Launch")
    print("=" * 30)
    
    # Change to correct directory
    output_dir = "real_traffic_output"
    if not os.path.exists(output_dir):
        print(f"❌ Error: Directory {output_dir} not found!")
        return False
    
    os.chdir(output_dir)
    print(f"📁 Working directory: {os.getcwd()}")
    
    # Check if files exist
    config_file = "professional_working_config.sumocfg"
    visual_file = "professional_visual_settings.xml"
    
    if not os.path.exists(config_file):
        print(f"❌ Error: Config file {config_file} not found!")
        return False
    
    if not os.path.exists(visual_file):
        print(f"❌ Error: Visual settings file {visual_file} not found!")
        return False
    
    print(f"✅ Config file found: {config_file}")
    print(f"✅ Visual settings found: {visual_file}")
    
    # Test command line version first
    print("\n🔄 Testing command line version...")
    sumo_path = r"C:\Program Files (x86)\Eclipse\Sumo\bin\sumo.exe"
    cmd_test = [sumo_path, "-c", config_file]
    
    try:
        result = subprocess.run(cmd_test, capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print("✅ Command line test PASSED")
        else:
            print(f"❌ Command line test FAILED: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Command line test ERROR: {e}")
        return False
    
    # Test GUI version
    print("\n🔄 Testing GUI version...")
    gui_path = r"C:\Program Files (x86)\Eclipse\Sumo\bin\sumo-gui.exe"
    cmd_gui = [gui_path, "-c", config_file, "--gui-settings-file", visual_file, "--delay", "500"]
    
    try:
        print(f"🚀 Launching: {' '.join(cmd_gui)}")
        process = subprocess.Popen(cmd_gui)
        print("✅ GUI launched successfully!")
        print("🎉 SUMO GUI should now be running!")
        return True
    except Exception as e:
        print(f"❌ GUI launch ERROR: {e}")
        return False

if __name__ == "__main__":
    print("🎯 SUMO Launch Test")
    print("=" * 20)
    
    if test_sumo_launch():
        print("\n🎉 SUCCESS! SUMO is working perfectly!")
        print("   Look for the SUMO GUI window with professional graphics!")
    else:
        print("\n❌ FAILED! There are still issues to resolve.")
