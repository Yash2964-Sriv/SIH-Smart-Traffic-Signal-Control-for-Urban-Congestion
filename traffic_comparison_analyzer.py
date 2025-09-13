#!/usr/bin/env python3
"""
Traffic Comparison Analyzer
Compares real traffic video with SUMO simulation and generates reports
"""

import json
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
from typing import Dict, List, Tuple
import pandas as pd

class TrafficComparisonAnalyzer:
    def __init__(self, real_data_path: str, sumo_data_path: str):
        self.real_data_path = real_data_path
        self.sumo_data_path = sumo_data_path
        self.real_data = {}
        self.sumo_data = {}
        self.comparison_results = {}
        
    def load_data(self) -> bool:
        """Load real and SUMO data"""
        print("📊 Loading comparison data...")
        
        try:
            # Load real traffic data
            with open(self.real_data_path, 'r') as f:
                self.real_data = json.load(f)
            
            # Load SUMO simulation data
            with open(self.sumo_data_path, 'r') as f:
                self.sumo_data = json.load(f)
            
            print("✅ Data loaded successfully")
            return True
            
        except Exception as e:
            print(f"❌ Error loading data: {e}")
            return False
    
    def compare_traffic_patterns(self) -> Dict:
        """Compare traffic patterns between real and simulated data"""
        print("🔍 Comparing traffic patterns...")
        
        real_patterns = self.real_data.get('traffic_patterns', {})
        sumo_metrics = self.sumo_data.get('metrics', {})
        
        # Calculate accuracy metrics
        vehicle_count_accuracy = self._calculate_vehicle_count_accuracy(real_patterns, sumo_metrics)
        flow_rate_accuracy = self._calculate_flow_rate_accuracy(real_patterns, sumo_metrics)
        timing_accuracy = self._calculate_timing_accuracy()
        
        self.comparison_results['traffic_patterns'] = {
            'vehicle_count_accuracy': vehicle_count_accuracy,
            'flow_rate_accuracy': flow_rate_accuracy,
            'timing_accuracy': timing_accuracy,
            'overall_pattern_accuracy': (vehicle_count_accuracy + flow_rate_accuracy + timing_accuracy) / 3
        }
        
        return self.comparison_results['traffic_patterns']
    
    def _calculate_vehicle_count_accuracy(self, real_patterns: Dict, sumo_metrics: Dict) -> float:
        """Calculate accuracy of vehicle count replication"""
        real_avg_vehicles = real_patterns.get('avg_vehicles_per_frame', 0)
        sumo_total_vehicles = sumo_metrics.get('total_vehicles', 0)
        
        # Normalize for comparison
        if real_avg_vehicles > 0:
            accuracy = min(100, max(0, 100 - abs(real_avg_vehicles - sumo_total_vehicles) / real_avg_vehicles * 100))
        else:
            accuracy = 0
        
        return accuracy
    
    def _calculate_flow_rate_accuracy(self, real_patterns: Dict, sumo_metrics: Dict) -> float:
        """Calculate accuracy of flow rate replication"""
        real_flow_rate = real_patterns.get('traffic_flow_rate', 0)
        sumo_throughput = sumo_metrics.get('throughput', 0)
        
        if real_flow_rate > 0:
            accuracy = min(100, max(0, 100 - abs(real_flow_rate - sumo_throughput) / real_flow_rate * 100))
        else:
            accuracy = 0
        
        return accuracy
    
    def _calculate_timing_accuracy(self) -> float:
        """Calculate accuracy of timing replication"""
        real_timing = self.real_data.get('timing_data', {})
        sumo_metrics = self.sumo_data.get('metrics', {})
        
        real_avg_travel_time = real_timing.get('avg_travel_time', 0)
        sumo_avg_speed = sumo_metrics.get('avg_speed', 0)
        
        # Convert speed to travel time for comparison
        if sumo_avg_speed > 0:
            sumo_avg_travel_time = 100 / sumo_avg_speed  # Assuming 100m distance
        else:
            sumo_avg_travel_time = 0
        
        if real_avg_travel_time > 0:
            accuracy = min(100, max(0, 100 - abs(real_avg_travel_time - sumo_avg_travel_time) / real_avg_travel_time * 100))
        else:
            accuracy = 0
        
        return accuracy
    
    def compare_ai_efficiency(self) -> Dict:
        """Compare AI control efficiency with real traffic"""
        print("🤖 Comparing AI efficiency...")
        
        real_timing = self.real_data.get('timing_data', {})
        sumo_metrics = self.sumo_data.get('metrics', {})
        
        # Calculate efficiency improvements
        waiting_time_improvement = self._calculate_waiting_time_improvement(real_timing, sumo_metrics)
        throughput_improvement = self._calculate_throughput_improvement(real_timing, sumo_metrics)
        overall_efficiency = self._calculate_overall_efficiency(real_timing, sumo_metrics)
        
        self.comparison_results['ai_efficiency'] = {
            'waiting_time_improvement': waiting_time_improvement,
            'throughput_improvement': throughput_improvement,
            'overall_efficiency': overall_efficiency,
            'efficiency_score': sumo_metrics.get('efficiency_score', 0)
        }
        
        return self.comparison_results['ai_efficiency']
    
    def _calculate_waiting_time_improvement(self, real_timing: Dict, sumo_metrics: Dict) -> float:
        """Calculate waiting time improvement with AI control"""
        real_waiting_time = real_timing.get('efficiency_metrics', {}).get('waiting_time', 0)
        sumo_waiting_time = sumo_metrics.get('avg_waiting_time', 0)
        
        if real_waiting_time > 0:
            improvement = ((real_waiting_time - sumo_waiting_time) / real_waiting_time) * 100
        else:
            improvement = 0
        
        return improvement
    
    def _calculate_throughput_improvement(self, real_timing: Dict, sumo_metrics: Dict) -> float:
        """Calculate throughput improvement with AI control"""
        real_throughput = real_timing.get('throughput', 0)
        sumo_throughput = sumo_metrics.get('throughput', 0)
        
        if real_throughput > 0:
            improvement = ((sumo_throughput - real_throughput) / real_throughput) * 100
        else:
            improvement = 0
        
        return improvement
    
    def _calculate_overall_efficiency(self, real_timing: Dict, sumo_metrics: Dict) -> float:
        """Calculate overall efficiency improvement"""
        waiting_improvement = self._calculate_waiting_time_improvement(real_timing, sumo_metrics)
        throughput_improvement = self._calculate_throughput_improvement(real_timing, sumo_metrics)
        
        return (waiting_improvement + throughput_improvement) / 2
    
    def generate_comprehensive_report(self) -> Dict:
        """Generate comprehensive comparison report"""
        print("📋 Generating comprehensive report...")
        
        # Compare all aspects
        traffic_patterns = self.compare_traffic_patterns()
        ai_efficiency = self.compare_ai_efficiency()
        
        # Generate overall report
        report = {
            'analysis_timestamp': datetime.now().isoformat(),
            'real_video_analysis': {
                'total_vehicles': len(self.real_data.get('vehicle_data', {})),
                'duration': self.real_data.get('video_info', {}).get('duration', 0),
                'avg_vehicles_per_frame': self.real_data.get('traffic_patterns', {}).get('avg_vehicles_per_frame', 0),
                'traffic_flow_rate': self.real_data.get('traffic_patterns', {}).get('traffic_flow_rate', 0)
            },
            'sumo_simulation': {
                'total_vehicles': self.sumo_data.get('metrics', {}).get('total_vehicles', 0),
                'avg_waiting_time': self.sumo_data.get('metrics', {}).get('avg_waiting_time', 0),
                'avg_speed': self.sumo_data.get('metrics', {}).get('avg_speed', 0),
                'throughput': self.sumo_data.get('metrics', {}).get('throughput', 0),
                'efficiency_score': self.sumo_data.get('metrics', {}).get('efficiency_score', 0)
            },
            'accuracy_metrics': traffic_patterns,
            'efficiency_improvements': ai_efficiency,
            'overall_assessment': self._generate_overall_assessment()
        }
        
        return report
    
    def _generate_overall_assessment(self) -> Dict:
        """Generate overall assessment of the system"""
        traffic_patterns = self.comparison_results.get('traffic_patterns', {})
        ai_efficiency = self.comparison_results.get('ai_efficiency', {})
        
        overall_accuracy = traffic_patterns.get('overall_pattern_accuracy', 0)
        overall_efficiency = ai_efficiency.get('overall_efficiency', 0)
        
        # Grade the system
        if overall_accuracy >= 90 and overall_efficiency >= 20:
            grade = "Excellent"
        elif overall_accuracy >= 80 and overall_efficiency >= 10:
            grade = "Good"
        elif overall_accuracy >= 70 and overall_efficiency >= 0:
            grade = "Fair"
        else:
            grade = "Needs Improvement"
        
        return {
            'overall_accuracy': overall_accuracy,
            'overall_efficiency_improvement': overall_efficiency,
            'grade': grade,
            'recommendations': self._generate_recommendations(overall_accuracy, overall_efficiency)
        }
    
    def _generate_recommendations(self, accuracy: float, efficiency: float) -> List[str]:
        """Generate recommendations based on performance"""
        recommendations = []
        
        if accuracy < 80:
            recommendations.append("Improve traffic pattern replication accuracy")
        if efficiency < 10:
            recommendations.append("Optimize AI traffic control algorithms")
        if accuracy >= 90 and efficiency >= 20:
            recommendations.append("System performing excellently - consider deployment")
        
        return recommendations
    
    def save_report(self, report: Dict, output_path: str = "traffic_comparison_report.json"):
        """Save comprehensive report"""
        with open(output_path, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        print(f"💾 Report saved to {output_path}")
    
    def generate_visualizations(self, report: Dict):
        """Generate visualization charts"""
        print("📊 Generating visualizations...")
        
        # Create comparison charts
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        
        # Accuracy metrics
        accuracy_data = report['accuracy_metrics']
        axes[0, 0].bar(['Vehicle Count', 'Flow Rate', 'Timing'], 
                      [accuracy_data['vehicle_count_accuracy'], 
                       accuracy_data['flow_rate_accuracy'], 
                       accuracy_data['timing_accuracy']])
        axes[0, 0].set_title('Replication Accuracy (%)')
        axes[0, 0].set_ylim(0, 100)
        
        # Efficiency improvements
        efficiency_data = report['efficiency_improvements']
        axes[0, 1].bar(['Waiting Time', 'Throughput', 'Overall'], 
                      [efficiency_data['waiting_time_improvement'], 
                       efficiency_data['throughput_improvement'], 
                       efficiency_data['overall_efficiency']])
        axes[0, 1].set_title('AI Efficiency Improvements (%)')
        
        # Overall assessment
        assessment = report['overall_assessment']
        axes[1, 0].pie([assessment['overall_accuracy'], 
                       100 - assessment['overall_accuracy']], 
                      labels=['Accuracy', 'Room for Improvement'],
                      autopct='%1.1f%%')
        axes[1, 0].set_title('Overall Accuracy')
        
        # Performance summary
        axes[1, 1].text(0.5, 0.5, f"Grade: {assessment['grade']}\n"
                                   f"Accuracy: {assessment['overall_accuracy']:.1f}%\n"
                                   f"Efficiency: {assessment['overall_efficiency_improvement']:.1f}%",
                       ha='center', va='center', fontsize=12,
                       bbox=dict(boxstyle="round,pad=0.3", facecolor="lightblue"))
        axes[1, 1].set_title('Performance Summary')
        axes[1, 1].axis('off')
        
        plt.tight_layout()
        plt.savefig('traffic_comparison_analysis.png', dpi=300, bbox_inches='tight')
        plt.show()
        
        print("📈 Visualizations saved as 'traffic_comparison_analysis.png'")

def main():
    """Main function to run comparison analysis"""
    analyzer = TrafficComparisonAnalyzer("real_traffic_analysis.json", "sumo_replication_data.json")
    
    if analyzer.load_data():
        report = analyzer.generate_comprehensive_report()
        analyzer.save_report(report)
        analyzer.generate_visualizations(report)
        
        print("\n🎉 Traffic Comparison Analysis Completed!")
        print(f"📊 Overall Accuracy: {report['overall_assessment']['overall_accuracy']:.1f}%")
        print(f"🚀 Efficiency Improvement: {report['overall_assessment']['overall_efficiency_improvement']:.1f}%")
        print(f"⭐ Grade: {report['overall_assessment']['grade']}")
    else:
        print("❌ Analysis failed")

if __name__ == "__main__":
    main()
