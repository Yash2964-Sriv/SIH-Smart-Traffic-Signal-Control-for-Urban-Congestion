#!/usr/bin/env python3
"""
Simple Working AI Controller for Multi-Intersection Traffic Management
BACKUP COPY - Created on 2024-12-19 to preserve chat history and current state
"""

import os
import sys
import time
import numpy as np
import traci
import subprocess
from typing import Dict, List, Tuple
import matplotlib.pyplot as plt

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

class SimpleWorkingAIController:
    """
    Simple AI controller for multiple intersections with basic traffic management
    """
    
    def __init__(self, junction_ids: List[str] = ["I1", "I2"], sumo_config: str = None):
        self.junction_ids = junction_ids
        self.sumo_config = sumo_config
        self.controllers = {}
        self.is_running = False
        
        if not self.sumo_config:
            raise ValueError("SUMO configuration file path must be provided.")
        
        # Initialize individual controllers for each intersection
        for junction_id in junction_ids:
            self.controllers[junction_id] = {
                'current_phase': 0,
                'phase_start_time': 0,
                'min_phase_time': 10.0,
                'max_phase_time': 60.0,
                'total_switches': 0,
                'waiting_time': 0,
                'vehicles_passed': 0
            }
        
        # Global coordination parameters
        self.coordination_delay = 5.0  # Delay between intersection switches
        self.last_switch_time = 0
        
        # Get SUMO path
        self.sumo_path = self._get_sumo_path()
        
        print(f"🚦 Simple Working AI Controller initialized")
        print(f"   Junctions: {junction_ids}")
        print(f"   SUMO Config: {sumo_config}")
        print(f"   Coordination delay: {self.coordination_delay}s")
    
    def _get_sumo_path(self) -> str:
        """Get SUMO GUI path"""
        sumo_paths = [
            r"C:\Program Files (x86)\Eclipse\Sumo\bin\sumo-gui.exe",
            r"C:\Program Files\Eclipse\Sumo\bin\sumo-gui.exe",
            "sumo-gui"  # If in PATH
        ]
        
        for path in sumo_paths:
            if os.path.exists(path):
                return path
        
        # Check if sumo-gui is in PATH
        try:
            result = subprocess.run(["where", "sumo-gui"], capture_output=True, text=True)
            if result.returncode == 0:
                return "sumo-gui"
        except:
            pass
        
        raise FileNotFoundError("SUMO GUI not found. Please ensure it's installed and in your PATH.")
    
    def start_simulation(self, gui: bool = True) -> bool:
        """Start SUMO simulation"""
        try:
            # Use full path if it exists, otherwise use command name
            if os.path.exists(self.sumo_path):
                sumo_cmd = [self.sumo_path, "-c", self.sumo_config, "--start"]
            else:
                sumo_cmd = ["sumo-gui", "-c", self.sumo_config, "--start"]
            
            if not gui:
                # Replace sumo-gui with sumo for non-GUI mode
                sumo_cmd[0] = sumo_cmd[0].replace("sumo-gui", "sumo")
            
            traci.start(sumo_cmd)
            self.is_running = True
            
            # Initialize traffic lights
            for junction_id in self.junction_ids:
                self.controllers[junction_id]['current_phase'] = traci.trafficlight.getPhase(junction_id)
                self.controllers[junction_id]['phase_start_time'] = traci.simulation.getTime()
            
            print(f"🚦 Traffic lights initialized for {self.junction_ids}")
            print("✅ SUMO simulation started successfully")
            return True
            
        except Exception as e:
            print(f"❌ Failed to start SUMO: {e}")
            self.is_running = False
            return False
    
    def close_simulation(self):
        """Close SUMO connection"""
        self.is_running = False
        try:
            traci.close()
        except:
            pass
        print("🛑 Simple Working AI Control stopped")
    
    def get_intersection_state(self, junction_id: str) -> Dict:
        """Get traffic state for a specific intersection"""
        try:
            # Get vehicles in the intersection area
            vehicles = traci.vehicle.getIDList()
            
            # Count vehicles approaching each direction
            north_vehicles = 0
            south_vehicles = 0
            east_vehicles = 0
            west_vehicles = 0
            
            total_waiting_time = 0
            total_speed = 0
            vehicle_count = 0
            
            for vehicle_id in vehicles:
                try:
                    # Get vehicle position and speed
                    pos = traci.vehicle.getPosition(vehicle_id)
                    speed = traci.vehicle.getSpeed(vehicle_id)
                    waiting_time = traci.vehicle.getAccumulatedWaitingTime(vehicle_id)
                    
                    total_waiting_time += waiting_time
                    total_speed += speed
                    vehicle_count += 1
                    
                    # Simple direction detection based on position
                    if junction_id == "I1":
                        if pos[0] < 100:  # West
                            west_vehicles += 1
                        elif pos[0] > 100:  # East
                            east_vehicles += 1
                        elif pos[1] < 100:  # North
                            north_vehicles += 1
                        elif pos[1] > 100:  # South
                            south_vehicles += 1
                    elif junction_id == "I2":
                        if pos[0] < 200:  # West
                            west_vehicles += 1
                        elif pos[0] > 200:  # East
                            east_vehicles += 1
                        elif pos[1] < 100:  # North
                            north_vehicles += 1
                        elif pos[1] > 100:  # South
                            south_vehicles += 1
                            
                except:
                    continue
            
            avg_speed = total_speed / vehicle_count if vehicle_count > 0 else 0
            queue_length = north_vehicles + south_vehicles + east_vehicles + west_vehicles
            
            return {
                'north_vehicles': north_vehicles,
                'south_vehicles': south_vehicles,
                'east_vehicles': east_vehicles,
                'west_vehicles': west_vehicles,
                'total_vehicles': vehicle_count,
                'total_waiting_time': total_waiting_time,
                'avg_speed': avg_speed,
                'queue_length': queue_length,
                'vehicles_passed': 0  # Will be calculated in update_metrics
            }
            
        except Exception as e:
            print(f"⚠️ Error getting state for {junction_id}: {e}")
            return {
                'north_vehicles': 0, 'south_vehicles': 0, 'east_vehicles': 0, 'west_vehicles': 0,
                'total_vehicles': 0, 'total_waiting_time': 0, 'avg_speed': 0, 'queue_length': 0, 'vehicles_passed': 0
            }
    
    def coordinate_intersections(self) -> List[Tuple[str, int]]:
        """Simple coordination logic for all intersections"""
        actions = []
        current_time = traci.simulation.getTime()
        
        for junction_id in self.junction_ids:
            controller = self.controllers[junction_id]
            state = self.get_intersection_state(junction_id)
            
            # Simple rule-based control
            action = self._simple_decision_logic(junction_id, state, current_time)
            actions.append((junction_id, action))
        
        return actions
    
    def _simple_decision_logic(self, junction_id: str, state: Dict, current_time: float) -> int:
        """Simple decision logic for traffic control"""
        controller = self.controllers[junction_id]
        current_phase = controller['current_phase']
        phase_duration = current_time - controller['phase_start_time']
        
        # Actions: 0=keep_current, 1=switch_phase, 2=extend_green_5s, 3=extend_green_10s
        
        # Don't switch too frequently
        if phase_duration < controller['min_phase_time']:
            return 0  # Keep current phase
        
        # Check if we should switch based on traffic
        north_south_traffic = state['north_vehicles'] + state['south_vehicles']
        east_west_traffic = state['east_vehicles'] + state['west_vehicles']
        
        # If current phase is North-South (0 or 2) and East-West has more traffic
        if current_phase in [0, 2] and east_west_traffic > north_south_traffic + 2:
            return 1  # Switch to East-West
        # If current phase is East-West (1 or 3) and North-South has more traffic
        elif current_phase in [1, 3] and north_south_traffic > east_west_traffic + 2:
            return 1  # Switch to North-South
        
        # Extend green if there's still traffic
        if phase_duration < controller['max_phase_time']:
            if current_phase in [0, 2] and north_south_traffic > 0:
                return 2  # Extend green 5s
            elif current_phase in [1, 3] and east_west_traffic > 0:
                return 2  # Extend green 5s
        
        return 0  # Keep current phase
    
    def execute_intersection_action(self, junction_id: str, action: int):
        """Execute action for a specific intersection"""
        try:
            controller = self.controllers[junction_id]
            current_phase = traci.trafficlight.getPhase(junction_id)
            current_time = traci.simulation.getTime()
            
            if action == 0:  # Keep current phase
                pass
            elif action == 1:  # Switch phase
                if current_time - controller['phase_start_time'] >= controller['min_phase_time']:
                    traci.trafficlight.setPhase(junction_id, (current_phase + 1) % 4)
                    controller['current_phase'] = (current_phase + 1) % 4
                    controller['phase_start_time'] = current_time
                    controller['total_switches'] += 1
            elif action == 2:  # Extend green 5s
                if current_phase in [0, 2]:  # North-South green
                    traci.trafficlight.setPhaseDuration(junction_id, 5.0)
                elif current_phase in [1, 3]:  # East-West green
                    traci.trafficlight.setPhaseDuration(junction_id, 5.0)
            elif action == 3:  # Extend green 10s
                if current_phase in [0, 2]:  # North-South green
                    traci.trafficlight.setPhaseDuration(junction_id, 10.0)
                elif current_phase in [1, 3]:  # East-West green
                    traci.trafficlight.setPhaseDuration(junction_id, 10.0)
                    
        except Exception as e:
            print(f"⚠️ Error executing action {action} for {junction_id}: {e}")
    
    def update_metrics(self, states: Dict) -> Dict:
        """Update performance metrics"""
        total_waiting_time = sum(state.get('total_waiting_time', 0) for state in states.values())
        total_vehicles = sum(state.get('total_vehicles', 0) for state in states.values())
        total_queue_length = sum(state.get('queue_length', 0) for state in states.values())
        avg_speed = np.mean([state.get('avg_speed', 0) for state in states.values()])
        
        return {
            'total_waiting_time': total_waiting_time,
            'total_vehicles': total_vehicles,
            'total_queue_length': total_queue_length,
            'avg_speed': avg_speed
        }
    
    def print_status(self, current_time: float, states: Dict, metrics: Dict):
        """Print current status"""
        print(f"\n⏰ Time: {current_time:.1f}s")
        print(f"🚗 Total Vehicles: {metrics['total_vehicles']}")
        print(f"⏳ Total Waiting Time: {metrics['total_waiting_time']:.1f}s")
        print(f"📏 Queue Length: {metrics['total_queue_length']}")
        print(f"🏃 Avg Speed: {metrics['avg_speed']:.1f} m/s")
        
        for junction_id, state in states.items():
            phase = self.controllers[junction_id]['current_phase']
            print(f"🚦 {junction_id}: Phase {phase}, Vehicles: {state['total_vehicles']}")
    
    def run_simulation(self, max_duration: float = 300.0, control_interval: float = 5.0):
        """Run the main simulation loop with AI control"""
        try:
            start_time = traci.simulation.getTime()
            
            print(f"\n🎯 Simple Working AI Control Active...")
            print("=" * 60)
            
            while self.is_running and traci.simulation.getTime() - start_time < max_duration:
                current_time = traci.simulation.getTime()
                
                # Get states for all intersections
                states = {}
                for junction_id in self.junction_ids:
                    states[junction_id] = self.get_intersection_state(junction_id)
                
                # Coordinate actions across intersections
                actions = self.coordinate_intersections()
                
                # Execute actions
                for junction_id, action in actions:
                    self.execute_intersection_action(junction_id, action)
                
                # Update metrics
                metrics = self.update_metrics(states)
                
                # Print status every 30 seconds
                if int(current_time) % 30 == 0:
                    self.print_status(current_time, states, metrics)
                
                # Advance simulation
                traci.simulationStep()
                
                # Control interval
                time.sleep(control_interval / 10.0)  # Scale down for faster simulation
                
        except KeyboardInterrupt:
            print("\n⏹️ Control loop interrupted by user")
        except Exception as e:
            print(f"❌ Error in control loop: {e}")
        finally:
            self.is_running = False
    
    def print_performance_report(self):
        """Print final performance report"""
        print("\n📊 Performance Report")
        print("=" * 40)
        
        for junction_id, controller in self.controllers.items():
            print(f"🚦 {junction_id}:")
            print(f"   Total Switches: {controller['total_switches']}")
            print(f"   Current Phase: {controller['current_phase']}")

def main():
    """Main function to run the AI controller"""
    print("🚦 Simple Working AI Traffic Controller")
    print("=" * 50)
    
    # Configuration
    config_file = "real_traffic_output/simple_multi_intersection.sumocfg"
    junction_ids = ["I1", "I2"]
    
    if not os.path.exists(config_file):
        print(f"❌ Config file not found: {config_file}")
        return
    
    try:
        # Create controller
        controller = SimpleWorkingAIController(junction_ids, config_file)
        
        # Start simulation
        if controller.start_simulation(gui=True):
            # Run simulation
            controller.run_simulation(max_duration=300.0, control_interval=2.0)
            
            # Print final report
            controller.print_performance_report()
        
        # Close simulation
        controller.close_simulation()
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()

"""
CHAT HISTORY AND DEVELOPMENT NOTES:
====================================

This file represents the current state of the AI Traffic Control System development.
The system includes:

1. Multi-intersection traffic management
2. Simple rule-based AI control logic
3. SUMO integration for traffic simulation
4. Real-time traffic state monitoring
5. Coordinated intersection control

Key Features Implemented:
- Traffic light phase management
- Vehicle counting and direction detection
- Waiting time and speed monitoring
- Intersection coordination
- Performance metrics tracking

The system is designed to work with SUMO traffic simulation and provides
a foundation for more advanced AI traffic control algorithms.

Backup created on: 2024-12-19
Purpose: Preserve chat history and current development state
"""
