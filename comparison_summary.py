#!/usr/bin/env python3
"""
Comparison Summary Generator
Creates a visual summary of the video vs SUMO comparison results
"""

import json
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime

def create_comparison_summary():
    """Create visual summary of comparison results"""
    print("📊 Creating Visual Comparison Summary")
    print("=" * 60)
    
    # Load the comparison report
    try:
        with open('working_sumo_comparison_report.json', 'r') as f:
            report = json.load(f)
    except FileNotFoundError:
        print("❌ Comparison report not found. Please run the comparison first.")
        return
    
    # Extract key metrics
    video_analysis = report['video_analysis']
    sumo_simulation = report['sumo_simulation']
    comparison_results = report['comparison_results']
    summary = report['summary']
    
    print(f"🎥 YOUR VIDEO ANALYSIS:")
    print(f"  • Frames Analyzed: {summary['video_analyzed']}")
    print(f"  • Average Vehicles: {video_analysis['intersection_analysis']['average_vehicles']:.1f}")
    print(f"  • Peak Traffic: {video_analysis['intersection_analysis']['peak_traffic']['max_vehicles']}")
    print(f"  • Detection Confidence: {video_analysis['intersection_analysis']['average_confidence']:.2f}")
    
    print(f"\n🚦 SUMO SIMULATION:")
    print(f"  • Simulation Steps: {summary['sumo_simulated']}")
    print(f"  • Average Vehicles: {sumo_simulation['average_vehicles']:.1f}")
    print(f"  • Max Vehicles: {sumo_simulation['max_vehicles']}")
    
    print(f"\n📈 COMPARISON RESULTS:")
    print(f"  • Replication Accuracy: {summary['accuracy_achieved']:.1f}%")
    print(f"  • Efficiency Improvement: {summary['efficiency_improvement']:.1f}%")
    print(f"  • AI Performance: {summary['ai_performance']:.1f}%")
    print(f"  • Time Saved by AI: {summary['time_saved']:.1f}%")
    
    # Create visual comparison
    create_visual_comparison(video_analysis, sumo_simulation, comparison_results)
    
    print(f"\n✅ Visual summary created successfully!")

def create_visual_comparison(video_analysis, sumo_simulation, comparison_results):
    """Create visual comparison charts"""
    try:
        # Create figure with subplots
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 10))
        fig.suptitle('SUMO vs Real Video Comparison Analysis', fontsize=16, fontweight='bold')
        
        # 1. Vehicle Count Comparison
        categories = ['Average', 'Peak', 'Efficiency']
        video_values = [
            video_analysis['intersection_analysis']['average_vehicles'],
            video_analysis['intersection_analysis']['peak_traffic']['max_vehicles'],
            comparison_results['efficiency']['video_efficiency']
        ]
        sumo_values = [
            sumo_simulation['average_vehicles'],
            sumo_simulation['max_vehicles'],
            comparison_results['efficiency']['sumo_efficiency']
        ]
        
        x = np.arange(len(categories))
        width = 0.35
        
        ax1.bar(x - width/2, video_values, width, label='Your Video', color='blue', alpha=0.7)
        ax1.bar(x + width/2, sumo_values, width, label='SUMO Simulation', color='red', alpha=0.7)
        ax1.set_xlabel('Metrics')
        ax1.set_ylabel('Values')
        ax1.set_title('Vehicle Count & Efficiency Comparison')
        ax1.set_xticks(x)
        ax1.set_xticklabels(categories)
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # 2. Accuracy Assessment
        accuracy = comparison_results['accuracy']['accuracy_percentage']
        ai_performance = comparison_results['ai_performance']['ai_percentage']
        time_saved = comparison_results['ai_performance']['time_saved_percentage']
        
        metrics = ['Accuracy', 'AI Performance', 'Time Saved']
        values = [accuracy, ai_performance, time_saved]
        colors = ['green' if v >= 80 else 'orange' if v >= 60 else 'red' for v in values]
        
        bars = ax2.bar(metrics, values, color=colors, alpha=0.7)
        ax2.set_ylabel('Percentage (%)')
        ax2.set_title('Performance Metrics')
        ax2.set_ylim(0, 100)
        ax2.grid(True, alpha=0.3)
        
        # Add value labels on bars
        for bar, value in zip(bars, values):
            ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1,
                    f'{value:.1f}%', ha='center', va='bottom', fontweight='bold')
        
        # 3. Traffic Light States (Video)
        tl_analysis = video_analysis['intersection_analysis']['traffic_light_analysis']
        tl_states = ['Red', 'Green', 'Yellow', 'Unknown']
        tl_percentages = [
            tl_analysis['red_percentage'],
            tl_analysis['green_percentage'],
            tl_analysis['yellow_percentage'],
            tl_analysis['unknown_percentage']
        ]
        colors_tl = ['red', 'green', 'yellow', 'gray']
        
        ax3.pie(tl_percentages, labels=tl_states, colors=colors_tl, autopct='%1.1f%%', startangle=90)
        ax3.set_title('Traffic Light States (Your Video)')
        
        # 4. Performance Assessment
        performance_score = (accuracy + ai_performance + time_saved) / 3
        performance_level = 'Excellent' if performance_score >= 90 else 'Good' if performance_score >= 80 else 'Fair' if performance_score >= 70 else 'Needs Improvement'
        
        ax4.text(0.5, 0.7, f'Overall Performance', ha='center', va='center', fontsize=16, fontweight='bold')
        ax4.text(0.5, 0.5, f'{performance_score:.1f}/100', ha='center', va='center', fontsize=24, fontweight='bold', color='green' if performance_score >= 80 else 'orange')
        ax4.text(0.5, 0.3, f'{performance_level}', ha='center', va='center', fontsize=14, style='italic')
        ax4.set_xlim(0, 1)
        ax4.set_ylim(0, 1)
        ax4.axis('off')
        
        plt.tight_layout()
        plt.savefig('comparison_summary.png', dpi=300, bbox_inches='tight')
        print(f"📊 Visual summary saved as 'comparison_summary.png'")
        
    except Exception as e:
        print(f"⚠️  Error creating visual summary: {e}")

if __name__ == "__main__":
    create_comparison_summary()
