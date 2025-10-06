#!/usr/bin/env python3
"""
Update completed game results and refresh predictions.
Run this daily or after games complete to update the "Last Week Results" tab.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from database import DatabaseManager
from data_collector import DataCollector
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main():
    """Update all incomplete games with final results."""
    try:
        db = DatabaseManager()
        collector = DataCollector()
        
        # Get incomplete games
        incomplete_games = db.get_incomplete_games()
        
        if incomplete_games.empty:
            logger.info("No incomplete games found - all results are up to date!")
            return
        
        logger.info(f"Found {len(incomplete_games)} games without results")
        
        # Update each incomplete game
        updated_count = 0
        for _, game in incomplete_games.iterrows():
            logger.info(f"Checking {game['away_team']} @ {game['home_team']} "
                       f"({game['season']} Week {game['week']})...")
            
            # Fetch fresh data for this week
            current_games = collector.get_games_for_week(game['season'], game['week'])
            
            # Find matching game
            for current_game in current_games:
                if current_game['game_id'] == game['game_id']:
                    if current_game['winner'] and current_game['winner'] != '':
                        # Game is complete - update it
                        if db.insert_game(current_game):
                            db.update_prediction_results(game['game_id'])
                            updated_count += 1
                            logger.info(f"  ✓ Updated: {current_game['winner']} won "
                                      f"{current_game['home_score']}-{current_game['away_score']}")
                    else:
                        logger.info(f"  ⏳ Still in progress or not started")
                    break
        
        logger.info(f"\n✅ Updated {updated_count} game(s) with final results")
        
        # Show stats
        stats = db.get_data_coverage_summary()
        logger.info(f"Database now has {stats['completed_games']}/{stats['total_games']} "
                   f"completed games")
        
    except Exception as e:
        logger.error(f"Error updating results: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
