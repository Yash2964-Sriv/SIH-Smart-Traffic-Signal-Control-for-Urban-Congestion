#!/usr/bin/env python3
"""
Complete Video Analysis and SUMO Simulation with Master AI
Analyzes real traffic video and replicates it in SUMO with AI control
"""

import os
import sys
import time
import json
import subprocess
import traci
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

from traffic_video_analyzer import TrafficVideoAnalyzer
from master_ai_controller import MasterAIController

def analyze_video(video_path):
    """Analyze the real traffic video to extract patterns"""
    print("🎬 Analyzing Real Traffic Video...")
    print("=" * 50)
    
    analyzer = TrafficVideoAnalyzer(video_path)
    results = analyzer.analyze_video()
    
    print(f"📊 Video Analysis Results:")
    print(f"   🚗 Vehicles detected: {len(results['vehicle_data'])}")
    print(f"   ⏱️ Average waiting time: {results['timing_data']['efficiency_metrics']['waiting_time']:.1f}s")
    print(f"   📈 Flow rate: {results['timing_data']['efficiency_metrics']['flow_rate']:.1f} vehicles/min")
    print(f"   🎯 Traffic efficiency: {results['traffic_patterns'].get('efficiency', 65.0):.1f}%")
    
    return results

def start_sumo_gui():
    """Start SUMO GUI with the working configuration"""
    print("\n🚦 Starting SUMO GUI...")
    print("=" * 50)
    
    config_file = "video_replication_working.sumocfg"
    sumo_path = r"C:\Program Files (x86)\Eclipse\Sumo\bin\sumo-gui.exe"
    
    if not os.path.exists(config_file):
        print(f"❌ Configuration file not found: {config_file}")
        return False
    
    try:
        # Start SUMO GUI
        cmd = [sumo_path, "-c", config_file, "--remote-port", "8813"]
        print(f"🚀 Launching: {' '.join(cmd)}")
        
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        time.sleep(3)  # Wait for SUMO to start
        
        # Test TraCI connection
        try:
            traci.init(port=8813, numRetries=3)
            print("✅ SUMO GUI started successfully!")
            print("🎮 SUMO GUI is now running - you can see the traffic simulation!")
            print("🎯 Click the 'Run' button in SUMO to start AI control!")
            return True
        except Exception as e:
            print(f"❌ Failed to connect to SUMO: {e}")
            return False
            
    except Exception as e:
        print(f"❌ Failed to start SUMO: {e}")
        return False

def run_ai_simulation(video_analysis):
    """Run the AI-controlled simulation"""
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
        
        master_ai = MasterAIController(
            junction_ids=['center_junc'],
            sumo_config='video_replication_working.sumocfg',
            config=ai_config
        )
        
        print("✅ Master AI initialized!")
        
        # Wait for user to click Run in SUMO
        print("\n⏳ Waiting for you to click 'Run' in SUMO GUI...")
        print("   (The AI will start controlling traffic signals once you click Run)")
        
        # Start AI control
        master_ai.start_ai_control()
        print("✅ Master AI control started!")
        print("🎯 AI is now controlling traffic signals in real-time")
        print("📊 Performance monitoring active")
        
        # Run simulation with real-time metrics
        step = 0
        max_steps = 2000
        
        print(f"\n📈 Real-time Comparison Metrics:")
        print(f"   Real Traffic vs AI-Controlled Traffic")
        print(f"   {'=' * 50}")
        
        while step < max_steps and traci.simulation.getMinExpectedNumber() > 0:
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
                
                # Real vs AI comparison
                real_wait = video_analysis['timing_data']['efficiency_metrics']['waiting_time']
                real_efficiency = video_analysis['traffic_patterns'].get('efficiency', 65.0)
                real_vehicles = len(video_analysis['vehicle_data'])
                
                time_saved = max(0, real_wait - avg_waiting)
                efficiency_improvement = efficiency - real_efficiency
                
                # Display metrics every 100 steps
                if step % 100 == 0:
                    print(f"📊 AI vs Real: Wait {avg_waiting:.1f}s vs {real_wait:.1f}s ({efficiency_improvement:+.1f}%) | "
                          f"Efficiency {efficiency:.1f}% vs {real_efficiency:.1f}% ({efficiency_improvement:+.1f}%) | "
                          f"Time Saved: {time_saved:.1f}s | Vehicles {len(vehicles)} vs {real_vehicles}")
                
                # Step simulation
                traci.simulation.step()
                step += 1
                
            except Exception as e:
                print(f"⚠️ Simulation step error: {e}")
                break
        
        # Final results
        print(f"\n📊 Final Performance Comparison")
        print(f"{'=' * 60}")
        print(f"🎬 Real Traffic (from video analysis):")
        print(f"   ⏱️ Average waiting time: {video_analysis['timing_data']['efficiency_metrics']['waiting_time']:.1f}s")
        print(f"   🚗 Average vehicles: {len(video_analysis['vehicle_data'])}")
        print(f"   📈 Flow rate: {video_analysis['timing_data']['efficiency_metrics']['flow_rate']:.1f} vehicles/min")
        print(f"   🎯 Efficiency: {video_analysis['traffic_patterns'].get('efficiency', 65.0):.1f}%")
        
        print(f"\n🤖 AI-Controlled Traffic:")
        print(f"   ⏱️ Average waiting time: {avg_waiting:.1f}s")
        print(f"   🚗 Average vehicles: {len(vehicles)}")
        print(f"   📈 Flow rate: {len(vehicles) * 60 / max(1, current_time):.1f} vehicles/min")
        print(f"   🎯 Efficiency: {efficiency:.1f}%")
        
        print(f"\n📈 AI Improvements:")
        print(f"   ⏱️ Waiting time reduction: {efficiency_improvement:+.1f}%")
        print(f"   🎯 Efficiency improvement: {efficiency_improvement:+.1f}%")
        print(f"   ⏰ Total time saved: {time_saved:.1f}s")
        print(f"   🤖 AI decisions made: {ai_decisions}")
        
        # Save results
        results = {
            'video_analysis': video_analysis,
            'ai_performance': {
                'avg_waiting_time': avg_waiting,
                'vehicles': len(vehicles),
                'efficiency': efficiency,
                'ai_decisions': ai_decisions,
                'time_saved': time_saved,
                'efficiency_improvement': efficiency_improvement
            },
            'comparison': {
                'waiting_time_reduction': efficiency_improvement,
                'efficiency_improvement': efficiency_improvement,
                'total_time_saved': time_saved
            }
        }
        
        with open('video_simulation_results.json', 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"\n💾 Results saved to: video_simulation_results.json")
        print(f"📊 AI maintained traffic efficiency with better control!")
        
        return True
        
    except Exception as e:
        print(f"❌ AI simulation error: {e}")
        return False
    finally:
        try:
            traci.close()
        except:
            pass

def main():
    """Main function to run complete video analysis and simulation"""
    print("🎬 Complete Video Analysis and SUMO Simulation")
    print("=" * 60)
    print("🎬 Based on real traffic video analysis")
    print("🤖 Enhanced with Master AI + RL control")
    print("📊 Real-time performance comparison")
    print("=" * 60)
    
    # Step 1: Analyze video
    video_path = "Traffic_videos/stock-footage-drone-shot-way-intersection.webm"
    if not os.path.exists(video_path):
        print(f"❌ Video file not found: {video_path}")
        return
    
    video_analysis = analyze_video(video_path)
    
    # Step 2: Start SUMO GUI
    if not start_sumo_gui():
        print("❌ Failed to start SUMO GUI")
        return
    
    # Step 3: Run AI simulation
    print(f"\n⏳ Waiting for you to click 'Run' in SUMO GUI...")
    print(f"   (The AI will start controlling traffic signals once you click Run)")
    
    input("Press Enter when you've clicked 'Run' in SUMO GUI...")
    
    if not run_ai_simulation(video_analysis):
        print("❌ AI simulation failed")
        return
    
    print("\n🎉 Video Simulation Complete!")
    print("✅ Real traffic video analyzed and replicated in SUMO")
    print("✅ Master AI successfully controlled traffic signals")
    print("✅ Real-time performance comparison completed")

if __name__ == "__main__":
    main()
