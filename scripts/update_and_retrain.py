#!/usr/bin/env python3
"""
Update game results and retrain models
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from agent import NFLPredictionAgent
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    """Update game results and retrain if necessary."""
    try:
        logger.info("Starting update and retrain process...")
        
        # Initialize agent
        agent = NFLPredictionAgent()
        
        # Update results and potentially retrain
        results = agent.update_results_and_retrain()
        
        if 'error' in results:
            logger.error(f"Update failed: {results['error']}")
            sys.exit(1)
        
        # Report results
        logger.info(f"Updated {results['updated_games']} game results")
        
        if results['retrained']:
            logger.info("Models were retrained with new data")
            if 'retrain_result' in results and 'error' not in results['retrain_result']:
                logger.info(f"Retrain accuracy: {results['retrain_result'].get('accuracy', 'N/A')}")
        else:
            logger.info("No retraining was necessary")
        
        # Show current performance
        summary = agent.get_performance_summary()
        if 'error' not in summary:
            logger.info(f"Current Performance:")
            logger.info(f"  Overall Accuracy: {summary['overall_accuracy']:.3f}")
            logger.info(f"  Total Predictions: {summary['total_predictions']}")
            logger.info(f"  Correct Predictions: {summary['correct_predictions']}")
            
    except Exception as e:
        logger.error(f"Error during update: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()