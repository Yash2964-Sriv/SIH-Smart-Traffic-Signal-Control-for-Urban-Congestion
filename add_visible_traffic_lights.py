#!/usr/bin/env python3
"""
Add visible traffic lights with red, yellow, green colors
"""

import os
import subprocess

def create_network_with_proper_traffic_lights():
    """Create network with properly configured traffic lights that show colors"""
    print("🚦 Creating Network with Visible Traffic Light Colors")
    
    # Enhanced node file with traffic light configuration
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
    
    with open("real_traffic_output/traffic_lights_nodes.nod.xml", "w") as f:
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
    
    with open("real_traffic_output/traffic_lights_edges.edg.xml", "w") as f:
        f.write(edg_content)
    
    print("✅ Node and edge files created")
    
    # Use netconvert to create the network with proper traffic lights
    sumo_bin = r"C:\Program Files (x86)\Eclipse\Sumo\bin"
    netconvert_path = os.path.join(sumo_bin, "netconvert.exe")
    
    if not os.path.exists(netconvert_path):
        print(f"❌ netconvert not found at {netconvert_path}")
        return False
    
    try:
        cmd = [
            netconvert_path,
            "--node-files", "real_traffic_output/traffic_lights_nodes.nod.xml",
            "--edge-files", "real_traffic_output/traffic_lights_edges.edg.xml",
            "--output-file", "real_traffic_output/visible_traffic_lights.net.xml",
            "--tls.default-type", "static",
            "--tls.guess-signals", "true"
        ]
        
        print("🔧 Running netconvert with traffic light signals...")
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Network with visible traffic lights created successfully!")
            return True
        else:
            print(f"❌ netconvert failed: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error running netconvert: {e}")
        return False

def create_visual_settings_with_colored_lights():
    """Create visual settings that show traffic light colors"""
    print("🎨 Creating Visual Settings with Colored Traffic Lights")
    
    visual_content = '''<?xml version="1.0" encoding="UTF-8"?>
<viewsettings xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="http://sumo.dlr.de/xsd/viewsettings_file.xsd">
    
    <!-- Professional color scheme with visible traffic lights -->
    <scheme name="traffic_lights_visible">
        <!-- Road elements -->
        <lane>
            <color value="0.2,0.2,0.2"/>
            <width value="1.2"/>
        </lane>
        <junction>
            <color value="0.3,0.3,0.3"/>
            <width value="1.0"/>
        </junction>
        
        <!-- Vehicle colors -->
        <vehicle>
            <color value="1,1,1"/>
            <width value="1.5"/>
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
        
        <!-- Traffic lights - Make them very visible -->
        <traffic_light>
            <color value="0,1,0"/>
            <width value="3.0"/>
        </traffic_light>
        
        <!-- Background -->
        <background>
            <color value="0.9,0.9,0.9"/>
        </background>
    </scheme>
    
    <!-- Decals for traffic light visualization -->
    <decals>
        <!-- I1 Traffic Lights -->
        <decal id="tl_I1_north" x="100" y="80" type="traffic_light" color="0,1,0" size="3.0"/>
        <decal id="tl_I1_south" x="100" y="120" type="traffic_light" color="1,0,0" size="3.0"/>
        <decal id="tl_I1_east" x="120" y="100" type="traffic_light" color="1,0,0" size="3.0"/>
        <decal id="tl_I1_west" x="80" y="100" type="traffic_light" color="1,0,0" size="3.0"/>
        
        <!-- I2 Traffic Lights -->
        <decal id="tl_I2_north" x="200" y="80" type="traffic_light" color="0,1,0" size="3.0"/>
        <decal id="tl_I2_south" x="200" y="120" type="traffic_light" color="1,0,0" size="3.0"/>
        <decal id="tl_I2_east" x="220" y="100" type="traffic_light" color="1,0,0" size="3.0"/>
        <decal id="tl_I2_west" x="180" y="100" type="traffic_light" color="1,0,0" size="3.0"/>
    </decals>
    
    <!-- POI for speed limit signs -->
    <poi>
        <poi id="speed_90" x="100" y="50" type="speed_limit" value="90" color="1,0,0" size="2.0"/>
        <poi id="speed_60" x="200" y="50" type="speed_limit" value="60" color="1,0,0" size="2.0"/>
        <poi id="speed_30" x="100" y="150" type="speed_limit" value="30" color="1,0,0" size="2.0"/>
    </poi>
    
</viewsettings>'''
    
    with open("real_traffic_output/traffic_lights_visual.xml", "w") as f:
        f.write(visual_content)
    
    print("✅ Visual settings with colored traffic lights created")

def create_config_with_visible_lights():
    """Create configuration that enables traffic light visualization"""
    print("⚙️ Creating Configuration with Visible Traffic Lights")
    
    config_content = '''<?xml version="1.0" encoding="UTF-8"?>
<configuration xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="http://sumo.dlr.de/xsd/sumoConfiguration.xsd">

    <input>
        <net-file value="visible_traffic_lights.net.xml"/>
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
        <gui-settings-file value="traffic_lights_visual.xml"/>
        <breakpoints value="0,30,60,90,120,150,180,210,240,270,300"/>
    </gui_only>

</configuration>'''
    
    with open("real_traffic_output/visible_traffic_lights.sumocfg", "w") as f:
        f.write(config_content)
    
    print("✅ Configuration with visible traffic lights created")

def create_launcher_with_visible_lights():
    """Create launcher for simulation with visible traffic lights"""
    print("🚀 Creating Launcher with Visible Traffic Lights")
    
    launcher_content = '''#!/usr/bin/env python3
"""
Launch Simulation with Visible Traffic Lights
"""

import os
import sys
import time

def main():
    """Main launcher for simulation with visible traffic lights"""
    print("🚦 SIMULATION WITH VISIBLE TRAFFIC LIGHTS")
    print("=" * 50)
    print("🎯 Features:")
    print("   • Red, Yellow, Green traffic light colors")
    print("   • Two intersections (I1, I2)")
    print("   • Multiple lanes in each direction")
    print("   • Speed limit signs (90, 60, 30 km/h)")
    print("   • AI-controlled traffic signals")
    
    # Check if config exists
    config_file = "real_traffic_output/visible_traffic_lights.sumocfg"
    if not os.path.exists(config_file):
        print(f"❌ Config file not found: {config_file}")
        return
    
    print(f"\\n✅ Configuration found: {config_file}")
    
    # Import and run the AI controller
    try:
        from ai_controller.simple_working_ai_controller import SimpleWorkingAIController
        
        print("\\n🎯 Starting Simulation with Visible Traffic Lights...")
        print("   - Traffic lights will show Red, Yellow, Green colors")
        print("   - AI will control traffic lights dynamically")
        print("   - Watch the lights change as traffic moves")
        print("   - Simulation will run for 10 minutes")
        print("   - Press Ctrl+C to stop early")
        
        # Create controller
        controller = SimpleWorkingAIController(
            junction_ids=["I1", "I2"],
            sumo_config=config_file
        )
        
        # Start simulation with GUI
        if controller.start_simulation(gui=True):
            print("\\n🚀 SUMO GUI with visible traffic lights should open now...")
            print("   Watch the traffic lights change colors!")
            print("   - Green: Go")
            print("   - Yellow: Caution")
            print("   - Red: Stop")
            
            # Run simulation for 10 minutes
            controller.run_simulation(max_duration=600.0, control_interval=2.0)
            
            # Print final performance report
            controller.print_performance_report()
        
        # Close simulation
        controller.close_simulation()
        
        print("\\n✅ Simulation with visible traffic lights completed!")
        print("   You should have seen the traffic lights changing colors")
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()'''
    
    with open("launch_visible_traffic_lights.py", "w") as f:
        f.write(launcher_content)
    
    print("✅ Launcher with visible traffic lights created")

def main():
    """Main function to add visible traffic lights"""
    print("🚦 ADDING VISIBLE TRAFFIC LIGHTS")
    print("=" * 50)
    
    # Create network with proper traffic lights
    if create_network_with_proper_traffic_lights():
        # Create visual settings
        create_visual_settings_with_colored_lights()
        
        # Create configuration
        create_config_with_visible_lights()
        
        # Create launcher
        create_launcher_with_visible_lights()
        
        print("\n🎉 VISIBLE TRAFFIC LIGHTS ADDED!")
        print("=" * 40)
        print("✅ Traffic lights will show Red, Yellow, Green colors")
        print("✅ Lights will change as traffic moves")
        print("✅ AI will control the light timing")
        print("✅ Professional visual appearance")
        
        print("\n🚀 TO RUN THE SIMULATION WITH VISIBLE LIGHTS:")
        print("   python launch_visible_traffic_lights.py")
        
    else:
        print("❌ Failed to create network with traffic lights")

if __name__ == "__main__":
    main()

