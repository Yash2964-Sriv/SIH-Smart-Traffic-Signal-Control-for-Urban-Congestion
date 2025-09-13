#!/usr/bin/env python3
"""
Connect Master AI to Running SUMO GUI
Simple connection script for AI traffic control
"""

import time
import traci
import sys
from final_rl_integration_solution import create_final_rl_master_ai

def connect_ai_to_sumo():
    """Connect Master AI to running SUMO instance"""
    print("🤖 Connecting Master AI to SUMO GUI...")
    print("=" * 50)
    
    try:
        # Connect to SUMO
        print("🔌 Connecting to SUMO...")
        traci.init(port=8813)
        print("✅ Connected to SUMO successfully!")
        
        # Initialize Master AI
        print("🧠 Initializing Master AI...")
        master_ai = create_final_rl_master_ai()
        print("✅ Master AI ready!")
        
        # Start AI control
        print("🚦 Starting AI traffic signal control...")
        print("🎮 Watch the SUMO GUI - AI is now controlling traffic signals!")
        print("=" * 50)
        
        step = 0
        while True:
            try:
                # Get traffic data
                traffic_data = get_traffic_data()
                
                # Get AI decision
                ai_action = master_ai.rl_action_selection(traffic_data)
                
                # Execute AI action
                execute_ai_action(ai_action, traffic_data)
                
                # Log progress
                if step % 50 == 0:
                    print(f"📊 Step {step}: AI Action {ai_action}, Vehicles: {len(traffic_data.get('vehicle_ids', []))}")
                
                # Advance simulation
                traci.simulationStep()
                step += 1
                
                # Small delay
                time.sleep(0.1)
                
            except KeyboardInterrupt:
                print("\n🛑 Stopping AI control...")
                break
            except Exception as e:
                print(f"⚠️ Error: {e}")
                time.sleep(1)
        
        # Close connection
        traci.close()
        print("✅ AI control stopped successfully!")
        
    except Exception as e:
        print(f"❌ Failed to connect to SUMO: {e}")
        print("Make sure SUMO GUI is running with the correct configuration")

def get_traffic_data():
    """Get current traffic data from SUMO"""
    try:
        # Get vehicle data
        vehicle_ids = traci.vehicle.getIDList()
        
        # Calculate basic metrics
        queue_length = 0
        waiting_time = 0
        vehicle_count = len(vehicle_ids)
        
        for veh_id in vehicle_ids:
            try:
                speed = traci.vehicle.getSpeed(veh_id)
                if speed < 1.0:  # Consider as queued
                    queue_length += 1
                waiting_time += traci.vehicle.getAccumulatedWaitingTime(veh_id)
            except:
                continue
        
        # Get traffic light state
        current_phase = traci.trafficlight.getPhase('I1')
        phase_duration = traci.trafficlight.getPhaseDuration('I1')
        
        return {
            'vehicle_ids': vehicle_ids,
            'queue_lengths': {'I1': queue_length, 'I2': 0, 'I3': 0, 'I4': 0},
            'waiting_times': {'I1': waiting_time, 'I2': 0, 'I3': 0, 'I4': 0},
            'vehicle_counts': {'north': vehicle_count//4, 'south': vehicle_count//4, 'east': vehicle_count//4, 'west': vehicle_count//4},
            'flow_rates': {'north': vehicle_count//4, 'south': vehicle_count//4, 'east': vehicle_count//4, 'west': vehicle_count//4},
            'current_phase': current_phase,
            'phase_duration': phase_duration,
            'efficiency_scores': {
                'throughput': min(100, (vehicle_count / 10) * 100),
                'waiting_time': max(0, 100 - (waiting_time / 100)),
                'speed': 85
            }
        }
        
    except Exception as e:
        return {
            'vehicle_ids': [],
            'queue_lengths': {'I1': 0, 'I2': 0, 'I3': 0, 'I4': 0},
            'waiting_times': {'I1': 0, 'I2': 0, 'I3': 0, 'I4': 0},
            'vehicle_counts': {'north': 0, 'south': 0, 'east': 0, 'west': 0},
            'flow_rates': {'north': 0, 'south': 0, 'east': 0, 'west': 0},
            'current_phase': 0,
            'phase_duration': 30,
            'efficiency_scores': {'throughput': 0, 'waiting_time': 0, 'speed': 0}
        }

def execute_ai_action(action, traffic_data):
    """Execute AI action on traffic signals"""
    try:
        if action == 0:  # Change phase
            current_phase = traci.trafficlight.getPhase('I1')
            next_phase = (current_phase + 1) % 4
            traci.trafficlight.setPhase('I1', next_phase)
            
        elif action == 1:  # Extend green time
            current_phase = traci.trafficlight.getPhase('I1')
            if current_phase in [0, 2]:  # Green phases
                traci.trafficlight.setPhaseDuration('I1', 35)
                
        elif action == 2:  # Reduce cycle time
            traci.trafficlight.setPhaseDuration('I1', 25)
            
        elif action == 3:  # Coordinate signals
            traci.trafficlight.setPhaseDuration('I1', 30)
            
        elif action == 4:  # Emergency priority
            traci.trafficlight.setPhase('I1', 0)
            traci.trafficlight.setPhaseDuration('I1', 60)
            
        elif action == 5:  # Adaptive timing
            queue_length = sum(traffic_data['queue_lengths'].values())
            if queue_length > 10:
                traci.trafficlight.setPhaseDuration('I1', 40)
            else:
                traci.trafficlight.setPhaseDuration('I1', 25)
                
        elif action == 6:  # Queue management
            max_queue = max(traffic_data['queue_lengths'].values())
            if max_queue > 5:
                traci.trafficlight.setPhase('I1', 0)
                
        elif action == 7:  # Flow optimization
            traci.trafficlight.setPhaseDuration('I1', 30)
            traci.trafficlight.setPhase('I1', 0)
            
    except Exception as e:
        print(f"⚠️ Error executing action {action}: {e}")

if __name__ == "__main__":
    print("🚀 Master AI + SUMO Traffic Control")
    print("=" * 40)
    print("🎬 Based on real traffic video analysis")
    print("🤖 AI-controlled traffic signals")
    print("=" * 40)
    
    connect_ai_to_sumo()
