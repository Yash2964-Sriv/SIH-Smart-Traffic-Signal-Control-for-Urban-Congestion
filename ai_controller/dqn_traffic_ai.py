#!/usr/bin/env python3
"""
Deep Q-Network (DQN) AI for Adaptive Traffic Signal Control
Real-time traffic optimization using reinforcement learning
"""

import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
import random
from collections import deque
import json
import time
from typing import Dict, List, Tuple, Optional
import os

class DQNTrafficAI(nn.Module):
    """
    Deep Q-Network for traffic signal control
    """
    
    def __init__(self, state_size: int, action_size: int, hidden_size: int = 128):
        super(DQNTrafficAI, self).__init__()
        
        self.state_size = state_size
        self.action_size = action_size
        
        # Neural network architecture
        self.fc1 = nn.Linear(state_size, hidden_size)
        self.fc2 = nn.Linear(hidden_size, hidden_size)
        self.fc3 = nn.Linear(hidden_size, hidden_size)
        self.fc4 = nn.Linear(hidden_size, action_size)
        
        # Dropout for regularization
        self.dropout = nn.Dropout(0.2)
        
    def forward(self, x):
        """Forward pass through the network"""
        x = F.relu(self.fc1(x))
        x = self.dropout(x)
        x = F.relu(self.fc2(x))
        x = self.dropout(x)
        x = F.relu(self.fc3(x))
        x = self.dropout(x)
        x = self.fc4(x)
        return x

class ReplayBuffer:
    """
    Experience replay buffer for DQN training
    """
    
    def __init__(self, capacity: int = 10000):
        self.buffer = deque(maxlen=capacity)
    
    def push(self, state, action, reward, next_state, done):
        """Add experience to buffer"""
        self.buffer.append((state, action, reward, next_state, done))
    
    def sample(self, batch_size: int):
        """Sample random batch from buffer"""
        batch = random.sample(self.buffer, batch_size)
        state, action, reward, next_state, done = map(np.stack, zip(*batch))
        return state, action, reward, next_state, done
    
    def __len__(self):
        return len(self.buffer)

class TrafficSignalController:
    """
    Main AI controller for traffic signal optimization
    """
    
    def __init__(self, 
                 state_size: int = 8,  # [cars_north, cars_south, cars_east, cars_west, current_phase, elapsed_time, queue_length, avg_speed]
                 action_size: int = 4,  # [extend_green_5s, extend_green_10s, switch_to_ew, switch_to_ns]
                 learning_rate: float = 0.001,
                 gamma: float = 0.95,
                 epsilon: float = 1.0,
                 epsilon_min: float = 0.01,
                 epsilon_decay: float = 0.9995,
                 memory_size: int = 10000,
                 batch_size: int = 32):
        
        self.state_size = state_size
        self.action_size = action_size
        self.learning_rate = learning_rate
        self.gamma = gamma
        self.epsilon = epsilon
        self.epsilon_min = epsilon_min
        self.epsilon_decay = epsilon_decay
        self.batch_size = batch_size
        
        # Neural networks
        self.q_network = DQNTrafficAI(state_size, action_size)
        self.target_network = DQNTrafficAI(state_size, action_size)
        self.optimizer = optim.Adam(self.q_network.parameters(), lr=learning_rate)
        
        # Experience replay
        self.memory = ReplayBuffer(memory_size)
        
        # Training metrics
        self.training_metrics = {
            'episode_rewards': [],
            'episode_waiting_times': [],
            'episode_throughputs': [],
            'episode_losses': []
        }
        
        # Action mapping
        self.action_map = {
            0: "extend_green_5s",
            1: "extend_green_10s", 
            2: "switch_to_ew",
            3: "switch_to_ns"
        }
        
        print("🧠 DQN Traffic AI initialized")
        print(f"   State size: {state_size}")
        print(f"   Action size: {action_size}")
        print(f"   Learning rate: {learning_rate}")
    
    def get_state(self, sumo_data: Dict) -> np.ndarray:
        """
        Extract state from SUMO data
        
        Args:
            sumo_data: Dictionary containing SUMO simulation data
            
        Returns:
            State vector as numpy array
        """
        # Extract vehicle counts per direction
        vehicles_north = sumo_data.get('vehicles_north', 0)
        vehicles_south = sumo_data.get('vehicles_south', 0)
        vehicles_east = sumo_data.get('vehicles_east', 0)
        vehicles_west = sumo_data.get('vehicles_west', 0)
        
        # Current traffic light phase (0: NS green, 1: EW green)
        current_phase = sumo_data.get('current_phase', 0)
        
        # Time since last phase change
        elapsed_time = sumo_data.get('elapsed_time', 0)
        
        # Average queue length
        queue_length = sumo_data.get('queue_length', 0)
        
        # Average vehicle speed
        avg_speed = sumo_data.get('avg_speed', 0)
        
        # Normalize values
        state = np.array([
            vehicles_north / 20.0,  # Normalize to max 20 vehicles
            vehicles_south / 20.0,
            vehicles_east / 20.0,
            vehicles_west / 20.0,
            current_phase,
            elapsed_time / 60.0,  # Normalize to max 60 seconds
            queue_length / 50.0,  # Normalize to max 50 vehicles
            avg_speed / 30.0  # Normalize to max 30 m/s
        ], dtype=np.float32)
        
        return state
    
    def select_action(self, state: np.ndarray, training: bool = True) -> int:
        """
        Select action using epsilon-greedy policy
        
        Args:
            state: Current state
            training: Whether in training mode
            
        Returns:
            Selected action index
        """
        if training and random.random() < self.epsilon:
            return random.randrange(self.action_size)
        
        with torch.no_grad():
            state_tensor = torch.FloatTensor(state).unsqueeze(0)
            q_values = self.q_network(state_tensor)
            return q_values.argmax().item()
    
    def remember(self, state, action, reward, next_state, done):
        """Store experience in replay buffer"""
        self.memory.push(state, action, reward, next_state, done)
    
    def replay(self):
        """Train the network on a batch of experiences"""
        if len(self.memory) < self.batch_size:
            return 0.0
        
        # Sample batch from memory
        states, actions, rewards, next_states, dones = self.memory.sample(self.batch_size)
        
        # Convert to tensors
        states = torch.FloatTensor(states)
        actions = torch.LongTensor(actions)
        rewards = torch.FloatTensor(rewards)
        next_states = torch.FloatTensor(next_states)
        dones = torch.BoolTensor(dones)
        
        # Current Q values
        current_q_values = self.q_network(states).gather(1, actions.unsqueeze(1))
        
        # Next Q values from target network
        with torch.no_grad():
            next_q_values = self.target_network(next_states).max(1)[0]
            target_q_values = rewards + (self.gamma * next_q_values * ~dones)
        
        # Compute loss
        loss = F.mse_loss(current_q_values.squeeze(), target_q_values)
        
        # Optimize
        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()
        
        # Decay epsilon
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay
        
        return loss.item()
    
    def update_target_network(self):
        """Update target network with current network weights"""
        self.target_network.load_state_dict(self.q_network.state_dict())
    
    def save_model(self, filepath: str):
        """Save the trained model"""
        torch.save({
            'q_network_state_dict': self.q_network.state_dict(),
            'target_network_state_dict': self.target_network.state_dict(),
            'optimizer_state_dict': self.optimizer.state_dict(),
            'epsilon': self.epsilon,
            'training_metrics': self.training_metrics
        }, filepath)
        print(f"✅ Model saved to {filepath}")
    
    def load_model(self, filepath: str):
        """Load a trained model"""
        if os.path.exists(filepath):
            checkpoint = torch.load(filepath)
            self.q_network.load_state_dict(checkpoint['q_network_state_dict'])
            self.target_network.load_state_dict(checkpoint['target_network_state_dict'])
            self.optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
            self.epsilon = checkpoint.get('epsilon', self.epsilon_min)
            self.training_metrics = checkpoint.get('training_metrics', self.training_metrics)
            print(f"✅ Model loaded from {filepath}")
        else:
            print(f"❌ Model file not found: {filepath}")
    
    def get_action_description(self, action: int) -> str:
        """Get human-readable action description"""
        return self.action_map.get(action, "unknown_action")
    
    def get_training_stats(self) -> Dict:
        """Get current training statistics"""
        if not self.training_metrics['episode_rewards']:
            return {}
        
        return {
            'avg_reward': np.mean(self.training_metrics['episode_rewards'][-100:]),
            'avg_waiting_time': np.mean(self.training_metrics['episode_waiting_times'][-100:]),
            'avg_throughput': np.mean(self.training_metrics['episode_throughputs'][-100:]),
            'avg_loss': np.mean(self.training_metrics['episode_losses'][-100:]),
            'epsilon': self.epsilon,
            'memory_size': len(self.memory)
        }

class TrafficMetrics:
    """
    Calculate traffic performance metrics
    """
    
    @staticmethod
    def calculate_waiting_time(vehicles: Dict) -> float:
        """Calculate average waiting time"""
        if not vehicles:
            return 0.0
        
        total_waiting_time = sum(veh.get('waiting_time', 0) for veh in vehicles.values())
        return total_waiting_time / len(vehicles) if vehicles else 0.0
    
    @staticmethod
    def calculate_throughput(vehicles: Dict, time_window: float = 60.0) -> float:
        """Calculate vehicles per minute"""
        if not vehicles:
            return 0.0
        
        # Count vehicles that have passed through intersection
        passed_vehicles = sum(1 for veh in vehicles.values() if veh.get('passed_intersection', False))
        return passed_vehicles / (time_window / 60.0)
    
    @staticmethod
    def calculate_queue_length(vehicles: Dict) -> int:
        """Calculate total queue length"""
        return len([veh for veh in vehicles.values() if veh.get('speed', 0) < 1.0])
    
    @staticmethod
    def calculate_avg_speed(vehicles: Dict) -> float:
        """Calculate average vehicle speed"""
        if not vehicles:
            return 0.0
        
        speeds = [veh.get('speed', 0) for veh in vehicles.values()]
        return np.mean(speeds) if speeds else 0.0

def main():
    """Test the AI controller"""
    print("🧠 Testing DQN Traffic AI Controller")
    print("=" * 50)
    
    # Create AI controller
    ai = TrafficSignalController()
    
    # Test state extraction
    test_sumo_data = {
        'vehicles_north': 5,
        'vehicles_south': 3,
        'vehicles_east': 8,
        'vehicles_west': 2,
        'current_phase': 0,
        'elapsed_time': 30,
        'queue_length': 10,
        'avg_speed': 15
    }
    
    state = ai.get_state(test_sumo_data)
    print(f"✅ State extracted: {state}")
    
    # Test action selection
    action = ai.select_action(state)
    print(f"✅ Action selected: {action} - {ai.get_action_description(action)}")
    
    # Test metrics
    test_vehicles = {
        'veh1': {'waiting_time': 10, 'speed': 5, 'passed_intersection': True},
        'veh2': {'waiting_time': 15, 'speed': 0, 'passed_intersection': False},
        'veh3': {'waiting_time': 8, 'speed': 12, 'passed_intersection': True}
    }
    
    waiting_time = TrafficMetrics.calculate_waiting_time(test_vehicles)
    throughput = TrafficMetrics.calculate_throughput(test_vehicles)
    queue_length = TrafficMetrics.calculate_queue_length(test_vehicles)
    avg_speed = TrafficMetrics.calculate_avg_speed(test_vehicles)
    
    print(f"✅ Metrics calculated:")
    print(f"   Waiting time: {waiting_time:.2f}s")
    print(f"   Throughput: {throughput:.2f} veh/min")
    print(f"   Queue length: {queue_length}")
    print(f"   Avg speed: {avg_speed:.2f} m/s")
    
    print("\n🎉 AI Controller test completed successfully!")

if __name__ == "__main__":
    main()
