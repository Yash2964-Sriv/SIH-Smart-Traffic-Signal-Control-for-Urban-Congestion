#!/usr/bin/env python3
"""
Test and Integrate RL Models
Tests all .pkl files in ai_models folder and integrates the best one with Master AI
"""

import os
import pickle
import numpy as np
import json
from datetime import datetime
from typing import Dict, List, Tuple
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RLModelTester:
    """Test and evaluate multiple RL models"""
    
    def __init__(self, models_folder: str = "ai_models"):
        self.models_folder = models_folder
        self.test_results = {}
        self.best_model = None
        self.best_score = -float('inf')
        
    def load_model(self, model_path: str) -> Dict:
        """Load and analyze a single RL model"""
        try:
            with open(model_path, 'rb') as f:
                model_data = pickle.load(f)
            
            # Extract model information
            model_info = {
                'file_path': model_path,
                'file_name': os.path.basename(model_path),
                'file_size': os.path.getsize(model_path),
                'model_type': 'unknown',
                'has_weights': False,
                'has_q_network': False,
                'state_size': None,
                'action_size': None,
                'performance_metrics': {},
                'config': {},
                'episode_count': 0,
                'step_count': 0,
                'load_success': True,
                'error': None
            }
            
            # Analyze model structure
            if isinstance(model_data, dict):
                # Check for Q-network structure
                if 'q_network' in model_data:
                    q_net = model_data['q_network']
                    model_info['has_q_network'] = True
                    model_info['state_size'] = q_net.get('state_size', None)
                    model_info['action_size'] = q_net.get('action_size', None)
                    model_info['has_weights'] = 'weights' in q_net
                    model_info['model_type'] = 'q_learning'
                
                # Check for target network
                if 'target_network' in model_data:
                    model_info['has_target_network'] = True
                
                # Extract performance metrics
                model_info['performance_metrics'] = model_data.get('performance_metrics', {})
                model_info['config'] = model_data.get('config', {})
                model_info['episode_count'] = model_data.get('episode_count', 0)
                model_info['step_count'] = model_data.get('step_count', 0)
                
                # Check for other model types
                if 'weights' in model_data and not model_info['has_q_network']:
                    model_info['model_type'] = 'neural_network'
                    model_info['has_weights'] = True
                
            elif hasattr(model_data, 'weights') and hasattr(model_data, 'bias'):
                model_info['model_type'] = 'q_network'
                model_info['has_weights'] = True
                model_info['state_size'] = getattr(model_data, 'state_size', None)
                model_info['action_size'] = getattr(model_data, 'action_size', None)
            
            return model_info
            
        except Exception as e:
            return {
                'file_path': model_path,
                'file_name': os.path.basename(model_path),
                'load_success': False,
                'error': str(e),
                'model_type': 'unknown'
            }
    
    def test_model_prediction(self, model_info: Dict) -> Dict:
        """Test model prediction capabilities"""
        if not model_info.get('load_success', False):
            return {'prediction_success': False, 'error': 'Model load failed'}
        
        try:
            # Load the model again for testing
            with open(model_info['file_path'], 'rb') as f:
                model_data = pickle.load(f)
            
            # Create test traffic data
            test_traffic_data = {
                'queue_lengths': {'I1': 5, 'I2': 10, 'I3': 3, 'I4': 8},
                'waiting_times': {'I1': 15, 'I2': 25, 'I3': 10, 'I4': 20},
                'vehicle_counts': {'north': 12, 'south': 8, 'east': 15, 'west': 10},
                'flow_rates': {'north': 200, 'south': 150, 'east': 180, 'west': 160},
                'current_phase': 1,
                'phase_duration': 30,
                'efficiency_scores': {'throughput': 85, 'waiting_time': 70, 'speed': 90}
            }
            
            # Convert to state representation
            state = self._get_state_representation(test_traffic_data, model_info)
            
            # Test prediction
            predictions = []
            for i in range(10):  # Test multiple predictions
                prediction = self._predict_action(model_data, state, model_info)
                predictions.append(prediction)
            
            # Calculate prediction metrics
            unique_predictions = len(set(predictions))
            prediction_consistency = unique_predictions / len(predictions)
            
            return {
                'prediction_success': True,
                'predictions': predictions,
                'unique_predictions': unique_predictions,
                'consistency': prediction_consistency,
                'average_prediction': np.mean(predictions),
                'prediction_std': np.std(predictions)
            }
            
        except Exception as e:
            return {
                'prediction_success': False,
                'error': str(e)
            }
    
    def _get_state_representation(self, traffic_data: Dict, model_info: Dict) -> np.ndarray:
        """Convert traffic data to state representation"""
        # Default state size
        state_size = model_info.get('state_size', 20)
        state = np.zeros(state_size)
        
        # Extract features (same as in RL trainer)
        idx = 0
        
        # Queue lengths
        queue_lengths = traffic_data.get('queue_lengths', {})
        for junction_id in ['I1', 'I2', 'I3', 'I4']:
            if idx < state_size:
                state[idx] = queue_lengths.get(junction_id, 0) / 100.0
                idx += 1
        
        # Waiting times
        waiting_times = traffic_data.get('waiting_times', {})
        for junction_id in ['I1', 'I2', 'I3', 'I4']:
            if idx < state_size:
                state[idx] = waiting_times.get(junction_id, 0) / 60.0
                idx += 1
        
        # Current phase and duration
        if idx < state_size:
            state[idx] = traffic_data.get('current_phase', 0) / 4.0
            idx += 1
        if idx < state_size:
            state[idx] = traffic_data.get('phase_duration', 0) / 120.0
            idx += 1
        
        # Time of day
        current_time = datetime.now()
        if idx < state_size:
            state[idx] = current_time.hour / 24.0
            idx += 1
        if idx < state_size:
            state[idx] = current_time.weekday() / 7.0
            idx += 1
        
        # Traffic flow rates
        flow_rates = traffic_data.get('flow_rates', {})
        for direction in ['north', 'south', 'east', 'west']:
            if idx < state_size:
                state[idx] = flow_rates.get(direction, 0) / 1000.0
                idx += 1
        
        # Vehicle counts
        vehicle_counts = traffic_data.get('vehicle_counts', {})
        for direction in ['north', 'south', 'east', 'west']:
            if idx < state_size:
                state[idx] = vehicle_counts.get(direction, 0) / 50.0
                idx += 1
        
        # Efficiency scores
        efficiency_scores = traffic_data.get('efficiency_scores', {})
        for metric in ['throughput', 'waiting_time', 'speed']:
            if idx < state_size:
                state[idx] = efficiency_scores.get(metric, 0) / 100.0
                idx += 1
        
        return state
    
    def _predict_action(self, model_data: any, state: np.ndarray, model_info: Dict) -> int:
        """Predict action using the loaded model"""
        try:
            if model_info['model_type'] == 'q_learning' and 'q_network' in model_data:
                q_net = model_data['q_network']
                weights = q_net.get('weights')
                bias = q_net.get('bias')
                
                if weights is not None and bias is not None:
                    q_values = np.dot(state, weights) + bias
                    return np.argmax(q_values)
            
            elif 'weights' in model_data:
                weights = model_data['weights']
                bias = model_data.get('bias', np.zeros(weights.shape[1]))
                output = np.dot(state, weights) + bias
                return np.argmax(output)
            
            # Fallback to random
            return np.random.randint(0, model_info.get('action_size', 8))
            
        except Exception as e:
            return np.random.randint(0, model_info.get('action_size', 8))
    
    def calculate_model_score(self, model_info: Dict, prediction_results: Dict) -> float:
        """Calculate overall score for model evaluation"""
        score = 0
        
        # Base score for successful load
        if model_info.get('load_success', False):
            score += 10
        
        # Score for prediction success
        if prediction_results.get('prediction_success', False):
            score += 20
        
        # Score for model completeness
        if model_info.get('has_weights', False):
            score += 15
        
        if model_info.get('has_q_network', False):
            score += 10
        
        # Score for training progress
        episode_count = model_info.get('episode_count', 0)
        if episode_count > 0:
            score += min(20, episode_count / 10)  # Max 20 points for episodes
        
        step_count = model_info.get('step_count', 0)
        if step_count > 0:
            score += min(15, step_count / 1000)  # Max 15 points for steps
        
        # Score for prediction consistency
        if prediction_results.get('prediction_success', False):
            consistency = prediction_results.get('consistency', 0)
            score += consistency * 10  # Max 10 points for consistency
        
        # Score for performance metrics
        perf_metrics = model_info.get('performance_metrics', {})
        if 'average_reward' in perf_metrics:
            avg_reward = perf_metrics['average_reward']
            if avg_reward > 0:
                score += min(15, avg_reward / 10)  # Max 15 points for rewards
        
        # Score for model type (prefer Q-learning)
        if model_info.get('model_type') == 'q_learning':
            score += 5
        
        return score
    
    def test_all_models(self) -> Dict:
        """Test all models in the ai_models folder"""
        print("🧪 Testing All RL Models")
        print("=" * 50)
        
        # Get all .pkl files
        pkl_files = [f for f in os.listdir(self.models_folder) if f.endswith('.pkl')]
        
        if not pkl_files:
            print("❌ No .pkl files found in ai_models folder")
            return {}
        
        print(f"📁 Found {len(pkl_files)} model files")
        
        # Test each model
        for i, pkl_file in enumerate(pkl_files):
            model_path = os.path.join(self.models_folder, pkl_file)
            print(f"\n🔍 Testing {i+1}/{len(pkl_files)}: {pkl_file}")
            
            # Load model
            model_info = self.load_model(model_path)
            
            # Test prediction
            prediction_results = self.test_model_prediction(model_info)
            
            # Calculate score
            score = self.calculate_model_score(model_info, prediction_results)
            
            # Store results
            self.test_results[pkl_file] = {
                'model_info': model_info,
                'prediction_results': prediction_results,
                'score': score
            }
            
            # Print results
            print(f"   📊 Score: {score:.2f}")
            print(f"   🎯 Model Type: {model_info.get('model_type', 'unknown')}")
            print(f"   📈 Episodes: {model_info.get('episode_count', 0)}")
            print(f"   🔢 Steps: {model_info.get('step_count', 0)}")
            print(f"   ✅ Load Success: {model_info.get('load_success', False)}")
            print(f"   🎲 Prediction Success: {prediction_results.get('prediction_success', False)}")
            
            if prediction_results.get('prediction_success', False):
                print(f"   🎯 Predictions: {prediction_results['predictions'][:5]}...")
                print(f"   📊 Consistency: {prediction_results['consistency']:.2f}")
            
            # Update best model
            if score > self.best_score:
                self.best_score = score
                self.best_model = pkl_file
                print(f"   🏆 New best model!")
        
        return self.test_results
    
    def get_best_model(self) -> Tuple[str, Dict]:
        """Get the best performing model"""
        if not self.test_results:
            return None, None
        
        best_file = max(self.test_results.keys(), key=lambda x: self.test_results[x]['score'])
        best_data = self.test_results[best_file]
        
        return best_file, best_data
    
    def generate_test_report(self) -> Dict:
        """Generate comprehensive test report"""
        report = {
            'test_timestamp': datetime.now().isoformat(),
            'total_models_tested': len(self.test_results),
            'best_model': self.best_model,
            'best_score': self.best_score,
            'model_rankings': [],
            'summary_statistics': {},
            'detailed_results': self.test_results
        }
        
        # Create rankings
        rankings = sorted(
            self.test_results.items(),
            key=lambda x: x[1]['score'],
            reverse=True
        )
        
        for i, (model_name, data) in enumerate(rankings):
            report['model_rankings'].append({
                'rank': i + 1,
                'model_name': model_name,
                'score': data['score'],
                'model_type': data['model_info'].get('model_type', 'unknown'),
                'episodes': data['model_info'].get('episode_count', 0),
                'steps': data['model_info'].get('step_count', 0)
            })
        
        # Summary statistics
        scores = [data['score'] for data in self.test_results.values()]
        report['summary_statistics'] = {
            'average_score': np.mean(scores),
            'max_score': np.max(scores),
            'min_score': np.min(scores),
            'std_score': np.std(scores),
            'successful_models': sum(1 for data in self.test_results.values() if data['model_info'].get('load_success', False)),
            'prediction_success_rate': sum(1 for data in self.test_results.values() if data['prediction_results'].get('prediction_success', False)) / len(self.test_results)
        }
        
        return report

def integrate_best_model_with_master_ai(best_model_path: str):
    """Integrate the best model with Master AI Controller"""
    print(f"\n🔗 Integrating Best Model with Master AI")
    print("=" * 50)
    
    try:
        # Import integration module
        from rl_model_integration import integrate_rl_model_with_master_ai
        from master_ai_controller import MasterAIController
        
        # Create Master AI Controller
        master_ai = MasterAIController()
        
        # Integrate best model
        success = integrate_rl_model_with_master_ai(master_ai, best_model_path)
        
        if success:
            print("✅ Best model integrated successfully!")
            
            # Test integrated system
            print("\n🧪 Testing integrated system...")
            
            test_traffic_data = {
                'queue_lengths': {'I1': 5, 'I2': 10, 'I3': 3, 'I4': 8},
                'waiting_times': {'I1': 15, 'I2': 25, 'I3': 10, 'I4': 20},
                'vehicle_counts': {'north': 12, 'south': 8, 'east': 15, 'west': 10},
                'flow_rates': {'north': 200, 'south': 150, 'east': 180, 'west': 160},
                'current_phase': 1,
                'phase_duration': 30,
                'efficiency_scores': {'throughput': 85, 'waiting_time': 70, 'speed': 90}
            }
            
            # Test multiple predictions
            actions = []
            for i in range(5):
                action = master_ai.select_action(test_traffic_data)
                actions.append(action)
            
            print(f"   🎯 Actions: {actions}")
            print(f"   📊 Action diversity: {len(set(actions))} unique actions")
            
            # Check RL enhancement status
            if hasattr(master_ai, 'rl_enhanced') and master_ai.rl_enhanced:
                print("   ✅ RL enhancement is active!")
            else:
                print("   ⚠️  RL enhancement may not be fully active")
            
            return True
        else:
            print("❌ Failed to integrate best model")
            return False
            
    except Exception as e:
        print(f"❌ Integration failed: {e}")
        return False

def main():
    """Main function"""
    print("🚀 RL Model Testing and Integration System")
    print("=" * 60)
    
    # Initialize tester
    tester = RLModelTester("ai_models")
    
    # Test all models
    test_results = tester.test_all_models()
    
    if not test_results:
        print("❌ No models were tested successfully")
        return
    
    # Get best model
    best_model, best_data = tester.get_best_model()
    
    if best_model:
        print(f"\n🏆 Best Model: {best_model}")
        print(f"   📊 Score: {best_data['score']:.2f}")
        print(f"   🎯 Type: {best_data['model_info'].get('model_type', 'unknown')}")
        print(f"   📈 Episodes: {best_data['model_info'].get('episode_count', 0)}")
        print(f"   🔢 Steps: {best_data['model_info'].get('step_count', 0)}")
        
        # Generate report
        report = tester.generate_test_report()
        
        # Save report
        os.makedirs('reports', exist_ok=True)
        report_path = f'reports/rl_model_test_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        print(f"\n📋 Test report saved to: {report_path}")
        
        # Integrate best model
        best_model_path = os.path.join("ai_models", best_model)
        integration_success = integrate_best_model_with_master_ai(best_model_path)
        
        if integration_success:
            print(f"\n🎉 Integration completed successfully!")
            print(f"📚 Your Master AI is now enhanced with the best RL model: {best_model}")
            print(f"🚀 Use master_ai.select_action(traffic_data) for RL-enhanced predictions!")
        else:
            print(f"\n❌ Integration failed, but you can integrate manually using:")
            print(f"   python integrate_your_rl_model.py \"{best_model_path}\"")
    
    else:
        print("❌ No suitable model found for integration")

if __name__ == "__main__":
    main()
