#!/usr/bin/env python3
"""
Multi-Intersection AI Traffic Controller
Controls traffic signals at multiple intersections (I1 and I2) with intelligent coordination
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

class MultiIntersectionAIController:
    """
    AI controller for multiple intersections with coordinated traffic management
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
        
        print(f"🚦 Multi-Intersection AI Controller initialized")
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
        print("🛑 Multi-Intersection AI Control stopped")
    
    def run_simulation(self, max_duration: float = 300.0, control_interval: float = 5.0):
        """Run the main simulation loop with AI control"""
        try:
            start_time = traci.simulation.getTime()
            
            print(f"\n🎯 Multi-Intersection AI Control Active...")
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
    
    def get_intersection_state(self, junction_id: str) -> Dict:
        """Get traffic state for a specific intersection"""
        try:
            # Get vehicles approaching this intersection
            vehicle_ids = traci.vehicle.getIDList()
            
            vehicles_north = 0
            vehicles_south = 0
            vehicles_east = 0
            vehicles_west = 0
            
            total_waiting_time = 0
            total_speed = 0
            vehicles_passed = 0
            
            # Get junction position
            junction_pos = traci.junction.getPosition(junction_id)
            junction_x, junction_y = junction_pos
            
            for veh_id in vehicle_ids:
                try:
                    pos = traci.vehicle.getPosition(veh_id)
                    speed = traci.vehicle.getSpeed(veh_id)
                    waiting_time = traci.vehicle.getWaitingTime(veh_id)
                    lane_id = traci.vehicle.getLaneID(veh_id)
                    
                    # Check if vehicle is near this intersection (within 50m)
                    distance = np.sqrt((pos[0] - junction_x)**2 + (pos[1] - junction_y)**2)
                    if distance > 50:
                        continue
                    
                    # Categorize by direction based on lane
                    if 'north' in lane_id.lower():
                        vehicles_north += 1
                    elif 'south' in lane_id.lower():
                        vehicles_south += 1
                    elif 'east' in lane_id.lower():
                        vehicles_east += 1
                    elif 'west' in lane_id.lower():
                        vehicles_west += 1
                    
                    total_waiting_time += waiting_time
                    total_speed += speed
                    
                    if speed > 5.0:  # Moving vehicle
                        vehicles_passed += 1
                        
                except:
                    continue
            
            current_phase = traci.trafficlight.getPhase(junction_id)
            elapsed_time = traci.simulation.getTime() - self.controllers[junction_id]['phase_start_time']
            
            return {
                'vehicles_north': vehicles_north,
                'vehicles_south': vehicles_south,
                'vehicles_east': vehicles_east,
                'vehicles_west': vehicles_west,
                'current_phase': current_phase,
                'elapsed_time': elapsed_time,
                'total_waiting_time': total_waiting_time,
                'vehicles_passed': vehicles_passed,
                'total_vehicles': vehicles_north + vehicles_south + vehicles_east + vehicles_west,
                'avg_speed': total_speed / max(1, vehicles_north + vehicles_south + vehicles_east + vehicles_west)
            }
            
        except Exception as e:
            print(f"❌ Error getting state for {junction_id}: {e}")
            return {}
    
    def decide_intersection_action(self, junction_id: str, state: Dict) -> str:
        """Decide action for a specific intersection"""
        try:
            current_phase = state.get('current_phase', 0)
            elapsed_time = state.get('elapsed_time', 0)
            
            vehicles_north = state.get('vehicles_north', 0)
            vehicles_south = state.get('vehicles_south', 0)
            vehicles_east = state.get('vehicles_east', 0)
            vehicles_west = state.get('vehicles_west', 0)
            
            # Calculate total vehicles in each direction
            ns_vehicles = vehicles_north + vehicles_south
            ew_vehicles = vehicles_east + vehicles_west
            
            # Don't switch if we haven't been in current phase long enough
            if elapsed_time < self.controllers[junction_id]['min_phase_time']:
                return 'wait'
            
            # If we've been in current phase too long, switch
            if elapsed_time > self.controllers[junction_id]['max_phase_time']:
                if current_phase in [0, 2]:  # Currently NS
                    return 'switch_to_ew'
                else:  # Currently EW
                    return 'switch_to_ns'
            
            # Intelligent decision making
            if current_phase in [0, 2]:  # Currently NS green
                # If EW has significantly more vehicles, switch
                if ew_vehicles > ns_vehicles * 1.5 and elapsed_time > 15:
                    return 'switch_to_ew'
                # If NS has no vehicles and EW has some, switch
                elif ns_vehicles == 0 and ew_vehicles > 0 and elapsed_time > 20:
                    return 'switch_to_ew'
                else:
                    return 'extend'
                    
            else:  # Currently EW green
                # If NS has significantly more vehicles, switch
                if ns_vehicles > ew_vehicles * 1.5 and elapsed_time > 15:
                    return 'switch_to_ns'
                # If EW has no vehicles and NS has some, switch
                elif ew_vehicles == 0 and ns_vehicles > 0 and elapsed_time > 20:
                    return 'switch_to_ns'
                else:
                    return 'extend'
                    
        except Exception as e:
            print(f"❌ Error in decision making for {junction_id}: {e}")
            return 'wait'
    
    def execute_intersection_action(self, junction_id: str, action: str) -> bool:
        """Execute action for a specific intersection"""
        try:
            current_time = traci.simulation.getTime()
            
            if action == 'extend':
                # Extend current phase by 10 seconds
                traci.trafficlight.setPhaseDuration(junction_id, 10.0)
                print(f"🟢 Extended {junction_id} phase by 10s")
                
            elif action == 'switch_to_ns':
                # Switch to North-South green
                traci.trafficlight.setPhase(junction_id, 0)
                self.controllers[junction_id]['current_phase'] = 0
                self.controllers[junction_id]['phase_start_time'] = current_time
                self.controllers[junction_id]['total_switches'] += 1
                print(f"🔄 Switched {junction_id} to North-South green")
                
            elif action == 'switch_to_ew':
                # Switch to East-West green
                traci.trafficlight.setPhase(junction_id, 1)
                self.controllers[junction_id]['current_phase'] = 1
                self.controllers[junction_id]['phase_start_time'] = current_time
                self.controllers[junction_id]['total_switches'] += 1
                print(f"🔄 Switched {junction_id} to East-West green")
                
            elif action == 'wait':
                # Do nothing, let current phase continue
                pass
                
            return True
            
        except Exception as e:
            print(f"❌ Error executing action {action} for {junction_id}: {e}")
            return False
    
    def coordinate_intersections(self) -> List[Tuple[str, str]]:
        """Coordinate actions across all intersections"""
        actions = []
        current_time = traci.simulation.getTime()
        
        # Get states for all intersections
        states = {}
        for junction_id in self.junction_ids:
            states[junction_id] = self.get_intersection_state(junction_id)
        
        # Decide actions for each intersection
        for junction_id in self.junction_ids:
            state = states[junction_id]
            action = self.decide_intersection_action(junction_id, state)
            actions.append((junction_id, action))
        
        # Apply coordination logic
        # If multiple intersections want to switch, stagger them
        switch_actions = [(j, a) for j, a in actions if a in ['switch_to_ns', 'switch_to_ew']]
        
        if len(switch_actions) > 1 and current_time - self.last_switch_time < self.coordination_delay:
            # Stagger the switches - only allow one at a time
            # Keep the first one, change others to 'wait'
            for i in range(1, len(switch_actions)):
                junction_id = switch_actions[i][0]
                # Find and replace in actions list
                for j, (j_id, action) in enumerate(actions):
                    if j_id == junction_id and action in ['switch_to_ns', 'switch_to_ew']:
                        actions[j] = (j_id, 'wait')
                        break
        
        return actions
    
    def update_metrics(self, states: Dict[str, Dict]):
        """Update performance metrics for all intersections"""
        try:
            total_waiting_time = 0
            total_vehicles_passed = 0
            total_switches = 0
            
            for junction_id, state in states.items():
                waiting_time = state.get('total_waiting_time', 0)
                vehicles_passed = state.get('vehicles_passed', 0)
                switches = self.controllers[junction_id]['total_switches']
                
                total_waiting_time += waiting_time
                total_vehicles_passed += vehicles_passed
                total_switches += switches
                
                # Update individual intersection metrics
                self.controllers[junction_id]['waiting_time'] = waiting_time
                self.controllers[junction_id]['vehicles_passed'] = vehicles_passed
            
            # Calculate global efficiency score
            efficiency_score = (
                total_vehicles_passed * 10 - 
                total_waiting_time * 0.1 - 
                total_switches * 5
            )
            
            return {
                'total_waiting_time': total_waiting_time,
                'total_vehicles_passed': total_vehicles_passed,
                'total_switches': total_switches,
                'efficiency_score': efficiency_score
            }
            
        except Exception as e:
            print(f"⚠️ Error updating metrics: {e}")
            return {}
    
    def print_status(self, current_time: float, states: Dict[str, Dict], metrics: Dict):
        """Print current status for all intersections"""
        try:
            print(f"\n⏰ Time: {current_time:.1f}s | "
                  f"Total Vehicles: {sum(s.get('total_vehicles', 0) for s in states.values())} | "
                  f"Total Waiting: {metrics.get('total_waiting_time', 0.0):.1f}s | "
                  f"Throughput: {metrics.get('total_vehicles_passed', 0)} | "
                  f"Efficiency: {metrics.get('efficiency_score', 0):.1f}")
            
            for junction_id in self.junction_ids:
                state = states.get(junction_id, {})
                print(f"   {junction_id}: Phase {state.get('current_phase', 0)} | "
                      f"NS: {state.get('vehicles_north', 0) + state.get('vehicles_south', 0)} | "
                      f"EW: {state.get('vehicles_east', 0) + state.get('vehicles_west', 0)}")
                      
        except Exception as e:
            print(f"⚠️ Error printing status: {e}")


class MultiIntersectionTrafficController:
    """
    Main controller class for multi-intersection AI traffic management
    """
    
    def __init__(self, sumo_config: str):
        self.sumo_config = sumo_config
        self.ai_controller = MultiIntersectionAIController()
        self.is_running = False
        
        print(f"🚦 Multi-Intersection AI Traffic Controller initialized")
        print(f"   Config: {sumo_config}")
    
    def start_simulation(self, gui: bool = True) -> bool:
        """Start SUMO simulation"""
        try:
            # Use full path to SUMO
            sumo_path = r"C:\Program Files (x86)\Eclipse\Sumo\bin\sumo-gui.exe"
            sumo_cmd_path = r"C:\Program Files (x86)\Eclipse\Sumo\bin\sumo.exe"
            
            # Start SUMO
            if gui:
                traci.start([sumo_path, "-c", self.sumo_config, "--start"])
            else:
                traci.start([sumo_cmd_path, "-c", self.sumo_config, "--start"])
            
            # Initialize traffic lights
            for junction_id in self.ai_controller.junction_ids:
                self.ai_controller.controllers[junction_id]['current_phase'] = traci.trafficlight.getPhase(junction_id)
                self.ai_controller.controllers[junction_id]['phase_start_time'] = traci.simulation.getTime()
            
            print(f"🚦 Traffic lights initialized for {self.ai_controller.junction_ids}")
            print("✅ SUMO simulation started successfully")
            return True
            
        except Exception as e:
            print(f"❌ Failed to start SUMO: {e}")
            return False
    
    def run_control_loop(self, max_duration: float = 300.0, control_interval: float = 5.0):
        """Run the main control loop"""
        try:
            self.is_running = True
            start_time = traci.simulation.getTime()
            
            print(f"\n🎯 Multi-Intersection AI Control Active...")
            print("=" * 60)
            
            while self.is_running and traci.simulation.getTime() - start_time < max_duration:
                current_time = traci.simulation.getTime()
                
                # Get states for all intersections
                states = {}
                for junction_id in self.ai_controller.junction_ids:
                    states[junction_id] = self.ai_controller.get_intersection_state(junction_id)
                
                # Coordinate actions across intersections
                actions = self.ai_controller.coordinate_intersections()
                
                # Execute actions
                for junction_id, action in actions:
                    self.ai_controller.execute_intersection_action(junction_id, action)
                
                # Update metrics
                metrics = self.ai_controller.update_metrics(states)
                
                # Print status every 30 seconds
                if int(current_time) % 30 == 0:
                    self.ai_controller.print_status(current_time, states, metrics)
                
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
    
    def stop_control(self):
        """Stop the control loop"""
        self.is_running = False
        try:
            traci.close()
        except:
            pass
        print("🛑 Multi-Intersection AI Control stopped")
    
    def print_performance_report(self):
        """Print performance report"""
        print("\n" + "=" * 60)
        print("📊 MULTI-INTERSECTION AI TRAFFIC CONTROL PERFORMANCE REPORT")
        print("=" * 60)
        
        total_waiting_time = 0
        total_vehicles_passed = 0
        total_switches = 0
        
        for junction_id in self.ai_controller.junction_ids:
            controller = self.ai_controller.controllers[junction_id]
            waiting_time = controller['waiting_time']
            vehicles_passed = controller['vehicles_passed']
            switches = controller['total_switches']
            
            total_waiting_time += waiting_time
            total_vehicles_passed += vehicles_passed
            total_switches += switches
            
            print(f"🚦 {junction_id}:")
            print(f"   ⏱️ Waiting time: {waiting_time:.1f}s")
            print(f"   🚗 Vehicles passed: {vehicles_passed}")
            print(f"   🔄 Signal switches: {switches}")
        
        print(f"\n📈 GLOBAL METRICS:")
        print(f"⏱️ Total waiting time: {total_waiting_time:.1f}s")
        print(f"🚗 Total vehicles passed: {total_vehicles_passed}")
        print(f"🔄 Total signal switches: {total_switches}")
        print(f"📈 Average waiting time: {total_waiting_time / max(1, total_vehicles_passed):.2f}s")
        print(f"🎯 Efficiency score: {total_vehicles_passed * 10 - total_waiting_time * 0.1 - total_switches * 5:.1f}")
        print("=" * 60)


def main():
    """Main function to run the multi-intersection AI traffic controller"""
    print("🚦 Multi-Intersection AI Traffic Signal Controller")
    print("=" * 60)
    
    # Configuration
    sumo_config = "real_traffic_output/professional_multi_intersection.sumocfg"
    
    # Create controller
    controller = MultiIntersectionAIController(sumo_config=sumo_config)
    
    try:
        # Start simulation
        if not controller.start_simulation(gui=True):
            return
        
        # Run simulation
        controller.run_simulation(max_duration=300.0, control_interval=5.0)
        
        # Print performance report
        controller.print_performance_report()
        
    except KeyboardInterrupt:
        print("\n⏹️ Simulation interrupted by user")
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        controller.close_simulation()
        print("\n✅ Multi-Intersection AI Traffic Control session ended")


if __name__ == "__main__":
    main()
