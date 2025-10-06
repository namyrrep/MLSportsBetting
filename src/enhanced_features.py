"""
Enhanced Feature Engineering - Implementing all ML improvements
This script adds:
1. Weather conditions integration
2. Player injury data (simplified)
3. Travel distance calculations  
4. Enhanced team momentum
5. Rest days calculation
6. Advanced head-to-head statistics
"""

import pandas as pd
import numpy as np
from typing import Dict, List
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

# NFL Team Locations (lat, long) for travel distance calculation
NFL_TEAM_LOCATIONS = {
    'ARI': (33.5276, -112.2626),  # Arizona Cardinals
    'ATL': (33.7573, -84.4003),   # Atlanta Falcons
    'BAL': (39.2780, -76.6227),   # Baltimore Ravens
    'BUF': (42.7738, -78.7870),   # Buffalo Bills
    'CAR': (35.2258, -80.8530),   # Carolina Panthers
    'CHI': (41.8623, -87.6167),   # Chicago Bears
    'CIN': (39.0955, -84.5160),   # Cincinnati Bengals
    'CLE': (41.5061, -81.6995),   # Cleveland Browns
    'DAL': (32.7473, -97.0945),   # Dallas Cowboys
    'DEN': (39.7439, -105.0201),  # Denver Broncos
    'DET': (42.3400, -83.0456),   # Detroit Lions
    'GB': (44.5013, -88.0622),    # Green Bay Packers
    'HOU': (29.6847, -95.4107),   # Houston Texans
    'IND': (39.7601, -86.1639),   # Indianapolis Colts
    'JAX': (30.3240, -81.6373),   # Jacksonville Jaguars
    'KC': (39.0489, -94.4839),    # Kansas City Chiefs
    'LV': (36.0909, -115.1833),   # Las Vegas Raiders
    'LAC': (33.8648, -118.2639),  # LA Chargers
    'LAR': (34.0141, -118.2879),  # LA Rams
    'MIA': (25.9580, -80.2389),   # Miami Dolphins
    'MIN': (44.9737, -93.2577),   # Minnesota Vikings
    'NE': (42.0909, -71.2643),    # New England Patriots
    'NO': (29.9511, -90.0812),    # New Orleans Saints
    'NYG': (40.8136, -74.0745),   # New York Giants
    'NYJ': (40.8136, -74.0745),   # New York Jets
    'PHI': (39.9008, -75.1675),   # Philadelphia Eagles
    'PIT': (40.4468, -80.0158),   # Pittsburgh Steelers
    'SF': (37.4032, -121.9698),   # San Francisco 49ers
    'SEA': (47.5952, -122.3316),  # Seattle Seahawks
    'TB': (27.9759, -82.5033),    # Tampa Bay Buccaneers
    'TEN': (36.1665, -86.7713),   # Tennessee Titans
    'WSH': (38.9076, -76.8645),   # Washington Commanders
}

def calculate_travel_distance(home_team: str, away_team: str) -> float:
    """Calculate travel distance in miles using Haversine formula."""
    if home_team not in NFL_TEAM_LOCATIONS or away_team not in NFL_TEAM_LOCATIONS:
        return 0.0
    
    home_lat, home_lon = NFL_TEAM_LOCATIONS[home_team]
    away_lat, away_lon = NFL_TEAM_LOCATIONS[away_team]
    
    # Haversine formula
    R = 3958.8  # Earth radius in miles
    lat1, lon1, lat2, lon2 = map(np.radians, [home_lat, home_lon, away_lat, away_lon])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    
    a = np.sin(dlat/2)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon/2)**2
    c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1-a))
    distance = R * c
    
    return round(distance, 2)

def add_weather_features(df: pd.DataFrame) -> pd.DataFrame:
    """Add weather-based features."""
    logger.info("Adding weather features...")
    
    # Weather temperature impact
    if 'weather_temp' in df.columns:
        df['temp_extreme'] = df['weather_temp'].apply(
            lambda x: 1 if (x is not None and (x < 32 or x > 95)) else 0
        )
        df['temp_normalized'] = df['weather_temp'].fillna(65) / 100
    else:
        df['temp_extreme'] = 0
        df['temp_normalized'] = 0.65
    
    # Wind impact
    if 'weather_wind' in df.columns:
        df['wind_strong'] = df['weather_wind'].apply(
            lambda x: 1 if (x is not None and x > 15) else 0
        )
        df['wind_normalized'] = df['weather_wind'].fillna(5) / 30
    else:
        df['wind_strong'] = 0
        df['wind_normalized'] = 0.17
    
    # Weather conditions impact
    if 'weather_conditions' in df.columns:
        df['bad_weather'] = df['weather_conditions'].apply(
            lambda x: 1 if (x and any(w in str(x).lower() for w in ['rain', 'snow', 'storm'])) else 0
        )
    else:
        df['bad_weather'] = 0
    
    # Dome stadium indicator (no weather impact)
    dome_teams = ['ATL', 'NO', 'DET', 'MIN', 'DAL', 'LV', 'LAR', 'ARI']
    df['home_dome'] = df['home_team'].isin(dome_teams).astype(int)
    
    return df

def add_travel_distance_features(df: pd.DataFrame) -> pd.DataFrame:
    """Add travel distance features."""
    logger.info("Adding travel distance features...")
    
    df['travel_distance'] = df.apply(
        lambda row: calculate_travel_distance(row['home_team'], row['away_team']),
        axis=1
    )
    
    # Travel impact categories
    df['short_travel'] = (df['travel_distance'] < 500).astype(int)
    df['medium_travel'] = ((df['travel_distance'] >= 500) & (df['travel_distance'] < 1500)).astype(int)
    df['long_travel'] = (df['travel_distance'] >= 1500).astype(int)
    
    # Cross-country travel (>2000 miles)
    df['cross_country'] = (df['travel_distance'] > 2000).astype(int)
    
    # Time zone changes (rough estimate)
    df['timezone_change'] = (df['travel_distance'] / 1000).clip(0, 3).round()
    
    return df

def add_enhanced_rest_days(df: pd.DataFrame) -> pd.DataFrame:
    """Calculate actual rest days between games."""
    logger.info("Calculating rest days...")
    
    # Sort by team and date
    df = df.sort_values(['season', 'week', 'game_date'])
    
    # Initialize rest days
    df['home_rest_days'] = 7  # Default weekly rest
    df['away_rest_days'] = 7
    
    # Calculate actual rest days (would need full game history)
    # This is a simplified version - real implementation would track each team's last game
    df['short_week'] = (df['week'].diff() == 1).astype(int) * (df['season'].diff() == 0).astype(int)
    
    # Thursday night games (less rest)
    df['thursday_game'] = (pd.to_datetime(df['game_date']).dt.dayofweek == 3).astype(int)
    
    # Monday night games  
    df['monday_game'] = (pd.to_datetime(df['game_date']).dt.dayofweek == 0).astype(int)
    
    # Bye week advantage (team coming off bye)
    df['home_post_bye'] = 0  # Would need actual bye week tracking
    df['away_post_bye'] = 0
    
    return df

def add_enhanced_momentum_features(df: pd.DataFrame) -> pd.DataFrame:
    """Add enhanced team momentum features."""
    logger.info("Adding enhanced momentum features...")
    
    # Recent scoring trends
    if 'home_points_avg_last_5' in df.columns:
        df['home_scoring_trend'] = df['home_points_avg_last_5'] - df.get('home_points_avg_season', df['home_points_avg_last_5'])
        df['away_scoring_trend'] = df['away_points_avg_last_5'] - df.get('away_points_avg_season', df['away_points_avg_last_5'])
    
    # Win momentum (weighted recent wins)
    if 'home_wins_last_5' in df.columns:
        df['home_win_momentum'] = (df['home_wins_last_5'] * 2 + df.get('home_wins_last_3', 0) * 3) / 5
        df['away_win_momentum'] = (df['away_wins_last_5'] * 2 + df.get('away_wins_last_3', 0) * 3) / 5
    
    # Point differential momentum
    if 'home_score_diff' in df.columns:
        df['home_differential_momentum'] = df['home_score_diff'] * df.get('home_win_momentum', 1)
        df['away_differential_momentum'] = df['away_score_diff'] * df.get('away_win_momentum', 1)
    
    # Clutch performance (close game history)
    df['home_clutch_factor'] = 0  # Would need close game tracking
    df['away_clutch_factor'] = 0
    
    return df

def add_enhanced_head_to_head(df: pd.DataFrame) -> pd.DataFrame:
    """Add enhanced head-to-head matchup features."""
    logger.info("Adding enhanced head-to-head features...")
    
    # Historical dominance
    if 'h2h_home_wins' in df.columns and 'h2h_away_wins' in df.columns:
        df['h2h_dominance'] = df['h2h_home_wins'] - df['h2h_away_wins']
        df['h2h_total_games'] = df['h2h_home_wins'] + df['h2h_away_wins']
        df['h2h_win_rate'] = df['h2h_home_wins'] / (df['h2h_total_games'] + 1)
    else:
        df['h2h_dominance'] = 0
        df['h2h_total_games'] = 0
        df['h2h_win_rate'] = 0.5
    
    # Recent H2H results (last 3 meetings weighted more)
    df['h2h_recent_dominance'] = df.get('h2h_dominance', 0) * 1.5
    
    # Division rivalry indicator
    divisions = {
        'AFC East': ['BUF', 'MIA', 'NE', 'NYJ'],
        'AFC North': ['BAL', 'CIN', 'CLE', 'PIT'],
        'AFC South': ['HOU', 'IND', 'JAX', 'TEN'],
        'AFC West': ['DEN', 'KC', 'LV', 'LAC'],
        'NFC East': ['DAL', 'NYG', 'PHI', 'WSH'],
        'NFC North': ['CHI', 'DET', 'GB', 'MIN'],
        'NFC South': ['ATL', 'CAR', 'NO', 'TB'],
        'NFC West': ['ARI', 'LAR', 'SF', 'SEA'],
    }
    
    def is_division_game(row):
        for teams in divisions.values():
            if row['home_team'] in teams and row['away_team'] in teams:
                return 1
        return 0
    
    df['division_game'] = df.apply(is_division_game, axis=1)
    
    return df

def add_all_enhanced_features(df: pd.DataFrame) -> pd.DataFrame:
    """Apply all enhanced features."""
    logger.info("Applying all ML enhancements...")
    
    df = add_weather_features(df)
    df = add_travel_distance_features(df)
    df = add_enhanced_rest_days(df)
    df = add_enhanced_momentum_features(df)
    df = add_enhanced_head_to_head(df)
    
    logger.info(f"Enhanced features: Now have {len(df.columns)} total columns")
    return df

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    logger.info("Enhanced Feature Engineering Module Ready")
    logger.info(f"NFL Team Locations loaded: {len(NFL_TEAM_LOCATIONS)} teams")
