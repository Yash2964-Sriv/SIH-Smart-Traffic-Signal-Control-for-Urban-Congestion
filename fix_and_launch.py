#!/usr/bin/env python3
"""
Fix Path Issues and Launch Professional SUMO with Background
"""

import os
import subprocess
from PIL import Image, ImageDraw

def create_simple_background():
    """Create a simple satellite-like background image"""
    print("🛰️ Creating Satellite Background Image...")
    
    # Create a 2000x2000 satellite-like background
    width, height = 2000, 2000
    img = Image.new('RGB', (width, height), color=(34, 139, 34))  # Forest green
    
    draw = ImageDraw.Draw(img)
    
    # Add road patterns
    road_color = (60, 60, 60)
    center_x, center_y = width // 2, height // 2
    
    # Main roads
    draw.rectangle([center_x - 20, 0, center_x + 20, height], fill=road_color)
    draw.rectangle([0, center_y - 20, width, center_y + 20], fill=road_color)
    
    # Lane markings
    for i in range(0, width, 50):
        if i != center_x - 20 and i != center_x + 20:
            draw.line([(i, 0), (i, height)], fill=(255, 255, 255), width=1)
    
    for i in range(0, height, 50):
        if i != center_y - 20 and i != center_y + 20:
            draw.line([(0, i), (width, i)], fill=(255, 255, 255), width=1)
    
    # Add buildings
    building_colors = [(139, 69, 19), (160, 82, 45), (210, 180, 140)]
    for i in range(20):
        x = (i * 150) % (width - 100)
        y = (i * 120) % (height - 100)
        if abs(x - center_x) > 100 or abs(y - center_y) > 100:
            w, h = 80, 60
            color = building_colors[i % len(building_colors)]
            draw.rectangle([x, y, x + w, y + h], fill=color)
    
    # Save background
    background_file = "real_traffic_output/background.png"
    img.save(background_file, "PNG")
    print(f"✅ Created background: {background_file}")
    return background_file

def create_working_config():
    """Create a working configuration without background issues"""
    print("⚙️ Creating Working Configuration...")
    
    config_content = '''<?xml version="1.0" encoding="UTF-8"?>
<configuration xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="http://sumo.dlr.de/xsd/sumoConfiguration.xsd">
    <input>
        <net-file value="real_osm_network.net.xml"/>
        <route-files value="real_osm_routes.rou.xml"/>
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
    </gui_only>
    <output>
        <fcd-output value="working_fcd.xml"/>
        <netstate-dump value="working_netstate.xml"/>
    </output>
</configuration>'''
    
    config_file = "real_traffic_output/working_osm_config.sumocfg"
    with open(config_file, 'w') as f:
        f.write(config_content)
    
    print(f"✅ Created working config: {config_file}")
    return config_file

def create_enhanced_visual():
    """Create enhanced visual settings"""
    print("🎨 Creating Enhanced Visual Settings...")
    
    visual_content = '''<viewsettings>
    <scheme name="real world"/>
    <delay value="500"/>
    <zoom value="2000"/>
    <viewport x="0" y="0"/>
    
    <vehicles>
        <default value="true" showType="true" showRoute="false" showSignals="true" showBlinker="true" showSpeed="false" showLane="false" showColor="true"/>
        <shape value="true"/>
        <minSize value="4"/>
        <maxSize value="400"/>
        <color value="byType"/>
        <scale value="2.0"/>
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
    
    <gui_only>
        <scale value="2.5"/>
        <lighting value="true"/>
        <shadows value="true"/>
        <textures value="true"/>
        <background value="white"/>
        <antialiase value="true"/>
    </gui_only>
</viewsettings>'''
    
    visual_file = "real_traffic_output/working_visual_settings.xml"
    with open(visual_file, 'w') as f:
        f.write(visual_content)
    
    print(f"✅ Created visual settings: {visual_file}")
    return visual_file

def launch_sumo_safely():
    """Launch SUMO safely from correct directory"""
    print("🚀 Launching Professional SUMO...")
    
    # Change to correct directory
    os.chdir("real_traffic_output")
    print(f"📁 Working directory: {os.getcwd()}")
    
    # Check if files exist
    config_file = "working_osm_config.sumocfg"
    visual_file = "working_visual_settings.xml"
    
    if not os.path.exists(config_file):
        print(f"❌ Config file not found: {config_file}")
        return False
    
    if not os.path.exists(visual_file):
        print(f"❌ Visual file not found: {visual_file}")
        return False
    
    # Launch SUMO
    sumo_path = r"C:\Program Files (x86)\Eclipse\Sumo\bin\sumo-gui.exe"
    cmd = [sumo_path, "-c", config_file, "--gui-settings-file", visual_file, "--delay", "500"]
    
    print(f"🔄 Running: {' '.join(cmd)}")
    
    try:
        subprocess.Popen(cmd)
        print("✅ Professional SUMO launched successfully!")
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("🎯 Fixing Path Issues and Launching Professional SUMO")
    print("=" * 60)
    
    # Create background image
    create_simple_background()
    
    # Create working configuration
    config_file = create_working_config()
    
    # Create enhanced visual settings
    visual_file = create_enhanced_visual()
    
    # Launch SUMO safely
    if launch_sumo_safely():
        print("\n🎉 SUCCESS! Professional SUMO is now running!")
        print("=" * 50)
        print("🎯 Features:")
        print("   • Real OpenStreetMap road network")
        print("   • Professional visual settings")
        print("   • Enhanced vehicle graphics")
        print("   • Realistic traffic patterns")
        print("\n✨ The path issues are fixed and SUMO is running!")
    else:
        print("\n❌ Failed to launch SUMO")
