"""
Demo: Run Traffic Simulation WITHOUT Real Video
Shows what you can do with built-in data sources
"""

import asyncio
import json
import logging
import os
import sys
from datetime import datetime

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from data_pipeline.osm_collector import OSMCollector
from simulation.sumo_baseline import SUMOBaselineSimulation
from simulation.sumo_ai_controller import SUMOAIController
from omniverse.usd_scene_builder import USDSceneBuilder
from comparison.metrics_analyzer import MetricsAnalyzer

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def demo_without_video():
    """Demo what you can do without real video data"""
    
    print("🚀 DEMO: Traffic Simulation WITHOUT Real Video")
    print("=" * 60)
    
    try:
        # Step 1: Get Real OSM Data
        print("\n1️⃣ Getting Real OSM Data...")
        osm_collector = OSMCollector()
        
        # Get real intersection data from Delhi
        osm_data = osm_collector.query_intersection_data(
            lat=28.6139,  # Delhi coordinates
            lon=77.2090,
            radius=100
        )
        
        print(f"✅ OSM Data Retrieved: {len(osm_data.get('elements', []))} elements")
        
        # Save OSM data
        with open('demo_osm_data.json', 'w') as f:
            json.dump(osm_data, f, indent=2)
        print("✅ OSM data saved to: demo_osm_data.json")
        
        # Step 2: Create SUMO Network
        print("\n2️⃣ Creating SUMO Network...")
        sumo_sim = SUMOBaselineSimulation()
        
        # Create intersection network
        network_file = sumo_sim.create_intersection_network('demo_output')
        print(f"✅ SUMO Network Created: {network_file}")
        
        # Create test routes
        routes_file = sumo_sim.create_test_routes(network_file, 'demo_output', vehicle_count=50)
        print(f"✅ Test Routes Created: {routes_file}")
        
        # Step 3: Run Baseline Simulation
        print("\n3️⃣ Running Baseline Simulation...")
        baseline_results = sumo_sim.run_baseline_simulation('demo_output', duration=300)
        
        if baseline_results['success']:
            print("✅ Baseline Simulation Completed Successfully")
            print(f"   - Network: {baseline_results['network_file']}")
            print(f"   - Routes: {baseline_results['routes_file']}")
            print(f"   - Duration: {baseline_results['duration']} seconds")
        else:
            print(f"❌ Baseline Simulation Failed: {baseline_results.get('error', 'Unknown error')}")
        
        # Step 4: Create Omniverse Scene
        print("\n4️⃣ Creating Omniverse Scene...")
        usd_builder = USDSceneBuilder('demo_output/omniverse')
        
        # Create USD scene
        usd_file = usd_builder.create_intersection_scene(
            network_file=network_file,
            output_file='demo_output/omniverse/demo_scene.usd'
        )
        
        if usd_file:
            print(f"✅ Omniverse Scene Created: {usd_file}")
        else:
            print("❌ Omniverse Scene Creation Failed")
        
        # Step 5: Generate Demo Report
        print("\n5️⃣ Generating Demo Report...")
        
        demo_report = {
            'demo_info': {
                'title': 'Traffic Simulation Demo (No Video Required)',
                'date': datetime.now().isoformat(),
                'status': 'completed'
            },
            'data_sources': {
                'osm_data': {
                    'available': True,
                    'elements': len(osm_data.get('elements', [])),
                    'file': 'demo_osm_data.json'
                },
                'sumo_network': {
                    'available': True,
                    'file': network_file
                },
                'test_routes': {
                    'available': True,
                    'file': routes_file,
                    'vehicle_count': 50
                }
            },
            'simulation_results': {
                'baseline_success': baseline_results['success'],
                'duration': baseline_results.get('duration', 0)
            },
            'omniverse_scene': {
                'usd_file': usd_file,
                'available': bool(usd_file)
            },
            'what_you_can_do': [
                "✅ Run SUMO simulations with test traffic",
                "✅ Create 3D scenes in Omniverse",
                "✅ Analyze traffic patterns",
                "✅ Test different intersection designs",
                "✅ Generate synthetic traffic data"
            ],
            'what_requires_video': [
                "❌ Real vehicle detection and tracking",
                "❌ Actual traffic patterns from your intersection",
                "❌ Real-world accuracy validation",
                "❌ Camera-based traffic analysis"
            ]
        }
        
        # Save demo report
        with open('demo_output/demo_report.json', 'w') as f:
            json.dump(demo_report, f, indent=2)
        
        print("✅ Demo Report Generated: demo_output/demo_report.json")
        
        # Print summary
        print("\n" + "=" * 60)
        print("🎉 DEMO COMPLETED SUCCESSFULLY!")
        print("=" * 60)
        print("✅ What you CAN do without video:")
        print("   • Run SUMO simulations with test traffic")
        print("   • Create 3D scenes in Omniverse")
        print("   • Analyze traffic patterns")
        print("   • Test different intersection designs")
        print("   • Generate synthetic traffic data")
        print("\n❌ What requires YOUR video:")
        print("   • Real vehicle detection and tracking")
        print("   • Actual traffic patterns from your intersection")
        print("   • Real-world accuracy validation")
        print("   • Camera-based traffic analysis")
        print("\n📁 Output files created in: demo_output/")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        return False

def main():
    """Main demo function"""
    print("Traffic Simulation Demo - No Video Required")
    print("This shows what you can do with built-in data sources")
    print()
    
    # Run demo
    success = asyncio.run(demo_without_video())
    
    if success:
        print("\n🎯 Next Steps:")
        print("1. Check the demo_output/ folder for results")
        print("2. Open the USD file in Omniverse")
        print("3. Run SUMO simulation: sumo -c demo_output/baseline_simulation.sumocfg")
        print("4. When ready, provide your real traffic video for accurate replication")
    else:
        print("\n❌ Demo failed. Check the error messages above.")

if __name__ == "__main__":
    main()
