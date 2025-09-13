#!/usr/bin/env python3
"""
Examine PKL file structure to understand the data format
"""

import pickle
import os
from pathlib import Path

def examine_pkl_file(filepath):
    """Examine the structure of a PKL file"""
    print(f"\nExamining: {filepath}")
    print("=" * 50)
    
    try:
        with open(filepath, 'rb') as f:
            data = pickle.load(f)
        
        print(f"Data type: {type(data)}")
        
        if isinstance(data, dict):
            print("Dictionary keys:")
            for key in data.keys():
                print(f"  - {key}: {type(data[key])}")
                if hasattr(data[key], 'shape'):
                    print(f"    Shape: {data[key].shape}")
                elif isinstance(data[key], (list, tuple)):
                    print(f"    Length: {len(data[key])}")
                elif isinstance(data[key], dict):
                    print(f"    Sub-keys: {list(data[key].keys())}")
        
        elif isinstance(data, (list, tuple)):
            print(f"Length: {len(data)}")
            if len(data) > 0:
                print(f"First element type: {type(data[0])}")
                if hasattr(data[0], 'shape'):
                    print(f"First element shape: {data[0].shape}")
        
        else:
            print(f"Value: {data}")
            
    except Exception as e:
        print(f"Error reading file: {e}")

def main():
    """Main function"""
    ai_models_dir = Path("ai_models")
    
    # Examine a few different models
    test_files = [
        "DDQL_Replay_600.pkl",  # Highest episode DDQL
        "DQL_Replay_500.pkl",   # Highest episode DQL
        "DDQL_Replay_1.pkl"     # First episode DDQL
    ]
    
    for filename in test_files:
        filepath = ai_models_dir / filename
        if filepath.exists():
            examine_pkl_file(filepath)
        else:
            print(f"File not found: {filepath}")

if __name__ == "__main__":
    main()
