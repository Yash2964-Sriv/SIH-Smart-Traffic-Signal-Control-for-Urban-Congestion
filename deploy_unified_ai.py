#!/usr/bin/env python3
"""
Deployment Script for Unified AI Controller
Deploys and tests the unified AI system
"""

import os
import json
import time
import subprocess
from datetime import datetime
from typing import Dict, List

class UnifiedAIDeployment:
    def __init__(self):
        self.deployment_status = {
            'start_time': datetime.now(),
            'stages_completed': [],
            'errors': [],
            'test_results': {},
            'deployment_success': False
        }
        
    def deploy_unified_ai(self) -> Dict:
        """Deploy the unified AI system"""
        print("🚀 Deploying Unified AI Controller")
        print("=" * 60)
        
        try:
            # Stage 1: Pre-deployment checks
            print("\n🔍 Stage 1: Pre-deployment Checks...")
            if not self._run_pre_deployment_checks():
                raise Exception("Pre-deployment checks failed")
            
            # Stage 2: System integration test
            print("\n🧪 Stage 2: System Integration Test...")
            if not self._run_integration_test():
                raise Exception("Integration test failed")
            
            # Stage 3: Performance validation
            print("\n📊 Stage 3: Performance Validation...")
            if not self._run_performance_validation():
                raise Exception("Performance validation failed")
            
            # Stage 4: Deploy unified AI
            print("\n🤖 Stage 4: Deploying Unified AI...")
            if not self._deploy_ai_system():
                raise Exception("AI deployment failed")
            
            # Stage 5: Final testing
            print("\n✅ Stage 5: Final Testing...")
            if not self._run_final_tests():
                raise Exception("Final testing failed")
            
            self.deployment_status['deployment_success'] = True
            self.deployment_status['end_time'] = datetime.now()
            
            print("\n🎉 Unified AI Deployment Completed Successfully!")
            self._print_deployment_summary()
            
            return self.deployment_status
            
        except Exception as e:
            self.deployment_status['errors'].append(str(e))
            print(f"\n❌ Deployment failed: {e}")
            return self.deployment_status
    
    def _run_pre_deployment_checks(self) -> bool:
        """Run pre-deployment checks"""
        print("  🔍 Checking system requirements...")
        
        checks = {
            'python_version': self._check_python_version(),
            'required_packages': self._check_required_packages(),
            'video_file': self._check_video_file(),
            'sumo_installation': self._check_sumo_installation(),
            'file_permissions': self._check_file_permissions()
        }
        
        all_passed = all(checks.values())
        
        for check, passed in checks.items():
            status = "✅" if passed else "❌"
            print(f"    {status} {check.replace('_', ' ').title()}")
        
        if all_passed:
            self.deployment_status['stages_completed'].append('pre_deployment_checks')
            print("  ✅ Pre-deployment checks passed")
            return True
        else:
            print("  ❌ Pre-deployment checks failed")
            return False
    
    def _check_python_version(self) -> bool:
        """Check Python version"""
        import sys
        return sys.version_info >= (3, 7)
    
    def _check_required_packages(self) -> bool:
        """Check required packages"""
        required_packages = [
            'cv2', 'numpy', 'traci', 'matplotlib', 'json'
        ]
        
        for package in required_packages:
            try:
                __import__(package)
            except ImportError:
                return False
        return True
    
    def _check_video_file(self) -> bool:
        """Check if video file exists"""
        return os.path.exists("Traffic_videos/stock-footage-drone-shot-way-intersection.webm")
    
    def _check_sumo_installation(self) -> bool:
        """Check SUMO installation"""
        try:
            result = subprocess.run(['sumo', '--version'], 
                                  capture_output=True, text=True, timeout=10)
            return result.returncode == 0
        except:
            return False
    
    def _check_file_permissions(self) -> bool:
        """Check file permissions"""
        try:
            # Test write permission
            with open("test_write_permission.txt", 'w') as f:
                f.write("test")
            os.remove("test_write_permission.txt")
            return True
        except:
            return False
    
    def _run_integration_test(self) -> bool:
        """Run system integration test"""
        print("  🧪 Testing component integration...")
        
        try:
            # Test unified AI controller import
            from unified_ai_controller import UnifiedAIController
            
            # Test initialization
            ai_controller = UnifiedAIController()
            
            # Test component loading
            status = ai_controller.get_ai_status()
            
            if status['ai_state']['current_mode'] == 'idle':
                self.deployment_status['stages_completed'].append('integration_test')
                print("  ✅ Integration test passed")
                return True
            else:
                print("  ❌ Integration test failed")
                return False
                
        except Exception as e:
            print(f"  ❌ Integration test error: {e}")
            return False
    
    def _run_performance_validation(self) -> bool:
        """Run performance validation"""
        print("  📊 Validating performance...")
        
        try:
            # Test video analysis performance
            start_time = time.time()
            
            from traffic_video_analyzer import TrafficVideoAnalyzer
            analyzer = TrafficVideoAnalyzer("Traffic_videos/stock-footage-drone-shot-way-intersection.webm")
            
            # Quick analysis test
            analysis_time = time.time() - start_time
            
            if analysis_time < 30:  # Should complete within 30 seconds
                self.deployment_status['stages_completed'].append('performance_validation')
                print(f"  ✅ Performance validation passed ({analysis_time:.2f}s)")
                return True
            else:
                print(f"  ❌ Performance validation failed (too slow: {analysis_time:.2f}s)")
                return False
                
        except Exception as e:
            print(f"  ❌ Performance validation error: {e}")
            return False
    
    def _deploy_ai_system(self) -> bool:
        """Deploy the AI system"""
        print("  🤖 Deploying unified AI system...")
        
        try:
            # Create deployment configuration
            deployment_config = {
                'deployment_time': datetime.now().isoformat(),
                'ai_components': [
                    'video_analyzer',
                    'sumo_replicator', 
                    'comparison_analyzer',
                    'traffic_controller'
                ],
                'monitoring_enabled': True,
                'real_time_adaptation': True,
                'performance_tracking': True
            }
            
            # Save deployment config
            with open("deployment_config.json", 'w') as f:
                json.dump(deployment_config, f, indent=2)
            
            # Create startup script
            self._create_startup_script()
            
            self.deployment_status['stages_completed'].append('ai_deployment')
            print("  ✅ AI system deployed successfully")
            return True
            
        except Exception as e:
            print(f"  ❌ AI deployment error: {e}")
            return False
    
    def _create_startup_script(self):
        """Create startup script for the unified AI"""
        startup_script = """#!/usr/bin/env python3
\"\"\"
Unified AI Controller Startup Script
\"\"\"

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from unified_ai_controller import UnifiedAIController

def main():
    print("Starting Unified AI Controller...")
    
    # Initialize and start the unified AI
    ai_controller = UnifiedAIController()
    
    # Run unified analysis
    results = ai_controller.start_unified_analysis()
    
    if results:
        print("Unified AI Controller started successfully!")
        print(f"Performance: {results.get('unified_metrics', {}).get('overall_ai_performance', 0):.1f}%")
        
        # Start real-time monitoring
        ai_controller.start_realtime_monitoring()
    else:
        print("Failed to start Unified AI Controller")

if __name__ == "__main__":
    main()
"""
        
        with open("start_unified_ai.py", 'w') as f:
            f.write(startup_script)
    
    def _run_final_tests(self) -> bool:
        """Run final comprehensive tests"""
        print("  ✅ Running final tests...")
        
        try:
            # Test unified AI controller
            from unified_ai_controller import UnifiedAIController
            
            ai_controller = UnifiedAIController()
            
            # Test AI analysis workflow
            print("    🧪 Testing AI analysis workflow...")
            results = ai_controller.start_unified_analysis()
            
            if results and 'unified_metrics' in results:
                performance = results['unified_metrics']['overall_ai_performance']
                
                if performance >= 80:  # Minimum performance threshold
                    self.deployment_status['test_results']['ai_performance'] = performance
                    self.deployment_status['stages_completed'].append('final_tests')
                    print(f"    ✅ Final tests passed (Performance: {performance:.1f}%)")
                    return True
                else:
                    print(f"    ❌ Final tests failed (Performance too low: {performance:.1f}%)")
                    return False
            else:
                print("    ❌ Final tests failed (No results generated)")
                return False
                
        except Exception as e:
            print(f"    ❌ Final tests error: {e}")
            return False
    
    def _print_deployment_summary(self):
        """Print deployment summary"""
        print("\n" + "=" * 60)
        print("📊 DEPLOYMENT SUMMARY")
        print("=" * 60)
        
        duration = self.deployment_status['end_time'] - self.deployment_status['start_time']
        
        print(f"⏱️ Deployment Time: {duration}")
        print(f"✅ Stages Completed: {len(self.deployment_status['stages_completed'])}/5")
        print(f"📊 Success Rate: {len(self.deployment_status['stages_completed'])/5*100:.1f}%")
        
        if 'ai_performance' in self.deployment_status['test_results']:
            print(f"🤖 AI Performance: {self.deployment_status['test_results']['ai_performance']:.1f}%")
        
        print(f"\n📁 Generated Files:")
        print(f"  - deployment_config.json")
        print(f"  - start_unified_ai.py")
        print(f"  - unified_ai_results.json")
        
        print(f"\n🚀 System Status: {'READY FOR PRODUCTION' if self.deployment_status['deployment_success'] else 'DEPLOYMENT FAILED'}")
        
        if self.deployment_status['errors']:
            print(f"\n❌ Errors:")
            for error in self.deployment_status['errors']:
                print(f"  - {error}")
    
    def start_production_mode(self):
        """Start production mode"""
        print("\n🚀 Starting Production Mode")
        print("=" * 60)
        
        try:
            # Run the unified AI controller
            subprocess.run([sys.executable, "start_unified_ai.py"], check=True)
        except Exception as e:
            print(f"❌ Production mode error: {e}")

def main():
    """Main deployment function"""
    print("🚀 Smart Traffic Simulator - Unified AI Deployment")
    print("=" * 60)
    
    # Initialize deployment
    deployment = UnifiedAIDeployment()
    
    # Deploy unified AI
    results = deployment.deploy_unified_ai()
    
    if results['deployment_success']:
        print("\n🎉 Deployment Successful!")
        
        # Ask if user wants to start production mode
        response = input("\n🚀 Start production mode? (y/n): ")
        if response.lower() == 'y':
            deployment.start_production_mode()
    else:
        print("\n❌ Deployment Failed!")
        print("Please check the errors and try again.")

if __name__ == "__main__":
    import sys
    main()
