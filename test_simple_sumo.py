#!/usr/bin/env python3
"""
Test Simple SUMO
Creates the simplest possible SUMO network to test if SUMO works at all
"""

import os
import subprocess

def test_simple_sumo():
    """Test with the simplest possible SUMO setup"""
    print("🧪 Testing Simple SUMO")
    print("=" * 50)
    
    # Create the simplest possible network
    print("📝 Creating ultra-simple network...")
    simple_network = """<?xml version="1.0" encoding="UTF-8"?>
<net version="1.9" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="http://sumo.dlr.de/xsd/net_file.xsd">
    <location netOffset="0.00,0.00" convBoundary="0.00,0.00,100.00,100.00" origBoundary="-10000000000.00,-10000000000.00,10000000000.00,10000000000.00" projParameter="!"/>
    
    <junction id="A" type="priority" x="0.00" y="0.00" incLanes="" intLanes="" shape="0.00,0.00 0.00,0.00"/>
    <junction id="B" type="priority" x="100.00" y="0.00" incLanes="" intLanes="" shape="100.00,0.00 100.00,0.00"/>
    
    <edge id="A2B" from="A" to="B" priority="1">
        <lane id="A2B_0" index="0" speed="13.89" length="100.00" shape="0.00,0.00 100.00,0.00"/>
    </edge>
</net>"""
    
    with open("test_simple.net.xml", 'w') as f:
        f.write(simple_network)
    print("✅ Created: test_simple.net.xml")
    
    # Create simple routes
    simple_routes = """<?xml version="1.0" encoding="UTF-8"?>
<routes xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="http://sumo.dlr.de/xsd/routes_file.xsd">
    <vType id="car" accel="2.0" decel="4.5" sigma="0.5" length="4.3" width="1.8" maxSpeed="50" guiShape="passenger" guiColor="0,0,1" minGap="2.5" tau="1.0"/>
    <route id="route1" edges="A2B"/>
    <flow id="flow1" route="route1" type="car" begin="0" end="100" period="5.0" departLane="0" departSpeed="10.0"/>
</routes>"""
    
    with open("test_simple.rou.xml", 'w') as f:
        f.write(simple_routes)
    print("✅ Created: test_simple.rou.xml")
    
    # Create simple config
    simple_config = """<?xml version="1.0" encoding="UTF-8"?>
<configuration xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="http://sumo.dlr.de/xsd/sumoConfiguration.xsd">
    <input>
        <net-file value="test_simple.net.xml"/>
        <route-files value="test_simple.rou.xml"/>
    </input>
    <time>
        <begin value="0"/>
        <end value="100"/>
        <step-length value="0.1"/>
    </time>
    <gui_only>
        <start value="true"/>
    </gui_only>
</configuration>"""
    
    with open("test_simple.sumocfg", 'w') as f:
        f.write(simple_config)
    print("✅ Created: test_simple.sumocfg")
    
    # Try to launch SUMO
    print("\n🚦 Testing SUMO GUI...")
    try:
        sumo_path = get_sumo_path()
        sumo_binary = os.path.join(sumo_path, "bin", "sumo-gui.exe")
        
        if not os.path.exists(sumo_binary):
            print(f"❌ SUMO binary not found: {sumo_binary}")
            return False
        
        # Launch SUMO GUI
        sumo_cmd = [sumo_binary, "-c", "test_simple.sumocfg"]
        
        print(f"Running: {' '.join(sumo_cmd)}")
        print("This should open SUMO GUI with a simple road...")
        
        # Start SUMO GUI process
        process = subprocess.Popen(sumo_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Wait a moment
        import time
        time.sleep(3)
        
        # Check if it's running
        if process.poll() is None:
            print("✅ SUMO GUI launched successfully!")
            print("You should see a SUMO window with a simple road")
            return True
        else:
            print("❌ SUMO GUI failed to start")
            stdout, stderr = process.communicate()
            if stderr:
                print(f"Error: {stderr.decode()}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def get_sumo_path():
    """Get SUMO installation path"""
    if 'SUMO_HOME' in os.environ:
        return os.environ['SUMO_HOME']
    
    possible_paths = [
        r"C:\Program Files (x86)\Eclipse\Sumo",
        r"C:\Program Files\Eclipse\Sumo",
        r"C:\sumo",
        r"C:\sumo-1.24.0"
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            return path
    
    raise Exception("SUMO not found. Please set SUMO_HOME environment variable.")

if __name__ == "__main__":
    test_simple_sumo()
