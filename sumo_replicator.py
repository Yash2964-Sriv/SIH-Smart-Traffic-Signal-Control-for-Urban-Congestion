#!/usr/bin/env python3
"""
SUMO Traffic Replicator
Replicates real traffic video patterns in SUMO simulation
"""

import os
import json
import numpy as np
import traci
import subprocess
from typing import Dict, List, Tuple
from datetime import datetime

class SUMOReplicator:
    def __init__(self, analysis_data: Dict, sumo_config: str = "replicated_traffic.sumocfg"):
        self.analysis_data = analysis_data
        self.sumo_config = sumo_config
        self.sumo_process = None
        self.replication_data = {
            'simulation_start': None,
            'vehicle_data': [],
            'traffic_light_data': [],
            'metrics': {}
        }
        
    def create_network(self) -> bool:
        """Create SUMO network based on video analysis"""
        print("🏗️ Creating SUMO network...")
        
        try:
            # Create a 4-way intersection network
            network_xml = self._generate_network_xml()
            with open("replicated_network.net.xml", 'w') as f:
                f.write(network_xml)
            
            # Create routes based on video analysis
            routes_xml = self._generate_routes_xml()
            with open("replicated_routes.rou.xml", 'w') as f:
                f.write(routes_xml)
            
            # Create traffic lights
            traffic_lights_xml = self._generate_traffic_lights_xml()
            with open("replicated_traffic_lights.xml", 'w') as f:
                f.write(traffic_lights_xml)
            
            print("✅ Network files created successfully")
            return True
            
        except Exception as e:
            print(f"❌ Error creating network: {e}")
            return False
    
    def _generate_network_xml(self) -> str:
        """Generate SUMO network XML"""
        return """<?xml version="1.0" encoding="UTF-8"?>
<net version="1.9" junctionCornerDetail="5" limitTurnSpeed="5.5" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="http://sumo.dlr.de/xsd/net_file.xsd">
    <location netOffset="0.00,0.00" convBoundary="0.00,0.00,200.00,200.00" origBoundary="-10000000000.00,-10000000000.00,10000000000.00,10000000000.00" projParameter="!"/>
    
    <!-- Nodes (Intersections) -->
    <junction id="I1" type="traffic_light" x="100.00" y="100.00" incLanes="E1_0 W1_0 N1_0 S1_0" intLanes=":I1_0 :I1_1 :I1_2 :I1_3" shape="100.00,90.00 110.00,100.00 100.00,110.00 90.00,100.00">
        <request index="0" response="00" foes="00" cont="0"/>
        <request index="1" response="00" foes="00" cont="0"/>
        <request index="2" response="00" foes="00" cont="0"/>
        <request index="3" response="00" foes="00" cont="0"/>
    </junction>
    
    <!-- Edges -->
    <edge id="E1" from="I1" to="I1" priority="1">
        <lane id="E1_0" index="0" speed="13.89" length="100.00" shape="200.00,100.00 100.00,100.00"/>
    </edge>
    <edge id="W1" from="I1" to="I1" priority="1">
        <lane id="W1_0" index="0" speed="13.89" length="100.00" shape="0.00,100.00 100.00,100.00"/>
    </edge>
    <edge id="N1" from="I1" to="I1" priority="1">
        <lane id="N1_0" index="0" speed="13.89" length="100.00" shape="100.00,0.00 100.00,100.00"/>
    </edge>
    <edge id="S1" from="I1" to="I1" priority="1">
        <lane id="S1_0" index="0" speed="13.89" length="100.00" shape="100.00,200.00 100.00,100.00"/>
    </edge>
    
    <!-- Internal lanes -->
    <edge id=":I1_0" from="I1" to="I1" priority="1">
        <lane id=":I1_0" index="0" speed="13.89" length="10.00" shape="100.00,100.00 110.00,100.00"/>
    </edge>
    <edge id=":I1_1" from="I1" to="I1" priority="1">
        <lane id=":I1_1" index="0" speed="13.89" length="10.00" shape="100.00,100.00 100.00,110.00"/>
    </edge>
    <edge id=":I1_2" from="I1" to="I1" priority="1">
        <lane id=":I1_2" index="0" speed="13.89" length="10.00" shape="100.00,100.00 90.00,100.00"/>
    </edge>
    <edge id=":I1_3" from="I1" to="I1" priority="1">
        <lane id=":I1_3" index="0" speed="13.89" length="10.00" shape="100.00,100.00 100.00,90.00"/>
    </edge>
    
    <!-- Connections -->
    <connection from="E1" to=":I1_0" fromLane="0" toLane="0" via=":I1_0" dir="s" state="M"/>
    <connection from=":I1_0" to="W1" fromLane="0" toLane="0" via=":I1_0" dir="s" state="M"/>
    <connection from="N1" to=":I1_1" fromLane="0" toLane="0" via=":I1_1" dir="s" state="M"/>
    <connection from=":I1_1" to="S1" fromLane="0" toLane="0" via=":I1_1" dir="s" state="M"/>
    <connection from="W1" to=":I1_2" fromLane="0" toLane="0" via=":I1_2" dir="s" state="M"/>
    <connection from=":I1_2" to="E1" fromLane="0" toLane="0" via=":I1_2" dir="s" state="M"/>
    <connection from="S1" to=":I1_3" fromLane="0" toLane="0" via=":I1_3" dir="s" state="M"/>
    <connection from=":I1_3" to="N1" fromLane="0" toLane="0" via=":I1_3" dir="s" state="M"/>
</net>"""
    
    def _generate_routes_xml(self) -> str:
        """Generate routes based on video analysis"""
        vehicle_data = self.analysis_data.get('vehicle_data', {})
        video_info = self.analysis_data.get('video_info', {})
        
        routes = []
        vehicle_id = 0
        
        # Generate vehicles based on video analysis
        for real_vehicle_id, positions in vehicle_data.items():
            if len(positions) > 1:
                # Determine route based on movement pattern
                start_pos = positions[0]['position']
                end_pos = positions[-1]['position']
                
                # Simple route determination
                if start_pos[0] < 50:  # From west
                    if end_pos[0] > 150:  # To east
                        route = "W1 E1"
                    elif end_pos[1] < 50:  # To north
                        route = "W1 N1"
                    else:  # To south
                        route = "W1 S1"
                elif start_pos[0] > 150:  # From east
                    if end_pos[0] < 50:  # To west
                        route = "E1 W1"
                    elif end_pos[1] < 50:  # To north
                        route = "E1 N1"
                    else:  # To south
                        route = "E1 S1"
                elif start_pos[1] < 50:  # From north
                    if end_pos[1] > 150:  # To south
                        route = "N1 S1"
                    elif end_pos[0] < 50:  # To west
                        route = "N1 W1"
                    else:  # To east
                        route = "N1 E1"
                else:  # From south
                    if end_pos[1] < 50:  # To north
                        route = "S1 N1"
                    elif end_pos[0] < 50:  # To west
                        route = "S1 W1"
                    else:  # To east
                        route = "S1 E1"
                
                # Calculate departure time
                departure_time = positions[0]['time']
                
                routes.append(f'    <vehicle id="veh{vehicle_id}" type="car" route="{route}" depart="{departure_time:.2f}"/>')
                vehicle_id += 1
        
        routes_xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<routes xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="http://sumo.dlr.de/xsd/routes_file.xsd">
    <vType id="car" accel="2.6" decel="4.5" sigma="0.5" length="5" maxSpeed="50"/>
{chr(10).join(routes)}
</routes>"""
        
        return routes_xml
    
    def _generate_traffic_lights_xml(self) -> str:
        """Generate traffic lights based on video analysis"""
        intersection_data = self.analysis_data.get('intersection_data', {})
        light_patterns = intersection_data.get('traffic_light_patterns', {})
        
        cycle_time = light_patterns.get('cycle_time', 60)
        green_time = light_patterns.get('green_time', 30)
        yellow_time = light_patterns.get('yellow_time', 3)
        red_time = light_patterns.get('red_time', 27)
        
        return f"""<?xml version="1.0" encoding="UTF-8"?>
<additional xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="http://sumo.dlr.de/xsd/additional_file.xsd">
    <tlLogic id="I1" type="static" programID="0" offset="0">
        <phase duration="{green_time}" state="GGrrGGrr"/>
        <phase duration="{yellow_time}" state="yyrryyrr"/>
        <phase duration="{green_time}" state="rrGGrrGG"/>
        <phase duration="{yellow_time}" state="rryyrryy"/>
    </tlLogic>
</additional>"""
    
    def run_simulation(self) -> bool:
        """Run SUMO simulation"""
        print("🚦 Starting SUMO simulation...")
        
        try:
            # Start SUMO
            sumo_cmd = ["sumo-gui", "-c", self.sumo_config, "--start"]
            traci.start(sumo_cmd)
            
            self.replication_data['simulation_start'] = datetime.now()
            
            # Run simulation
            step = 0
            while traci.simulation.getMinExpectedNumber() > 0:
                traci.simulationStep()
                
                # Collect data
                self._collect_simulation_data(step)
                
                step += 1
                if step % 100 == 0:
                    print(f"   Simulation step: {step}")
            
            traci.close()
            print("✅ Simulation completed successfully")
            return True
            
        except Exception as e:
            print(f"❌ Error running simulation: {e}")
            return False
    
    def _collect_simulation_data(self, step: int):
        """Collect data during simulation"""
        current_time = traci.simulation.getTime()
        
        # Collect vehicle data
        vehicle_ids = traci.vehicle.getIDList()
        for veh_id in vehicle_ids:
            pos = traci.vehicle.getPosition(veh_id)
            speed = traci.vehicle.getSpeed(veh_id)
            waiting_time = traci.vehicle.getAccumulatedWaitingTime(veh_id)
            
            self.replication_data['vehicle_data'].append({
                'step': step,
                'time': current_time,
                'vehicle_id': veh_id,
                'position': pos,
                'speed': speed,
                'waiting_time': waiting_time
            })
        
        # Collect traffic light data
        tl_state = traci.trafficlight.getRedYellowGreenState("I1")
        self.replication_data['traffic_light_data'].append({
            'step': step,
            'time': current_time,
            'state': tl_state
        })
    
    def calculate_metrics(self) -> Dict:
        """Calculate simulation metrics"""
        print("📊 Calculating simulation metrics...")
        
        vehicle_data = self.replication_data['vehicle_data']
        
        if not vehicle_data:
            return {}
        
        # Calculate basic metrics
        total_vehicles = len(set([v['vehicle_id'] for v in vehicle_data]))
        total_waiting_time = sum([v['waiting_time'] for v in vehicle_data])
        avg_speed = np.mean([v['speed'] for v in vehicle_data])
        
        # Calculate efficiency metrics
        throughput = total_vehicles / (self.replication_data['simulation_start'] - datetime.now()).total_seconds() if self.replication_data['simulation_start'] else 0
        
        self.replication_data['metrics'] = {
            'total_vehicles': total_vehicles,
            'total_waiting_time': total_waiting_time,
            'avg_waiting_time': total_waiting_time / total_vehicles if total_vehicles > 0 else 0,
            'avg_speed': avg_speed,
            'throughput': throughput,
            'efficiency_score': self._calculate_efficiency_score()
        }
        
        return self.replication_data['metrics']
    
    def _calculate_efficiency_score(self) -> float:
        """Calculate overall efficiency score"""
        # Simplified efficiency calculation
        metrics = self.replication_data['metrics']
        
        # Weighted score based on waiting time, speed, and throughput
        waiting_score = max(0, 100 - metrics['avg_waiting_time'] * 2)
        speed_score = min(100, metrics['avg_speed'] * 2)
        throughput_score = min(100, metrics['throughput'] * 10)
        
        return (waiting_score + speed_score + throughput_score) / 3
    
    def save_replication_data(self, output_path: str = "sumo_replication_data.json"):
        """Save replication data"""
        with open(output_path, 'w') as f:
            json.dump(self.replication_data, f, indent=2, default=str)
        print(f"💾 Replication data saved to {output_path}")

def main():
    """Main function to replicate traffic in SUMO"""
    # Load analysis data
    if not os.path.exists("real_traffic_analysis.json"):
        print("❌ Analysis data not found. Please run traffic_video_analyzer.py first.")
        return
    
    with open("real_traffic_analysis.json", 'r') as f:
        analysis_data = json.load(f)
    
    replicator = SUMOReplicator(analysis_data)
    
    # Create network
    if not replicator.create_network():
        print("❌ Failed to create network")
        return
    
    # Run simulation
    if replicator.run_simulation():
        metrics = replicator.calculate_metrics()
        replicator.save_replication_data()
        print("🎉 SUMO replication completed successfully!")
        print(f"📈 Efficiency Score: {metrics.get('efficiency_score', 0):.2f}")
    else:
        print("❌ Simulation failed")

if __name__ == "__main__":
    main()