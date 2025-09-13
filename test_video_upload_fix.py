#!/usr/bin/env python3
"""
Test script to verify video upload fix
"""

import requests
import os

def test_video_upload():
    """Test video upload functionality"""
    print("🧪 Testing Video Upload Fix...")
    
    # Check if sample video exists
    sample_video = "Traffic_videos/stock-footage-drone-shot-way-intersection.webm"
    if not os.path.exists(sample_video):
        print(f"❌ Sample video not found: {sample_video}")
        return False
    
    try:
        with open(sample_video, 'rb') as f:
            files = {'video': f}
            response = requests.post(
                "http://localhost:5000/api/upload-video",
                files=files,
                timeout=30
            )
        
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                print("✅ Video upload working correctly")
                print(f"   📁 File: {result.get('filename')}")
                print(f"   📍 Path: {result.get('filepath')}")
                return True
            else:
                print(f"❌ Upload failed: {result.get('message')}")
                return False
        else:
            print(f"❌ Upload error: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Upload test failed: {e}")
        return False

def test_live_simulation():
    """Test live simulation functionality"""
    print("\n🎮 Testing Live Simulation...")
    
    try:
        data = {"video_path": "Traffic_videos/stock-footage-drone-shot-way-intersection.webm"}
        response = requests.post(
            "http://localhost:5000/api/start-live-simulation",
            json=data,
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                print("✅ Live simulation working correctly")
                print(f"   🎬 Video: {result.get('video_path')}")
                print(f"   🆔 Simulation ID: {result.get('simulation_id')}")
                return True
            else:
                print(f"❌ Simulation failed: {result.get('message')}")
                return False
        else:
            print(f"❌ Simulation error: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Simulation test failed: {e}")
        return False

def test_live_metrics():
    """Test live metrics functionality"""
    print("\n📊 Testing Live Metrics...")
    
    try:
        response = requests.get("http://localhost:5000/api/live-metrics", timeout=5)
        if response.status_code == 200:
            metrics = response.json()
            print("✅ Live metrics working correctly")
            
            if metrics.get("simulation_running"):
                print("   📊 Simulation is running")
                print(f"   ⏱️  Duration: {metrics.get('duration', 'Unknown')}")
            else:
                print("   📊 No simulation currently running")
            
            return True
        else:
            print(f"❌ Metrics error: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Metrics test failed: {e}")
        return False

def main():
    """Main test function"""
    print("🔧 TESTING VIDEO UPLOAD FIX")
    print("=" * 50)
    
    # Test all endpoints
    upload_ok = test_video_upload()
    simulation_ok = test_live_simulation()
    metrics_ok = test_live_metrics()
    
    print("\n📋 TEST RESULTS:")
    print("=" * 30)
    print(f"Video Upload: {'✅ PASS' if upload_ok else '❌ FAIL'}")
    print(f"Live Simulation: {'✅ PASS' if simulation_ok else '❌ FAIL'}")
    print(f"Live Metrics: {'✅ PASS' if metrics_ok else '❌ FAIL'}")
    
    if upload_ok and simulation_ok and metrics_ok:
        print("\n🎉 ALL TESTS PASSED!")
        print("The video upload fix is working correctly!")
        print("\n🌐 Now you can:")
        print("   1. Go to http://localhost:3000")
        print("   2. Click 'Live Video Simulation'")
        print("   3. Upload a video and start simulation!")
    else:
        print("\n❌ Some tests failed. Please check the backend API.")
    
    return upload_ok and simulation_ok and metrics_ok

if __name__ == "__main__":
    main()


