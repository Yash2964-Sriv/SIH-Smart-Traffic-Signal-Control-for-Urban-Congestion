#!/usr/bin/env python3
"""
Test connection fix
"""

import os
import sys

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from ai_controller.simple_working_ai_controller import SimpleWorkingAIController
    
    print("Testing connection fix...")
    
    # Create controller
    controller = SimpleWorkingAIController(
        junction_ids=["I1", "I2"],
        sumo_config="real_traffic_output/visible_traffic_lights.sumocfg"
    )
    
    print("Controller created successfully")
    
    # Try to start SUMO
    result = controller.start_simulation(gui=True, auto_start=False)
    print(f"SUMO start result: {result}")
    
    if result:
        print("SUMO GUI should be open now!")
        print("Click 'Run' in SUMO to test the connection...")
        input("Press Enter to close SUMO...")
        controller.close_simulation()
    else:
        print("Failed to start SUMO")
        
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()

