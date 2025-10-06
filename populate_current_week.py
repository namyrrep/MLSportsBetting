#!/usr/bin/env python3
"""Populate current week with games and predictions."""

import sys
sys.path.insert(0, 'src')

from database import DatabaseManager
from agent import NFLPredictionAgent
from data_collector import DataCollector
from datetime import datetime

def main():
    db = DatabaseManager()
    collector = DataCollector()
    
    # Determine current NFL week (2025 season, October 6)
    # NFL 2025 season started Sept 2025, so we're around week 5-6
    season = 2025
    week = 6
    
    print(f"Fetching schedule for {season} Week {week}...")
    games = collector.get_games_for_week(season, week)
    print(f"Found {len(games)} games")
    
    if not games:
        print("No games found - ESPN API may not have 2025 schedule yet")
        print("Using 2024 data instead for demonstration...")
        season = 2024
        week = 6
        games = collector.get_games_for_week(season, week)
        print(f"Found {len(games)} games for {season} week {week}")
    
    # Insert games into database
    inserted = 0
    for game in games:
        if db.insert_game(game):
            inserted += 1
    
    print(f"Inserted {inserted} games into database")
    
    # Now generate predictions
    print(f"\nGenerating predictions for {season} week {week}...")
    agent = NFLPredictionAgent()
    predictions = agent.predict_week(season, week)
    
    print(f"Generated {len(predictions)} predictions")
    
    # Verify they're in the database
    current = db.get_current_predictions()
    past = db.get_past_predictions()
    
    print(f"\nAPI endpoints will return:")
    print(f"  /predictions/current: {len(current)} predictions")
    print(f"  /predictions/past: {len(past)} predictions")
    
    if current or past:
        print("\n✓ Success! Frontend should now display predictions.")
    else:
        print("\n⚠ Still no predictions - checking what went wrong...")
        
        # Debug info
        conn = db.connection()
        cursor = conn.cursor()
        cursor.execute(f"SELECT COUNT(*) FROM games WHERE season={season} AND week={week}")
        game_count = cursor.fetchone()[0]
        cursor.execute(f"SELECT COUNT(*) FROM predictions p JOIN games g ON p.game_id = g.game_id WHERE g.season={season} AND g.week={week}")
        pred_count = cursor.fetchone()[0]
        conn.close()
        
        print(f"  Games in DB for {season} W{week}: {game_count}")
        print(f"  Predictions for those games: {pred_count}")

if __name__ == "__main__":
    main()
