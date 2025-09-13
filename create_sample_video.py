"""
Create Sample Traffic Video
Generates a synthetic traffic video for testing the video processing system
"""

import cv2
import numpy as np
import random
import math
from pathlib import Path

def create_sample_traffic_video(output_path: str = "sample_traffic.mp4", duration: int = 30):
    """
    Create a sample traffic video with moving vehicles
    
    Args:
        output_path: Path to save the video
        duration: Duration in seconds
    """
    print(f"🎬 Creating sample traffic video: {output_path}")
    print(f"   Duration: {duration} seconds")
    
    # Video properties
    width, height = 800, 600
    fps = 30
    total_frames = duration * fps
    
    # Create video writer
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
    
    # Define intersection area
    center_x, center_y = width // 2, height // 2
    intersection_size = 100
    
    # Vehicle classes
    vehicle_types = [
        {'name': 'car', 'color': (0, 0, 255), 'size': (40, 20)},
        {'name': 'truck', 'color': (0, 255, 0), 'size': (60, 25)},
        {'name': 'bus', 'color': (255, 0, 0), 'size': (70, 30)},
        {'name': 'motorcycle', 'color': (255, 255, 0), 'size': (25, 15)}
    ]
    
    # Lane definitions
    lanes = {
        'north': {'start': (center_x, 0), 'end': (center_x, center_y - intersection_size//2), 'direction': (0, 1)},
        'south': {'start': (center_x, height), 'end': (center_x, center_y + intersection_size//2), 'direction': (0, -1)},
        'east': {'start': (width, center_y), 'end': (center_x + intersection_size//2, center_y), 'direction': (-1, 0)},
        'west': {'start': (0, center_y), 'end': (center_x - intersection_size//2, center_y), 'direction': (1, 0)}
    }
    
    # Active vehicles
    vehicles = []
    
    for frame_num in range(total_frames):
        # Create new frame
        frame = np.zeros((height, width, 3), dtype=np.uint8)
        
        # Draw background (road)
        cv2.rectangle(frame, (0, 0), (width, height), (50, 50, 50), -1)
        
        # Draw intersection
        cv2.rectangle(frame, 
                     (center_x - intersection_size//2, center_y - intersection_size//2),
                     (center_x + intersection_size//2, center_y + intersection_size//2),
                     (100, 100, 100), -1)
        
        # Draw lane markings
        for lane_name, lane_data in lanes.items():
            cv2.line(frame, lane_data['start'], lane_data['end'], (255, 255, 255), 3)
        
        # Draw traffic light
        light_color = (0, 255, 0) if (frame_num // 30) % 2 == 0 else (0, 0, 255)
        cv2.circle(frame, (center_x, center_y), 10, light_color, -1)
        
        # Spawn new vehicles occasionally
        if random.random() < 0.1:  # 10% chance per frame
            lane_name = random.choice(list(lanes.keys()))
            lane_data = lanes[lane_name]
            vehicle_type = random.choice(vehicle_types)
            
            # Calculate spawn position
            if lane_name in ['north', 'south']:
                spawn_x = center_x + random.randint(-20, 20)
                spawn_y = lane_data['start'][1]
            else:
                spawn_x = lane_data['start'][0]
                spawn_y = center_y + random.randint(-20, 20)
            
            vehicle = {
                'type': vehicle_type,
                'position': [spawn_x, spawn_y],
                'lane': lane_name,
                'speed': random.uniform(1, 3),
                'direction': lane_data['direction']
            }
            vehicles.append(vehicle)
        
        # Update and draw vehicles
        vehicles_to_remove = []
        for i, vehicle in enumerate(vehicles):
            # Update position
            vehicle['position'][0] += vehicle['direction'][0] * vehicle['speed']
            vehicle['position'][1] += vehicle['direction'][1] * vehicle['speed']
            
            # Check if vehicle is out of bounds
            x, y = vehicle['position']
            if x < -50 or x > width + 50 or y < -50 or y > height + 50:
                vehicles_to_remove.append(i)
                continue
            
            # Draw vehicle
            vehicle_type = vehicle['type']
            size = vehicle_type['size']
            color = vehicle_type['color']
            
            # Draw vehicle body
            cv2.rectangle(frame,
                         (int(x - size[0]//2), int(y - size[1]//2)),
                         (int(x + size[0]//2), int(y + size[1]//2)),
                         color, -1)
            
            # Draw vehicle label
            cv2.putText(frame, vehicle_type['name'][:3],
                       (int(x - 15), int(y - 10)),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)
        
        # Remove out-of-bounds vehicles
        for i in reversed(vehicles_to_remove):
            vehicles.pop(i)
        
        # Write frame
        out.write(frame)
        
        # Progress update
        if frame_num % 100 == 0:
            progress = (frame_num / total_frames) * 100
            print(f"   Progress: {progress:.1f}% | Vehicles: {len(vehicles)}")
    
    # Release video writer
    out.release()
    
    print(f"✅ Sample video created: {output_path}")
    print(f"   Resolution: {width}x{height}")
    print(f"   FPS: {fps}")
    print(f"   Frames: {total_frames}")
    
    return output_path

def main():
    """Main function to create sample video"""
    print("🎬 Sample Traffic Video Creator")
    print("=" * 35)
    
    # Create sample video
    video_path = create_sample_traffic_video("sample_traffic.mp4", duration=30)
    
    print(f"\n🎉 Sample video created successfully!")
    print(f"📁 Video saved to: {video_path}")
    print(f"\nYou can now use this video to test the video processing system:")
    print(f"   python video_traffic_processor.py")

if __name__ == "__main__":
    main()
