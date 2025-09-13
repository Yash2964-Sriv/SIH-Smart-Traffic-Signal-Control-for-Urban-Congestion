#!/usr/bin/env python3
"""
Analyze Real Traffic Video and Replicate in SUMO
Creates a complete SUMO simulation based on real traffic video analysis
"""

import cv2
import numpy as np
import json
import os
import time
from datetime import datetime

class TrafficVideoAnalyzer:
    """Analyzes real traffic video to extract patterns"""
    
    def __init__(self, video_path):
        self.video_path = video_path
        self.analysis_data = {
            'vehicle_counts': [],
            'traffic_phases': [],
            'waiting_times': [],
            'flow_rates': [],
            'intersection_activity': []
        }
    
    def analyze_video(self):
        """Analyze the traffic video"""
        print("🎬 Analyzing real traffic video...")
        print(f"📁 Video: {self.video_path}")
        
        cap = cv2.VideoCapture(self.video_path)
        if not cap.isOpened():
            print("❌ Could not open video file")
            return False
        
        frame_count = 0
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        
        print(f"📊 Video info: {total_frames} frames, {fps:.1f} FPS")
        
        # Analyze every 10th frame for performance
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            if frame_count % 10 == 0:
                # Analyze this frame
                analysis = self._analyze_frame(frame, frame_count, fps)
                self.analysis_data['vehicle_counts'].append(analysis['vehicle_count'])
                self.analysis_data['traffic_phases'].append(analysis['traffic_phase'])
                self.analysis_data['waiting_times'].append(analysis['waiting_time'])
                self.analysis_data['flow_rates'].append(analysis['flow_rate'])
                self.analysis_data['intersection_activity'].append(analysis['intersection_activity'])
                
                if frame_count % 100 == 0:
                    print(f"   📈 Processed {frame_count}/{total_frames} frames")
            
            frame_count += 1
        
        cap.release()
        
        # Calculate averages and patterns
        self._calculate_patterns()
        
        print("✅ Video analysis completed!")
        return True
    
    def _analyze_frame(self, frame, frame_number, fps):
        """Analyze a single frame"""
        # Convert to grayscale for processing
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Simple vehicle detection using contours
        # This is a simplified approach - in practice, you'd use more sophisticated methods
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        edges = cv2.Canny(blurred, 50, 150)
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Filter contours by size (approximate vehicle detection)
        vehicle_count = 0
        for contour in contours:
            area = cv2.contourArea(contour)
            if 100 < area < 2000:  # Vehicle-sized objects
                vehicle_count += 1
        
        # Simulate traffic phases based on frame analysis
        traffic_phase = (frame_number // 30) % 4  # 4-phase cycle
        
        # Simulate waiting times and flow rates
        waiting_time = max(0, vehicle_count * 2.5)  # More vehicles = more waiting
        flow_rate = min(vehicle_count * 0.8, 20)  # Flow rate based on vehicle count
        
        # Intersection activity (simplified)
        intersection_activity = {
            'north': vehicle_count // 4,
            'south': vehicle_count // 4,
            'east': vehicle_count // 4,
            'west': vehicle_count // 4
        }
        
        return {
            'vehicle_count': vehicle_count,
            'traffic_phase': traffic_phase,
            'waiting_time': waiting_time,
            'flow_rate': flow_rate,
            'intersection_activity': intersection_activity
        }
    
    def _calculate_patterns(self):
        """Calculate traffic patterns from analysis data"""
        if not self.analysis_data['vehicle_counts']:
            return
        
        # Calculate averages
        avg_vehicles = np.mean(self.analysis_data['vehicle_counts'])
        avg_waiting = np.mean(self.analysis_data['waiting_times'])
        avg_flow = np.mean(self.analysis_data['flow_rates'])
        
        # Calculate peak times
        max_vehicles = max(self.analysis_data['vehicle_counts'])
        peak_frame = self.analysis_data['vehicle_counts'].index(max_vehicles)
        
        # Traffic patterns
        self.patterns = {
            'average_vehicles': float(avg_vehicles),
            'average_waiting_time': float(avg_waiting),
            'average_flow_rate': float(avg_flow),
            'peak_vehicles': max_vehicles,
            'peak_time': peak_frame * 10,  # Convert frame to time
            'total_frames': len(self.analysis_data['vehicle_counts']),
            'traffic_intensity': 'high' if avg_vehicles > 10 else 'medium' if avg_vehicles > 5 else 'low'
        }
        
        print(f"📊 Analysis Results:")
        print(f"   🚗 Average vehicles: {avg_vehicles:.1f}")
        print(f"   ⏱️ Average waiting time: {avg_waiting:.1f}s")
        print(f"   📈 Average flow rate: {avg_flow:.1f} vehicles/min")
        print(f"   🏆 Peak vehicles: {max_vehicles}")
        print(f"   🚦 Traffic intensity: {self.patterns['traffic_intensity']}")
    
    def save_analysis(self, filename='video_analysis.json'):
        """Save analysis data to file"""
        data = {
            'analysis_data': self.analysis_data,
            'patterns': self.patterns,
            'timestamp': datetime.now().isoformat(),
            'video_path': self.video_path
        }
        
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
        
        print(f"💾 Analysis saved to {filename}")

def create_sumo_from_analysis(analysis_file='video_analysis.json'):
    """Create SUMO simulation based on video analysis"""
    print("🏗️ Creating SUMO simulation from video analysis...")
    
    # Load analysis data
    with open(analysis_file, 'r') as f:
        data = json.load(f)
    
    patterns = data['patterns']
    
    # Create network XML
    network_xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<net version="1.9" junctionCornerDetail="5" limitTurnSpeed="5.5">
    <location netOffset="0.00,0.00" convBoundary="0.00,0.00,200.00,200.00" origBoundary="-10000000000.00,-10000000000.00,10000000000.00,10000000000.00" projParameter="!" />
    
    <!-- Traffic light junction -->
    <junction id="center" x="100.00" y="100.00" type="traffic_light" incLanes="north2center_0 south2center_0 east2center_0 west2center_0" intLanes=":center_0" shape="100.00,100.00" />
    
    <!-- Boundary junctions -->
    <junction id="north" x="100.00" y="200.00" type="priority" incLanes="" intLanes="" shape="100.00,200.00" />
    <junction id="south" x="100.00" y="0.00" type="priority" incLanes="" intLanes="" shape="100.00,0.00" />
    <junction id="east" x="200.00" y="100.00" type="priority" incLanes="" intLanes="" shape="200.00,100.00" />
    <junction id="west" x="0.00" y="100.00" type="priority" incLanes="" intLanes="" shape="0.00,100.00" />
    
    <!-- Edges -->
    <edge id="north2center" from="north" to="center" priority="1" numLanes="1" speed="13.89">
        <lane id="north2center_0" index="0" speed="13.89" length="100.00" width="3.50" shape="100.00,200.00 100.00,100.00" />
    </edge>
    
    <edge id="center2south" from="center" to="south" priority="1" numLanes="1" speed="13.89">
        <lane id="center2south_0" index="0" speed="13.89" length="100.00" width="3.50" shape="100.00,100.00 100.00,0.00" />
    </edge>
    
    <edge id="east2center" from="east" to="center" priority="1" numLanes="1" speed="13.89">
        <lane id="east2center_0" index="0" speed="13.89" length="100.00" width="3.50" shape="200.00,100.00 100.00,100.00" />
    </edge>
    
    <edge id="center2west" from="center" to="west" priority="1" numLanes="1" speed="13.89">
        <lane id="center2west_0" index="0" speed="13.89" length="100.00" width="3.50" shape="100.00,100.00 0.00,100.00" />
    </edge>
    
    <!-- Internal edge for traffic light -->
    <edge id=":center_0" from="center" to="center" priority="1" numLanes="1" speed="13.89">
        <lane id=":center_0" index="0" speed="13.89" length="0.00" width="3.50" shape="100.00,100.00 100.00,100.00" />
    </edge>
    
    <!-- Connections -->
    <connection from="north2center" to="center2south" fromLane="0" toLane="0" dir="s" state="M" />
    <connection from="east2center" to="center2west" fromLane="0" toLane="0" dir="l" state="M" />
    <connection from="center2south" to="north2center" fromLane="0" toLane="0" dir="s" state="M" />
    <connection from="center2west" to="east2center" fromLane="0" toLane="0" dir="l" state="M" />
</net>"""
    
    # Create routes XML based on analysis
    avg_vehicles = patterns['average_vehicles']
    vehicle_count = max(5, int(avg_vehicles * 2))  # Scale up for simulation
    
    routes_xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<routes xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="http://sumo.dlr.de/xsd/routes_file.xsd">
    <vType id="car" accel="2.6" decel="4.5" sigma="0.5" length="4.3" maxSpeed="13.89" />
    
    <route id="north_to_south" edges="north2center center2south" />
    <route id="south_to_north" edges="center2south north2center" />
    <route id="east_to_west" edges="east2center center2west" />
    <route id="west_to_east" edges="center2west east2center" />
    
    <!-- Generate vehicles based on analysis -->
"""
    
    # Generate vehicles based on analysis patterns
    for i in range(vehicle_count):
        depart_time = i * 2  # Spread vehicles over time
        route = ['north_to_south', 'south_to_north', 'east_to_west', 'west_to_east'][i % 4]
        routes_xml += f'    <vehicle id="veh{i}" type="car" route="{route}" depart="{depart_time}" />\n'
    
    routes_xml += "</routes>"
    
    # Create SUMO configuration
    config_xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<configuration xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="http://sumo.dlr.de/xsd/sumoConfiguration.xsd">
    <input>
        <net-file value="replicated_network.net.xml" />
        <route-files value="replicated_routes.rou.xml" />
    </input>
    <time>
        <begin value="0" />
        <end value="3600" />
    </time>
    <traci_server>
        <remote-port value="8813" />
    </traci_server>
</configuration>"""
    
    # Save files
    with open('replicated_network.net.xml', 'w') as f:
        f.write(network_xml)
    
    with open('replicated_routes.rou.xml', 'w') as f:
        f.write(routes_xml)
    
    with open('replicated_traffic.sumocfg', 'w') as f:
        f.write(config_xml)
    
    print("✅ SUMO files created successfully!")
    print(f"   📁 Network: replicated_network.net.xml")
    print(f"   🛣️ Routes: replicated_routes.rou.xml")
    print(f"   ⚙️ Config: replicated_traffic.sumocfg")
    print(f"   🚗 Vehicles: {vehicle_count}")

def main():
    """Main function to analyze video and create SUMO simulation"""
    print("🎬 Real Traffic Video Analysis & SUMO Replication")
    print("=" * 60)
    
    video_path = "Traffic_videos/stock-footage-drone-shot-way-intersection.webm"
    
    if not os.path.exists(video_path):
        print(f"❌ Video file not found: {video_path}")
        return
    
    # Analyze video
    analyzer = TrafficVideoAnalyzer(video_path)
    if analyzer.analyze_video():
        analyzer.save_analysis()
        
        # Create SUMO simulation
        create_sumo_from_analysis()
        
        print("\n🎉 Video analysis and SUMO replication completed!")
        print("🚀 Ready to run AI-controlled simulation!")
    else:
        print("❌ Video analysis failed")

if __name__ == "__main__":
    main()
