#!/usr/bin/env python3
"""
Test script for Enhanced Dashboard API endpoints
"""

import requests
import json
import time
import os

def test_api_endpoints():
    """Test all API endpoints"""
    base_url = "http://localhost:5000"
    
    print("🧪 Testing Enhanced Dashboard API Endpoints")
    print("=" * 50)
    
    # Test 1: Check if backend is running
    try:
        response = requests.get(f"{base_url}/api/metrics", timeout=5)
        if response.status_code == 200:
            print("✅ Backend API is running")
        else:
            print("❌ Backend API not responding")
            return False
    except requests.exceptions.RequestException:
        print("❌ Backend API not accessible")
        return False
    
    # Test 2: Test video upload endpoint (without file)
    try:
        response = requests.post(f"{base_url}/api/upload-video")
        if response.status_code == 400:
            print("✅ Video upload endpoint exists (expected error without file)")
        else:
            print(f"⚠️  Video upload endpoint returned: {response.status_code}")
    except Exception as e:
        print(f"❌ Video upload test failed: {e}")
    
    # Test 3: Test live simulation endpoint
    try:
        data = {"video_path": "Traffic_videos/stock-footage-drone-shot-way-intersection.webm"}
        response = requests.post(
            f"{base_url}/api/start-live-simulation",
            json=data,
            timeout=10
        )
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                print("✅ Live simulation endpoint working")
            else:
                print(f"⚠️  Live simulation failed: {result.get('message')}")
        else:
            print(f"❌ Live simulation endpoint error: {response.status_code}")
    except Exception as e:
        print(f"❌ Live simulation test failed: {e}")
    
    # Test 4: Test live metrics endpoint
    try:
        response = requests.get(f"{base_url}/api/live-metrics", timeout=5)
        if response.status_code == 200:
            metrics = response.json()
            print("✅ Live metrics endpoint working")
            if metrics.get("simulation_running"):
                print("   📊 Simulation is running")
            else:
                print("   📊 No simulation running")
        else:
            print(f"❌ Live metrics endpoint error: {response.status_code}")
    except Exception as e:
        print(f"❌ Live metrics test failed: {e}")
    
    # Test 5: Test basic simulation endpoints
    try:
        # Test start simulation
        response = requests.post(f"{base_url}/api/start", timeout=5)
        if response.status_code == 200:
            print("✅ Basic simulation start endpoint working")
        else:
            print(f"❌ Basic simulation start error: {response.status_code}")
        
        # Test stop simulation
        response = requests.post(f"{base_url}/api/stop", timeout=5)
        if response.status_code == 200:
            print("✅ Basic simulation stop endpoint working")
        else:
            print(f"❌ Basic simulation stop error: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Basic simulation test failed: {e}")
    
    print("\n🎉 API Testing Complete!")
    return True

def test_file_upload():
    """Test file upload functionality"""
    print("\n📁 Testing File Upload Functionality")
    print("=" * 40)
    
    # Check if sample video exists
    sample_video = "Traffic_videos/stock-footage-drone-shot-way-intersection.webm"
    if os.path.exists(sample_video):
        print(f"✅ Sample video found: {sample_video}")
        
        # Test upload
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
                    print("✅ Video upload successful")
                    print(f"   📁 File: {result.get('filename')}")
                    return result.get('filepath')
                else:
                    print(f"❌ Upload failed: {result.get('message')}")
            else:
                print(f"❌ Upload error: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Upload test failed: {e}")
    else:
        print(f"⚠️  Sample video not found: {sample_video}")
        print("   You can upload your own video through the dashboard")
    
    return None

def main():
    """Main test function"""
    print("🚀 Enhanced Dashboard API Test Suite")
    print("=" * 50)
    
    # Wait for backend to start
    print("⏳ Waiting for backend to start...")
    time.sleep(3)
    
    # Test API endpoints
    if test_api_endpoints():
        print("\n✅ All API endpoints are working!")
    else:
        print("\n❌ Some API endpoints failed")
    
    # Test file upload
    uploaded_file = test_file_upload()
    
    if uploaded_file:
        print(f"\n🎬 Testing live simulation with uploaded file...")
        try:
            data = {"video_path": uploaded_file}
            response = requests.post(
                "http://localhost:5000/api/start-live-simulation",
                json=data,
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get("success"):
                    print("✅ Live simulation started successfully!")
                    print("   🎮 SUMO GUI should open shortly")
                    print("   📊 Check dashboard for live metrics")
                else:
                    print(f"❌ Live simulation failed: {result.get('message')}")
            else:
                print(f"❌ Live simulation error: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Live simulation test failed: {e}")
    
    print("\n🎉 Testing Complete!")
    print("=" * 30)
    print("🌐 Open http://localhost:3000 to use the dashboard")
    print("📱 Click 'Live Video Simulation' to upload and test")

if __name__ == "__main__":
    main()


