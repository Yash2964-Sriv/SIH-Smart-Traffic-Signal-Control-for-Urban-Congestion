#!/usr/bin/env python3
"""
AI Traffic Signal Controller
Real-time AI-controlled traffic signal management for SUMO simulation
"""

import os
import sys
import time
import json
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
import traci
import sumolib
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from dqn_traffic_ai import TrafficSignalController
from sumo_ai_integration import SUMOAIIntegration

class AITrafficController:
    """
    Real-time AI traffic signal controller
    """
    
    def __init__(self, sumo_config: str, model_path: str = None):
        """
        Initialize AI traffic controller
        
        Args:
            sumo_config: Path to SUMO configuration file
            model_path: Path to trained AI model
        """
        self.sumo_config = sumo_config
        self.model_path = model_path or "ai_controller/training_output/models/traffic_ai_final.pth"
        
        # Initialize AI controller
        self.ai_controller = TrafficSignalController()
        
        # Load trained model
        if os.path.exists(self.model_path):
            self.ai_controller.load_model(self.model_path)
            print(f"✅ Loaded trained AI model from {self.model_path}")
        else:
            print(f"⚠️ Model not found at {self.model_path}, using untrained model")
        
        # Initialize SUMO integration
        self.sumo_ai = SUMOAIIntegration(sumo_config, ai_controller=self.ai_controller)
        
        # Control parameters
        self.control_interval = 5.0  # seconds between AI decisions
        self.last_decision_time = 0
        self.is_running = False
        
        # Performance tracking
        self.performance_metrics = {
            'total_waiting_time': 0,
            'total_vehicles_passed': 0,
            'total_switches': 0,
            'avg_waiting_time': 0,
            'throughput': 0,
            'efficiency_score': 0
        }
        
        print(f"🚦 AI Traffic Controller initialized")
        print(f"   Control interval: {self.control_interval}s")
        print(f"   Model: {'Trained' if os.path.exists(self.model_path) else 'Untrained'}")
    
    def start_ai_control(self, gui=True, max_duration=300):
        """
        Start AI-controlled traffic signal management
        
        Args:
            gui: Whether to show SUMO GUI
            max_duration: Maximum simulation duration in seconds
        """
        print(f"\n🚀 Starting AI Traffic Control...")
        print(f"   GUI: {'Enabled' if gui else 'Disabled'}")
        print(f"   Max duration: {max_duration}s")
        print(f"   Control interval: {self.control_interval}s")
        
        # Start SUMO simulation
        if not self.sumo_ai.start_simulation():
            print("❌ Failed to start SUMO simulation")
            return False
        
        self.is_running = True
        start_time = time.time()
        step_count = 0
        
        print(f"\n🎯 AI Control Active - Making real-time decisions...")
        print("=" * 60)
        
        try:
            while self.is_running and (time.time() - start_time) < max_duration:
                current_time = traci.simulation.getTime()
                
                # Check if it's time for AI decision
                if current_time - self.last_decision_time >= self.control_interval:
                    self._make_ai_decision()
                    self.last_decision_time = current_time
                
                # Advance simulation
                traci.simulationStep()
                step_count += 1
                
                # Update performance metrics
                self._update_metrics()
                
                # Print status every 30 seconds
                if step_count % 300 == 0:  # Assuming 0.1s step length
                    self._print_status(current_time)
                
                # Check if simulation ended
                if traci.simulation.getMinExpectedNumber() == 0:
                    print("\n✅ No more vehicles in simulation")
                    break
        
        except KeyboardInterrupt:
            print("\n⏹️ AI Control stopped by user")
        
        except Exception as e:
            print(f"\n❌ Error during AI control: {e}")
        
        finally:
            self.stop_ai_control()
            self._print_final_report()
    
    def _make_ai_decision(self):
        """
        Make AI decision for traffic signal control
        """
        try:
            # Get current traffic state
            state_dict = self.sumo_ai.get_traffic_state()
            
            # Convert to numpy array format expected by AI
            state = np.array([
                state_dict.get('vehicles_north', 0),
                state_dict.get('vehicles_south', 0), 
                state_dict.get('vehicles_east', 0),
                state_dict.get('vehicles_west', 0),
                state_dict.get('current_phase', 0),
                state_dict.get('elapsed_time', 0),
                state_dict.get('queue_length', 0),
                state_dict.get('avg_speed', 0)
            ], dtype=np.float32)
            
            # Get AI action (no exploration during inference)
            action = self.ai_controller.select_action(state, training=False)
            
            # Execute action
            self._execute_action(action)
            
            # Get metrics for this decision
            metrics = self.sumo_ai.get_traffic_state()
            
            # Print decision info
            action_names = ['extend_green_5s', 'extend_green_10s', 'switch_to_ew', 'switch_to_ns']
            print(f"🤖 AI Decision: {action_names[action]} | "
                  f"Vehicles: {metrics['total_vehicles']} | "
                  f"Waiting: {metrics['total_waiting_time']:.1f}s | "
                  f"Phase: {metrics['current_phase']}")
            
        except Exception as e:
            print(f"❌ Error in AI decision: {e}")
    
    def _execute_action(self, action):
        """
        Execute AI action in SUMO
        
        Args:
            action: Action index (0-3)
        """
        junction_id = self.sumo_ai.junction_id
        current_phase = traci.trafficlight.getPhase(junction_id)
        
        if action == 0:  # Extend green by 5s
            if current_phase in [0, 2]:  # Green phases
                current_duration = traci.trafficlight.getPhaseDuration(junction_id)
                traci.trafficlight.setPhaseDuration(junction_id, current_duration + 5)
        
        elif action == 1:  # Extend green by 10s
            if current_phase in [0, 2]:  # Green phases
                current_duration = traci.trafficlight.getPhaseDuration(junction_id)
                traci.trafficlight.setPhaseDuration(junction_id, current_duration + 10)
        
        elif action == 2:  # Switch to EW green
            if current_phase != 2:  # Not already EW green
                traci.trafficlight.setPhase(junction_id, 1)  # Yellow
                time.sleep(0.1)  # Brief pause for yellow
                traci.trafficlight.setPhase(junction_id, 2)  # EW green
                self.performance_metrics['total_switches'] += 1
        
        elif action == 3:  # Switch to NS green
            if current_phase != 0:  # Not already NS green
                traci.trafficlight.setPhase(junction_id, 3)  # Yellow
                time.sleep(0.1)  # Brief pause for yellow
                traci.trafficlight.setPhase(junction_id, 0)  # NS green
                self.performance_metrics['total_switches'] += 1
    
    def _update_metrics(self):
        """
        Update performance metrics
        """
        try:
            metrics = self.sumo_ai.get_traffic_state()
            
            # Safely extract metrics with defaults
            total_waiting_time = metrics.get('total_waiting_time', 0)
            vehicles_passed = metrics.get('vehicles_passed', 0)
            total_vehicles = metrics.get('total_vehicles', 0)
            
            self.performance_metrics['total_waiting_time'] = total_waiting_time
            self.performance_metrics['total_vehicles_passed'] = vehicles_passed
            
            # Calculate average waiting time
            if total_vehicles > 0:
                self.performance_metrics['avg_waiting_time'] = total_waiting_time / total_vehicles
            else:
                self.performance_metrics['avg_waiting_time'] = 0
            
            # Calculate efficiency score (higher is better)
            switches = self.performance_metrics['total_switches']
            
            # Efficiency = throughput - waiting_penalty - switch_penalty
            self.performance_metrics['efficiency_score'] = (
                vehicles_passed * 10 - total_waiting_time * 0.1 - switches * 5
            )
            
        except Exception as e:
            print(f"⚠️ Error updating metrics: {e}")
    
    def _print_status(self, current_time):
        """
        Print current status
        """
        metrics = self.sumo_ai.get_traffic_state()
        print(f"⏰ Time: {current_time:.1f}s | "
              f"Vehicles: {metrics['total_vehicles']} | "
              f"Waiting: {metrics['total_waiting_time']:.1f}s | "
              f"Throughput: {metrics['vehicles_passed']} | "
              f"Efficiency: {self.performance_metrics['efficiency_score']:.1f}")
    
    def stop_ai_control(self):
        """
        Stop AI control and close SUMO
        """
        self.is_running = False
        try:
            traci.close()
        except:
            pass
        print("🛑 AI Control stopped")
    
    def _print_final_report(self):
        """
        Print final performance report
        """
        print("\n" + "=" * 60)
        print("📊 AI TRAFFIC CONTROL PERFORMANCE REPORT")
        print("=" * 60)
        print(f"⏱️ Total waiting time: {self.performance_metrics['total_waiting_time']:.1f}s")
        print(f"🚗 Total vehicles passed: {self.performance_metrics['total_vehicles_passed']}")
        print(f"🔄 Total signal switches: {self.performance_metrics['total_switches']}")
        print(f"📈 Average waiting time: {self.performance_metrics['avg_waiting_time']:.2f}s")
        print(f"🎯 Efficiency score: {self.performance_metrics['efficiency_score']:.1f}")
        print("=" * 60)
    
    def compare_with_fixed_timing(self, duration=300):
        """
        Compare AI control with fixed timing
        
        Args:
            duration: Comparison duration in seconds
        """
        print(f"\n🆚 Starting AI vs Fixed Timing Comparison...")
        print(f"   Duration: {duration}s each")
        
        # Test AI control
        print(f"\n🤖 Testing AI Control...")
        ai_start_time = time.time()
        self.start_ai_control(gui=False, max_duration=duration)
        ai_duration = time.time() - ai_start_time
        ai_metrics = self.performance_metrics.copy()
        
        # Test fixed timing (reset and run with fixed signals)
        print(f"\n⏰ Testing Fixed Timing...")
        self.sumo_ai.close()
        time.sleep(2)
        
        # Start with fixed timing
        if not self.sumo_ai.start(gui=False):
            print("❌ Failed to start fixed timing test")
            return
        
        fixed_start_time = time.time()
        start_time = time.time()
        
        while (time.time() - start_time) < duration:
            traci.simulationStep()
        
        fixed_duration = time.time() - fixed_start_time
        fixed_metrics = self.sumo_ai.get_metrics()
        
        # Print comparison
        print(f"\n" + "=" * 60)
        print("📊 AI vs FIXED TIMING COMPARISON")
        print("=" * 60)
        print(f"🤖 AI Control:")
        print(f"   Waiting time: {ai_metrics['total_waiting_time']:.1f}s")
        print(f"   Throughput: {ai_metrics['total_vehicles_passed']}")
        print(f"   Efficiency: {ai_metrics['efficiency_score']:.1f}")
        print(f"   Switches: {ai_metrics['total_switches']}")
        
        print(f"\n⏰ Fixed Timing:")
        print(f"   Waiting time: {fixed_metrics['total_waiting_time']:.1f}s")
        print(f"   Throughput: {fixed_metrics['throughput']}")
        print(f"   Switches: 0")
        
        # Calculate improvement
        if fixed_metrics['total_waiting_time'] > 0:
            waiting_improvement = (
                (fixed_metrics['total_waiting_time'] - ai_metrics['total_waiting_time']) 
                / fixed_metrics['total_waiting_time'] * 100
            )
            print(f"\n📈 Improvement:")
            print(f"   Waiting time reduction: {waiting_improvement:.1f}%")
        
        print("=" * 60)
        
        self.sumo_ai.close()

def main():
    """
    Main function to run AI traffic control
    """
    print("🚦 AI Traffic Signal Controller")
    print("=" * 40)
    
    # Configuration
    sumo_config = "real_traffic_output/professional_working_config.sumocfg"
    model_path = "ai_controller/training_output/models/traffic_ai_final.pth"
    
    # Check if files exist
    if not os.path.exists(sumo_config):
        print(f"❌ SUMO config not found: {sumo_config}")
        return
    
    if not os.path.exists(model_path):
        print(f"⚠️ Trained model not found: {model_path}")
        print("   Using untrained model...")
    
    # Create AI controller
    controller = AITrafficController(sumo_config, model_path)
    
    try:
        # Start AI control with GUI
        print(f"\n🎮 Starting AI Control with GUI...")
        controller.start_ai_control(gui=True, max_duration=300)
        
        # Ask user for comparison
        response = input(f"\n🆚 Run AI vs Fixed Timing comparison? (y/n): ")
        if response.lower() == 'y':
            controller.compare_with_fixed_timing(duration=180)
    
    except KeyboardInterrupt:
        print(f"\n⏹️ Stopped by user")
    
    except Exception as e:
        print(f"\n❌ Error: {e}")
    
    finally:
        controller.stop_ai_control()
        print(f"\n✅ AI Traffic Control session ended")

if __name__ == "__main__":
    main()
