"""
Python SUMO Simulator
A simple traffic simulator that mimics SUMO behavior without requiring SUMO installation
"""

import json
import xml.etree.ElementTree as ET
import time
import random
from datetime import datetime
from typing import Dict, List, Tuple
import math

class PythonSUMOSimulator:
    def __init__(self, config_file: str):
        """
        Initialize Python SUMO Simulator
        
        Args:
            config_file: SUMO configuration file path
        """
        self.config_file = config_file
        self.network_file = None
        self.routes_file = None
        self.vehicles = []
        self.traffic_lights = {}
        self.simulation_time = 0
        self.step_length = 1.0
        self.duration = 300
        
        # Load configuration
        self._load_config()
        
        # Load network and routes
        self._load_network()
        self._load_routes()
        
        # Initialize simulation
        self._initialize_simulation()
    
    def _load_config(self):
        """Load SUMO configuration file"""
        try:
            tree = ET.parse(self.config_file)
            root = tree.getroot()
            
            # Get network file
            net_elem = root.find('.//net-file')
            if net_elem is not None:
                self.network_file = net_elem.get('value')
            
            # Get routes file
            routes_elem = root.find('.//route-files')
            if routes_elem is not None:
                self.routes_file = routes_elem.get('value')
            
            # Get simulation duration
            end_elem = root.find('.//time/end')
            if end_elem is not None:
                self.duration = float(end_elem.get('value', 300))
            
            # Get step length
            step_elem = root.find('.//time/step-length')
            if step_elem is not None:
                self.step_length = float(step_elem.get('value', 1.0))
            
            print(f"✅ Configuration loaded:")
            print(f"   Network: {self.network_file}")
            print(f"   Routes: {self.routes_file}")
            print(f"   Duration: {self.duration} seconds")
            print(f"   Step length: {self.step_length} seconds")
            
        except Exception as e:
            print(f"❌ Error loading config: {e}")
            raise
    
    def _load_network(self):
        """Load SUMO network file"""
        try:
            if not self.network_file:
                return
            
            tree = ET.parse(self.network_file)
            root = tree.getroot()
            
            # Load junctions
            self.junctions = {}
            for junction in root.findall('.//junction'):
                junction_id = junction.get('id')
                junction_type = junction.get('type', 'priority')
                x = float(junction.get('x', 0))
                y = float(junction.get('y', 0))
                
                self.junctions[junction_id] = {
                    'id': junction_id,
                    'type': junction_type,
                    'x': x,
                    'y': y
                }
                
                # Load traffic lights
                if junction_type == 'traffic_light':
                    self.traffic_lights[junction_id] = {
                        'current_phase': 0,
                        'phase_duration': 0,
                        'max_phase_duration': 31,
                        'phases': [
                            {'duration': 31, 'state': 'GGrrrrGGrrrr'},
                            {'duration': 6, 'state': 'yyrrrryyrrrr'},
                            {'duration': 31, 'state': 'rrGGrrrrGGrr'},
                            {'duration': 6, 'state': 'rryyrrrryyrr'},
                            {'duration': 31, 'state': 'rrrrGGrrrrGG'},
                            {'duration': 6, 'state': 'rrrryyrrrryy'},
                            {'duration': 31, 'state': 'rrrrrrGGrrrr'},
                            {'duration': 6, 'state': 'rrrrrryyrrrr'}
                        ]
                    }
            
            # Load edges
            self.edges = {}
            for edge in root.findall('.//edge'):
                edge_id = edge.get('id')
                from_junction = edge.get('from')
                to_junction = edge.get('to')
                
                # Load lanes
                lanes = []
                for lane in edge.findall('.//lane'):
                    lane_id = lane.get('id')
                    speed = float(lane.get('speed', 13.89))
                    length = float(lane.get('length', 100.0))
                    
                    lanes.append({
                        'id': lane_id,
                        'speed': speed,
                        'length': length
                    })
                
                self.edges[edge_id] = {
                    'id': edge_id,
                    'from': from_junction,
                    'to': to_junction,
                    'lanes': lanes
                }
            
            print(f"✅ Network loaded:")
            print(f"   Junctions: {len(self.junctions)}")
            print(f"   Edges: {len(self.edges)}")
            print(f"   Traffic lights: {len(self.traffic_lights)}")
            
        except Exception as e:
            print(f"❌ Error loading network: {e}")
            raise
    
    def _load_routes(self):
        """Load vehicle routes"""
        try:
            if not self.routes_file:
                return
            
            tree = ET.parse(self.routes_file)
            root = tree.getroot()
            
            # Load vehicle types
            self.vehicle_types = {}
            for vtype in root.findall('.//vType'):
                vtype_id = vtype.get('id')
                accel = float(vtype.get('accel', 2.6))
                decel = float(vtype.get('decel', 4.5))
                max_speed = float(vtype.get('maxSpeed', 50))
                length = float(vtype.get('length', 5))
                
                self.vehicle_types[vtype_id] = {
                    'accel': accel,
                    'decel': decel,
                    'max_speed': max_speed,
                    'length': length
                }
            
            # Load vehicles
            self.vehicles = []
            for vehicle in root.findall('.//vehicle'):
                vehicle_id = vehicle.get('id')
                vehicle_type = vehicle.get('type', 'car')
                depart_time = float(vehicle.get('depart', 0))
                route = vehicle.get('route', '')
                
                # Parse route
                route_parts = route.split('-') if '-' in route else [route]
                
                self.vehicles.append({
                    'id': vehicle_id,
                    'type': vehicle_type,
                    'depart_time': depart_time,
                    'route': route_parts,
                    'current_position': 0.0,
                    'current_speed': 0.0,
                    'status': 'waiting' if depart_time > 0 else 'active'
                })
            
            print(f"✅ Routes loaded:")
            print(f"   Vehicle types: {len(self.vehicle_types)}")
            print(f"   Vehicles: {len(self.vehicles)}")
            
        except Exception as e:
            print(f"❌ Error loading routes: {e}")
            raise
    
    def _initialize_simulation(self):
        """Initialize simulation state"""
        self.simulation_time = 0
        self.active_vehicles = []
        self.completed_vehicles = []
        self.metrics = {
            'total_vehicles': len(self.vehicles),
            'active_vehicles': 0,
            'completed_vehicles': 0,
            'average_speed': 0.0,
            'total_waiting_time': 0.0,
            'queue_length': 0
        }
        
        print("✅ Simulation initialized")
    
    def run_simulation(self, gui: bool = False):
        """
        Run the simulation
        
        Args:
            gui: Whether to show GUI (text-based)
        """
        print(f"\n🚀 Starting Python SUMO Simulation")
        print(f"Duration: {self.duration} seconds")
        print(f"Step length: {self.step_length} seconds")
        print("=" * 50)
        
        start_time = time.time()
        
        try:
            while self.simulation_time < self.duration:
                # Update simulation step
                self._simulation_step()
                
                # Show progress
                if self.simulation_time % 10 == 0:
                    progress = (self.simulation_time / self.duration) * 100
                    print(f"⏱️  Time: {self.simulation_time:.1f}s | Progress: {progress:.1f}% | Active: {len(self.active_vehicles)} | Completed: {len(self.completed_vehicles)}")
                
                # Update simulation time
                self.simulation_time += self.step_length
                
                # Small delay for visualization
                if gui:
                    time.sleep(0.1)
            
            # Final statistics
            self._calculate_final_metrics()
            
            elapsed_time = time.time() - start_time
            print(f"\n✅ Simulation completed in {elapsed_time:.2f} seconds")
            print(f"📊 Final Statistics:")
            print(f"   Total vehicles: {self.metrics['total_vehicles']}")
            print(f"   Completed vehicles: {self.metrics['completed_vehicles']}")
            print(f"   Average speed: {self.metrics['average_speed']:.2f} m/s")
            print(f"   Total waiting time: {self.metrics['total_waiting_time']:.2f} seconds")
            
            return True
            
        except KeyboardInterrupt:
            print(f"\n⏹️  Simulation stopped by user at {self.simulation_time:.1f}s")
            return False
        except Exception as e:
            print(f"\n❌ Simulation error: {e}")
            return False
    
    def _simulation_step(self):
        """Execute one simulation step"""
        # Update traffic lights
        self._update_traffic_lights()
        
        # Spawn new vehicles
        self._spawn_vehicles()
        
        # Update active vehicles
        self._update_vehicles()
        
        # Update metrics
        self._update_metrics()
    
    def _update_traffic_lights(self):
        """Update traffic light states"""
        for tl_id, tl_data in self.traffic_lights.items():
            tl_data['phase_duration'] += self.step_length
            
            # Check if phase should change
            current_phase = tl_data['current_phase']
            current_phase_data = tl_data['phases'][current_phase]
            
            if tl_data['phase_duration'] >= current_phase_data['duration']:
                # Move to next phase
                tl_data['current_phase'] = (current_phase + 1) % len(tl_data['phases'])
                tl_data['phase_duration'] = 0
    
    def _spawn_vehicles(self):
        """Spawn vehicles that should depart at current time"""
        for vehicle in self.vehicles:
            if (vehicle['status'] == 'waiting' and 
                vehicle['depart_time'] <= self.simulation_time):
                
                vehicle['status'] = 'active'
                vehicle['current_speed'] = 5.0  # Initial speed
                self.active_vehicles.append(vehicle)
    
    def _update_vehicles(self):
        """Update active vehicles"""
        for vehicle in self.active_vehicles[:]:  # Copy list to avoid modification during iteration
            # Simple vehicle movement
            vehicle['current_position'] += vehicle['current_speed'] * self.step_length
            
            # Check if vehicle completed its route
            if vehicle['current_position'] >= 100.0:  # Assume route length of 100m
                vehicle['status'] = 'completed'
                self.active_vehicles.remove(vehicle)
                self.completed_vehicles.append(vehicle)
            else:
                # Update speed (simple model)
                vehicle['current_speed'] = min(vehicle['current_speed'] + 1.0, 13.89)  # Max speed ~50 km/h
    
    def _update_metrics(self):
        """Update simulation metrics"""
        self.metrics['active_vehicles'] = len(self.active_vehicles)
        self.metrics['completed_vehicles'] = len(self.completed_vehicles)
        
        if self.active_vehicles:
            speeds = [v['current_speed'] for v in self.active_vehicles]
            self.metrics['average_speed'] = sum(speeds) / len(speeds)
        else:
            self.metrics['average_speed'] = 0.0
    
    def _calculate_final_metrics(self):
        """Calculate final simulation metrics"""
        if self.completed_vehicles:
            # Calculate average travel time
            travel_times = []
            for vehicle in self.completed_vehicles:
                travel_time = self.simulation_time - vehicle['depart_time']
                travel_times.append(travel_time)
            
            avg_travel_time = sum(travel_times) / len(travel_times)
            self.metrics['average_travel_time'] = avg_travel_time
        else:
            self.metrics['average_travel_time'] = 0.0
    
    def get_traffic_light_state(self, tl_id: str) -> str:
        """Get current traffic light state"""
        if tl_id in self.traffic_lights:
            current_phase = self.traffic_lights[tl_id]['current_phase']
            return self.traffic_lights[tl_id]['phases'][current_phase]['state']
        return "unknown"
    
    def get_vehicle_positions(self) -> List[Dict]:
        """Get current vehicle positions"""
        positions = []
        for vehicle in self.active_vehicles:
            positions.append({
                'id': vehicle['id'],
                'type': vehicle['type'],
                'position': vehicle['current_position'],
                'speed': vehicle['current_speed']
            })
        return positions

def main():
    """Main function to run the simulator"""
    print("🐍 Python SUMO Simulator")
    print("=" * 30)
    
    # Check if config file exists
    config_file = "demo_output/baseline_simulation.sumocfg"
    
    try:
        # Initialize simulator
        simulator = PythonSUMOSimulator(config_file)
        
        # Ask user for GUI mode
        gui_mode = input("Enable GUI mode? (y/n): ").lower().strip() == 'y'
        
        # Run simulation
        success = simulator.run_simulation(gui=gui_mode)
        
        if success:
            print("\n🎉 Simulation completed successfully!")
            print("\n📊 You can now:")
            print("1. View the generated network and route files")
            print("2. Analyze the simulation results")
            print("3. Use this data for further analysis")
        else:
            print("\n❌ Simulation failed or was interrupted")
    
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nMake sure the configuration file exists and is valid.")

if __name__ == "__main__":
    main()
