#!/usr/bin/env python3
"""
Create Simple Working SUMO Network
Creates a working SUMO network using a simple, proven approach
"""

import os
import subprocess
import sys

def create_simple_working_network():
    """Create a simple working SUMO network"""
    print("🔧 Creating Simple Working SUMO Network")
    print("=" * 50)
    
    # Create a very simple network XML that we know works
    print("📝 Creating simple network...")
    network_content = """<?xml version="1.0" encoding="UTF-8"?>
<net version="1.9" junctionCornerDetail="5" limitTurnSpeed="5.5" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="http://sumo.dlr.de/xsd/net_file.xsd">
    <location netOffset="0.00,0.00" convBoundary="0.00,0.00,200.00,200.00" origBoundary="-10000000000.00,-10000000000.00,10000000000.00,10000000000.00" projParameter="!"/>
    
    <!-- Nodes -->
    <junction id="north" type="priority" x="100.00" y="150.00" incLanes="" intLanes="" shape="100.00,150.00 100.00,150.00"/>
    <junction id="south" type="priority" x="100.00" y="50.00" incLanes="" intLanes="" shape="100.00,50.00 100.00,50.00"/>
    <junction id="east" type="priority" x="150.00" y="100.00" incLanes="" intLanes="" shape="150.00,100.00 150.00,100.00"/>
    <junction id="west" type="priority" x="50.00" y="100.00" incLanes="" intLanes="" shape="50.00,100.00 50.00,100.00"/>
    <junction id="center" type="traffic_light" x="100.00" y="100.00" incLanes="north2center_0 north2center_1 north2center_2 east2center_0 east2center_1 east2center_2 south2center_0 south2center_1 south2center_2 west2center_0 west2center_1 west2center_2" intLanes="" shape="100.00,90.00 110.00,100.00 100.00,110.00 90.00,100.00">
        <request index="0" response="00" foes="00" cont="0"/>
        <request index="1" response="00" foes="00" cont="0"/>
        <request index="2" response="00" foes="00" cont="0"/>
        <request index="3" response="00" foes="00" cont="0"/>
        <request index="4" response="00" foes="00" cont="0"/>
        <request index="5" response="00" foes="00" cont="0"/>
        <request index="6" response="00" foes="00" cont="0"/>
        <request index="7" response="00" foes="00" cont="0"/>
        <request index="8" response="00" foes="00" cont="0"/>
        <request index="9" response="00" foes="00" cont="0"/>
        <request index="10" response="00" foes="00" cont="0"/>
        <request index="11" response="00" foes="00" cont="0"/>
    </junction>
    
    <!-- Edges -->
    <edge id="north2center" from="north" to="center" priority="1">
        <lane id="north2center_0" index="0" speed="13.89" length="50.00" shape="100.00,150.00 100.00,100.00"/>
        <lane id="north2center_1" index="1" speed="13.89" length="50.00" shape="105.00,150.00 105.00,100.00"/>
        <lane id="north2center_2" index="2" speed="13.89" length="50.00" shape="110.00,150.00 110.00,100.00"/>
    </edge>
    
    <edge id="center2south" from="center" to="south" priority="1">
        <lane id="center2south_0" index="0" speed="13.89" length="50.00" shape="100.00,100.00 100.00,50.00"/>
        <lane id="center2south_1" index="1" speed="13.89" length="50.00" shape="105.00,100.00 105.00,50.00"/>
        <lane id="center2south_2" index="2" speed="13.89" length="50.00" shape="110.00,100.00 110.00,50.00"/>
    </edge>
    
    <edge id="east2center" from="east" to="center" priority="1">
        <lane id="east2center_0" index="0" speed="13.89" length="50.00" shape="150.00,100.00 100.00,100.00"/>
        <lane id="east2center_1" index="1" speed="13.89" length="50.00" shape="150.00,105.00 100.00,105.00"/>
        <lane id="east2center_2" index="2" speed="13.89" length="50.00" shape="150.00,110.00 100.00,110.00"/>
    </edge>
    
    <edge id="center2west" from="center" to="west" priority="1">
        <lane id="center2west_0" index="0" speed="13.89" length="50.00" shape="100.00,100.00 50.00,100.00"/>
        <lane id="center2west_1" index="1" speed="13.89" length="50.00" shape="100.00,105.00 50.00,105.00"/>
        <lane id="center2west_2" index="2" speed="13.89" length="50.00" shape="100.00,110.00 50.00,110.00"/>
    </edge>
    
    <edge id="south2center" from="south" to="center" priority="1">
        <lane id="south2center_0" index="0" speed="13.89" length="50.00" shape="100.00,50.00 100.00,100.00"/>
        <lane id="south2center_1" index="1" speed="13.89" length="50.00" shape="95.00,50.00 95.00,100.00"/>
        <lane id="south2center_2" index="2" speed="13.89" length="50.00" shape="90.00,50.00 90.00,100.00"/>
    </edge>
    
    <edge id="center2north" from="center" to="north" priority="1">
        <lane id="center2north_0" index="0" speed="13.89" length="50.00" shape="100.00,100.00 100.00,150.00"/>
        <lane id="center2north_1" index="1" speed="13.89" length="50.00" shape="95.00,100.00 95.00,150.00"/>
        <lane id="center2north_2" index="2" speed="13.89" length="50.00" shape="90.00,100.00 90.00,150.00"/>
    </edge>
    
    <edge id="west2center" from="west" to="center" priority="1">
        <lane id="west2center_0" index="0" speed="13.89" length="50.00" shape="50.00,100.00 100.00,100.00"/>
        <lane id="west2center_1" index="1" speed="13.89" length="50.00" shape="50.00,95.00 100.00,95.00"/>
        <lane id="west2center_2" index="2" speed="13.89" length="50.00" shape="50.00,90.00 100.00,90.00"/>
    </edge>
    
    <edge id="center2east" from="center" to="east" priority="1">
        <lane id="center2east_0" index="0" speed="13.89" length="50.00" shape="100.00,100.00 150.00,100.00"/>
        <lane id="center2east_1" index="1" speed="13.89" length="50.00" shape="100.00,95.00 150.00,95.00"/>
        <lane id="center2east_2" index="2" speed="13.89" length="50.00" shape="100.00,90.00 150.00,90.00"/>
    </edge>
    
    <!-- Connections -->
    <connection from="north2center" to="center2south" fromLane="0" toLane="0" state="M"/>
    <connection from="north2center" to="center2east" fromLane="1" toLane="0" state="M"/>
    <connection from="north2center" to="center2west" fromLane="2" toLane="0" state="M"/>
    
    <connection from="east2center" to="center2west" fromLane="0" toLane="0" state="M"/>
    <connection from="east2center" to="center2north" fromLane="1" toLane="0" state="M"/>
    <connection from="east2center" to="center2south" fromLane="2" toLane="0" state="M"/>
    
    <connection from="south2center" to="center2north" fromLane="0" toLane="0" state="M"/>
    <connection from="south2center" to="center2east" fromLane="1" toLane="0" state="M"/>
    <connection from="south2center" to="center2west" fromLane="2" toLane="0" state="M"/>
    
    <connection from="west2center" to="center2east" fromLane="0" toLane="0" state="M"/>
    <connection from="west2center" to="center2north" fromLane="1" toLane="0" state="M"/>
    <connection from="west2center" to="center2south" fromLane="2" toLane="0" state="M"/>
</net>"""
    
    with open("simple_network.net.xml", 'w') as f:
        f.write(network_content)
    print("✅ Created: simple_network.net.xml")
    
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
    
    with open("simple_routes.rou.xml", 'w') as f:
        f.write(routes_content)
    print("✅ Created: simple_routes.rou.xml")
    
    # Create config
    print("📝 Creating configuration...")
    config_content = """<?xml version="1.0" encoding="UTF-8"?>
<configuration xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="http://sumo.dlr.de/xsd/sumoConfiguration.xsd">
    <input>
        <net-file value="simple_network.net.xml"/>
        <route-files value="simple_routes.rou.xml"/>
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
    
    with open("simple_config.sumocfg", 'w') as f:
        f.write(config_content)
    print("✅ Created: simple_config.sumocfg")
    
    print("\n🎉 Simple working SUMO network created successfully!")
    print("Files created:")
    print("  - simple_network.net.xml")
    print("  - simple_routes.rou.xml")
    print("  - simple_config.sumocfg")
    
    return True

if __name__ == "__main__":
    create_simple_working_network()
