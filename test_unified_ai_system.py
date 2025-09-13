#!/usr/bin/env python3
"""
Comprehensive Test Suite for Unified AI System
Tests the complete integrated AI system
"""

import os
import json
import time
from datetime import datetime
from typing import Dict

class UnifiedAISystemTester:
    def __init__(self):
        self.test_results = {
            'unified_ai_controller': False,
            'video_analysis_integration': False,
            'sumo_control_integration': False,
            'comparison_analysis_integration': False,
            'ai_decision_making': False,
            'performance_metrics': False,
            'overall_success': False
        }
        self.errors = []
        
    def run_comprehensive_tests(self) -> Dict:
        """Run comprehensive tests for unified AI system"""
        print("Testing Unified AI System")
        print("=" * 60)
        
        # Test 1: Unified AI Controller
        self.test_unified_ai_controller()
        
        # Test 2: Video Analysis Integration
        self.test_video_analysis_integration()
        
        # Test 3: SUMO Control Integration
        self.test_sumo_control_integration()
        
        # Test 4: Comparison Analysis Integration
        self.test_comparison_analysis_integration()
        
        # Test 5: AI Decision Making
        self.test_ai_decision_making()
        
        # Test 6: Performance Metrics
        self.test_performance_metrics()
        
        # Generate final report
        self.generate_final_report()
        
        return self.test_results
    
    def test_unified_ai_controller(self):
        """Test unified AI controller functionality"""
        print("\nTesting Unified AI Controller...")
        
        try:
            from unified_ai_simple import UnifiedAISimple
            
            # Test initialization
            ai_controller = UnifiedAISimple()
            
            # Test basic functionality
            if hasattr(ai_controller, 'start_unified_analysis'):
                print("  Unified AI controller has start_unified_analysis method")
            else:
                raise AttributeError("Missing start_unified_analysis method")
            
            if hasattr(ai_controller, 'get_ai_status'):
                print("  Unified AI controller has get_ai_status method")
            else:
                raise AttributeError("Missing get_ai_status method")
            
            # Test AI state
            status = ai_controller.get_ai_status()
            if status['ai_state']['current_mode'] == 'idle':
                print("  AI state initialized correctly")
            else:
                raise ValueError("AI state not initialized correctly")
            
            self.test_results['unified_ai_controller'] = True
            print("  Unified AI Controller Test PASSED")
            
        except Exception as e:
            self.errors.append(f"Unified AI Controller Error: {e}")
            print(f"  Unified AI Controller Test FAILED: {e}")
    
    def test_video_analysis_integration(self):
        """Test video analysis integration"""
        print("\nTesting Video Analysis Integration...")
        
        try:
            from unified_ai_simple import UnifiedAISimple
            
            ai_controller = UnifiedAISimple()
            
            # Test video analysis integration
            video_results = ai_controller._analyze_video_realtime()
            
            if video_results and 'vehicle_data' in video_results:
                print(f"  Video analysis integrated: {len(video_results['vehicle_data'])} vehicles tracked")
            else:
                raise ValueError("Video analysis integration failed")
            
            # Test AI enhancement
            if 'traffic_patterns' in video_results:
                patterns = video_results['traffic_patterns']
                if 'ai_corrected_vehicle_count' in patterns:
                    print("  AI enhancement applied to video analysis")
                else:
                    raise ValueError("AI enhancement not applied")
            
            self.test_results['video_analysis_integration'] = True
            print("  Video Analysis Integration Test PASSED")
            
        except Exception as e:
            self.errors.append(f"Video Analysis Integration Error: {e}")
            print(f"  Video Analysis Integration Test FAILED: {e}")
    
    def test_sumo_control_integration(self):
        """Test SUMO control integration"""
        print("\nTesting SUMO Control Integration...")
        
        try:
            from unified_ai_simple import UnifiedAISimple
            
            ai_controller = UnifiedAISimple()
            
            # Test SUMO control integration
            mock_video_data = {
                'traffic_patterns': {'traffic_flow_rate': 100},
                'timing_data': {'avg_travel_time': 10}
            }
            
            sumo_results = ai_controller._create_intelligent_simulation(mock_video_data)
            
            if sumo_results and 'metrics' in sumo_results:
                print(f"  SUMO control integrated: {sumo_results['metrics']['total_vehicles']} vehicles simulated")
            else:
                raise ValueError("SUMO control integration failed")
            
            # Test AI optimization
            if 'ai_adaptations' in sumo_results:
                print("  AI optimization applied to SUMO simulation")
            else:
                raise ValueError("AI optimization not applied")
            
            self.test_results['sumo_control_integration'] = True
            print("  SUMO Control Integration Test PASSED")
            
        except Exception as e:
            self.errors.append(f"SUMO Control Integration Error: {e}")
            print(f"  SUMO Control Integration Test FAILED: {e}")
    
    def test_comparison_analysis_integration(self):
        """Test comparison analysis integration"""
        print("\nTesting Comparison Analysis Integration...")
        
        try:
            from unified_ai_simple import UnifiedAISimple
            
            ai_controller = UnifiedAISimple()
            
            # Test comparison analysis integration
            mock_video_data = {
                'traffic_patterns': {'avg_vehicles_per_frame': 10},
                'timing_data': {'avg_travel_time': 10}
            }
            
            mock_simulation_data = {
                'metrics': {
                    'total_vehicles': 10,
                    'avg_waiting_time': 5,
                    'throughput': 100
                }
            }
            
            comparison_results = ai_controller._run_realtime_comparison(mock_video_data, mock_simulation_data)
            
            if comparison_results and 'accuracy_metrics' in comparison_results:
                print("  Comparison analysis integrated successfully")
            else:
                raise ValueError("Comparison analysis integration failed")
            
            # Test AI enhancement
            if 'efficiency_improvements' in comparison_results:
                efficiency = comparison_results['efficiency_improvements']
                if 'ai_predicted_improvements' in efficiency:
                    print("  AI enhancement applied to comparison analysis")
                else:
                    raise ValueError("AI enhancement not applied to comparison")
            
            self.test_results['comparison_analysis_integration'] = True
            print("  Comparison Analysis Integration Test PASSED")
            
        except Exception as e:
            self.errors.append(f"Comparison Analysis Integration Error: {e}")
            print(f"  Comparison Analysis Integration Test FAILED: {e}")
    
    def test_ai_decision_making(self):
        """Test AI decision making functionality"""
        print("\nTesting AI Decision Making...")
        
        try:
            from unified_ai_simple import UnifiedAISimple
            
            ai_controller = UnifiedAISimple()
            
            # Test AI decision making
            mock_comparison_data = {
                'accuracy_metrics': {'overall_pattern_accuracy': 50},
                'efficiency_improvements': {'overall_efficiency': 20}
            }
            
            ai_decisions = ai_controller._make_unified_ai_decisions(mock_comparison_data)
            
            if ai_decisions and 'traffic_optimization' in ai_decisions:
                print("  AI decision making functional")
            else:
                raise ValueError("AI decision making failed")
            
            # Test decision quality
            optimization = ai_decisions['traffic_optimization']
            if 'priority' in optimization and 'recommended_actions' in optimization:
                print("  AI decisions contain required information")
            else:
                raise ValueError("AI decisions missing required information")
            
            self.test_results['ai_decision_making'] = True
            print("  AI Decision Making Test PASSED")
            
        except Exception as e:
            self.errors.append(f"AI Decision Making Error: {e}")
            print(f"  AI Decision Making Test FAILED: {e}")
    
    def test_performance_metrics(self):
        """Test performance metrics calculation"""
        print("\nTesting Performance Metrics...")
        
        try:
            from unified_ai_simple import UnifiedAISimple
            
            ai_controller = UnifiedAISimple()
            
            # Test performance metrics calculation
            mock_data = {
                'video_data': {'traffic_patterns': {'avg_vehicles_per_frame': 10}},
                'simulation_data': {'metrics': {'total_vehicles': 10}},
                'control_data': {'ai_control_enabled': True},
                'comparison_data': {'accuracy_metrics': {'overall_pattern_accuracy': 80}}
            }
            
            metrics = ai_controller._calculate_unified_metrics(
                mock_data['video_data'],
                mock_data['simulation_data'],
                mock_data['control_data'],
                mock_data['comparison_data']
            )
            
            if metrics and 'overall_ai_performance' in metrics:
                print(f"  Performance metrics calculated: {metrics['overall_ai_performance']}%")
            else:
                raise ValueError("Performance metrics calculation failed")
            
            # Test performance assessment
            assessment = ai_controller._assess_unified_performance(metrics)
            if 'grade' in assessment and 'status' in assessment:
                print(f"  Performance assessed: {assessment['grade']} - {assessment['status']}")
            else:
                raise ValueError("Performance assessment failed")
            
            self.test_results['performance_metrics'] = True
            print("  Performance Metrics Test PASSED")
            
        except Exception as e:
            self.errors.append(f"Performance Metrics Error: {e}")
            print(f"  Performance Metrics Test FAILED: {e}")
    
    def generate_final_report(self):
        """Generate final test report"""
        print("\nGenerating Final Test Report...")
        print("=" * 60)
        
        # Calculate overall success
        passed_tests = sum(1 for result in self.test_results.values() if result)
        total_tests = len(self.test_results) - 1  # Exclude overall_success
        
        self.test_results['overall_success'] = passed_tests == total_tests
        
        # Print results
        print(f"\nTest Results Summary:")
        print(f"  Unified AI Controller: {'PASSED' if self.test_results['unified_ai_controller'] else 'FAILED'}")
        print(f"  Video Analysis Integration: {'PASSED' if self.test_results['video_analysis_integration'] else 'FAILED'}")
        print(f"  SUMO Control Integration: {'PASSED' if self.test_results['sumo_control_integration'] else 'FAILED'}")
        print(f"  Comparison Analysis Integration: {'PASSED' if self.test_results['comparison_analysis_integration'] else 'FAILED'}")
        print(f"  AI Decision Making: {'PASSED' if self.test_results['ai_decision_making'] else 'FAILED'}")
        print(f"  Performance Metrics: {'PASSED' if self.test_results['performance_metrics'] else 'FAILED'}")
        
        print(f"\nOverall Success Rate: {passed_tests}/{total_tests} ({passed_tests/total_tests*100:.1f}%)")
        
        if self.errors:
            print(f"\nErrors Found:")
            for error in self.errors:
                print(f"  - {error}")
        
        # Save report
        report = {
            'timestamp': datetime.now().isoformat(),
            'test_results': self.test_results,
            'errors': self.errors,
            'success_rate': passed_tests / total_tests * 100
        }
        
        with open("unified_ai_test_report.json", 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"\nTest report saved to 'unified_ai_test_report.json'")
        
        if self.test_results['overall_success']:
            print("\nAll tests passed! Unified AI system is ready for production.")
        else:
            print("\nSome tests failed. Please review errors and fix issues.")

def main():
    """Main function to run unified AI system tests"""
    tester = UnifiedAISystemTester()
    results = tester.run_comprehensive_tests()
    
    return results

if __name__ == "__main__":
    main()
