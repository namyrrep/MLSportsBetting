import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
import logging

# Key player mappings used for narrative reasoning
TEAM_STAR_PLAYERS = {
    "ARI": {"qb": "Kyler Murray"},
    "ATL": {"qb": "Kirk Cousins"},
    "BAL": {"qb": "Lamar Jackson"},
    "BUF": {"qb": "Josh Allen"},
    "CAR": {"qb": "Bryce Young"},
    "CHI": {"qb": "Caleb Williams"},
    "CIN": {"qb": "Joe Burrow"},
    "CLE": {"qb": "Deshaun Watson"},
    "DAL": {"qb": "Dak Prescott"},
    "DEN": {"qb": "Bo Nix"},
    "DET": {"qb": "Jared Goff"},
    "GB": {"qb": "Jordan Love"},
    "HOU": {"qb": "C.J. Stroud"},
    "IND": {"qb": "Anthony Richardson"},
    "JAX": {"qb": "Trevor Lawrence"},
    "KC": {"qb": "Patrick Mahomes"},
    "LV": {"qb": "Aidan O'Connell"},
    "LAC": {"qb": "Justin Herbert"},
    "LAR": {"qb": "Matthew Stafford"},
    "MIA": {"qb": "Tua Tagovailoa"},
    "MIN": {"qb": "J.J. McCarthy"},
    "NE": {"qb": "Drake Maye"},
    "NO": {"qb": "Derek Carr"},
    "NYG": {"qb": "Daniel Jones"},
    "NYJ": {"qb": "Aaron Rodgers"},
    "PHI": {"qb": "Jalen Hurts"},
    "PIT": {"qb": "Russell Wilson"},
    "SF": {"qb": "Brock Purdy"},
    "SEA": {"qb": "Geno Smith"},
    "TB": {"qb": "Baker Mayfield"},
    "TEN": {"qb": "Will Levis"},
    "WSH": {"qb": "Jayden Daniels"},
}

from .database import DatabaseManager
from .data_collector import DataCollector
from .feature_engineering import FeatureEngineer
from .ml_models import MLModelManager

logger = logging.getLogger(__name__)

class NFLPredictionAgent:
    """Main agent class that orchestrates NFL game prediction."""
    
    def __init__(self, db_path: str = "data/nfl_games.db", 
                 model_path: str = "data/models"):
        self.db = DatabaseManager(db_path)
        self.data_collector = DataCollector()
        self.feature_engineer = FeatureEngineer()
        self.model_manager = MLModelManager(model_path)
        
        self.is_trained = False
        self.last_training_date = None
        
        # Try to load existing models
        self.model_manager.load_models()
    
    def collect_and_store_data(self, start_year: int, end_year: int, update_existing: bool = True) -> bool:
        """Collect historical data and store in database, skipping existing games."""
        try:
            logger.info(f"Collecting data from {start_year} to {end_year}...")
            
            # Get coverage summary first
            coverage = self.db.get_data_coverage_summary()
            logger.info(f"Current database has {coverage['total_games']} games, {coverage['completed_games']} completed")
            
            # Collect only missing games by passing database manager
            games_data = self.data_collector.collect_historical_data(start_year, end_year, self.db)
            
            if not games_data:
                logger.info("No new games to collect - database is up to date")
                
                # Still check for game result updates if requested
                if update_existing:
                    updated_count = self.update_incomplete_games()
                    logger.info(f"Updated {updated_count} game results")
                    return updated_count > 0
                
                return True
            
            # Store new games in database
            successful_inserts = self.db.insert_games_batch(games_data)
            logger.info(f"Successfully stored {successful_inserts} new games in database")
            
            # Update any incomplete games with results
            if update_existing:
                updated_count = self.update_incomplete_games()
                logger.info(f"Updated {updated_count} game results")
            
            return successful_inserts > 0
            
        except Exception as e:
            logger.error(f"Error collecting and storing data: {e}")
            return False
    
    def update_incomplete_games(self) -> int:
        """Update games that don't have results yet."""
        try:
            # Get incomplete games
            incomplete_games = self.db.get_incomplete_games()
            
            if incomplete_games.empty:
                return 0
            
            logger.info(f"Found {len(incomplete_games)} incomplete games to update")
            
            updated_count = 0
            for _, game in incomplete_games.iterrows():
                # Fetch updated data for this game's week
                current_games = self.data_collector.get_games_for_week(
                    game['season'], game['week']
                )
                
                # Find matching game with results
                for current_game in current_games:
                    if (current_game['game_id'] == game['game_id'] and 
                        current_game['winner'] is not None):
                        
                        # Update this game
                        self.db.update_game_results([current_game])
                        updated_count += 1
                        break
            
            return updated_count
            
        except Exception as e:
            logger.error(f"Error updating incomplete games: {e}")
            return 0
    
    def train_models(self, retrain: bool = False) -> Dict[str, Any]:
        """Train all ML models using stored data."""
        try:
            logger.info("Starting model training...")
            
            # Get training data from database
            games_df = self.db.get_games()
            
            if len(games_df) < 100:
                logger.error("Insufficient data for training (need at least 100 games)")
                return {'error': 'Insufficient training data'}
            
            # Filter completed games only
            completed_games = games_df[games_df['winner'].notna()].copy()
            
            if len(completed_games) < 50:
                logger.error("Insufficient completed games for training")
                return {'error': 'Insufficient completed games'}
            
            logger.info(f"Training on {len(completed_games)} completed games")
            
            # Create features
            features_df = self.feature_engineer.create_features(completed_games)
            
            # Prepare for ML
            X, feature_names = self.feature_engineer.prepare_features_for_ml(features_df)
            y = self.feature_engineer.create_target_variable(completed_games)
            
            # Train models
            results = self.model_manager.train_all_models(X, y)
            
            # Update training status
            self.is_trained = True
            self.last_training_date = datetime.now()
            
            logger.info("Model training completed successfully")
            return {
                'status': 'success',
                'models_trained': len(results),
                'training_samples': len(X),
                'features_used': len(feature_names),
                'results': results
            }
            
        except Exception as e:
            logger.error(f"Error during model training: {e}")
            return {'error': str(e)}
    
    def predict_games(self, games_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Predict outcomes for given games."""
        if not self.is_trained:
            logger.warning("Models not trained. Training with available data...")
            training_result = self.train_models()
            if 'error' in training_result:
                return [{'error': 'Cannot make predictions without trained models'}]
        
        try:
            predictions = []
            
            for game_data in games_data:
                # Create a temporary DataFrame for this game
                game_df = pd.DataFrame([game_data])
                
                # Create features
                features_df = self.feature_engineer.create_features(game_df)
                X, feature_names = self.feature_engineer.prepare_features_for_ml(features_df)
                
                # Get ensemble prediction
                pred, prob = self.model_manager.get_ensemble_prediction(X)
                
                # Determine predicted winner
                home_team = game_data['home_team']
                away_team = game_data['away_team']
                predicted_winner = home_team if pred[0] == 1 else away_team
                
                # Generate reasoning based on features
                reasoning = self._generate_prediction_reasoning(
                    features_df.iloc[0] if len(features_df) > 0 else {},
                    home_team,
                    away_team,
                    predicted_winner,
                    pred[0] == 1
                )
                
                prediction_result = {
                    'game_id': game_data.get('game_id'),
                    'home_team': home_team,
                    'away_team': away_team,
                    'predicted_winner': predicted_winner,
                    'win_probability': float(prob[0]) if pred[0] == 1 else float(1 - prob[0]),
                    'confidence_score': abs(prob[0] - 0.5) * 2,  # Scale to 0-1
                    'prediction_date': datetime.now().isoformat(),
                    'reasoning': reasoning
                }
                
                predictions.append(prediction_result)
                
                # Store prediction in database
                self.db.insert_prediction({
                    'game_id': game_data.get('game_id'),
                    'model_name': 'ensemble',
                    'predicted_winner': predicted_winner,
                    'win_probability': prediction_result['win_probability'],
                    'predicted_spread': None,  # TODO: Add spread prediction
                    'confidence_score': prediction_result['confidence_score']
                })
            
            return predictions
            
        except Exception as e:
            logger.error(f"Error making predictions: {e}")
            return [{'error': str(e)}]
    
    def _collect_reason_facts(self, features: pd.Series, home_team: str,
                              away_team: str, predicted_winner: str,
                              home_predicted: bool) -> list[str]:
        team = home_team if home_predicted else away_team
        opponent = away_team if home_predicted else home_team
        prefix = "home" if home_predicted else "away"
        opp_prefix = "away" if home_predicted else "home"

        qb_name = TEAM_STAR_PLAYERS.get(team, {}).get("qb", f"{team} quarterback")

        facts: list[str] = []

        # Offensive outlook and touchdown projection
        points_avg = features.get(f"{prefix}_points_avg_last_5", 0)
        opp_points_allowed = features.get(f"{opp_prefix}_points_allowed_avg_last_5", 0)
        if points_avg and points_avg > 0:
            projected_td = points_avg / 7
            facts.append(
                f"{qb_name} pilots an offense scoring {points_avg:.1f} ppg across the last five; projection translates to roughly {projected_td:.1f} trips to the end zone"
            )
        if opp_points_allowed and opp_points_allowed > 0:
            facts.append(
                f"{opponent} defense has surrendered {opp_points_allowed:.1f} ppg recently, a matchup edge the model highlighted"
            )

        # Defensive form comparison
        team_points_allowed = features.get(f"{prefix}_points_allowed_avg_last_5", 0)
        opponent_points_avg = features.get(f"{opp_prefix}_points_avg_last_5", 0)
        if team_points_allowed and opponent_points_avg:
            margin = opponent_points_avg - team_points_allowed
            if margin > 1:
                facts.append(
                    f"{team} defense is holding foes {margin:.1f} points below {opponent}'s recent scoring pace ({opponent_points_avg:.1f} ppg)"
                )
            else:
                facts.append(
                    f"{team} defense allows {team_points_allowed:.1f} ppg, aligning with {opponent}'s {opponent_points_avg:.1f} ppg output"
                )

        # Momentum facts using win streak and momentum indices
        win_momentum = features.get(f"{prefix}_win_momentum", 0)
        opp_momentum = features.get(f"{opp_prefix}_win_momentum", 0)
        if win_momentum and win_momentum > opp_momentum:
            facts.append(
                f"Momentum tilt: {team} weighted win trend ({win_momentum:.2f}) tops {opponent}'s ({opp_momentum:.2f})"
            )

        win_streak = features.get(f"{prefix}_win_streak", 0)
        if win_streak and win_streak >= 2:
            facts.append(f"{team} arrives on a {int(win_streak)}-game heater")

        # Situational edges (travel, rest, venue)
        travel_distance = features.get("travel_distance", 0)
        if home_predicted and travel_distance and travel_distance > 1000:
            facts.append(f"{opponent} faced a {int(travel_distance)}-mile road trip")

        if features.get("short_week", 0) > 0:
            if home_predicted:
                facts.append(f"{opponent} entered on short rest")
            else:
                facts.append(f"{team} had to navigate a short-week turnaround")

        if home_predicted and features.get("home_field_advantage", 0) > 0:
            facts.append(f"{team} also carried the domed/home field advantage")

        # Head-to-head insights
        h2h_wins = features.get("h2h_home_wins" if home_predicted else "h2h_away_wins", 0)
        h2h_games = features.get("h2h_games_played", 0)
        if h2h_games and h2h_games > 0 and h2h_wins:
            facts.append(
                f"{team} has claimed {int(h2h_wins)} of the last {int(h2h_games)} meetings"
            )

        return facts

    def _generate_prediction_reasoning(self, features: pd.Series, home_team: str,
                                      away_team: str, predicted_winner: str,
                                      home_predicted: bool) -> str:
        """Build reasoning narrative from recent team metrics."""

        try:
            facts = self._collect_reason_facts(features, home_team, away_team, predicted_winner, home_predicted)

            if not facts:
                return f"Model favors {predicted_winner} based on statistical matchup edges"

            return " • " + " • ".join(facts[:4])

        except Exception as error:
            logger.error(f"Error generating reasoning: {error}")
            return f"Model predicts {predicted_winner} will win"

    def _generate_completed_game_reasoning(self, features: pd.Series, home_team: str,
                                           away_team: str, predicted_winner: str,
                                           actual_winner: str, home_score: int,
                                           away_score: int, home_spread: float | None,
                                           home_predicted: bool) -> str:
        """Explain the prediction using the final score for context."""

        facts = self._collect_reason_facts(features, home_team, away_team, predicted_winner, home_predicted)

        margin = None
        if home_score is not None and away_score is not None:
            margin = abs(home_score - away_score)

        favorite_note = None
        if home_spread is not None:
            favorite = None
            favorite_margin = abs(home_spread)
            if home_spread < 0:
                favorite = home_team
            elif home_spread > 0:
                favorite = away_team

            if favorite:
                if predicted_winner != favorite:
                    favorite_note = (
                        f"Pregame line (ESPN) favored {favorite} by {favorite_margin:.1f}, so the model backed the underdog {predicted_winner}."
                    )
                else:
                    favorite_note = f"Closing line on ESPN had {favorite} -{favorite_margin:.1f}."
            elif favorite_margin == 0:
                favorite_note = "Markets had this listed as a pick'em game."

        score_summary = None
        if home_score is not None and away_score is not None:
            score_summary = f"Final: {home_team} {home_score}, {away_team} {away_score}."

        if actual_winner == predicted_winner:
            segments = [f"✅ CORRECT: Predicted {predicted_winner} to win."]
            if score_summary:
                segments.append(score_summary)
            if favorite_note:
                segments.append(favorite_note)
            if facts:
                segments.append("Model keyed on: " + "; ".join(facts[:3]))
            if margin and margin >= 14:
                segments.append(f"{predicted_winner} controlled the matchup with a {margin}-point cushion.")
            return " ".join(segments)

        # Incorrect prediction path
        segments = [f"❌ INCORRECT: Predicted {predicted_winner}, but {actual_winner} won {home_score}-{away_score}."]
        if favorite_note:
            segments.append(favorite_note)
        if facts:
            segments.append("Model leaned on: " + "; ".join(facts[:3]))
        if margin and margin >= 14:
            segments.append(f"{actual_winner} broke it open with a {margin}-point margin.")
        elif margin:
            segments.append(f"Margin landed at {margin}.")
        segments.append("Model will recalibrate around the actual result.")
        return " ".join(segments)
    
    def predict_week(self, season: int, week: int) -> List[Dict[str, Any]]:
        """Predict all games for a specific week."""
        try:
            # Get games for the week (these might not have results yet)
            games_data = self.data_collector.get_games_for_week(season, week)
            
            if not games_data:
                logger.warning(f"No games found for {season} week {week}")
                return []
            
            # Make predictions
            predictions = self.predict_games(games_data)
            
            logger.info(f"Made predictions for {len(predictions)} games in {season} week {week}")
            return predictions
            
        except Exception as e:
            logger.error(f"Error predicting week {season}-{week}: {e}")
            return [{'error': str(e)}]
    
    def update_results_and_retrain(self) -> Dict[str, Any]:
        """Update game results and retrain models if needed."""
        try:
            logger.info("Updating game results...")
            
            # Get recent games without results
            recent_games = self.db.get_games()
            games_to_update = recent_games[recent_games['winner'].isna()]
            
            updated_count = 0
            for _, game in games_to_update.iterrows():
                # Try to fetch updated results
                current_games = self.data_collector.get_games_for_week(
                    game['season'], game['week']
                )
                
                for current_game in current_games:
                    if (current_game['game_id'] == game['game_id'] and 
                        current_game['winner'] is not None):
                        
                        # Update game in database
                        if self.db.insert_game(current_game):
                            # Update prediction results
                            self.db.update_prediction_results(game['game_id'])
                            updated_count += 1
            
            logger.info(f"Updated {updated_count} game results")
            
            # Check if retraining is needed (weekly or after significant updates)
            should_retrain = (
                self.last_training_date is None or
                (datetime.now() - self.last_training_date).days >= 7 or
                updated_count >= 10
            )
            
            retrain_result = {}
            if should_retrain:
                logger.info("Retraining models with updated data...")
                retrain_result = self.train_models(retrain=True)
            
            return {
                'updated_games': updated_count,
                'retrained': should_retrain,
                'retrain_result': retrain_result
            }
            
        except Exception as e:
            logger.error(f"Error updating results and retraining: {e}")
            return {'error': str(e)}
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get overall performance summary of predictions."""
        try:
            # Get model accuracies
            model_accuracies = {}
            for model_name in self.model_manager.models.keys():
                accuracy = self.db.get_model_accuracy(model_name)
                model_accuracies[model_name] = accuracy
            
            # Get ensemble accuracy
            ensemble_accuracy = self.db.get_model_accuracy('ensemble')
            
            # Get total predictions made
            with self.db.connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT COUNT(*) as total, 
                           SUM(CASE WHEN correct_prediction = 1 THEN 1 ELSE 0 END) as correct
                    FROM predictions 
                    WHERE actual_winner IS NOT NULL
                """)
                result = cursor.fetchone()
                total_predictions = result[0] if result else 0
                correct_predictions = result[1] if result else 0
            
            return {
                'total_predictions': total_predictions,
                'correct_predictions': correct_predictions,
                'overall_accuracy': correct_predictions / total_predictions if total_predictions > 0 else 0,
                'ensemble_accuracy': ensemble_accuracy,
                'model_accuracies': model_accuracies,
                'last_training_date': self.last_training_date.isoformat() if self.last_training_date else None,
                'is_trained': self.is_trained
            }
            
        except Exception as e:
            logger.error(f"Error getting performance summary: {e}")
            return {'error': str(e)}
    
    def predict_current_week(self) -> List[Dict[str, Any]]:
        """Predict games for the current NFL week."""
        # This is a simplified implementation
        # You would need to determine the current NFL season and week
        current_year = datetime.now().year
        
        # Simple logic to determine current week (would need refinement)
        if datetime.now().month >= 9:  # NFL season starts in September
            current_week = min(((datetime.now() - datetime(current_year, 9, 1)).days // 7) + 1, 18)
        else:
            current_year -= 1
            current_week = 18  # End of previous season
        
        return self.predict_week(current_year, current_week)
    
    def get_team_analysis(self, team: str, season: int) -> Dict[str, Any]:
        """Get comprehensive analysis for a specific team."""
        try:
            # Get team's games
            team_games = self.db.get_games(season=season, team=team)
            
            if len(team_games) == 0:
                return {'error': f'No games found for {team} in {season}'}
            
            # Calculate basic stats
            wins = len(team_games[team_games['winner'] == team])
            total_games = len(team_games[team_games['winner'].notna()])
            
            # Calculate average scores
            home_games = team_games[team_games['home_team'] == team]
            away_games = team_games[team_games['away_team'] == team]
            
            home_points = home_games['home_score'].mean() if len(home_games) > 0 else 0
            away_points = away_games['away_score'].mean() if len(away_games) > 0 else 0
            
            return {
                'team': team,
                'season': season,
                'wins': wins,
                'losses': total_games - wins,
                'win_percentage': wins / total_games if total_games > 0 else 0,
                'average_home_score': home_points,
                'average_away_score': away_points,
                'total_games_played': total_games
            }
            
        except Exception as e:
            logger.error(f"Error analyzing team {team}: {e}")
            return {'error': str(e)}