#!/usr/bin/env python3
"""
Examine pickle files to understand their structure
"""

import pickle
import os

def examine_pickle_files():
    """Examine all pickle files in ai_models folder"""
    models_folder = "ai_models"
    
    if not os.path.exists(models_folder):
        print("ai_models folder not found")
        return
    
    pkl_files = [f for f in os.listdir(models_folder) if f.endswith('.pkl')]
    
    print(f"Found {len(pkl_files)} pickle files:")
    print("=" * 50)
    
    for pkl_file in pkl_files[:5]:  # Check first 5 files
        file_path = os.path.join(models_folder, pkl_file)
        try:
            with open(file_path, 'rb') as f:
                data = pickle.load(f)
            
            print(f"\nFile: {pkl_file}")
            print(f"Type: {type(data)}")
            print(f"Value: {data}")
            
            if isinstance(data, dict):
                print(f"Keys: {list(data.keys())}")
                for key, value in data.items():
                    print(f"  {key}: {type(value)} - {value}")
            
        except Exception as e:
            print(f"Error loading {pkl_file}: {e}")

if __name__ == "__main__":
    examine_pickle_files()
