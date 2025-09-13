"""
Real Traffic Data Processor
Processes real traffic video with YOLO + DeepSORT/ByteTrack for accurate SUMO replication
"""

import cv2
import numpy as np
from ultralytics import YOLO
import torch
from typing import Dict, List, Optional, Tuple
import logging
from datetime import datetime
import json
import os

# DeepSORT imports (you'll need to install: pip install deep-sort-realtime)
try:
    from deep_sort_realtime import DeepSort
    DEEPSORT_AVAILABLE = True
except ImportError:
    DEEPSORT_AVAILABLE = False
    print("DeepSORT not available. Install with: pip install deep-sort-realtime")

logger = logging.getLogger(__name__)

class RealTrafficProcessor:
    def __init__(self, model_path: str = "yolov8n.pt", tracker_type: str = "deepsort"):
        """
        Initialize real traffic processor with YOLO + tracking
        
        Args:
            model_path: Path to YOLO model weights
            tracker_type: "deepsort" or "bytetrack"
        """
        self.model = YOLO(model_path)
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model.to(self.device)
        
        # Initialize tracker
        self.tracker_type = tracker_type
        if tracker_type == "deepsort" and DEEPSORT_AVAILABLE:
            self.tracker = DeepSort(
                max_age=50,
                n_init=3,
                max_cosine_distance=0.2,
                nn_budget=100
            )
        else:
            self.tracker = None
            logger.warning("DeepSORT not available, using simple tracking")
        
        # Vehicle classes for traffic
        self.vehicle_classes = {
            2: 'car',
            3: 'motorcycle', 
            5: 'bus',
            7: 'truck'
        }
        
        # Tracking data
        self.tracked_vehicles = {}
        self.vehicle_trajectories = {}
        self.frame_count = 0
        
        # Camera calibration (you'll need to calibrate your camera)
        self.camera_matrix = None
        self.dist_coeffs = None
        self.calibrated = False
        
    def calibrate_camera(self, calibration_images: List[np.ndarray] = None):
        """
        Calibrate camera for accurate world coordinates
        
        Args:
            calibration_images: List of calibration images with known patterns
        """
        # This is a simplified calibration
        # In production, use proper camera calibration with chessboard patterns
        
        # Default camera parameters (you should replace with your camera's actual parameters)
        self.camera_matrix = np.array([
            [1000, 0, 320],
            [0, 1000, 240],
            [0, 0, 1]
        ], dtype=np.float32)
        
        self.dist_coeffs = np.zeros((4, 1))
        self.calibrated = True
        
        logger.info("Camera calibration completed (using default parameters)")
    
    def pixel_to_world(self, pixel_point: Tuple[int, int], depth: float = 1.0) -> Tuple[float, float]:
        """
        Convert pixel coordinates to world coordinates
        
        Args:
            pixel_point: (x, y) pixel coordinates
            depth: Estimated depth (distance from camera)
            
        Returns:
            (x, y) world coordinates in meters
        """
        if not self.calibrated:
            # Use simple scaling if not calibrated
            scale_factor = 0.1  # meters per pixel (adjust based on your camera setup)
            world_x = (pixel_point[0] - 320) * scale_factor
            world_y = (pixel_point[1] - 240) * scale_factor
            return world_x, world_y
        
        # Proper camera calibration conversion
        pixel_coords = np.array([[pixel_point]], dtype=np.float32)
        undistorted = cv2.undistortPoints(pixel_coords, self.camera_matrix, self.dist_coeffs)
        
        # Convert to world coordinates (simplified)
        world_x = undistorted[0][0][0] * depth
        world_y = undistorted[0][0][1] * depth
        
        return world_x, world_y
    
    def detect_vehicles(self, frame: np.ndarray) -> List[Dict]:
        """
        Detect vehicles in frame using YOLO
        
        Args:
            frame: Input video frame
            
        Returns:
            List of detected vehicles with bounding boxes
        """
        try:
            results = self.model(
                frame, 
                conf=0.5,
                classes=list(self.vehicle_classes.keys()),
                verbose=False
            )
            
            detections = []
            for result in results:
                boxes = result.boxes
                if boxes is not None:
                    for box in boxes:
                        x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                        conf = box.conf[0].cpu().numpy()
                        cls = int(box.cls[0].cpu().numpy())
                        
                        # Calculate center point
                        center_x = (x1 + x2) / 2
                        center_y = (y1 + y2) / 2
                        
                        # Convert to world coordinates
                        world_x, world_y = self.pixel_to_world((center_x, center_y))
                        
                        detection = {
                            'bbox': [int(x1), int(y1), int(x2), int(y2)],
                            'center': [center_x, center_y],
                            'world_center': [world_x, world_y],
                            'confidence': float(conf),
                            'class_id': cls,
                            'class_name': self.vehicle_classes[cls],
                            'timestamp': self.frame_count / 30.0,  # Assuming 30 FPS
                            'frame_id': self.frame_count
                        }
                        
                        detections.append(detection)
            
            return detections
            
        except Exception as e:
            logger.error(f"Vehicle detection error: {e}")
            return []
    
    def track_vehicles(self, detections: List[Dict]) -> List[Dict]:
        """
        Track vehicles across frames using DeepSORT/ByteTrack
        
        Args:
            detections: Current frame detections
            
        Returns:
            List of tracked vehicles with IDs
        """
        if not self.tracker:
            return self._simple_tracking(detections)
        
        try:
            # Prepare detections for DeepSORT
            detections_for_tracker = []
            for det in detections:
                bbox = det['bbox']
                confidence = det['confidence']
                class_id = det['class_id']
                
                # DeepSORT expects [x1, y1, w, h, confidence, class_id]
                detections_for_tracker.append([
                    bbox[0], bbox[1], bbox[2] - bbox[0], bbox[3] - bbox[1],
                    confidence, class_id
                ])
            
            # Update tracker
            tracks = self.tracker.update_tracks(detections_for_tracker, frame=None)
            
            # Process tracked vehicles
            tracked_vehicles = []
            for track in tracks:
                if not track.is_confirmed():
                    continue
                
                track_id = track.track_id
                bbox = track.to_tlwh()
                
                # Convert back to our format
                x1, y1, w, h = bbox
                center_x = x1 + w / 2
                center_y = y1 + h / 2
                
                # Convert to world coordinates
                world_x, world_y = self.pixel_to_world((center_x, center_y))
                
                tracked_vehicle = {
                    'track_id': track_id,
                    'bbox': [int(x1), int(y1), int(x1 + w), int(y1 + h)],
                    'center': [center_x, center_y],
                    'world_center': [world_x, world_y],
                    'class_name': 'vehicle',  # DeepSORT doesn't preserve class
                    'timestamp': self.frame_count / 30.0,
                    'frame_id': self.frame_count
                }
                
                tracked_vehicles.append(tracked_vehicle)
                
                # Update trajectory
                if track_id not in self.vehicle_trajectories:
                    self.vehicle_trajectories[track_id] = []
                
                self.vehicle_trajectories[track_id].append({
                    'frame_id': self.frame_count,
                    'world_center': [world_x, world_y],
                    'timestamp': self.frame_count / 30.0
                })
            
            return tracked_vehicles
            
        except Exception as e:
            logger.error(f"Vehicle tracking error: {e}")
            return self._simple_tracking(detections)
    
    def _simple_tracking(self, detections: List[Dict]) -> List[Dict]:
        """Fallback simple tracking if DeepSORT not available"""
        tracked_vehicles = []
        
        for i, detection in enumerate(detections):
            # Simple ID assignment
            track_id = f"vehicle_{i}_{self.frame_count}"
            
            tracked_vehicle = {
                'track_id': track_id,
                'bbox': detection['bbox'],
                'center': detection['center'],
                'world_center': detection['world_center'],
                'class_name': detection['class_name'],
                'timestamp': detection['timestamp'],
                'frame_id': self.frame_count
            }
            
            tracked_vehicles.append(tracked_vehicle)
            
            # Update trajectory
            if track_id not in self.vehicle_trajectories:
                self.vehicle_trajectories[track_id] = []
            
            self.vehicle_trajectories[track_id].append({
                'frame_id': self.frame_count,
                'world_center': detection['world_center'],
                'timestamp': detection['timestamp']
            })
        
        return tracked_vehicles
    
    def process_video(self, video_path: str, output_dir: str = "processed_traffic") -> Dict:
        """
        Process entire video and extract vehicle trajectories
        
        Args:
            video_path: Path to input video file
            output_dir: Output directory for processed data
            
        Returns:
            Dictionary containing processed traffic data
        """
        try:
            os.makedirs(output_dir, exist_ok=True)
            
            # Open video
            cap = cv2.VideoCapture(video_path)
            if not cap.isOpened():
                raise ValueError(f"Could not open video: {video_path}")
            
            # Get video properties
            fps = cap.get(cv2.CAP_PROP_FPS)
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            
            logger.info(f"Processing video: {video_path}")
            logger.info(f"FPS: {fps}, Frames: {total_frames}, Resolution: {width}x{height}")
            
            # Calibrate camera
            self.calibrate_camera()
            
            # Process frames
            all_tracked_vehicles = []
            frame_data = []
            
            self.frame_count = 0
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                
                # Detect vehicles
                detections = self.detect_vehicles(frame)
                
                # Track vehicles
                tracked_vehicles = self.track_vehicles(detections)
                
                # Store frame data
                frame_info = {
                    'frame_id': self.frame_count,
                    'timestamp': self.frame_count / fps,
                    'detections': detections,
                    'tracked_vehicles': tracked_vehicles
                }
                frame_data.append(frame_info)
                all_tracked_vehicles.extend(tracked_vehicles)
                
                self.frame_count += 1
                
                if self.frame_count % 100 == 0:
                    logger.info(f"Processed {self.frame_count}/{total_frames} frames")
            
            cap.release()
            
            # Generate SUMO-compatible data
            sumo_data = self._generate_sumo_data(all_tracked_vehicles, frame_data)
            
            # Save processed data
            self._save_processed_data(sumo_data, output_dir)
            
            logger.info(f"Video processing completed. Processed {self.frame_count} frames")
            
            return {
                'success': True,
                'total_frames': self.frame_count,
                'total_vehicles': len(self.vehicle_trajectories),
                'fps': fps,
                'resolution': [width, height],
                'sumo_data': sumo_data,
                'output_dir': output_dir
            }
            
        except Exception as e:
            logger.error(f"Video processing error: {e}")
            return {'success': False, 'error': str(e)}
    
    def _generate_sumo_data(self, tracked_vehicles: List[Dict], frame_data: List[Dict]) -> Dict:
        """
        Generate SUMO-compatible data from tracked vehicles
        
        Args:
            tracked_vehicles: All tracked vehicles
            frame_data: Frame-by-frame data
            
        Returns:
            SUMO-compatible data structure
        """
        try:
            # Group vehicles by track ID
            vehicles_by_track = {}
            for vehicle in tracked_vehicles:
                track_id = vehicle['track_id']
                if track_id not in vehicles_by_track:
                    vehicles_by_track[track_id] = []
                vehicles_by_track[track_id].append(vehicle)
            
            # Generate vehicle routes for SUMO
            sumo_vehicles = []
            for track_id, vehicle_frames in vehicles_by_track.items():
                if len(vehicle_frames) < 5:  # Skip short tracks
                    continue
                
                # Sort by frame ID
                vehicle_frames.sort(key=lambda x: x['frame_id'])
                
                # Extract trajectory
                trajectory = []
                for frame in vehicle_frames:
                    world_center = frame['world_center']
                    trajectory.append({
                        'x': world_center[0],
                        'y': world_center[1],
                        'timestamp': frame['timestamp']
                    })
                
                # Create SUMO vehicle
                sumo_vehicle = {
                    'id': track_id,
                    'type': self._map_vehicle_type(vehicle_frames[0]['class_name']),
                    'trajectory': trajectory,
                    'start_time': vehicle_frames[0]['timestamp'],
                    'end_time': vehicle_frames[-1]['timestamp'],
                    'duration': vehicle_frames[-1]['timestamp'] - vehicle_frames[0]['timestamp']
                }
                
                sumo_vehicles.append(sumo_vehicle)
            
            # Generate traffic statistics
            stats = self._calculate_traffic_stats(frame_data)
            
            return {
                'vehicles': sumo_vehicles,
                'statistics': stats,
                'total_vehicles': len(sumo_vehicles),
                'duration': max([v['end_time'] for v in sumo_vehicles]) if sumo_vehicles else 0
            }
            
        except Exception as e:
            logger.error(f"SUMO data generation error: {e}")
            return {}
    
    def _map_vehicle_type(self, class_name: str) -> str:
        """Map vehicle class to SUMO vehicle type"""
        type_mapping = {
            'car': 'passenger',
            'motorcycle': 'motorcycle',
            'bus': 'bus',
            'truck': 'truck'
        }
        return type_mapping.get(class_name, 'passenger')
    
    def _calculate_traffic_stats(self, frame_data: List[Dict]) -> Dict:
        """Calculate traffic statistics"""
        try:
            total_vehicles = 0
            vehicle_counts_per_frame = []
            
            for frame in frame_data:
                vehicle_count = len(frame['tracked_vehicles'])
                vehicle_counts_per_frame.append(vehicle_count)
                total_vehicles += vehicle_count
            
            return {
                'total_vehicles': total_vehicles,
                'average_vehicles_per_frame': np.mean(vehicle_counts_per_frame),
                'max_vehicles_per_frame': max(vehicle_counts_per_frame),
                'min_vehicles_per_frame': min(vehicle_counts_per_frame),
                'total_frames': len(frame_data)
            }
            
        except Exception as e:
            logger.error(f"Statistics calculation error: {e}")
            return {}
    
    def _save_processed_data(self, sumo_data: Dict, output_dir: str):
        """Save processed data to files"""
        try:
            # Save SUMO data
            sumo_file = os.path.join(output_dir, 'sumo_traffic_data.json')
            with open(sumo_file, 'w') as f:
                json.dump(sumo_data, f, indent=2, default=str)
            
            # Save vehicle trajectories
            trajectories_file = os.path.join(output_dir, 'vehicle_trajectories.json')
            with open(trajectories_file, 'w') as f:
                json.dump(self.vehicle_trajectories, f, indent=2, default=str)
            
            logger.info(f"Processed data saved to: {output_dir}")
            
        except Exception as e:
            logger.error(f"Data saving error: {e}")

# Example usage
if __name__ == "__main__":
    # Initialize processor
    processor = RealTrafficProcessor(
        model_path="yolov8n.pt",
        tracker_type="deepsort"
    )
    
    # Process video
    result = processor.process_video(
        video_path="traffic_video.mp4",
        output_dir="processed_traffic"
    )
    
    if result['success']:
        print(f"✅ Processing completed!")
        print(f"📊 Total vehicles: {result['total_vehicles']}")
        print(f"🎬 Total frames: {result['total_frames']}")
        print(f"📁 Output directory: {result['output_dir']}")
    else:
        print(f"❌ Processing failed: {result['error']}")
