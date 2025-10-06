import requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import time
import logging
from bs4 import BeautifulSoup
import json

logger = logging.getLogger(__name__)

class DataCollector:
    """Collects NFL game data from various sources."""
    
    def __init__(self):
        self.base_url = "https://site.api.espn.com/apis/site/v2/sports/football/nfl"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def get_games_for_week(self, season: int, week: int, force_refresh: bool = False) -> List[Dict[str, Any]]:
        """Fetch games for a specific week and season."""
        try:
            url = f"{self.base_url}/scoreboard"
            params = {
                'seasontype': 2,  # Regular season
                'week': week,
                'year': season
            }
            
            response = self.session.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            games = []
            for event in data.get('events', []):
                game_data = self._parse_game_data(event, season, week)
                if game_data:
                    games.append(game_data)
            
            logger.info(f"Collected {len(games)} games for {season} week {week}")
            return games
            
        except Exception as e:
            logger.error(f"Error fetching games for {season} week {week}: {e}")
            return []
    
    def get_missing_games_for_week(self, season: int, week: int, existing_games: List[str]) -> List[Dict[str, Any]]:
        """Fetch only games that don't exist in the database."""
        all_games = self.get_games_for_week(season, week)
        
        # Filter out games that already exist
        missing_games = []
        for game in all_games:
            if game['game_id'] not in existing_games:
                missing_games.append(game)
        
        if len(missing_games) > 0:
            logger.info(f"Found {len(missing_games)} new games for {season} week {week}")
        
        return missing_games
    
    def _parse_game_data(self, event: Dict, season: int, week: int) -> Optional[Dict[str, Any]]:
        """Parse individual game data from ESPN API response."""
        try:
            competition = event['competitions'][0]
            competitors = competition['competitors']
            
            # Find home and away teams
            home_team = None
            away_team = None
            home_score = None
            away_score = None
            
            for competitor in competitors:
                team_info = competitor['team']
                score = int(competitor.get('score', 0))
                
                if competitor.get('homeAway') == 'home':
                    home_team = team_info['abbreviation']
                    home_score = score
                else:
                    away_team = team_info['abbreviation']
                    away_score = score
            
            # Determine winner
            winner = None
            if home_score is not None and away_score is not None:
                if home_score > away_score:
                    winner = home_team
                elif away_score > home_score:
                    winner = away_team
                # else: tie (rare in NFL)
            
            # Get game date
            game_date = event.get('date', '')
            
            # Get betting information if available
            home_spread = None
            total_points = None
            
            if 'odds' in competition:
                for odd in competition['odds']:
                    if 'spread' in odd:
                        home_spread = float(odd['spread'])
                    if 'overUnder' in odd:
                        total_points = float(odd['overUnder'])
            
            game_data = {
                'game_id': event['id'],
                'season': season,
                'week': week,
                'game_date': game_date,
                'home_team': home_team,
                'away_team': away_team,
                'home_score': home_score,
                'away_score': away_score,
                'winner': winner,
                'home_spread': home_spread,
                'total_points': total_points,
                'weather_temp': None,
                'weather_wind': None,
                'weather_conditions': None
            }
            
            return game_data
            
        except Exception as e:
            logger.error(f"Error parsing game data: {e}")
            return None
    
    def get_team_stats(self, season: int) -> Dict[str, Dict[str, Any]]:
        """Fetch team statistics for a season."""
        try:
            url = f"{self.base_url}/teams"
            response = self.session.get(url)
            response.raise_for_status()
            data = response.json()
            
            team_stats = {}
            
            for team in data.get('sports', [{}])[0].get('leagues', [{}])[0].get('teams', []):
                team_info = team['team']
                team_abbr = team_info['abbreviation']
                
                # Get detailed team stats
                stats_url = f"{self.base_url}/teams/{team_info['id']}/statistics"
                stats_params = {'season': season}
                
                try:
                    stats_response = self.session.get(stats_url, params=stats_params)
                    stats_response.raise_for_status()
                    stats_data = stats_response.json()
                    
                    # Parse team statistics
                    team_stats[team_abbr] = self._parse_team_stats(stats_data, team_abbr)
                    
                    # Rate limiting
                    time.sleep(0.5)
                    
                except Exception as e:
                    logger.warning(f"Could not fetch stats for {team_abbr}: {e}")
                    team_stats[team_abbr] = self._get_default_team_stats(team_abbr)
            
            return team_stats
            
        except Exception as e:
            logger.error(f"Error fetching team stats: {e}")
            return {}
    
    def _parse_team_stats(self, stats_data: Dict, team_abbr: str) -> Dict[str, Any]:
        """Parse team statistics from API response."""
        try:
            # This is a simplified version - you may need to adjust based on actual API response
            return {
                'team': team_abbr,
                'points_for': 0,
                'points_against': 0,
                'yards_per_game': 0,
                'yards_allowed_per_game': 0,
                'turnovers': 0,
                'turnover_diff': 0,
                'strength_of_schedule': 0,
                'elo_rating': 1500  # Default ELO rating
            }
        except Exception as e:
            logger.error(f"Error parsing team stats for {team_abbr}: {e}")
            return self._get_default_team_stats(team_abbr)
    
    def _get_default_team_stats(self, team_abbr: str) -> Dict[str, Any]:
        """Return default team statistics."""
        return {
            'team': team_abbr,
            'points_for': 0,
            'points_against': 0,
            'yards_per_game': 0,
            'yards_allowed_per_game': 0,
            'turnovers': 0,
            'turnover_diff': 0,
            'strength_of_schedule': 0,
            'elo_rating': 1500
        }
    
    def collect_historical_data(self, start_year: int, end_year: int, db_manager=None) -> List[Dict[str, Any]]:
        """Collect historical game data for many seasons, skipping existing data."""
        all_games = []
        
        for season in range(start_year, end_year + 1):
            logger.info(f"Collecting data for {season} season...")
            
            # Regular season typically has 18 weeks
            for week in range(1, 19):
                if db_manager:
                    # Get existing games for this week
                    existing_games_df = db_manager.get_games(season=season, week=week)
                    existing_game_ids = existing_games_df['game_id'].tolist() if not existing_games_df.empty else []
                    
                    # Only fetch missing games
                    games = self.get_missing_games_for_week(season, week, existing_game_ids)
                else:
                    # Fetch all games if no database manager provided
                    games = self.get_games_for_week(season, week)
                
                all_games.extend(games)
                
                # Rate limiting only if we actually fetched data
                if games:
                    time.sleep(1)
            
            # Add playoff weeks (weeks 19-22)
            for week in range(19, 23):
                if db_manager:
                    existing_games_df = db_manager.get_games(season=season, week=week)
                    existing_game_ids = existing_games_df['game_id'].tolist() if not existing_games_df.empty else []
                    games = self.get_missing_games_for_week(season, week, existing_game_ids)
                else:
                    games = self.get_games_for_week(season, week)
                
                all_games.extend(games)
                if games:
                    time.sleep(1)
        
        logger.info(f"Collected {len(all_games)} new games (skipped existing ones)")
        return all_games
    
    def get_current_week_games(self) -> List[Dict[str, Any]]:
        """Get games for the current NFL week."""
        # This is a simplified implementation
        # You would need to determine the current NFL season and week
        current_year = datetime.now().year
        
        # Estimate current week (this is very simplified)
        current_week = 1
        
        return self.get_games_for_week(current_year, current_week)

class WeatherCollector:
    """Collects weather data for NFL games."""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
    
    def get_weather_for_game(self, stadium_location: str, game_date: str) -> Dict[str, Any]:
        """Get weather data for a specific game."""
        # This would require a weather API key
        # For now, return dummy data
        return {
            'temperature': 70,
            'wind_speed': 5,
            'conditions': 'Clear'
        }