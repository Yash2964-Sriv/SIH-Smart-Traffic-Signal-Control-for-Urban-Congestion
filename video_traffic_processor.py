"""
Video Traffic Data Processor
Processes video files to extract vehicle data and replicate in SUMO
"""

import cv2
import numpy as np
import json
import xml.etree.ElementTree as ET
from datetime import datetime
import os
import sys
from pathlib import Path
import time
from typing import List, Dict, Tuple, Optional
import math

# Add the current directory to Python path for imports
sys.path.append(str(Path(__file__).parent))

try:
    from ultralytics import YOLO
    YOLO_AVAILABLE = True
except ImportError:
    YOLO_AVAILABLE = False
    print("⚠️  YOLO not available. Install with: pip install ultralytics")

class VideoTrafficProcessor:
    def __init__(self, video_path: str, output_dir: str = "video_output"):
        """
        Initialize video traffic processor
        
        Args:
            video_path: Path to input video file
            output_dir: Directory to save output files
        """
        self.video_path = video_path
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # Initialize video capture
        self.cap = cv2.VideoCapture(video_path)
        if not self.cap.isOpened():
            raise ValueError(f"Could not open video file: {video_path}")
        
        # Get video properties
        self.fps = int(self.cap.get(cv2.CAP_PROP_FPS))
        self.frame_width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.frame_height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.total_frames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
        self.duration = self.total_frames / self.fps
        
        print(f"📹 Video loaded:")
        print(f"   Resolution: {self.frame_width}x{self.frame_height}")
        print(f"   FPS: {self.fps}")
        print(f"   Duration: {self.duration:.2f} seconds")
        print(f"   Total frames: {self.total_frames}")
        
        # Initialize YOLO model
        self.yolo_model = None
        self.yolo_available = YOLO_AVAILABLE
        if self.yolo_available:
            try:
                self.yolo_model = YOLO('yolov8n.pt')  # Load nano model for speed
                print("✅ YOLO model loaded successfully")
            except Exception as e:
                print(f"⚠️  Could not load YOLO model: {e}")
                self.yolo_available = False
        
        # Vehicle tracking data
        self.vehicles = []
        self.frame_data = []
        self.current_frame = 0
        
        # Lane definitions (adjust based on your video)
        self.lanes = self._define_lanes()
        
    def _define_lanes(self) -> Dict[str, Dict]:
        """Define lane regions in the video frame"""
        # Define lane regions as polygons (adjust coordinates based on your video)
        center_x, center_y = self.frame_width // 2, self.frame_height // 2
        lane_width = 100
        
        lanes = {
            'north': {
                'name': 'Northbound',
                'polygon': np.array([
                    [center_x - lane_width//2, 0],
                    [center_x + lane_width//2, 0],
                    [center_x + lane_width//3, center_y - 50],
                    [center_x - lane_width//3, center_y - 50]
                ]),
                'direction': 'north'
            },
            'south': {
                'name': 'Southbound', 
                'polygon': np.array([
                    [center_x - lane_width//3, center_y + 50],
                    [center_x + lane_width//3, center_y + 50],
                    [center_x + lane_width//2, self.frame_height],
                    [center_x - lane_width//2, self.frame_height]
                ]),
                'direction': 'south'
            },
            'east': {
                'name': 'Eastbound',
                'polygon': np.array([
                    [center_x + 50, center_y - lane_width//3],
                    [self.frame_width, center_y - lane_width//2],
                    [self.frame_width, center_y + lane_width//2],
                    [center_x + 50, center_y + lane_width//3]
                ]),
                'direction': 'east'
            },
            'west': {
                'name': 'Westbound',
                'polygon': np.array([
                    [center_x - 50, center_y + lane_width//3],
                    [0, center_y + lane_width//2],
                    [0, center_y - lane_width//2],
                    [center_x - 50, center_y - lane_width//3]
                ]),
                'direction': 'west'
            }
        }
        return lanes
    
    def detect_vehicles_yolo(self, frame: np.ndarray) -> List[Dict]:
        """Detect vehicles in frame using YOLO"""
        if not self.yolo_model:
            return []
        
        try:
            results = self.yolo_model(frame, verbose=False)
            vehicles = []
            
            for result in results:
                boxes = result.boxes
                if boxes is not None:
                    for box in boxes:
                        # Get bounding box coordinates
                        x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                        confidence = box.conf[0].cpu().numpy()
                        class_id = int(box.cls[0].cpu().numpy())
                        
                        # Filter for vehicles (car, truck, bus, motorcycle)
                        vehicle_classes = [2, 3, 5, 7]  # COCO class IDs for vehicles
                        if class_id in vehicle_classes and confidence > 0.5:
                            center_x = (x1 + x2) / 2
                            center_y = (y1 + y2) / 2
                            
                            # Determine vehicle type
                            vehicle_type = 'car'
                            if class_id == 2:  # car
                                vehicle_type = 'car'
                            elif class_id == 3:  # motorcycle
                                vehicle_type = 'motorcycle'
                            elif class_id == 5:  # bus
                                vehicle_type = 'bus'
                            elif class_id == 7:  # truck
                                vehicle_type = 'truck'
                            
                            vehicles.append({
                                'bbox': [int(x1), int(y1), int(x2), int(y2)],
                                'center': [int(center_x), int(center_y)],
                                'confidence': float(confidence),
                                'class_id': class_id,
                                'vehicle_type': vehicle_type
                            })
            
            return vehicles
            
        except Exception as e:
            print(f"⚠️  YOLO detection error: {e}")
            return []
    
    def detect_vehicles_opencv(self, frame: np.ndarray) -> List[Dict]:
        """Fallback vehicle detection using OpenCV (motion detection)"""
        # Convert to grayscale
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Apply Gaussian blur
        blurred = cv2.GaussianBlur(gray, (21, 21), 0)
        
        # Initialize background subtractor
        if not hasattr(self, 'bg_subtractor'):
            self.bg_subtractor = cv2.createBackgroundSubtractorMOG2(detectShadows=True)
        
        # Apply background subtraction
        fg_mask = self.bg_subtractor.apply(blurred)
        
        # Find contours
        contours, _ = cv2.findContours(fg_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        vehicles = []
        for contour in contours:
            # Filter by area
            area = cv2.contourArea(contour)
            if area > 200:  # Lower minimum area threshold for better detection
                # Get bounding box
                x, y, w, h = cv2.boundingRect(contour)
                
                # Filter by aspect ratio (vehicles are typically wider than tall)
                aspect_ratio = w / h
                if 0.3 < aspect_ratio < 4.0:  # More flexible aspect ratio
                    center_x = x + w // 2
                    center_y = y + h // 2
                    
                    # Additional size filtering
                    if w > 20 and h > 10:  # Minimum size requirements
                        vehicles.append({
                            'bbox': [x, y, x + w, y + h],
                            'center': [center_x, center_y],
                            'confidence': 0.7,  # Default confidence for motion detection
                            'class_id': 2,  # Default to car
                            'vehicle_type': 'car'
                        })
        
        return vehicles
    
    def assign_vehicle_to_lane(self, vehicle: Dict) -> Optional[str]:
        """Assign vehicle to a lane based on its position"""
        center_x, center_y = vehicle['center']
        point = np.array([center_x, center_y])
        
        for lane_id, lane_data in self.lanes.items():
            if cv2.pointPolygonTest(lane_data['polygon'], (center_x, center_y), False) >= 0:
                return lane_id
        
        return None
    
    def track_vehicles(self, vehicles: List[Dict]) -> List[Dict]:
        """Simple vehicle tracking using position-based matching"""
        tracked_vehicles = []
        
        for vehicle in vehicles:
            # Find closest existing vehicle
            min_distance = float('inf')
            closest_vehicle = None
            
            for existing_vehicle in self.vehicles:
                if existing_vehicle['tracking_id'] is not None:
                    # Calculate distance
                    dist = math.sqrt(
                        (vehicle['center'][0] - existing_vehicle['center'][0])**2 +
                        (vehicle['center'][1] - existing_vehicle['center'][1])**2
                    )
                    
                    if dist < min_distance and dist < 50:  # Max distance threshold
                        min_distance = dist
                        closest_vehicle = existing_vehicle
            
            if closest_vehicle:
                # Update existing vehicle
                closest_vehicle['center'] = vehicle['center']
                closest_vehicle['bbox'] = vehicle['bbox']
                closest_vehicle['last_seen'] = self.current_frame
                tracked_vehicles.append(closest_vehicle)
            else:
                # Create new vehicle
                new_vehicle = {
                    'tracking_id': len(self.vehicles),
                    'center': vehicle['center'],
                    'bbox': vehicle['bbox'],
                    'confidence': vehicle['confidence'],
                    'vehicle_type': vehicle['vehicle_type'],
                    'lane': self.assign_vehicle_to_lane(vehicle),
                    'first_seen': self.current_frame,
                    'last_seen': self.current_frame,
                    'positions': [vehicle['center']]
                }
                self.vehicles.append(new_vehicle)
                tracked_vehicles.append(new_vehicle)
        
        # Remove vehicles not seen for too long
        self.vehicles = [v for v in self.vehicles if self.current_frame - v['last_seen'] < 30]
        
        return tracked_vehicles
    
    def process_video(self, max_frames: Optional[int] = None, show_preview: bool = True) -> Dict:
        """Process the entire video and extract vehicle data"""
        print(f"\n🎬 Processing video: {self.video_path}")
        print(f"   Max frames: {max_frames or self.total_frames}")
        print(f"   Show preview: {show_preview}")
        
        frame_count = 0
        start_time = time.time()
        
        try:
            while True:
                ret, frame = self.cap.read()
                if not ret:
                    break
                
                if max_frames and frame_count >= max_frames:
                    break
                
                # Detect vehicles
                if self.yolo_available and self.yolo_model:
                    vehicles = self.detect_vehicles_yolo(frame)
                else:
                    vehicles = self.detect_vehicles_opencv(frame)
                
                # Track vehicles
                tracked_vehicles = self.track_vehicles(vehicles)
                
                # Store frame data
                frame_data = {
                    'frame_number': frame_count,
                    'timestamp': frame_count / self.fps,
                    'vehicles': tracked_vehicles
                }
                self.frame_data.append(frame_data)
                
                # Show preview
                if show_preview and frame_count % 10 == 0:  # Show every 10th frame
                    preview_frame = frame.copy()
                    
                    # Draw lane regions
                    for lane_id, lane_data in self.lanes.items():
                        cv2.polylines(preview_frame, [lane_data['polygon']], True, (0, 255, 0), 2)
                        cv2.putText(preview_frame, lane_data['name'], 
                                  (lane_data['polygon'][0][0], lane_data['polygon'][0][1] - 10),
                                  cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                    
                    # Draw vehicles
                    for vehicle in tracked_vehicles:
                        x1, y1, x2, y2 = vehicle['bbox']
                        cv2.rectangle(preview_frame, (x1, y1), (x2, y2), (0, 0, 255), 2)
                        cv2.putText(preview_frame, f"{vehicle['vehicle_type']} {vehicle['tracking_id']}", 
                                  (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)
                    
                    # Show frame
                    cv2.imshow('Video Processing', preview_frame)
                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        break
                
                frame_count += 1
                self.current_frame = frame_count
                
                # Progress update
                if frame_count % 100 == 0:
                    progress = (frame_count / (max_frames or self.total_frames)) * 100
                    elapsed = time.time() - start_time
                    fps = frame_count / elapsed
                    print(f"   Progress: {progress:.1f}% | FPS: {fps:.1f} | Vehicles: {len(self.vehicles)}")
        
        except KeyboardInterrupt:
            print("\n⏹️  Processing stopped by user")
        
        finally:
            self.cap.release()
            cv2.destroyAllWindows()
        
        # Calculate processing statistics
        processing_time = time.time() - start_time
        total_vehicles = len(self.vehicles)
        
        # Store processing stats
        self.frames_processed = frame_count
        self.processing_time = processing_time
        
        print(f"\n✅ Video processing completed:")
        print(f"   Frames processed: {frame_count}")
        print(f"   Processing time: {processing_time:.2f} seconds")
        print(f"   Total vehicles detected: {total_vehicles}")
        print(f"   Average FPS: {frame_count / processing_time:.1f}")
        
        return {
            'frames_processed': frame_count,
            'processing_time': processing_time,
            'total_vehicles': total_vehicles,
            'fps': frame_count / processing_time
        }
    
    def generate_sumo_data(self) -> Dict[str, str]:
        """Generate SUMO network and route files from video data"""
        print(f"\n🔄 Generating SUMO data from video analysis...")
        
        # Create SUMO network
        network_file = self.output_dir / "video_intersection.net.xml"
        self._create_sumo_network(network_file)
        
        # Create SUMO routes
        routes_file = self.output_dir / "video_routes.rou.xml"
        self._create_sumo_routes(routes_file)
        
        # Create SUMO configuration
        config_file = self.output_dir / "video_simulation.sumocfg"
        self._create_sumo_config(config_file, network_file.name, routes_file.name)
        
        print(f"✅ SUMO files generated:")
        print(f"   Network: {network_file}")
        print(f"   Routes: {routes_file}")
        print(f"   Config: {config_file}")
        
        return {
            'network': str(network_file),
            'routes': str(routes_file),
            'config': str(config_file)
        }
    
    def _create_sumo_network(self, output_file: str):
        """Create SUMO network file"""
        # Simple 4-way intersection network
        network_xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<net version="1.9" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="http://sumo.dlr.de/xsd/net_file.xsd">
    <location netOffset="0.00,0.00" convBoundary="0.00,0.00,200.00,200.00" origBoundary="-180.00,-90.00,180.00,90.00" projParameter="+proj=longlat +ellps=WGS84 +datum=WGS84 +no_defs"/>
    
    <!-- Nodes (Junctions) -->
    <junction id="center" type="traffic_light" x="100.0" y="100.0" incLanes="" intLanes="" shape="100.0,100.0"/>
    <junction id="north_end" type="priority" x="100.0" y="0.0" incLanes="" intLanes="" shape="100.0,0.0"/>
    <junction id="south_end" type="priority" x="100.0" y="200.0" incLanes="" intLanes="" shape="100.0,200.0"/>
    <junction id="east_end" type="priority" x="200.0" y="100.0" incLanes="" intLanes="" shape="200.0,100.0"/>
    <junction id="west_end" type="priority" x="0.0" y="100.0" incLanes="" intLanes="" shape="0.0,100.0"/>
    
    <!-- Edges (Roads) -->
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
    
    <!-- Traffic Light Logic -->
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
        
        with open(output_file, 'w') as f:
            f.write(network_xml)
    
    def _create_sumo_routes(self, output_file: str):
        """Create SUMO routes file from video data"""
        # Group vehicles by lane and departure time
        lane_vehicles = {'north': [], 'south': [], 'east': [], 'west': []}
        
        for vehicle in self.vehicles:
            if vehicle['lane'] in lane_vehicles:
                lane_vehicles[vehicle['lane']].append(vehicle)
        
        # Create routes XML
        routes_xml = '<?xml version="1.0" encoding="UTF-8"?>\n<routes>\n'
        
        # Vehicle types
        routes_xml += '    <vType id="car" accel="2.6" decel="4.5" sigma="0.5" length="5" maxSpeed="50"/>\n'
        routes_xml += '    <vType id="truck" accel="1.2" decel="3.5" sigma="0.3" length="12" maxSpeed="30"/>\n'
        routes_xml += '    <vType id="bus" accel="1.0" decel="3.0" sigma="0.2" length="15" maxSpeed="25"/>\n'
        routes_xml += '    <vType id="motorcycle" accel="3.0" decel="6.0" sigma="0.8" length="2" maxSpeed="60"/>\n'
        
        # Routes
        routes_xml += '    <route id="north_route" edges="north"/>\n'
        routes_xml += '    <route id="south_route" edges="south"/>\n'
        routes_xml += '    <route id="east_route" edges="east"/>\n'
        routes_xml += '    <route id="west_route" edges="west"/>\n'
        
        # Vehicles
        vehicle_id = 0
        for lane, vehicles in lane_vehicles.items():
            for vehicle in vehicles:
                # Calculate departure time based on first appearance
                depart_time = vehicle['first_seen'] / self.fps
                
                # Map vehicle type to SUMO type
                vehicle_type = vehicle['vehicle_type']
                if vehicle_type == 'truck':
                    vtype = 'truck'
                elif vehicle_type == 'bus':
                    vtype = 'bus'
                elif vehicle_type == 'motorcycle':
                    vtype = 'motorcycle'
                else:
                    vtype = 'car'
                
                route_id = f"{lane}_route"
                routes_xml += f'    <vehicle id="veh_{vehicle_id}" type="{vtype}" depart="{depart_time:.1f}" route="{route_id}"/>\n'
                vehicle_id += 1
        
        routes_xml += '</routes>'
        
        with open(output_file, 'w') as f:
            f.write(routes_xml)
    
    def _create_sumo_config(self, output_file: str, network_file: str, routes_file: str):
        """Create SUMO configuration file"""
        config_xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<configuration xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="http://sumo.dlr.de/xsd/sumoConfiguration.xsd">
    <input>
        <net-file value="{network_file}"/>
        <route-files value="{routes_file}"/>
    </input>
    <time>
        <begin value="0"/>
        <end value="{int(self.duration)}"/>
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
        <fcd-output value="video_simulation_fcd.xml"/>
        <netstate-dump value="video_simulation_netstate.xml"/>
    </output>
</configuration>"""
        
        with open(output_file, 'w') as f:
            f.write(config_xml)
    
    def save_analysis_data(self) -> str:
        """Save analysis data to JSON file"""
        analysis_data = {
            'video_info': {
                'path': self.video_path,
                'fps': self.fps,
                'resolution': [self.frame_width, self.frame_height],
                'duration': self.duration,
                'total_frames': self.total_frames
            },
            'processing_stats': {
                'frames_processed': len(self.frame_data),
                'total_vehicles': len(self.vehicles),
                'lanes_detected': list(self.lanes.keys())
            },
            'vehicles': self.vehicles,
            'frame_data': self.frame_data
        }
        
        output_file = self.output_dir / "video_analysis.json"
        with open(output_file, 'w') as f:
            json.dump(analysis_data, f, indent=2)
        
        print(f"📊 Analysis data saved to: {output_file}")
        return str(output_file)

def main():
    """Main function to process video and generate SUMO data"""
    print("🎥 Video Traffic Data Processor")
    print("=" * 40)
    
    # Check if video file exists
    video_path = input("Enter path to video file: ").strip()
    if not os.path.exists(video_path):
        print(f"❌ Video file not found: {video_path}")
        return
    
    # Create processor
    try:
        processor = VideoTrafficProcessor(video_path)
        
        # Process video
        max_frames = input("Max frames to process (Enter for all): ").strip()
        max_frames = int(max_frames) if max_frames else None
        
        show_preview = input("Show preview? (y/n): ").lower().strip() == 'y'
        
        # Process video
        stats = processor.process_video(max_frames=max_frames, show_preview=show_preview)
        
        # Generate SUMO data
        sumo_files = processor.generate_sumo_data()
        
        # Save analysis data
        analysis_file = processor.save_analysis_data()
        
        print(f"\n🎉 Video processing completed successfully!")
        print(f"📁 Output directory: {processor.output_dir}")
        print(f"📊 Analysis file: {analysis_file}")
        print(f"🚦 SUMO files: {list(sumo_files.values())}")
        
        # Ask if user wants to run SUMO simulation
        run_sumo = input("\nRun SUMO simulation? (y/n): ").lower().strip() == 'y'
        if run_sumo:
            config_file = sumo_files['config']
            print(f"\n🚀 Running SUMO simulation with: {config_file}")
            print("   Use Ctrl+C to stop the simulation")
            
            # Run SUMO
            import subprocess
            try:
                subprocess.run([
                    r"C:\Program Files (x86)\Eclipse\Sumo\bin\sumo.exe",
                    "-c", config_file
                ], cwd=processor.output_dir)
            except KeyboardInterrupt:
                print("\n⏹️  SUMO simulation stopped")
            except Exception as e:
                print(f"❌ Error running SUMO: {e}")
    
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
