#!/usr/bin/env python3
"""
Test Complete AI Traffic Control System
"""

import os
import sys
import time
import numpy as np
from dqn_traffic_ai import TrafficSignalController, TrafficMetrics
from sumo_ai_integration import SUMOAIIntegration
from real_time_ai_controller import RealTimeAIController

def test_ai_components():
    """Test individual AI components"""
    print("🧪 Testing AI Components")
    print("=" * 40)
    
    # Test 1: DQN AI Controller
    print("1. Testing DQN AI Controller...")
    try:
        ai = TrafficSignalController()
        
        # Test state extraction
        test_state = {
            'vehicles_north': 5,
            'vehicles_south': 3,
            'vehicles_east': 8,
            'vehicles_west': 2,
            'current_phase': 0,
            'elapsed_time': 30,
            'queue_length': 10,
            'avg_speed': 15
        }
        
        state_vector = ai.get_state(test_state)
        action = ai.select_action(state_vector)
        
        print(f"   ✅ State vector: {state_vector}")
        print(f"   ✅ Action selected: {action} - {ai.get_action_description(action)}")
        
    except Exception as e:
        print(f"   ❌ DQN AI Controller test failed: {e}")
        return False
    
    # Test 2: Traffic Metrics
    print("2. Testing Traffic Metrics...")
    try:
        test_vehicles = {
            'veh1': {'waiting_time': 10, 'speed': 5, 'passed_intersection': True},
            'veh2': {'waiting_time': 15, 'speed': 0, 'passed_intersection': False},
            'veh3': {'waiting_time': 8, 'speed': 12, 'passed_intersection': True}
        }
        
        waiting_time = TrafficMetrics.calculate_waiting_time(test_vehicles)
        throughput = TrafficMetrics.calculate_throughput(test_vehicles)
        queue_length = TrafficMetrics.calculate_queue_length(test_vehicles)
        avg_speed = TrafficMetrics.calculate_avg_speed(test_vehicles)
        
        print(f"   ✅ Waiting time: {waiting_time:.2f}s")
        print(f"   ✅ Throughput: {throughput:.2f} veh/min")
        print(f"   ✅ Queue length: {queue_length}")
        print(f"   ✅ Avg speed: {avg_speed:.2f} m/s")
        
    except Exception as e:
        print(f"   ❌ Traffic Metrics test failed: {e}")
        return False
    
    # Test 3: SUMO Integration
    print("3. Testing SUMO Integration...")
    try:
        sumo_config = "real_traffic_output/professional_working_config.sumocfg"
        
        if not os.path.exists(sumo_config):
            print(f"   ⚠️ SUMO config not found: {sumo_config}")
            print("   Skipping SUMO integration test")
        else:
            sumo_ai = SUMOAIIntegration(sumo_config, ai_controller=ai)
            
            if sumo_ai.start_simulation():
                state = sumo_ai.get_traffic_state()
                print(f"   ✅ Traffic state extracted: {len(state)} fields")
                
                action = ai.select_action(ai.get_state(state))
                success = sumo_ai.execute_action(action)
                print(f"   ✅ Action executed: {success}")
                
                import traci
                traci.close()
            else:
                print("   ❌ Failed to start SUMO simulation")
                return False
        
    except Exception as e:
        print(f"   ❌ SUMO Integration test failed: {e}")
        return False
    
    print("✅ All AI components tested successfully!")
    return True

def test_training_pipeline():
    """Test training pipeline"""
    print("\n🎓 Testing Training Pipeline")
    print("=" * 40)
    
    try:
        # Create AI controller
        ai = TrafficSignalController()
        
        # Test training components
        print("1. Testing experience replay...")
        
        # Add some dummy experiences
        for i in range(100):
            state = np.random.random(8)
            action = np.random.randint(0, 4)
            reward = np.random.random()
            next_state = np.random.random(8)
            done = np.random.random() > 0.9
            
            ai.remember(state, action, reward, next_state, done)
        
        print(f"   ✅ Memory size: {len(ai.memory)}")
        
        # Test replay
        if len(ai.memory) >= ai.batch_size:
            loss = ai.replay()
            print(f"   ✅ Training loss: {loss:.4f}")
        
        # Test target network update
        ai.update_target_network()
        print("   ✅ Target network updated")
        
        # Test model saving/loading
        test_model_path = "ai_controller/test_model.pth"
        ai.save_model(test_model_path)
        
        new_ai = TrafficSignalController()
        new_ai.load_model(test_model_path)
        print("   ✅ Model save/load successful")
        
        # Clean up
        if os.path.exists(test_model_path):
            os.remove(test_model_path)
        
        print("✅ Training pipeline tested successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Training pipeline test failed: {e}")
        return False

def test_real_time_controller():
    """Test real-time controller"""
    print("\n🚦 Testing Real-Time Controller")
    print("=" * 40)
    
    try:
        sumo_config = "real_traffic_output/professional_working_config.sumocfg"
        
        if not os.path.exists(sumo_config):
            print(f"   ⚠️ SUMO config not found: {sumo_config}")
            print("   Skipping real-time controller test")
            return True
        
        # Create controller
        controller = RealTimeAIController(sumo_config, control_interval=1.0)
        
        # Test dashboard data
        dashboard_data = controller.get_dashboard_data()
        print(f"   ✅ Dashboard data: {len(dashboard_data)} fields")
        
        # Test performance data
        performance_data = controller.get_performance_data()
        print(f"   ✅ Performance data: {len(performance_data)} fields")
        
        print("✅ Real-time controller tested successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Real-time controller test failed: {e}")
        return False

def run_quick_training_demo():
    """Run a quick training demonstration"""
    print("\n🎬 Quick Training Demo")
    print("=" * 40)
    
    try:
        sumo_config = "real_traffic_output/professional_working_config.sumocfg"
        
        if not os.path.exists(sumo_config):
            print(f"   ⚠️ SUMO config not found: {sumo_config}")
            return False
        
        # Create AI controller
        ai = TrafficSignalController()
        
        # Create SUMO integration
        sumo_ai = SUMOAIIntegration(sumo_config, ai_controller=ai)
        
        print("   🚀 Running 5 training episodes...")
        
        # Run a few training episodes
        for episode in range(5):
            print(f"   📚 Episode {episode + 1}/5")
            
            metrics = sumo_ai.run_ai_episode(max_steps=100, training=True)
            
            print(f"      Reward: {metrics['total_reward']:.2f}, "
                  f"Vehicles: {metrics['total_vehicles_passed']}, "
                  f"Steps: {metrics['steps']}")
        
        print("✅ Quick training demo completed!")
        return True
        
    except Exception as e:
        print(f"❌ Quick training demo failed: {e}")
        return False

def main():
    """Main test function"""
    print("🧠 AI Traffic Control System Test")
    print("=" * 60)
    print("Testing: DQN AI + SUMO Integration + Real-time Control")
    print("=" * 60)
    
    # Test 1: AI Components
    components_ok = test_ai_components()
    
    # Test 2: Training Pipeline
    training_ok = test_training_pipeline()
    
    # Test 3: Real-time Controller
    realtime_ok = test_real_time_controller()
    
    # Test 4: Quick Training Demo
    demo_ok = run_quick_training_demo()
    
    # Summary
    print("\n📊 TEST RESULTS")
    print("=" * 30)
    print(f"✅ AI Components: {'PASS' if components_ok else 'FAIL'}")
    print(f"✅ Training Pipeline: {'PASS' if training_ok else 'FAIL'}")
    print(f"✅ Real-time Controller: {'PASS' if realtime_ok else 'FAIL'}")
    print(f"✅ Quick Training Demo: {'PASS' if demo_ok else 'FAIL'}")
    
    overall_success = components_ok and training_ok and realtime_ok and demo_ok
    
    if overall_success:
        print("\n🎉 ALL TESTS PASSED!")
        print("✅ AI Traffic Control System is ready!")
        print("\n🚀 Next steps:")
        print("   1. Run: python ai_controller/train_traffic_ai.py")
        print("   2. Run: python ai_controller/real_time_ai_controller.py")
        print("   3. Integrate with dashboard for visualization")
    else:
        print("\n⚠️ SOME TESTS FAILED")
        print("❌ Please check the errors above")
    
    return overall_success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

