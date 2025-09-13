#!/usr/bin/env python3
"""
Training Script for Master AI Controller
Comprehensive training pipeline for reinforcement learning on real traffic data
"""

import os
import sys
import json
import time
import argparse
from datetime import datetime
from typing import Dict, List
import matplotlib.pyplot as plt
import numpy as np

from master_ai_controller import MasterAIController

class MasterAITrainer:
    """Comprehensive trainer for Master AI Controller"""
    
    def __init__(self, config_path: str = None):
        """Initialize trainer with configuration"""
        self.config = self._load_config(config_path)
        self.master_ai = MasterAIController(self.config)
        self.training_history = []
        self.evaluation_results = []
        
    def _load_config(self, config_path: str) -> Dict:
        """Load training configuration"""
        default_config = {
            'learning_rate': 0.001,
            'discount_factor': 0.95,
            'epsilon': 0.1,
            'epsilon_decay': 0.995,
            'epsilon_min': 0.01,
            'memory_size': 10000,
            'batch_size': 32,
            'target_update_frequency': 100,
            'training_frequency': 4,
            'video_path': "Traffic_videos/stock-footage-drone-shot-way-intersection.webm",
            'model_save_path': "models/master_ai_model.pkl",
            'experience_save_path': "data/experience_buffer.pkl",
            'training_episodes': 100,
            'evaluation_episodes': 10,
            'save_frequency': 10,
            'plot_frequency': 20
        }
        
        if config_path and os.path.exists(config_path):
            with open(config_path, 'r') as f:
                user_config = json.load(f)
                default_config.update(user_config)
        
        return default_config
    
    def train(self, episodes: int = None) -> Dict:
        """Train the Master AI Controller"""
        episodes = episodes or self.config['training_episodes']
        
        print(f"🚀 Starting Master AI Training")
        print(f"📊 Episodes: {episodes}")
        print(f"🎯 Learning Rate: {self.config['learning_rate']}")
        print(f"🧠 Epsilon: {self.config['epsilon']}")
        print("=" * 60)
        
        start_time = datetime.now()
        
        for episode in range(episodes):
            print(f"\n📚 Episode {episode + 1}/{episodes}")
            
            # Run training episode
            episode_data = self.master_ai.start_training_episode()
            self.training_history.append(episode_data)
            
            # Log progress
            if episode % 10 == 0:
                self._log_training_progress(episode)
            
            # Save model periodically
            if episode % self.config['save_frequency'] == 0:
                self.master_ai.save_model()
                self.master_ai.save_experience_buffer()
                print(f"💾 Model saved at episode {episode + 1}")
            
            # Generate plots periodically
            if episode % self.config['plot_frequency'] == 0 and episode > 0:
                self._generate_training_plots()
        
        # Final save
        self.master_ai.save_model()
        self.master_ai.save_experience_buffer()
        
        training_time = datetime.now() - start_time
        
        print(f"\n✅ Training Completed!")
        print(f"⏱️  Total Time: {training_time}")
        print(f"📊 Episodes: {episodes}")
        
        # Generate final report
        final_report = self._generate_final_report()
        return final_report
    
    def evaluate(self, test_videos: List[str] = None) -> Dict:
        """Evaluate trained model on test data"""
        print(f"\n🧪 Starting Model Evaluation")
        print("=" * 40)
        
        if test_videos is None:
            test_videos = [self.config['video_path']]
        
        evaluation_results = {
            'test_videos': test_videos,
            'evaluation_episodes': [],
            'overall_metrics': {}
        }
        
        for i, video_path in enumerate(test_videos):
            print(f"\n🎬 Testing Video {i + 1}/{len(test_videos)}: {video_path}")
            
            # Run evaluation episodes
            video_results = []
            for episode in range(self.config['evaluation_episodes']):
                print(f"  Episode {episode + 1}/{self.config['evaluation_episodes']}")
                
                # Temporarily change video path
                original_path = self.config['video_path']
                self.config['video_path'] = video_path
                
                # Run evaluation
                eval_data = self.master_ai.evaluate_model(video_path)
                video_results.append(eval_data)
                
                # Restore original path
                self.config['video_path'] = original_path
            
            # Calculate video-specific metrics
            video_metrics = self._calculate_video_metrics(video_results)
            evaluation_results['evaluation_episodes'].extend(video_results)
            evaluation_results[f'video_{i}_metrics'] = video_metrics
        
        # Calculate overall metrics
        evaluation_results['overall_metrics'] = self._calculate_overall_metrics(
            evaluation_results['evaluation_episodes']
        )
        
        self.evaluation_results = evaluation_results
        
        print(f"\n📊 Evaluation Results:")
        print(f"  Average Reward: {evaluation_results['overall_metrics']['average_reward']:.2f}")
        print(f"  Efficiency Score: {evaluation_results['overall_metrics']['efficiency_score']:.2f}")
        print(f"  Accuracy Score: {evaluation_results['overall_metrics']['accuracy_score']:.2f}")
        print(f"  Stability Score: {evaluation_results['overall_metrics']['stability_score']:.2f}")
        
        return evaluation_results
    
    def _log_training_progress(self, episode: int):
        """Log training progress"""
        status = self.master_ai.get_training_status()
        
        print(f"\n📈 Training Progress (Episode {episode + 1}):")
        print(f"  Average Reward: {status['average_reward']:.2f}")
        print(f"  Best Performance: {status['best_performance']:.2f}")
        print(f"  Epsilon: {status['epsilon']:.3f}")
        print(f"  Experience Buffer: {status['experience_buffer_size']}")
        print(f"  Convergence Rate: {status['convergence_rate']:.2f}")
    
    def _calculate_video_metrics(self, video_results: List[Dict]) -> Dict:
        """Calculate metrics for a specific video"""
        if not video_results:
            return {}
        
        rewards = [result['total_reward'] for result in video_results]
        efficiency_scores = [result['efficiency_score'] for result in video_results]
        accuracy_scores = [result['accuracy_score'] for result in video_results]
        stability_scores = [result['stability_score'] for result in video_results]
        
        return {
            'average_reward': np.mean(rewards),
            'std_reward': np.std(rewards),
            'average_efficiency': np.mean(efficiency_scores),
            'average_accuracy': np.mean(accuracy_scores),
            'average_stability': np.mean(stability_scores),
            'episodes': len(video_results)
        }
    
    def _calculate_overall_metrics(self, all_results: List[Dict]) -> Dict:
        """Calculate overall evaluation metrics"""
        if not all_results:
            return {}
        
        rewards = [result['total_reward'] for result in all_results]
        efficiency_scores = [result['efficiency_score'] for result in all_results]
        accuracy_scores = [result['accuracy_score'] for result in all_results]
        stability_scores = [result['stability_score'] for result in all_results]
        
        return {
            'average_reward': np.mean(rewards),
            'std_reward': np.std(rewards),
            'efficiency_score': np.mean(efficiency_scores),
            'accuracy_score': np.mean(accuracy_scores),
            'stability_score': np.mean(stability_scores),
            'total_episodes': len(all_results)
        }
    
    def _generate_training_plots(self):
        """Generate training progress plots"""
        if len(self.training_history) < 2:
            return
        
        # Extract data for plotting
        episodes = list(range(1, len(self.training_history) + 1))
        rewards = [episode['total_reward'] for episode in self.training_history]
        steps = [episode['steps'] for episode in self.training_history]
        
        # Create plots
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 10))
        
        # Reward over episodes
        ax1.plot(episodes, rewards, 'b-', alpha=0.7)
        ax1.set_title('Training Rewards Over Episodes')
        ax1.set_xlabel('Episode')
        ax1.set_ylabel('Total Reward')
        ax1.grid(True)
        
        # Moving average of rewards
        if len(rewards) > 10:
            window_size = min(20, len(rewards) // 5)
            moving_avg = np.convolve(rewards, np.ones(window_size)/window_size, mode='valid')
            ax2.plot(episodes[window_size-1:], moving_avg, 'r-', linewidth=2)
            ax2.set_title(f'Moving Average Rewards (Window: {window_size})')
            ax2.set_xlabel('Episode')
            ax2.set_ylabel('Average Reward')
            ax2.grid(True)
        
        # Steps per episode
        ax3.plot(episodes, steps, 'g-', alpha=0.7)
        ax3.set_title('Steps Per Episode')
        ax3.set_xlabel('Episode')
        ax3.set_ylabel('Steps')
        ax3.grid(True)
        
        # Reward distribution
        ax4.hist(rewards, bins=20, alpha=0.7, color='purple')
        ax4.set_title('Reward Distribution')
        ax4.set_xlabel('Total Reward')
        ax4.set_ylabel('Frequency')
        ax4.grid(True)
        
        plt.tight_layout()
        plt.savefig(f'plots/training_progress_{len(episodes)}.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"📊 Training plots saved to plots/training_progress_{len(episodes)}.png")
    
    def _generate_final_report(self) -> Dict:
        """Generate comprehensive final training report"""
        report = {
            'training_summary': {
                'total_episodes': len(self.training_history),
                'training_time': str(datetime.now()),
                'final_performance': self.master_ai.get_training_status()
            },
            'performance_analysis': self._analyze_performance(),
            'model_architecture': {
                'state_size': self.master_ai.q_network['state_size'],
                'action_size': self.master_ai.q_network['action_size'],
                'layers': self.master_ai.q_network['layers']
            },
            'configuration': self.config,
            'recommendations': self._generate_recommendations()
        }
        
        # Save report
        os.makedirs('reports', exist_ok=True)
        report_path = f'reports/training_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        print(f"📋 Final report saved to {report_path}")
        
        return report
    
    def _analyze_performance(self) -> Dict:
        """Analyze training performance"""
        if not self.training_history:
            return {}
        
        rewards = [episode['total_reward'] for episode in self.training_history]
        steps = [episode['steps'] for episode in self.training_history]
        
        # Calculate performance metrics
        analysis = {
            'reward_statistics': {
                'mean': np.mean(rewards),
                'std': np.std(rewards),
                'min': np.min(rewards),
                'max': np.max(rewards),
                'median': np.median(rewards)
            },
            'step_statistics': {
                'mean': np.mean(steps),
                'std': np.std(steps),
                'min': np.min(steps),
                'max': np.max(steps),
                'median': np.median(steps)
            },
            'learning_curve': {
                'improvement_rate': self._calculate_improvement_rate(rewards),
                'convergence_episode': self._find_convergence_episode(rewards),
                'stability_score': self._calculate_stability_score(rewards)
            }
        }
        
        return analysis
    
    def _calculate_improvement_rate(self, rewards: List[float]) -> float:
        """Calculate learning improvement rate"""
        if len(rewards) < 10:
            return 0
        
        # Compare first 25% vs last 25%
        quarter = len(rewards) // 4
        early_avg = np.mean(rewards[:quarter])
        late_avg = np.mean(rewards[-quarter:])
        
        if early_avg == 0:
            return 0
        
        return ((late_avg - early_avg) / early_avg) * 100
    
    def _find_convergence_episode(self, rewards: List[float]) -> int:
        """Find episode where learning converged"""
        if len(rewards) < 20:
            return len(rewards)
        
        # Look for stable performance (low variance in recent episodes)
        window_size = 20
        for i in range(window_size, len(rewards)):
            recent_rewards = rewards[i-window_size:i]
            if np.std(recent_rewards) < np.mean(recent_rewards) * 0.1:  # 10% coefficient of variation
                return i
        
        return len(rewards)
    
    def _calculate_stability_score(self, rewards: List[float]) -> float:
        """Calculate stability score (0-100)"""
        if len(rewards) < 10:
            return 0
        
        # Calculate coefficient of variation
        mean_reward = np.mean(rewards)
        std_reward = np.std(rewards)
        
        if mean_reward == 0:
            return 0
        
        cv = std_reward / mean_reward
        stability = max(0, 100 - (cv * 100))
        
        return stability
    
    def _generate_recommendations(self) -> List[str]:
        """Generate training recommendations"""
        recommendations = []
        
        status = self.master_ai.get_training_status()
        
        if status['average_reward'] < 50:
            recommendations.append("Consider increasing learning rate or training for more episodes")
        
        if status['convergence_rate'] > 10:
            recommendations.append("Model is not converging well, consider adjusting hyperparameters")
        
        if status['experience_buffer_size'] < 1000:
            recommendations.append("Collect more experience data for better training")
        
        if status['epsilon'] > 0.1:
            recommendations.append("Consider reducing exploration rate for better exploitation")
        
        if status['best_performance'] < 100:
            recommendations.append("Consider increasing model complexity or training duration")
        
        return recommendations
    
    def run_complete_training_pipeline(self) -> Dict:
        """Run complete training and evaluation pipeline"""
        print("🚀 Starting Complete Master AI Training Pipeline")
        print("=" * 60)
        
        # Create necessary directories
        os.makedirs('models', exist_ok=True)
        os.makedirs('data', exist_ok=True)
        os.makedirs('plots', exist_ok=True)
        os.makedirs('reports', exist_ok=True)
        
        # Phase 1: Training
        print("\n🎯 Phase 1: Training")
        training_results = self.train()
        
        # Phase 2: Evaluation
        print("\n🧪 Phase 2: Evaluation")
        evaluation_results = self.evaluate()
        
        # Phase 3: Final Report
        print("\n📋 Phase 3: Final Report")
        final_report = {
            'training_results': training_results,
            'evaluation_results': evaluation_results,
            'pipeline_completed': True,
            'completion_time': datetime.now().isoformat()
        }
        
        print("\n✅ Complete Training Pipeline Finished!")
        print(f"📊 Final Performance: {evaluation_results['overall_metrics']['average_reward']:.2f}")
        print(f"🎯 Model saved to: {self.config['model_save_path']}")
        
        return final_report

def main():
    """Main function for training script"""
    parser = argparse.ArgumentParser(description='Train Master AI Controller')
    parser.add_argument('--config', type=str, help='Path to configuration file')
    parser.add_argument('--episodes', type=int, help='Number of training episodes')
    parser.add_argument('--evaluate', action='store_true', help='Run evaluation after training')
    parser.add_argument('--complete', action='store_true', help='Run complete training pipeline')
    
    args = parser.parse_args()
    
    # Initialize trainer
    trainer = MasterAITrainer(args.config)
    
    if args.complete:
        # Run complete pipeline
        results = trainer.run_complete_training_pipeline()
    else:
        # Run training
        episodes = args.episodes or trainer.config['training_episodes']
        training_results = trainer.train(episodes)
        
        if args.evaluate:
            # Run evaluation
            evaluation_results = trainer.evaluate()
            results = {
                'training_results': training_results,
                'evaluation_results': evaluation_results
            }
        else:
            results = training_results
    
    print("\n🎉 Training completed successfully!")
    return results

if __name__ == "__main__":
    main()

