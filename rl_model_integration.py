#!/usr/bin/env python3
"""
RL Model Integration Module
Integrates pre-trained RL models (.pkl files) into Master AI Controller
"""

import os
import pickle
import numpy as np
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class RLModelIntegrator:
    """
    Integrates pre-trained RL models into Master AI Controller
    """
    
    def __init__(self, model_path: str = None):
        """Initialize RL Model Integrator"""
        self.model_path = model_path
        self.trained_model = None
        self.model_info = None
        self.is_loaded = False
        
        if model_path and os.path.exists(model_path):
            self.load_model(model_path)
    
    def load_model(self, model_path: str) -> bool:
        """Load pre-trained RL model from pickle file"""
        try:
            with open(model_path, 'rb') as f:
                self.trained_model = pickle.load(f)
            
            # Extract model information
            self.model_info = self._extract_model_info(self.trained_model)
            self.is_loaded = True
            self.model_path = model_path
            
            logger.info(f"Successfully loaded RL model from {model_path}")
            logger.info(f"Model info: {self.model_info}")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to load RL model from {model_path}: {e}")
            return False
    
    def _extract_model_info(self, model_data: Any) -> Dict:
        """Extract model information from loaded data"""
        info = {
            'model_type': 'unknown',
            'state_size': None,
            'action_size': None,
            'has_weights': False,
            'has_q_network': False,
            'has_target_network': False,
            'performance_metrics': {},
            'config': {},
            'episode_count': 0,
            'step_count': 0
        }
        
        try:
            # Check if it's a dictionary (common format)
            if isinstance(model_data, dict):
                # Check for Q-network structure
                if 'q_network' in model_data:
                    q_net = model_data['q_network']
                    info['has_q_network'] = True
                    info['state_size'] = q_net.get('state_size', None)
                    info['action_size'] = q_net.get('action_size', None)
                    info['has_weights'] = 'weights' in q_net
                
                # Check for target network
                if 'target_network' in model_data:
                    info['has_target_network'] = True
                
                # Extract other information
                info['performance_metrics'] = model_data.get('performance_metrics', {})
                info['config'] = model_data.get('config', {})
                info['episode_count'] = model_data.get('episode_count', 0)
                info['step_count'] = model_data.get('step_count', 0)
                
                # Determine model type
                if info['has_q_network']:
                    info['model_type'] = 'q_learning'
                elif 'weights' in model_data:
                    info['model_type'] = 'neural_network'
                else:
                    info['model_type'] = 'custom'
            
            # Check if it's a direct Q-network
            elif hasattr(model_data, 'weights') and hasattr(model_data, 'bias'):
                info['model_type'] = 'q_network'
                info['has_weights'] = True
                info['state_size'] = getattr(model_data, 'state_size', None)
                info['action_size'] = getattr(model_data, 'action_size', None)
            
            # Check if it's a scikit-learn model
            elif hasattr(model_data, 'predict'):
                info['model_type'] = 'sklearn'
                info['has_weights'] = True
            
            # Check if it's a PyTorch model
            elif hasattr(model_data, 'state_dict'):
                info['model_type'] = 'pytorch'
                info['has_weights'] = True
            
            # Check if it's a TensorFlow model
            elif hasattr(model_data, 'predict'):
                info['model_type'] = 'tensorflow'
                info['has_weights'] = True
            
        except Exception as e:
            logger.warning(f"Could not fully extract model info: {e}")
        
        return info
    
    def get_state_representation(self, traffic_data: Dict) -> np.ndarray:
        """Convert traffic data to state representation compatible with loaded model"""
        if not self.is_loaded:
            raise ValueError("No model loaded. Please load a model first.")
        
        # Default state size (adjust based on your model)
        state_size = self.model_info.get('state_size', 20)
        state = np.zeros(state_size)
        
        # Extract features from traffic data (same as in RL trainer)
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
        from datetime import datetime
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
    
    def predict_action(self, traffic_data: Dict) -> int:
        """Predict best action using loaded RL model"""
        if not self.is_loaded:
            raise ValueError("No model loaded. Please load a model first.")
        
        # Get state representation
        state = self.get_state_representation(traffic_data)
        
        # Predict action based on model type
        if self.model_info['model_type'] == 'q_learning':
            return self._predict_q_learning(state)
        elif self.model_info['model_type'] == 'neural_network':
            return self._predict_neural_network(state)
        elif self.model_info['model_type'] == 'sklearn':
            return self._predict_sklearn(state)
        elif self.model_info['model_type'] == 'pytorch':
            return self._predict_pytorch(state)
        elif self.model_info['model_type'] == 'tensorflow':
            return self._predict_tensorflow(state)
        else:
            return self._predict_generic(state)
    
    def _predict_q_learning(self, state: np.ndarray) -> int:
        """Predict action using Q-learning model"""
        if 'q_network' in self.trained_model:
            q_net = self.trained_model['q_network']
            weights = q_net.get('weights')
            bias = q_net.get('bias')
            
            if weights is not None and bias is not None:
                # Calculate Q-values
                q_values = np.dot(state, weights) + bias
                return np.argmax(q_values)
        
        # Fallback to random action
        return np.random.randint(0, self.model_info.get('action_size', 8))
    
    def _predict_neural_network(self, state: np.ndarray) -> int:
        """Predict action using neural network model"""
        # Try to find weights and bias
        if 'weights' in self.trained_model:
            weights = self.trained_model['weights']
            bias = self.trained_model.get('bias', np.zeros(weights.shape[1]))
            
            # Calculate output
            output = np.dot(state, weights) + bias
            return np.argmax(output)
        
        # Fallback
        return np.random.randint(0, self.model_info.get('action_size', 8))
    
    def _predict_sklearn(self, state: np.ndarray) -> int:
        """Predict action using scikit-learn model"""
        try:
            prediction = self.trained_model.predict(state.reshape(1, -1))
            return int(prediction[0])
        except:
            return np.random.randint(0, self.model_info.get('action_size', 8))
    
    def _predict_pytorch(self, state: np.ndarray) -> int:
        """Predict action using PyTorch model"""
        try:
            import torch
            state_tensor = torch.FloatTensor(state).unsqueeze(0)
            with torch.no_grad():
                output = self.trained_model(state_tensor)
                return int(torch.argmax(output).item())
        except:
            return np.random.randint(0, self.model_info.get('action_size', 8))
    
    def _predict_tensorflow(self, state: np.ndarray) -> int:
        """Predict action using TensorFlow model"""
        try:
            prediction = self.trained_model.predict(state.reshape(1, -1))
            return int(np.argmax(prediction))
        except:
            return np.random.randint(0, self.model_info.get('action_size', 8))
    
    def _predict_generic(self, state: np.ndarray) -> int:
        """Generic prediction method"""
        # Try to find any prediction method
        if hasattr(self.trained_model, 'predict'):
            try:
                prediction = self.trained_model.predict(state.reshape(1, -1))
                return int(prediction[0])
            except:
                pass
        
        # Fallback to random
        return np.random.randint(0, self.model_info.get('action_size', 8))
    
    def get_model_performance(self) -> Dict:
        """Get performance metrics from loaded model"""
        if not self.is_loaded:
            return {}
        
        return self.model_info.get('performance_metrics', {})
    
    def get_model_config(self) -> Dict:
        """Get configuration from loaded model"""
        if not self.is_loaded:
            return {}
        
        return self.model_info.get('config', {})
    
    def is_model_ready(self) -> bool:
        """Check if model is ready for use"""
        return self.is_loaded and self.model_info.get('has_weights', False)
    
    def get_action_space_size(self) -> int:
        """Get action space size"""
        return self.model_info.get('action_size', 8)
    
    def get_state_space_size(self) -> int:
        """Get state space size"""
        return self.model_info.get('state_size', 20)

def integrate_rl_model_with_master_ai(master_ai_controller, rl_model_path: str):
    """
    Integrate pre-trained RL model with existing Master AI Controller
    
    Args:
        master_ai_controller: Your existing Master AI Controller instance
        rl_model_path: Path to the .pkl file containing trained RL model
    
    Returns:
        bool: True if integration successful, False otherwise
    """
    try:
        # Load RL model
        rl_integrator = RLModelIntegrator(rl_model_path)
        
        if not rl_integrator.is_model_ready():
            logger.error("RL model is not ready for integration")
            return False
        
        # Override the action selection method in master AI controller
        def rl_enhanced_action_selection(traffic_data):
            """Enhanced action selection using RL model"""
            try:
                # Use RL model for action prediction
                action = rl_integrator.predict_action(traffic_data)
                return action
            except Exception as e:
                logger.warning(f"RL prediction failed, using fallback: {e}")
                # Fallback to original method
                return master_ai_controller.select_action_original(traffic_data)
        
        # Store original method as backup
        if hasattr(master_ai_controller, 'select_action'):
            master_ai_controller.select_action_original = master_ai_controller.select_action
        
        # Replace with RL-enhanced method
        master_ai_controller.select_action = rl_enhanced_action_selection
        
        # Add RL model info to controller
        master_ai_controller.rl_model = rl_integrator
        master_ai_controller.rl_enhanced = True
        
        logger.info("Successfully integrated RL model with Master AI Controller")
        return True
        
    except Exception as e:
        logger.error(f"Failed to integrate RL model: {e}")
        return False

def create_enhanced_master_ai_with_rl(master_ai_class, rl_model_path: str):
    """
    Create an enhanced Master AI Controller class with RL integration
    
    Args:
        master_ai_class: Your existing Master AI Controller class
        rl_model_path: Path to the .pkl file containing trained RL model
    
    Returns:
        Enhanced Master AI Controller class
    """
    
    class EnhancedMasterAI(master_ai_class):
        """Enhanced Master AI Controller with RL integration"""
        
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.rl_integrator = None
            self.rl_enhanced = False
            self._load_rl_model(rl_model_path)
        
        def _load_rl_model(self, model_path: str):
            """Load RL model during initialization"""
            try:
                self.rl_integrator = RLModelIntegrator(model_path)
                if self.rl_integrator.is_model_ready():
                    self.rl_enhanced = True
                    logger.info("RL model loaded successfully")
                else:
                    logger.warning("RL model loaded but not ready")
            except Exception as e:
                logger.error(f"Failed to load RL model: {e}")
        
        def select_action(self, traffic_data: Dict) -> int:
            """Enhanced action selection with RL model"""
            if self.rl_enhanced and self.rl_integrator:
                try:
                    return self.rl_integrator.predict_action(traffic_data)
                except Exception as e:
                    logger.warning(f"RL prediction failed, using fallback: {e}")
            
            # Fallback to original method
            return super().select_action(traffic_data)
        
        def get_rl_performance(self) -> Dict:
            """Get RL model performance metrics"""
            if self.rl_integrator:
                return self.rl_integrator.get_model_performance()
            return {}
        
        def is_rl_enhanced(self) -> bool:
            """Check if RL enhancement is active"""
            return self.rl_enhanced
    
    return EnhancedMasterAI

# Example usage functions
def example_integration():
    """Example of how to integrate RL model"""
    
    # Method 1: Integrate with existing instance
    from master_ai_controller import MasterAIController
    
    # Create master AI controller
    master_ai = MasterAIController()
    
    # Integrate RL model
    rl_model_path = "path/to/your/trained_model.pkl"
    success = integrate_rl_model_with_master_ai(master_ai, rl_model_path)
    
    if success:
        print("✅ RL model integrated successfully!")
        
        # Test with traffic data
        traffic_data = {
            'queue_lengths': {'I1': 5, 'I2': 10, 'I3': 3, 'I4': 8},
            'waiting_times': {'I1': 15, 'I2': 25, 'I3': 10, 'I4': 20},
            'vehicle_counts': {'north': 12, 'south': 8, 'east': 15, 'west': 10},
            'flow_rates': {'north': 200, 'south': 150, 'east': 180, 'west': 160},
            'current_phase': 1,
            'phase_duration': 30,
            'efficiency_scores': {'throughput': 85, 'waiting_time': 70, 'speed': 90}
        }
        
        # Get RL-enhanced action
        action = master_ai.select_action(traffic_data)
        print(f"RL-enhanced action: {action}")
    
    # Method 2: Create enhanced class
    EnhancedMasterAI = create_enhanced_master_ai_with_rl(MasterAIController, rl_model_path)
    enhanced_ai = EnhancedMasterAI()
    
    if enhanced_ai.is_rl_enhanced():
        print("✅ Enhanced Master AI with RL created successfully!")

if __name__ == "__main__":
    # Test the integration
    example_integration()

