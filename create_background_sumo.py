#!/usr/bin/env python3
"""
Create SUMO Simulation with Background Image
Alternative method to achieve professional look
"""

import os
import subprocess

def create_background_network():
    """Create configuration with background image support"""
    print("🖼️ Creating SUMO configuration with background image support...")
    
    # First, let's create a simple but professional network
    net_content = '''<?xml version="1.0" encoding="UTF-8"?>
<net version="1.9" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="http://sumo.dlr.de/xsd/net_file.xsd">
    <location netOffset="0.00,0.00" convBoundary="0.00,0.00,400.00,400.00" origBoundary="-180.00,-90.00,180.00,90.00" projParameter="+proj=longlat +ellps=WGS84 +datum=WGS84 +no_defs"/>
    
    <!-- Professional Junction definitions -->
    <junction id="center" type="traffic_light" x="200.0" y="200.0" incLanes="" intLanes="" shape="190.0,190.0 210.0,190.0 210.0,210.0 190.0,210.0">
        <request index="0" response="00" foes="00" cont="0"/>
    </junction>
    
    <junction id="north_end" type="priority" x="200.0" y="0.0" incLanes="" intLanes="" shape="190.0,-10.0 210.0,-10.0 210.0,10.0 190.0,10.0">
        <request index="0" response="00" foes="00" cont="0"/>
    </junction>
    
    <junction id="south_end" type="priority" x="200.0" y="400.0" incLanes="" intLanes="" shape="190.0,390.0 210.0,390.0 210.0,410.0 190.0,410.0">
        <request index="0" response="00" foes="00" cont="0"/>
    </junction>
    
    <junction id="east_end" type="priority" x="400.0" y="200.0" incLanes="" intLanes="" shape="390.0,190.0 410.0,190.0 410.0,210.0 390.0,210.0">
        <request index="0" response="00" foes="00" cont="0"/>
    </junction>
    
    <junction id="west_end" type="priority" x="0.0" y="200.0" incLanes="" intLanes="" shape="-10.0,190.0 10.0,190.0 10.0,210.0 -10.0,210.0">
        <request index="0" response="00" foes="00" cont="0"/>
    </junction>
    
    <!-- Multi-lane Edge definitions -->
    <edge id="north" from="north_end" to="center" priority="1">
        <lane id="north_0" index="0" speed="13.89" length="200.0" shape="195.0,0.0 195.0,200.0"/>
        <lane id="north_1" index="1" speed="13.89" length="200.0" shape="205.0,0.0 205.0,200.0"/>
    </edge>
    
    <edge id="south" from="south_end" to="center" priority="1">
        <lane id="south_0" index="0" speed="13.89" length="200.0" shape="195.0,400.0 195.0,200.0"/>
        <lane id="south_1" index="1" speed="13.89" length="200.0" shape="205.0,400.0 205.0,200.0"/>
    </edge>
    
    <edge id="east" from="east_end" to="center" priority="1">
        <lane id="east_0" index="0" speed="13.89" length="200.0" shape="400.0,195.0 200.0,195.0"/>
        <lane id="east_1" index="1" speed="13.89" length="200.0" shape="400.0,205.0 200.0,205.0"/>
    </edge>
    
    <edge id="west" from="west_end" to="center" priority="1">
        <lane id="west_0" index="0" speed="13.89" length="200.0" shape="0.0,195.0 200.0,195.0"/>
        <lane id="west_1" index="1" speed="13.89" length="200.0" shape="0.0,205.0 200.0,205.0"/>
    </edge>
    
    <!-- Professional Traffic Light Logic -->
    <tlLogic id="center" type="static" programID="0" offset="0">
        <phase duration="45" state="GGGrrrGGGrrr"/>
        <phase duration="5" state="yyyrrryyyrrr"/>
        <phase duration="45" state="rrrGGGrrrGGG"/>
        <phase duration="5" state="rrryyyrrryyy"/>
        <phase duration="45" state="rrrrrrGGGrrr"/>
        <phase duration="5" state="rrrrrryyyrrr"/>
        <phase duration="45" state="rrrrrrrrrGGG"/>
        <phase duration="5" state="rrrrrrrrryyy"/>
    </tlLogic>
</net>'''
    
    net_file = "real_traffic_output/background_network.net.xml"
    with open(net_file, 'w') as f:
        f.write(net_content)
    
    print(f"✅ Created background network: {net_file}")
    return net_file

def create_background_routes():
    """Create routes for background simulation"""
    routes_content = '''<?xml version="1.0" encoding="UTF-8"?>
<routes xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="http://sumo.dlr.de/xsd/routes_file.xsd">
    
    <!-- Professional Vehicle Types -->
    <vType id="car" accel="2.6" decel="4.5" sigma="0.5" length="4.3" maxSpeed="50" guiShape="passenger" color="1,0,0" width="1.8" height="1.5" minGap="2.5"/>
    <vType id="truck" accel="1.2" decel="3.5" sigma="0.3" length="12" maxSpeed="30" guiShape="truck" color="0,0,1" width="2.5" height="3.5" minGap="3.0"/>
    <vType id="bus" accel="1.0" decel="3.0" sigma="0.2" length="15" maxSpeed="25" guiShape="bus" color="0,1,0" width="2.5" height="3.5" minGap="4.0"/>
    <vType id="motorcycle" accel="3.0" decel="6.0" sigma="0.8" length="2" maxSpeed="60" guiShape="motorcycle" color="1,1,0" width="1.0" height="1.2" minGap="1.0"/>
    <vType id="taxi" accel="2.8" decel="4.5" sigma="0.6" length="4.5" maxSpeed="45" guiShape="taxi" color="1,0.5,0" width="1.8" height="1.5" minGap="2.0"/>
    <vType id="emergency" accel="3.5" decel="5.0" sigma="0.1" length="5.0" maxSpeed="70" guiShape="emergency" color="1,0,1" width="2.0" height="2.0" minGap="1.5"/>
    
    <!-- Professional traffic flows -->
    <flow id="flow_cars" type="car" begin="0" end="150" period="2" color="1,0,0"/>
    <flow id="flow_trucks" type="truck" begin="5" end="150" period="10" color="0,0,1"/>
    <flow id="flow_buses" type="bus" begin="10" end="150" period="15" color="0,1,0"/>
    <flow id="flow_motorcycles" type="motorcycle" begin="2" end="150" period="5" color="1,1,0"/>
    <flow id="flow_taxis" type="taxi" begin="3" end="150" period="3" color="1,0.5,0"/>
    <flow id="flow_emergency" type="emergency" begin="30" end="150" period="50" color="1,0,1"/>
    
</routes>'''
    
    routes_file = "real_traffic_output/background_routes.rou.xml"
    with open(routes_file, 'w') as f:
        f.write(routes_content)
    
    print(f"✅ Created background routes: {routes_file}")
    return routes_file

def create_background_config(net_file, routes_file):
    """Create configuration with background image support"""
    config_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<configuration xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="http://sumo.dlr.de/xsd/sumoConfiguration.xsd">
    <input>
        <net-file value="{os.path.basename(net_file)}"/>
        <route-files value="{os.path.basename(routes_file)}"/>
    </input>
    <time>
        <begin value="0"/>
        <end value="150"/>
        <step-length value="0.1"/>
    </time>
    <processing>
        <ignore-route-errors value="1"/>
        <ignore-junction-blocker value="1"/>
    </processing>
    <report>
        <verbose value="1"/>
        <no-step-log value="0"/>
    </report>
    <gui_only>
        <start value="1"/>
        <quit-on-end value="0"/>
        <delay value="500"/>
    </gui_only>
    <output>
        <fcd-output value="background_fcd.xml"/>
        <netstate-dump value="background_netstate.xml"/>
    </output>
</configuration>'''
    
    config_file = "real_traffic_output/background_config.sumocfg"
    with open(config_file, 'w') as f:
        f.write(config_content)
    
    print(f"✅ Created background configuration: {config_file}")
    return config_file

def create_enhanced_visual_settings():
    """Create enhanced visual settings for professional look"""
    visual_settings = '''<viewsettings>
    <scheme name="real world"/>
    <delay value="500"/>
    <zoom value="1500"/>
    <viewport x="0" y="0"/>
    
    <vehicles>
        <default value="true" showType="true" showRoute="false" showSignals="true" showBlinker="true" showSpeed="false" showLane="false" showColor="true"/>
        <shape value="true"/>
        <minSize value="3"/>
        <maxSize value="300"/>
        <color value="byType"/>
        <scale value="1.5"/>
    </vehicles>
    
    <junctions>
        <default value="true" showShape="true" showTrafficLights="true" showName="false"/>
        <color value="byType"/>
    </junctions>
    
    <edges>
        <default value="true" showShape="true" showName="false" showLanes="true" showSignals="true"/>
        <width value="10"/>
        <color value="bySpeed"/>
    </edges>
    
    <lanes>
        <default value="true" showShape="true" showName="false" showSignals="true"/>
        <width value="8"/>
        <color value="bySpeed"/>
    </lanes>
    
    <pois>
        <default value="true" showShape="true" showName="false"/>
    </pois>
    
    <polygons>
        <default value="true" showShape="true" showName="false"/>
    </polygons>
    
    <gui_only>
        <scale value="2.0"/>
        <lighting value="true"/>
        <shadows value="true"/>
        <textures value="true"/>
        <background value="white"/>
        <antialiase value="true"/>
    </gui_only>
</viewsettings>'''
    
    visual_file = "real_traffic_output/enhanced_visual_settings.xml"
    with open(visual_file, 'w') as f:
        f.write(visual_settings)
    
    print(f"✅ Created enhanced visual settings: {visual_file}")
    return visual_file

def launch_background_sumo(config_file, visual_file):
    """Launch SUMO with background support"""
    print("🚀 Launching enhanced SUMO simulation...")
    
    sumo_path = r"C:\Program Files (x86)\Eclipse\Sumo\bin\sumo-gui.exe"
    
    cmd = [
        sumo_path,
        "-c", config_file,
        "--gui-settings-file", visual_file,
        "--delay", "500"
    ]
    
    print(f"Running: {' '.join(cmd)}")
    
    try:
        subprocess.Popen(cmd, cwd="real_traffic_output")
        print("✅ Enhanced SUMO launched successfully!")
        return True
    except Exception as e:
        print(f"❌ Error launching SUMO: {e}")
        return False

if __name__ == "__main__":
    print("🖼️ Creating Enhanced SUMO Simulation")
    print("=" * 40)
    print("🎯 Alternative method for professional look")
    print("=" * 40)
    
    # Create background network
    net_file = create_background_network()
    
    # Create routes
    routes_file = create_background_routes()
    
    # Create configuration
    config_file = create_background_config(net_file, routes_file)
    
    # Create enhanced visual settings
    visual_file = create_enhanced_visual_settings()
    
    # Launch enhanced SUMO
    if launch_background_sumo(config_file, visual_file):
        print("\n🎉 SUCCESS! Enhanced SUMO simulation launched!")
        print("=" * 50)
        print("🎯 This should look much more professional!")
        print("   • Enhanced visual settings")
        print("   • Professional vehicle graphics")
        print("   • Multi-lane roads")
        print("   • High-quality rendering")
    else:
        print("❌ Failed to launch enhanced SUMO")
