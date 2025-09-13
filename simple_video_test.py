"""
Simple Video Test
Test video processing with OpenCV motion detection
"""

import cv2
import numpy as np
from pathlib import Path
import time

def test_video_processing():
    """Test video processing with a simple approach"""
    print("🎬 Simple Video Processing Test")
    print("=" * 35)
    
    # Create a simple test video
    print("1️⃣ Creating test video...")
    width, height = 400, 300
    fps = 10
    duration = 10  # 10 seconds
    total_frames = fps * duration
    
    # Create video writer
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter('simple_test.mp4', fourcc, fps, (width, height))
    
    # Create moving rectangles (simulating vehicles)
    for frame_num in range(total_frames):
        # Create frame
        frame = np.zeros((height, width, 3), dtype=np.uint8)
        
        # Draw background
        cv2.rectangle(frame, (0, 0), (width, height), (50, 50, 50), -1)
        
        # Draw moving rectangles (vehicles)
        t = frame_num / fps
        
        # Vehicle 1 - moving horizontally
        x1 = int(50 + t * 20) % width
        cv2.rectangle(frame, (x1, height//2 - 10), (x1 + 40, height//2 + 10), (0, 0, 255), -1)
        
        # Vehicle 2 - moving vertically
        y1 = int(50 + t * 15) % height
        cv2.rectangle(frame, (width//2 - 10, y1), (width//2 + 10, y1 + 30), (0, 255, 0), -1)
        
        # Vehicle 3 - moving diagonally
        x2 = int(100 + t * 10) % width
        y2 = int(100 + t * 8) % height
        cv2.rectangle(frame, (x2, y2), (x2 + 30, y2 + 20), (255, 0, 0), -1)
        
        out.write(frame)
    
    out.release()
    print("✅ Test video created: simple_test.mp4")
    
    # Process the video
    print("\n2️⃣ Processing video...")
    
    cap = cv2.VideoCapture('simple_test.mp4')
    bg_subtractor = cv2.createBackgroundSubtractorMOG2(detectShadows=True)
    
    frame_count = 0
    vehicles_detected = 0
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        # Convert to grayscale
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (21, 21), 0)
        
        # Apply background subtraction
        fg_mask = bg_subtractor.apply(blurred)
        
        # Find contours
        contours, _ = cv2.findContours(fg_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Count vehicles
        frame_vehicles = 0
        for contour in contours:
            area = cv2.contourArea(contour)
            if area > 100:  # Minimum area threshold
                x, y, w, h = cv2.boundingRect(contour)
                aspect_ratio = w / h
                if 0.3 < aspect_ratio < 4.0 and w > 15 and h > 10:
                    frame_vehicles += 1
        
        vehicles_detected += frame_vehicles
        
        # Show frame
        cv2.imshow('Original', frame)
        cv2.imshow('Motion Detection', fg_mask)
        
        if cv2.waitKey(30) & 0xFF == ord('q'):
            break
        
        frame_count += 1
    
    cap.release()
    cv2.destroyAllWindows()
    
    print(f"✅ Video processing completed:")
    print(f"   Frames processed: {frame_count}")
    print(f"   Total vehicle detections: {vehicles_detected}")
    print(f"   Average detections per frame: {vehicles_detected / frame_count:.2f}")
    
    # Generate SUMO data
    print("\n3️⃣ Generating SUMO data...")
    
    # Create simple SUMO network
    network_xml = """<?xml version="1.0" encoding="UTF-8"?>
<net version="1.9" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="http://sumo.dlr.de/xsd/net_file.xsd">
    <location netOffset="0.00,0.00" convBoundary="0.00,0.00,200.00,200.00" origBoundary="-180.00,-90.00,180.00,90.00" projParameter="+proj=longlat +ellps=WGS84 +datum=WGS84 +no_defs"/>
    
    <junction id="center" type="traffic_light" x="100.0" y="100.0" incLanes="" intLanes="" shape="100.0,100.0"/>
    <junction id="north_end" type="priority" x="100.0" y="0.0" incLanes="" intLanes="" shape="100.0,0.0"/>
    <junction id="south_end" type="priority" x="100.0" y="200.0" incLanes="" intLanes="" shape="100.0,200.0"/>
    <junction id="east_end" type="priority" x="200.0" y="100.0" incLanes="" intLanes="" shape="200.0,100.0"/>
    <junction id="west_end" type="priority" x="0.0" y="100.0" incLanes="" intLanes="" shape="0.0,100.0"/>
    
    <edge id="north" from="north_end" to="center" priority="1">
        <lane id="north_0" index="0" speed="13.89" length="100.0" shape="100.0,0.0 100.0,100.0"/>
    </edge>
    <edge id="south" from="south_end" to="center" priority="1">
        <lane id="south_0" index="0" speed="13.89" length="100.0" shape="100.0,200.0 100.0,100.0"/>
    </edge>
    <edge id="east" from="east_end" to="center" priority="1">
        <lane id="east_0" index="0" speed="13.89" length="100.0" shape="200.0,100.0 100.0,100.0"/>
    </edge>
    <edge id="west" from="west_end" to="center" priority="1">
        <lane id="west_0" index="0" speed="13.89" length="100.0" shape="0.0,100.0 100.0,100.0"/>
    </edge>
    
    <tlLogic id="center" type="static" programID="0" offset="0">
        <phase duration="31" state="GGrrrrGGrrrr"/>
        <phase duration="6" state="yyrrrryyrrrr"/>
        <phase duration="31" state="rrGGrrrrGGrr"/>
        <phase duration="6" state="rryyrrrryyrr"/>
        <phase duration="31" state="rrrrGGrrrrGG"/>
        <phase duration="6" state="rrrryyrrrryy"/>
        <phase duration="31" state="rrrrrrGGrrrr"/>
        <phase duration="6" state="rrrrrryyrrrr"/>
    </tlLogic>
</net>"""
    
    with open('simple_network.net.xml', 'w') as f:
        f.write(network_xml)
    
    # Create routes based on detected vehicles
    routes_xml = """<?xml version="1.0" encoding="UTF-8"?>
<routes>
    <vType id="car" accel="2.6" decel="4.5" sigma="0.5" length="5" maxSpeed="50"/>
    
    <route id="north_route" edges="north"/>
    <route id="south_route" edges="south"/>
    <route id="east_route" edges="east"/>
    <route id="west_route" edges="west"/>
    
    <vehicle id="veh_0" type="car" depart="1" route="north_route"/>
    <vehicle id="veh_1" type="car" depart="2" route="south_route"/>
    <vehicle id="veh_2" type="car" depart="3" route="east_route"/>
    <vehicle id="veh_3" type="car" depart="4" route="west_route"/>
    <vehicle id="veh_4" type="car" depart="5" route="north_route"/>
    <vehicle id="veh_5" type="car" depart="6" route="south_route"/>
</routes>"""
    
    with open('simple_routes.rou.xml', 'w') as f:
        f.write(routes_xml)
    
    # Create config
    config_xml = """<?xml version="1.0" encoding="UTF-8"?>
<configuration xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="http://sumo.dlr.de/xsd/sumoConfiguration.xsd">
    <input>
        <net-file value="simple_network.net.xml"/>
        <route-files value="simple_routes.rou.xml"/>
    </input>
    <time>
        <begin value="0"/>
        <end value="10"/>
        <step-length value="1"/>
    </time>
    <processing>
        <ignore-route-errors value="1"/>
        <ignore-junction-blocker value="1"/>
    </processing>
    <report>
        <verbose value="1"/>
        <no-step-log value="1"/>
    </report>
    <output>
        <fcd-output value="simple_simulation_fcd.xml"/>
        <netstate-dump value="simple_simulation_netstate.xml"/>
    </output>
</configuration>"""
    
    with open('simple_simulation.sumocfg', 'w') as f:
        f.write(config_xml)
    
    print("✅ SUMO files generated:")
    print("   - simple_network.net.xml")
    print("   - simple_routes.rou.xml")
    print("   - simple_simulation.sumocfg")
    
    # Run SUMO simulation
    print("\n4️⃣ Running SUMO simulation...")
    import subprocess
    
    try:
        result = subprocess.run([
            r"C:\Program Files (x86)\Eclipse\Sumo\bin\sumo.exe",
            "-c", "simple_simulation.sumocfg"
        ], capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print("✅ SUMO simulation completed successfully!")
            print("   Simulation output:")
            print(result.stdout)
        else:
            print("❌ SUMO simulation failed:")
            print(result.stderr)
    
    except Exception as e:
        print(f"❌ Error running SUMO: {e}")
    
    print(f"\n🎉 Simple video test completed!")
    print(f"📁 Generated files:")
    print(f"   - simple_test.mp4 (test video)")
    print(f"   - simple_network.net.xml (SUMO network)")
    print(f"   - simple_routes.rou.xml (SUMO routes)")
    print(f"   - simple_simulation.sumocfg (SUMO config)")

if __name__ == "__main__":
    test_video_processing()
