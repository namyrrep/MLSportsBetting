"""Populate predictions for 2025 Week 5."""

import logging
from src.data_collector import DataCollector
from src.database import DatabaseManager
from src.agent import NFLPredictionAgent

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    # Initialize components
    collector = DataCollector()
    db_manager = DatabaseManager()
    agent = NFLPredictionAgent()
    
    season = 2025
    week = 5
    
    logger.info(f"Fetching games for {season} Week {week}...")
    games = collector.get_games_for_week(season, week)
    
    if not games:
        logger.warning(f"No games found for {season} Week {week}")
        return
    
    logger.info(f"Found {len(games)} games. Inserting into database...")
    for game in games:
        db_manager.insert_game(game)
    
    logger.info(f"Generating predictions for {season} Week {week}...")
    agent.predict_week(season, week)
    
    logger.info("✅ Complete! Week 5 predictions are ready.")

if __name__ == "__main__":
    main()
