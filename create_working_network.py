#!/usr/bin/env python3
"""
Create Working SUMO Network
Creates a proper SUMO network that works with TraCI
"""

def create_working_network():
    """Create a working SUMO network"""
    network_xml = """<?xml version="1.0" encoding="UTF-8"?>
<net version="1.9" junctionCornerDetail="5" limitTurnSpeed="5.5" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="http://sumo.dlr.de/xsd/net_file.xsd">
    <location netOffset="0.00,0.00" convBoundary="0.00,0.00,200.00,200.00" origBoundary="-10000000000.00,-10000000000.00,10000000000.00,10000000000.00" projParameter="!"/>
    
    <!-- Nodes -->
    <junction id="I1" type="traffic_light" x="100.00" y="100.00" incLanes="E1_0 W1_0 N1_0 S1_0" intLanes="" shape="100.00,90.00 110.00,100.00 100.00,110.00 90.00,100.00">
        <request index="0" response="00" foes="00" cont="0"/>
        <request index="1" response="00" foes="00" cont="0"/>
        <request index="2" response="00" foes="00" cont="0"/>
        <request index="3" response="00" foes="00" cont="0"/>
    </junction>
    
    <!-- Edges -->
    <edge id="E1" from="I1" to="I1" priority="1">
        <lane id="E1_0" index="0" speed="15.0" length="120.00" shape="220.00,100.00 100.00,100.00"/>
    </edge>
    <edge id="W1" from="I1" to="I1" priority="1">
        <lane id="W1_0" index="0" speed="15.0" length="120.00" shape="-20.00,100.00 100.00,100.00"/>
    </edge>
    <edge id="N1" from="I1" to="I1" priority="1">
        <lane id="N1_0" index="0" speed="15.0" length="120.00" shape="100.00,-20.00 100.00,100.00"/>
    </edge>
    <edge id="S1" from="I1" to="I1" priority="1">
        <lane id="S1_0" index="0" speed="15.0" length="120.00" shape="100.00,220.00 100.00,100.00"/>
    </edge>
    
    <!-- Connections -->
    <connection from="E1" to="W1" fromLane="0" toLane="0" dir="s" state="M"/>
    <connection from="W1" to="E1" fromLane="0" toLane="0" dir="s" state="M"/>
    <connection from="N1" to="S1" fromLane="0" toLane="0" dir="s" state="M"/>
    <connection from="S1" to="N1" fromLane="0" toLane="0" dir="s" state="M"/>
</net>"""
    
    with open("working_network.net.xml", 'w') as f:
        f.write(network_xml)
    
    print("✅ Working network created: working_network.net.xml")

def create_working_routes():
    """Create working routes"""
    routes_xml = """<?xml version="1.0" encoding="UTF-8"?>
<routes xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="http://sumo.dlr.de/xsd/routes_file.xsd">
    <vType id="car" accel="3.0" decel="5.0" sigma="0.3" length="4.5" maxSpeed="60" minGap="1.5" tau="1.0"/>
    <vehicle id="veh0" type="car" route="E1 W1" depart="0"/>
    <vehicle id="veh1" type="car" route="W1 E1" depart="2"/>
    <vehicle id="veh2" type="car" route="N1 S1" depart="4"/>
    <vehicle id="veh3" type="car" route="S1 N1" depart="6"/>
    <vehicle id="veh4" type="car" route="E1 W1" depart="8"/>
    <vehicle id="veh5" type="car" route="W1 E1" depart="10"/>
    <vehicle id="veh6" type="car" route="N1 S1" depart="12"/>
    <vehicle id="veh7" type="car" route="S1 N1" depart="14"/>
    <vehicle id="veh8" type="car" route="E1 W1" depart="16"/>
    <vehicle id="veh9" type="car" route="W1 E1" depart="18"/>
</routes>"""
    
    with open("working_routes.rou.xml", 'w') as f:
        f.write(routes_xml)
    
    print("✅ Working routes created: working_routes.rou.xml")

def create_working_traffic_lights():
    """Create working traffic lights"""
    traffic_lights_xml = """<?xml version="1.0" encoding="UTF-8"?>
<additional xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="http://sumo.dlr.de/xsd/additional_file.xsd">
    <tlLogic id="I1" type="static" programID="0" offset="0">
        <phase duration="30" state="GGrrGGrr"/>
        <phase duration="3" state="yyrryyrr"/>
        <phase duration="30" state="rrGGrrGG"/>
        <phase duration="3" state="rryyrryy"/>
    </tlLogic>
</additional>"""
    
    with open("working_traffic_lights.xml", 'w') as f:
        f.write(traffic_lights_xml)
    
    print("✅ Working traffic lights created: working_traffic_lights.xml")

def create_working_sumo_config():
    """Create working SUMO configuration"""
    sumo_config = """<?xml version="1.0" encoding="UTF-8"?>
<configuration xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="http://sumo.dlr.de/xsd/sumoConfiguration.xsd">
    <input>
        <net-file value="working_network.net.xml"/>
        <route-files value="working_routes.rou.xml"/>
        <additional-files value="working_traffic_lights.xml"/>
    </input>
    <time>
        <begin value="0"/>
        <end value="100"/>
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
</configuration>"""
    
    with open("working_simulation.sumocfg", 'w') as f:
        f.write(sumo_config)
    
    print("✅ Working SUMO config created: working_simulation.sumocfg")

if __name__ == "__main__":
    print("🔧 Creating Working SUMO Files...")
    create_working_network()
    create_working_routes()
    create_working_traffic_lights()
    create_working_sumo_config()
    print("✅ All working files created successfully!")
