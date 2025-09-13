# Master AI Controller for Smart Traffic Simulator

## 🤖 Overview

The Master AI Controller is a comprehensive reinforcement learning system designed for intelligent traffic control. It integrates video analysis, SUMO simulation, and real-time decision making to optimize traffic flow through machine learning.

## 🚀 Key Features

### Reinforcement Learning Capabilities
- **Q-Learning Algorithm**: Deep Q-Network (DQN) for traffic control decisions
- **Experience Replay**: Efficient learning from past experiences
- **Epsilon-Greedy Policy**: Balanced exploration and exploitation
- **Target Network**: Stable learning with periodic updates

### Traffic Control Actions
1. **Change Phase**: Switch traffic light phases
2. **Extend Green Time**: Prolong green light duration
3. **Reduce Cycle Time**: Optimize overall cycle timing
4. **Coordinate Signals**: Synchronize multiple intersections
5. **Emergency Priority**: Handle emergency vehicles
6. **Adaptive Timing**: Dynamic timing based on conditions
7. **Queue Management**: Prevent queue overflow
8. **Flow Optimization**: Maximize traffic throughput

### Real-time Processing
- **Video Analysis**: Extract traffic patterns from real videos
- **State Representation**: Convert traffic data to RL state space
- **Action Execution**: Implement traffic control decisions
- **Performance Monitoring**: Track and optimize performance

## 📁 File Structure

```
master_ai_controller.py      # Main AI controller class
train_master_ai.py          # Training script
master_ai_config.json       # Configuration file
MASTER_AI_README.md         # This documentation
models/                     # Saved model files
data/                       # Experience buffer data
plots/                      # Training progress plots
reports/                    # Training reports
logs/                       # Training logs
```

## 🛠️ Installation

### Prerequisites
```bash
pip install numpy opencv-python matplotlib pickle-mixin
```

### Dependencies
- Python 3.7+
- NumPy
- OpenCV
- Matplotlib
- Pickle
- SUMO (for simulation)
- TraCI (for SUMO control)

## 🎯 Quick Start

### 1. Basic Training
```python
from master_ai_controller import MasterAIController

# Initialize with default config
master_ai = MasterAIController()

# Train for 100 episodes
for episode in range(100):
    episode_data = master_ai.start_training_episode()
    print(f"Episode {episode + 1}: Reward = {episode_data['total_reward']:.2f}")

# Save trained model
master_ai.save_model()
```

### 2. Using Training Script
```bash
# Train with default configuration
python train_master_ai.py

# Train with custom episodes
python train_master_ai.py --episodes 200

# Train and evaluate
python train_master_ai.py --episodes 100 --evaluate

# Run complete pipeline
python train_master_ai.py --complete
```

### 3. Custom Configuration
```python
# Load custom configuration
config = {
    'learning_rate': 0.002,
    'epsilon': 0.15,
    'training_episodes': 200,
    'video_path': 'path/to/your/video.mp4'
}

master_ai = MasterAIController(config)
```

## 🧠 Architecture

### State Representation
The AI observes a 20-dimensional state space:
- **Queue Lengths**: Normalized queue lengths for 4 junctions
- **Waiting Times**: Normalized waiting times for 4 junctions
- **Traffic Phases**: Current phase and duration
- **Time Context**: Hour of day and day of week
- **Flow Rates**: Traffic flow in 4 directions
- **Vehicle Counts**: Vehicle counts in 4 directions
- **Efficiency Scores**: Throughput, waiting time, speed metrics

### Action Space
8 discrete actions for traffic control:
- Phase changes
- Timing adjustments
- Signal coordination
- Emergency handling
- Queue management
- Flow optimization

### Reward Function
Multi-component reward system:
- **Queue Reduction**: Reward for shorter queues
- **Waiting Time Reduction**: Reward for shorter waits
- **Flow Rate Increase**: Reward for higher throughput
- **Action-Specific Rewards**: Different rewards for different actions
- **Penalties**: Negative rewards for poor performance

## 📊 Training Process

### 1. Episode Structure
```
Video Analysis → State Initialization → Action Selection → 
Action Execution → Reward Calculation → Experience Storage → 
Model Training → State Update
```

### 2. Learning Algorithm
- **Experience Replay**: Store and sample from past experiences
- **Target Network**: Use separate network for stable targets
- **Epsilon Decay**: Gradually reduce exploration over time
- **Gradient Descent**: Update Q-network weights

### 3. Performance Monitoring
- **Reward Tracking**: Monitor episode and average rewards
- **Convergence Analysis**: Track learning progress
- **Stability Metrics**: Measure performance consistency
- **Visualization**: Generate training progress plots

## 🔧 Configuration

### Key Parameters

#### Learning Parameters
```json
{
  "learning_rate": 0.001,        // Learning rate for Q-network
  "discount_factor": 0.95,       // Future reward discount
  "epsilon": 0.1,                // Initial exploration rate
  "epsilon_decay": 0.995,        // Exploration decay rate
  "epsilon_min": 0.01            // Minimum exploration rate
}
```

#### Training Parameters
```json
{
  "training_episodes": 100,      // Number of training episodes
  "batch_size": 32,              // Experience replay batch size
  "memory_size": 10000,          // Experience buffer size
  "target_update_frequency": 100 // Target network update frequency
}
```

#### State Normalization
```json
{
  "queue_lengths": {"normalization_factor": 100.0},
  "waiting_times": {"normalization_factor": 60.0},
  "flow_rates": {"normalization_factor": 1000.0},
  "vehicle_counts": {"normalization_factor": 50.0}
}
```

## 📈 Performance Metrics

### Training Metrics
- **Average Reward**: Mean reward over episodes
- **Best Performance**: Highest reward achieved
- **Convergence Rate**: Learning stability measure
- **Experience Buffer Size**: Available training data

### Evaluation Metrics
- **Efficiency Score**: Overall traffic efficiency (0-100)
- **Accuracy Score**: Action success rate (0-100)
- **Stability Score**: Performance consistency (0-100)
- **Adaptability Score**: Adaptation capability (0-100)

## 🎮 Usage Examples

### 1. Training on Custom Video
```python
# Initialize with custom video
config = {'video_path': 'my_traffic_video.mp4'}
master_ai = MasterAIController(config)

# Train for 50 episodes
for episode in range(50):
    episode_data = master_ai.start_training_episode()
    print(f"Episode {episode + 1}: {episode_data['total_reward']:.2f}")
```

### 2. Real-time Control
```python
# Load trained model
master_ai = MasterAIController()
master_ai.load_model()

# Start real-time control
master_ai.start_real_time_control('live_traffic_video.mp4')
```

### 3. Model Evaluation
```python
# Evaluate on test videos
test_videos = ['test1.mp4', 'test2.mp4', 'test3.mp4']
evaluation_results = master_ai.evaluate_model(test_videos[0])

print(f"Efficiency: {evaluation_results['efficiency_score']:.2f}")
print(f"Accuracy: {evaluation_results['accuracy_score']:.2f}")
```

## 🔍 Advanced Features

### 1. Custom Reward Functions
```python
def custom_reward_function(self, traffic_data, action_type):
    # Implement custom reward logic
    reward = 0
    # ... custom calculations
    return reward

# Override default reward function
master_ai._calculate_reward = custom_reward_function
```

### 2. Custom State Representation
```python
def custom_state_representation(self, traffic_data):
    # Implement custom state encoding
    state = np.zeros(self.q_network['state_size'])
    # ... custom state logic
    return state

# Override default state representation
master_ai.get_state_representation = custom_state_representation
```

### 3. Custom Action Execution
```python
def custom_action_execution(self, action, traffic_data):
    # Implement custom action logic
    # ... custom action implementation
    return action_results

# Override default action execution
master_ai.execute_action = custom_action_execution
```

## 📊 Monitoring and Visualization

### Training Progress
- **Real-time Logging**: Console and file logging
- **Progress Plots**: Automatic plot generation
- **Performance Tracking**: Comprehensive metrics
- **Model Checkpoints**: Periodic model saving

### Generated Plots
1. **Reward Over Episodes**: Learning progress
2. **Moving Average Rewards**: Smoothed learning curve
3. **Steps Per Episode**: Episode length analysis
4. **Reward Distribution**: Performance distribution

## 🚀 Deployment

### 1. Model Export
```python
# Save trained model
master_ai.save_model('production_model.pkl')

# Save experience buffer
master_ai.save_experience_buffer('production_experience.pkl')
```

### 2. Production Deployment
```python
# Load production model
master_ai = MasterAIController()
master_ai.load_model('production_model.pkl')

# Start production control
master_ai.start_real_time_control()
```

## 🔧 Troubleshooting

### Common Issues

#### 1. Low Performance
- **Increase Training Episodes**: Train for more episodes
- **Adjust Learning Rate**: Try different learning rates
- **Check Reward Function**: Ensure rewards are meaningful
- **Verify State Representation**: Check state encoding

#### 2. Convergence Problems
- **Reduce Learning Rate**: Lower learning rate for stability
- **Increase Target Update Frequency**: More stable targets
- **Check Experience Buffer**: Ensure sufficient experience data
- **Adjust Epsilon Decay**: Slower exploration decay

#### 3. Memory Issues
- **Reduce Memory Size**: Lower experience buffer size
- **Decrease Batch Size**: Smaller training batches
- **Clear Old Data**: Remove old experience data

### Debug Mode
```python
# Enable debug logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Run with debug output
master_ai = MasterAIController()
```

## 📚 API Reference

### MasterAIController Class

#### Methods
- `__init__(config)`: Initialize controller
- `start_training_episode(video_path)`: Run training episode
- `evaluate_model(test_video)`: Evaluate on test data
- `save_model(filepath)`: Save trained model
- `load_model(filepath)`: Load trained model
- `start_real_time_control(video_path)`: Start real-time control
- `get_training_status()`: Get current training status

#### Properties
- `q_network`: Q-network architecture
- `experience_buffer`: Experience replay buffer
- `performance_metrics`: Training performance data
- `config`: Configuration parameters

## 🤝 Contributing

### Development Setup
1. Fork the repository
2. Create feature branch
3. Implement changes
4. Add tests
5. Submit pull request

### Code Style
- Follow PEP 8 guidelines
- Add docstrings to functions
- Include type hints
- Write comprehensive tests

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- SUMO (Simulation of Urban Mobility)
- OpenCV for video processing
- NumPy for numerical computations
- Matplotlib for visualization

## 📞 Support

For questions and support:
- Create an issue on GitHub
- Check the documentation
- Review the examples
- Contact the development team

---

**Happy Training! 🚀🤖**

