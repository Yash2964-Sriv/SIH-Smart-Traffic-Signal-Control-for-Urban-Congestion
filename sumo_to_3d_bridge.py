#!/usr/bin/env python3
"""
SUMO to 3D Visualization Bridge
Alternative to VIV8 - Custom implementation using available libraries
"""

import traci
import sumolib
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle
import json
import time
from typing import Dict, List, Tuple, Optional
import os

class SUMOTo3DBridge:
    """
    Custom SUMO to 3D visualization bridge
    Replaces VIV8 functionality using matplotlib and other available libraries
    """
    
    def __init__(self, sumo_config: str, gui_settings: Optional[str] = None):
        """
        Initialize the SUMO to 3D bridge
        
        Args:
            sumo_config: Path to SUMO configuration file
            gui_settings: Optional path to GUI settings file
        """
        self.sumo_config = sumo_config
        self.gui_settings = gui_settings
        self.sumo_process = None
        self.net = None
        self.vehicles = {}
        self.traffic_lights = {}
        self.simulation_time = 0
        
    def start_sumo(self):
        """Start SUMO simulation"""
        try:
            # Start SUMO with TraCI
            sumo_cmd = [
                "C:\\Program Files (x86)\\Eclipse\\Sumo\\bin\\sumo.exe",
                "-c", self.sumo_config,
                "--start"
            ]
            
            if self.gui_settings:
                sumo_cmd.extend(["--gui-settings-file", self.gui_settings])
            
            traci.start(sumo_cmd)
            
            # Load network - get the correct path from config
            config_dir = os.path.dirname(self.sumo_config)
            net_file = os.path.join(config_dir, "professional_working_network.net.xml")
            if os.path.exists(net_file):
                self.net = sumolib.net.readNet(net_file)
            else:
                print(f"❌ Network file not found: {net_file}")
                return False
            
            print("✅ SUMO simulation started successfully")
            return True
            
        except Exception as e:
            print(f"❌ Failed to start SUMO: {e}")
            return False
    
    def get_vehicle_data(self) -> Dict:
        """Extract vehicle data from SUMO"""
        vehicles = {}
        
        try:
            # Get all vehicle IDs
            vehicle_ids = traci.vehicle.getIDList()
            
            for veh_id in vehicle_ids:
                # Get vehicle position and properties
                pos = traci.vehicle.getPosition(veh_id)
                angle = traci.vehicle.getAngle(veh_id)
                speed = traci.vehicle.getSpeed(veh_id)
                type_id = traci.vehicle.getTypeID(veh_id)
                
                vehicles[veh_id] = {
                    'position': pos,
                    'angle': angle,
                    'speed': speed,
                    'type': type_id,
                    'x': pos[0],
                    'y': pos[1]
                }
            
            return vehicles
            
        except Exception as e:
            print(f"❌ Error getting vehicle data: {e}")
            return {}
    
    def get_traffic_light_data(self) -> Dict:
        """Extract traffic light data from SUMO"""
        traffic_lights = {}
        
        try:
            # Get all traffic light IDs
            tl_ids = traci.trafficlight.getIDList()
            
            for tl_id in tl_ids:
                # Get traffic light state
                state = traci.trafficlight.getRedYellowGreenState(tl_id)
                program = traci.trafficlight.getCompleteRedYellowGreenDefinition(tl_id)
                
                traffic_lights[tl_id] = {
                    'state': state,
                    'program': program
                }
            
            return traffic_lights
            
        except Exception as e:
            print(f"❌ Error getting traffic light data: {e}")
            return {}
    
    def create_3d_visualization(self, vehicles: Dict, traffic_lights: Dict):
        """Create 3D visualization using matplotlib"""
        fig = plt.figure(figsize=(12, 8))
        ax = fig.add_subplot(111, projection='3d')
        
        # Set up the plot
        ax.set_xlabel('X Position (m)')
        ax.set_ylabel('Y Position (m)')
        ax.set_zlabel('Time (s)')
        ax.set_title(f'SUMO 3D Traffic Visualization - Time: {self.simulation_time:.1f}s')
        
        # Plot vehicles as 3D points
        if vehicles:
            x_coords = [v['x'] for v in vehicles.values()]
            y_coords = [v['y'] for v in vehicles.values()]
            z_coords = [self.simulation_time] * len(vehicles)
            
            # Color vehicles by type
            colors = []
            for v in vehicles.values():
                if 'truck' in v['type'].lower():
                    colors.append('red')
                elif 'bus' in v['type'].lower():
                    colors.append('blue')
                elif 'motorcycle' in v['type'].lower():
                    colors.append('green')
                else:
                    colors.append('orange')
            
            ax.scatter(x_coords, y_coords, z_coords, c=colors, s=50, alpha=0.7)
        
        # Plot traffic lights
        if traffic_lights:
            for tl_id, tl_data in traffic_lights.items():
                # Get traffic light position (simplified)
                tl_pos = (0, 0)  # This would need to be extracted from the network
                ax.scatter(tl_pos[0], tl_pos[1], self.simulation_time, 
                          c='red' if 'r' in tl_data['state'] else 'green', 
                          s=100, marker='s')
        
        plt.tight_layout()
        return fig
    
    def export_to_usd(self, vehicles: Dict, traffic_lights: Dict, output_file: str):
        """Export traffic data to USD format for Omniverse"""
        try:
            from pxr import Usd, UsdGeom, Gf, Sdf
            
            # Create USD stage
            stage = Usd.Stage.CreateNew(output_file)
            
            # Create root prim
            root_prim = stage.DefinePrim("/World", "Xform")
            stage.SetDefaultPrim(root_prim)
            
            # Create vehicles in USD
            for veh_id, veh_data in vehicles.items():
                vehicle_path = f"/World/Vehicles/{veh_id}"
                vehicle_prim = stage.DefinePrim(vehicle_path, "Xform")
                
                # Set position
                position = Gf.Vec3d(veh_data['x'], veh_data['y'], 0.0)
                UsdGeom.XformCommonAPI(vehicle_prim).SetTranslate(position)
                
                # Set rotation
                rotation = Gf.Vec3f(0, 0, veh_data['angle'])
                UsdGeom.XformCommonAPI(vehicle_prim).SetRotate(rotation)
                
                # Create geometry (simplified cube)
                cube_prim = stage.DefinePrim(f"{vehicle_path}/Geometry", "Cube")
                cube = UsdGeom.Cube(cube_prim)
                cube.CreateSizeAttr(4.0)  # Vehicle size
                
                # Set color based on vehicle type
                if 'truck' in veh_data['type'].lower():
                    cube.CreateDisplayColorAttr([(1.0, 0.0, 0.0)])  # Red
                elif 'bus' in veh_data['type'].lower():
                    cube.CreateDisplayColorAttr([(0.0, 0.0, 1.0)])  # Blue
                else:
                    cube.CreateDisplayColorAttr([(1.0, 0.5, 0.0)])  # Orange
            
            # Create traffic lights in USD
            for tl_id, tl_data in traffic_lights.items():
                tl_path = f"/World/TrafficLights/{tl_id}"
                tl_prim = stage.DefinePrim(tl_path, "Xform")
                
                # Set position (simplified)
                position = Gf.Vec3d(0, 0, 0)
                UsdGeom.XformCommonAPI(tl_prim).SetTranslate(position)
                
                # Create traffic light geometry
                tl_geom = stage.DefinePrim(f"{tl_path}/Geometry", "Cylinder")
                cylinder = UsdGeom.Cylinder(tl_geom)
                cylinder.CreateHeightAttr(3.0)
                cylinder.CreateRadiusAttr(0.5)
                
                # Set color based on state
                if 'r' in tl_data['state']:
                    cylinder.CreateDisplayColorAttr([(1.0, 0.0, 0.0)])  # Red
                elif 'y' in tl_data['state']:
                    cylinder.CreateDisplayColorAttr([(1.0, 1.0, 0.0)])  # Yellow
                else:
                    cylinder.CreateDisplayColorAttr([(0.0, 1.0, 0.0)])  # Green
            
            # Save USD file
            stage.Save()
            print(f"✅ USD file exported: {output_file}")
            return True
            
        except Exception as e:
            print(f"❌ Error exporting to USD: {e}")
            return False
    
    def run_simulation(self, duration: int = 100, export_usd: bool = True):
        """Run the complete simulation with 3D visualization"""
        if not self.start_sumo():
            return False
        
        try:
            print(f"🚀 Running simulation for {duration} seconds...")
            
            # Create output directory
            os.makedirs("3d_output", exist_ok=True)
            
            # Run simulation
            for step in range(duration):
                # Advance simulation
                traci.simulationStep()
                self.simulation_time = traci.simulation.getTime()
                
                # Get data
                vehicles = self.get_vehicle_data()
                traffic_lights = self.get_traffic_light_data()
                
                # Create 3D visualization every 10 steps
                if step % 10 == 0:
                    fig = self.create_3d_visualization(vehicles, traffic_lights)
                    fig.savefig(f"3d_output/step_{step:03d}.png", dpi=150, bbox_inches='tight')
                    plt.close(fig)
                
                # Export to USD every 20 steps
                if export_usd and step % 20 == 0:
                    usd_file = f"3d_output/simulation_step_{step:03d}.usda"
                    self.export_to_usd(vehicles, traffic_lights, usd_file)
                
                # Print progress
                if step % 10 == 0:
                    print(f"Step {step}/{duration} - Vehicles: {len(vehicles)}, Time: {self.simulation_time:.1f}s")
            
            print("✅ Simulation completed successfully!")
            return True
            
        except Exception as e:
            print(f"❌ Simulation error: {e}")
            return False
        
        finally:
            # Close TraCI connection
            traci.close()
    
    def create_network_visualization(self):
        """Create a 3D visualization of the network"""
        if not self.net:
            print("❌ Network not loaded")
            return None
        
        fig = plt.figure(figsize=(12, 8))
        ax = fig.add_subplot(111, projection='3d')
        
        # Plot edges
        for edge in self.net.getEdges():
            shape = edge.getShape()
            if len(shape) > 1:
                x_coords = [point[0] for point in shape]
                y_coords = [point[1] for point in shape]
                z_coords = [0] * len(shape)
                
                ax.plot(x_coords, y_coords, z_coords, 'k-', linewidth=2)
        
        # Plot nodes
        for node in self.net.getNodes():
            pos = node.getCoord()
            ax.scatter(pos[0], pos[1], 0, c='red', s=100, marker='o')
        
        ax.set_xlabel('X Position (m)')
        ax.set_ylabel('Y Position (m)')
        ax.set_zlabel('Z Position (m)')
        ax.set_title('SUMO Network 3D Visualization')
        
        plt.tight_layout()
        return fig

def main():
    """Main function to demonstrate the SUMO to 3D bridge"""
    print("🎯 SUMO to 3D Visualization Bridge")
    print("=" * 50)
    
    # Configuration
    sumo_config = "real_traffic_output/professional_working_config.sumocfg"
    gui_settings = "real_traffic_output/professional_visual_settings.xml"
    
    # Check if files exist
    if not os.path.exists(sumo_config):
        print(f"❌ SUMO config not found: {sumo_config}")
        return False
    
    # Create bridge
    bridge = SUMOTo3DBridge(sumo_config, gui_settings)
    
    # Create network visualization
    print("📊 Creating network visualization...")
    network_fig = bridge.create_network_visualization()
    if network_fig:
        network_fig.savefig("3d_output/network_3d.png", dpi=150, bbox_inches='tight')
        plt.close(network_fig)
        print("✅ Network visualization saved")
    
    # Run simulation
    print("🚀 Starting simulation...")
    success = bridge.run_simulation(duration=50, export_usd=True)
    
    if success:
        print("🎉 SUCCESS! Check the '3d_output' directory for results")
        print("📁 Files created:")
        print("   - Network 3D visualization: network_3d.png")
        print("   - Simulation frames: step_*.png")
        print("   - USD files: simulation_step_*.usda")
    else:
        print("❌ Simulation failed")
    
    return success

if __name__ == "__main__":
    main()
