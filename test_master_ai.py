#!/usr/bin/env python3
"""
Test Script for Master AI Controller
Verifies basic functionality and training capabilities
"""

import os
import sys
import numpy as np
from master_ai_controller import MasterAIController

def test_initialization():
    """Test Master AI Controller initialization"""
    print("🧪 Test 1: Initialization")
    
    try:
        # Test default initialization
        master_ai = MasterAIController()
        assert master_ai is not None
        assert master_ai.q_network is not None
        assert master_ai.experience_buffer is not None
        print("  ✅ Default initialization successful")
        
        # Test custom configuration
        custom_config = {
            'learning_rate': 0.002,
            'epsilon': 0.15,
            'training_episodes': 5
        }
        master_ai_custom = MasterAIController(custom_config)
        assert master_ai_custom.config['learning_rate'] == 0.002
        assert master_ai_custom.config['epsilon'] == 0.15
        print("  ✅ Custom configuration successful")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Initialization failed: {e}")
        return False

def test_state_representation():
    """Test state representation functionality"""
    print("\n🧪 Test 2: State Representation")
    
    try:
        master_ai = MasterAIController()
        
        # Test state representation
        traffic_data = {
            'queue_lengths': {'I1': 5, 'I2': 10, 'I3': 3, 'I4': 8},
            'waiting_times': {'I1': 15, 'I2': 25, 'I3': 10, 'I4': 20},
            'vehicle_counts': {'north': 12, 'south': 8, 'east': 15, 'west': 10},
            'flow_rates': {'north': 200, 'south': 150, 'east': 180, 'west': 160},
            'current_phase': 1,
            'phase_duration': 30,
            'efficiency_scores': {'throughput': 85, 'waiting_time': 70, 'speed': 90}
        }
        
        state = master_ai.get_state_representation(traffic_data)
        
        # Verify state properties
        assert isinstance(state, np.ndarray)
        assert state.shape == (master_ai.q_network['state_size'],)
        assert not np.any(np.isnan(state))
        assert not np.any(np.isinf(state))
        
        print(f"  ✅ State representation successful")
        print(f"     State shape: {state.shape}")
        print(f"     State range: [{state.min():.3f}, {state.max():.3f}]")
        
        return True
        
    except Exception as e:
        print(f"  ❌ State representation failed: {e}")
        return False

def test_action_selection():
    """Test action selection functionality"""
    print("\n🧪 Test 3: Action Selection")
    
    try:
        master_ai = MasterAIController()
        
        # Test state representation
        traffic_data = {
            'queue_lengths': {'I1': 5, 'I2': 10, 'I3': 3, 'I4': 8},
            'waiting_times': {'I1': 15, 'I2': 25, 'I3': 10, 'I4': 20},
            'vehicle_counts': {'north': 12, 'south': 8, 'east': 15, 'west': 10},
            'flow_rates': {'north': 200, 'south': 150, 'east': 180, 'west': 160},
            'current_phase': 1,
            'phase_duration': 30,
            'efficiency_scores': {'throughput': 85, 'waiting_time': 70, 'speed': 90}
        }
        
        state = master_ai.get_state_representation(traffic_data)
        
        # Test action selection
        action = master_ai.select_action(state, training=True)
        
        # Verify action properties
        assert isinstance(action, int)
        assert 0 <= action < master_ai.q_network['action_size']
        
        print(f"  ✅ Action selection successful")
        print(f"     Selected action: {action}")
        
        # Test multiple actions
        actions = [master_ai.select_action(state, training=True) for _ in range(10)]
        unique_actions = set(actions)
        print(f"     Action diversity: {len(unique_actions)} unique actions out of 10")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Action selection failed: {e}")
        return False

def test_action_execution():
    """Test action execution functionality"""
    print("\n🧪 Test 4: Action Execution")
    
    try:
        master_ai = MasterAIController()
        
        # Test traffic data
        traffic_data = {
            'queue_lengths': {'I1': 5, 'I2': 10, 'I3': 3, 'I4': 8},
            'waiting_times': {'I1': 15, 'I2': 25, 'I3': 10, 'I4': 20},
            'vehicle_counts': {'north': 12, 'south': 8, 'east': 15, 'west': 10},
            'flow_rates': {'north': 200, 'south': 150, 'east': 180, 'west': 160},
            'current_phase': 1,
            'phase_duration': 30,
            'efficiency_scores': {'throughput': 85, 'waiting_time': 70, 'speed': 90}
        }
        
        # Test all actions
        for action in range(master_ai.q_network['action_size']):
            result = master_ai.execute_action(action, traffic_data)
            
            # Verify result properties
            assert isinstance(result, dict)
            assert 'action_taken' in result
            assert 'success' in result
            assert 'reward' in result
            assert 'new_state' in result
            assert 'traffic_changes' in result
            
            assert result['action_taken'] == action
            assert isinstance(result['success'], bool)
            assert isinstance(result['reward'], (int, float))
            assert isinstance(result['new_state'], dict)
            assert isinstance(result['traffic_changes'], dict)
        
        print(f"  ✅ Action execution successful")
        print(f"     Tested {master_ai.q_network['action_size']} actions")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Action execution failed: {e}")
        return False

def test_experience_storage():
    """Test experience storage functionality"""
    print("\n🧪 Test 5: Experience Storage")
    
    try:
        master_ai = MasterAIController()
        
        # Create test experience
        state = np.random.randn(master_ai.q_network['state_size'])
        action = 0
        reward = 10.5
        next_state = np.random.randn(master_ai.q_network['state_size'])
        done = False
        
        # Store experience
        master_ai.store_experience(state, action, reward, next_state, done)
        
        # Verify storage
        assert len(master_ai.experience_buffer) == 1
        
        stored_experience = master_ai.experience_buffer[0]
        assert np.array_equal(stored_experience['state'], state)
        assert stored_experience['action'] == action
        assert stored_experience['reward'] == reward
        assert np.array_equal(stored_experience['next_state'], next_state)
        assert stored_experience['done'] == done
        
        print(f"  ✅ Experience storage successful")
        print(f"     Buffer size: {len(master_ai.experience_buffer)}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Experience storage failed: {e}")
        return False

def test_model_training():
    """Test model training functionality"""
    print("\n🧪 Test 6: Model Training")
    
    try:
        master_ai = MasterAIController()
        
        # Add some experiences to buffer
        for _ in range(50):  # Add more than batch_size
            state = np.random.randn(master_ai.q_network['state_size'])
            action = np.random.randint(0, master_ai.q_network['action_size'])
            reward = np.random.randn()
            next_state = np.random.randn(master_ai.q_network['state_size'])
            done = np.random.choice([True, False])
            
            master_ai.store_experience(state, action, reward, next_state, done)
        
        # Test training
        initial_weights = master_ai.q_network['weights'].copy()
        master_ai.train_model()
        
        # Verify weights changed (indicating training occurred)
        weights_changed = not np.array_equal(initial_weights, master_ai.q_network['weights'])
        
        print(f"  ✅ Model training successful")
        print(f"     Buffer size: {len(master_ai.experience_buffer)}")
        print(f"     Weights changed: {weights_changed}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Model training failed: {e}")
        return False

def test_model_save_load():
    """Test model save and load functionality"""
    print("\n🧪 Test 7: Model Save/Load")
    
    try:
        master_ai = MasterAIController()
        
        # Modify some values for testing
        master_ai.episode_count = 10
        master_ai.step_count = 100
        master_ai.performance_metrics['average_reward'] = 50.5
        
        # Save model
        test_model_path = "test_model.pkl"
        master_ai.save_model(test_model_path)
        
        # Verify file exists
        assert os.path.exists(test_model_path)
        
        # Create new instance and load model
        master_ai_new = MasterAIController()
        success = master_ai_new.load_model(test_model_path)
        
        # Verify load success
        assert success
        assert master_ai_new.episode_count == 10
        assert master_ai_new.step_count == 100
        assert master_ai_new.performance_metrics['average_reward'] == 50.5
        
        # Cleanup
        os.remove(test_model_path)
        
        print(f"  ✅ Model save/load successful")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Model save/load failed: {e}")
        return False

def test_training_status():
    """Test training status functionality"""
    print("\n🧪 Test 8: Training Status")
    
    try:
        master_ai = MasterAIController()
        
        # Get training status
        status = master_ai.get_training_status()
        
        # Verify status properties
        assert isinstance(status, dict)
        assert 'episode_count' in status
        assert 'step_count' in status
        assert 'epsilon' in status
        assert 'experience_buffer_size' in status
        assert 'average_reward' in status
        assert 'best_performance' in status
        assert 'convergence_rate' in status
        assert 'training_mode' in status
        assert 'evaluation_mode' in status
        
        print(f"  ✅ Training status successful")
        print(f"     Episodes: {status['episode_count']}")
        print(f"     Steps: {status['step_count']}")
        print(f"     Epsilon: {status['epsilon']:.3f}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Training status failed: {e}")
        return False

def run_all_tests():
    """Run all tests"""
    print("🧪 Master AI Controller - Test Suite")
    print("=" * 50)
    
    tests = [
        test_initialization,
        test_state_representation,
        test_action_selection,
        test_action_execution,
        test_experience_storage,
        test_model_training,
        test_model_save_load,
        test_training_status
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print(f"\n📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("✅ All tests passed! Master AI Controller is working correctly.")
        return True
    else:
        print(f"❌ {total - passed} tests failed. Please check the implementation.")
        return False

def main():
    """Main test function"""
    try:
        success = run_all_tests()
        
        if success:
            print("\n🎉 Master AI Controller is ready for training!")
            print("\n📚 Next Steps:")
            print("  1. Run: python example_master_ai_usage.py")
            print("  2. Run: python train_master_ai.py")
            print("  3. Train on your traffic videos")
            print("  4. Deploy for real-time control")
        else:
            print("\n❌ Some tests failed. Please fix the issues before proceeding.")
            sys.exit(1)
            
    except Exception as e:
        print(f"\n❌ Test suite failed with error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

