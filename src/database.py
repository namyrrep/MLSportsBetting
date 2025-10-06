import sqlite3
import pandas as pd
from datetime import datetime
from typing import List, Dict, Any, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseManager:
    """Manages SQLite database operations for NFL game data."""
    
    def __init__(self, db_path: str = "data/nfl_games.db"):
        self.db_path = db_path
        self.init_database()
    
    def connection(self) -> sqlite3.Connection:
        """Return a raw SQLite connection."""
        return sqlite3.connect(self.db_path)

    def init_database(self):
        """Initialize database with required tables."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Games table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS games (
                    game_id TEXT PRIMARY KEY,
                    season INTEGER,
                    week INTEGER,
                    game_date TEXT,
                    home_team TEXT,
                    away_team TEXT,
                    home_score INTEGER,
                    away_score INTEGER,
                    winner TEXT,
                    home_spread REAL,
                    total_points REAL,
                    weather_temp REAL,
                    weather_wind REAL,
                    weather_conditions TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Team statistics table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS team_stats (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    team TEXT,
                    season INTEGER,
                    week INTEGER,
                    wins INTEGER,
                    losses INTEGER,
                    points_for REAL,
                    points_against REAL,
                    yards_per_game REAL,
                    yards_allowed_per_game REAL,
                    turnovers REAL,
                    turnover_diff REAL,
                    strength_of_schedule REAL,
                    elo_rating REAL,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Predictions table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS predictions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    game_id TEXT,
                    model_name TEXT,
                    predicted_winner TEXT,
                    win_probability REAL,
                    predicted_spread REAL,
                    confidence_score REAL,
                    prediction_date TEXT,
                    actual_winner TEXT,
                    correct_prediction BOOLEAN,
                    FOREIGN KEY (game_id) REFERENCES games (game_id)
                )
            ''')
            
            # Model performance table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS model_performance (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    model_name TEXT,
                    season INTEGER,
                    week INTEGER,
                    accuracy REAL,
                    precision_score REAL,
                    recall_score REAL,
                    f1_score REAL,
                    roc_auc REAL,
                    total_predictions INTEGER,
                    correct_predictions INTEGER,
                    evaluation_date TEXT DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.commit()
            logger.info("Database initialized successfully")
    
    def insert_game(self, game_data: Dict[str, Any]) -> bool:
        """Insert a single game into the database."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT OR REPLACE INTO games (
                        game_id, season, week, game_date, home_team, away_team,
                        home_score, away_score, winner, home_spread, total_points,
                        weather_temp, weather_wind, weather_conditions, updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    game_data.get('game_id'),
                    game_data.get('season'),
                    game_data.get('week'),
                    game_data.get('game_date'),
                    game_data.get('home_team'),
                    game_data.get('away_team'),
                    game_data.get('home_score'),
                    game_data.get('away_score'),
                    game_data.get('winner'),
                    game_data.get('home_spread'),
                    game_data.get('total_points'),
                    game_data.get('weather_temp'),
                    game_data.get('weather_wind'),
                    game_data.get('weather_conditions'),
                    datetime.now().isoformat()
                ))
                
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"Error inserting game: {e}")
            return False
    
    def insert_games_batch(self, games_data: List[Dict[str, Any]]) -> int:
        """Insert multiple games in batch."""
        successful_inserts = 0
        for game_data in games_data:
            if self.insert_game(game_data):
                successful_inserts += 1
        return successful_inserts
    
    def get_games(self, season: Optional[int] = None, week: Optional[int] = None, 
                  team: Optional[str] = None) -> pd.DataFrame:
        """Retrieve games based on filters."""
        query = "SELECT * FROM games WHERE 1=1"
        params = []
        
        if season:
            query += " AND season = ?"
            params.append(season)
        if week:
            query += " AND week = ?"
            params.append(week)
        if team:
            query += " AND (home_team = ? OR away_team = ?)"
            params.extend([team, team])
        
        query += " ORDER BY game_date DESC"
        
        with sqlite3.connect(self.db_path) as conn:
            return pd.read_sql_query(query, conn, params=params)
    
    def insert_prediction(self, prediction_data: Dict[str, Any]) -> bool:
        """Insert a prediction into the database."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT INTO predictions (
                        game_id, model_name, predicted_winner, win_probability,
                        predicted_spread, confidence_score, prediction_date
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    prediction_data.get('game_id'),
                    prediction_data.get('model_name'),
                    prediction_data.get('predicted_winner'),
                    prediction_data.get('win_probability'),
                    prediction_data.get('predicted_spread'),
                    prediction_data.get('confidence_score'),
                    datetime.now().isoformat()
                ))
                
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"Error inserting prediction: {e}")
            return False
    
    def update_prediction_results(self, game_id: str) -> bool:
        """Update predictions with actual game results."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Get actual game result
                cursor.execute("SELECT winner FROM games WHERE game_id = ?", (game_id,))
                result = cursor.fetchone()
                
                if result:
                    actual_winner = result[0]
                    
                    # Update all predictions for this game
                    cursor.execute('''
                        UPDATE predictions 
                        SET actual_winner = ?, 
                            correct_prediction = (predicted_winner = ?)
                        WHERE game_id = ?
                    ''', (actual_winner, actual_winner, game_id))
                    
                    conn.commit()
                    return True
                    
        except Exception as e:
            logger.error(f"Error updating prediction results: {e}")
            
        return False
    
    def get_model_accuracy(self, model_name: str, season: Optional[int] = None) -> float:
        """Calculate model accuracy."""
        query = '''
            SELECT AVG(CAST(correct_prediction as FLOAT)) as accuracy
            FROM predictions p
            JOIN games g ON p.game_id = g.game_id
            WHERE p.model_name = ? AND p.actual_winner IS NOT NULL
        '''
        params = [model_name]
        
        if season:
            query += " AND g.season = ?"
            params.append(season)
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            result = cursor.fetchone()
            return result[0] if result[0] is not None else 0.0
    
    def get_team_record(self, team: str, season: int, up_to_week: int) -> Dict[str, int]:
        """Get team's win-loss record up to a specific week."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT 
                    SUM(CASE WHEN winner = ? THEN 1 ELSE 0 END) as wins,
                    COUNT(*) as total_games
                FROM games 
                WHERE (home_team = ? OR away_team = ?) 
                AND season = ? AND week < ? AND winner IS NOT NULL
            ''', (team, team, team, season, up_to_week))
            
            result = cursor.fetchone()
            wins = result[0] if result[0] else 0
            total = result[1] if result[1] else 0
            
            return {
                'wins': wins,
                'losses': total - wins,
                'total_games': total
            }
    
    def get_existing_game_ids(self, season: Optional[int] = None, week: Optional[int] = None) -> List[str]:
        """Get list of existing game IDs for given season/week."""
        query = "SELECT game_id FROM games WHERE 1=1"
        params = []
        
        if season:
            query += " AND season = ?"
            params.append(season)
        if week:
            query += " AND week = ?"
            params.append(week)
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return [row[0] for row in cursor.fetchall()]
    
    def get_incomplete_games(self, season: Optional[int] = None) -> pd.DataFrame:
        """Get games that don't have results yet (winner is null)."""
        query = "SELECT * FROM games WHERE winner IS NULL OR winner = ''"
        params = []
        
        if season:
            query += " AND season = ?"
            params.append(season)
        
        query += " ORDER BY game_date DESC"
        
        with sqlite3.connect(self.db_path) as conn:
            return pd.read_sql_query(query, conn, params=params)
    
    def update_game_results(self, games_data: List[Dict[str, Any]]) -> int:
        """Update existing games with new results."""
        updated_count = 0
        
        for game_data in games_data:
            try:
                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.cursor()
                    
                    # Update game results
                    cursor.execute('''
                        UPDATE games 
                        SET home_score = ?, away_score = ?, winner = ?, updated_at = ?
                        WHERE game_id = ? AND (winner IS NULL OR winner = '' OR home_score IS NULL)
                    ''', (
                        game_data.get('home_score'),
                        game_data.get('away_score'),
                        game_data.get('winner'),
                        datetime.now().isoformat(),
                        game_data.get('game_id')
                    ))
                    
                    if cursor.rowcount > 0:
                        updated_count += 1
                        
                        # Update prediction results for this game
                        self.update_prediction_results(game_data.get('game_id'))
                    
                    conn.commit()
                    
            except Exception as e:
                logger.error(f"Error updating game {game_data.get('game_id')}: {e}")
        
        return updated_count
    
    def get_data_coverage_summary(self) -> Dict[str, Any]:
        """Get summary of data coverage by season and week."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Get games by season
            cursor.execute('''
                SELECT season, 
                       COUNT(*) as total_games,
                       SUM(CASE WHEN winner IS NOT NULL AND winner != '' THEN 1 ELSE 0 END) as completed_games
                FROM games 
                GROUP BY season 
                ORDER BY season
            ''')
            
            seasons = []
            for row in cursor.fetchall():
                seasons.append({
                    'season': row[0],
                    'total_games': row[1],
                    'completed_games': row[2],
                    'completion_rate': row[2] / row[1] if row[1] > 0 else 0
                })
            
            # Get total summary
            cursor.execute('''
                SELECT COUNT(*) as total_games,
                       SUM(CASE WHEN winner IS NOT NULL AND winner != '' THEN 1 ELSE 0 END) as completed_games,
                       MIN(season) as earliest_season,
                       MAX(season) as latest_season
                FROM games
            ''')
            
            summary = cursor.fetchone()
            
            return {
                'total_games': summary[0] if summary else 0,
                'completed_games': summary[1] if summary else 0,
                'earliest_season': summary[2],
                'latest_season': summary[3],
                'seasons': seasons
            }
    
    def get_current_predictions(self, season: int = None, week: int = None, limit: int = None) -> list[dict]:
        """Return ensemble predictions for the next scheduled week or specified season/week."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            # Use provided season/week or find next scheduled week
            if season is not None and week is not None:
                target_season, target_week = season, week
            else:
                cursor.execute('''
                    SELECT season, week
                    FROM games
                    WHERE winner IS NULL OR winner = ''
                    ORDER BY season DESC, week ASC
                    LIMIT 1
                ''')
                upcoming = cursor.fetchone()

                if not upcoming:
                    return []

                target_season, target_week = upcoming['season'], upcoming['week']

            cursor.execute('''
                WITH latest_predictions AS (
                    SELECT pr.game_id,
                           pr.predicted_winner,
                           pr.win_probability,
                           pr.confidence_score,
                           pr.prediction_date
                    FROM predictions pr
                    JOIN (
                        SELECT game_id, MAX(prediction_date) AS max_date
                        FROM predictions
                        WHERE model_name = 'ensemble'
                        GROUP BY game_id
                    ) latest ON latest.game_id = pr.game_id AND latest.max_date = pr.prediction_date
                    WHERE pr.model_name = 'ensemble'
                )
          SELECT g.game_id, g.season, g.week, g.game_date,
              g.home_team, g.away_team,
              g.home_spread, g.total_points,
              g.weather_temp, g.weather_wind, g.weather_conditions,
              lp.predicted_winner, lp.win_probability,
              lp.confidence_score, lp.prediction_date
                FROM games g
                JOIN latest_predictions lp ON lp.game_id = g.game_id
                WHERE g.season = ? AND g.week = ?
                ORDER BY datetime(g.game_date) ASC, g.home_team
            ''', (target_season, target_week))

            rows = cursor.fetchall()

        predictions: List[Dict[str, Any]] = []
        for row in rows:
            predictions.append({
                'game_id': row['game_id'],
                'season': row['season'],
                'week': row['week'],
                'game_date': row['game_date'],
                'home_team': row['home_team'],
                'away_team': row['away_team'],
                'predicted_winner': row['predicted_winner'],
                'win_probability': float(row['win_probability']) if row['win_probability'] is not None else None,
                'confidence_score': float(row['confidence_score']) if row['confidence_score'] is not None else None,
                'prediction_date': row['prediction_date'],
                'home_spread': float(row['home_spread']) if row['home_spread'] is not None else None,
                'total_points': float(row['total_points']) if row['total_points'] is not None else None,
                'weather_temp': float(row['weather_temp']) if row['weather_temp'] is not None else None,
                'weather_wind': float(row['weather_wind']) if row['weather_wind'] is not None else None,
                'weather_conditions': row['weather_conditions'],
                'espn_url': f"https://www.espn.com/nfl/game/_/gameId/{row['game_id']}" if row['game_id'] else None
            })

        return predictions

    def get_past_predictions(
        self,
        season: Optional[int] = None,
        week: Optional[int] = None,
        limit: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """Return ensemble predictions for the most recently completed week or a specific week."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            if season is None or week is None:
                cursor.execute('''
                    SELECT g.season, g.week
                    FROM games g
                    JOIN predictions pr ON pr.game_id = g.game_id AND pr.model_name = 'ensemble'
                    WHERE g.winner IS NOT NULL AND g.winner != ''
                    ORDER BY g.season DESC, g.week DESC
                    LIMIT 1
                ''')
                latest = cursor.fetchone()

                if not latest:
                    return []

                season = latest['season']
                week = latest['week']

            cursor.execute('''
                WITH latest_predictions AS (
                    SELECT pr.game_id,
                           pr.predicted_winner,
                           pr.win_probability,
                           pr.confidence_score,
                           pr.prediction_date
                    FROM predictions pr
                    JOIN (
                        SELECT game_id, MAX(prediction_date) AS max_date
                        FROM predictions
                        WHERE model_name = 'ensemble'
                        GROUP BY game_id
                    ) latest ON latest.game_id = pr.game_id AND latest.max_date = pr.prediction_date
                    WHERE pr.model_name = 'ensemble'
                )
          SELECT g.game_id, g.season, g.week, g.game_date,
              g.home_team, g.away_team,
              g.home_spread, g.total_points,
              g.weather_temp, g.weather_wind, g.weather_conditions,
                       g.home_score, g.away_score, g.winner AS actual_winner,
                       lp.predicted_winner, lp.win_probability,
                       lp.confidence_score, lp.prediction_date
                FROM games g
                JOIN latest_predictions lp ON lp.game_id = g.game_id
                WHERE g.season = ? AND g.week = ?
                  AND g.winner IS NOT NULL AND g.winner != ''
                ORDER BY datetime(g.game_date) DESC, g.home_team
            ''', (season, week))

            rows = cursor.fetchall()

        predictions: List[Dict[str, Any]] = []
        for index, row in enumerate(rows):
            if limit is not None and index >= limit:
                break

            actual_winner = row['actual_winner']
            predicted_winner = row['predicted_winner']

            predictions.append({
                'game_id': row['game_id'],
                'season': row['season'],
                'week': row['week'],
                'game_date': row['game_date'],
                'home_team': row['home_team'],
                'away_team': row['away_team'],
                'home_spread': float(row['home_spread']) if row['home_spread'] is not None else None,
                'total_points': float(row['total_points']) if row['total_points'] is not None else None,
                'weather_temp': float(row['weather_temp']) if row['weather_temp'] is not None else None,
                'weather_wind': float(row['weather_wind']) if row['weather_wind'] is not None else None,
                'weather_conditions': row['weather_conditions'],
                'home_score': row['home_score'],
                'away_score': row['away_score'],
                'predicted_winner': predicted_winner,
                'win_probability': float(row['win_probability']) if row['win_probability'] is not None else None,
                'confidence_score': float(row['confidence_score']) if row['confidence_score'] is not None else None,
                'prediction_date': row['prediction_date'],
                'actual_winner': actual_winner,
                'correct_prediction': bool(
                    predicted_winner and actual_winner and predicted_winner == actual_winner
                ),
                'espn_url': f"https://www.espn.com/nfl/game/_/gameId/{row['game_id']}" if row['game_id'] else None
            })

        return predictions

    def get_weekly_accuracy_breakdown(self, limit: int = 6) -> list[dict[str, Any]]:
        """Return accuracy by season/week for the latest completed weeks (limit rows)."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            cursor.execute(
                '''
                WITH latest_predictions AS (
                    SELECT pr.*
                    FROM predictions pr
                    JOIN (
                        SELECT game_id, MAX(prediction_date) AS max_date
                        FROM predictions
                        WHERE model_name = 'ensemble'
                        GROUP BY game_id
                    ) latest ON latest.game_id = pr.game_id AND latest.max_date = pr.prediction_date
                    WHERE pr.model_name = 'ensemble'
                      AND pr.actual_winner IS NOT NULL
                )
                SELECT g.season,
                       g.week,
                       SUM(CASE WHEN lp.correct_prediction = 1 THEN 1 ELSE 0 END) AS correct,
                       COUNT(*) AS total,
                       MIN(lp.prediction_date) AS earliest_prediction,
                       MAX(lp.prediction_date) AS latest_prediction
                FROM latest_predictions lp
                JOIN games g ON g.game_id = lp.game_id
                GROUP BY g.season, g.week
                ORDER BY g.season DESC, g.week DESC
                LIMIT ?
                ''',
                (limit,),
            )

            rows = cursor.fetchall()

        breakdown: list[dict[str, Any]] = []
        for row in rows:
            total = row['total']
            correct = row['correct']
            accuracy = (correct / total) if total else 0
            breakdown.append(
                {
                    'season': row['season'],
                    'week': row['week'],
                    'correct': correct,
                    'total': total,
                    'accuracy': accuracy,
                    'earliest_prediction': row['earliest_prediction'],
                    'latest_prediction': row['latest_prediction'],
                }
            )

        return breakdown

    def get_recent_prediction_outcomes(self, limit: int = 12) -> list[dict[str, Any]]:
        """Return most recent predictions with outcome for streak/recency insights."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            cursor.execute(
                '''
                WITH latest_predictions AS (
                    SELECT pr.*
                    FROM predictions pr
                    JOIN (
                        SELECT game_id, MAX(prediction_date) AS max_date
                        FROM predictions
                        WHERE model_name = 'ensemble'
                        GROUP BY game_id
                    ) latest ON latest.game_id = pr.game_id AND latest.max_date = pr.prediction_date
                    WHERE pr.model_name = 'ensemble'
                      AND pr.actual_winner IS NOT NULL
                )
                SELECT lp.game_id,
                       g.season,
                       g.week,
                       lp.predicted_winner,
                       lp.actual_winner,
                       lp.correct_prediction,
                       lp.prediction_date
                FROM latest_predictions lp
                JOIN games g ON g.game_id = lp.game_id
                ORDER BY datetime(g.game_date) DESC
                LIMIT ?
                ''',
                (limit,),
            )

            rows = cursor.fetchall()

        outcomes: list[dict[str, Any]] = []
        for row in rows:
            outcomes.append(
                {
                    'game_id': row['game_id'],
                    'season': row['season'],
                    'week': row['week'],
                    'predicted_winner': row['predicted_winner'],
                    'actual_winner': row['actual_winner'],
                    'correct_prediction': bool(row['correct_prediction']),
                    'prediction_date': row['prediction_date'],
                }
            )

        return outcomes