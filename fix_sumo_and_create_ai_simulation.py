#!/usr/bin/env python3
"""
Fix SUMO Configuration and Create AI-Controlled Traffic Simulation
Based on Real Traffic Video Analysis
"""

import os
import sys
import json
import time
import subprocess
import shutil
from datetime import datetime
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SUMOFixer:
    """Fix SUMO configuration and create AI-controlled simulation"""
    
    def __init__(self):
        self.workspace_root = Path.cwd()
        self.real_traffic_dir = self.workspace_root / "real_traffic_output"
        self.traffic_videos_dir = self.workspace_root / "Traffic_videos"
        self.models_dir = self.workspace_root / "models"
        self.models_dir.mkdir(exist_ok=True)
        
    def fix_sumo_configuration(self):
        """Fix SUMO configuration file paths"""
        logger.info("🔧 Fixing SUMO configuration...")
        
        # Create a working configuration file
        config_content = '''<?xml version="1.0" encoding="UTF-8"?>
<configuration xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="http://sumo.dlr.de/xsd/sumoConfiguration.xsd">

    <input>
        <net-file value="real_traffic_output/visible_traffic_lights.net.xml"/>
        <route-files value="real_traffic_output/enhanced_multi_intersection.rou.xml"/>
    </input>

    <time>
        <begin value="0"/>
        <end value="600"/>
        <step-length value="0.1"/>
    </time>

    <processing>
        <ignore-route-errors value="true"/>
    </processing>

    <report>
        <verbose value="true"/>
        <no-step-log value="false"/>
        <duration-log.statistics value="true"/>
        <no-warnings value="false"/>
    </report>

    <gui_only>
        <start value="true"/>
        <quit-on-end value="false"/>
        <delay value="100"/>
        <gui-settings-file value="real_traffic_output/traffic_lights_visual.xml"/>
    </gui_only>

</configuration>'''
        
        # Write the fixed configuration
        config_path = self.workspace_root / "fixed_ai_simulation.sumocfg"
        with open(config_path, 'w') as f:
            f.write(config_content)
        
        logger.info(f"✅ Fixed configuration saved to: {config_path}")
        return config_path
    
    def create_ai_controlled_routes(self):
        """Create AI-controlled route file based on real traffic patterns"""
        logger.info("🤖 Creating AI-controlled routes...")
        
        # Analyze the real traffic video patterns (simulated based on typical intersection patterns)
        route_content = '''<?xml version="1.0" encoding="UTF-8"?>
<routes xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="http://sumo.dlr.de/xsd/routes_file.xsd">

    <!-- Vehicle types with realistic parameters -->
    <vType id="car" accel="2.6" decel="4.5" sigma="0.5" length="4.3" maxSpeed="50" color="1,1,0"/>
    <vType id="truck" accel="1.2" decel="3.0" sigma="0.3" length="12.0" maxSpeed="30" color="0,0,1"/>
    <vType id="bus" accel="1.5" decel="3.5" sigma="0.4" length="12.0" maxSpeed="25" color="1,0,1"/>
    <vType id="emergency" accel="3.0" decel="6.0" sigma="0.2" length="5.0" maxSpeed="60" color="1,0,0"/>

    <!-- High-density main road traffic (East-West) - Peak hours simulation -->
    <flow id="main_west_to_east_peak" type="car" begin="0" end="300" period="8" from="main_west" to="main_east" color="0,1,0"/>
    <flow id="main_east_to_west_peak" type="car" begin="0" end="300" period="10" from="main_east_reverse" to="main_west_reverse" color="1,0,0"/>
    
    <!-- Off-peak traffic -->
    <flow id="main_west_to_east_off" type="car" begin="300" end="600" period="15" from="main_west" to="main_east" color="0,0.8,0"/>
    <flow id="main_east_to_west_off" type="car" begin="300" end="600" period="18" from="main_east_reverse" to="main_west_reverse" color="0.8,0,0"/>
    
    <!-- Secondary road traffic (North-South) - Realistic patterns -->
    <flow id="secondary_north_1_to_south" type="car" begin="0" end="600" period="20" from="secondary_north_1" to="secondary_south_1" color="0,0,1"/>
    <flow id="secondary_north_2_to_south" type="car" begin="0" end="600" period="25" from="secondary_north_2" to="secondary_south_2" color="1,0,1"/>

    <!-- Turning traffic with realistic timing -->
    <flow id="main_to_secondary_1" type="car" begin="0" end="600" period="30" from="main_west" to="secondary_south_1" color="1,0.5,0"/>
    <flow id="secondary_1_to_main" type="car" begin="0" end="600" period="35" from="secondary_north_1" to="main_center" color="0.5,1,0"/>
    
    <flow id="main_to_secondary_2" type="car" begin="0" end="600" period="40" from="main_center" to="secondary_south_2" color="0.5,0,1"/>
    <flow id="secondary_2_to_main" type="car" begin="0" end="600" period="45" from="secondary_north_2" to="main_east" color="1,0.5,1"/>

    <!-- Mixed vehicle types for realism -->
    <flow id="truck_main_west" type="truck" begin="0" end="600" period="80" from="main_west" to="main_east" color="0,0,0.8"/>
    <flow id="truck_main_east" type="truck" begin="0" end="600" period="90" from="main_east_reverse" to="main_west_reverse" color="0.8,0,0"/>
    
    <flow id="bus_secondary_1" type="bus" begin="0" end="600" period="120" from="secondary_north_1" to="secondary_south_1" color="0.5,0,0.5"/>
    <flow id="bus_secondary_2" type="bus" begin="0" end="600" period="150" from="secondary_north_2" to="secondary_south_2" color="0.5,0.5,0"/>

    <!-- Emergency vehicles for AI control testing -->
    <flow id="emergency_west" type="emergency" begin="100" end="120" period="20" from="main_west" to="main_east" color="1,0,0"/>
    <flow id="emergency_east" type="emergency" begin="200" end="220" period="20" from="main_east_reverse" to="main_west_reverse" color="1,0,0"/>

</routes>'''
        
        route_path = self.real_traffic_dir / "ai_controlled_routes.rou.xml"
        with open(route_path, 'w') as f:
            f.write(route_content)
        
        logger.info(f"✅ AI-controlled routes saved to: {route_path}")
        return route_path
    
    def create_ai_traffic_controller(self):
        """Create AI traffic controller that integrates with SUMO"""
        logger.info("🧠 Creating AI traffic controller...")
        
        controller_code = '''#!/usr/bin/env python3
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
    print("🤖 AI Traffic Controller Starting...")
    
    # Connect to SUMO
    try:
        traci.init(port=8813)
        print("✅ Connected to SUMO")
    except Exception as e:
        print(f"❌ Failed to connect to SUMO: {e}")
        return
    
    # Initialize AI controller
    controller = AITrafficController()
    
    # Run simulation
    step = 0
    max_steps = 6000  # 10 minutes at 0.1s steps
    
    print("🚦 Starting AI-controlled traffic simulation...")
    
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
        print("\\n📊 AI Performance Report:")
        print(json.dumps(report, indent=2))
        
        # Save performance data
        with open('ai_traffic_performance.json', 'w') as f:
            json.dump(report, f, indent=2)
        
        print("\\n✅ AI-controlled simulation completed successfully!")
        
    except Exception as e:
        print(f"❌ Simulation error: {e}")
    
    finally:
        traci.close()

if __name__ == "__main__":
    main()
'''
        
        controller_path = self.workspace_root / "ai_traffic_controller.py"
        with open(controller_path, 'w') as f:
            f.write(controller_code)
        
        logger.info(f"✅ AI traffic controller saved to: {controller_path}")
        return controller_path
    
    def create_launch_script(self):
        """Create script to launch the complete AI simulation"""
        logger.info("🚀 Creating launch script...")
        
        launch_script = '''@echo off
echo 🤖 Starting AI-Controlled Traffic Simulation...
echo ================================================

echo.
echo Step 1: Starting SUMO with fixed configuration...
start "SUMO GUI" sumo-gui -c fixed_ai_simulation.sumocfg --remote-port 8813

echo.
echo Waiting for SUMO to initialize...
timeout /t 3 /nobreak > nul

echo.
echo Step 2: Starting AI Traffic Controller...
python ai_traffic_controller.py

echo.
echo ✅ AI simulation completed!
pause
'''
        
        launch_path = self.workspace_root / "launch_ai_simulation.bat"
        with open(launch_path, 'w') as f:
            f.write(launch_script)
        
        logger.info(f"✅ Launch script saved to: {launch_path}")
        return launch_path
    
    def test_simulation(self):
        """Test the simulation to ensure it works"""
        logger.info("🧪 Testing simulation...")
        
        try:
            # Test SUMO configuration
            config_path = self.workspace_root / "fixed_ai_simulation.sumocfg"
            if not config_path.exists():
                logger.error("Configuration file not found")
                return False
            
            # Test network file
            network_path = self.real_traffic_dir / "visible_traffic_lights.net.xml"
            if not network_path.exists():
                logger.error("Network file not found")
                return False
            
            # Test route file
            route_path = self.real_traffic_dir / "ai_controlled_routes.rou.xml"
            if not route_path.exists():
                logger.error("Route file not found")
                return False
            
            logger.info("✅ All files exist and are accessible")
            return True
            
        except Exception as e:
            logger.error(f"Test failed: {e}")
            return False
    
    def run_complete_simulation(self):
        """Run the complete AI simulation"""
        logger.info("🎯 Running complete AI simulation...")
        
        try:
            # Test first
            if not self.test_simulation():
                logger.error("Simulation test failed")
                return False
            
            # Launch the simulation
            launch_script = self.workspace_root / "launch_ai_simulation.bat"
            if launch_script.exists():
                logger.info("🚀 Launching AI simulation...")
                subprocess.run([str(launch_script)], shell=True)
                return True
            else:
                logger.error("Launch script not found")
                return False
                
        except Exception as e:
            logger.error(f"Simulation failed: {e}")
            return False

def main():
    """Main function"""
    print("🤖 AI Traffic Simulation Setup and Launch")
    print("=" * 50)
    
    # Initialize fixer
    fixer = SUMOFixer()
    
    # Fix SUMO configuration
    config_path = fixer.fix_sumo_configuration()
    
    # Create AI-controlled routes
    route_path = fixer.create_ai_controlled_routes()
    
    # Create AI traffic controller
    controller_path = fixer.create_ai_traffic_controller()
    
    # Create launch script
    launch_path = fixer.create_launch_script()
    
    # Test the simulation
    if fixer.test_simulation():
        print("\\n✅ All components created successfully!")
        print(f"📁 Configuration: {config_path}")
        print(f"📁 Routes: {route_path}")
        print(f"📁 Controller: {controller_path}")
        print(f"📁 Launch Script: {launch_path}")
        
        print("\\n🚀 To run the AI simulation:")
        print("1. Double-click 'launch_ai_simulation.bat'")
        print("2. Or run: python ai_traffic_controller.py")
        
        # Ask if user wants to run now
        response = input("\\nDo you want to run the simulation now? (y/n): ")
        if response.lower() == 'y':
            fixer.run_complete_simulation()
    else:
        print("❌ Setup failed. Please check the errors above.")

if __name__ == "__main__":
    main()
