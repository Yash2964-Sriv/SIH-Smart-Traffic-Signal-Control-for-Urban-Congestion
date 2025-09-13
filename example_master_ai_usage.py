#!/usr/bin/env python3
"""
Example Usage of Master AI Controller
Demonstrates how to train and use the Master AI for traffic control
"""

import os
import json
from master_ai_controller import MasterAIController

def example_basic_training():
    """Example: Basic training with default configuration"""
    print("🎯 Example 1: Basic Training")
    print("=" * 40)
    
    # Initialize Master AI Controller
    master_ai = MasterAIController()
    
    # Train for 10 episodes (for demonstration)
    print("Starting training...")
    for episode in range(10):
        episode_data = master_ai.start_training_episode()
        print(f"Episode {episode + 1}: Reward = {episode_data['total_reward']:.2f}")
    
    # Save the trained model
    master_ai.save_model()
    print("✅ Model saved successfully!")

def example_custom_configuration():
    """Example: Training with custom configuration"""
    print("\n🎯 Example 2: Custom Configuration")
    print("=" * 40)
    
    # Custom configuration
    custom_config = {
        'learning_rate': 0.002,
        'epsilon': 0.15,
        'training_episodes': 20,
        'video_path': "Traffic_videos/stock-footage-drone-shot-way-intersection.webm",
        'model_save_path': "models/custom_model.pkl"
    }
    
    # Initialize with custom config
    master_ai = MasterAIController(custom_config)
    
    # Train with custom settings
    print("Training with custom configuration...")
    for episode in range(20):
        episode_data = master_ai.start_training_episode()
        print(f"Episode {episode + 1}: Reward = {episode_data['total_reward']:.2f}")
    
    # Save custom model
    master_ai.save_model()
    print("✅ Custom model saved!")

def example_model_evaluation():
    """Example: Evaluating trained model"""
    print("\n🎯 Example 3: Model Evaluation")
    print("=" * 40)
    
    # Initialize and load trained model
    master_ai = MasterAIController()
    
    # Try to load existing model
    if master_ai.load_model():
        print("✅ Loaded existing model")
        
        # Evaluate on test video
        test_video = "Traffic_videos/stock-footage-drone-shot-way-intersection.webm"
        evaluation_results = master_ai.evaluate_model(test_video)
        
        print(f"📊 Evaluation Results:")
        print(f"  Total Reward: {evaluation_results['total_reward']:.2f}")
        print(f"  Efficiency Score: {evaluation_results['efficiency_score']:.2f}")
        print(f"  Accuracy Score: {evaluation_results['accuracy_score']:.2f}")
        print(f"  Stability Score: {evaluation_results['stability_score']:.2f}")
    else:
        print("❌ No trained model found. Please train first.")

def example_training_status():
    """Example: Checking training status"""
    print("\n🎯 Example 4: Training Status")
    print("=" * 40)
    
    # Initialize controller
    master_ai = MasterAIController()
    
    # Get training status
    status = master_ai.get_training_status()
    
    print(f"📊 Training Status:")
    print(f"  Episodes: {status['episode_count']}")
    print(f"  Steps: {status['step_count']}")
    print(f"  Epsilon: {status['epsilon']:.3f}")
    print(f"  Experience Buffer: {status['experience_buffer_size']}")
    print(f"  Average Reward: {status['average_reward']:.2f}")
    print(f"  Best Performance: {status['best_performance']:.2f}")
    print(f"  Convergence Rate: {status['convergence_rate']:.2f}")

def example_custom_reward_function():
    """Example: Custom reward function"""
    print("\n🎯 Example 5: Custom Reward Function")
    print("=" * 40)
    
    # Initialize controller
    master_ai = MasterAIController()
    
    # Define custom reward function
    def custom_reward(traffic_data, action_type):
        """Custom reward function that emphasizes efficiency"""
        reward = 0
        
        # Base reward from queue lengths
        queue_lengths = traffic_data.get('queue_lengths', {})
        avg_queue = sum(queue_lengths.values()) / len(queue_lengths) if queue_lengths else 0
        reward += max(0, 20 - avg_queue)  # Higher reward for shorter queues
        
        # Efficiency bonus
        if action_type in ['coordinate_signals', 'optimize_flow']:
            reward += 10  # Bonus for efficiency actions
        
        return reward
    
    # Override default reward function
    master_ai._calculate_reward = custom_reward
    
    print("✅ Custom reward function applied")
    print("Training with custom rewards...")
    
    # Train with custom reward function
    for episode in range(5):
        episode_data = master_ai.start_training_episode()
        print(f"Episode {episode + 1}: Reward = {episode_data['total_reward']:.2f}")

def example_training_report():
    """Example: Generating training report"""
    print("\n🎯 Example 6: Training Report")
    print("=" * 40)
    
    # Initialize controller
    master_ai = MasterAIController()
    
    # Generate training report
    report = master_ai.generate_training_report()
    
    print(f"📋 Training Report:")
    print(f"  Total Episodes: {report['training_summary']['total_episodes']}")
    print(f"  Total Steps: {report['training_summary']['total_steps']}")
    print(f"  Current Epsilon: {report['training_summary']['final_performance']['epsilon']:.3f}")
    print(f"  Experience Buffer: {report['training_summary']['final_performance']['experience_buffer_size']}")
    
    print(f"\n💡 Recommendations:")
    for rec in report['recommendations']:
        print(f"  • {rec}")

def example_real_time_control():
    """Example: Real-time control (simulation)"""
    print("\n🎯 Example 7: Real-time Control")
    print("=" * 40)
    
    # Initialize controller
    master_ai = MasterAIController()
    
    # Load trained model if available
    if master_ai.load_model():
        print("✅ Loaded trained model")
        print("🚦 Starting real-time control simulation...")
        print("   (This would normally run indefinitely)")
        print("   Press Ctrl+C to stop")
        
        # Note: In real implementation, this would run continuously
        # master_ai.start_real_time_control()
        print("   Real-time control would start here...")
    else:
        print("❌ No trained model found. Please train first.")

def main():
    """Run all examples"""
    print("🤖 Master AI Controller - Usage Examples")
    print("=" * 60)
    
    # Create necessary directories
    os.makedirs('models', exist_ok=True)
    os.makedirs('data', exist_ok=True)
    
    try:
        # Run examples
        example_basic_training()
        example_custom_configuration()
        example_model_evaluation()
        example_training_status()
        example_custom_reward_function()
        example_training_report()
        example_real_time_control()
        
        print("\n✅ All examples completed successfully!")
        print("\n📚 Next Steps:")
        print("  1. Train for more episodes for better performance")
        print("  2. Experiment with different configurations")
        print("  3. Try custom reward functions")
        print("  4. Evaluate on different traffic videos")
        print("  5. Deploy for real-time control")
        
    except Exception as e:
        print(f"\n❌ Error running examples: {e}")
        print("Please check your setup and try again.")

if __name__ == "__main__":
    main()

