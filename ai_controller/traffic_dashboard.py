#!/usr/bin/env python3
"""
Traffic Control Dashboard
Real-time visualization of AI traffic signal control
"""

import os
import sys
import time
import json
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
import threading
import queue
from collections import deque
import traci
import sumolib
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ai_traffic_controller import AITrafficController

class TrafficDashboard:
    """
    Real-time traffic control dashboard
    """
    
    def __init__(self, sumo_config: str, model_path: str = None):
        """
        Initialize dashboard
        
        Args:
            sumo_config: Path to SUMO configuration file
            model_path: Path to trained AI model
        """
        self.sumo_config = sumo_config
        self.model_path = model_path or "ai_controller/training_output/models/traffic_ai_final.pth"
        
        # Data storage
        self.data_buffer = {
            'time': deque(maxlen=1000),
            'waiting_time': deque(maxlen=1000),
            'vehicles_count': deque(maxlen=1000),
            'throughput': deque(maxlen=1000),
            'efficiency': deque(maxlen=1000),
            'current_phase': deque(maxlen=1000),
            'ai_actions': deque(maxlen=100)
        }
        
        # Control flags
        self.is_running = False
        self.update_interval = 1.0  # seconds
        
        # AI Controller
        self.ai_controller = AITrafficController(sumo_config, model_path)
        
        print(f"📊 Traffic Dashboard initialized")
        print(f"   Update interval: {self.update_interval}s")
    
    def start_dashboard(self, gui=True, max_duration=600):
        """
        Start the traffic control dashboard
        
        Args:
            gui: Whether to show SUMO GUI
            max_duration: Maximum simulation duration in seconds
        """
        print(f"\n🚀 Starting Traffic Control Dashboard...")
        print(f"   GUI: {'Enabled' if gui else 'Disabled'}")
        print(f"   Max duration: {max_duration}s")
        
        # Start SUMO simulation
        if not self.ai_controller.sumo_ai.start(gui=gui):
            print("❌ Failed to start SUMO simulation")
            return False
        
        self.is_running = True
        start_time = time.time()
        step_count = 0
        
        print(f"\n📊 Dashboard Active - Real-time monitoring...")
        print("=" * 60)
        
        try:
            while self.is_running and (time.time() - start_time) < max_duration:
                current_time = traci.simulation.getTime()
                
                # Update data
                self._update_data(current_time)
                
                # Make AI decision every 5 seconds
                if step_count % 50 == 0:  # Assuming 0.1s step length
                    self._make_ai_decision()
                
                # Update dashboard every second
                if step_count % 10 == 0:
                    self._update_dashboard(current_time)
                
                # Advance simulation
                traci.simulationStep()
                step_count += 1
                
                # Check if simulation ended
                if traci.simulation.getMinExpectedNumber() == 0:
                    print("\n✅ No more vehicles in simulation")
                    break
        
        except KeyboardInterrupt:
            print("\n⏹️ Dashboard stopped by user")
        
        except Exception as e:
            print(f"\n❌ Error in dashboard: {e}")
        
        finally:
            self.stop_dashboard()
            self._generate_final_report()
    
    def _update_data(self, current_time):
        """
        Update data buffer with current metrics
        
        Args:
            current_time: Current simulation time
        """
        try:
            metrics = self.ai_controller.sumo_ai.get_metrics()
            
            self.data_buffer['time'].append(current_time)
            self.data_buffer['waiting_time'].append(metrics['total_waiting_time'])
            self.data_buffer['vehicles_count'].append(metrics['num_vehicles_waiting'])
            self.data_buffer['throughput'].append(metrics['throughput'])
            self.data_buffer['current_phase'].append(metrics['current_phase'])
            
            # Calculate efficiency
            efficiency = metrics['throughput'] * 10 - metrics['total_waiting_time'] * 0.1
            self.data_buffer['efficiency'].append(efficiency)
            
        except Exception as e:
            print(f"⚠️ Error updating data: {e}")
    
    def _make_ai_decision(self):
        """
        Make AI decision for traffic control
        """
        try:
            # Get current state
            state = self.ai_controller.sumo_ai.get_state()
            
            # Get AI action
            action = self.ai_controller.ai_controller.select_action(state, training=False)
            
            # Execute action
            self.ai_controller._execute_action(action)
            
            # Store action
            action_names = ['extend_green_5s', 'extend_green_10s', 'switch_to_ew', 'switch_to_ns']
            self.data_buffer['ai_actions'].append({
                'time': traci.simulation.getTime(),
                'action': action_names[action],
                'action_id': action
            })
            
        except Exception as e:
            print(f"❌ Error in AI decision: {e}")
    
    def _update_dashboard(self, current_time):
        """
        Update and display dashboard information
        
        Args:
            current_time: Current simulation time
        """
        try:
            # Get latest metrics
            metrics = self.ai_controller.sumo_ai.get_metrics()
            
            # Clear screen and display dashboard
            os.system('cls' if os.name == 'nt' else 'clear')
            
            print("🚦 AI TRAFFIC CONTROL DASHBOARD")
            print("=" * 50)
            print(f"⏰ Simulation Time: {current_time:.1f}s")
            print(f"🚗 Vehicles Waiting: {metrics['num_vehicles_waiting']}")
            print(f"⏱️ Total Waiting Time: {metrics['total_waiting_time']:.1f}s")
            print(f"🚦 Current Phase: {metrics['current_phase']}")
            print(f"📈 Throughput: {metrics['throughput']} vehicles")
            print(f"🔄 Signal Switches: {self.ai_controller.performance_metrics['total_switches']}")
            
            # Display recent AI actions
            print(f"\n🤖 Recent AI Actions:")
            recent_actions = list(self.data_buffer['ai_actions'])[-5:]
            for action_data in recent_actions:
                print(f"   {action_data['time']:.1f}s: {action_data['action']}")
            
            # Display performance trends
            if len(self.data_buffer['time']) > 10:
                print(f"\n📊 Performance Trends:")
                recent_waiting = list(self.data_buffer['waiting_time'])[-10:]
                recent_throughput = list(self.data_buffer['throughput'])[-10:]
                
                avg_waiting = np.mean(recent_waiting)
                avg_throughput = np.mean(recent_throughput)
                
                print(f"   Avg Waiting (last 10s): {avg_waiting:.1f}s")
                print(f"   Avg Throughput (last 10s): {avg_throughput:.1f}")
            
            print("=" * 50)
            print("Press Ctrl+C to stop")
            
        except Exception as e:
            print(f"⚠️ Error updating dashboard: {e}")
    
    def _generate_final_report(self):
        """
        Generate final performance report
        """
        print(f"\n" + "=" * 60)
        print("📊 FINAL TRAFFIC CONTROL REPORT")
        print("=" * 60)
        
        if len(self.data_buffer['time']) > 0:
            # Calculate statistics
            total_time = max(self.data_buffer['time']) - min(self.data_buffer['time'])
            avg_waiting = np.mean(self.data_buffer['waiting_time'])
            max_waiting = np.max(self.data_buffer['waiting_time'])
            total_throughput = max(self.data_buffer['throughput'])
            total_switches = len(self.data_buffer['ai_actions'])
            
            print(f"⏱️ Simulation Duration: {total_time:.1f}s")
            print(f"📈 Average Waiting Time: {avg_waiting:.2f}s")
            print(f"📊 Maximum Waiting Time: {max_waiting:.1f}s")
            print(f"🚗 Total Vehicles Processed: {total_throughput}")
            print(f"🔄 Total AI Decisions: {total_switches}")
            
            # Calculate efficiency
            if total_time > 0:
                efficiency = (total_throughput / total_time) * 60  # vehicles per minute
                print(f"🎯 Processing Rate: {efficiency:.1f} vehicles/min")
            
            # Action breakdown
            action_counts = {}
            for action_data in self.data_buffer['ai_actions']:
                action = action_data['action']
                action_counts[action] = action_counts.get(action, 0) + 1
            
            print(f"\n🤖 AI Action Breakdown:")
            for action, count in action_counts.items():
                percentage = (count / total_switches) * 100 if total_switches > 0 else 0
                print(f"   {action}: {count} ({percentage:.1f}%)")
        
        print("=" * 60)
    
    def stop_dashboard(self):
        """
        Stop dashboard and close SUMO
        """
        self.is_running = False
        self.ai_controller.stop_ai_control()
        print("🛑 Dashboard stopped")
    
    def save_data(self, filename=None):
        """
        Save collected data to file
        
        Args:
            filename: Output filename
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"ai_controller/training_output/logs/dashboard_data_{timestamp}.json"
        
        # Convert deques to lists for JSON serialization
        data = {}
        for key, value in self.data_buffer.items():
            data[key] = list(value)
        
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
        
        print(f"💾 Dashboard data saved to: {filename}")

def main():
    """
    Main function to run traffic dashboard
    """
    print("📊 Traffic Control Dashboard")
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
    
    # Create dashboard
    dashboard = TrafficDashboard(sumo_config, model_path)
    
    try:
        # Start dashboard
        dashboard.start_dashboard(gui=True, max_duration=600)
        
        # Ask user to save data
        response = input(f"\n💾 Save dashboard data? (y/n): ")
        if response.lower() == 'y':
            dashboard.save_data()
    
    except KeyboardInterrupt:
        print(f"\n⏹️ Stopped by user")
    
    except Exception as e:
        print(f"\n❌ Error: {e}")
    
    finally:
        dashboard.stop_dashboard()
        print(f"\n✅ Dashboard session ended")

if __name__ == "__main__":
    main()
