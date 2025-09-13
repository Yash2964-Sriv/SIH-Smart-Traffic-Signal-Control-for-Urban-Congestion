#!/usr/bin/env python3
"""
Test and verify the actual simulation quality
"""

import os
import subprocess
import xml.etree.ElementTree as ET

def test_simulation_files():
    """Test if all required files exist and are valid"""
    print("🔍 Testing simulation files...")
    
    files_to_check = [
        "real_traffic_output/professional_working_config.sumocfg",
        "real_traffic_output/professional_working_network.net.xml", 
        "real_traffic_output/professional_working_routes.rou.xml",
        "real_traffic_output/professional_visual_settings.xml"
    ]
    
    all_exist = True
    for file in files_to_check:
        if os.path.exists(file):
            print(f"✅ {file} - EXISTS")
        else:
            print(f"❌ {file} - MISSING")
            all_exist = False
    
    return all_exist

def test_simulation_runs():
    """Test if simulation actually runs without errors"""
    print("\n🚀 Testing simulation execution...")
    
    cmd = [
        "C:\\Program Files (x86)\\Eclipse\\Sumo\\bin\\sumo.exe",
        "-c", "professional_working_config.sumocfg"
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, cwd="real_traffic_output", timeout=30)
        if result.returncode == 0:
            print("✅ Simulation runs successfully")
            print(f"   Duration: {result.stdout.split('Duration: ')[1].split('s')[0] if 'Duration:' in result.stdout else 'Unknown'}")
            print(f"   Vehicles: {result.stdout.split('Inserted: ')[1].split()[0] if 'Inserted:' in result.stdout else 'Unknown'}")
            return True
        else:
            print(f"❌ Simulation failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Error running simulation: {e}")
        return False

def analyze_visual_settings():
    """Analyze the visual settings quality"""
    print("\n🎨 Analyzing visual settings...")
    
    try:
        tree = ET.parse("real_traffic_output/professional_visual_settings.xml")
        root = tree.getroot()
        
        features = {
            "scale": "1.0",
            "lighting": False,
            "shadows": False,
            "textures": False,
            "antialiasing": False,
            "vehicle_types": 0
        }
        
        # Check scale
        scale_elem = root.find("scale")
        if scale_elem is not None:
            features["scale"] = scale_elem.get("value", "1.0")
        
        # Check lighting
        lighting_elem = root.find("lighting")
        if lighting_elem is not None:
            enabled_elem = lighting_elem.find("enabled")
            if enabled_elem is not None:
                features["lighting"] = enabled_elem.get("value", "false").lower() == "true"
        
        # Check shadows
        shadows_elem = root.find("shadows")
        if shadows_elem is not None:
            enabled_elem = shadows_elem.find("enabled")
            if enabled_elem is not None:
                features["shadows"] = enabled_elem.get("value", "false").lower() == "true"
        
        # Check textures
        textures_elem = root.find("textures")
        if textures_elem is not None:
            enabled_elem = textures_elem.find("enabled")
            if enabled_elem is not None:
                features["textures"] = enabled_elem.get("value", "false").lower() == "true"
        
        # Check antialiasing
        antialiasing_elem = root.find("antialiasing")
        if antialiasing_elem is not None:
            enabled_elem = antialiasing_elem.find("enabled")
            if enabled_elem is not None:
                features["antialiasing"] = enabled_elem.get("value", "false").lower() == "true"
        
        # Count vehicle types from routes file
        try:
            routes_tree = ET.parse("real_traffic_output/professional_working_routes.rou.xml")
            routes_root = routes_tree.getroot()
            vehicle_types = routes_root.findall(".//vType")
            features["vehicle_types"] = len(vehicle_types)
        except:
            features["vehicle_types"] = 0
        
        print(f"   Scale: {features['scale']}x")
        print(f"   Lighting: {'✅' if features['lighting'] else '❌'}")
        print(f"   Shadows: {'✅' if features['shadows'] else '❌'}")
        print(f"   Textures: {'✅' if features['textures'] else '❌'}")
        print(f"   Antialiasing: {'✅' if features['antialiasing'] else '❌'}")
        print(f"   Vehicle Types: {features['vehicle_types']}")
        
        return features
        
    except Exception as e:
        print(f"❌ Error analyzing visual settings: {e}")
        return None

def analyze_network_complexity():
    """Analyze the network complexity"""
    print("\n🛣️ Analyzing network complexity...")
    
    try:
        tree = ET.parse("real_traffic_output/professional_working_network.net.xml")
        root = tree.getroot()
        
        edges = root.findall(".//edge")
        junctions = root.findall(".//junction")
        lanes = root.findall(".//lane")
        
        print(f"   Edges: {len(edges)}")
        print(f"   Junctions: {len(junctions)}")
        print(f"   Lanes: {len(lanes)}")
        
        return {
            "edges": len(edges),
            "junctions": len(junctions),
            "lanes": len(lanes)
        }
        
    except Exception as e:
        print(f"❌ Error analyzing network: {e}")
        return None

def calculate_quality_score(visual_features, network_complexity):
    """Calculate overall quality score"""
    print("\n📊 Calculating quality score...")
    
    score = 0
    max_score = 100
    
    # Visual quality (40 points)
    if visual_features:
        if float(visual_features["scale"]) >= 2.0:
            score += 10
        if visual_features["lighting"]:
            score += 10
        if visual_features["shadows"]:
            score += 10
        if visual_features["textures"]:
            score += 10
    
    # Vehicle variety (20 points)
    if visual_features and visual_features["vehicle_types"] >= 5:
        score += 20
    elif visual_features and visual_features["vehicle_types"] >= 3:
        score += 15
    elif visual_features and visual_features["vehicle_types"] >= 1:
        score += 10
    
    # Network complexity (20 points)
    if network_complexity:
        if network_complexity["edges"] >= 10:
            score += 10
        if network_complexity["junctions"] >= 5:
            score += 10
    
    # Simulation functionality (20 points)
    score += 20  # We know it runs successfully
    
    percentage = (score / max_score) * 100
    print(f"   Quality Score: {score}/{max_score} ({percentage:.1f}%)")
    
    return percentage

def main():
    """Main test function"""
    print("🎯 SIMULATION QUALITY TEST")
    print("=" * 50)
    
    # Test 1: Check files exist
    files_ok = test_simulation_files()
    
    # Test 2: Check simulation runs
    simulation_ok = test_simulation_runs()
    
    # Test 3: Analyze visual settings
    visual_features = analyze_visual_settings()
    
    # Test 4: Analyze network complexity
    network_complexity = analyze_network_complexity()
    
    # Test 5: Calculate quality score
    if files_ok and simulation_ok and visual_features and network_complexity:
        quality_score = calculate_quality_score(visual_features, network_complexity)
        
        print("\n🎉 TEST RESULTS:")
        print("=" * 30)
        print(f"✅ Files: {'PASS' if files_ok else 'FAIL'}")
        print(f"✅ Simulation: {'PASS' if simulation_ok else 'FAIL'}")
        print(f"✅ Visual Features: {'PASS' if visual_features else 'FAIL'}")
        print(f"✅ Network: {'PASS' if network_complexity else 'FAIL'}")
        print(f"📊 Quality Score: {quality_score:.1f}%")
        
        if quality_score >= 80:
            print("🎯 EXCELLENT QUALITY!")
        elif quality_score >= 60:
            print("✅ GOOD QUALITY")
        else:
            print("⚠️ NEEDS IMPROVEMENT")
    else:
        print("\n❌ TEST FAILED - Cannot calculate quality score")

if __name__ == "__main__":
    main()
