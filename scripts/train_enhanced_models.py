"""
Enhanced Model Training def load_training_data(db: DatabaseManager):
    \"\"\"Load all completed games for training.\"\"\"
    logger.info(\"Loading training data from database...\")
    
    # Get all games (returns DataFrame)
    df = db.get_games()
    
    # Filter for completed games (winner is not None)
    df = df[df['winner'].notna()]
    
    if len(df) == 0:
        raise ValueError(\"No completed games found in database!\")
    
    logger.info(f\"Loaded {len(df)} completed games\")ements all ML improvements
This script:
1. Loads expanded historical data (2020-2024)
2. Applies enhanced feature engineering
3. Performs hyperparameter tuning
4. Trains all 6 models with optimal parameters
5. Saves tuned models for production use
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from src.database import DatabaseManager
from src.feature_engineering import FeatureEngineer
from src.ml_models import MLModelManager
from src.hyperparameter_tuning import tune_all_models, get_quick_param_grids
import pandas as pd
import logging
from sklearn.model_selection import train_test_split
import joblib

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def load_training_data(db: DatabaseManager):
    """Load all completed games for training."""
    logger.info("Loading training data from database...")
    
    # Get all games (returns DataFrame)
    df = db.get_games()
    
    # Filter for completed games (winner is not None)
    df = df[df['winner'].notna()]
    
    if len(df) == 0:
        raise ValueError("No completed games found in database!")
    
    logger.info(f"Loaded {len(df)} completed games")
    
    # Show data distribution
    if 'season' in df.columns:
        season_counts = df['season'].value_counts().sort_index()
        logger.info("\nGames by season:")
        for season, count in season_counts.items():
            logger.info(f"  {season}: {count} games")
    
    return df

def prepare_features_and_target(df: pd.DataFrame):
    """Create features and target variable."""
    logger.info("\nCreating enhanced features...")
    
    feature_engineer = FeatureEngineer()
    
    # Create all features (including enhanced ones)
    features_df = feature_engineer.create_features(df)
    logger.info(f"Created {len(features_df.columns)} features")
    
    # Prepare for ML
    X, feature_cols = feature_engineer.prepare_features_for_ml(features_df)
    logger.info(f"Prepared {len(feature_cols)} feature columns for ML")
    
    # Create target
    y = feature_engineer.create_target_variable(df)
    logger.info(f"Target distribution: {y.value_counts().to_dict()}")
    
    return X, y, feature_cols

def train_enhanced_models(X, y, quick_tune=False):
    """Train models with hyperparameter tuning."""
    logger.info("\n" + "="*70)
    logger.info("TRAINING ENHANCED MODELS WITH HYPERPARAMETER TUNING")
    logger.info("="*70)
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    logger.info(f"\nTraining set: {len(X_train)} samples")
    logger.info(f"Test set: {len(X_test)} samples")
    
    # Initialize model manager
    model_manager = MLModelManager()
    
    # Perform hyperparameter tuning
    logger.info("\n" + "="*70)
    logger.info("HYPERPARAMETER TUNING (This may take 10-30 minutes)")
    logger.info("="*70)
    
    tuned_models = tune_all_models(
        models=model_manager.models,
        X_train=X_train,
        y_train=y_train,
        quick=quick_tune
    )
    
    # Update model manager with tuned models
    model_manager.models = tuned_models
    
    # Train and evaluate all models
    logger.info("\n" + "="*70)
    logger.info("FINAL MODEL TRAINING AND EVALUATION")
    logger.info("="*70)
    
    results = model_manager.train_all_models(X, y)
    
    # Display results
    logger.info("\n" + "="*70)
    logger.info("MODEL PERFORMANCE SUMMARY")
    logger.info("="*70)
    
    for model_name, metrics in sorted(results.items(), key=lambda x: x[1].get('accuracy', 0), reverse=True):
        logger.info(f"\n{model_name.upper()}:")
        for metric_name, value in metrics.items():
            logger.info(f"  {metric_name}: {value:.4f}")
    
    return model_manager, results

def save_enhanced_models(model_manager: MLModelManager):
    """Save all trained models."""
    logger.info("\n" + "="*70)
    logger.info("SAVING ENHANCED MODELS")
    logger.info("="*70)
    
    saved_count = 0
    
    for model_name, model in model_manager.models.items():
        try:
            save_path = os.path.join(model_manager.model_save_path, f"{model_name}.pkl")
            joblib.dump(model, save_path)
            logger.info(f"✓ Saved {model_name} to {save_path}")
            saved_count += 1
        except Exception as e:
            logger.error(f"✗ Failed to save {model_name}: {str(e)}")
    
    # Save scalers
    for scaler_name, scaler in model_manager.scalers.items():
        try:
            save_path = os.path.join(model_manager.model_save_path, f"{scaler_name}_scaler.pkl")
            joblib.dump(scaler, save_path)
            logger.info(f"✓ Saved {scaler_name} scaler to {save_path}")
        except Exception as e:
            logger.error(f"✗ Failed to save {scaler_name} scaler: {str(e)}")
    
    logger.info(f"\nSaved {saved_count} models successfully")
    return saved_count

def main(quick_tune=False):
    """Main training pipeline."""
    logger.info("="*70)
    logger.info("ENHANCED NFL PREDICTION MODEL TRAINING")
    logger.info("Implementing all ML improvements:")
    logger.info("  1. Enhanced features (weather, travel, injuries)")
    logger.info("  2. Expanded training data (2020-2024)")
    logger.info("  3. Hyperparameter tuning")
    logger.info("  4. Improved momentum & matchup features")
    logger.info("="*70)
    
    try:
        # Step 1: Load data
        db = DatabaseManager()
        df = load_training_data(db)
        
        if len(df) < 100:
            logger.warning(f"\n⚠ WARNING: Only {len(df)} games available for training!")
            logger.warning("Consider running scripts/collect_historical_data.py first")
            logger.warning("to collect more historical data (2020-2024 seasons)")
            
            response = input("\nContinue with limited data? (y/n): ")
            if response.lower() != 'y':
                logger.info("Training cancelled. Run data collection first.")
                return
        
        # Step 2: Prepare features
        X, y, feature_cols = prepare_features_and_target(df)
        
        # Step 3: Train models with tuning
        model_manager, results = train_enhanced_models(X, y, quick_tune=quick_tune)
        
        # Step 4: Save models
        saved_count = save_enhanced_models(model_manager)
        
        # Summary
        logger.info("\n" + "="*70)
        logger.info("TRAINING COMPLETE!")
        logger.info("="*70)
        logger.info(f"✓ Trained on {len(df)} games")
        logger.info(f"✓ Created {len(feature_cols)} enhanced features")
        logger.info(f"✓ Saved {saved_count} tuned models")
        logger.info("\nBest model by accuracy:")
        best_model = max(results.items(), key=lambda x: x[1].get('accuracy', 0))
        logger.info(f"  {best_model[0]}: {best_model[1]['accuracy']:.4f}")
        
        logger.info("\n✓ Models are ready for production use!")
        logger.info("Restart your API server to use the enhanced models.")
        
    except KeyboardInterrupt:
        logger.warning("\n⚠ Training interrupted by user")
        
    except Exception as e:
        logger.error(f"\n✗ Training failed: {str(e)}")
        logger.exception("Full traceback:")
        raise

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Train enhanced NFL prediction models')
    parser.add_argument(
        '--quick',
        action='store_true',
        help='Use quick hyperparameter tuning (faster but less thorough)'
    )
    
    args = parser.parse_args()
    
    logger.info(f"Quick tuning mode: {args.quick}")
    main(quick_tune=args.quick)
