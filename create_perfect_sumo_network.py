#!/usr/bin/env python3
"""
Create Perfect SUMO Network
Creates a working SUMO network using the netconvert tool to ensure it's correct
"""

import os
import subprocess
import sys

def create_perfect_network():
    """Create a perfect SUMO network using netconvert"""
    print("🔧 Creating Perfect SUMO Network")
    print("=" * 50)
    
    # First, let's create a simple .nod.xml file
    print("📝 Creating node file...")
    node_content = """<?xml version="1.0" encoding="UTF-8"?>
<nodes xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="http://sumo.dlr.de/xsd/nodes_file.xsd">
    <node id="north" x="100.00" y="150.00" type="priority"/>
    <node id="south" x="100.00" y="50.00" type="priority"/>
    <node id="east" x="150.00" y="100.00" type="priority"/>
    <node id="west" x="50.00" y="100.00" type="priority"/>
    <node id="center" x="100.00" y="100.00" type="traffic_light"/>
</nodes>"""
    
    with open("perfect_nodes.nod.xml", 'w') as f:
        f.write(node_content)
    print("✅ Created: perfect_nodes.nod.xml")
    
    # Create edge file
    print("📝 Creating edge file...")
    edge_content = """<?xml version="1.0" encoding="UTF-8"?>
<edges xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="http://sumo.dlr.de/xsd/edges_file.xsd">
    <edge id="north2center" from="north" to="center" priority="1" numLanes="3" speed="13.89"/>
    <edge id="center2south" from="center" to="south" priority="1" numLanes="3" speed="13.89"/>
    <edge id="east2center" from="east" to="center" priority="1" numLanes="3" speed="13.89"/>
    <edge id="center2west" from="center" to="west" priority="1" numLanes="3" speed="13.89"/>
    <edge id="south2center" from="south" to="center" priority="1" numLanes="3" speed="13.89"/>
    <edge id="center2north" from="center" to="north" priority="1" numLanes="3" speed="13.89"/>
    <edge id="west2center" from="west" to="center" priority="1" numLanes="3" speed="13.89"/>
    <edge id="center2east" from="center" to="east" priority="1" numLanes="3" speed="13.89"/>
</edges>"""
    
    with open("perfect_edges.edg.xml", 'w') as f:
        f.write(edge_content)
    print("✅ Created: perfect_edges.edg.xml")
    
    # Create connection file
    print("📝 Creating connection file...")
    connection_content = """<?xml version="1.0" encoding="UTF-8"?>
<connections xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="http://sumo.dlr.de/xsd/connections_file.xsd">
    <connection from="north2center" to="center2south" fromLane="0" toLane="0" dir="s" state="M"/>
    <connection from="north2center" to="center2east" fromLane="1" toLane="0" dir="r" state="M"/>
    <connection from="north2center" to="center2west" fromLane="2" toLane="0" dir="l" state="M"/>
    
    <connection from="east2center" to="center2west" fromLane="0" toLane="0" dir="s" state="M"/>
    <connection from="east2center" to="center2north" fromLane="1" toLane="0" dir="r" state="M"/>
    <connection from="east2center" to="center2south" fromLane="2" toLane="0" dir="l" state="M"/>
    
    <connection from="south2center" to="center2north" fromLane="0" toLane="0" dir="s" state="M"/>
    <connection from="south2center" to="center2east" fromLane="1" toLane="0" dir="r" state="M"/>
    <connection from="south2center" to="center2west" fromLane="2" toLane="0" dir="l" state="M"/>
    
    <connection from="west2center" to="center2east" fromLane="0" toLane="0" dir="s" state="M"/>
    <connection from="west2center" to="center2north" fromLane="1" toLane="0" dir="r" state="M"/>
    <connection from="west2center" to="center2south" fromLane="2" toLane="0" dir="l" state="M"/>
</connections>"""
    
    with open("perfect_connections.con.xml", 'w') as f:
        f.write(connection_content)
    print("✅ Created: perfect_connections.con.xml")
    
    # Now use netconvert to create the network
    print("🔧 Converting to SUMO network using netconvert...")
    
    try:
        # Get SUMO path
        sumo_path = get_sumo_path()
        netconvert_binary = os.path.join(sumo_path, "bin", "netconvert.exe")
        
        if not os.path.exists(netconvert_binary):
            print(f"❌ netconvert not found: {netconvert_binary}")
            return False
        
        # Run netconvert
        netconvert_cmd = [
            netconvert_binary,
            "--node-files", "perfect_nodes.nod.xml",
            "--edge-files", "perfect_edges.edg.xml", 
            "--connection-files", "perfect_connections.con.xml",
            "--output-file", "perfect_network.net.xml"
        ]
        
        print(f"Running: {' '.join(netconvert_cmd)}")
        result = subprocess.run(netconvert_cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Network created successfully: perfect_network.net.xml")
        else:
            print(f"❌ netconvert failed: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error running netconvert: {e}")
        return False
    
    # Create routes
    print("📝 Creating routes...")
    routes_content = """<?xml version="1.0" encoding="UTF-8"?>
<routes xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="http://sumo.dlr.de/xsd/routes_file.xsd">
    <vType id="car" accel="2.0" decel="4.5" sigma="0.5" length="4.3" width="1.8" maxSpeed="50" guiShape="passenger" guiColor="0,0,1" minGap="2.5" tau="1.0"/>
    <vType id="bus" accel="1.0" decel="4.0" sigma="0.5" length="12" width="2.5" maxSpeed="30" guiShape="bus" guiColor="1,0,0" minGap="3.0" tau="1.5"/>
    <vType id="truck" accel="0.8" decel="4.0" sigma="0.5" length="7.1" width="2.5" maxSpeed="25" guiShape="truck" guiColor="0.5,0.25,0" minGap="3.0" tau="1.5"/>
    
    <!-- Routes -->
    <route id="S_to_N" edges="south2center center2north"/>
    <route id="S_to_E" edges="south2center center2east"/>
    <route id="S_to_W" edges="south2center center2west"/>
    <route id="N_to_S" edges="north2center center2south"/>
    <route id="N_to_E" edges="north2center center2east"/>
    <route id="N_to_W" edges="north2center center2west"/>
    <route id="E_to_W" edges="east2center center2west"/>
    <route id="E_to_N" edges="east2center center2north"/>
    <route id="E_to_S" edges="east2center center2south"/>
    <route id="W_to_E" edges="west2center center2east"/>
    <route id="W_to_N" edges="west2center center2north"/>
    <route id="W_to_S" edges="west2center center2south"/>
    
    <!-- Traffic flows -->
    <flow id="S_through" route="S_to_N" type="car" begin="0" end="999999" period="3.0" departLane="1" departSpeed="8.0"/>
    <flow id="S_right" route="S_to_E" type="car" begin="0" end="999999" period="4.0" departLane="2" departSpeed="6.0"/>
    <flow id="S_left" route="S_to_W" type="car" begin="0" end="999999" period="5.0" departLane="0" departSpeed="5.0"/>
    
    <flow id="N_through" route="N_to_S" type="car" begin="0" end="999999" period="3.2" departLane="1" departSpeed="8.0"/>
    <flow id="N_right" route="N_to_W" type="car" begin="0" end="999999" period="4.2" departLane="2" departSpeed="6.0"/>
    <flow id="N_left" route="N_to_E" type="car" begin="0" end="999999" period="5.2" departLane="0" departSpeed="5.0"/>
    
    <flow id="E_through" route="E_to_W" type="car" begin="0" end="999999" period="2.8" departLane="1" departSpeed="8.0"/>
    <flow id="E_right" route="E_to_N" type="car" begin="0" end="999999" period="3.8" departLane="2" departSpeed="6.0"/>
    <flow id="E_left" route="E_to_S" type="car" begin="0" end="999999" period="4.8" departLane="0" departSpeed="5.0"/>
    
    <flow id="W_through" route="W_to_E" type="car" begin="0" end="999999" period="3.1" departLane="1" departSpeed="8.0"/>
    <flow id="W_right" route="W_to_S" type="car" begin="0" end="999999" period="4.1" departLane="2" departSpeed="6.0"/>
    <flow id="W_left" route="W_to_N" type="car" begin="0" end="999999" period="5.1" departLane="0" departSpeed="5.0"/>
    
    <!-- Add buses and trucks for realism -->
    <flow id="S_bus" route="S_to_N" type="bus" begin="0" end="999999" period="25.0" departLane="1" departSpeed="6.0"/>
    <flow id="N_truck" route="N_to_S" type="truck" begin="0" end="999999" period="20.0" departLane="1" departSpeed="5.0"/>
    <flow id="E_bus" route="E_to_W" type="bus" begin="0" end="999999" period="30.0" departLane="1" departSpeed="6.0"/>
    <flow id="W_truck" route="W_to_E" type="truck" begin="0" end="999999" period="22.0" departLane="1" departSpeed="5.0"/>
</routes>"""
    
    with open("perfect_routes.rou.xml", 'w') as f:
        f.write(routes_content)
    print("✅ Created: perfect_routes.rou.xml")
    
    # Create config
    print("📝 Creating configuration...")
    config_content = """<?xml version="1.0" encoding="UTF-8"?>
<configuration xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="http://sumo.dlr.de/xsd/sumoConfiguration.xsd">
    <input>
        <net-file value="perfect_network.net.xml"/>
        <route-files value="perfect_routes.rou.xml"/>
    </input>
    
    <time>
        <begin value="0"/>
        <end value="999999"/>
        <step-length value="0.1"/>
    </time>
    
    <processing>
        <ignore-route-errors value="true"/>
    </processing>
    
    <report>
        <verbose value="true"/>
        <duration-log.statistics value="true"/>
        <no-step-log value="true"/>
    </report>
    
    <gui_only>
        <start value="true"/>
    </gui_only>
</configuration>"""
    
    with open("perfect_config.sumocfg", 'w') as f:
        f.write(config_content)
    print("✅ Created: perfect_config.sumocfg")
    
    print("\n🎉 Perfect SUMO network created successfully!")
    print("Files created:")
    print("  - perfect_network.net.xml (generated by netconvert)")
    print("  - perfect_routes.rou.xml")
    print("  - perfect_config.sumocfg")
    print("  - perfect_nodes.nod.xml")
    print("  - perfect_edges.edg.xml")
    print("  - perfect_connections.con.xml")
    
    return True

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
    create_perfect_network()
