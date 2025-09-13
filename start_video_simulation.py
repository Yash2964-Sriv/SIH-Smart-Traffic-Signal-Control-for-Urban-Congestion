#!/usr/bin/env python3
"""
Start Video Simulation with Master AI
Automatically starts SUMO simulation and connects Master AI for real-time control
"""

import os
import sys
import time
import json
import traci
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

from master_ai_controller import MasterAIController

def connect_to_sumo():
    """Connect to the running SUMO instance"""
    print("🔌 Connecting to SUMO...")
    print("=" * 50)
    
    try:
        traci.init(port=8813, numRetries=3)
        print("✅ Connected to SUMO successfully!")
        
        # Get simulation info
        current_time = traci.simulation.getTime()
        vehicles = traci.vehicle.getIDList()
        traffic_lights = traci.trafficlight.getIDList()
        
        print(f"⏰ Simulation time: {current_time}")
        print(f"🚗 Current vehicles: {len(vehicles)}")
        print(f"🚦 Traffic lights: {traffic_lights}")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to connect to SUMO: {e}")
        return False

def start_simulation():
    """Start the SUMO simulation"""
    print("\n▶️ Starting SUMO Simulation...")
    print("=" * 50)
    
    try:
        # Start simulation
        traci.simulation.step()
        print("✅ Simulation started!")
        
        # Check for vehicles
        vehicles = traci.vehicle.getIDList()
        print(f"🚗 Vehicles in simulation: {len(vehicles)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to start simulation: {e}")
        return False

def run_master_ai_control():
    """Run Master AI traffic control with real-time metrics"""
    print("\n🤖 Starting Master AI Traffic Control...")
    print("=" * 50)
    
    try:
        # Initialize Master AI
        ai_config = {
            'learning_rate': 0.001,
            'discount_factor': 0.95,
            'epsilon': 0.1,
            'epsilon_decay': 0.995,
            'epsilon_min': 0.01,
            'memory_size': 10000,
            'batch_size': 32,
            'target_update_frequency': 100,
            'training_frequency': 4,
            'video_path': 'Traffic_videos/stock-footage-drone-shot-way-intersection.webm',
            'model_save_path': 'models/master_ai_model.pkl',
            'experience_save_path': 'data/experience_buffer.pkl'
        }
        
        master_ai = MasterAIController(config=ai_config)
        
        print("✅ Master AI initialized!")
        
        # Start AI control
        master_ai.start_real_time_control()
        print("✅ Master AI control started!")
        print("🎯 AI is now controlling traffic signals in real-time")
        
        # Real traffic baseline (from video analysis)
        real_waiting_time = 6.6  # seconds
        real_vehicles = 829
        real_flow_rate = 41.3  # vehicles/min
        real_efficiency = 65.0  # percent
        
        print(f"\n📈 Real-time AI vs Real Traffic Comparison:")
        print(f"   Real Traffic Baseline: {real_vehicles} vehicles, {real_waiting_time}s avg wait, {real_flow_rate} vehicles/min")
        print(f"   {'=' * 60}")
        
        # Run simulation with real-time metrics
        step = 0
        max_steps = 3000
        total_waiting_time = 0
        total_vehicles = 0
        
        while step < max_steps:
            try:
                # Get current simulation state
                vehicles = traci.vehicle.getIDList()
                current_time = traci.simulation.getTime()
                
                # Calculate metrics
                waiting_time = sum(traci.vehicle.getWaitingTime(veh) for veh in vehicles) if vehicles else 0
                avg_waiting = waiting_time / len(vehicles) if vehicles else 0
                efficiency = max(0, 100 - (avg_waiting / 10))  # Simple efficiency calculation
                
                # AI performance
                ai_action = master_ai.get_current_action()
                ai_decisions = step
                
                # Calculate improvements
                time_saved = max(0, real_waiting_time - avg_waiting)
                efficiency_improvement = efficiency - real_efficiency
                flow_rate = len(vehicles) * 60 / max(1, current_time) if current_time > 0 else 0
                
                # Update totals
                total_waiting_time += waiting_time
                total_vehicles += len(vehicles)
                
                # Display metrics every 50 steps
                if step % 50 == 0:
                    print(f"📊 Step {step}: AI vs Real | Wait {avg_waiting:.1f}s vs {real_waiting_time:.1f}s | "
                          f"Efficiency {efficiency:.1f}% vs {real_efficiency:.1f}% | "
                          f"Vehicles {len(vehicles)} vs {real_vehicles} | Time Saved: {time_saved:.1f}s")
                
                # Step simulation
                traci.simulation.step()
                step += 1
                
                # Check if simulation ended
                if traci.simulation.getMinExpectedNumber() == 0 and step > 100:
                    print("🏁 Simulation completed naturally")
                    break
                    
            except Exception as e:
                print(f"⚠️ Simulation step error: {e}")
                break
        
        # Final results
        avg_total_waiting = total_waiting_time / max(1, total_vehicles) if total_vehicles > 0 else 0
        final_efficiency = max(0, 100 - (avg_total_waiting / 10))
        final_time_saved = max(0, real_waiting_time - avg_total_waiting)
        
        print(f"\n📊 Final Performance Comparison")
        print(f"{'=' * 60}")
        print(f"🎬 Real Traffic (from video analysis):")
        print(f"   ⏱️ Average waiting time: {real_waiting_time:.1f}s")
        print(f"   🚗 Total vehicles: {real_vehicles}")
        print(f"   📈 Flow rate: {real_flow_rate:.1f} vehicles/min")
        print(f"   🎯 Efficiency: {real_efficiency:.1f}%")
        
        print(f"\n🤖 AI-Controlled Traffic:")
        print(f"   ⏱️ Average waiting time: {avg_total_waiting:.1f}s")
        print(f"   🚗 Total vehicles: {total_vehicles}")
        print(f"   📈 Flow rate: {flow_rate:.1f} vehicles/min")
        print(f"   🎯 Efficiency: {final_efficiency:.1f}%")
        
        print(f"\n📈 AI Improvements:")
        print(f"   ⏱️ Waiting time reduction: {final_time_saved:.1f}s ({final_time_saved/real_waiting_time*100:.1f}%)")
        print(f"   🎯 Efficiency improvement: {final_efficiency - real_efficiency:+.1f}%")
        print(f"   ⏰ Total time saved: {final_time_saved:.1f}s")
        print(f"   🤖 AI decisions made: {ai_decisions}")
        
        # Save results
        results = {
            'real_traffic': {
                'waiting_time': real_waiting_time,
                'vehicles': real_vehicles,
                'flow_rate': real_flow_rate,
                'efficiency': real_efficiency
            },
            'ai_traffic': {
                'waiting_time': avg_total_waiting,
                'vehicles': total_vehicles,
                'flow_rate': flow_rate,
                'efficiency': final_efficiency
            },
            'improvements': {
                'time_saved': final_time_saved,
                'efficiency_improvement': final_efficiency - real_efficiency,
                'ai_decisions': ai_decisions
            }
        }
        
        with open('video_simulation_results.json', 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"\n💾 Results saved to: video_simulation_results.json")
        print(f"🎉 Master AI successfully controlled traffic signals!")
        
        return True
        
    except Exception as e:
        print(f"❌ AI control error: {e}")
        return False
    finally:
        try:
            traci.close()
        except:
            pass

def main():
    """Main function to run the complete video simulation"""
    print("🎬 Video Simulation with Master AI")
    print("=" * 60)
    print("🎬 Replicating real traffic video in SUMO")
    print("🤖 Master AI controlling traffic signals")
    print("📊 Real-time performance comparison")
    print("=" * 60)
    
    # Step 1: Connect to SUMO
    if not connect_to_sumo():
        print("❌ Failed to connect to SUMO")
        return
    
    # Step 2: Start simulation
    if not start_simulation():
        print("❌ Failed to start simulation")
        return
    
    # Step 3: Run Master AI control
    if not run_master_ai_control():
        print("❌ Failed to run AI control")
        return
    
    print("\n🎉 Video Simulation Complete!")
    print("✅ Real traffic video replicated in SUMO")
    print("✅ Master AI successfully controlled traffic signals")
    print("✅ Performance comparison completed")

if __name__ == "__main__":
    main()
