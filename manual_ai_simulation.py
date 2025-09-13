#!/usr/bin/env python3
"""
Manual AI Simulation - Step by step approach
"""

import os
import sys
import time
import json
import traci
import numpy as np
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ManualAIController:
    """Manual AI traffic controller with better error handling"""
    
    def __init__(self):
        self.traffic_lights = ['I1', 'I2']
        self.control_interval = 10  # Control every 10 seconds
        self.last_control_time = 0
        self.performance_data = {
            'total_vehicles': 0,
            'queue_lengths': [],
            'ai_decisions': []
        }
        self.connected = False
    
    def connect_to_sumo(self, max_retries=30, retry_delay=2):
        """Connect to SUMO with retries"""
        logger.info("Attempting to connect to SUMO...")
        
        for attempt in range(max_retries):
            try:
                traci.init(port=8813)
                self.connected = True
                logger.info("Successfully connected to SUMO!")
                return True
            except Exception as e:
                logger.info(f"Connection attempt {attempt + 1}/{max_retries} failed: {e}")
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
        
        logger.error("Failed to connect to SUMO after all retries")
        return False
    
    def get_traffic_state(self):
        """Get current traffic state"""
        if not self.connected:
            return None
        
        state = {
            'queue_lengths': {},
            'vehicle_counts': {'north': 0, 'south': 0, 'east': 0, 'west': 0}
        }
        
        try:
            # Get queue lengths for each traffic light
            for tl_id in self.traffic_lights:
                if tl_id in traci.trafficlight.getIDList():
                    waiting_vehicles = traci.trafficlight.getControlledLanes(tl_id)
                    queue_length = 0
                    for lane in waiting_vehicles:
                        queue_length += traci.lane.getLastStepHaltingNumber(lane)
                    state['queue_lengths'][tl_id] = queue_length
            
            # Get vehicle counts
            vehicle_list = traci.vehicle.getIDList()
            state['vehicle_counts'] = {
                'north': len([v for v in vehicle_list if 'north' in v]),
                'south': len([v for v in vehicle_list if 'south' in v]),
                'east': len([v for v in vehicle_list if 'east' in v]),
                'west': len([v for v in vehicle_list if 'west' in v])
            }
            
        except Exception as e:
            logger.error(f"Error getting traffic state: {e}")
        
        return state
    
    def make_ai_decision(self, traffic_state):
        """Make AI decision based on traffic state"""
        try:
            # Simple AI logic based on queue lengths
            total_queue = sum(traffic_state['queue_lengths'].values())
            
            if total_queue > 20:
                # High traffic - extend green time
                return 1
            elif total_queue > 10:
                # Medium traffic - change phase
                return 0
            else:
                # Low traffic - optimize flow
                return 7
                
        except Exception as e:
            logger.error(f"Error making AI decision: {e}")
            return 0
    
    def apply_decision(self, action, traffic_state):
        """Apply AI decision to traffic lights"""
        if not self.connected:
            return
        
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
                        traci.trafficlight.setPhaseDuration(tl_id, current_duration + 10)
            
            elif action == 7:  # Flow optimization
                for tl_id in self.traffic_lights:
                    if tl_id in traci.trafficlight.getIDList():
                        traci.trafficlight.setPhaseDuration(tl_id, 35)
            
            # Record decision
            self.performance_data['ai_decisions'].append({
                'action': action,
                'timestamp': time.time(),
                'queue_lengths': traffic_state['queue_lengths']
            })
            
        except Exception as e:
            logger.error(f"Error applying decision: {e}")
    
    def control_traffic(self, current_time):
        """Main traffic control function"""
        if not self.connected:
            return
        
        if current_time - self.last_control_time >= self.control_interval:
            # Get traffic state
            traffic_state = self.get_traffic_state()
            if traffic_state is None:
                return
            
            # Make AI decision
            action = self.make_ai_decision(traffic_state)
            
            # Apply decision
            self.apply_decision(action, traffic_state)
            
            # Update performance tracking
            self.performance_data['total_vehicles'] = sum(traffic_state['vehicle_counts'].values())
            self.performance_data['queue_lengths'].append(sum(traffic_state['queue_lengths'].values()))
            
            self.last_control_time = current_time
            
            logger.info(f"AI Decision at {current_time:.1f}s: Action {action}, "
                       f"Queues: {traffic_state['queue_lengths']}")
    
    def get_performance_report(self):
        """Get performance report"""
        avg_queue = np.mean(self.performance_data['queue_lengths']) if self.performance_data['queue_lengths'] else 0
        
        return {
            'total_vehicles_processed': self.performance_data['total_vehicles'],
            'average_queue_length': avg_queue,
            'ai_decisions_made': len(self.performance_data['ai_decisions']),
            'efficiency_score': max(0, 100 - avg_queue * 2),
            'timestamp': datetime.now().isoformat()
        }
    
    def run_simulation(self, max_steps=3000):
        """Run the AI simulation"""
        if not self.connected:
            logger.error("Not connected to SUMO")
            return False
        
        logger.info("Starting AI-controlled traffic simulation...")
        
        try:
            step = 0
            while step < max_steps:
                current_time = step * 0.1
                
                # Control traffic with AI
                self.control_traffic(current_time)
                
                # Step simulation
                traci.simulationStep()
                step += 1
                
                # Print progress every 200 steps
                if step % 200 == 0:
                    progress = (step / max_steps) * 100
                    logger.info(f"Progress: {progress:.1f}% - Step {step}/{max_steps}")
            
            # Get final performance report
            report = self.get_performance_report()
            logger.info("AI Performance Report:")
            logger.info(json.dumps(report, indent=2))
            
            # Save performance data
            with open('manual_ai_performance.json', 'w') as f:
                json.dump(report, f, indent=2)
            
            logger.info("AI-controlled simulation completed successfully!")
            return True
            
        except Exception as e:
            logger.error(f"Simulation error: {e}")
            return False

def main():
    """Main function"""
    print("Manual AI Traffic Controller")
    print("=" * 30)
    print("Make sure SUMO is running with:")
    print("sumo-gui -c video_replication_simulation.sumocfg --remote-port 8813")
    print()
    
    # Create AI controller
    controller = ManualAIController()
    
    # Connect to SUMO
    if not controller.connect_to_sumo():
        print("Failed to connect to SUMO. Please start SUMO first.")
        print("Run: sumo-gui -c video_replication_simulation.sumocfg --remote-port 8813")
        return
    
    # Run simulation
    success = controller.run_simulation()
    
    if success:
        print("\n✅ AI simulation completed successfully!")
        print("Check 'manual_ai_performance.json' for performance metrics.")
    else:
        print("\n❌ Simulation failed. Check the logs for details.")
    
    # Clean up
    try:
        traci.close()
    except:
        pass

if __name__ == "__main__":
    main()
