#!/usr/bin/env python3
"""
Test TraCI Connection with Better Error Handling
"""

import traci
import time

def test_traci_connection():
    """Test TraCI connection with better error handling"""
    print("🔌 Testing TraCI Connection...")
    print("=" * 40)
    
    try:
        # Try to connect to TraCI
        print("🔗 Attempting to connect to TraCI server on port 8813...")
        traci.init(port=8813, numRetries=5)
        print("✅ Connected to TraCI successfully!")
        
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
        for i in range(5):
            traci.simulationStep()
            sim_time = traci.simulation.getTime()
            vehicle_count = len(traci.vehicle.getIDList())
            print(f"   Step {i+1}: Time={sim_time:.1f}s, Vehicles={vehicle_count}")
            time.sleep(0.5)
        
        # Close connection
        traci.close()
        print("✅ Connection test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        print("💡 Make sure SUMO GUI is running and click the 'Run' button")
        return False

if __name__ == "__main__":
    print("🧪 TraCI Connection Test")
    print("=" * 30)
    test_traci_connection()
