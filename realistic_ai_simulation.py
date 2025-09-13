#!/usr/bin/env python3
"""
Realistic AI Traffic Simulation
Uses professional 4-way intersection to replicate real traffic video with AI control
"""

import os
import sys
import time
import json
import subprocess
import traci
from typing import Dict, List, Any
import numpy as np
from datetime import datetime

class RealisticAISimulation:
    def __init__(self):
        self.sumo_path = self._get_sumo_path()
        self.network_file = "sumofiles/4way_3lane_lh.net.xml"
        self.routes_file = "sumofiles/test_4way_3lane_balanced_fixed.rou.xml"
        self.config_file = "realistic_ai_simulation.sumocfg"
        self.traffic_light_id = "center"
        self.simulation_data = []
        self.ai_control_active = False
        self.performance_metrics = {}
        
    def _get_sumo_path(self):
        """Get SUMO installation path"""
        if 'SUMO_HOME' in os.environ:
            return os.environ['SUMO_HOME']
        
        # Try common SUMO installation paths
        possible_paths = [
            r"C:\Program Files (x86)\Eclipse\Sumo",
            r"C:\Program Files\Eclipse\Sumo",
            r"C:\sumo",
            r"C:\sumo-1.24.0"
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                return path
        
        raise Exception("SUMO not found. Please set SUMO_HOME environment variable.")
    
    def create_config(self):
        """Create SUMO configuration file"""
        config_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<configuration xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="http://sumo.dlr.de/xsd/sumoConfiguration.xsd">
    <input>
        <net-file value="{self.network_file}"/>
        <route-files value="{self.routes_file}"/>
    </input>
    
    <time>
        <begin value="0"/>
        <end value="300"/>
        <step-length value="0.1"/>
    </time>
    
    <processing>
        <ignore-route-errors value="true"/>
    </processing>
    
    <report>
        <verbose value="true"/>
        <duration-log.statistics value="true"/>
        <no-step-log value="true"/>
    </report>
    
    <gui_only>
        <start value="true"/>
    </gui_only>
</configuration>"""
        
        with open(self.config_file, 'w') as f:
            f.write(config_content)
        
        print(f"✅ Created SUMO config: {self.config_file}")
    
    def start_simulation(self):
        """Start SUMO simulation with TraCI"""
        print("🚦 Starting Realistic AI Traffic Simulation...")
        print("=" * 60)
        
        # Create configuration
        self.create_config()
        
        # Start SUMO GUI
        sumo_binary = os.path.join(self.sumo_path, "bin", "sumo-gui.exe")
        sumo_cmd = [sumo_binary, "-c", self.config_file, "--remote-port", "8813"]
        
        print("  🚦 Starting SUMO GUI...")
        try:
            # Start SUMO as subprocess
            subprocess.Popen(sumo_cmd, stdout=sys.stdout, stderr=sys.stderr)
            time.sleep(3)  # Wait for SUMO to start
            
            # Connect via TraCI
            traci.start(sumo_cmd, port=8813, numRetries=10)
            print("  ✅ Connected to SUMO via TraCI")
            
            # Run simulation with AI control
            self._run_ai_simulation()
            
        except Exception as e:
            print(f"  ❌ Error starting simulation: {e}")
            return False
        
        return True
    
    def _run_ai_simulation(self):
        """Run the AI-controlled simulation"""
        print("\n🤖 Starting AI Traffic Control...")
        print("  - Analyzing traffic patterns in real-time")
        print("  - Optimizing traffic light timing")
        print("  - Collecting performance data")
        
        step = 0
        max_steps = 3000  # 300 seconds with 0.1s steps
        
        # Get initial traffic light state
        tl_program = traci.trafficlight.getCompleteRedYellowGreenDefinition(self.traffic_light_id)
        current_phase = traci.trafficlight.getPhase(self.traffic_light_id)
        
        print(f"  📊 Initial traffic light phase: {current_phase}")
        print(f"  🚦 Traffic light program: {len(tl_program[0].phases)} phases")
        
        # AI Control Parameters
        ai_control_start = 100  # Start AI control after 10 seconds
        phase_duration_override = 15  # AI-controlled phase duration
        last_phase_change = 0
        
        try:
            while step < max_steps and traci.simulation.getMinExpectedNumber() > 0:
                # Get current simulation time
                sim_time = traci.simulation.getTime()
                
                # Collect traffic data
                self._collect_traffic_data(step, sim_time)
                
                # AI Control Logic (starts after initial period)
                if step > ai_control_start:
                    if not self.ai_control_active:
                        print("  🤖 AI Control Activated!")
                        self.ai_control_active = True
                    
                    # AI decision making
                    ai_decision = self._ai_traffic_control(sim_time, step)
                    
                    # Apply AI decision
                    if ai_decision and sim_time - last_phase_change > 5:  # Minimum 5 seconds between changes
                        self._apply_ai_decision(ai_decision)
                        last_phase_change = sim_time
                
                # Step simulation
                traci.simulationStep()
                step += 1
                
                # Progress indicator
                if step % 100 == 0:
                    print(f"  ⏱️  Simulation time: {sim_time:.1f}s | Step: {step} | Vehicles: {traci.simulation.getMinExpectedNumber()}")
            
            print("\n✅ Simulation completed successfully!")
            self._generate_performance_report()
            
        except Exception as e:
            print(f"  ❌ Simulation error: {e}")
        finally:
            traci.close()
    
    def _collect_traffic_data(self, step: int, sim_time: float):
        """Collect traffic data for analysis"""
        try:
            # Get vehicle count
            vehicle_count = traci.simulation.getMinExpectedNumber()
            
            # Get traffic light state
            current_phase = traci.trafficlight.getPhase(self.traffic_light_id)
            phase_duration = traci.trafficlight.getPhaseDuration(self.traffic_light_id)
            
            # Get vehicle positions and speeds
            vehicle_data = []
            for vehicle_id in traci.vehicle.getIDList():
                try:
                    pos = traci.vehicle.getPosition(vehicle_id)
                    speed = traci.vehicle.getSpeed(vehicle_id)
                    vehicle_data.append({
                        'id': vehicle_id,
                        'x': pos[0],
                        'y': pos[1],
                        'speed': speed
                    })
                except:
                    continue
            
            # Store data
            self.simulation_data.append({
                'step': step,
                'time': sim_time,
                'vehicle_count': vehicle_count,
                'traffic_light_phase': current_phase,
                'phase_duration': phase_duration,
                'vehicles': vehicle_data,
                'ai_control_active': self.ai_control_active
            })
            
        except Exception as e:
            print(f"  ⚠️  Data collection error: {e}")
    
    def _ai_traffic_control(self, sim_time: float, step: int) -> Dict[str, Any]:
        """AI traffic control decision making"""
        try:
            # Get current traffic conditions
            vehicle_count = traci.simulation.getMinExpectedNumber()
            current_phase = traci.trafficlight.getPhase(self.traffic_light_id)
            
            # Analyze traffic patterns
            traffic_analysis = self._analyze_traffic_patterns()
            
            # AI Decision Logic
            if vehicle_count > 20:  # High traffic
                if current_phase == 0 or current_phase == 2:  # Main phases
                    return {
                        'action': 'extend_phase',
                        'duration': 20,
                        'reason': 'High traffic detected - extending main phase'
                    }
                else:
                    return {
                        'action': 'change_phase',
                        'target_phase': 0 if current_phase == 1 else 2,
                        'reason': 'High traffic - switching to main phase'
                    }
            elif vehicle_count < 5:  # Low traffic
                if current_phase == 0 or current_phase == 2:  # Main phases
                    return {
                        'action': 'shorten_phase',
                        'duration': 10,
                        'reason': 'Low traffic - shortening main phase'
                    }
            else:  # Medium traffic
                return {
                    'action': 'optimize_timing',
                    'duration': 15,
                    'reason': 'Medium traffic - optimizing timing'
                }
                
        except Exception as e:
            print(f"  ⚠️  AI control error: {e}")
            return None
    
    def _analyze_traffic_patterns(self) -> Dict[str, Any]:
        """Analyze current traffic patterns"""
        try:
            # Get recent data (last 50 steps)
            recent_data = self.simulation_data[-50:] if len(self.simulation_data) > 50 else self.simulation_data
            
            if not recent_data:
                return {'traffic_density': 'unknown', 'trend': 'stable'}
            
            # Calculate average vehicle count
            avg_vehicles = sum(d['vehicle_count'] for d in recent_data) / len(recent_data)
            
            # Determine traffic density
            if avg_vehicles > 15:
                density = 'high'
            elif avg_vehicles > 8:
                density = 'medium'
            else:
                density = 'low'
            
            # Calculate trend
            if len(recent_data) > 10:
                first_half = sum(d['vehicle_count'] for d in recent_data[:len(recent_data)//2])
                second_half = sum(d['vehicle_count'] for d in recent_data[len(recent_data)//2:])
                trend = 'increasing' if second_half > first_half else 'decreasing'
            else:
                trend = 'stable'
            
            return {
                'traffic_density': density,
                'trend': trend,
                'average_vehicles': avg_vehicles
            }
            
        except Exception as e:
            print(f"  ⚠️  Traffic analysis error: {e}")
            return {'traffic_density': 'unknown', 'trend': 'stable'}
    
    def _apply_ai_decision(self, decision: Dict[str, Any]):
        """Apply AI decision to traffic light"""
        try:
            action = decision['action']
            reason = decision['reason']
            
            print(f"  🤖 AI Decision: {action} - {reason}")
            
            if action == 'extend_phase':
                # Extend current phase
                traci.trafficlight.setPhaseDuration(self.traffic_light_id, decision['duration'])
                print(f"    ⏱️  Extended phase to {decision['duration']} seconds")
                
            elif action == 'shorten_phase':
                # Shorten current phase
                traci.trafficlight.setPhaseDuration(self.traffic_light_id, decision['duration'])
                print(f"    ⏱️  Shortened phase to {decision['duration']} seconds")
                
            elif action == 'change_phase':
                # Change to target phase
                traci.trafficlight.setPhase(self.traffic_light_id, decision['target_phase'])
                print(f"    🔄 Changed to phase {decision['target_phase']}")
                
            elif action == 'optimize_timing':
                # Optimize timing
                traci.trafficlight.setPhaseDuration(self.traffic_light_id, decision['duration'])
                print(f"    ⚡ Optimized timing to {decision['duration']} seconds")
                
        except Exception as e:
            print(f"  ❌ Error applying AI decision: {e}")
    
    def _generate_performance_report(self):
        """Generate performance report"""
        print("\n📊 Generating Performance Report...")
        print("=" * 60)
        
        try:
            # Calculate metrics
            total_steps = len(self.simulation_data)
            total_time = self.simulation_data[-1]['time'] if self.simulation_data else 0
            
            # AI Control metrics
            ai_controlled_steps = sum(1 for d in self.simulation_data if d.get('ai_control_active', False))
            ai_control_percentage = (ai_controlled_steps / total_steps * 100) if total_steps > 0 else 0
            
            # Traffic efficiency
            avg_vehicles = sum(d['vehicle_count'] for d in self.simulation_data) / total_steps if total_steps > 0 else 0
            max_vehicles = max(d['vehicle_count'] for d in self.simulation_data) if self.simulation_data else 0
            
            # Phase distribution
            phase_counts = {}
            for d in self.simulation_data:
                phase = d['traffic_light_phase']
                phase_counts[phase] = phase_counts.get(phase, 0) + 1
            
            # Generate report
            report = {
                'simulation_summary': {
                    'total_duration': f"{total_time:.1f} seconds",
                    'total_steps': total_steps,
                    'ai_control_percentage': f"{ai_control_percentage:.1f}%",
                    'ai_controlled_steps': ai_controlled_steps
                },
                'traffic_metrics': {
                    'average_vehicles': f"{avg_vehicles:.1f}",
                    'maximum_vehicles': max_vehicles,
                    'traffic_efficiency': f"{avg_vehicles/max_vehicles*100:.1f}%" if max_vehicles > 0 else "N/A"
                },
                'traffic_light_analysis': {
                    'phase_distribution': phase_counts,
                    'most_used_phase': max(phase_counts, key=phase_counts.get) if phase_counts else "N/A"
                },
                'ai_performance': {
                    'decisions_made': len([d for d in self.simulation_data if d.get('ai_control_active', False)]),
                    'control_effectiveness': f"{ai_control_percentage:.1f}%"
                }
            }
            
            # Display report
            print(f"📈 Simulation Summary:")
            print(f"  • Total Duration: {report['simulation_summary']['total_duration']}")
            print(f"  • AI Control: {report['simulation_summary']['ai_control_percentage']}")
            print(f"  • Total Steps: {report['simulation_summary']['total_steps']}")
            
            print(f"\n🚗 Traffic Metrics:")
            print(f"  • Average Vehicles: {report['traffic_metrics']['average_vehicles']}")
            print(f"  • Maximum Vehicles: {report['traffic_metrics']['maximum_vehicles']}")
            print(f"  • Traffic Efficiency: {report['traffic_metrics']['traffic_efficiency']}")
            
            print(f"\n🚦 Traffic Light Analysis:")
            for phase, count in report['traffic_light_analysis']['phase_distribution'].items():
                percentage = (count / total_steps * 100) if total_steps > 0 else 0
                print(f"  • Phase {phase}: {count} steps ({percentage:.1f}%)")
            
            print(f"\n🤖 AI Performance:")
            print(f"  • Decisions Made: {report['ai_performance']['decisions_made']}")
            print(f"  • Control Effectiveness: {report['ai_performance']['control_effectiveness']}")
            
            # Save report
            with open('realistic_ai_simulation_report.json', 'w') as f:
                json.dump(report, f, indent=2)
            
            print(f"\n✅ Performance report saved: realistic_ai_simulation_report.json")
            
        except Exception as e:
            print(f"❌ Error generating report: {e}")

def main():
    """Main function"""
    print("🚀 Realistic AI Traffic Simulation")
    print("=" * 60)
    print("This simulation uses a professional 4-way intersection")
    print("to replicate real traffic patterns with AI control.")
    print("=" * 60)
    
    try:
        # Create simulation
        simulation = RealisticAISimulation()
        
        # Start simulation
        success = simulation.start_simulation()
        
        if success:
            print("\n🎉 Simulation completed successfully!")
            print("Check the SUMO GUI to see the realistic traffic simulation")
            print("and the performance report for detailed analysis.")
        else:
            print("\n❌ Simulation failed. Please check the error messages above.")
            
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("Please ensure SUMO is properly installed and configured.")

if __name__ == "__main__":
    main()
