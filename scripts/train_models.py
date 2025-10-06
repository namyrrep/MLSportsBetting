#!/usr/bin/env python3
"""
Train ML models for NFL game prediction
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from agent import NFLPredictionAgent
import logging
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    """Train all ML models using stored data."""
    try:
        logger.info("Starting model training...")
        
        # Initialize agent
        agent = NFLPredictionAgent()
        
        # Train models
        results = agent.train_models()
        
        if 'error' in results:
            logger.error(f"Training failed: {results['error']}")
            sys.exit(1)
        
        # Print results
        logger.info("Training completed successfully!")
        logger.info(f"Models trained: {results['models_trained']}")
        logger.info(f"Training samples: {results['training_samples']}")
        logger.info(f"Features used: {results['features_used']}")
        
        # Print individual model performance
        for model_name, metrics in results['results'].items():
            if 'error' not in metrics:
                logger.info(f"{model_name}: Accuracy = {metrics['accuracy']:.4f}")
            else:
                logger.warning(f"{model_name}: Error - {metrics['error']}")
                
    except Exception as e:
        logger.error(f"Error during model training: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()