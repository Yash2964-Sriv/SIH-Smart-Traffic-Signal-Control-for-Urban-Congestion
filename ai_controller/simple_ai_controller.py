#!/usr/bin/env python3
"""
Simple AI Traffic Controller - A more effective approach
This controller uses a rule-based system with some AI elements for better traffic management
"""

import os
import sys
import time
import numpy as np
import traci
from typing import Dict, List, Tuple
import matplotlib.pyplot as plt

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

class SimpleTrafficController:
    """
    Simple but effective traffic signal controller
    Uses rule-based logic with adaptive timing
    """
    
    def __init__(self, junction_id: str = "center"):
        self.junction_id = junction_id
        self.current_phase = 0
        self.phase_start_time = 0
        self.min_phase_time = 10.0  # Minimum 10 seconds per phase
        self.max_phase_time = 60.0  # Maximum 60 seconds per phase
        self.phase_duration = 30.0  # Default phase duration
        
        # Performance tracking
        self.performance_metrics = {
            'total_waiting_time': 0,
            'total_vehicles_passed': 0,
            'total_switches': 0,
            'efficiency_score': 0
        }
        
        print(f"🚦 Simple Traffic Controller initialized")
        print(f"   Junction: {junction_id}")
        print(f"   Min phase time: {self.min_phase_time}s")
        print(f"   Max phase time: {self.max_phase_time}s")
    
    def get_traffic_state(self) -> Dict:
        """Get current traffic state from SUMO"""
        try:
            vehicle_ids = traci.vehicle.getIDList()
            
            # Count vehicles by direction
            vehicles_north = 0
            vehicles_south = 0
            vehicles_east = 0
            vehicles_west = 0
            
            total_waiting_time = 0
            total_speed = 0
            vehicles_passed = 0
            
            for veh_id in vehicle_ids:
                try:
                    speed = traci.vehicle.getSpeed(veh_id)
                    waiting_time = traci.vehicle.getWaitingTime(veh_id)
                    lane_id = traci.vehicle.getLaneID(veh_id)
                    
                    # Categorize by direction
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
            
            current_phase = traci.trafficlight.getPhase(self.junction_id)
            elapsed_time = traci.simulation.getTime() - self.phase_start_time
            
            return {
                'vehicles_north': vehicles_north,
                'vehicles_south': vehicles_south,
                'vehicles_east': vehicles_east,
                'vehicles_west': vehicles_west,
                'current_phase': current_phase,
                'elapsed_time': elapsed_time,
                'total_waiting_time': total_waiting_time,
                'vehicles_passed': vehicles_passed,
                'total_vehicles': len(vehicle_ids),
                'avg_speed': total_speed / len(vehicle_ids) if vehicle_ids else 0
            }
            
        except Exception as e:
            print(f"❌ Error getting traffic state: {e}")
            return {}
    
    def decide_action(self, state: Dict) -> str:
        """
        Decide the next action based on traffic state
        Returns: 'extend', 'switch_to_ns', 'switch_to_ew', 'wait'
        """
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
            if elapsed_time < self.min_phase_time:
                return 'wait'
            
            # If we've been in current phase too long, switch
            if elapsed_time > self.max_phase_time:
                if current_phase in [0, 2]:  # Currently NS
                    return 'switch_to_ew'
                else:  # Currently EW
                    return 'switch_to_ns'
            
            # Adaptive logic based on vehicle counts
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
            print(f"❌ Error in decision making: {e}")
            return 'wait'
    
    def execute_action(self, action: str) -> bool:
        """Execute the decided action"""
        try:
            current_time = traci.simulation.getTime()
            
            if action == 'extend':
                # Extend current phase by 10 seconds
                traci.trafficlight.setPhaseDuration(self.junction_id, 10.0)
                print(f"🟢 Extended current phase by 10s")
                
            elif action == 'switch_to_ns':
                # Switch to North-South green
                traci.trafficlight.setPhase(self.junction_id, 0)
                self.current_phase = 0
                self.phase_start_time = current_time
                self.performance_metrics['total_switches'] += 1
                print(f"🔄 Switched to North-South green")
                
            elif action == 'switch_to_ew':
                # Switch to East-West green
                traci.trafficlight.setPhase(self.junction_id, 1)
                self.current_phase = 1
                self.phase_start_time = current_time
                self.performance_metrics['total_switches'] += 1
                print(f"🔄 Switched to East-West green")
                
            elif action == 'wait':
                # Do nothing, let current phase continue
                pass
                
            return True
            
        except Exception as e:
            print(f"❌ Error executing action {action}: {e}")
            return False
    
    def update_metrics(self, state: Dict):
        """Update performance metrics"""
        try:
            self.performance_metrics['total_waiting_time'] = state.get('total_waiting_time', 0)
            self.performance_metrics['total_vehicles_passed'] = state.get('vehicles_passed', 0)
            
            # Calculate efficiency score
            waiting_time = state.get('total_waiting_time', 0)
            vehicles_passed = state.get('vehicles_passed', 0)
            switches = self.performance_metrics['total_switches']
            
            self.performance_metrics['efficiency_score'] = (
                vehicles_passed * 10 - waiting_time * 0.1 - switches * 5
            )
            
        except Exception as e:
            print(f"⚠️ Error updating metrics: {e}")
    
    def print_status(self, current_time: float, state: Dict):
        """Print current status"""
        try:
            print(f"⏰ Time: {current_time:.1f}s | "
                  f"Vehicles: {state.get('total_vehicles', 0)} | "
                  f"Waiting: {state.get('total_waiting_time', 0.0):.1f}s | "
                  f"Throughput: {state.get('vehicles_passed', 0)} | "
                  f"Phase: {state.get('current_phase', 0)} | "
                  f"Efficiency: {self.performance_metrics['efficiency_score']:.1f}")
        except Exception as e:
            print(f"⚠️ Error printing status: {e}")


class SimpleAITrafficController:
    """
    Main controller class for simple AI traffic management
    """
    
    def __init__(self, sumo_config: str):
        self.sumo_config = sumo_config
        self.traffic_controller = SimpleTrafficController()
        self.is_running = False
        
        print(f"🚦 Simple AI Traffic Controller initialized")
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
            
            # Initialize traffic light
            self.traffic_controller.current_phase = traci.trafficlight.getPhase(self.traffic_controller.junction_id)
            self.traffic_controller.phase_start_time = traci.simulation.getTime()
            
            print(f"🚦 Traffic light initialized - Phase: {self.traffic_controller.current_phase}")
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
            
            print(f"\n🎯 AI Control Active - Making intelligent decisions...")
            print("=" * 60)
            
            while self.is_running and traci.simulation.getTime() - start_time < max_duration:
                current_time = traci.simulation.getTime()
                
                # Get traffic state
                state = self.traffic_controller.get_traffic_state()
                
                # Decide action
                action = self.traffic_controller.decide_action(state)
                
                # Execute action
                self.traffic_controller.execute_action(action)
                
                # Update metrics
                self.traffic_controller.update_metrics(state)
                
                # Print status every 30 seconds
                if int(current_time) % 30 == 0:
                    self.traffic_controller.print_status(current_time, state)
                
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
        print("🛑 AI Control stopped")
    
    def print_performance_report(self):
        """Print performance report"""
        print("\n" + "=" * 60)
        print("📊 AI TRAFFIC CONTROL PERFORMANCE REPORT")
        print("=" * 60)
        print(f"⏱️ Total waiting time: {self.traffic_controller.performance_metrics['total_waiting_time']:.1f}s")
        print(f"🚗 Total vehicles passed: {self.traffic_controller.performance_metrics['total_vehicles_passed']}")
        print(f"🔄 Total signal switches: {self.traffic_controller.performance_metrics['total_switches']}")
        print(f"📈 Average waiting time: {self.traffic_controller.performance_metrics['total_waiting_time'] / max(1, self.traffic_controller.performance_metrics['total_vehicles_passed']):.2f}s")
        print(f"🎯 Efficiency score: {self.traffic_controller.performance_metrics['efficiency_score']:.1f}")
        print("=" * 60)


def main():
    """Main function to run the simple AI traffic controller"""
    print("🚦 Simple AI Traffic Signal Controller")
    print("=" * 50)
    
    # Configuration
    sumo_config = "real_traffic_output/professional_working_config.sumocfg"
    
    # Create controller
    controller = SimpleAITrafficController(sumo_config)
    
    try:
        # Start simulation
        if not controller.start_simulation(gui=True):
            return
        
        # Run control loop
        controller.run_control_loop(max_duration=300.0, control_interval=5.0)
        
        # Print performance report
        controller.print_performance_report()
        
    except KeyboardInterrupt:
        print("\n⏹️ Simulation interrupted by user")
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        controller.stop_control()
        print("\n✅ Simple AI Traffic Control session ended")


if __name__ == "__main__":
    main()
