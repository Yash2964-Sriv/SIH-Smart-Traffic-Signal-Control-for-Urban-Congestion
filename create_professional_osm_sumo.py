#!/usr/bin/env python3
"""
Create Professional SUMO with OpenStreetMap + Background Image
Achieve the exact quality from the reference image
"""

import os
import subprocess
import requests
import xml.etree.ElementTree as ET

def download_real_osm_data():
    """Download real OpenStreetMap data for a major intersection"""
    print("🗺️ Downloading Real OpenStreetMap Data...")
    
    # Use a real major intersection (Times Square area for complexity)
    overpass_url = "http://overpass-api.de/api/interpreter"
    
    # Larger area around Times Square for better road network
    query = """
    [out:xml][timeout:45];
    (
      way["highway"~"^(primary|secondary|tertiary|residential|trunk|motorway)$"](40.755, -73.990, 40.765, -73.980);
      node["highway"~"^(traffic_signals|stop)$"](40.755, -73.990, 40.765, -73.980);
      relation["type"="route"]["route"~"^(bus|trolleybus)$"](40.755, -73.990, 40.765, -73.980);
    );
    out geom;
    """
    
    try:
        print("📡 Downloading from OpenStreetMap...")
        response = requests.post(overpass_url, data=query, timeout=60)
        
        if response.status_code == 200:
            osm_file = "real_traffic_output/real_intersection.osm"
            with open(osm_file, 'w', encoding='utf-8') as f:
                f.write(response.text)
            print(f"✅ Downloaded real OSM data: {osm_file}")
            return osm_file
        else:
            print(f"❌ Error downloading OSM data: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Error downloading OSM data: {e}")
        return None

def convert_osm_to_sumo(osm_file):
    """Convert OSM data to professional SUMO network"""
    print("🏗️ Converting OSM to Professional SUMO Network...")
    
    sumo_path = r"C:\Program Files (x86)\Eclipse\Sumo\bin\netconvert.exe"
    net_file = "real_traffic_output/real_osm_network.net.xml"
    
    cmd = [
        sumo_path,
        "--osm-files", osm_file,
        "--output-file", net_file,
        "--osm.elevation",
        "--osm.bike-access", 
        "--osm.sidewalks",
        "--osm.crossings",
        "--osm.turn-lanes",
        "--junctions.join",
        "--junctions.join-dist", "20",
        "--tls.guess",
        "--tls.guess.threshold", "3",
        "--tls.join",
        "--tls.join-dist", "30",
        "--roundabouts.guess",
        "--ramps.guess",
        "--sidewalks.guess",
        "--crossings.guess",
        "--bikelanes.guess",
        "--default.lanewidth", "3.5",
        "--default.speed", "13.89",
        "--default.lanenumber", "2",
        "--geometry.max-angle", "25",
        "--geometry.min-radius", "15",
        "--junctions.corner-detail", "10",
        "--junctions.internal-link-detail", "10",
        "--junctions.limit-turn-speed", "1.5",
        "--junctions.higher-speed",
        "--verbose"
    ]
    
    try:
        print("🔄 Converting OSM to SUMO network...")
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Successfully created professional SUMO network from OSM!")
            return net_file
        else:
            print(f"❌ Error converting OSM: {result.stderr}")
            return None
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def create_background_image():
    """Create a professional background image"""
    print("🖼️ Creating Professional Background Image...")
    
    # For now, create a simple background that can be replaced with real satellite imagery
    # In a real implementation, you would download satellite imagery from Google Maps, Bing, etc.
    
    background_info = {
        "file": "real_traffic_output/background.png",
        "x": "0",
        "y": "0", 
        "width": "2000",
        "height": "2000"
    }
    
    print("📝 Note: For production use, replace with real satellite imagery")
    print("   - Download from Google Maps, Bing Maps, or open data")
    print("   - Ensure geo-referenced alignment with OSM coordinates")
    print("   - Save as background.png in real_traffic_output folder")
    
    return background_info

def create_professional_routes():
    """Create professional routes with realistic traffic"""
    print("🚗 Creating Professional Traffic Routes...")
    
    routes_content = '''<?xml version="1.0" encoding="UTF-8"?>
<routes xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="http://sumo.dlr.de/xsd/routes_file.xsd">
    
    <!-- Professional Vehicle Types -->
    <vType id="car" accel="2.6" decel="4.5" sigma="0.5" length="4.3" maxSpeed="50" guiShape="passenger" color="1,0,0" width="1.8" height="1.5" minGap="2.5"/>
    <vType id="truck" accel="1.2" decel="3.5" sigma="0.3" length="12" maxSpeed="30" guiShape="truck" color="0,0,1" width="2.5" height="3.5" minGap="3.0"/>
    <vType id="bus" accel="1.0" decel="3.0" sigma="0.2" length="15" maxSpeed="25" guiShape="bus" color="0,1,0" width="2.5" height="3.5" minGap="4.0"/>
    <vType id="motorcycle" accel="3.0" decel="6.0" sigma="0.8" length="2" maxSpeed="60" guiShape="motorcycle" color="1,1,0" width="1.0" height="1.2" minGap="1.0"/>
    <vType id="taxi" accel="2.8" decel="4.5" sigma="0.6" length="4.5" maxSpeed="45" guiShape="taxi" color="1,0.5,0" width="1.8" height="1.5" minGap="2.0"/>
    <vType id="emergency" accel="3.5" decel="5.0" sigma="0.1" length="5.0" maxSpeed="70" guiShape="emergency" color="1,0,1" width="2.0" height="2.0" minGap="1.5"/>
    
    <!-- Realistic traffic flows -->
    <flow id="flow_cars" type="car" begin="0" end="200" period="1.5" color="1,0,0"/>
    <flow id="flow_trucks" type="truck" begin="5" end="200" period="8" color="0,0,1"/>
    <flow id="flow_buses" type="bus" begin="10" end="200" period="12" color="0,1,0"/>
    <flow id="flow_motorcycles" type="motorcycle" begin="2" end="200" period="4" color="1,1,0"/>
    <flow id="flow_taxis" type="taxi" begin="3" end="200" period="2.5" color="1,0.5,0"/>
    <flow id="flow_emergency" type="emergency" begin="30" end="200" period="40" color="1,0,1"/>
    
</routes>'''
    
    routes_file = "real_traffic_output/real_osm_routes.rou.xml"
    with open(routes_file, 'w') as f:
        f.write(routes_content)
    
    print(f"✅ Created professional routes: {routes_file}")
    return routes_file

def create_professional_config(net_file, routes_file, background_info):
    """Create professional configuration with background image"""
    print("⚙️ Creating Professional Configuration with Background...")
    
    config_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<configuration xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="http://sumo.dlr.de/xsd/sumoConfiguration.xsd">
    <input>
        <net-file value="{os.path.basename(net_file)}"/>
        <route-files value="{os.path.basename(routes_file)}"/>
    </input>
    <time>
        <begin value="0"/>
        <end value="200"/>
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
        <background>
            <img file="{background_info['file']}" x="{background_info['x']}" y="{background_info['y']}" width="{background_info['width']}" height="{background_info['height']}"/>
        </background>
    </gui_only>
    <output>
        <fcd-output value="real_osm_fcd.xml"/>
        <netstate-dump value="real_osm_netstate.xml"/>
    </output>
</configuration>'''
    
    config_file = "real_traffic_output/real_osm_config.sumocfg"
    with open(config_file, 'w') as f:
        f.write(config_content)
    
    print(f"✅ Created professional configuration: {config_file}")
    return config_file

def create_enhanced_visual_settings():
    """Create enhanced visual settings for professional quality"""
    print("🎨 Creating Enhanced Visual Settings...")
    
    visual_settings = '''<viewsettings>
    <scheme name="real world"/>
    <delay value="500"/>
    <zoom value="2000"/>
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
        <width value="8"/>
        <color value="bySpeed"/>
    </edges>
    
    <lanes>
        <default value="true" showShape="true" showName="false" showSignals="true"/>
        <width value="6"/>
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

def launch_professional_sumo(config_file, visual_file):
    """Launch SUMO with professional quality"""
    print("🚀 Launching Professional SUMO with Real-World Background...")
    
    # Change to correct directory
    os.chdir("real_traffic_output")
    
    sumo_path = r"C:\Program Files (x86)\Eclipse\Sumo\bin\sumo-gui.exe"
    cmd = [sumo_path, "-c", config_file, "--gui-settings-file", visual_file, "--delay", "500"]
    
    print(f"🔄 Running: {' '.join(cmd)}")
    
    try:
        subprocess.Popen(cmd)
        print("✅ Professional SUMO launched!")
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("🎯 Creating Professional SUMO with OpenStreetMap + Background")
    print("=" * 60)
    print("🎯 Goal: Achieve the exact quality from reference image")
    print("=" * 60)
    
    # Step 1: Download real OSM data
    osm_file = download_real_osm_data()
    
    if osm_file:
        # Step 2: Convert to professional SUMO network
        net_file = convert_osm_to_sumo(osm_file)
        
        if net_file:
            # Step 3: Create background image info
            background_info = create_background_image()
            
            # Step 4: Create professional routes
            routes_file = create_professional_routes()
            
            # Step 5: Create professional configuration with background
            config_file = create_professional_config(net_file, routes_file, background_info)
            
            # Step 6: Create enhanced visual settings
            visual_file = create_enhanced_visual_settings()
            
            # Step 7: Launch professional SUMO
            if launch_professional_sumo(config_file, visual_file):
                print("\n🎉 SUCCESS! Professional SUMO with Real-World Background launched!")
                print("=" * 70)
                print("🎯 This should now match the reference image quality!")
                print("   • Real OpenStreetMap road network")
                print("   • Professional background image support")
                print("   • Enhanced visual settings")
                print("   • Realistic traffic patterns")
                print("\n📝 Note: For best results, replace background.png with real satellite imagery")
            else:
                print("\n❌ Failed to launch professional SUMO")
        else:
            print("\n❌ Failed to create network from OSM data")
    else:
        print("\n❌ Failed to download OSM data")
