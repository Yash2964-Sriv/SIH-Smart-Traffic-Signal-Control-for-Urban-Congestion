"""
Main Workflow Entry Point
Smart Traffic Simulator - Complete Workflow
"""

import asyncio
import json
import logging
import os
import sys
from datetime import datetime
from typing import Dict

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from workflow.smart_traffic_workflow import SmartTrafficWorkflow

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('smart_traffic_workflow.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def load_config(config_file: str = "config/workflow_config.json") -> Dict:
    """Load workflow configuration"""
    try:
        if os.path.exists(config_file):
            with open(config_file, 'r') as f:
                return json.load(f)
        else:
            # Create default configuration
            return create_default_config(config_file)
    except Exception as e:
        logger.error(f"Config loading error: {e}")
        return create_default_config(config_file)

def create_default_config(config_file: str) -> Dict:
    """Create default configuration"""
    config = {
        "output_dir": "workflow_output",
        "intersection": {
            "lat": 28.6139,  # Delhi coordinates
            "lon": 77.2090,
            "radius": 100
        },
        "camera": {
            "enabled": False,
            "url": "rtsp://localhost:8554/stream",
            "model_path": "yolov8n.pt"
        },
        "maps_api": {
            "enabled": False,
            "api_key": "your_api_key_here",
            "provider": "google"
        },
        "ai": {
            "model_path": "yolov8n.pt",
            "device": "auto"
        },
        "sumo": {
            "binary": "sumo",
            "tools_path": None
        },
        "simulation": {
            "duration": 3600,  # 1 hour
            "step_length": 1
        }
    }
    
    # Create config directory if it doesn't exist
    os.makedirs(os.path.dirname(config_file), exist_ok=True)
    
    # Save default config
    with open(config_file, 'w') as f:
        json.dump(config, f, indent=2)
    
    logger.info(f"Default configuration created: {config_file}")
    return config

async def main():
    """Main workflow execution"""
    try:
        logger.info("Starting Smart Traffic Simulator Workflow...")
        
        # Load configuration
        config = load_config()
        logger.info(f"Configuration loaded: {config}")
        
        # Initialize workflow
        workflow = SmartTrafficWorkflow(config)
        workflow.initialize_components()
        
        # Run complete workflow
        results = await workflow.run_complete_workflow()
        
        # Print summary
        print("\n" + "="*60)
        print("SMART TRAFFIC SIMULATOR - WORKFLOW COMPLETED")
        print("="*60)
        print(f"Execution Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Output Directory: {config['output_dir']}")
        print(f"Simulation Duration: {config['simulation']['duration']} seconds")
        
        if results.get('comparison_results'):
            comparison = results['comparison_results']
            if 'comparison' in comparison:
                overall_improvement = comparison['comparison'].get('overall_improvement', 0)
                print(f"Overall Improvement: {overall_improvement:.1f}%")
        
        print(f"Results saved to: {config['output_dir']}")
        print("="*60)
        
        return results
        
    except Exception as e:
        logger.error(f"Workflow execution failed: {e}")
        raise

def run_workflow():
    """Run the workflow synchronously"""
    try:
        return asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Workflow interrupted by user")
    except Exception as e:
        logger.error(f"Workflow failed: {e}")
        return None

if __name__ == "__main__":
    # Check if running in interactive mode
    if len(sys.argv) > 1 and sys.argv[1] == "--interactive":
        print("Smart Traffic Simulator - Interactive Mode")
        print("=" * 50)
        
        # Interactive configuration
        config = load_config()
        
        print("Current Configuration:")
        print(json.dumps(config, indent=2))
        
        print("\nOptions:")
        print("1. Run with current configuration")
        print("2. Modify configuration")
        print("3. Exit")
        
        choice = input("\nEnter your choice (1-3): ").strip()
        
        if choice == "1":
            run_workflow()
        elif choice == "2":
            print("Configuration modification not implemented yet.")
            print("Please edit config/workflow_config.json manually.")
        else:
            print("Exiting...")
    else:
        # Run workflow directly
        run_workflow()
