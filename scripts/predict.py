#!/usr/bin/env python3
"""
Make predictions for NFL games
"""

import sys
import os
import argparse
import json
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from agent import NFLPredictionAgent
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    """Make predictions for specified week or current week."""
    parser = argparse.ArgumentParser(description='Predict NFL games')
    parser.add_argument('--season', type=int, help='Season year (e.g., 2024)')
    parser.add_argument('--week', type=int, help='Week number (1-18 for regular season)')
    parser.add_argument('--current', action='store_true', 
                       help='Predict current week games')
    parser.add_argument('--output', type=str, help='Output file for predictions (JSON)')
    
    args = parser.parse_args()
    
    try:
        # Initialize agent
        agent = NFLPredictionAgent()
        
        # Make predictions
        if args.current:
            logger.info("Making predictions for current week...")
            predictions = agent.predict_current_week()
        elif args.season and args.week:
            logger.info(f"Making predictions for {args.season} week {args.week}...")
            predictions = agent.predict_week(args.season, args.week)
        else:
            logger.error("Please specify either --current or both --season and --week")
            sys.exit(1)
        
        if not predictions:
            logger.warning("No predictions generated")
            return
        
        # Check for errors
        if len(predictions) == 1 and 'error' in predictions[0]:
            logger.error(f"Prediction error: {predictions[0]['error']}")
            sys.exit(1)
        
        # Display predictions
        logger.info(f"Generated {len(predictions)} predictions:")
        for pred in predictions:
            if 'error' not in pred:
                logger.info(f"{pred['away_team']} @ {pred['home_team']}: "
                          f"{pred['predicted_winner']} "
                          f"(Confidence: {pred['confidence_score']:.2f})")
        
        # Save to file if requested
        if args.output:
            with open(args.output, 'w') as f:
                json.dump(predictions, f, indent=2)
            logger.info(f"Predictions saved to {args.output}")
        
        # Get performance summary
        summary = agent.get_performance_summary()
        if 'error' not in summary:
            logger.info(f"Agent Performance - Overall Accuracy: {summary['overall_accuracy']:.2f}")
            logger.info(f"Total Predictions Made: {summary['total_predictions']}")
            
    except Exception as e:
        logger.error(f"Error making predictions: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()