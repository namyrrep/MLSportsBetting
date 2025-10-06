import pandas as pd
import numpy as np
from typing import Dict, List, Any, Tuple
from sklearn.preprocessing import StandardScaler, LabelEncoder
import logging
from src.enhanced_features import add_all_enhanced_features

logger = logging.getLogger(__name__)

class FeatureEngineer:
    """Creates features for machine learning models from raw game data."""
    
    def __init__(self):
        self.scalers = {}
        self.encoders = {}
        self.team_mappings = {}
    
    def create_features(self, games_df: pd.DataFrame) -> pd.DataFrame:
        """Create comprehensive features from games data."""
        logger.info("Creating features from games data...")
        
        # Make a copy to avoid modifying original data
        df = games_df.copy()
        
        # Basic features
        df = self._add_basic_features(df)
        
        # Historical performance features
        df = self._add_historical_features(df)
        
        # Head-to-head features
        df = self._add_head_to_head_features(df)
        
        # Situational features
        df = self._add_situational_features(df)
        
        # Advanced statistics
        df = self._add_advanced_stats(df)
        
        # Apply ALL enhanced features (ML improvements)
        df = add_all_enhanced_features(df)
        
        logger.info(f"Created {len(df.columns)} features with ML enhancements")
        return df
    
    def _add_basic_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add basic game features."""
        # Convert game_date to datetime if it's not already
        df['game_date'] = pd.to_datetime(df['game_date'])
        
        # Day of week (0=Monday, 6=Sunday)
        df['day_of_week'] = df['game_date'].dt.dayofweek
        
        # Month of the season
        df['month'] = df['game_date'].dt.month
        
        # Is it a playoff game?
        df['is_playoff'] = (df['week'] > 18).astype(int)
        
        # Is it a division game? (simplified - would need division mappings)
        df['is_division_game'] = 0  # Placeholder
        
        # Home field advantage indicator
        df['home_field_advantage'] = 1
        
        return df
    
    def _add_historical_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add features based on historical team performance."""
        # Sort by date to ensure proper chronological order
        df = df.sort_values(['season', 'week', 'game_date']).reset_index(drop=True)
        
        # Initialize feature columns
        feature_cols = [
            'home_wins_last_5', 'home_losses_last_5',
            'away_wins_last_5', 'away_losses_last_5',
            'home_points_avg_last_5', 'home_points_allowed_avg_last_5',
            'away_points_avg_last_5', 'away_points_allowed_avg_last_5',
            'home_win_streak', 'away_win_streak',
            'home_elo', 'away_elo'
        ]
        
        for col in feature_cols:
            df[col] = 0.0
        
        # Calculate rolling statistics for each team
        for idx, row in df.iterrows():
            home_team = row['home_team']
            away_team = row['away_team']
            current_date = row['game_date']
            
            # Get historical data up to this point
            historical_data = df[df['game_date'] < current_date].copy()
            
            if len(historical_data) > 0:
                # Home team historical stats
                home_stats = self._calculate_team_stats(historical_data, home_team, current_date)
                for key, value in home_stats.items():
                    if f'home_{key}' in df.columns:
                        df.at[idx, f'home_{key}'] = value
                
                # Away team historical stats
                away_stats = self._calculate_team_stats(historical_data, away_team, current_date)
                for key, value in away_stats.items():
                    if f'away_{key}' in df.columns:
                        df.at[idx, f'away_{key}'] = value
        
        return df
    
    def _calculate_team_stats(self, historical_data: pd.DataFrame, team: str, 
                            current_date: pd.Timestamp) -> Dict[str, float]:
        """Calculate various statistics for a team based on historical data."""
        # Get team's recent games (as home or away)
        team_games = historical_data[
            (historical_data['home_team'] == team) | 
            (historical_data['away_team'] == team)
        ].tail(10)  # Last 10 games
        
        if len(team_games) == 0:
            return self._get_default_stats()
        
        # Calculate wins/losses
        wins = 0
        total_points = 0
        total_points_allowed = 0
        win_streak = 0
        
        for _, game in team_games.iterrows():
            if pd.isna(game['winner']) or game['winner'] == '':
                continue
                
            is_home = game['home_team'] == team
            team_score = game['home_score'] if is_home else game['away_score']
            opponent_score = game['away_score'] if is_home else game['home_score']
            
            if pd.notna(team_score) and pd.notna(opponent_score):
                total_points += team_score
                total_points_allowed += opponent_score
                
                if game['winner'] == team:
                    wins += 1
                    win_streak += 1
                else:
                    win_streak = 0
        
        games_played = len(team_games)
        losses = games_played - wins
        
        # Calculate averages
        points_avg = total_points / games_played if games_played > 0 else 0
        points_allowed_avg = total_points_allowed / games_played if games_played > 0 else 0
        
        # Simple ELO calculation (starting at 1500)
        elo_rating = 1500 + (wins - losses) * 10
        
        return {
            'wins_last_5': min(wins, 5),
            'losses_last_5': min(losses, 5),
            'points_avg_last_5': points_avg,
            'points_allowed_avg_last_5': points_allowed_avg,
            'win_streak': win_streak,
            'elo': elo_rating
        }
    
    def _get_default_stats(self) -> Dict[str, float]:
        """Return default statistics for teams with no historical data."""
        return {
            'wins_last_5': 0,
            'losses_last_5': 0,
            'points_avg_last_5': 20.0,  # Average NFL score
            'points_allowed_avg_last_5': 20.0,
            'win_streak': 0,
            'elo': 1500
        }
    
    def _add_head_to_head_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add head-to-head historical features."""
        df['h2h_home_wins'] = 0
        df['h2h_away_wins'] = 0
        df['h2h_games_played'] = 0
        
        for idx, row in df.iterrows():
            home_team = row['home_team']
            away_team = row['away_team']
            current_date = row['game_date']
            
            # Find previous matchups
            h2h_games = df[
                (df['game_date'] < current_date) &
                (
                    ((df['home_team'] == home_team) & (df['away_team'] == away_team)) |
                    ((df['home_team'] == away_team) & (df['away_team'] == home_team))
                )
            ]
            
            if len(h2h_games) > 0:
                home_wins = len(h2h_games[h2h_games['winner'] == home_team])
                away_wins = len(h2h_games[h2h_games['winner'] == away_team])
                
                df.at[idx, 'h2h_home_wins'] = home_wins
                df.at[idx, 'h2h_away_wins'] = away_wins
                df.at[idx, 'h2h_games_played'] = len(h2h_games)
        
        return df
    
    def _add_situational_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add situational features like rest days, travel, etc."""
        # Days of rest (simplified - would need actual calculation)
        df['home_rest_days'] = 7  # Assume standard week
        df['away_rest_days'] = 7
        
        # Temperature and weather impact (if available)
        df['weather_impact'] = 0  # Placeholder
        
        # Spread difference from market expectations
        df['spread_value'] = df['home_spread'].fillna(0)
        
        return df
    
    def _add_advanced_stats(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add advanced statistical features."""
        # ELO difference
        df['elo_difference'] = df['home_elo'] - df['away_elo']
        
        # Recent form difference
        df['form_difference'] = (df['home_wins_last_5'] - df['home_losses_last_5']) - \
                               (df['away_wins_last_5'] - df['away_losses_last_5'])
        
        # Scoring differential
        df['home_score_diff'] = df['home_points_avg_last_5'] - df['home_points_allowed_avg_last_5']
        df['away_score_diff'] = df['away_points_avg_last_5'] - df['away_points_allowed_avg_last_5']
        
        # Momentum indicators
        df['home_momentum'] = df['home_win_streak'] * 0.1
        df['away_momentum'] = df['away_win_streak'] * 0.1
        
        return df
    
    def prepare_features_for_ml(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, List[str]]:
        """Prepare features for machine learning models."""
        # Select feature columns (exclude target and metadata)
        exclude_cols = [
            'game_id', 'game_date', 'home_team', 'away_team', 
            'home_score', 'away_score', 'winner', 'created_at', 'updated_at'
        ]
        
        feature_cols = [col for col in df.columns if col not in exclude_cols]
        
        # Handle missing values
        feature_df = df[feature_cols].copy()
        
        # Fill numeric columns with mean
        numeric_cols = feature_df.select_dtypes(include=[np.number]).columns
        for col in numeric_cols:
            feature_df[col] = feature_df[col].fillna(feature_df[col].mean())
        
        # Fill any remaining NaN with 0
        feature_df = feature_df.fillna(0)
        
        # Encode categorical variables if any
        categorical_cols = feature_df.select_dtypes(include=['object']).columns
        for col in categorical_cols:
            if col not in self.encoders:
                self.encoders[col] = LabelEncoder()
                feature_df[col] = self.encoders[col].fit_transform(feature_df[col].astype(str))
            else:
                feature_df[col] = self.encoders[col].transform(feature_df[col].astype(str))
        
        # Ensure no infinite values
        feature_df = feature_df.replace([np.inf, -np.inf], 0)
        
        return feature_df, feature_cols
    
    def create_target_variable(self, df: pd.DataFrame) -> pd.Series:
        """Create target variable for classification (1 if home team wins, 0 otherwise)."""
        # Convert winner to binary (1 = home wins, 0 = away wins)
        target = (df['winner'] == df['home_team']).astype(int)
        return target