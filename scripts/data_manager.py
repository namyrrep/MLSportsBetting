#!/usr/bin/env python3
"""
Data management utilities for the NFL prediction system
"""

import sys
import os
import argparse
import pandas as pd
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from agent import NFLPredictionAgent
from database import DatabaseManager
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def show_data_coverage(agent):
    """Show detailed data coverage information."""
    coverage = agent.db.get_data_coverage_summary()
    
    print("\n📊 Database Coverage Report")
    print("=" * 50)
    print(f"Total Games: {coverage['total_games']}")
    print(f"Completed Games: {coverage['completed_games']}")
    
    if coverage['total_games'] > 0:
        incomplete = coverage['total_games'] - coverage['completed_games']
        completion_rate = coverage['completed_games'] / coverage['total_games']
        print(f"Incomplete Games: {incomplete}")
        print(f"Overall Completion Rate: {completion_rate:.1%}")
    
    if coverage['seasons']:
        print(f"\nData Range: {coverage['earliest_season']}-{coverage['latest_season']}")
        print("\nDetailed Coverage by Season:")
        print("-" * 50)
        
        for season_data in coverage['seasons']:
            season = season_data['season']
            total = season_data['total_games']
            completed = season_data['completed_games']
            rate = season_data['completion_rate']
            incomplete = total - completed
            
            status = "✅" if rate == 1.0 else "🔄" if rate > 0.8 else "⚠️"
            
            print(f"{status} {season}: {completed:3d}/{total:3d} completed ({rate:6.1%}) - {incomplete:2d} pending")

def update_incomplete_games(agent):
    """Update games that don't have results yet."""
    print("\n🔄 Updating Incomplete Games")
    print("=" * 50)
    
    incomplete_games = agent.db.get_incomplete_games()
    
    if incomplete_games.empty:
        print("✅ No incomplete games found - database is fully up to date!")
        return
    
    print(f"Found {len(incomplete_games)} incomplete games")
    
    # Group by season and week for efficient processing
    seasons_weeks = incomplete_games[['season', 'week']].drop_duplicates()
    
    print("Incomplete games by season/week:")
    for _, row in seasons_weeks.iterrows():
        season_week_games = incomplete_games[
            (incomplete_games['season'] == row['season']) & 
            (incomplete_games['week'] == row['week'])
        ]
        print(f"  {row['season']} Week {row['week']}: {len(season_week_games)} games")
    
    # Update incomplete games
    updated_count = agent.update_incomplete_games()
    
    if updated_count > 0:
        print(f"✅ Successfully updated {updated_count} games with results!")
    else:
        print("ℹ️ No new results found for incomplete games")

def show_recent_activity(agent):
    """Show recently added/updated games."""
    print("\n📅 Recent Database Activity")
    print("=" * 50)
    
    # Get recent games
    recent_games = agent.db.get_games()
    
    if recent_games.empty:
        print("No games in database")
        return
    
    # Sort by updated_at if available, otherwise by game_date
    if 'updated_at' in recent_games.columns:
        recent_games = recent_games.sort_values('updated_at', ascending=False).head(10)
    else:
        recent_games = recent_games.sort_values('game_date', ascending=False).head(10)
    
    print("Most Recent Games:")
    for _, game in recent_games.iterrows():
        status = "✅" if pd.notna(game['winner']) else "⏳"
        score = f"{game['home_score']}-{game['away_score']}" if pd.notna(game['home_score']) else "TBD"
        print(f"{status} {game['season']} Week {game['week']}: {game['away_team']} @ {game['home_team']} ({score})")

def main():
    """Data management utilities."""
    parser = argparse.ArgumentParser(description='NFL Database Management Utilities')
    parser.add_argument('--coverage', action='store_true',
                       help='Show detailed data coverage report')
    parser.add_argument('--update', action='store_true',
                       help='Update incomplete games with latest results')
    parser.add_argument('--recent', action='store_true',
                       help='Show recent database activity')
    parser.add_argument('--all', action='store_true',
                       help='Run all reports')
    
    args = parser.parse_args()
    
    try:
        # Initialize agent
        agent = NFLPredictionAgent()
        
        if args.all or args.coverage:
            show_data_coverage(agent)
        
        if args.all or args.update:
            update_incomplete_games(agent)
        
        if args.all or args.recent:
            show_recent_activity(agent)
        
        if not any([args.coverage, args.update, args.recent, args.all]):
            print("No action specified. Use --help for options or --all for full report")
            show_data_coverage(agent)
            
    except Exception as e:
        logger.error(f"Error in data management: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()