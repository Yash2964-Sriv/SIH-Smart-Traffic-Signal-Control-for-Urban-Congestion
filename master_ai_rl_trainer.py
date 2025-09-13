#!/usr/bin/env python3
"""
Master AI RL Trainer - Focused Reinforcement Learning Training Module
Train this AI on real traffic data, then integrate with your existing system
"""

import os
import json
import time
import numpy as np
import pickle
import random
from datetime import datetime
from typing import Dict, List, Tuple, Optional
from collections import deque
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MasterAIRLTrainer:
    """
    Master AI Reinforcement Learning Trainer
    Focused on training RL models for traffic control
    """
    
    def __init__(self, config: Dict = None):
        """Initialize RL Trainer"""
        
        # Default configuration
        self.config = config or {
            'learning_rate': 0.001,
            'discount_factor': 0.95,
            'epsilon': 0.1,
            'epsilon_decay': 0.995,
            'epsilon_min': 0.01,
            'memory_size': 10000,
            'batch_size': 32,
            'target_update_frequency': 100,
            'training_frequency': 4,
            'state_size': 25,  # Increased to accommodate all features
            'action_size': 8,
            'model_save_path': "models/rl_trained_model.pkl",
            'experience_save_path': "data/rl_experience_buffer.pkl"
        }
        
        # RL Components
        self.q_network = self._initialize_q_network()
        self.target_network = self._initialize_q_network()
        self.experience_buffer = deque(maxlen=self.config['memory_size'])
        
        # Training state
        self.episode_count = 0
        self.step_count = 0
        self.training_mode = True
        
        # Performance tracking
        self.performance_metrics = {
            'episode_rewards': [],
            'average_reward': 0,
            'best_performance': -float('inf'),
            'convergence_rate': 0,
            'learning_progress': []
        }
        
        logger.info("Master AI RL Trainer initialized")
    
    def _initialize_q_network(self) -> Dict:
        """Initialize Q-Network for RL training"""
        state_size = self.config['state_size']
        action_size = self.config['action_size']
        
        # Simple Q-Network (can be replaced with deep neural network)
        q_network = {
            'state_size': state_size,
            'action_size': action_size,
            'weights': np.random.normal(0, 0.1, (state_size, action_size)),
            'bias': np.zeros(action_size),
            'layers': [
                {'type': 'dense', 'units': 64, 'activation': 'relu'},
                {'type': 'dense', 'units': 32, 'activation': 'relu'},
                {'type': 'dense', 'units': action_size, 'activation': 'linear'}
            ]
        }
        
        return q_network
    
    def get_state_representation(self, traffic_data: Dict) -> np.ndarray:
        """Convert traffic data to state representation for RL"""
        state = np.zeros(self.q_network['state_size'])
        
        # Extract features from traffic data
        idx = 0
        
        # Queue lengths (normalized)
        queue_lengths = traffic_data.get('queue_lengths', {})
        for junction_id in ['I1', 'I2']:  # Only use existing traffic lights
            state[idx] = queue_lengths.get(junction_id, 0) / 100.0
            idx += 1
        
        # Fill remaining junction slots with zeros
        for _ in range(2):  # I3, I4 don't exist
            state[idx] = 0
            idx += 1
        
        # Waiting times (normalized)
        waiting_times = traffic_data.get('waiting_times', {})
        for junction_id in ['I1', 'I2']:
            state[idx] = waiting_times.get(junction_id, 0) / 60.0
            idx += 1
        
        # Fill remaining waiting time slots
        for _ in range(2):
            state[idx] = 0
            idx += 1
        
        # Current phase and duration (use average if multiple traffic lights)
        current_phases = traffic_data.get('current_phase', {})
        phase_durations = traffic_data.get('phase_duration', {})
        
        if current_phases:
            avg_phase = np.mean(list(current_phases.values())) / 4.0
        else:
            avg_phase = 0
        state[idx] = avg_phase
        idx += 1
        
        if phase_durations:
            avg_duration = np.mean(list(phase_durations.values())) / 120.0
        else:
            avg_duration = 0
        state[idx] = avg_duration
        idx += 1
        
        # Time of day
        current_time = datetime.now()
        state[idx] = current_time.hour / 24.0
        idx += 1
        state[idx] = current_time.weekday() / 7.0
        idx += 1
        
        # Traffic flow rates
        flow_rates = traffic_data.get('flow_rates', {})
        for direction in ['north', 'south', 'east', 'west']:
            state[idx] = flow_rates.get(direction, 0) / 1000.0
            idx += 1
        
        # Vehicle counts
        vehicle_counts = traffic_data.get('vehicle_counts', {})
        for direction in ['north', 'south', 'east', 'west']:
            state[idx] = vehicle_counts.get(direction, 0) / 50.0
            idx += 1
        
        # Efficiency scores
        efficiency_scores = traffic_data.get('efficiency_scores', {})
        for metric in ['throughput', 'waiting_time', 'speed']:
            state[idx] = efficiency_scores.get(metric, 0) / 100.0
            idx += 1
        
        # Fill remaining state space
        while idx < self.q_network['state_size']:
            state[idx] = 0
            idx += 1
        
        return state
    
    def select_action(self, state: np.ndarray, training: bool = True) -> int:
        """Select action using epsilon-greedy policy"""
        if training and random.random() < self.config['epsilon']:
            # Exploration: random action
            action = random.randint(0, self.q_network['action_size'] - 1)
        else:
            # Exploitation: best action according to Q-network
            q_values = self._forward_pass(state)
            action = np.argmax(q_values)
        
        return action
    
    def _forward_pass(self, state: np.ndarray) -> np.ndarray:
        """Forward pass through Q-network"""
        q_values = np.dot(state, self.q_network['weights']) + self.q_network['bias']
        return q_values
    
    def execute_action(self, action: int, traffic_data: Dict) -> Dict:
        """Execute selected action and return results"""
        action_results = {
            'action_taken': action,
            'success': True,
            'new_state': None,
            'reward': 0,
            'traffic_changes': {}
        }
        
        try:
            # Map action to traffic control decision
            if action == 0:  # Change phase
                action_results = self._change_phase(traffic_data)
            elif action == 1:  # Extend green time
                action_results = self._extend_green_time(traffic_data)
            elif action == 2:  # Reduce cycle time
                action_results = self._reduce_cycle_time(traffic_data)
            elif action == 3:  # Coordinate signals
                action_results = self._coordinate_signals(traffic_data)
            elif action == 4:  # Emergency priority
                action_results = self._emergency_priority(traffic_data)
            elif action == 5:  # Adaptive timing
                action_results = self._adaptive_timing(traffic_data)
            elif action == 6:  # Queue management
                action_results = self._manage_queues(traffic_data)
            elif action == 7:  # Flow optimization
                action_results = self._optimize_flow(traffic_data)
            
        except Exception as e:
            logger.error(f"Action execution failed: {e}")
            action_results['success'] = False
            action_results['reward'] = -10
        
        return action_results
    
    def _change_phase(self, traffic_data: Dict) -> Dict:
        """Change traffic light phase"""
        return {
            'action_taken': 0,
            'success': True,
            'new_state': self._update_traffic_state(traffic_data, {'phase_change': True}),
            'reward': self._calculate_reward(traffic_data, 'phase_change'),
            'traffic_changes': {'phase_changed': True}
        }
    
    def _extend_green_time(self, traffic_data: Dict) -> Dict:
        """Extend green light duration"""
        return {
            'action_taken': 1,
            'success': True,
            'new_state': self._update_traffic_state(traffic_data, {'green_extension': 5}),
            'reward': self._calculate_reward(traffic_data, 'green_extension'),
            'traffic_changes': {'green_extended': 5}
        }
    
    def _reduce_cycle_time(self, traffic_data: Dict) -> Dict:
        """Reduce overall cycle time"""
        return {
            'action_taken': 2,
            'success': True,
            'new_state': self._update_traffic_state(traffic_data, {'cycle_reduction': 10}),
            'reward': self._calculate_reward(traffic_data, 'cycle_reduction'),
            'traffic_changes': {'cycle_reduced': 10}
        }
    
    def _coordinate_signals(self, traffic_data: Dict) -> Dict:
        """Coordinate multiple traffic signals"""
        return {
            'action_taken': 3,
            'success': True,
            'new_state': self._update_traffic_state(traffic_data, {'coordination': True}),
            'reward': self._calculate_reward(traffic_data, 'coordination'),
            'traffic_changes': {'signals_coordinated': True}
        }
    
    def _emergency_priority(self, traffic_data: Dict) -> Dict:
        """Implement emergency vehicle priority"""
        return {
            'action_taken': 4,
            'success': True,
            'new_state': self._update_traffic_state(traffic_data, {'emergency_priority': True}),
            'reward': self._calculate_reward(traffic_data, 'emergency_priority'),
            'traffic_changes': {'emergency_priority': True}
        }
    
    def _adaptive_timing(self, traffic_data: Dict) -> Dict:
        """Implement adaptive timing"""
        return {
            'action_taken': 5,
            'success': True,
            'new_state': self._update_traffic_state(traffic_data, {'adaptive_timing': True}),
            'reward': self._calculate_reward(traffic_data, 'adaptive_timing'),
            'traffic_changes': {'timing_adapted': True}
        }
    
    def _manage_queues(self, traffic_data: Dict) -> Dict:
        """Manage vehicle queues"""
        return {
            'action_taken': 6,
            'success': True,
            'new_state': self._update_traffic_state(traffic_data, {'queue_management': True}),
            'reward': self._calculate_reward(traffic_data, 'queue_management'),
            'traffic_changes': {'queues_managed': True}
        }
    
    def _optimize_flow(self, traffic_data: Dict) -> Dict:
        """Optimize traffic flow"""
        return {
            'action_taken': 7,
            'success': True,
            'new_state': self._update_traffic_state(traffic_data, {'flow_optimization': True}),
            'reward': self._calculate_reward(traffic_data, 'flow_optimization'),
            'traffic_changes': {'flow_optimized': True}
        }
    
    def _update_traffic_state(self, current_data: Dict, changes: Dict) -> Dict:
        """Update traffic state based on action results"""
        new_state = current_data.copy()
        new_state.update(changes)
        return new_state
    
    def _calculate_reward(self, traffic_data: Dict, action_type: str) -> float:
        """Calculate reward for the taken action"""
        reward = 0
        
        # Base reward components
        queue_lengths = traffic_data.get('queue_lengths', {})
        waiting_times = traffic_data.get('waiting_times', {})
        flow_rates = traffic_data.get('flow_rates', {})
        
        # Reward for reducing queue lengths
        avg_queue_length = np.mean(list(queue_lengths.values())) if queue_lengths else 0
        reward += max(0, 10 - avg_queue_length)
        
        # Reward for reducing waiting times
        avg_waiting_time = np.mean(list(waiting_times.values())) if waiting_times else 0
        reward += max(0, 20 - avg_waiting_time)
        
        # Reward for increasing flow rates
        avg_flow_rate = np.mean(list(flow_rates.values())) if flow_rates else 0
        reward += avg_flow_rate / 10
        
        # Action-specific rewards
        if action_type == 'phase_change':
            reward += 5
        elif action_type == 'green_extension':
            reward += 3
        elif action_type == 'coordination':
            reward += 8
        elif action_type == 'emergency_priority':
            reward += 15
        
        # Penalties for poor performance
        if avg_queue_length > 50:
            reward -= 10
        if avg_waiting_time > 60:
            reward -= 15
        
        return reward
    
    def store_experience(self, state: np.ndarray, action: int, reward: float, 
                        next_state: np.ndarray, done: bool):
        """Store experience in replay buffer"""
        experience = {
            'state': state,
            'action': action,
            'reward': reward,
            'next_state': next_state,
            'done': done,
            'timestamp': datetime.now()
        }
        
        self.experience_buffer.append(experience)
    
    def train_model(self, batch_size: int = None):
        """Train the Q-network using experience replay"""
        if len(self.experience_buffer) < self.config['batch_size']:
            return
        
        batch_size = batch_size or self.config['batch_size']
        batch = random.sample(self.experience_buffer, batch_size)
        
        # Prepare training data
        states = np.array([exp['state'] for exp in batch])
        actions = np.array([exp['action'] for exp in batch])
        rewards = np.array([exp['reward'] for exp in batch])
        next_states = np.array([exp['next_state'] for exp in batch])
        dones = np.array([exp['done'] for exp in batch])
        
        # Calculate target Q-values
        target_q_values = self._calculate_target_q_values(next_states, rewards, dones)
        
        # Update Q-network weights
        self._update_q_network(states, actions, target_q_values)
        
        # Update epsilon for exploration
        if self.config['epsilon'] > self.config['epsilon_min']:
            self.config['epsilon'] *= self.config['epsilon_decay']
        
        # Update target network periodically
        if self.step_count % self.config['target_update_frequency'] == 0:
            self._update_target_network()
        
        self.step_count += 1
    
    def _calculate_target_q_values(self, next_states: np.ndarray, rewards: np.ndarray, 
                                 dones: np.ndarray) -> np.ndarray:
        """Calculate target Q-values using target network"""
        next_q_values = np.array([self._forward_pass(state) for state in next_states])
        max_next_q_values = np.max(next_q_values, axis=1)
        
        target_q_values = rewards + (self.config['discount_factor'] * max_next_q_values * (1 - dones))
        return target_q_values
    
    def _update_q_network(self, states: np.ndarray, actions: np.ndarray, 
                         target_q_values: np.ndarray):
        """Update Q-network weights using gradient descent"""
        learning_rate = self.config['learning_rate']
        
        for i, state in enumerate(states):
            action = actions[i]
            target = target_q_values[i]
            
            # Current Q-value
            current_q = self._forward_pass(state)[action]
            
            # Calculate error
            error = target - current_q
            
            # Update weights
            self.q_network['weights'][:, action] += learning_rate * error * state
            self.q_network['bias'][action] += learning_rate * error
    
    def _update_target_network(self):
        """Update target network with current Q-network weights"""
        self.target_network['weights'] = self.q_network['weights'].copy()
        self.target_network['bias'] = self.q_network['bias'].copy()
        logger.info("Target network updated")
    
    def train_episode(self, traffic_data: Dict, max_steps: int = 1000) -> Dict:
        """Train for one episode"""
        logger.info(f"Starting training episode {self.episode_count + 1}")
        
        episode_data = {
            'episode_id': self.episode_count,
            'start_time': datetime.now(),
            'total_reward': 0,
            'steps': 0,
            'actions_taken': [],
            'performance_metrics': {}
        }
        
        # Initialize state
        current_state = traffic_data.copy()
        done = False
        
        for step in range(max_steps):
            if done:
                break
            
            # Get state representation
            state_vector = self.get_state_representation(current_state)
            
            # Select action
            action = self.select_action(state_vector, training=True)
            
            # Execute action
            action_result = self.execute_action(action, current_state)
            
            # Calculate reward
            reward = action_result['reward']
            episode_data['total_reward'] += reward
            
            # Get next state
            next_state = action_result['new_state']
            if next_state is None:
                next_state = current_state
            
            # Store experience
            self.store_experience(state_vector, action, reward, 
                                self.get_state_representation(next_state), done)
            
            # Train model
            if step % self.config['training_frequency'] == 0:
                self.train_model()
            
            # Update state
            current_state = next_state
            episode_data['steps'] += 1
            episode_data['actions_taken'].append(action)
            
            # Check if episode is done
            if self._is_episode_done(current_state, step):
                done = True
        
        # Update performance metrics
        self._update_episode_metrics(episode_data)
        self.episode_count += 1
        
        logger.info(f"Episode {self.episode_count} completed: Reward = {episode_data['total_reward']:.2f}")
        
        return episode_data
    
    def _is_episode_done(self, state: Dict, step: int) -> bool:
        """Check if episode should end"""
        if step >= 1000:
            return True
        
        # End episode if all queues are empty and no vehicles
        queue_lengths = state.get('queue_lengths', {})
        if all(length == 0 for length in queue_lengths.values()):
            vehicle_counts = state.get('vehicle_counts', {})
            if all(count == 0 for count in vehicle_counts.values()):
                return True
        
        return False
    
    def _update_episode_metrics(self, episode_data: Dict):
        """Update performance metrics after episode"""
        total_reward = episode_data.get('total_reward', 0)
        
        # Update reward history
        self.performance_metrics['episode_rewards'].append(total_reward)
        
        # Calculate average reward
        if self.performance_metrics['episode_rewards']:
            self.performance_metrics['average_reward'] = np.mean(
                self.performance_metrics['episode_rewards'][-100:]  # Last 100 episodes
            )
        
        # Update best performance
        if total_reward > self.performance_metrics['best_performance']:
            self.performance_metrics['best_performance'] = total_reward
        
        # Calculate convergence rate
        if len(self.performance_metrics['episode_rewards']) > 10:
            recent_rewards = self.performance_metrics['episode_rewards'][-10:]
            self.performance_metrics['convergence_rate'] = np.std(recent_rewards)
    
    def save_model(self, filepath: str = None):
        """Save trained model"""
        filepath = filepath or self.config['model_save_path']
        
        model_data = {
            'q_network': self.q_network,
            'target_network': self.target_network,
            'config': self.config,
            'performance_metrics': self.performance_metrics,
            'episode_count': self.episode_count,
            'step_count': self.step_count,
            'timestamp': datetime.now().isoformat()
        }
        
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        with open(filepath, 'wb') as f:
            pickle.dump(model_data, f)
        
        logger.info(f"Model saved to {filepath}")
    
    def load_model(self, filepath: str = None):
        """Load trained model"""
        filepath = filepath or self.config['model_save_path']
        
        if not os.path.exists(filepath):
            logger.warning(f"Model file {filepath} not found")
            return False
        
        try:
            with open(filepath, 'rb') as f:
                model_data = pickle.load(f)
            
            self.q_network = model_data['q_network']
            self.target_network = model_data['target_network']
            self.config.update(model_data['config'])
            self.performance_metrics = model_data['performance_metrics']
            self.episode_count = model_data['episode_count']
            self.step_count = model_data['step_count']
            
            logger.info(f"Model loaded from {filepath}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            return False
    
    def save_experience_buffer(self, filepath: str = None):
        """Save experience buffer"""
        filepath = filepath or self.config['experience_save_path']
        
        experience_data = {
            'buffer': list(self.experience_buffer),
            'config': self.config,
            'timestamp': datetime.now().isoformat()
        }
        
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        with open(filepath, 'wb') as f:
            pickle.dump(experience_data, f)
        
        logger.info(f"Experience buffer saved to {filepath}")
    
    def load_experience_buffer(self, filepath: str = None):
        """Load experience buffer"""
        filepath = filepath or self.config['experience_save_path']
        
        if not os.path.exists(filepath):
            logger.warning(f"Experience buffer file {filepath} not found")
            return False
        
        try:
            with open(filepath, 'rb') as f:
                experience_data = pickle.load(f)
            
            self.experience_buffer = deque(experience_data['buffer'], maxlen=self.config['memory_size'])
            
            logger.info(f"Experience buffer loaded from {filepath}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to load experience buffer: {e}")
            return False
    
    def get_training_status(self) -> Dict:
        """Get current training status"""
        return {
            'episode_count': self.episode_count,
            'step_count': self.step_count,
            'epsilon': self.config['epsilon'],
            'experience_buffer_size': len(self.experience_buffer),
            'average_reward': self.performance_metrics['average_reward'],
            'best_performance': self.performance_metrics['best_performance'],
            'convergence_rate': self.performance_metrics['convergence_rate'],
            'training_mode': self.training_mode
        }
    
    def predict_action(self, traffic_data: Dict) -> int:
        """Predict best action for given traffic data (for inference)"""
        state = self.get_state_representation(traffic_data)
        action = self.select_action(state, training=False)
        return action
    
    def get_model_info(self) -> Dict:
        """Get model information for integration"""
        return {
            'state_size': self.q_network['state_size'],
            'action_size': self.q_network['action_size'],
            'weights': self.q_network['weights'],
            'bias': self.q_network['bias'],
            'config': self.config,
            'performance_metrics': self.performance_metrics
        }

def main():
    """Main function for training the RL model"""
    print("🤖 Master AI RL Trainer")
    print("=" * 40)
    
    # Initialize trainer
    config = {
        'learning_rate': 0.001,
        'epsilon': 0.1,
        'training_episodes': 100,
        'model_save_path': "models/rl_trained_model.pkl"
    }
    
    trainer = MasterAIRLTrainer(config)
    
    # Sample traffic data for training
    sample_traffic_data = {
        'queue_lengths': {'I1': 5, 'I2': 10, 'I3': 3, 'I4': 8},
        'waiting_times': {'I1': 15, 'I2': 25, 'I3': 10, 'I4': 20},
        'vehicle_counts': {'north': 12, 'south': 8, 'east': 15, 'west': 10},
        'flow_rates': {'north': 200, 'south': 150, 'east': 180, 'west': 160},
        'current_phase': 1,
        'phase_duration': 30,
        'efficiency_scores': {'throughput': 85, 'waiting_time': 70, 'speed': 90}
    }
    
    # Train for multiple episodes
    print("Starting training...")
    for episode in range(config['training_episodes']):
        episode_data = trainer.train_episode(sample_traffic_data)
        
        if episode % 10 == 0:
            status = trainer.get_training_status()
            print(f"Episode {episode + 1}: Reward = {episode_data['total_reward']:.2f}, "
                  f"Avg Reward = {status['average_reward']:.2f}, "
                  f"Epsilon = {status['epsilon']:.3f}")
    
    # Save trained model
    trainer.save_model()
    trainer.save_experience_buffer()
    
    print(f"\n✅ Training completed!")
    print(f"📊 Final Performance: {trainer.performance_metrics['average_reward']:.2f}")
    print(f"🎯 Model saved to: {config['model_save_path']}")
    
    # Test prediction
    print(f"\n🧪 Testing prediction...")
    predicted_action = trainer.predict_action(sample_traffic_data)
    print(f"Predicted action for sample data: {predicted_action}")

if __name__ == "__main__":
    main()
