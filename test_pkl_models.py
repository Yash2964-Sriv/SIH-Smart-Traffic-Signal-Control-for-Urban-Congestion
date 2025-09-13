#!/usr/bin/env python3
"""
Test PKL Models - Select the best performing model
"""

import os
import pickle
import numpy as np
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class PKLModelTester:
    """Test and evaluate PKL models"""
    
    def __init__(self):
        self.ai_models_dir = Path("ai_models")
        self.models = []
        self.test_results = {}
    
    def load_models(self):
        """Load all available PKL models"""
        logger.info("Loading PKL models...")
        
        for pkl_file in self.ai_models_dir.glob("*.pkl"):
            try:
                with open(pkl_file, 'rb') as f:
                    model_data = pickle.load(f)
                
                model_info = {
                    'filename': pkl_file.name,
                    'data': model_data,
                    'type': 'DQL' if 'DQL' in pkl_file.name else 'DDQL',
                    'episode': self._extract_episode_number(pkl_file.name)
                }
                
                self.models.append(model_info)
                logger.info(f"Loaded: {pkl_file.name}")
                
            except Exception as e:
                logger.error(f"Failed to load {pkl_file.name}: {e}")
    
    def _extract_episode_number(self, filename):
        """Extract episode number from filename"""
        try:
            # Extract number from filename like "DQL_Replay_500.pkl"
            parts = filename.split('_')
            for part in parts:
                if part.replace('.pkl', '').isdigit():
                    return int(part.replace('.pkl', ''))
            return 0
        except:
            return 0
    
    def test_model_performance(self, model_info):
        """Test model performance with sample traffic data"""
        try:
            model_data = model_info['data']
            
            # Create sample traffic state
            sample_state = np.random.random(25)  # Match our state size
            
            # Test model prediction capability
            if 'q_network' in model_data:
                q_network = model_data['q_network']
                if 'weights' in q_network and 'bias' in q_network:
                    # Test forward pass
                    q_values = np.dot(sample_state, q_network['weights']) + q_network['bias']
                    prediction = np.argmax(q_values)
                    
                    # Calculate performance metrics
                    performance = {
                        'prediction_quality': float(np.max(q_values)),
                        'action_distribution': float(np.std(q_values)),
                        'model_completeness': 1.0 if len(q_network['weights']) > 0 else 0.0,
                        'episode_count': model_info['episode'],
                        'model_type': model_info['type']
                    }
                    
                    return performance
            
            return None
            
        except Exception as e:
            logger.error(f"Error testing model {model_info['filename']}: {e}")
            return None
    
    def evaluate_all_models(self):
        """Evaluate all loaded models"""
        logger.info("Evaluating all models...")
        
        for model_info in self.models:
            performance = self.test_model_performance(model_info)
            if performance:
                self.test_results[model_info['filename']] = performance
                logger.info(f"Model {model_info['filename']}: Quality={performance['prediction_quality']:.3f}, "
                           f"Episodes={performance['episode_count']}, Type={performance['model_type']}")
    
    def select_best_model(self):
        """Select the best performing model"""
        if not self.test_results:
            logger.error("No models evaluated successfully")
            return None
        
        # Score models based on multiple criteria
        scored_models = []
        
        for filename, performance in self.test_results.items():
            # Calculate composite score
            score = (
                performance['prediction_quality'] * 0.4 +  # Prediction quality
                performance['action_distribution'] * 0.2 +  # Action diversity
                performance['model_completeness'] * 0.2 +  # Model completeness
                min(performance['episode_count'] / 1000, 1.0) * 0.2  # Training episodes (capped)
            )
            
            scored_models.append((filename, score, performance))
        
        # Sort by score (highest first)
        scored_models.sort(key=lambda x: x[1], reverse=True)
        
        best_model = scored_models[0]
        logger.info(f"Best model selected: {best_model[0]} with score {best_model[1]:.3f}")
        
        return best_model[0], best_model[2]
    
    def run_evaluation(self):
        """Run complete model evaluation"""
        logger.info("Starting PKL model evaluation...")
        
        # Load models
        self.load_models()
        
        if not self.models:
            logger.error("No models found to evaluate")
            return None
        
        # Evaluate models
        self.evaluate_all_models()
        
        if not self.test_results:
            logger.error("No models evaluated successfully")
            return None
        
        # Select best model
        best_model_name, best_performance = self.select_best_model()
        
        logger.info(f"Evaluation complete. Best model: {best_model_name}")
        return best_model_name, best_performance

def main():
    """Main function"""
    print("PKL Model Evaluation System")
    print("=" * 30)
    
    tester = PKLModelTester()
    result = tester.run_evaluation()
    
    if result:
        best_model, performance = result
        print(f"\n✅ Best model selected: {best_model}")
        print(f"📊 Performance metrics:")
        print(f"   - Prediction Quality: {performance['prediction_quality']:.3f}")
        print(f"   - Action Distribution: {performance['action_distribution']:.3f}")
        print(f"   - Episode Count: {performance['episode_count']}")
        print(f"   - Model Type: {performance['model_type']}")
    else:
        print("❌ No suitable model found")

if __name__ == "__main__":
    main()
