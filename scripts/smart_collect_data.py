#!/usr/bin/env python3
"""
Smart data collection that only fetches missing games
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
    """Smart data collection that avoids redundant API calls."""
    parser = argparse.ArgumentParser(description='Smart NFL game data collection')
    parser.add_argument('--start-year', type=int, default=2018, 
                       help='Start year for data collection (default: 2018)')
    parser.add_argument('--end-year', type=int, default=2024,
                       help='End year for data collection (default: 2024)')
    parser.add_argument('--update-existing', action='store_true',
                       help='Update games that already exist but may have new results')
    parser.add_argument('--show-coverage', action='store_true',
                       help='Show current data coverage before collecting')
    
    args = parser.parse_args()
    
    try:
        # Initialize agent
        agent = NFLPredictionAgent()
        
        # Show current coverage if requested
        if args.show_coverage:
            coverage = agent.db.get_data_coverage_summary()
            print("\n📊 Current Data Coverage:")
            print("=" * 40)
            print(f"Total Games: {coverage['total_games']}")
            print(f"Completed Games: {coverage['completed_games']}")
            
            if coverage['total_games'] > 0:
                completion_rate = coverage['completed_games'] / coverage['total_games']
                print(f"Completion Rate: {completion_rate:.1%}")
            
            if coverage['seasons']:
                print(f"Seasons: {coverage['earliest_season']}-{coverage['latest_season']}")
                print("\nBy Season:")
                for season_data in coverage['seasons']:
                    print(f"  {season_data['season']}: {season_data['completed_games']}/{season_data['total_games']} "
                          f"({season_data['completion_rate']:.1%})")
            print()
        
        # Collect data intelligently
        logger.info(f"Starting smart data collection from {args.start_year} to {args.end_year}")
        logger.info("This will skip games that already exist in the database")
        
        success = agent.collect_and_store_data(
            args.start_year, 
            args.end_year, 
            update_existing=args.update_existing
        )
        
        if success:
            # Show updated coverage
            coverage = agent.db.get_data_coverage_summary()
            print("\n✅ Smart Data Collection Completed!")
            print("=" * 40)
            print(f"Total Games in Database: {coverage['total_games']}")
            print(f"Completed Games: {coverage['completed_games']}")
            
            if coverage['total_games'] > 0:
                completion_rate = coverage['completed_games'] / coverage['total_games']
                print(f"Overall Completion Rate: {completion_rate:.1%}")
        else:
            logger.error("Smart data collection failed!")
            sys.exit(1)
            
    except Exception as e:
        logger.error(f"Error during smart data collection: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()