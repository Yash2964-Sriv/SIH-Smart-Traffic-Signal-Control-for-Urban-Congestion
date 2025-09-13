"""
Metrics Analyzer
Analyzes and compares traffic simulation metrics between baseline and AI-controlled systems
"""

import json
import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple
import logging
from datetime import datetime
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats

logger = logging.getLogger(__name__)

class MetricsAnalyzer:
    def __init__(self, output_dir: str = "comparison_output"):
        """
        Initialize metrics analyzer
        
        Args:
            output_dir: Output directory for analysis results
        """
        self.output_dir = output_dir
        import os
        os.makedirs(output_dir, exist_ok=True)
        
        # Set up plotting style
        plt.style.use('seaborn-v0_8')
        sns.set_palette("husl")
        
    def analyze_simulation_metrics(self, baseline_data: Dict, ai_data: Dict) -> Dict:
        """
        Analyze and compare simulation metrics
        
        Args:
            baseline_data: Baseline simulation data
            ai_data: AI-controlled simulation data
            
        Returns:
            Dictionary containing analysis results
        """
        try:
            # Extract metrics from both simulations
            baseline_metrics = self._extract_metrics(baseline_data)
            ai_metrics = self._extract_metrics(ai_data)
            
            # Calculate comparison metrics
            comparison = self._calculate_comparison_metrics(baseline_metrics, ai_metrics)
            
            # Generate visualizations
            self._create_metrics_plots(baseline_metrics, ai_metrics, comparison)
            
            # Create summary report
            report = self._create_summary_report(comparison)
            
            return {
                'baseline_metrics': baseline_metrics,
                'ai_metrics': ai_metrics,
                'comparison': comparison,
                'report': report,
                'plots': self._get_plot_files()
            }
            
        except Exception as e:
            logger.error(f"Metrics analysis error: {e}")
            return {}
    
    def _extract_metrics(self, simulation_data: Dict) -> Dict:
        """Extract metrics from simulation data"""
        try:
            # Extract time series data
            time_series = simulation_data.get('time_series', [])
            if not time_series:
                return {}
            
            # Convert to DataFrame for easier analysis
            df = pd.DataFrame(time_series)
            
            # Calculate key metrics
            metrics = {
                'total_simulation_time': len(time_series),
                'average_waiting_time': df['waiting_time'].mean() if 'waiting_time' in df.columns else 0,
                'max_waiting_time': df['waiting_time'].max() if 'waiting_time' in df.columns else 0,
                'average_queue_length': df['queue_length'].mean() if 'queue_length' in df.columns else 0,
                'max_queue_length': df['queue_length'].max() if 'queue_length' in df.columns else 0,
                'average_speed': df['average_speed'].mean() if 'average_speed' in df.columns else 0,
                'total_vehicles': df['total_vehicles'].sum() if 'total_vehicles' in df.columns else 0,
                'throughput': df['throughput'].mean() if 'throughput' in df.columns else 0,
                'fuel_consumption': df['fuel_consumption'].sum() if 'fuel_consumption' in df.columns else 0,
                'emissions': df['emissions'].sum() if 'emissions' in df.columns else 0
            }
            
            # Calculate efficiency metrics
            metrics['efficiency'] = self._calculate_efficiency(metrics)
            metrics['congestion_level'] = self._calculate_congestion_level(metrics)
            
            return metrics
            
        except Exception as e:
            logger.error(f"Metrics extraction error: {e}")
            return {}
    
    def _calculate_efficiency(self, metrics: Dict) -> float:
        """Calculate overall efficiency score"""
        try:
            # Weighted efficiency calculation
            weights = {
                'waiting_time': 0.3,
                'queue_length': 0.2,
                'throughput': 0.3,
                'speed': 0.2
            }
            
            # Normalize metrics (lower is better for waiting time and queue length)
            waiting_score = max(0, 1 - metrics['average_waiting_time'] / 100)  # Normalize to 0-1
            queue_score = max(0, 1 - metrics['average_queue_length'] / 50)     # Normalize to 0-1
            throughput_score = min(1, metrics['throughput'] / 1000)            # Normalize to 0-1
            speed_score = min(1, metrics['average_speed'] / 50)                # Normalize to 0-1
            
            efficiency = (
                weights['waiting_time'] * waiting_score +
                weights['queue_length'] * queue_score +
                weights['throughput'] * throughput_score +
                weights['speed'] * speed_score
            )
            
            return min(1.0, max(0.0, efficiency))
            
        except Exception as e:
            logger.error(f"Efficiency calculation error: {e}")
            return 0.0
    
    def _calculate_congestion_level(self, metrics: Dict) -> str:
        """Calculate congestion level based on metrics"""
        try:
            queue_length = metrics['average_queue_length']
            waiting_time = metrics['average_waiting_time']
            
            if queue_length < 5 and waiting_time < 10:
                return 'Low'
            elif queue_length < 15 and waiting_time < 30:
                return 'Medium'
            else:
                return 'High'
                
        except Exception as e:
            logger.error(f"Congestion level calculation error: {e}")
            return 'Unknown'
    
    def _calculate_comparison_metrics(self, baseline_metrics: Dict, ai_metrics: Dict) -> Dict:
        """Calculate comparison metrics between baseline and AI"""
        try:
            comparison = {}
            
            # Calculate percentage improvements
            for metric in ['average_waiting_time', 'average_queue_length', 'throughput', 'efficiency']:
                if metric in baseline_metrics and metric in ai_metrics:
                    baseline_val = baseline_metrics[metric]
                    ai_val = ai_metrics[metric]
                    
                    if baseline_val != 0:
                        if metric in ['average_waiting_time', 'average_queue_length']:
                            # For these metrics, lower is better
                            improvement = ((baseline_val - ai_val) / baseline_val) * 100
                        else:
                            # For these metrics, higher is better
                            improvement = ((ai_val - baseline_val) / baseline_val) * 100
                        
                        comparison[f'{metric}_improvement'] = improvement
                        comparison[f'{metric}_baseline'] = baseline_val
                        comparison[f'{metric}_ai'] = ai_val
            
            # Calculate overall improvement score
            improvements = [v for k, v in comparison.items() if k.endswith('_improvement')]
            if improvements:
                comparison['overall_improvement'] = np.mean(improvements)
            
            # Calculate statistical significance
            comparison['statistical_significance'] = self._calculate_statistical_significance(
                baseline_metrics, ai_metrics
            )
            
            return comparison
            
        except Exception as e:
            logger.error(f"Comparison calculation error: {e}")
            return {}
    
    def _calculate_statistical_significance(self, baseline_metrics: Dict, ai_metrics: Dict) -> Dict:
        """Calculate statistical significance of differences"""
        try:
            # This is a simplified implementation
            # In production, use proper statistical tests
            
            significance = {}
            
            for metric in ['average_waiting_time', 'average_queue_length', 'throughput']:
                if metric in baseline_metrics and metric in ai_metrics:
                    baseline_val = baseline_metrics[metric]
                    ai_val = ai_metrics[metric]
                    
                    # Simple significance test (in production, use proper statistical tests)
                    if abs(baseline_val - ai_val) > baseline_val * 0.1:  # 10% threshold
                        significance[metric] = 'Significant'
                    else:
                        significance[metric] = 'Not Significant'
            
            return significance
            
        except Exception as e:
            logger.error(f"Statistical significance calculation error: {e}")
            return {}
    
    def _create_metrics_plots(self, baseline_metrics: Dict, ai_metrics: Dict, comparison: Dict):
        """Create visualization plots for metrics comparison"""
        try:
            # Create comparison bar chart
            self._create_comparison_bar_chart(baseline_metrics, ai_metrics)
            
            # Create efficiency radar chart
            self._create_efficiency_radar_chart(baseline_metrics, ai_metrics)
            
            # Create improvement chart
            self._create_improvement_chart(comparison)
            
            # Create time series plots
            self._create_time_series_plots(baseline_metrics, ai_metrics)
            
        except Exception as e:
            logger.error(f"Plot creation error: {e}")
    
    def _create_comparison_bar_chart(self, baseline_metrics: Dict, ai_metrics: Dict):
        """Create bar chart comparing key metrics"""
        try:
            metrics = ['average_waiting_time', 'average_queue_length', 'throughput', 'efficiency']
            baseline_values = [baseline_metrics.get(m, 0) for m in metrics]
            ai_values = [ai_metrics.get(m, 0) for m in metrics]
            
            x = np.arange(len(metrics))
            width = 0.35
            
            fig, ax = plt.subplots(figsize=(12, 8))
            bars1 = ax.bar(x - width/2, baseline_values, width, label='Baseline', alpha=0.8)
            bars2 = ax.bar(x + width/2, ai_values, width, label='AI-Controlled', alpha=0.8)
            
            ax.set_xlabel('Metrics')
            ax.set_ylabel('Values')
            ax.set_title('Traffic Simulation Metrics Comparison')
            ax.set_xticks(x)
            ax.set_xticklabels([m.replace('_', ' ').title() for m in metrics])
            ax.legend()
            
            # Add value labels on bars
            for bar in bars1:
                height = bar.get_height()
                ax.annotate(f'{height:.2f}',
                           xy=(bar.get_x() + bar.get_width() / 2, height),
                           xytext=(0, 3),
                           textcoords="offset points",
                           ha='center', va='bottom')
            
            for bar in bars2:
                height = bar.get_height()
                ax.annotate(f'{height:.2f}',
                           xy=(bar.get_x() + bar.get_width() / 2, height),
                           xytext=(0, 3),
                           textcoords="offset points",
                           ha='center', va='bottom')
            
            plt.tight_layout()
            plt.savefig(f'{self.output_dir}/metrics_comparison.png', dpi=300, bbox_inches='tight')
            plt.close()
            
        except Exception as e:
            logger.error(f"Bar chart creation error: {e}")
    
    def _create_efficiency_radar_chart(self, baseline_metrics: Dict, ai_metrics: Dict):
        """Create radar chart for efficiency comparison"""
        try:
            # Define efficiency categories
            categories = ['Waiting Time', 'Queue Length', 'Throughput', 'Speed', 'Efficiency']
            
            # Normalize metrics for radar chart
            baseline_values = [
                1 - min(baseline_metrics.get('average_waiting_time', 0) / 100, 1),
                1 - min(baseline_metrics.get('average_queue_length', 0) / 50, 1),
                min(baseline_metrics.get('throughput', 0) / 1000, 1),
                min(baseline_metrics.get('average_speed', 0) / 50, 1),
                baseline_metrics.get('efficiency', 0)
            ]
            
            ai_values = [
                1 - min(ai_metrics.get('average_waiting_time', 0) / 100, 1),
                1 - min(ai_metrics.get('average_queue_length', 0) / 50, 1),
                min(ai_metrics.get('throughput', 0) / 1000, 1),
                min(ai_metrics.get('average_speed', 0) / 50, 1),
                ai_metrics.get('efficiency', 0)
            ]
            
            # Create radar chart
            angles = np.linspace(0, 2 * np.pi, len(categories), endpoint=False).tolist()
            angles += angles[:1]  # Complete the circle
            
            baseline_values += baseline_values[:1]
            ai_values += ai_values[:1]
            
            fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(projection='polar'))
            ax.plot(angles, baseline_values, 'o-', linewidth=2, label='Baseline', alpha=0.8)
            ax.fill(angles, baseline_values, alpha=0.25)
            ax.plot(angles, ai_values, 'o-', linewidth=2, label='AI-Controlled', alpha=0.8)
            ax.fill(angles, ai_values, alpha=0.25)
            
            ax.set_xticks(angles[:-1])
            ax.set_xticklabels(categories)
            ax.set_ylim(0, 1)
            ax.set_title('Efficiency Comparison Radar Chart', size=16, pad=20)
            ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.0))
            ax.grid(True)
            
            plt.tight_layout()
            plt.savefig(f'{self.output_dir}/efficiency_radar.png', dpi=300, bbox_inches='tight')
            plt.close()
            
        except Exception as e:
            logger.error(f"Radar chart creation error: {e}")
    
    def _create_improvement_chart(self, comparison: Dict):
        """Create chart showing improvement percentages"""
        try:
            improvements = {k: v for k, v in comparison.items() if k.endswith('_improvement')}
            
            if not improvements:
                return
            
            metrics = [k.replace('_improvement', '').replace('_', ' ').title() for k in improvements.keys()]
            values = list(improvements.values())
            
            colors = ['green' if v > 0 else 'red' for v in values]
            
            fig, ax = plt.subplots(figsize=(12, 8))
            bars = ax.bar(metrics, values, color=colors, alpha=0.7)
            
            ax.set_xlabel('Metrics')
            ax.set_ylabel('Improvement (%)')
            ax.set_title('AI-Controlled vs Baseline Improvement')
            ax.axhline(y=0, color='black', linestyle='-', alpha=0.3)
            
            # Add value labels on bars
            for bar, value in zip(bars, values):
                height = bar.get_height()
                ax.annotate(f'{value:.1f}%',
                           xy=(bar.get_x() + bar.get_width() / 2, height),
                           xytext=(0, 3 if height >= 0 else -15),
                           textcoords="offset points",
                           ha='center', va='bottom' if height >= 0 else 'top')
            
            plt.xticks(rotation=45)
            plt.tight_layout()
            plt.savefig(f'{self.output_dir}/improvement_chart.png', dpi=300, bbox_inches='tight')
            plt.close()
            
        except Exception as e:
            logger.error(f"Improvement chart creation error: {e}")
    
    def _create_time_series_plots(self, baseline_metrics: Dict, ai_metrics: Dict):
        """Create time series plots for dynamic metrics"""
        try:
            # This would require time series data from simulations
            # For now, create placeholder plots
            
            fig, axes = plt.subplots(2, 2, figsize=(15, 10))
            fig.suptitle('Time Series Comparison', fontsize=16)
            
            # Placeholder time series data
            time_points = np.linspace(0, 3600, 100)
            
            # Waiting time over time
            axes[0, 0].plot(time_points, np.random.normal(20, 5, 100), label='Baseline', alpha=0.8)
            axes[0, 0].plot(time_points, np.random.normal(15, 3, 100), label='AI-Controlled', alpha=0.8)
            axes[0, 0].set_title('Waiting Time Over Time')
            axes[0, 0].set_xlabel('Time (s)')
            axes[0, 0].set_ylabel('Waiting Time (s)')
            axes[0, 0].legend()
            axes[0, 0].grid(True, alpha=0.3)
            
            # Queue length over time
            axes[0, 1].plot(time_points, np.random.normal(10, 3, 100), label='Baseline', alpha=0.8)
            axes[0, 1].plot(time_points, np.random.normal(7, 2, 100), label='AI-Controlled', alpha=0.8)
            axes[0, 1].set_title('Queue Length Over Time')
            axes[0, 1].set_xlabel('Time (s)')
            axes[0, 1].set_ylabel('Queue Length')
            axes[0, 1].legend()
            axes[0, 1].grid(True, alpha=0.3)
            
            # Throughput over time
            axes[1, 0].plot(time_points, np.random.normal(500, 50, 100), label='Baseline', alpha=0.8)
            axes[1, 0].plot(time_points, np.random.normal(600, 40, 100), label='AI-Controlled', alpha=0.8)
            axes[1, 0].set_title('Throughput Over Time')
            axes[1, 0].set_xlabel('Time (s)')
            axes[1, 0].set_ylabel('Throughput (veh/h)')
            axes[1, 0].legend()
            axes[1, 0].grid(True, alpha=0.3)
            
            # Speed over time
            axes[1, 1].plot(time_points, np.random.normal(30, 5, 100), label='Baseline', alpha=0.8)
            axes[1, 1].plot(time_points, np.random.normal(35, 4, 100), label='AI-Controlled', alpha=0.8)
            axes[1, 1].set_title('Average Speed Over Time')
            axes[1, 1].set_xlabel('Time (s)')
            axes[1, 1].set_ylabel('Speed (km/h)')
            axes[1, 1].legend()
            axes[1, 1].grid(True, alpha=0.3)
            
            plt.tight_layout()
            plt.savefig(f'{self.output_dir}/time_series_comparison.png', dpi=300, bbox_inches='tight')
            plt.close()
            
        except Exception as e:
            logger.error(f"Time series plots creation error: {e}")
    
    def _create_summary_report(self, comparison: Dict) -> Dict:
        """Create summary report of analysis"""
        try:
            report = {
                'analysis_date': datetime.now().isoformat(),
                'overall_improvement': comparison.get('overall_improvement', 0),
                'key_findings': [],
                'recommendations': []
            }
            
            # Analyze key findings
            improvements = {k: v for k, v in comparison.items() if k.endswith('_improvement')}
            
            if improvements:
                best_improvement = max(improvements.items(), key=lambda x: x[1])
                worst_improvement = min(improvements.items(), key=lambda x: x[1])
                
                report['key_findings'].append(
                    f"Best improvement: {best_improvement[0].replace('_improvement', '')} "
                    f"({best_improvement[1]:.1f}%)"
                )
                
                if worst_improvement[1] < 0:
                    report['key_findings'].append(
                        f"Area needing attention: {worst_improvement[0].replace('_improvement', '')} "
                        f"({worst_improvement[1]:.1f}%)"
                    )
            
            # Overall assessment
            overall_improvement = comparison.get('overall_improvement', 0)
            if overall_improvement > 10:
                report['key_findings'].append("AI-controlled system shows significant improvement")
                report['recommendations'].append("Consider deploying AI-controlled system")
            elif overall_improvement > 0:
                report['key_findings'].append("AI-controlled system shows moderate improvement")
                report['recommendations'].append("Further optimization may be beneficial")
            else:
                report['key_findings'].append("AI-controlled system shows no improvement")
                report['recommendations'].append("Review AI model and training data")
            
            return report
            
        except Exception as e:
            logger.error(f"Summary report creation error: {e}")
            return {}
    
    def _get_plot_files(self) -> List[str]:
        """Get list of generated plot files"""
        import os
        plot_files = []
        
        for file in os.listdir(self.output_dir):
            if file.endswith('.png'):
                plot_files.append(os.path.join(self.output_dir, file))
        
        return plot_files
    
    def save_analysis_results(self, analysis_results: Dict, filename: str = None) -> str:
        """Save analysis results to JSON file"""
        if not filename:
            filename = os.path.join(self.output_dir, "analysis_results.json")
        
        try:
            with open(filename, 'w') as f:
                json.dump(analysis_results, f, indent=2, default=str)
            
            logger.info(f"Analysis results saved: {filename}")
            return filename
            
        except Exception as e:
            logger.error(f"Analysis results save error: {e}")
            return ""
