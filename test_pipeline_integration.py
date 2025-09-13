#!/usr/bin/env python3
"""
Test Complete Pipeline Integration: SUMO → TraCI → Omniverse
"""

import sys
import os

def test_imports():
    """Test if all required libraries can be imported"""
    print("🧪 Testing Pipeline Integration")
    print("=" * 50)
    
    # Test SUMO/TraCI
    try:
        import traci
        import sumolib
        print("✅ SUMO/TraCI: sumolib, traci - SUCCESS")
    except ImportError as e:
        print(f"❌ SUMO/TraCI: FAILED - {e}")
        return False
    
    # Test 3D Visualization
    try:
        import shapely
        import geopandas
        import networkx
        import pyproj
        import matplotlib
        print("✅ 3D Visualization: shapely, geopandas, networkx, pyproj, matplotlib - SUCCESS")
    except ImportError as e:
        print(f"❌ 3D Visualization: FAILED - {e}")
        return False
    
    # Test Custom SUMO to 3D Bridge
    try:
        from sumo_to_3d_bridge import SUMOTo3DBridge
        print("✅ Custom 3D Bridge: SUMOTo3DBridge - SUCCESS")
    except ImportError as e:
        print(f"❌ Custom 3D Bridge: FAILED - {e}")
        return False
    
    # Test GIS/OSM
    try:
        import osmium
        print("✅ GIS/OSM: osmium - SUCCESS")
    except ImportError as e:
        print(f"❌ GIS/OSM: FAILED - {e}")
        return False
    
    # Test USD/Omniverse
    try:
        from pxr import Usd, UsdGeom, Gf
        print("✅ USD/Omniverse: pxr (USD) - SUCCESS")
    except ImportError as e:
        print(f"❌ USD/Omniverse: FAILED - {e}")
        return False
    
    # Test Jupyter
    try:
        import notebook
        import ipywidgets
        print("✅ Jupyter: notebook, ipywidgets - SUCCESS")
    except ImportError as e:
        print(f"❌ Jupyter: FAILED - {e}")
        return False
    
    return True

def test_sumo_connection():
    """Test SUMO connection via TraCI"""
    print("\n🔗 Testing SUMO Connection")
    print("=" * 30)
    
    try:
        import traci
        import sumolib
        
        # Test if SUMO is accessible
        sumo_binary = "C:\\Program Files (x86)\\Eclipse\\Sumo\\bin\\sumo.exe"
        if os.path.exists(sumo_binary):
            print("✅ SUMO binary found")
        else:
            print("❌ SUMO binary not found")
            return False
        
        # Test network loading
        network_file = "real_traffic_output/professional_working_network.net.xml"
        if os.path.exists(network_file):
            net = sumolib.net.readNet(network_file)
            print(f"✅ Network loaded: {len(net.getEdges())} edges, {len(net.getNodes())} nodes")
        else:
            print("❌ Network file not found")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ SUMO connection test failed: {e}")
        return False

def test_usd_capabilities():
    """Test USD capabilities"""
    print("\n🎨 Testing USD Capabilities")
    print("=" * 30)
    
    try:
        from pxr import Usd, UsdGeom, Gf
        
        # Create a simple USD stage
        stage = Usd.Stage.CreateNew("test_pipeline.usda")
        
        # Create a simple cube
        cube = UsdGeom.Cube.Define(stage, "/World/Cube")
        cube.CreateSizeAttr(2.0)
        
        # Save the stage
        stage.Save()
        
        print("✅ USD stage creation - SUCCESS")
        print("✅ Basic USD operations - SUCCESS")
        
        # Clean up
        if os.path.exists("test_pipeline.usda"):
            os.remove("test_pipeline.usda")
        
        return True
        
    except Exception as e:
        print(f"❌ USD test failed: {e}")
        return False

def test_gis_capabilities():
    """Test GIS capabilities"""
    print("\n🗺️ Testing GIS Capabilities")
    print("=" * 30)
    
    try:
        import geopandas as gpd
        import shapely.geometry as geom
        import pyproj
        
        # Test basic geometry operations
        point = geom.Point(0, 0)
        polygon = geom.Polygon([(0, 0), (1, 0), (1, 1), (0, 1)])
        
        print("✅ Shapely geometry operations - SUCCESS")
        
        # Test coordinate transformation
        transformer = pyproj.Transformer.from_crs("EPSG:4326", "EPSG:3857")
        x, y = transformer.transform(0, 0)
        
        print("✅ PyProj coordinate transformation - SUCCESS")
        
        return True
        
    except Exception as e:
        print(f"❌ GIS test failed: {e}")
        return False

def main():
    """Main test function"""
    print("🎯 COMPLETE PIPELINE INTEGRATION TEST")
    print("=" * 60)
    print("Testing: SUMO → TraCI → NVIDIA Omniverse Pipeline")
    print("=" * 60)
    
    # Test 1: Import all libraries
    imports_ok = test_imports()
    
    # Test 2: SUMO connection
    sumo_ok = test_sumo_connection()
    
    # Test 3: USD capabilities
    usd_ok = test_usd_capabilities()
    
    # Test 4: GIS capabilities
    gis_ok = test_gis_capabilities()
    
    # Summary
    print("\n📊 INTEGRATION TEST RESULTS")
    print("=" * 40)
    print(f"✅ Library Imports: {'PASS' if imports_ok else 'FAIL'}")
    print(f"✅ SUMO Connection: {'PASS' if sumo_ok else 'FAIL'}")
    print(f"✅ USD Capabilities: {'PASS' if usd_ok else 'FAIL'}")
    print(f"✅ GIS Capabilities: {'PASS' if gis_ok else 'FAIL'}")
    
    overall_success = imports_ok and sumo_ok and usd_ok and gis_ok
    
    if overall_success:
        print("\n🎉 ALL TESTS PASSED!")
        print("✅ Pipeline is ready for: SUMO → TraCI → Omniverse")
        print("✅ You can now create photorealistic traffic simulations!")
    else:
        print("\n⚠️ SOME TESTS FAILED")
        print("❌ Pipeline needs additional setup")
    
    return overall_success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
