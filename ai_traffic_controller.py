#!/usr/bin/env python3
"""
AI Traffic Controller - Real-time traffic light control using RL
"""

import os
import sys
import time
import json
import traci
import numpy as np
from datetime import datetime
from typing import Dict, List, Tuple
import logging

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from master_ai_rl_trainer import MasterAIRLTrainer

class AITrafficController:
    """AI-controlled traffic light system"""
    
    def __init__(self):
        self.rl_trainer = MasterAIRLTrainer()
        self.traffic_lights = ['I1', 'I2']  # Traffic light IDs
        self.control_interval = 5  # Control every 5 seconds
        self.last_control_time = 0
        
        # Performance tracking
        self.performance_data = {
            'total_vehicles': 0,
            'waiting_times': [],
            'queue_lengths': [],
            'throughput': 0,
            'ai_decisions': []
        }
        
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    def get_traffic_state(self) -> Dict:
        """Get current traffic state from SUMO"""
        state = {
            'queue_lengths': {},
            'waiting_times': {},
            'vehicle_counts': {},
            'flow_rates': {},
            'current_phase': {},
            'phase_duration': {},
            'efficiency_scores': {}
        }
        
        try:
            # Get queue lengths for each traffic light
            for tl_id in self.traffic_lights:
                if traci.trafficlight.getIDList() and tl_id in traci.trafficlight.getIDList():
                    # Get waiting vehicles
                    waiting_vehicles = traci.trafficlight.getControlledLanes(tl_id)
                    queue_length = 0
                    for lane in waiting_vehicles:
                        queue_length += traci.lane.getLastStepHaltingNumber(lane)
                    
                    state['queue_lengths'][tl_id] = queue_length
                    
                    # Get current phase
                    state['current_phase'][tl_id] = traci.trafficlight.getPhase(tl_id)
                    
                    # Get phase duration
                    state['phase_duration'][tl_id] = traci.trafficlight.getPhaseDuration(tl_id)
            
            # Get vehicle counts by direction
            vehicle_list = traci.vehicle.getIDList()
            state['vehicle_counts'] = {
                'north': len([v for v in vehicle_list if 'north' in v]),
                'south': len([v for v in vehicle_list if 'south' in v]),
                'east': len([v for v in vehicle_list if 'east' in v]),
                'west': len([v for v in vehicle_list if 'west' in v])
            }
            
            # Calculate flow rates
            for direction in ['north', 'south', 'east', 'west']:
                state['flow_rates'][direction] = state['vehicle_counts'][direction] * 10
            
            # Calculate efficiency scores
            avg_queue = np.mean(list(state['queue_lengths'].values())) if state['queue_lengths'] else 0
            state['efficiency_scores'] = {
                'throughput': max(0, 100 - avg_queue * 2),
                'waiting_time': max(0, 100 - avg_queue * 5),
                'speed': max(0, 100 - avg_queue * 3)
            }
            
        except Exception as e:
            self.logger.error(f"Error getting traffic state: {e}")
        
        return state
    
    def apply_ai_decision(self, action: int, traffic_state: Dict):
        """Apply AI decision to traffic lights"""
        try:
            if action == 0:  # Change phase
                for tl_id in self.traffic_lights:
                    if tl_id in traci.trafficlight.getIDList():
                        current_phase = traci.trafficlight.getPhase(tl_id)
                        new_phase = (current_phase + 1) % 4
                        traci.trafficlight.setPhase(tl_id, new_phase)
            
            elif action == 1:  # Extend green time
                for tl_id in self.traffic_lights:
                    if tl_id in traci.trafficlight.getIDList():
                        current_duration = traci.trafficlight.getPhaseDuration(tl_id)
                        traci.trafficlight.setPhaseDuration(tl_id, current_duration + 5)
            
            elif action == 2:  # Reduce cycle time
                for tl_id in self.traffic_lights:
                    if tl_id in traci.trafficlight.getIDList():
                        current_duration = traci.trafficlight.getPhaseDuration(tl_id)
                        traci.trafficlight.setPhaseDuration(tl_id, max(10, current_duration - 5))
            
            elif action == 3:  # Coordinate signals
                # Synchronize traffic lights
                for i, tl_id in enumerate(self.traffic_lights):
                    if tl_id in traci.trafficlight.getIDList():
                        offset = i * 2  # Stagger the phases
                        traci.trafficlight.setPhase(tl_id, (traci.trafficlight.getPhase(tl_id) + offset) % 4)
            
            elif action == 4:  # Emergency priority
                # Set all lights to green for main roads
                for tl_id in self.traffic_lights:
                    if tl_id in traci.trafficlight.getIDList():
                        traci.trafficlight.setPhase(tl_id, 0)  # Green phase
            
            elif action == 5:  # Adaptive timing
                # Adjust timing based on queue lengths
                for tl_id in self.traffic_lights:
                    if tl_id in traci.trafficlight.getIDList():
                        queue_length = traffic_state['queue_lengths'].get(tl_id, 0)
                        if queue_length > 10:
                            traci.trafficlight.setPhaseDuration(tl_id, 50)
                        else:
                            traci.trafficlight.setPhaseDuration(tl_id, 30)
            
            elif action == 6:  # Queue management
                # Prioritize lanes with longer queues
                for tl_id in self.traffic_lights:
                    if tl_id in traci.trafficlight.getIDList():
                        queue_length = traffic_state['queue_lengths'].get(tl_id, 0)
                        if queue_length > 15:
                            traci.trafficlight.setPhase(tl_id, 0)  # Green for main flow
            
            elif action == 7:  # Flow optimization
                # Optimize for overall flow
                for tl_id in self.traffic_lights:
                    if tl_id in traci.trafficlight.getIDList():
                        traci.trafficlight.setPhaseDuration(tl_id, 40)  # Balanced timing
            
            self.performance_data['ai_decisions'].append({
                'action': action,
                'timestamp': time.time(),
                'traffic_state': traffic_state
            })
            
        except Exception as e:
            self.logger.error(f"Error applying AI decision: {e}")
    
    def control_traffic(self, current_time: float):
        """Main traffic control function"""
        if current_time - self.last_control_time >= self.control_interval:
            # Get current traffic state
            traffic_state = self.get_traffic_state()
            
            # Get AI decision
            action = self.rl_trainer.predict_action(traffic_state)
            
            # Apply AI decision
            self.apply_ai_decision(action, traffic_state)
            
            # Update performance tracking
            self.update_performance_metrics(traffic_state)
            
            self.last_control_time = current_time
            
            self.logger.info(f"AI Decision at {current_time:.1f}s: Action {action}, "
                           f"Queues: {traffic_state['queue_lengths']}")
    
    def update_performance_metrics(self, traffic_state: Dict):
        """Update performance metrics"""
        self.performance_data['total_vehicles'] = sum(traffic_state['vehicle_counts'].values())
        self.performance_data['queue_lengths'].append(sum(traffic_state['queue_lengths'].values()))
        
        if len(self.performance_data['queue_lengths']) > 100:
            self.performance_data['queue_lengths'] = self.performance_data['queue_lengths'][-100:]
    
    def get_performance_report(self) -> Dict:
        """Get performance report"""
        avg_queue = np.mean(self.performance_data['queue_lengths']) if self.performance_data['queue_lengths'] else 0
        
        return {
            'total_vehicles_processed': self.performance_data['total_vehicles'],
            'average_queue_length': avg_queue,
            'ai_decisions_made': len(self.performance_data['ai_decisions']),
            'efficiency_score': max(0, 100 - avg_queue * 2),
            'timestamp': datetime.now().isoformat()
        }

def main():
    """Main function to run AI-controlled simulation"""
    print("AI Traffic Controller Starting...")
    
    # Connect to SUMO
    try:
        traci.init(port=8813)
        print("Connected to SUMO")
    except Exception as e:
        print(f"Failed to connect to SUMO: {e}")
        return
    
    # Initialize AI controller
    controller = AITrafficController()
    
    # Run simulation
    step = 0
    max_steps = 6000  # 10 minutes at 0.1s steps
    
    print("Starting AI-controlled traffic simulation...")
    
    try:
        while step < max_steps:
            current_time = step * 0.1
            
            # Control traffic with AI
            controller.control_traffic(current_time)
            
            # Step simulation
            traci.simulationStep()
            step += 1
            
            # Print progress every 100 steps
            if step % 100 == 0:
                progress = (step / max_steps) * 100
                print(f"Progress: {progress:.1f}% - Step {step}/{max_steps}")
        
        # Get final performance report
        report = controller.get_performance_report()
        print("\nAI Performance Report:")
        print(json.dumps(report, indent=2))
        
        # Save performance data
        with open('ai_traffic_performance.json', 'w') as f:
            json.dump(report, f, indent=2)
        
        print("\nAI-controlled simulation completed successfully!")
        
    except Exception as e:
        print(f"Simulation error: {e}")
    
    finally:
        traci.close()

if __name__ == "__main__":
    main()
