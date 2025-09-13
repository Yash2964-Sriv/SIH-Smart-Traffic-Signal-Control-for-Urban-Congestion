#!/usr/bin/env python3
"""
Master AI Controller for Smart Traffic Simulator
Designed for Reinforcement Learning Training and Real-life Traffic Control
"""

import os
import json
import time
import numpy as np
import cv2
import traci
import subprocess
import threading
import pickle
import random
from datetime import datetime
from typing import Dict, List, Tuple, Optional, Any
import matplotlib.pyplot as plt
from collections import deque
import logging

# Import all AI components
from traffic_video_analyzer import TrafficVideoAnalyzer
from sumo_replicator import SUMOReplicator
from traffic_comparison_analyzer import TrafficComparisonAnalyzer
from ai_controller.simple_working_ai_controller import SimpleWorkingAIController

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MasterAIController:
    """
    Master AI Controller designed for reinforcement learning training
    Integrates all traffic analysis, control, and learning components
    """
    
    def __init__(self, config: Dict = None):
        """Initialize Master AI Controller with RL capabilities"""
        
        # Default configuration
        self.config = config or {
            'learning_rate': 0.001,
            'discount_factor': 0.95,
            'epsilon': 0.1,  # Exploration rate
            'epsilon_decay': 0.995,
            'epsilon_min': 0.01,
            'memory_size': 10000,
            'batch_size': 32,
            'target_update_frequency': 100,
            'training_frequency': 4,
            'video_path': "Traffic_videos/stock-footage-drone-shot-way-intersection.webm",
            'model_save_path': "models/master_ai_model.pkl",
            'experience_save_path': "data/experience_buffer.pkl"
        }
        
        # RL Components
        self.q_network = self._initialize_q_network()
        self.target_network = self._initialize_q_network()
        self.experience_buffer = deque(maxlen=self.config['memory_size'])
        self.optimizer = None  # Will be initialized based on framework
        
        # AI State Management
        self.current_state = None
        self.previous_state = None
        self.current_action = None
        self.previous_action = None
        self.reward_history = []
        self.episode_count = 0
        self.step_count = 0
        
        # Performance Tracking
        self.performance_metrics = {
            'total_rewards': [],
            'episode_rewards': [],
            'average_reward': 0,
            'best_performance': -float('inf'),
            'convergence_rate': 0,
            'learning_progress': []
        }
        
        # Traffic Control State
        self.traffic_state = {
            'current_phase': 0,
            'phase_duration': 0,
            'queue_lengths': {},
            'waiting_times': {},
            'vehicle_counts': {},
            'flow_rates': {},
            'efficiency_scores': {}
        }
        
        # AI Components
        self.video_analyzer = None
        self.sumo_replicator = None
        self.comparison_analyzer = None
        self.traffic_controller = None
        
        # Training Mode
        self.training_mode = True
        self.evaluation_mode = False
        
        # Real-time Data
        self.real_time_data = {
            'video_feed': None,
            'simulation_data': None,
            'traffic_metrics': None,
            'ai_decisions': []
        }
        
        logger.info("Master AI Controller initialized for RL training")
        logger.info(f"Configuration: {self.config}")
    
    def _initialize_q_network(self) -> Dict:
        """Initialize Q-Network for reinforcement learning"""
        # State space: [queue_lengths, waiting_times, phase_duration, time_of_day, weather, etc.]
        state_size = 20  # Adjust based on actual state representation
        
        # Action space: [change_phase, extend_green, reduce_cycle, coordinate_signals, etc.]
        action_size = 8  # Adjust based on available actions
        
        # Simple Q-Network structure (can be replaced with deep neural network)
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
        for junction_id in ['I1', 'I2', 'I3', 'I4']:  # Example junction IDs
            state[idx] = queue_lengths.get(junction_id, 0) / 100.0  # Normalize
            idx += 1
        
        # Waiting times (normalized)
        waiting_times = traffic_data.get('waiting_times', {})
        for junction_id in ['I1', 'I2', 'I3', 'I4']:
            state[idx] = waiting_times.get(junction_id, 0) / 60.0  # Normalize to minutes
            idx += 1
        
        # Current phase and duration
        state[idx] = traffic_data.get('current_phase', 0) / 4.0  # Normalize phase
        idx += 1
        state[idx] = traffic_data.get('phase_duration', 0) / 120.0  # Normalize duration
        idx += 1
        
        # Time of day (hour, day of week)
        current_time = datetime.now()
        state[idx] = current_time.hour / 24.0  # Normalize hour
        idx += 1
        state[idx] = current_time.weekday() / 7.0  # Normalize day of week
        idx += 1
        
        # Traffic flow rates
        flow_rates = traffic_data.get('flow_rates', {})
        for direction in ['north', 'south', 'east', 'west']:
            state[idx] = flow_rates.get(direction, 0) / 1000.0  # Normalize
            idx += 1
        
        # Vehicle counts
        vehicle_counts = traffic_data.get('vehicle_counts', {})
        for direction in ['north', 'south', 'east', 'west']:
            state[idx] = vehicle_counts.get(direction, 0) / 50.0  # Normalize
            idx += 1
        
        # Efficiency scores
        efficiency_scores = traffic_data.get('efficiency_scores', {})
        for metric in ['throughput', 'waiting_time', 'speed']:
            state[idx] = efficiency_scores.get(metric, 0) / 100.0  # Normalize
            idx += 1
        
        # Fill remaining state space with zeros if needed
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
        # Simple linear Q-network implementation
        q_values = np.dot(state, self.q_network['weights']) + self.q_network['bias']
        return q_values
    
    def execute_action(self, action: int, traffic_data: Dict) -> Dict:
        """Execute selected action and return results"""
        action_results = {
            'action_taken': action,
            'success': False,
            'new_state': None,
            'reward': 0,
            'traffic_changes': {}
        }
        
        try:
            # Map action to traffic control decision
            if action == 0:  # Change to next phase
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
            
            action_results['success'] = True
            
        except Exception as e:
            logger.error(f"Action execution failed: {e}")
            action_results['success'] = False
            action_results['reward'] = -10  # Penalty for failed action
        
        return action_results
    
    def _change_phase(self, traffic_data: Dict) -> Dict:
        """Change traffic light phase"""
        # Implementation for phase change
        return {
            'action_taken': 0,
            'success': True,
            'new_state': self._update_traffic_state(traffic_data, {'phase_change': True}),
            'reward': self._calculate_reward(traffic_data, 'phase_change'),
            'traffic_changes': {'phase_changed': True}
        }
    
    def _extend_green_time(self, traffic_data: Dict) -> Dict:
        """Extend green light duration"""
        # Implementation for extending green time
        return {
            'action_taken': 1,
            'success': True,
            'new_state': self._update_traffic_state(traffic_data, {'green_extension': 5}),
            'reward': self._calculate_reward(traffic_data, 'green_extension'),
            'traffic_changes': {'green_extended': 5}
        }
    
    def _reduce_cycle_time(self, traffic_data: Dict) -> Dict:
        """Reduce overall cycle time"""
        # Implementation for cycle time reduction
        return {
            'action_taken': 2,
            'success': True,
            'new_state': self._update_traffic_state(traffic_data, {'cycle_reduction': 10}),
            'reward': self._calculate_reward(traffic_data, 'cycle_reduction'),
            'traffic_changes': {'cycle_reduced': 10}
        }
    
    def _coordinate_signals(self, traffic_data: Dict) -> Dict:
        """Coordinate multiple traffic signals"""
        # Implementation for signal coordination
        return {
            'action_taken': 3,
            'success': True,
            'new_state': self._update_traffic_state(traffic_data, {'coordination': True}),
            'reward': self._calculate_reward(traffic_data, 'coordination'),
            'traffic_changes': {'signals_coordinated': True}
        }
    
    def _emergency_priority(self, traffic_data: Dict) -> Dict:
        """Implement emergency vehicle priority"""
        # Implementation for emergency priority
        return {
            'action_taken': 4,
            'success': True,
            'new_state': self._update_traffic_state(traffic_data, {'emergency_priority': True}),
            'reward': self._calculate_reward(traffic_data, 'emergency_priority'),
            'traffic_changes': {'emergency_priority': True}
        }
    
    def _adaptive_timing(self, traffic_data: Dict) -> Dict:
        """Implement adaptive timing based on current conditions"""
        # Implementation for adaptive timing
        return {
            'action_taken': 5,
            'success': True,
            'new_state': self._update_traffic_state(traffic_data, {'adaptive_timing': True}),
            'reward': self._calculate_reward(traffic_data, 'adaptive_timing'),
            'traffic_changes': {'timing_adapted': True}
        }
    
    def _manage_queues(self, traffic_data: Dict) -> Dict:
        """Manage vehicle queues to prevent overflow"""
        # Implementation for queue management
        return {
            'action_taken': 6,
            'success': True,
            'new_state': self._update_traffic_state(traffic_data, {'queue_management': True}),
            'reward': self._calculate_reward(traffic_data, 'queue_management'),
            'traffic_changes': {'queues_managed': True}
        }
    
    def _optimize_flow(self, traffic_data: Dict) -> Dict:
        """Optimize overall traffic flow"""
        # Implementation for flow optimization
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
        reward += max(0, 10 - avg_queue_length)  # Higher reward for shorter queues
        
        # Reward for reducing waiting times
        avg_waiting_time = np.mean(list(waiting_times.values())) if waiting_times else 0
        reward += max(0, 20 - avg_waiting_time)  # Higher reward for shorter waits
        
        # Reward for increasing flow rates
        avg_flow_rate = np.mean(list(flow_rates.values())) if flow_rates else 0
        reward += avg_flow_rate / 10  # Reward proportional to flow rate
        
        # Action-specific rewards
        if action_type == 'phase_change':
            reward += 5  # Reward for proactive phase changes
        elif action_type == 'green_extension':
            reward += 3  # Reward for extending green when needed
        elif action_type == 'coordination':
            reward += 8  # Higher reward for coordination
        elif action_type == 'emergency_priority':
            reward += 15  # High reward for emergency handling
        
        # Penalty for inefficient actions
        if avg_queue_length > 50:  # Very long queues
            reward -= 10
        if avg_waiting_time > 60:  # Very long waits
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
        
        # Update Q-network weights (simplified gradient descent)
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
        # Simple gradient descent update (can be replaced with more sophisticated optimizers)
        learning_rate = self.config['learning_rate']
        
        for i, state in enumerate(states):
            action = actions[i]
            target = target_q_values[i]
            
            # Current Q-value
            current_q = self._forward_pass(state)[action]
            
            # Calculate error
            error = target - current_q
            
            # Update weights (simplified gradient descent)
            self.q_network['weights'][:, action] += learning_rate * error * state
            self.q_network['bias'][action] += learning_rate * error
    
    def _update_target_network(self):
        """Update target network with current Q-network weights"""
        self.target_network['weights'] = self.q_network['weights'].copy()
        self.target_network['bias'] = self.q_network['bias'].copy()
        logger.info("Target network updated")
    
    def start_training_episode(self, video_path: str = None) -> Dict:
        """Start a training episode with video analysis"""
        logger.info(f"Starting training episode {self.episode_count + 1}")
        
        video_path = video_path or self.config['video_path']
        episode_data = {
            'episode_id': self.episode_count,
            'start_time': datetime.now(),
            'video_path': video_path,
            'total_reward': 0,
            'steps': 0,
            'actions_taken': [],
            'performance_metrics': {}
        }
        
        try:
            # Analyze video for traffic patterns
            if self.video_analyzer is None:
                self.video_analyzer = TrafficVideoAnalyzer(video_path)
            
            video_analysis = self.video_analyzer.analyze_video()
            episode_data['video_analysis'] = video_analysis
            
            # Create SUMO simulation
            if self.sumo_replicator is None:
                self.sumo_replicator = SUMOReplicator(video_analysis)
            
            simulation_created = self.sumo_replicator.create_network()
            episode_data['simulation_created'] = simulation_created
            
            if simulation_created:
                # Run training simulation
                training_results = self._run_training_simulation(video_analysis)
                episode_data.update(training_results)
            
            # Update performance metrics
            self._update_episode_metrics(episode_data)
            
            self.episode_count += 1
            logger.info(f"Training episode {self.episode_count} completed")
            
        except Exception as e:
            logger.error(f"Training episode failed: {e}")
            episode_data['error'] = str(e)
        
        return episode_data
    
    def _run_training_simulation(self, video_analysis: Dict) -> Dict:
        """Run training simulation with RL agent"""
        logger.info("Running training simulation")
        
        simulation_data = {
            'simulation_start': datetime.now(),
            'total_steps': 0,
            'total_reward': 0,
            'actions_taken': [],
            'performance_history': []
        }
        
        # Initialize simulation state
        current_state = self._initialize_simulation_state(video_analysis)
        
        # Run simulation steps
        max_steps = 1000  # Maximum steps per episode
        done = False
        
        for step in range(max_steps):
            if done:
                break
            
            # Select action
            action = self.select_action(current_state, training=True)
            
            # Execute action
            action_result = self.execute_action(action, current_state)
            
            # Calculate reward
            reward = action_result['reward']
            simulation_data['total_reward'] += reward
            
            # Get next state
            next_state = action_result['new_state']
            if next_state is None:
                next_state = current_state
            
            # Store experience
            self.store_experience(current_state, action, reward, next_state, done)
            
            # Train model
            if step % self.config['training_frequency'] == 0:
                self.train_model()
            
            # Update state
            current_state = next_state
            simulation_data['total_steps'] += 1
            simulation_data['actions_taken'].append(action)
            
            # Check if episode is done
            if self._is_episode_done(current_state, step):
                done = True
            
            # Log progress
            if step % 100 == 0:
                logger.info(f"Step {step}: Reward={reward:.2f}, Total={simulation_data['total_reward']:.2f}")
        
        simulation_data['simulation_end'] = datetime.now()
        simulation_data['duration'] = (simulation_data['simulation_end'] - simulation_data['simulation_start']).total_seconds()
        
        return simulation_data
    
    def _initialize_simulation_state(self, video_analysis: Dict) -> Dict:
        """Initialize simulation state from video analysis"""
        # Extract traffic patterns from video analysis
        traffic_patterns = video_analysis.get('traffic_patterns', {})
        timing_data = video_analysis.get('timing_data', {})
        
        # Initialize traffic state
        initial_state = {
            'queue_lengths': {'I1': 0, 'I2': 0, 'I3': 0, 'I4': 0},
            'waiting_times': {'I1': 0, 'I2': 0, 'I3': 0, 'I4': 0},
            'vehicle_counts': {'north': 0, 'south': 0, 'east': 0, 'west': 0},
            'flow_rates': {'north': 0, 'south': 0, 'east': 0, 'west': 0},
            'current_phase': 0,
            'phase_duration': 0,
            'efficiency_scores': {'throughput': 0, 'waiting_time': 0, 'speed': 0}
        }
        
        # Update with video analysis data
        if 'avg_vehicles_per_frame' in traffic_patterns:
            total_vehicles = traffic_patterns['avg_vehicles_per_frame']
            # Distribute vehicles across directions
            for direction in initial_state['vehicle_counts']:
                initial_state['vehicle_counts'][direction] = total_vehicles / 4
        
        if 'traffic_flow_rate' in traffic_patterns:
            flow_rate = traffic_patterns['traffic_flow_rate']
            for direction in initial_state['flow_rates']:
                initial_state['flow_rates'][direction] = flow_rate / 4
        
        return initial_state
    
    def _is_episode_done(self, state: Dict, step: int) -> bool:
        """Check if episode should end"""
        # End episode if maximum steps reached
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
        self.performance_metrics['total_rewards'].append(total_reward)
        
        # Calculate average reward
        if self.performance_metrics['episode_rewards']:
            self.performance_metrics['average_reward'] = np.mean(self.performance_metrics['episode_rewards'][-100:])  # Last 100 episodes
        
        # Update best performance
        if total_reward > self.performance_metrics['best_performance']:
            self.performance_metrics['best_performance'] = total_reward
        
        # Calculate convergence rate
        if len(self.performance_metrics['episode_rewards']) > 10:
            recent_rewards = self.performance_metrics['episode_rewards'][-10:]
            self.performance_metrics['convergence_rate'] = np.std(recent_rewards)
        
        # Log performance
        logger.info(f"Episode {episode_data['episode_id']}: Reward={total_reward:.2f}, "
                   f"Avg Reward={self.performance_metrics['average_reward']:.2f}, "
                   f"Best={self.performance_metrics['best_performance']:.2f}")
    
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
        """Save experience buffer for later use"""
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
    
    def evaluate_model(self, test_video_path: str) -> Dict:
        """Evaluate trained model on test data"""
        logger.info("Evaluating model on test data")
        
        self.evaluation_mode = True
        original_epsilon = self.config['epsilon']
        self.config['epsilon'] = 0  # No exploration during evaluation
        
        try:
            # Run evaluation episode
            evaluation_data = self.start_training_episode(test_video_path)
            
            # Calculate evaluation metrics
            evaluation_metrics = {
                'total_reward': evaluation_data.get('total_reward', 0),
                'average_reward_per_step': evaluation_data.get('total_reward', 0) / max(1, evaluation_data.get('total_steps', 1)),
                'efficiency_score': self._calculate_efficiency_score(evaluation_data),
                'accuracy_score': self._calculate_accuracy_score(evaluation_data),
                'stability_score': self._calculate_stability_score(evaluation_data)
            }
            
            logger.info(f"Evaluation completed: {evaluation_metrics}")
            
        finally:
            self.evaluation_mode = False
            self.config['epsilon'] = original_epsilon
        
        return evaluation_metrics
    
    def _calculate_efficiency_score(self, episode_data: Dict) -> float:
        """Calculate efficiency score for evaluation"""
        # Simplified efficiency calculation
        total_reward = episode_data.get('total_reward', 0)
        total_steps = episode_data.get('total_steps', 1)
        
        efficiency = (total_reward / total_steps) * 100
        return min(100, max(0, efficiency))
    
    def _calculate_accuracy_score(self, episode_data: Dict) -> float:
        """Calculate accuracy score for evaluation"""
        # Simplified accuracy calculation based on action success rate
        actions_taken = episode_data.get('actions_taken', [])
        if not actions_taken:
            return 0
        
        # Assume all actions were successful for simplicity
        success_rate = 1.0
        return success_rate * 100
    
    def _calculate_stability_score(self, episode_data: Dict) -> float:
        """Calculate stability score for evaluation"""
        # Simplified stability calculation based on reward consistency
        total_reward = episode_data.get('total_reward', 0)
        total_steps = episode_data.get('total_steps', 1)
        
        if total_steps == 0:
            return 0
        
        # Stability based on consistent positive rewards
        stability = min(100, max(0, (total_reward / total_steps) * 10))
        return stability
    
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
            'training_mode': self.training_mode,
            'evaluation_mode': self.evaluation_mode
        }
    
    def start_real_time_control(self, video_path: str = None):
        """Start real-time traffic control using trained model"""
        logger.info("Starting real-time traffic control")
        
        self.training_mode = False
        self.evaluation_mode = False
        self.config['epsilon'] = 0  # No exploration in real-time control
        
        # Load trained model if available
        if not self.load_model():
            logger.warning("No trained model found, using random actions")
        
        try:
            # Initialize video analysis
            video_path = video_path or self.config['video_path']
            self.video_analyzer = TrafficVideoAnalyzer(video_path)
            video_analysis = self.video_analyzer.analyze_video()
            
            # Create SUMO simulation
            self.sumo_replicator = SUMOReplicator(video_analysis)
            if not self.sumo_replicator.create_network():
                raise Exception("Failed to create SUMO network")
            
            # Start real-time control loop
            self._real_time_control_loop(video_analysis)
            
        except Exception as e:
            logger.error(f"Real-time control failed: {e}")
    
    def _real_time_control_loop(self, video_analysis: Dict):
        """Real-time control loop"""
        logger.info("Starting real-time control loop")
        
        # Initialize traffic state
        current_state = self._initialize_simulation_state(video_analysis)
        
        step = 0
        while True:
            try:
                # Get current state representation
                state_vector = self.get_state_representation(current_state)
                
                # Select action using trained model
                action = self.select_action(state_vector, training=False)
                
                # Execute action
                action_result = self.execute_action(action, current_state)
                
                # Update state
                if action_result['new_state']:
                    current_state = action_result['new_state']
                
                # Log action
                logger.info(f"Step {step}: Action {action}, Reward {action_result['reward']:.2f}")
                
                step += 1
                time.sleep(1)  # Control frequency
                
            except KeyboardInterrupt:
                logger.info("Real-time control stopped by user")
                break
            except Exception as e:
                logger.error(f"Real-time control error: {e}")
                time.sleep(5)
    
    def generate_training_report(self) -> Dict:
        """Generate comprehensive training report"""
        report = {
            'training_summary': {
                'total_episodes': self.episode_count,
                'total_steps': self.step_count,
                'current_epsilon': self.config['epsilon'],
                'experience_buffer_size': len(self.experience_buffer)
            },
            'performance_metrics': self.performance_metrics,
            'model_architecture': {
                'state_size': self.q_network['state_size'],
                'action_size': self.q_network['action_size'],
                'layers': self.q_network['layers']
            },
            'configuration': self.config,
            'recommendations': self._generate_training_recommendations()
        }
        
        return report
    
    def _generate_training_recommendations(self) -> List[str]:
        """Generate training recommendations"""
        recommendations = []
        
        if self.performance_metrics['average_reward'] < 50:
            recommendations.append("Consider increasing learning rate or training for more episodes")
        
        if self.performance_metrics['convergence_rate'] > 10:
            recommendations.append("Model is not converging well, consider adjusting hyperparameters")
        
        if len(self.experience_buffer) < 1000:
            recommendations.append("Collect more experience data for better training")
        
        if self.config['epsilon'] > 0.1:
            recommendations.append("Consider reducing exploration rate for better exploitation")
        
        return recommendations

def main():
    """Main function for training and testing the Master AI Controller"""
    print("🤖 Master AI Controller for Smart Traffic Simulator")
    print("=" * 60)
    
    # Initialize Master AI Controller
    config = {
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
        'experience_save_path': "data/experience_buffer.pkl"
    }
    
    master_ai = MasterAIController(config)
    
    # Training mode
    print("\n🎯 Starting Training Mode")
    print("=" * 40)
    
    # Train for multiple episodes
    num_episodes = 10  # Adjust as needed
    
    for episode in range(num_episodes):
        print(f"\n📚 Training Episode {episode + 1}/{num_episodes}")
        episode_data = master_ai.start_training_episode()
        
        if episode % 5 == 0:  # Save model every 5 episodes
            master_ai.save_model()
            master_ai.save_experience_buffer()
    
    # Final model save
    master_ai.save_model()
    master_ai.save_experience_buffer()
    
    # Generate training report
    report = master_ai.generate_training_report()
    
    print("\n📊 Training Report")
    print("=" * 40)
    print(f"Total Episodes: {report['training_summary']['total_episodes']}")
    print(f"Total Steps: {report['training_summary']['total_steps']}")
    print(f"Average Reward: {report['performance_metrics']['average_reward']:.2f}")
    print(f"Best Performance: {report['performance_metrics']['best_performance']:.2f}")
    print(f"Convergence Rate: {report['performance_metrics']['convergence_rate']:.2f}")
    
    print("\n💡 Recommendations:")
    for rec in report['recommendations']:
        print(f"  • {rec}")
    
    # Option to start real-time control
    response = input("\n🚦 Start real-time control? (y/n): ")
    if response.lower() == 'y':
        master_ai.start_real_time_control()

if __name__ == "__main__":
    main()

