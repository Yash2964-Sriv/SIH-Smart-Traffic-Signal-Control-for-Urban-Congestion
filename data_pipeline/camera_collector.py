"""
Camera Data Collector
Handles real-time CCTV feed processing and vehicle detection
"""

import cv2
import numpy as np
from ultralytics import YOLO
import asyncio
import websockets
import json
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import logging

logger = logging.getLogger(__name__)

class CameraCollector:
    def __init__(self, camera_url: str, model_path: str = "yolov8n.pt"):
        """
        Initialize camera collector with YOLO model
        
        Args:
            camera_url: RTSP/HTTP URL for camera feed
            model_path: Path to YOLO model weights
        """
        self.camera_url = camera_url
        self.model = YOLO(model_path)
        self.cap = None
        self.is_running = False
        
        # Vehicle detection classes (COCO dataset)
        self.vehicle_classes = [2, 3, 5, 7]  # car, motorcycle, bus, truck
        
        # Detection tracking
        self.detection_history = []
        self.max_history = 100
        
    async def connect_camera(self) -> bool:
        """Connect to camera feed"""
        try:
            self.cap = cv2.VideoCapture(self.camera_url)
            if not self.cap.isOpened():
                logger.error(f"Failed to connect to camera: {self.camera_url}")
                return False
            
            # Set camera properties
            self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
            self.cap.set(cv2.CAP_PROP_FPS, 30)
            
            logger.info(f"Connected to camera: {self.camera_url}")
            return True
        except Exception as e:
            logger.error(f"Camera connection error: {e}")
            return False
    
    def detect_vehicles(self, frame: np.ndarray) -> List[Dict]:
        """
        Detect vehicles in frame using YOLO
        
        Args:
            frame: Input video frame
            
        Returns:
            List of detected vehicles with bounding boxes and confidence
        """
        try:
            results = self.model(frame, conf=0.5, classes=self.vehicle_classes)
            
            detections = []
            for result in results:
                boxes = result.boxes
                if boxes is not None:
                    for box in boxes:
                        x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                        conf = box.conf[0].cpu().numpy()
                        cls = int(box.cls[0].cpu().numpy())
                        
                        detections.append({
                            'bbox': [int(x1), int(y1), int(x2), int(y2)],
                            'confidence': float(conf),
                            'class': cls,
                            'class_name': self.model.names[cls],
                            'timestamp': datetime.now().isoformat()
                        })
            
            return detections
        except Exception as e:
            logger.error(f"Vehicle detection error: {e}")
            return []
    
    def track_vehicles(self, detections: List[Dict]) -> List[Dict]:
        """
        Track vehicles across frames using simple centroid tracking
        
        Args:
            detections: Current frame detections
            
        Returns:
            List of tracked vehicles with IDs
        """
        # Simple centroid tracking implementation
        # In production, use DeepSORT or ByteTrack for better tracking
        
        tracked_vehicles = []
        for detection in detections:
            # Calculate centroid
            x1, y1, x2, y2 = detection['bbox']
            centroid = [(x1 + x2) // 2, (y1 + y2) // 2]
            
            # Simple tracking: assign ID based on position
            vehicle_id = f"{detection['class_name']}_{centroid[0]}_{centroid[1]}"
            
            tracked_vehicle = {
                **detection,
                'vehicle_id': vehicle_id,
                'centroid': centroid,
                'speed': 0.0,  # Calculate from frame difference
                'direction': 'unknown'  # Calculate from movement
            }
            
            tracked_vehicles.append(tracked_vehicle)
        
        return tracked_vehicles
    
    def extract_traffic_metrics(self, tracked_vehicles: List[Dict]) -> Dict:
        """
        Extract traffic metrics from tracked vehicles
        
        Args:
            tracked_vehicles: List of tracked vehicles
            
        Returns:
            Dictionary of traffic metrics
        """
        if not tracked_vehicles:
            return {
                'vehicle_count': 0,
                'vehicle_density': 0.0,
                'average_speed': 0.0,
                'vehicle_types': {},
                'timestamp': datetime.now().isoformat()
            }
        
        # Count vehicles by type
        vehicle_types = {}
        speeds = []
        
        for vehicle in tracked_vehicles:
            vehicle_type = vehicle['class_name']
            vehicle_types[vehicle_type] = vehicle_types.get(vehicle_type, 0) + 1
            speeds.append(vehicle['speed'])
        
        return {
            'vehicle_count': len(tracked_vehicles),
            'vehicle_density': len(tracked_vehicles) / 100.0,  # Normalized density
            'average_speed': np.mean(speeds) if speeds else 0.0,
            'vehicle_types': vehicle_types,
            'timestamp': datetime.now().isoformat()
        }
    
    async def process_frame(self) -> Optional[Dict]:
        """
        Process single frame from camera
        
        Returns:
            Dictionary containing frame data and metrics
        """
        if not self.cap or not self.cap.isOpened():
            return None
        
        ret, frame = self.cap.read()
        if not ret:
            logger.warning("Failed to read frame from camera")
            return None
        
        # Detect vehicles
        detections = self.detect_vehicles(frame)
        
        # Track vehicles
        tracked_vehicles = self.track_vehicles(detections)
        
        # Extract metrics
        metrics = self.extract_traffic_metrics(tracked_vehicles)
        
        # Store in history
        self.detection_history.append({
            'frame': frame,
            'detections': detections,
            'tracked_vehicles': tracked_vehicles,
            'metrics': metrics
        })
        
        # Keep only recent history
        if len(self.detection_history) > self.max_history:
            self.detection_history.pop(0)
        
        return {
            'frame': frame,
            'detections': detections,
            'tracked_vehicles': tracked_vehicles,
            'metrics': metrics,
            'timestamp': datetime.now().isoformat()
        }
    
    async def start_collection(self, websocket_url: str = "ws://localhost:8000/ws/camera"):
        """
        Start continuous data collection and streaming
        
        Args:
            websocket_url: WebSocket URL for streaming data
        """
        if not await self.connect_camera():
            return
        
        self.is_running = True
        logger.info("Starting camera data collection...")
        
        try:
            async with websockets.connect(websocket_url) as websocket:
                while self.is_running:
                    frame_data = await self.process_frame()
                    if frame_data:
                        # Send data via WebSocket
                        await websocket.send(json.dumps({
                            'type': 'camera_data',
                            'data': frame_data
                        }))
                    
                    await asyncio.sleep(0.033)  # ~30 FPS
                    
        except Exception as e:
            logger.error(f"Camera collection error: {e}")
        finally:
            self.is_running = False
            if self.cap:
                self.cap.release()
    
    def stop_collection(self):
        """Stop data collection"""
        self.is_running = False
        if self.cap:
            self.cap.release()
        logger.info("Camera data collection stopped")
    
    def get_latest_metrics(self) -> Optional[Dict]:
        """Get latest traffic metrics"""
        if self.detection_history:
            return self.detection_history[-1]['metrics']
        return None
    
    def get_detection_history(self, limit: int = 10) -> List[Dict]:
        """Get recent detection history"""
        return self.detection_history[-limit:] if self.detection_history else []
