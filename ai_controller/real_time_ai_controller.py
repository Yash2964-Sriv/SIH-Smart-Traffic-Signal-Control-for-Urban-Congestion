#!/usr/bin/env python3
"""
Real-Time AI Traffic Controller
Live traffic signal control with dashboard integration
"""

import time
import json
import threading
from datetime import datetime
from typing import Dict, List, Optional
import os
from dqn_traffic_ai import TrafficSignalController
from sumo_ai_integration import SUMOAIIntegration

class RealTimeAIController:
    """
    Real-time AI traffic controller with dashboard integration
    """
    
    def __init__(self, 
                 sumo_config: str,
                 model_path: str = "ai_controller/trained_traffic_ai.pth",
                 control_interval: float = 5.0):
        """
        Initialize real-time AI controller
        
        Args:
            sumo_config: Path to SUMO configuration file
            model_path: Path to trained AI model
            control_interval: Time interval between AI decisions (seconds)
        """
        self.sumo_config = sumo_config
        self.model_path = model_path
        self.control_interval = control_interval
        
        # AI controller
        self.ai_controller = TrafficSignalController()
        self.load_trained_model()
        
        # SUMO integration
        self.sumo_ai = None
        
        # Control state
        self.is_running = False
        self.control_thread = None
        
        # Performance tracking
        self.performance_data = {
            'timestamp': [],
            'waiting_times': [],
            'throughputs': [],
            'queue_lengths': [],
            'actions_taken': [],
            'rewards': []
        }
        
        # Dashboard data
        self.dashboard_data = {
            'current_state': {},
            'performance_metrics': {},
            'ai_status': 'stopped',
            'last_update': None
        }
        
        print(f"🚦 Real-Time AI Controller initialized")
        print(f"   Model: {model_path}")
        print(f"   Control interval: {control_interval}s")
    
    def load_trained_model(self):
        """Load trained AI model"""
        if os.path.exists(self.model_path):
            self.ai_controller.load_model(self.model_path)
            print(f"✅ Trained model loaded: {self.model_path}")
        else:
            print(f"⚠️ Trained model not found: {self.model_path}")
            print("   Using untrained model (random actions)")
    
    def start_ai_control(self):
        """Start real-time AI control"""
        if self.is_running:
            print("⚠️ AI control is already running")
            return False
        
        try:
            # Initialize SUMO integration
            self.sumo_ai = SUMOAIIntegration(self.sumo_config, ai_controller=self.ai_controller)
            
            if not self.sumo_ai.start_simulation():
                print("❌ Failed to start SUMO simulation")
                return False
            
            # Start control thread
            self.is_running = True
            self.control_thread = threading.Thread(target=self._control_loop)
            self.control_thread.daemon = True
            self.control_thread.start()
            
            print("🚀 Real-time AI control started")
            return True
            
        except Exception as e:
            print(f"❌ Error starting AI control: {e}")
            return False
    
    def stop_ai_control(self):
        """Stop real-time AI control"""
        if not self.is_running:
            print("⚠️ AI control is not running")
            return
        
        self.is_running = False
        
        if self.control_thread:
            self.control_thread.join(timeout=5.0)
        
        # Close SUMO connection
        if self.sumo_ai:
            try:
                import traci
                traci.close()
            except:
                pass
        
        print("⏹️ Real-time AI control stopped")
    
    def _control_loop(self):
        """Main control loop"""
        print("🔄 Starting AI control loop...")
        
        while self.is_running:
            try:
                # Get current traffic state
                state = self.sumo_ai.get_traffic_state()
                if not state:
                    time.sleep(1.0)
                    continue
                
                # AI selects action
                state_vector = self.ai_controller.get_state(state)
                action = self.ai_controller.select_action(state_vector, training=False)
                
                # Execute action
                action_success = self.sumo_ai.execute_action(action)
                
                # Calculate reward
                reward = self.sumo_ai.calculate_reward(state, action)
                
                # Update performance data
                self._update_performance_data(state, action, reward)
                
                # Update dashboard data
                self._update_dashboard_data(state, action, reward)
                
                # Advance simulation
                import traci
                traci.simulationStep()
                
                # Print status
                print(f"🔄 AI Action: {self.ai_controller.get_action_description(action)} | "
                      f"Vehicles: {state.get('total_vehicles', 0)} | "
                      f"Waiting: {state.get('avg_waiting_time', 0):.1f}s | "
                      f"Reward: {reward:.2f}")
                
                # Wait for next control cycle
                time.sleep(self.control_interval)
                
            except Exception as e:
                print(f"❌ Error in control loop: {e}")
                time.sleep(1.0)
    
    def _update_performance_data(self, state: Dict, action: int, reward: float):
        """Update performance tracking data"""
        timestamp = datetime.now().isoformat()
        
        self.performance_data['timestamp'].append(timestamp)
        self.performance_data['waiting_times'].append(state.get('avg_waiting_time', 0))
        self.performance_data['throughputs'].append(state.get('vehicles_passed', 0))
        self.performance_data['queue_lengths'].append(state.get('queue_length', 0))
        self.performance_data['actions_taken'].append(action)
        self.performance_data['rewards'].append(reward)
        
        # Keep only last 1000 data points
        max_points = 1000
        for key in self.performance_data:
            if len(self.performance_data[key]) > max_points:
                self.performance_data[key] = self.performance_data[key][-max_points:]
    
    def _update_dashboard_data(self, state: Dict, action: int, reward: float):
        """Update dashboard data"""
        self.dashboard_data['current_state'] = state
        self.dashboard_data['performance_metrics'] = {
            'avg_waiting_time': np.mean(self.performance_data['waiting_times'][-10:]) if self.performance_data['waiting_times'] else 0,
            'avg_throughput': np.mean(self.performance_data['throughputs'][-10:]) if self.performance_data['throughputs'] else 0,
            'avg_queue_length': np.mean(self.performance_data['queue_lengths'][-10:]) if self.performance_data['queue_lengths'] else 0,
            'total_reward': sum(self.performance_data['rewards'][-100:]) if self.performance_data['rewards'] else 0
        }
        self.dashboard_data['ai_status'] = 'running' if self.is_running else 'stopped'
        self.dashboard_data['last_update'] = datetime.now().isoformat()
    
    def get_dashboard_data(self) -> Dict:
        """Get current dashboard data"""
        return self.dashboard_data.copy()
    
    def get_performance_data(self) -> Dict:
        """Get performance data for analysis"""
        return self.performance_data.copy()
    
    def save_performance_report(self, filepath: str = None):
        """Save performance report"""
        if not filepath:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filepath = f"ai_controller/performance_report_{timestamp}.json"
        
        report_data = {
            'timestamp': datetime.now().isoformat(),
            'control_interval': self.control_interval,
            'model_path': self.model_path,
            'performance_data': self.performance_data,
            'dashboard_data': self.dashboard_data
        }
        
        with open(filepath, 'w') as f:
            json.dump(report_data, f, indent=2)
        
        print(f"📊 Performance report saved: {filepath}")
        return filepath
    
    def compare_with_baseline(self, baseline_data: Dict) -> Dict:
        """Compare AI performance with baseline"""
        if not self.performance_data['waiting_times']:
            return {}
        
        ai_avg_waiting = np.mean(self.performance_data['waiting_times'][-100:])
        ai_avg_throughput = np.mean(self.performance_data['throughputs'][-100:])
        
        baseline_avg_waiting = baseline_data.get('avg_waiting_time', 0)
        baseline_avg_throughput = baseline_data.get('avg_throughput', 0)
        
        improvement = {
            'waiting_time_improvement': ((baseline_avg_waiting - ai_avg_waiting) / baseline_avg_waiting * 100) if baseline_avg_waiting > 0 else 0,
            'throughput_improvement': ((ai_avg_throughput - baseline_avg_throughput) / baseline_avg_throughput * 100) if baseline_avg_throughput > 0 else 0,
            'ai_waiting_time': ai_avg_waiting,
            'baseline_waiting_time': baseline_avg_waiting,
            'ai_throughput': ai_avg_throughput,
            'baseline_throughput': baseline_avg_throughput
        }
        
        return improvement

def main():
    """Test real-time AI controller"""
    print("🚦 Testing Real-Time AI Controller")
    print("=" * 50)
    
    # Configuration
    sumo_config = "real_traffic_output/professional_working_config.sumocfg"
    model_path = "ai_controller/trained_traffic_ai.pth"
    
    # Create controller
    controller = RealTimeAIController(sumo_config, model_path, control_interval=2.0)
    
    try:
        # Start AI control
        if controller.start_ai_control():
            print("✅ AI control started successfully")
            
            # Run for 30 seconds
            print("🔄 Running for 30 seconds...")
            time.sleep(30)
            
            # Get dashboard data
            dashboard_data = controller.get_dashboard_data()
            print(f"📊 Dashboard data: {dashboard_data}")
            
            # Save performance report
            controller.save_performance_report()
            
        else:
            print("❌ Failed to start AI control")
    
    except KeyboardInterrupt:
        print("\n⏹️ Stopping AI control...")
    
    finally:
        controller.stop_ai_control()
        print("✅ Test completed")

if __name__ == "__main__":
    import numpy as np
    main()

