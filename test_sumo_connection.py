#!/usr/bin/env python3
"""
Test SUMO Connection
Simple test to verify TraCI connection works
"""

import traci
import time

def test_sumo_connection():
    """Test connection to SUMO"""
    print("🔌 Testing SUMO Connection...")
    
    try:
        # Connect to SUMO
        traci.init(port=8813)
        print("✅ Connected to SUMO successfully!")
        
        # Get simulation info
        sim_time = traci.simulation.getTime()
        print(f"⏰ Simulation time: {sim_time}")
        
        # Get vehicle count
        vehicle_ids = traci.vehicle.getIDList()
        print(f"🚗 Vehicles: {len(vehicle_ids)}")
        
        # Get traffic light info
        try:
            tl_ids = traci.trafficlight.getIDList()
            print(f"🚦 Traffic lights: {tl_ids}")
            
            if 'center' in tl_ids:
                phase = traci.trafficlight.getPhase('center')
                print(f"🚦 Current phase: {phase}")
        except Exception as e:
            print(f"⚠️ Traffic light error: {e}")
        
        # Run a few simulation steps
        print("🏃 Running simulation steps...")
        for i in range(10):
            traci.simulationStep()
            sim_time = traci.simulation.getTime()
            vehicle_count = len(traci.vehicle.getIDList())
            print(f"   Step {i+1}: Time={sim_time:.1f}s, Vehicles={vehicle_count}")
            time.sleep(0.1)
        
        # Close connection
        traci.close()
        print("✅ Connection test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False

if __name__ == "__main__":
    print("🧪 SUMO Connection Test")
    print("=" * 30)
    test_sumo_connection()
