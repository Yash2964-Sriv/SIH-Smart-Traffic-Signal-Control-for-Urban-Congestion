#!/usr/bin/env python3
"""
SUMO AI Integration Module
Connects DQN AI with SUMO simulation via TraCI
"""

import traci
import sumolib
import numpy as np
import time
import json
from typing import Dict, List, Tuple, Optional
import os
from dqn_traffic_ai import TrafficSignalController, TrafficMetrics

class SUMOAIIntegration:
    """
    Integration between SUMO simulation and DQN AI
    """
    
    def __init__(self, 
                 sumo_config: str,
                 junction_id: str = "center",
                 ai_controller: Optional[TrafficSignalController] = None):
        """
        Initialize SUMO AI integration
        
        Args:
            sumo_config: Path to SUMO configuration file
            junction_id: ID of the traffic light junction to control
            ai_controller: DQN AI controller instance
        """
        self.sumo_config = sumo_config
        self.junction_id = junction_id
        self.ai_controller = ai_controller or TrafficSignalController()
        
        # SUMO connection
        self.sumo_process = None
        self.net = None
        self.simulation_time = 0
        
        # Traffic light state
        self.current_phase = 0
        self.phase_start_time = 0
        self.phase_duration = 0
        
        # Performance tracking
        self.performance_metrics = {
            'total_waiting_time': 0,
            'total_vehicles_passed': 0,
            'total_switches': 0,
            'episode_rewards': []
        }
        
        # Phase definitions
        self.phases = {
            0: "NS_green",  # North-South green
            1: "EW_green"   # East-West green
        }
        
        print(f"🚦 SUMO AI Integration initialized")
        print(f"   Junction ID: {junction_id}")
        print(f"   AI Controller: {'Loaded' if ai_controller else 'New'}")
    
    def start_simulation(self):
        """Start SUMO simulation with TraCI"""
        try:
            # Start SUMO
            sumo_cmd = [
                "C:\\Program Files (x86)\\Eclipse\\Sumo\\bin\\sumo.exe",
                "-c", self.sumo_config,
                "--start"
            ]
            
            traci.start(sumo_cmd)
            
            # Load network
            config_dir = os.path.dirname(self.sumo_config)
            net_file = os.path.join(config_dir, "professional_working_network.net.xml")
            if os.path.exists(net_file):
                self.net = sumolib.net.readNet(net_file)
            else:
                print(f"❌ Network file not found: {net_file}")
                return False
            
            # Initialize traffic light
            self._initialize_traffic_light()
            
            print("✅ SUMO simulation started successfully")
            return True
            
        except Exception as e:
            print(f"❌ Failed to start SUMO: {e}")
            return False
    
    def _initialize_traffic_light(self):
        """Initialize traffic light state"""
        try:
            # Get current phase
            self.current_phase = traci.trafficlight.getPhase(self.junction_id)
            self.phase_start_time = traci.simulation.getTime()
            self.phase_duration = 0
            
            print(f"🚦 Traffic light initialized - Phase: {self.current_phase}")
            
        except Exception as e:
            print(f"❌ Error initializing traffic light: {e}")
    
    def get_traffic_state(self) -> Dict:
        """
        Extract comprehensive traffic state from SUMO
        
        Returns:
            Dictionary containing traffic state data
        """
        try:
            # Get all vehicles
            vehicle_ids = traci.vehicle.getIDList()
            vehicles = {}
            
            # Categorize vehicles by direction
            vehicles_north = 0
            vehicles_south = 0
            vehicles_east = 0
            vehicles_west = 0
            
            total_waiting_time = 0
            total_speed = 0
            vehicles_passed = 0
            
            for veh_id in vehicle_ids:
                try:
                    # Get vehicle data
                    pos = traci.vehicle.getPosition(veh_id)
                    speed = traci.vehicle.getSpeed(veh_id)
                    waiting_time = traci.vehicle.getWaitingTime(veh_id)
                    lane_id = traci.vehicle.getLaneID(veh_id)
                    
                    # Categorize by direction based on lane
                    if 'north' in lane_id.lower():
                        vehicles_north += 1
                    elif 'south' in lane_id.lower():
                        vehicles_south += 1
                    elif 'east' in lane_id.lower():
                        vehicles_east += 1
                    elif 'west' in lane_id.lower():
                        vehicles_west += 1
                    
                    # Track metrics
                    total_waiting_time += waiting_time
                    total_speed += speed
                    
                    # Check if vehicle passed intersection
                    if speed > 5.0:  # Moving at reasonable speed
                        vehicles_passed += 1
                    
                    vehicles[veh_id] = {
                        'position': pos,
                        'speed': speed,
                        'waiting_time': waiting_time,
                        'lane_id': lane_id,
                        'passed_intersection': speed > 5.0
                    }
                    
                except Exception as e:
                    continue  # Skip invalid vehicles
            
            # Get traffic light state
            current_phase = traci.trafficlight.getPhase(self.junction_id)
            elapsed_time = traci.simulation.getTime() - self.phase_start_time
            
            # Calculate metrics
            avg_waiting_time = total_waiting_time / len(vehicles) if vehicles else 0
            avg_speed = total_speed / len(vehicles) if vehicles else 0
            queue_length = len([v for v in vehicles.values() if v['speed'] < 1.0])
            
            state = {
                'vehicles_north': vehicles_north,
                'vehicles_south': vehicles_south,
                'vehicles_east': vehicles_east,
                'vehicles_west': vehicles_west,
                'current_phase': current_phase,
                'elapsed_time': elapsed_time,
                'queue_length': queue_length,
                'avg_speed': avg_speed,
                'total_vehicles': len(vehicles),
                'vehicles_passed': vehicles_passed,
                'total_waiting_time': total_waiting_time,
                'avg_waiting_time': avg_waiting_time
            }
            
            return state
            
        except Exception as e:
            print(f"❌ Error getting traffic state: {e}")
            return {}
    
    def execute_action(self, action: int) -> bool:
        """
        Execute AI action on traffic light
        
        Args:
            action: Action index from AI controller
            
        Returns:
            True if action executed successfully
        """
        try:
            current_time = traci.simulation.getTime()
            current_phase = traci.trafficlight.getPhase(self.junction_id)
            
            # Only allow phase changes if we've been in current phase for at least 5 seconds
            min_phase_time = 5.0
            time_in_phase = current_time - self.phase_start_time
            
            if action == 0:  # extend_green_5s
                # Extend current green phase by 5 seconds
                if current_phase in [0, 2]:  # NS green phases
                    traci.trafficlight.setPhaseDuration(self.junction_id, 5.0)
                    print(f"🟢 Extended NS green by 5s")
                elif current_phase in [1, 3]:  # EW green phases
                    traci.trafficlight.setPhaseDuration(self.junction_id, 5.0)
                    print(f"🟢 Extended EW green by 5s")
                
            elif action == 1:  # extend_green_10s
                # Extend current green phase by 10 seconds
                if current_phase in [0, 2]:  # NS green phases
                    traci.trafficlight.setPhaseDuration(self.junction_id, 10.0)
                    print(f"🟢 Extended NS green by 10s")
                elif current_phase in [1, 3]:  # EW green phases
                    traci.trafficlight.setPhaseDuration(self.junction_id, 10.0)
                    print(f"🟢 Extended EW green by 10s")
                
            elif action == 2:  # switch_to_ew
                # Switch to East-West green (only if enough time has passed)
                if time_in_phase >= min_phase_time and current_phase not in [1, 3]:
                    traci.trafficlight.setPhase(self.junction_id, 1)
                    self.current_phase = 1
                    self.phase_start_time = current_time
                    self.performance_metrics['total_switches'] += 1
                    print(f"🔄 Switched to EW green")
                else:
                    print(f"⏳ Cannot switch to EW - only {time_in_phase:.1f}s in current phase")
                
            elif action == 3:  # switch_to_ns
                # Switch to North-South green (only if enough time has passed)
                if time_in_phase >= min_phase_time and current_phase not in [0, 2]:
                    traci.trafficlight.setPhase(self.junction_id, 0)
                    self.current_phase = 0
                    self.phase_start_time = current_time
                    self.performance_metrics['total_switches'] += 1
                    print(f"🔄 Switched to NS green")
                else:
                    print(f"⏳ Cannot switch to NS - only {time_in_phase:.1f}s in current phase")
            
            return True
            
        except Exception as e:
            print(f"❌ Error executing action {action}: {e}")
            return False
    
    def calculate_reward(self, state: Dict, action: int) -> float:
        """
        Calculate reward for AI action
        
        Args:
            state: Current traffic state
            action: Action taken
            
        Returns:
            Reward value
        """
        # Get state values
        total_waiting_time = state.get('total_waiting_time', 0)
        vehicles_passed = state.get('vehicles_passed', 0)
        queue_length = state.get('queue_length', 0)
        avg_speed = state.get('avg_speed', 0)
        total_vehicles = state.get('total_vehicles', 0)
        
        # Reward components
        # 1. Penalty for waiting time (higher penalty for more waiting)
        waiting_penalty = -total_waiting_time * 0.01
        
        # 2. Reward for vehicles passing through
        throughput_reward = vehicles_passed * 2.0
        
        # 3. Penalty for queue length
        queue_penalty = -queue_length * 0.5
        
        # 4. Reward for maintaining good speed
        speed_reward = avg_speed * 0.1 if avg_speed > 5.0 else 0
        
        # 5. Penalty for frequent switching (to avoid oscillation)
        switching_penalty = -0.5 if action in [2, 3] else 0
        
        # 6. Bonus for clearing traffic
        clear_bonus = 5.0 if queue_length == 0 and total_vehicles > 0 else 0
        
        # 7. Penalty for having too many vehicles waiting
        congestion_penalty = -total_vehicles * 0.1 if total_vehicles > 10 else 0
        
        # Total reward
        reward = (waiting_penalty + throughput_reward + queue_penalty + 
                 speed_reward + switching_penalty + clear_bonus + congestion_penalty)
        
        return reward
    
    def run_ai_episode(self, max_steps: int = 1000, training: bool = True) -> Dict:
        """
        Run one episode of AI-controlled simulation
        
        Args:
            max_steps: Maximum simulation steps
            training: Whether to train the AI
            
        Returns:
            Episode performance metrics
        """
        if not self.start_simulation():
            return {}
        
        episode_metrics = {
            'total_reward': 0,
            'total_waiting_time': 0,
            'total_vehicles_passed': 0,
            'total_switches': 0,
            'steps': 0
        }
        
        try:
            for step in range(max_steps):
                # Get current state
                state = self.get_traffic_state()
                if not state:
                    break
                
                # AI selects action
                state_vector = self.ai_controller.get_state(state)
                action = self.ai_controller.select_action(state_vector, training=training)
                
                # Execute action
                action_success = self.execute_action(action)
                
                # Advance simulation
                traci.simulationStep()
                self.simulation_time = traci.simulation.getTime()
                
                # Get next state
                next_state = self.get_traffic_state()
                if not next_state:
                    break
                
                # Calculate reward
                reward = self.calculate_reward(state, action)
                
                # Store experience for training
                if training:
                    next_state_vector = self.ai_controller.get_state(next_state)
                    done = step >= max_steps - 1
                    self.ai_controller.remember(state_vector, action, reward, next_state_vector, done)
                    
                    # Train the AI
                    if len(self.ai_controller.memory) > self.ai_controller.batch_size:
                        loss = self.ai_controller.replay()
                        if step % 100 == 0:
                            print(f"Step {step}: Loss = {loss:.4f}, Reward = {reward:.2f}")
                
                # Update metrics
                episode_metrics['total_reward'] += reward
                episode_metrics['total_waiting_time'] += state.get('avg_waiting_time', 0)
                episode_metrics['total_vehicles_passed'] += state.get('vehicles_passed', 0)
                episode_metrics['steps'] = step + 1
                
                # Print progress
                if step % 100 == 0:
                    print(f"Step {step}: Vehicles = {state.get('total_vehicles', 0)}, "
                          f"Waiting = {state.get('avg_waiting_time', 0):.2f}s, "
                          f"Action = {self.ai_controller.get_action_description(action)}")
            
            # Update target network
            if training and step % 50 == 0:
                self.ai_controller.update_target_network()
            
            print(f"✅ Episode completed: {episode_metrics['steps']} steps, "
                  f"Reward = {episode_metrics['total_reward']:.2f}")
            
        except Exception as e:
            print(f"❌ Error in episode: {e}")
        
        finally:
            traci.close()
        
        return episode_metrics
    
    def run_training(self, num_episodes: int = 100):
        """Run training episodes"""
        print(f"🎓 Starting AI training for {num_episodes} episodes...")
        
        for episode in range(num_episodes):
            print(f"\n📚 Episode {episode + 1}/{num_episodes}")
            
            # Run episode
            metrics = self.run_ai_episode(training=True)
            
            # Store episode metrics
            self.ai_controller.training_metrics['episode_rewards'].append(metrics['total_reward'])
            self.ai_controller.training_metrics['episode_waiting_times'].append(metrics['total_waiting_time'])
            self.ai_controller.training_metrics['episode_throughputs'].append(metrics['total_vehicles_passed'])
            
            # Print progress
            if episode % 10 == 0:
                stats = self.ai_controller.get_training_stats()
                print(f"📊 Training Stats: Avg Reward = {stats.get('avg_reward', 0):.2f}, "
                      f"Epsilon = {stats.get('epsilon', 0):.3f}")
        
        print("✅ Training completed!")
        
        # Save trained model
        model_path = "ai_controller/trained_traffic_ai.pth"
        self.ai_controller.save_model(model_path)
    
    def run_inference(self, max_steps: int = 1000):
        """Run inference with trained AI"""
        print("🚀 Running AI inference...")
        
        # Load trained model
        model_path = "ai_controller/trained_traffic_ai.pth"
        self.ai_controller.load_model(model_path)
        
        # Run episode without training
        metrics = self.run_ai_episode(max_steps, training=False)
        
        print(f"✅ Inference completed: {metrics}")
        return metrics
    
    def start(self, gui=False):
        """
        Start SUMO simulation (alias for start_simulation)
        """
        return self.start_simulation()
    
    def close(self):
        """
        Close SUMO connection
        """
        try:
            traci.close()
        except:
            pass

def main():
    """Test the SUMO AI integration"""
    print("🧠 Testing SUMO AI Integration")
    print("=" * 50)
    
    # Configuration
    sumo_config = "real_traffic_output/professional_working_config.sumocfg"
    
    # Create AI controller
    ai_controller = TrafficSignalController()
    
    # Create SUMO integration
    sumo_ai = SUMOAIIntegration(sumo_config, ai_controller=ai_controller)
    
    # Test state extraction
    if sumo_ai.start_simulation():
        state = sumo_ai.get_traffic_state()
        print(f"✅ Traffic state extracted: {state}")
        
        # Test action execution
        action = ai_controller.select_action(ai_controller.get_state(state))
        print(f"✅ Action selected: {action} - {ai_controller.get_action_description(action)}")
        
        success = sumo_ai.execute_action(action)
        print(f"✅ Action executed: {success}")
        
        traci.close()
    
    print("🎉 SUMO AI Integration test completed!")

if __name__ == "__main__":
    main()
