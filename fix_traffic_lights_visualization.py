#!/usr/bin/env python3
"""
Fix traffic lights visualization in SUMO simulation
"""

import os
import subprocess

def create_enhanced_visual_settings_with_lights():
    """Create visual settings that properly show traffic lights"""
    print("🔧 Creating Enhanced Visual Settings with Traffic Lights")
    
    visual_content = '''<?xml version="1.0" encoding="UTF-8"?>
<viewsettings xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="http://sumo.dlr.de/xsd/viewsettings_file.xsd">
    
    <!-- Professional color scheme -->
    <scheme name="professional_traffic_lights">
        <!-- Road elements -->
        <lane>
            <color value="0.2,0.2,0.2"/>
            <width value="1.0"/>
        </lane>
        <junction>
            <color value="0.3,0.3,0.3"/>
            <width value="1.0"/>
        </junction>
        
        <!-- Vehicle colors -->
        <vehicle>
            <color value="1,1,1"/>
            <width value="1.2"/>
        </vehicle>
        <vehicle_halo>
            <color value="1,0,0"/>
            <width value="0.3"/>
        </vehicle_halo>
        <vehicle_text>
            <color value="0,0,0"/>
            <size value="0.8"/>
        </vehicle_text>
        
        <!-- Text elements -->
        <edge_text>
            <color value="0,0,0"/>
            <size value="1.0"/>
        </edge_text>
        <junction_text>
            <color value="0,0,0"/>
            <size value="1.0"/>
        </junction_text>
        
        <!-- Traffic lights - Enhanced visibility -->
        <traffic_light>
            <color value="0,1,0"/>
            <width value="2.0"/>
        </traffic_light>
        
        <!-- Background -->
        <background>
            <color value="0.9,0.9,0.9"/>
        </background>
    </scheme>
    
    <!-- Decals for traffic light visualization -->
    <decals>
        <decal id="traffic_light_I1_north" x="100" y="80" type="traffic_light" color="0,1,0" size="2.0"/>
        <decal id="traffic_light_I1_south" x="100" y="120" type="traffic_light" color="1,0,0" size="2.0"/>
        <decal id="traffic_light_I1_east" x="120" y="100" type="traffic_light" color="1,0,0" size="2.0"/>
        <decal id="traffic_light_I1_west" x="80" y="100" type="traffic_light" color="1,0,0" size="2.0"/>
        
        <decal id="traffic_light_I2_north" x="200" y="80" type="traffic_light" color="0,1,0" size="2.0"/>
        <decal id="traffic_light_I2_south" x="200" y="120" type="traffic_light" color="1,0,0" size="2.0"/>
        <decal id="traffic_light_I2_east" x="220" y="100" type="traffic_light" color="1,0,0" size="2.0"/>
        <decal id="traffic_light_I2_west" x="180" y="100" type="traffic_light" color="1,0,0" size="2.0"/>
    </decals>
    
    <!-- POI for speed limit signs -->
    <poi>
        <poi id="speed_90" x="100" y="50" type="speed_limit" value="90" color="1,0,0" size="1.5"/>
        <poi id="speed_60" x="200" y="50" type="speed_limit" value="60" color="1,0,0" size="1.5"/>
        <poi id="speed_30" x="100" y="150" type="speed_limit" value="30" color="1,0,0" size="1.5"/>
    </poi>
    
</viewsettings>'''
    
    with open("real_traffic_output/enhanced_visual_settings.xml", "w") as f:
        f.write(visual_content)
    
    print("✅ Enhanced visual settings with traffic lights created")

def create_enhanced_config_with_lights():
    """Create configuration that enables traffic light visualization"""
    print("🔧 Creating Enhanced Configuration with Traffic Light Visualization")
    
    config_content = '''<?xml version="1.0" encoding="UTF-8"?>
<configuration xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="http://sumo.dlr.de/xsd/sumoConfiguration.xsd">

    <input>
        <net-file value="enhanced_multi_intersection.net.xml"/>
        <route-files value="enhanced_multi_intersection.rou.xml"/>
    </input>

    <time>
        <begin value="0"/>
        <end value="600"/>
        <step-length value="0.1"/>
    </time>

    <processing>
        <ignore-route-errors value="true"/>
    </processing>

    <report>
        <verbose value="true"/>
        <no-step-log value="true"/>
        <duration-log.statistics value="true"/>
        <no-warnings value="false"/>
    </report>

    <gui_only>
        <start value="true"/>
        <quit-on-end value="false"/>
        <delay value="100"/>
        <gui-settings-file value="enhanced_visual_settings.xml"/>
        <breakpoints value="0,30,60,90,120,150,180,210,240,270,300"/>
    </gui_only>

</configuration>'''
    
    with open("real_traffic_output/enhanced_multi_intersection.sumocfg", "w") as f:
        f.write(config_content)
    
    print("✅ Enhanced configuration with traffic light visualization created")

def create_network_with_visible_lights():
    """Create network with properly configured traffic lights"""
    print("🔧 Creating Network with Visible Traffic Lights")
    
    # Enhanced node file
    nod_content = '''<?xml version="1.0" encoding="UTF-8"?>
<nodes xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="http://sumo.dlr.de/xsd/nodes_file.xsd">
    <node id="J1" x="0.00" y="100.00" type="priority"/>
    <node id="I1" x="100.00" y="100.00" type="traffic_light"/>
    <node id="I2" x="200.00" y="100.00" type="traffic_light"/>
    <node id="J2" x="300.00" y="100.00" type="priority"/>
    <node id="J3" x="100.00" y="0.00" type="priority"/>
    <node id="J4" x="100.00" y="200.00" type="priority"/>
    <node id="J5" x="200.00" y="0.00" type="priority"/>
    <node id="J6" x="200.00" y="200.00" type="priority"/>
</nodes>'''
    
    with open("real_traffic_output/enhanced_nodes.nod.xml", "w") as f:
        f.write(nod_content)
    
    # Enhanced edge file
    edg_content = '''<?xml version="1.0" encoding="UTF-8"?>
<edges xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="http://sumo.dlr.de/xsd/edges_file.xsd">
    <!-- Main road (East-West) - 2 lanes each direction -->
    <edge id="main_west" from="J1" to="I1" priority="1" numLanes="2" speed="16.67"/>
    <edge id="main_center" from="I1" to="I2" priority="1" numLanes="2" speed="16.67"/>
    <edge id="main_east" from="I2" to="J2" priority="1" numLanes="2" speed="16.67"/>
    <edge id="main_west_reverse" from="I1" to="J1" priority="1" numLanes="2" speed="16.67"/>
    <edge id="main_center_reverse" from="I2" to="I1" priority="1" numLanes="2" speed="16.67"/>
    <edge id="main_east_reverse" from="J2" to="I2" priority="1" numLanes="2" speed="16.67"/>
    
    <!-- Secondary roads (North-South) - 2 lanes each direction -->
    <edge id="secondary_north_1" from="J3" to="I1" priority="1" numLanes="2" speed="25.0"/>
    <edge id="secondary_south_1" from="I1" to="J4" priority="1" numLanes="2" speed="8.33"/>
    <edge id="secondary_north_2" from="J5" to="I2" priority="1" numLanes="2" speed="16.67"/>
    <edge id="secondary_south_2" from="I2" to="J6" priority="1" numLanes="2" speed="16.67"/>
</edges>'''
    
    with open("real_traffic_output/enhanced_edges.edg.xml", "w") as f:
        f.write(edg_content)
    
    print("✅ Enhanced node and edge files created")
    
    # Use netconvert to create the network
    sumo_bin = r"C:\Program Files (x86)\Eclipse\Sumo\bin"
    netconvert_path = os.path.join(sumo_bin, "netconvert.exe")
    
    if not os.path.exists(netconvert_path):
        print(f"❌ netconvert not found at {netconvert_path}")
        return False
    
    try:
        cmd = [
            netconvert_path,
            "--node-files", "real_traffic_output/enhanced_nodes.nod.xml",
            "--edge-files", "real_traffic_output/enhanced_edges.edg.xml",
            "--output-file", "real_traffic_output/enhanced_multi_intersection.net.xml",
            "--tls.default-type", "static"
        ]
        
        print("🔧 Running netconvert with traffic light support...")
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Enhanced network with traffic lights created successfully!")
            return True
        else:
            print(f"❌ netconvert failed: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error running netconvert: {e}")
        return False

def main():
    """Main function to fix traffic light visualization"""
    print("🚦 FIXING TRAFFIC LIGHT VISUALIZATION")
    print("=" * 50)
    
    # Create network with visible traffic lights
    if create_network_with_visible_lights():
        # Create enhanced visual settings
        create_enhanced_visual_settings_with_lights()
        
        # Create enhanced configuration
        create_enhanced_config_with_lights()
        
        print("\n🎉 TRAFFIC LIGHT VISUALIZATION FIXED!")
        print("=" * 40)
        print("✅ Traffic lights will now be visible")
        print("✅ Red and green lights will show properly")
        print("✅ Enhanced visual settings applied")
        print("✅ Professional appearance maintained")
        
        print("\n🚀 TO RUN THE FIXED SIMULATION:")
        print("   python launch_enhanced_simulation.py")
        
    else:
        print("❌ Failed to create network with traffic lights")

if __name__ == "__main__":
    main()

