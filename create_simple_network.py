#!/usr/bin/env python3
"""
Create a simple working network using SUMO tools
"""

import os
import subprocess
import sys

def create_simple_network():
    """Create a simple working network"""
    print("🔧 Creating Simple Working Network")
    print("=" * 40)
    
    # Check if SUMO is available
    sumo_paths = [
        r"C:\Program Files (x86)\Eclipse\Sumo\bin",
        r"C:\Program Files\Eclipse\Sumo\bin"
    ]
    
    sumo_bin = None
    for path in sumo_paths:
        if os.path.exists(path):
            sumo_bin = path
            break
    
    if not sumo_bin:
        print("❌ SUMO not found!")
        return False
    
    print(f"✅ SUMO found: {sumo_bin}")
    
    # Create a simple .nod.xml file
    nod_content = '''<?xml version="1.0" encoding="UTF-8"?>
<nodes xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="http://sumo.dlr.de/xsd/nodes_file.xsd">
    <node id="J1" x="0.00" y="85.00" type="priority"/>
    <node id="I1" x="100.00" y="100.00" type="traffic_light"/>
    <node id="I2" x="200.00" y="100.00" type="traffic_light"/>
    <node id="J2" x="300.00" y="85.00" type="priority"/>
    <node id="J3" x="95.00" y="0.00" type="priority"/>
    <node id="J4" x="95.00" y="200.00" type="priority"/>
    <node id="J5" x="200.00" y="0.00" type="priority"/>
    <node id="J6" x="200.00" y="200.00" type="priority"/>
</nodes>'''
    
    with open("real_traffic_output/simple_nodes.nod.xml", "w") as f:
        f.write(nod_content)
    
    # Create a simple .edg.xml file
    edg_content = '''<?xml version="1.0" encoding="UTF-8"?>
<edges xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="http://sumo.dlr.de/xsd/edges_file.xsd">
    <edge id="main_west" from="J1" to="I1" priority="1" numLanes="2" speed="16.67"/>
    <edge id="main_center" from="I1" to="I2" priority="1" numLanes="2" speed="16.67"/>
    <edge id="main_east" from="I2" to="J2" priority="1" numLanes="2" speed="16.67"/>
    <edge id="main_west_reverse" from="I1" to="J1" priority="1" numLanes="2" speed="16.67"/>
    <edge id="main_center_reverse" from="I2" to="I1" priority="1" numLanes="2" speed="16.67"/>
    <edge id="main_east_reverse" from="J2" to="I2" priority="1" numLanes="2" speed="16.67"/>
    <edge id="secondary_north_1" from="J3" to="I1" priority="1" numLanes="2" speed="13.89"/>
    <edge id="secondary_south_1" from="I1" to="J4" priority="1" numLanes="2" speed="13.89"/>
    <edge id="secondary_north_2" from="J5" to="I2" priority="1" numLanes="1" speed="13.89"/>
    <edge id="secondary_south_2" from="I2" to="J6" priority="1" numLanes="1" speed="8.33"/>
</edges>'''
    
    with open("real_traffic_output/simple_edges.edg.xml", "w") as f:
        f.write(edg_content)
    
    print("✅ Created node and edge files")
    
    # Use netconvert to create the network
    netconvert_path = os.path.join(sumo_bin, "netconvert.exe")
    if not os.path.exists(netconvert_path):
        print(f"❌ netconvert not found at {netconvert_path}")
        return False
    
    try:
        cmd = [
            netconvert_path,
            "--node-files", "real_traffic_output/simple_nodes.nod.xml",
            "--edge-files", "real_traffic_output/simple_edges.edg.xml",
            "--output-file", "real_traffic_output/simple_multi_intersection.net.xml"
        ]
        
        print("🔧 Running netconvert...")
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Network created successfully!")
            return True
        else:
            print(f"❌ netconvert failed: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error running netconvert: {e}")
        return False

if __name__ == "__main__":
    create_simple_network()

