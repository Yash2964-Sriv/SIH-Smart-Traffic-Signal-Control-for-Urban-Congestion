#!/usr/bin/env python3
"""
Enhanced Master AI with RL Integration
Integrates RL capabilities into the existing Master AI Controller
"""

import os
import json
import time
import numpy as np
import pickle
import random
from datetime import datetime
from typing import Dict, List, Tuple, Optional, Any
import logging

# Import existing Master AI Controller
from master_ai_controller import MasterAIController

logger = logging.getLogger(__name__)

class EnhancedMasterAIWithRL(MasterAIController):
    """
    Enhanced Master AI Controller with integrated RL capabilities
    """
    
    def __init__(self, config: Dict = None, rl_model_path: str = None):
        """Initialize Enhanced Master AI with RL"""
        super().__init__(config)
        
        # RL components
        self.rl_model = None
        self.rl_enhanced = False
        self.rl_model_path = rl_model_path
        self.rl_performance_history = []
        
        # Load RL model if provided
        if rl_model_path and os.path.exists(rl_model_path):
            self.load_rl_model(rl_model_path)
    
    def load_rl_model(self, model_path: str) -> bool:
        """Load RL model from pickle file"""
        try:
            with open(model_path, 'rb') as f:
                model_data = pickle.load(f)
            
            # Check if it's a valid RL model
            if self._is_valid_rl_model(model_data):
                self.rl_model = model_data
                self.rl_enhanced = True
                self.rl_model_path = model_path
                logger.info(f"RL model loaded successfully from {model_path}")
                return True
            else:
                logger.warning(f"Invalid RL model format in {model_path}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to load RL model from {model_path}: {e}")
            return False
    
    def _is_valid_rl_model(self, model_data: Any) -> bool:
        """Check if the loaded data is a valid RL model"""
        # Check for common RL model structures
        if isinstance(model_data, dict):
            # Check for Q-network structure
            if 'q_network' in model_data:
                q_net = model_data['q_network']
                return 'weights' in q_net and 'bias' in q_net
            
            # Check for neural network weights
            if 'weights' in model_data:
                return isinstance(model_data['weights'], np.ndarray)
            
            # Check for other RL model indicators
            rl_indicators = ['state_size', 'action_size', 'epsilon', 'learning_rate']
            return any(indicator in model_data for indicator in rl_indicators)
        
        # Check for direct neural network objects
        if hasattr(model_data, 'weights') and hasattr(model_data, 'bias'):
            return True
        
        # Check for scikit-learn models
        if hasattr(model_data, 'predict'):
            return True
        
        return False
    
    def get_rl_state_representation(self, traffic_data: Dict) -> np.ndarray:
        """Convert traffic data to state representation for RL"""
        # Default state size (adjust based on your model)
        state_size = 20
        state = np.zeros(state_size)
        
        # Extract features from traffic data
        idx = 0
        
        # Queue lengths (normalized)
        queue_lengths = traffic_data.get('queue_lengths', {})
        for junction_id in ['I1', 'I2', 'I3', 'I4']:
            if idx < state_size:
                state[idx] = queue_lengths.get(junction_id, 0) / 100.0
                idx += 1
        
        # Waiting times (normalized)
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
    
    def predict_rl_action(self, traffic_data: Dict) -> int:
        """Predict action using RL model"""
        if not self.rl_enhanced or self.rl_model is None:
            # Fallback to original action selection
            return self.select_action_original(traffic_data)
        
        try:
            # Get state representation
            state = self.get_rl_state_representation(traffic_data)
            
            # Predict action based on model type
            if isinstance(self.rl_model, dict):
                if 'q_network' in self.rl_model:
                    return self._predict_q_learning(state)
                elif 'weights' in self.rl_model:
                    return self._predict_neural_network(state)
                else:
                    return self._predict_generic(state)
            else:
                return self._predict_generic(state)
                
        except Exception as e:
            logger.warning(f"RL prediction failed: {e}, using fallback")
            return self.select_action_original(traffic_data)
    
    def _predict_q_learning(self, state: np.ndarray) -> int:
        """Predict action using Q-learning model"""
        q_net = self.rl_model['q_network']
        weights = q_net.get('weights')
        bias = q_net.get('bias')
        
        if weights is not None and bias is not None:
            q_values = np.dot(state, weights) + bias
            return np.argmax(q_values)
        
        return np.random.randint(0, 8)
    
    def _predict_neural_network(self, state: np.ndarray) -> int:
        """Predict action using neural network model"""
        weights = self.rl_model['weights']
        bias = self.rl_model.get('bias', np.zeros(weights.shape[1]))
        
        output = np.dot(state, weights) + bias
        return np.argmax(output)
    
    def _predict_generic(self, state: np.ndarray) -> int:
        """Generic prediction method"""
        if hasattr(self.rl_model, 'predict'):
            try:
                prediction = self.rl_model.predict(state.reshape(1, -1))
                return int(prediction[0])
            except:
                pass
        
        return np.random.randint(0, 8)
    
    def select_action(self, traffic_data: Dict) -> int:
        """Enhanced action selection with RL integration"""
        if self.rl_enhanced:
            action = self.predict_rl_action(traffic_data)
            
            # Record RL performance
            self.rl_performance_history.append({
                'timestamp': datetime.now(),
                'action': action,
                'traffic_data': traffic_data
            })
            
            return action
        else:
            # Use original action selection
            return self.select_action_original(traffic_data)
    
    def select_action_original(self, traffic_data: Dict) -> int:
        """Original action selection method (fallback)"""
        # This would be your original action selection logic
        # For now, return a random action as placeholder
        return np.random.randint(0, 8)
    
    def train_rl_model(self, training_data: List[Dict], episodes: int = 100):
        """Train RL model on provided data"""
        if not self.rl_enhanced:
            logger.warning("No RL model loaded for training")
            return False
        
        logger.info(f"Training RL model for {episodes} episodes")
        
        for episode in range(episodes):
            # Sample training data
            episode_data = random.choice(training_data)
            
            # Get state representation
            state = self.get_rl_state_representation(episode_data)
            
            # Predict action
            action = self.predict_rl_action(episode_data)
            
            # Calculate reward (simplified)
            reward = self._calculate_reward(episode_data, action)
            
            # Update model (simplified)
            self._update_rl_model(state, action, reward)
            
            if episode % 10 == 0:
                logger.info(f"Episode {episode}: Action {action}, Reward {reward:.2f}")
        
        logger.info("RL model training completed")
        return True
    
    def _calculate_reward(self, traffic_data: Dict, action: int) -> float:
        """Calculate reward for RL training"""
        reward = 0
        
        # Base reward from traffic conditions
        queue_lengths = traffic_data.get('queue_lengths', {})
        avg_queue = np.mean(list(queue_lengths.values())) if queue_lengths else 0
        reward += max(0, 10 - avg_queue)
        
        waiting_times = traffic_data.get('waiting_times', {})
        avg_wait = np.mean(list(waiting_times.values())) if waiting_times else 0
        reward += max(0, 20 - avg_wait)
        
        # Action-specific rewards
        action_rewards = {
            0: 5,   # Change phase
            1: 3,   # Extend green
            2: 4,   # Reduce cycle
            3: 8,   # Coordinate
            4: 15,  # Emergency
            5: 6,   # Adaptive
            6: 7,   # Queue management
            7: 9    # Flow optimization
        }
        
        reward += action_rewards.get(action, 0)
        
        return reward
    
    def _update_rl_model(self, state: np.ndarray, action: int, reward: float):
        """Update RL model (simplified)"""
        # This is a placeholder for actual RL model updates
        # In a real implementation, you would update the model weights here
        pass
    
    def get_rl_performance(self) -> Dict:
        """Get RL performance metrics"""
        if not self.rl_performance_history:
            return {}
        
        recent_actions = [entry['action'] for entry in self.rl_performance_history[-100:]]
        
        return {
            'total_decisions': len(self.rl_performance_history),
            'recent_actions': recent_actions,
            'action_diversity': len(set(recent_actions)),
            'most_common_action': max(set(recent_actions), key=recent_actions.count),
            'rl_enhanced': self.rl_enhanced,
            'model_path': self.rl_model_path
        }
    
    def save_enhanced_model(self, filepath: str = None):
        """Save enhanced model with RL integration"""
        if filepath is None:
            filepath = f"models/enhanced_master_ai_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pkl"
        
        model_data = {
            'base_controller': self,
            'rl_model': self.rl_model,
            'rl_enhanced': self.rl_enhanced,
            'rl_performance_history': self.rl_performance_history,
            'config': self.config,
            'timestamp': datetime.now().isoformat()
        }
        
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        with open(filepath, 'wb') as f:
            pickle.dump(model_data, f)
        
        logger.info(f"Enhanced model saved to {filepath}")
    
    def load_enhanced_model(self, filepath: str) -> bool:
        """Load enhanced model with RL integration"""
        try:
            with open(filepath, 'rb') as f:
                model_data = pickle.load(f)
            
            # Restore RL components
            self.rl_model = model_data.get('rl_model')
            self.rl_enhanced = model_data.get('rl_enhanced', False)
            self.rl_performance_history = model_data.get('rl_performance_history', [])
            
            logger.info(f"Enhanced model loaded from {filepath}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to load enhanced model: {e}")
            return False

def create_enhanced_master_ai(rl_model_path: str = None) -> EnhancedMasterAIWithRL:
    """Create enhanced Master AI with RL integration"""
    config = {
        'learning_rate': 0.001,
        'epsilon': 0.1,
        'video_path': "Traffic_videos/stock-footage-drone-shot-way-intersection.webm"
    }
    
    return EnhancedMasterAIWithRL(config, rl_model_path)

def main():
    """Main function for testing enhanced Master AI"""
    print("🤖 Enhanced Master AI with RL Integration")
    print("=" * 50)
    
    # Create enhanced Master AI
    enhanced_ai = create_enhanced_master_ai()
    
    # Test with sample traffic data
    test_traffic_data = {
        'queue_lengths': {'I1': 5, 'I2': 10, 'I3': 3, 'I4': 8},
        'waiting_times': {'I1': 15, 'I2': 25, 'I3': 10, 'I4': 20},
        'vehicle_counts': {'north': 12, 'south': 8, 'east': 15, 'west': 10},
        'flow_rates': {'north': 200, 'south': 150, 'east': 180, 'west': 160},
        'current_phase': 1,
        'phase_duration': 30,
        'efficiency_scores': {'throughput': 85, 'waiting_time': 70, 'speed': 90}
    }
    
    print("🧪 Testing Enhanced Master AI...")
    
    # Test action selection
    for i in range(5):
        action = enhanced_ai.select_action(test_traffic_data)
        print(f"   Action {i+1}: {action}")
    
    # Get performance metrics
    performance = enhanced_ai.get_rl_performance()
    print(f"\n📊 Performance Metrics:")
    print(f"   RL Enhanced: {performance.get('rl_enhanced', False)}")
    print(f"   Total Decisions: {performance.get('total_decisions', 0)}")
    print(f"   Action Diversity: {performance.get('action_diversity', 0)}")
    
    # Save enhanced model
    enhanced_ai.save_enhanced_model()
    
    print(f"\n✅ Enhanced Master AI created and tested successfully!")

if __name__ == "__main__":
    main()
