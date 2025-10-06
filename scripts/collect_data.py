#!/usr/bin/env python3
"""
Collect historical NFL game data and store in database
"""

import sys
import os
import argparse
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from agent import NFLPredictionAgent
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    """Collect historical data for specified years."""
    parser = argparse.ArgumentParser(description='Collect NFL game data')
    parser.add_argument('--start-year', type=int, default=2018, 
                       help='Start year for data collection (default: 2018)')
    parser.add_argument('--end-year', type=int, default=2024,
                       help='End year for data collection (default: 2024)')
    
    args = parser.parse_args()
    
    try:
        logger.info(f"Starting data collection from {args.start_year} to {args.end_year}")
        
        # Initialize agent
        agent = NFLPredictionAgent()
        
        # Collect and store data
        success = agent.collect_and_store_data(args.start_year, args.end_year)
        
        if success:
            logger.info("Data collection completed successfully!")
        else:
            logger.error("Data collection failed!")
            sys.exit(1)
            
    except Exception as e:
        logger.error(f"Error during data collection: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()