"""FastAPI application that exposes NFL prediction data for the React UI."""

import sys
import os
# Add parent directory to path to allow imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime
from typing import Optional, Any, Dict, List
import logging

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware

from src.database import DatabaseManager
from src.feature_engineering import FeatureEngineer
import pandas as pd

logger = logging.getLogger(__name__)

app = FastAPI(
    title="NFL Prediction Service",
    description="REST API that surfaces upcoming and historical NFL prediction results",
    version="1.0.0",
)

db_manager = DatabaseManager()
feature_engineer = FeatureEngineer()


def _clamp_probability(value: Optional[float]) -> Optional[float]:
    """Clamp probability or confidence values into the [0, 1] range."""
    if value is None:
        return None
    try:
        numeric = float(value)
    except (TypeError, ValueError):
        return None
    return max(0.0, min(1.0, numeric))


def _confidence_bucket(score: Optional[float]) -> Dict[str, Any]:
    """Map a probability to a confidence bucket label and bounds."""
    normalized = _clamp_probability(score)
    if normalized is None:
        return {"label": "Unknown", "min": None, "max": None}

    if normalized >= 0.75:
        return {"label": "High", "min": 0.75, "max": 1.0}
    if normalized >= 0.55:
        return {"label": "Medium", "min": 0.55, "max": 0.75}
    return {"label": "Low", "min": 0.0, "max": 0.55}


def _derive_spread_metadata(prediction: Dict[str, Any]) -> Dict[str, Any]:
    """Return betting-line context for the prediction based on home spread."""
    home_spread = prediction.get("home_spread")
    if home_spread is None:
        return {
            "favorite_team": None,
            "favorite_side": None,
            "spread_margin": None,
            "is_pick_em": None,
            "is_underdog_pick": False,
            "underdog_side": None,
        }

    try:
        spread = float(home_spread)
    except (TypeError, ValueError):
        return {
            "favorite_team": None,
            "favorite_side": None,
            "spread_margin": None,
            "is_pick_em": None,
            "is_underdog_pick": False,
            "underdog_side": None,
        }

    favorite_team = None
    favorite_side = None
    if spread < 0:
        favorite_team = prediction.get("home_team")
        favorite_side = "home"
    elif spread > 0:
        favorite_team = prediction.get("away_team")
        favorite_side = "away"

    spread_margin = abs(spread)
    is_pick_em = spread_margin < 0.5

    predicted_winner = prediction.get("predicted_winner")
    is_underdog_pick = False
    underdog_side = None

    if favorite_team and predicted_winner and predicted_winner != favorite_team and not is_pick_em:
        is_underdog_pick = True
        if predicted_winner == prediction.get("home_team"):
            underdog_side = "home"
        elif predicted_winner == prediction.get("away_team"):
            underdog_side = "away"

    return {
        "favorite_team": favorite_team,
        "favorite_side": favorite_side,
        "spread_margin": round(spread_margin, 1),
        "is_pick_em": is_pick_em,
        "is_underdog_pick": is_underdog_pick,
        "underdog_side": underdog_side,
    }


def _compute_current_streak(outcomes: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    """Calculate the current prediction streak (wins or losses)."""
    if not outcomes:
        return None

    streak_type: Optional[str] = None
    streak_length = 0

    for outcome in outcomes:
        is_correct = bool(outcome.get("correct_prediction"))
        if is_correct:
            if streak_type in (None, "win"):
                streak_type = "win"
                streak_length += 1
            else:
                break
        else:
            if streak_type in (None, "loss"):
                streak_type = "loss"
                streak_length += 1
            else:
                break

    if streak_length == 0 or streak_type is None:
        return None

    return {"type": streak_type, "length": streak_length}


def add_reasoning_to_predictions(predictions: list) -> list:
    """Add reasoning explanation to each prediction."""
    from src.agent import NFLPredictionAgent
    
    agent = NFLPredictionAgent()
    
    for prediction in predictions:
        try:
            # Get the game data
            game_df = pd.DataFrame([{
                'game_id': prediction.get('game_id'),
                'season': prediction.get('season'),
                'week': prediction.get('week'),
                'game_date': prediction.get('game_date'),
                'home_team': prediction.get('home_team'),
                'away_team': prediction.get('away_team'),
                'home_score': prediction.get('home_score'),
                'away_score': prediction.get('away_score'),
                'winner': prediction.get('actual_winner'),
                'home_spread': prediction.get('home_spread'),
                'total_points': prediction.get('total_points'),
                'weather_temp': prediction.get('weather_temp'),
                'weather_wind': prediction.get('weather_wind'),
                'weather_conditions': prediction.get('weather_conditions')
            }])
            
            # Create features
            features_df = feature_engineer.create_features(game_df)
            
            if len(features_df) > 0:
                # Generate reasoning
                home_team = prediction.get('home_team')
                away_team = prediction.get('away_team')
                predicted_winner = prediction.get('predicted_winner')
                actual_winner = prediction.get('actual_winner')
                home_predicted = predicted_winner == home_team
                
                # Check if this is a completed game with result
                if actual_winner and prediction.get('correct_prediction') is not None:
                    home_score = prediction.get('home_score')
                    away_score = prediction.get('away_score')
                    home_spread = prediction.get('home_spread')
                    reasoning = agent._generate_completed_game_reasoning(
                        features_df.iloc[0],
                        home_team,
                        away_team,
                        predicted_winner,
                        actual_winner,
                        home_score,
                        away_score,
                        home_spread,
                        home_predicted
                    )
                else:
                    # Future game - explain why we're predicting this team
                    reasoning = agent._generate_prediction_reasoning(
                        features_df.iloc[0],
                        home_team,
                        away_team,
                        predicted_winner,
                        home_predicted
                    )
                
                prediction['reasoning'] = reasoning
            else:
                prediction['reasoning'] = f"Model predicts {prediction.get('predicted_winner')} will win"
                
        except Exception as e:
            logger.error(f"Error generating reasoning for game {prediction.get('game_id')}: {e}")
            prediction['reasoning'] = f"Model predicts {prediction.get('predicted_winner')} will win"

        # Attach confidence tier and spread metadata for downstream features
        prediction['win_probability'] = _clamp_probability(prediction.get('win_probability'))
        confidence_source = (
            prediction.get('confidence_score')
            if prediction.get('confidence_score') is not None
            else prediction.get('win_probability')
        )

        normalized_confidence = _clamp_probability(confidence_source)
        prediction['confidence_score'] = normalized_confidence
        prediction['confidence_bucket'] = _confidence_bucket(normalized_confidence)

        spread_meta = _derive_spread_metadata(prediction)
        prediction.update(spread_meta)
    
    return predictions

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    """Run first update check when the server boots."""
    logger.info("Server starting - checking for completed game results...")
    try:
        updated = update_completed_games()
        logger.info(f"Startup check complete - updated {updated} games")
    except Exception as e:
        logger.error(f"Startup update failed: {e}")


def update_completed_games():
    """Background task to update game results for incomplete games."""
    try:
        from src.data_collector import DataCollector
        
        collector = DataCollector()
        incomplete_games = db_manager.get_incomplete_games()
        
        if incomplete_games.empty:
            logger.info("No incomplete games to update")
            return
        
        logger.info(f"Checking {len(incomplete_games)} incomplete games for results...")
        updated_count = 0
        
        for _, game in incomplete_games.iterrows():
            # Fetch fresh data for this week
            current_games = collector.get_games_for_week(game['season'], game['week'])
            
            # Find matching game with results
            for current_game in current_games:
                if (current_game['game_id'] == game['game_id'] and 
                    current_game['winner'] is not None and 
                    current_game['winner'] != ''):
                    
                    # Update game with results
                    if db_manager.insert_game(current_game):
                        # Update prediction results
                        db_manager.update_prediction_results(game['game_id'])
                        updated_count += 1
                        logger.info(f"Updated game {game['game_id']}: {current_game['winner']} won")
                    break
        
        logger.info(f"Updated {updated_count} games with results")
        return updated_count
        
    except Exception as e:
        logger.error(f"Error updating completed games: {e}")
        return 0


def _timestamp() -> str:
    """Return a UTC timestamp suitable for responses."""
    return datetime.utcnow().isoformat() + "Z"


@app.get("/health")
def health_check() -> dict:
    """Health endpoint used by the UI to confirm the API is running."""
    return {"status": "ok", "generated_at": _timestamp()}


@app.get("/predictions/current")
def get_current_predictions(
    auto_populate: bool = True,
    season: Optional[int] = None,
    week: Optional[int] = None
) -> dict:
    """Return predictions for the upcoming week.

    When ``auto_populate`` is true and the database has no entries, the
    server will fetch the schedule and create predictions before responding.

    Args:
        auto_populate: If true, build predictions when none exist.
        season: Season number to query.
        week: Week number to query.
    """
    try:
        # Default to current season/week if not specified
        if season is None:
            season = 2025
        if week is None:
            week = 6
        
        predictions = db_manager.get_current_predictions(season=season, week=week)
        
        # Auto-populate if empty and requested
        if not predictions and auto_populate:
            from src.data_collector import DataCollector
            from src.agent import NFLPredictionAgent
            
            # Fetch and insert games
            collector = DataCollector()
            games = collector.get_games_for_week(season, week)
            
            if games:
                for game in games:
                    db_manager.insert_game(game)
                
                # Generate predictions
                agent = NFLPredictionAgent()
                agent.predict_week(season, week)
                
                # Retry query
                predictions = db_manager.get_current_predictions()
        
        # Add reasoning to predictions
        predictions = add_reasoning_to_predictions(predictions)
        
        response = {
            "generated_at": _timestamp(),
            "predictions": predictions,
            "count": len(predictions),
        }

        if predictions:
            response["season"] = predictions[0]["season"]
            response["week"] = predictions[0]["week"]

        return response
    except Exception as exc:  # pragma: no cover - defensive programming
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.get("/predictions/past")
def get_past_predictions(
    season: Optional[int] = None, 
    week: Optional[int] = None,
    background_tasks: BackgroundTasks = None
) -> dict:
    """Return predictions and outcomes for the most recently completed week by default.
    
    Also triggers a background update to check for new game results.
    """
    try:
        # Trigger background update of completed games
        if background_tasks:
            background_tasks.add_task(update_completed_games)
        
        predictions = db_manager.get_past_predictions(season=season, week=week)
        
        # Add reasoning to predictions
        predictions = add_reasoning_to_predictions(predictions)
        
        # Calculate accuracy statistics
        correct_count = sum(1 for p in predictions if p.get('correct_prediction') == True)
        incorrect_count = sum(1 for p in predictions if p.get('correct_prediction') == False)
        total_evaluated = correct_count + incorrect_count
        accuracy_percentage = (correct_count / total_evaluated * 100) if total_evaluated > 0 else 0
        
        response = {
            "generated_at": _timestamp(),
            "predictions": predictions,
            "count": len(predictions),
            "accuracy_stats": {
                "correct": correct_count,
                "incorrect": incorrect_count,
                "total_evaluated": total_evaluated,
                "accuracy_percentage": round(accuracy_percentage, 1),
                "pending": len(predictions) - total_evaluated
            }
        }

        if predictions:
            response["season"] = predictions[0]["season"]
            response["week"] = predictions[0]["week"]
        else:
            if season is not None:
                response["season"] = season
            if week is not None:
                response["week"] = week

        return response
    except Exception as exc:  # pragma: no cover - defensive programming
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.get("/insights/upsets")
def get_upset_watch(
    season: Optional[int] = None,
    week: Optional[int] = None,
    limit: int = 5,
) -> dict:
    """Highlight underdog picks for the upcoming slate."""
    try:
        predictions = db_manager.get_current_predictions(season=season, week=week)
        if not predictions:
            return {
                "generated_at": _timestamp(),
                "upsets": [],
                "count": 0,
                "total_candidates": 0,
                "season": season,
                "week": week,
            }

        enriched = add_reasoning_to_predictions(predictions)
        upsets = [p for p in enriched if p.get('is_underdog_pick')]
        upsets.sort(
            key=lambda item: (
                item.get('confidence_score') or 0.0,
                item.get('spread_margin') or 0.0,
            ),
            reverse=True,
        )

        limited = upsets[: max(0, limit)]
        season_val = limited[0]['season'] if limited else enriched[0].get('season')
        week_val = limited[0]['week'] if limited else enriched[0].get('week')

        return {
            "generated_at": _timestamp(),
            "upsets": limited,
            "count": len(limited),
            "total_candidates": len(upsets),
            "season": season_val,
            "week": week_val,
        }
    except Exception as exc:  # pragma: no cover - defensive programming
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.get("/metrics/overview")
def metrics_overview(weekly_limit: int = 6, recent_limit: int = 12) -> dict:
    """Give accuracy metrics and the current streak."""
    from src.agent import NFLPredictionAgent

    try:
        agent = NFLPredictionAgent()
        summary = agent.get_performance_summary()
        if 'error' in summary:
            raise HTTPException(status_code=500, detail=summary['error'])

        weekly_breakdown = db_manager.get_weekly_accuracy_breakdown(limit=weekly_limit)
        recent_outcomes = db_manager.get_recent_prediction_outcomes(limit=recent_limit)

        recent_accuracy = 0.0
        if recent_outcomes:
            hits = sum(1 for item in recent_outcomes if item.get('correct_prediction'))
            recent_accuracy = hits / len(recent_outcomes)

        streak = _compute_current_streak(recent_outcomes)

        return {
            "generated_at": _timestamp(),
            "overall": summary,
            "weekly_breakdown": weekly_breakdown,
            "recent_accuracy": recent_accuracy,
            "recent_sample_size": len(recent_outcomes),
            "current_streak": streak,
            "recent_outcomes": recent_outcomes,
        }
    except HTTPException:
        raise
    except Exception as exc:  # pragma: no cover - defensive programming
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.post("/predictions/refresh")
def refresh_predictions() -> dict:
    """Manually trigger an update of completed game results."""
    try:
        updated_count = update_completed_games()
        return {
            "status": "success",
            "updated_games": updated_count,
            "generated_at": _timestamp()
        }
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


if __name__ == "__main__":
    try:
        import uvicorn  # type: ignore
    except ImportError as exc:  # pragma: no cover - startup guard
        raise SystemExit("uvicorn is required to run the API server.") from exc

    print("🚀 Starting NFL Prediction API Server...")
    print("📊 Dashboard will be available at: http://localhost:8000")
    print("🔄 API endpoints ready for predictions")
    uvicorn.run(app, host="0.0.0.0", port=8000)
