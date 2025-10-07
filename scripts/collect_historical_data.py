"""
Historical Data Expansion Script
Collects NFL game data from 2020-2024 seasons to expand training dataset.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from src.data_collector import DataCollector
from src.database import DatabaseManager
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def collect_historical_seasons():
    """Collect historical data from 2020-2024."""
    db = DatabaseManager()
    collector = DataCollector()
    
    # Seasons to collect (2020-2024)
    seasons = [2020, 2021, 2022, 2023, 2024]
    
    logger.info("="*70)
    logger.info("HISTORICAL DATA COLLECTION - EXPANDING TRAINING DATASET")
    logger.info("="*70)
    
    total_games_collected = 0
    
    for season in seasons:
        logger.info(f"\n{'='*70}")
        logger.info(f"Collecting {season} Season Data")
        logger.info(f"{'='*70}")
        
        try:
            # Collect full regular season (weeks 1-18)
            for week in range(1, 19):
                logger.info(f"\nProcessing {season} Week {week}...")
                
                games = collector.get_games_for_week(season, week)
                
                if games:
                    logger.info(f"Found {len(games)} games for {season} Week {week}")
                    
                    # Store games in database
                    for game in games:
                        success = db.insert_game(game)
                        if success:
                            total_games_collected += 1
                            logger.info(f"  ✓ Stored: {game['away_team']} @ {game['home_team']}")
                else:
                    logger.warning(f"No games found for {season} Week {week}")
            
            logger.info(f"\n✓ Completed {season} season - Total games so far: {total_games_collected}")
            
        except Exception as e:
            logger.error(f"Error collecting {season} season: {str(e)}")
            continue
    
    logger.info(f"\n{'='*70}")
    logger.info(f"COLLECTION COMPLETE")
    logger.info(f"{'='*70}")
    logger.info(f"Total historical games collected: {total_games_collected}")
    
    # Get database statistics
    try:
        all_games_df = db.get_games()
        completed_games_df = all_games_df[all_games_df['winner'].notna()]
        logger.info(f"Total completed games in database: {len(completed_games_df)}")
        
        # Count by season
        if 'season' in completed_games_df.columns:
            season_counts = completed_games_df['season'].value_counts().sort_index()
            logger.info("\nGames by season:")
            for season, count in season_counts.items():
                logger.info(f"  {season}: {count} games")
            
    except Exception as e:
        logger.error(f"Error getting database statistics: {str(e)}")
    
    return total_games_collected

if __name__ == "__main__":
    logger.info("Starting historical data collection...")
    logger.info("This will collect NFL game data from 2020-2024 seasons")
    logger.info("Estimated time: 10-15 minutes\n")
    
    try:
        total_games = collect_historical_seasons()
        logger.info(f"\n✓ SUCCESS! Collected {total_games} historical games")
        logger.info("Database is now ready for enhanced model training")
        
    except KeyboardInterrupt:
        logger.warning("\n⚠ Collection interrupted by user")
        logger.info("Partial data has been saved to database")
        
    except Exception as e:
        logger.error(f"\n✗ FAILED: {str(e)}")
        logger.error("Check logs for details")
