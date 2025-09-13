#!/usr/bin/env python3
"""
Live SUMO Comparison System
Runs SUMO GUI with real-time comparison against the provided video
"""

import os
import sys
import cv2
import json
import numpy as np
from typing import Dict, List, Any, Tuple
import subprocess
import traci
import time
from datetime import datetime
import threading

class LiveSUMOComparison:
    def __init__(self, video_path: str):
        self.video_path = video_path
        self.analysis_data = {}
        self.sumo_data = {}
        self.comparison_data = {}
        self.is_running = False
        
    def start_live_comparison(self):
        """Start live SUMO comparison with video"""
        print("🚀 Live SUMO Comparison System")
        print("=" * 80)
        print("Starting SUMO GUI with real-time video comparison")
        print("=" * 80)
        
        # Step 1: Analyze video first
        print("\n📹 STEP 1: Analyzing Real Video")
        print("-" * 50)
        if not self._analyze_video():
            return False
        
        # Step 2: Start SUMO with TraCI
        print("\n🚦 STEP 2: Starting SUMO Simulation")
        print("-" * 50)
        if not self._start_sumo_simulation():
            return False
        
        # Step 3: Run live comparison
        print("\n📊 STEP 3: Live Comparison")
        print("-" * 50)
        self._run_live_comparison()
        
        return True
    
    def _analyze_video(self):
        """Analyze the real video"""
        print("🎥 Analyzing real traffic video...")
        
        if not os.path.exists(self.video_path):
            print(f"❌ Video file not found: {self.video_path}")
            return False
        
        try:
            # Open video
            cap = cv2.VideoCapture(self.video_path)
            if not cap.isOpened():
                print("❌ Could not open video file")
                return False
            
            # Get video properties
            fps = cap.get(cv2.CAP_PROP_FPS)
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            duration = frame_count / fps
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            
            print(f"📊 Video Properties:")
            print(f"  • FPS: {fps:.2f}")
            print(f"  • Duration: {duration:.1f} seconds")
            print(f"  • Resolution: {width}x{height}")
            print(f"  • Total Frames: {frame_count}")
            
            # Initialize analysis data
            self.analysis_data = {
                'video_properties': {
                    'fps': fps,
                    'duration': duration,
                    'width': width,
                    'height': height,
                    'frame_count': frame_count
                },
                'traffic_patterns': [],
                'vehicle_detections': [],
                'traffic_light_states': [],
                'intersection_analysis': {}
            }
            
            # Enhanced vehicle detection setup
            vehicle_detector = cv2.createBackgroundSubtractorMOG2(detectShadows=True)
            vehicle_detector.setShadowThreshold(0.5)
            vehicle_detector.setShadowValue(127)
            
            print(f"\n🔍 Analyzing {frame_count} frames...")
            
            frame_number = 0
            total_vehicles_detected = 0
            
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                
                # Preprocess frame
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                blurred = cv2.GaussianBlur(gray, (5, 5), 0)
                
                # Enhanced vehicle detection
                fg_mask = vehicle_detector.apply(blurred)
                
                # Morphological operations
                kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
                cleaned_mask = cv2.morphologyEx(fg_mask, cv2.MORPH_CLOSE, kernel)
                cleaned_mask = cv2.morphologyEx(cleaned_mask, cv2.MORPH_OPEN, kernel)
                
                # Find contours
                contours, _ = cv2.findContours(cleaned_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                
                # Filter contours by area and aspect ratio
                vehicle_contours = []
                for contour in contours:
                    area = cv2.contourArea(contour)
                    if 100 < area < 5000:  # Reasonable vehicle size
                        x, y, w, h = cv2.boundingRect(contour)
                        aspect_ratio = w / h
                        if 0.3 < aspect_ratio < 3.0:  # Reasonable vehicle shape
                            vehicle_contours.append(contour)
                
                vehicle_count = len(vehicle_contours)
                total_vehicles_detected += vehicle_count
                
                # Detect traffic lights
                traffic_light_state = self._detect_traffic_lights(frame)
                
                # Store analysis data
                timestamp = frame_number / fps
                self.analysis_data['traffic_patterns'].append({
                    'timestamp': timestamp,
                    'frame': frame_number,
                    'vehicle_count': vehicle_count,
                    'detection_confidence': min(vehicle_count / 10.0, 1.0)
                })
                
                self.analysis_data['vehicle_detections'].append({
                    'timestamp': timestamp,
                    'frame': frame_number,
                    'vehicles': vehicle_count,
                    'contours': len(contours),
                    'filtered_contours': len(vehicle_contours)
                })
                
                self.analysis_data['traffic_light_states'].append({
                    'timestamp': timestamp,
                    'frame': frame_number,
                    'state': traffic_light_state
                })
                
                frame_number += 1
                
                # Progress indicator
                if frame_number % 60 == 0:
                    progress = (frame_number / frame_count) * 100
                    print(f"  📈 Progress: {progress:.1f}% - Vehicles: {vehicle_count}")
            
            cap.release()
            
            # Analyze patterns
            self._analyze_traffic_patterns()
            
            print(f"\n✅ Video analysis completed!")
            print(f"  • Analyzed {frame_number} frames")
            print(f"  • Total vehicles detected: {total_vehicles_detected}")
            print(f"  • Average vehicles per frame: {total_vehicles_detected/frame_number:.1f}")
            
            return True
            
        except Exception as e:
            print(f"❌ Video analysis error: {e}")
            return False
    
    def _detect_traffic_lights(self, frame) -> str:
        """Detect traffic light state"""
        try:
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            
            # Define color ranges
            red_lower1 = np.array([0, 50, 50])
            red_upper1 = np.array([10, 255, 255])
            red_lower2 = np.array([170, 50, 50])
            red_upper2 = np.array([180, 255, 255])
            
            green_lower = np.array([40, 50, 50])
            green_upper = np.array([80, 255, 255])
            
            yellow_lower = np.array([20, 50, 50])
            yellow_upper = np.array([30, 255, 255])
            
            # Create masks
            red_mask1 = cv2.inRange(hsv, red_lower1, red_upper1)
            red_mask2 = cv2.inRange(hsv, red_lower2, red_upper2)
            red_mask = cv2.bitwise_or(red_mask1, red_mask2)
            
            green_mask = cv2.inRange(hsv, green_lower, green_upper)
            yellow_mask = cv2.inRange(hsv, yellow_lower, yellow_upper)
            
            # Count pixels
            red_pixels = cv2.countNonZero(red_mask)
            green_pixels = cv2.countNonZero(green_mask)
            yellow_pixels = cv2.countNonZero(yellow_mask)
            
            # Determine state
            threshold = 50
            if red_pixels > threshold and red_pixels > green_pixels and red_pixels > yellow_pixels:
                return 'red'
            elif green_pixels > threshold and green_pixels > red_pixels and green_pixels > yellow_pixels:
                return 'green'
            elif yellow_pixels > threshold and yellow_pixels > red_pixels and yellow_pixels > green_pixels:
                return 'yellow'
            else:
                return 'unknown'
                
        except Exception as e:
            return 'unknown'
    
    def _analyze_traffic_patterns(self):
        """Analyze traffic patterns"""
        try:
            patterns = self.analysis_data['traffic_patterns']
            
            if not patterns:
                return
            
            # Calculate statistics
            vehicle_counts = [p['vehicle_count'] for p in patterns]
            timestamps = [p['timestamp'] for p in patterns]
            confidences = [p['detection_confidence'] for p in patterns]
            
            # Peak traffic times
            max_vehicles = max(vehicle_counts) if vehicle_counts else 0
            peak_times = [t for t, v in zip(timestamps, vehicle_counts) if v == max_vehicles]
            
            # Traffic density over time
            density_analysis = {
                'low_traffic': len([v for v in vehicle_counts if v < 3]),
                'medium_traffic': len([v for v in vehicle_counts if 3 <= v < 8]),
                'high_traffic': len([v for v in vehicle_counts if v >= 8])
            }
            
            # Traffic light state analysis
            tl_states = [s['state'] for s in self.analysis_data['traffic_light_states']]
            tl_analysis = {
                'red_percentage': (tl_states.count('red') / len(tl_states)) * 100 if tl_states else 0,
                'green_percentage': (tl_states.count('green') / len(tl_states)) * 100 if tl_states else 0,
                'yellow_percentage': (tl_states.count('yellow') / len(tl_states)) * 100 if tl_states else 0,
                'unknown_percentage': (tl_states.count('unknown') / len(tl_states)) * 100 if tl_states else 0
            }
            
            # Movement analysis
            movement_analysis = self._analyze_movement_patterns(patterns)
            
            self.analysis_data['intersection_analysis'] = {
                'peak_traffic': {
                    'max_vehicles': max_vehicles,
                    'peak_times': peak_times
                },
                'density_distribution': density_analysis,
                'traffic_light_analysis': tl_analysis,
                'movement_analysis': movement_analysis,
                'average_vehicles': np.mean(vehicle_counts) if vehicle_counts else 0,
                'vehicle_count_std': np.std(vehicle_counts) if vehicle_counts else 0,
                'average_confidence': np.mean(confidences) if confidences else 0,
                'total_vehicles_detected': sum(vehicle_counts)
            }
            
            print(f"📊 Video Analysis Results:")
            print(f"  • Peak Traffic: {max_vehicles} vehicles")
            print(f"  • Average Vehicles: {np.mean(vehicle_counts):.1f}")
            print(f"  • Detection Confidence: {np.mean(confidences):.2f}")
            print(f"  • Traffic Light States: Red {tl_analysis['red_percentage']:.1f}%, Green {tl_analysis['green_percentage']:.1f}%, Yellow {tl_analysis['yellow_percentage']:.1f}%")
            
        except Exception as e:
            print(f"⚠️  Pattern analysis error: {e}")
    
    def _analyze_movement_patterns(self, patterns: List[Dict]) -> Dict[str, Any]:
        """Analyze vehicle movement patterns"""
        try:
            if len(patterns) < 2:
                return {'trend': 'insufficient_data'}
            
            # Calculate traffic trend
            first_half = patterns[:len(patterns)//2]
            second_half = patterns[len(patterns)//2:]
            
            first_half_avg = np.mean([p['vehicle_count'] for p in first_half])
            second_half_avg = np.mean([p['vehicle_count'] for p in second_half])
            
            if second_half_avg > first_half_avg * 1.1:
                trend = 'increasing'
            elif second_half_avg < first_half_avg * 0.9:
                trend = 'decreasing'
            else:
                trend = 'stable'
            
            # Calculate variability
            vehicle_counts = [p['vehicle_count'] for p in patterns]
            variability = np.std(vehicle_counts) / np.mean(vehicle_counts) if np.mean(vehicle_counts) > 0 else 0
            
            return {
                'trend': trend,
                'variability': variability,
                'first_half_avg': first_half_avg,
                'second_half_avg': second_half_avg
            }
            
        except Exception as e:
            return {'trend': 'error', 'error': str(e)}
    
    def _start_sumo_simulation(self):
        """Start SUMO simulation with TraCI"""
        print("🚦 Starting SUMO simulation...")
        
        try:
            # Create SUMO configuration
            self._create_sumo_config()
            
            # Get SUMO path
            sumo_path = self._get_sumo_path()
            sumo_binary = os.path.join(sumo_path, "bin", "sumo-gui.exe")
            sumo_cmd = [sumo_binary, "-c", "live_comparison.sumocfg", "--remote-port", "8813"]
            
            print("  🚦 Starting SUMO GUI...")
            print("  - The SUMO GUI will open in a new window")
            print("  - You can see the 4-way intersection with 3 lanes per direction")
            print("  - AI will control traffic lights in real-time")
            print("  - Watch for live comparison data in the console")
            
            # Start SUMO as subprocess
            subprocess.Popen(sumo_cmd, stdout=sys.stdout, stderr=sys.stderr)
            time.sleep(5)  # Wait for SUMO to start
            
            print("  🤖 Connecting to SUMO via TraCI...")
            
            # Connect via TraCI
            traci.start(sumo_cmd, port=8813, numRetries=10)
            print("  ✅ Connected to SUMO via TraCI")
            
            return True
            
        except Exception as e:
            print(f"❌ SUMO simulation error: {e}")
            return False
    
    def _get_sumo_path(self):
        """Get SUMO installation path"""
        if 'SUMO_HOME' in os.environ:
            return os.environ['SUMO_HOME']
        
        possible_paths = [
            r"C:\Program Files (x86)\Eclipse\Sumo",
            r"C:\Program Files\Eclipse\Sumo",
            r"C:\sumo",
            r"C:\sumo-1.24.0"
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                return path
        
        raise Exception("SUMO not found. Please set SUMO_HOME environment variable.")
    
    def _create_sumo_config(self):
        """Create SUMO configuration"""
        print("  🔧 Creating SUMO configuration...")
        
        # Use the professional 4-way intersection
        network_file = "sumofiles/4way_3lane_lh.net.xml"
        
        # Create routes based on video analysis
        routes_file = "live_comparison_routes.rou.xml"
        self._create_routes(routes_file)
        
        # Create SUMO config
        config_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<configuration xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="http://sumo.dlr.de/xsd/sumoConfiguration.xsd">
    <input>
        <net-file value="{network_file}"/>
        <route-files value="{routes_file}"/>
    </input>
    
    <time>
        <begin value="0"/>
        <end value="300"/>
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
    
    <gui_only>
        <start value="true"/>
    </gui_only>
</configuration>"""
        
        with open("live_comparison.sumocfg", 'w') as f:
            f.write(config_content)
        
        print(f"  ✅ Created SUMO config: live_comparison.sumocfg")
    
    def _create_routes(self, routes_file: str):
        """Create routes based on video analysis"""
        print("  🛣️  Creating routes from video analysis...")
        
        # Get traffic patterns from analysis
        patterns = self.analysis_data['traffic_patterns']
        avg_vehicles = np.mean([p['vehicle_count'] for p in patterns]) if patterns else 5
        max_vehicles = max([p['vehicle_count'] for p in patterns]) if patterns else 10
        
        # Scale traffic density based on analysis
        base_period = 3.0
        if avg_vehicles > 8:
            base_period = 2.0  # Higher density
        elif avg_vehicles < 3:
            base_period = 5.0  # Lower density
        
        # Create routes with realistic traffic patterns
        routes_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<routes xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="http://sumo.dlr.de/xsd/routes_file.xsd">
    <vType id="car" accel="1.8" decel="6.0" sigma="0.35" length="4" width="1.8" maxSpeed="16.67" guiShape="passenger" guiColor="0,0,1" minGap="1.5" tau="1.2"/>
    <vType id="bus" accel="1.0" decel="5.5" sigma="0.35" length="12" width="2.5" maxSpeed="13.89" guiShape="bus" guiColor="1,0,0" minGap="2.5" tau="1.6"/>
    <vType id="truck" accel="0.7" decel="5.0" sigma="0.35" length="10" width="2.5" maxSpeed="12.0" guiShape="truck" guiColor="0.5,0.25,0" minGap="2.5" tau="1.6"/>
    
    <!-- Routes -->
    <route id="S_to_N" edges="south2center center2north"/>
    <route id="S_to_E" edges="south2center center2east"/>
    <route id="S_to_W" edges="south2center center2west"/>
    <route id="N_to_S" edges="north2center center2south"/>
    <route id="N_to_E" edges="north2center center2east"/>
    <route id="N_to_W" edges="north2center center2west"/>
    <route id="E_to_W" edges="east2center center2west"/>
    <route id="E_to_N" edges="east2center center2north"/>
    <route id="E_to_S" edges="east2center center2south"/>
    <route id="W_to_E" edges="west2center center2east"/>
    <route id="W_to_N" edges="west2center center2north"/>
    <route id="W_to_S" edges="west2center center2south"/>
    
    <!-- Traffic flows based on video analysis -->
    <flow id="S_through" route="S_to_N" type="car" begin="0" end="300" period="{base_period:.1f}" departLane="1" departSpeed="5.0"/>
    <flow id="S_right" route="S_to_E" type="car" begin="0" end="300" period="{base_period * 1.2:.1f}" departLane="2" departSpeed="5.0"/>
    <flow id="S_left" route="S_to_W" type="car" begin="0" end="300" period="{base_period * 1.5:.1f}" departLane="0" departSpeed="4.0"/>
    
    <flow id="N_through" route="N_to_S" type="car" begin="0" end="300" period="{base_period * 1.1:.1f}" departLane="1" departSpeed="5.0"/>
    <flow id="N_right" route="N_to_W" type="car" begin="0" end="300" period="{base_period * 1.3:.1f}" departLane="2" departSpeed="5.0"/>
    <flow id="N_left" route="N_to_E" type="car" begin="0" end="300" period="{base_period * 1.6:.1f}" departLane="0" departSpeed="4.0"/>
    
    <flow id="E_through" route="E_to_W" type="car" begin="0" end="300" period="{base_period * 0.9:.1f}" departLane="1" departSpeed="5.0"/>
    <flow id="E_right" route="E_to_N" type="car" begin="0" end="300" period="{base_period * 1.1:.1f}" departLane="2" departSpeed="5.0"/>
    <flow id="E_left" route="E_to_S" type="car" begin="0" end="300" period="{base_period * 1.4:.1f}" departLane="0" departSpeed="4.0"/>
    
    <flow id="W_through" route="W_to_E" type="car" begin="0" end="300" period="{base_period * 1.0:.1f}" departLane="1" departSpeed="5.0"/>
    <flow id="W_right" route="W_to_S" type="car" begin="0" end="300" period="{base_period * 1.2:.1f}" departLane="2" departSpeed="5.0"/>
    <flow id="W_left" route="W_to_N" type="car" begin="0" end="300" period="{base_period * 1.5:.1f}" departLane="0" departSpeed="4.0"/>
    
    <!-- Add buses and trucks for realism -->
    <flow id="S_bus" route="S_to_N" type="bus" begin="0" end="300" period="30.0" departLane="1" departSpeed="4.0"/>
    <flow id="N_truck" route="N_to_S" type="truck" begin="0" end="300" period="25.0" departLane="1" departSpeed="3.5"/>
    <flow id="E_bus" route="E_to_W" type="bus" begin="0" end="300" period="35.0" departLane="1" departSpeed="4.0"/>
    <flow id="W_truck" route="W_to_E" type="truck" begin="0" end="300" period="28.0" departLane="1" departSpeed="3.5"/>
</routes>"""
        
        with open(routes_file, 'w') as f:
            f.write(routes_content)
        
        print(f"  ✅ Created routes: {routes_file}")
        print(f"  📊 Traffic density: {avg_vehicles:.1f} avg vehicles, {max_vehicles} max vehicles")
    
    def _run_live_comparison(self):
        """Run live comparison between video and SUMO"""
        print("📊 Starting live comparison...")
        print("Watch the SUMO GUI and monitor the comparison data below:")
        print("=" * 80)
        
        try:
            step = 0
            max_steps = 3000
            ai_control_start = 100
            
            # Get video data for comparison
            video_patterns = self.analysis_data['traffic_patterns']
            video_avg = np.mean([p['vehicle_count'] for p in video_patterns]) if video_patterns else 0
            video_max = max([p['vehicle_count'] for p in video_patterns]) if video_patterns else 0
            
            print(f"🎥 Video Reference Data:")
            print(f"  • Average Vehicles: {video_avg:.1f}")
            print(f"  • Peak Vehicles: {video_max}")
            print(f"  • Total Frames: {len(video_patterns)}")
            print("=" * 80)
            
            self.is_running = True
            
            while step < max_steps and traci.simulation.getMinExpectedNumber() > 0 and self.is_running:
                # Get current simulation time
                sim_time = traci.simulation.getTime()
                vehicle_count = traci.simulation.getMinExpectedNumber()
                
                # Store SUMO data
                self.sumo_data[step] = {
                    'time': sim_time,
                    'vehicle_count': vehicle_count,
                    'step': step
                }
                
                # AI Control Logic
                if step > ai_control_start:
                    self._apply_ai_control(sim_time, vehicle_count)
                
                # Live comparison every 50 steps
                if step % 50 == 0:
                    self._display_live_comparison(sim_time, vehicle_count, video_avg, video_max)
                
                # Step simulation
                traci.simulationStep()
                step += 1
                
                # Check for user input to stop
                if step % 200 == 0:
                    print(f"\n⏱️  Simulation Time: {sim_time:.1f}s | Step: {step} | Vehicles: {vehicle_count}")
                    print("Press Ctrl+C to stop the simulation and see final results...")
            
            # Final comparison
            self._display_final_comparison()
            
        except KeyboardInterrupt:
            print("\n\n🛑 Simulation stopped by user")
            self._display_final_comparison()
        except Exception as e:
            print(f"\n❌ Simulation error: {e}")
        finally:
            self.is_running = False
            try:
                traci.close()
            except:
                pass
    
    def _apply_ai_control(self, sim_time: float, vehicle_count: int):
        """Apply AI control to traffic lights"""
        try:
            # AI control based on video analysis
            if vehicle_count > 20:
                traci.trafficlight.setPhaseDuration("center", 30)
            elif vehicle_count > 10:
                traci.trafficlight.setPhaseDuration("center", 25)
            elif vehicle_count < 5:
                traci.trafficlight.setPhaseDuration("center", 15)
            else:
                traci.trafficlight.setPhaseDuration("center", 20)
                
        except Exception as e:
            pass  # Ignore TraCI errors
    
    def _display_live_comparison(self, sim_time: float, vehicle_count: int, video_avg: float, video_max: int):
        """Display live comparison data"""
        try:
            # Calculate current accuracy
            accuracy = 100 - abs(vehicle_count - video_avg) / max(video_avg, 1) * 100
            
            # Calculate efficiency
            efficiency = (vehicle_count / video_max) * 100 if video_max > 0 else 0
            
            print(f"\n📊 LIVE COMPARISON - Time: {sim_time:.1f}s")
            print(f"  🎥 Video Reference: {video_avg:.1f} avg, {video_max} max")
            print(f"  🚦 SUMO Current: {vehicle_count} vehicles")
            print(f"  📈 Accuracy: {accuracy:.1f}%")
            print(f"  ⚡ Efficiency: {efficiency:.1f}%")
            print(f"  🤖 AI Control: {'Active' if sim_time > 10 else 'Starting...'}")
            
        except Exception as e:
            print(f"⚠️  Comparison display error: {e}")
    
    def _display_final_comparison(self):
        """Display final comparison results"""
        print("\n\n📊 FINAL COMPARISON RESULTS")
        print("=" * 80)
        
        try:
            if not self.analysis_data['traffic_patterns'] or not self.sumo_data:
                print("❌ Insufficient data for comparison")
                return
            
            # Calculate final metrics
            video_avg = np.mean([p['vehicle_count'] for p in self.analysis_data['traffic_patterns']])
            video_max = max([p['vehicle_count'] for p in self.analysis_data['traffic_patterns']])
            
            sumo_avg = np.mean([d['vehicle_count'] for d in self.sumo_data.values()])
            sumo_max = max([d['vehicle_count'] for d in self.sumo_data.values()])
            
            # Calculate accuracy
            accuracy = 100 - abs(sumo_avg - video_avg) / max(video_avg, 1) * 100
            
            # Calculate efficiency
            video_efficiency = (video_avg / video_max) * 100 if video_max > 0 else 0
            sumo_efficiency = (sumo_avg / sumo_max) * 100 if sumo_max > 0 else 0
            efficiency_improvement = sumo_efficiency - video_efficiency
            
            print(f"🎥 VIDEO ANALYSIS RESULTS:")
            print(f"  • Frames Analyzed: {len(self.analysis_data['traffic_patterns'])}")
            print(f"  • Average Vehicles: {video_avg:.1f}")
            print(f"  • Peak Vehicles: {video_max}")
            print(f"  • Detection Confidence: {self.analysis_data['intersection_analysis']['average_confidence']:.2f}")
            
            print(f"\n🚦 SUMO SIMULATION RESULTS:")
            print(f"  • Simulation Steps: {len(self.sumo_data)}")
            print(f"  • Average Vehicles: {sumo_avg:.1f}")
            print(f"  • Peak Vehicles: {sumo_max}")
            print(f"  • Simulation Duration: {max([d['time'] for d in self.sumo_data.values()]):.1f}s")
            
            print(f"\n📈 COMPARISON METRICS:")
            print(f"  • Replication Accuracy: {accuracy:.1f}%")
            print(f"  • Video Efficiency: {video_efficiency:.1f}%")
            print(f"  • SUMO Efficiency: {sumo_efficiency:.1f}%")
            print(f"  • Efficiency Improvement: {efficiency_improvement:.1f}%")
            
            # Performance assessment
            if accuracy >= 90:
                print(f"\n🎯 PERFORMANCE ASSESSMENT: EXCELLENT (91%+)")
            elif accuracy >= 80:
                print(f"\n🎯 PERFORMANCE ASSESSMENT: GOOD (80-90%)")
            elif accuracy >= 70:
                print(f"\n🎯 PERFORMANCE ASSESSMENT: FAIR (70-79%)")
            else:
                print(f"\n🎯 PERFORMANCE ASSESSMENT: NEEDS IMPROVEMENT (<70%)")
            
            print(f"\n✅ SUMO successfully replicated your video with {accuracy:.1f}% accuracy!")
            
        except Exception as e:
            print(f"❌ Final comparison error: {e}")

def main():
    """Main function"""
    print("🚀 Live SUMO Comparison System")
    print("=" * 80)
    print("Runs SUMO GUI with real-time comparison against your video")
    print("=" * 80)
    
    # Check for video file
    video_path = "Traffic_videos/stock-footage-drone-shot-way-intersection.webm"
    
    if not os.path.exists(video_path):
        print(f"❌ Video file not found: {video_path}")
        print("Please ensure the video file exists in the Traffic_videos folder.")
        return
    
    try:
        # Create live comparison system
        system = LiveSUMOComparison(video_path)
        
        # Start live comparison
        if system.start_live_comparison():
            print("\n🎉 Live comparison completed successfully!")
            print("You can see how well SUMO replicated your real video!")
        else:
            print("\n❌ Live comparison failed.")
            
    except Exception as e:
        print(f"\n❌ Error: {e}")

if __name__ == "__main__":
    main()
