"""
Hyperparameter Tuning Module - Implements GridSearchCV for all models
This module adds systematic hyperparameter tuning to improve model performance.
"""

import numpy as np
from sklearn.model_selection import GridSearchCV
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.neural_network import MLPClassifier
import xgboost as xgb
import lightgbm as lgb
import logging

logger = logging.getLogger(__name__)

def get_param_grids():
    """Define parameter grids for each model."""
    param_grids = {
        'random_forest': {
            'n_estimators': [100, 200, 300],
            'max_depth': [10, 15, 20, None],
            'min_samples_split': [2, 5, 10],
            'min_samples_leaf': [1, 2, 4],
            'max_features': ['sqrt', 'log2', None]
        },
        'xgboost': {
            'n_estimators': [100, 200, 300],
            'max_depth': [3, 6, 9],
            'learning_rate': [0.01, 0.05, 0.1, 0.2],
            'subsample': [0.7, 0.8, 0.9],
            'colsample_bytree': [0.7, 0.8, 0.9],
            'gamma': [0, 0.1, 0.2]
        },
        'lightgbm': {
            'n_estimators': [100, 200, 300],
            'max_depth': [3, 6, 9],
            'learning_rate': [0.01, 0.05, 0.1, 0.2],
            'subsample': [0.7, 0.8, 0.9],
            'colsample_bytree': [0.7, 0.8, 0.9],
            'num_leaves': [31, 50, 70]
        },
        'logistic_regression': {
            'C': [0.001, 0.01, 0.1, 1, 10, 100],
            'penalty': ['l1', 'l2', 'elasticnet', None],
            'solver': ['lbfgs', 'liblinear', 'saga'],
            'max_iter': [500, 1000, 2000]
        },
        'gradient_boosting': {
            'n_estimators': [100, 200, 300],
            'learning_rate': [0.01, 0.05, 0.1, 0.2],
            'max_depth': [3, 5, 7, 9],
            'subsample': [0.7, 0.8, 0.9, 1.0],
            'min_samples_split': [2, 5, 10],
            'min_samples_leaf': [1, 2, 4]
        },
        'neural_network': {
            'hidden_layer_sizes': [(50,), (100,), (100, 50), (100, 100), (150, 75)],
            'activation': ['relu', 'tanh'],
            'alpha': [0.0001, 0.001, 0.01],
            'learning_rate': ['constant', 'adaptive'],
            'max_iter': [500, 1000]
        }
    }
    return param_grids

def get_quick_param_grids():
    """Define smaller parameter grids for faster tuning."""
    param_grids = {
        'random_forest': {
            'n_estimators': [100, 200],
            'max_depth': [10, 15],
            'min_samples_split': [2, 5],
        },
        'xgboost': {
            'n_estimators': [100, 200],
            'max_depth': [3, 6],
            'learning_rate': [0.05, 0.1],
        },
        'lightgbm': {
            'n_estimators': [100, 200],
            'max_depth': [3, 6],
            'learning_rate': [0.05, 0.1],
        },
        'logistic_regression': {
            'C': [0.1, 1, 10],
            'penalty': ['l2', None],
        },
        'gradient_boosting': {
            'n_estimators': [100, 200],
            'learning_rate': [0.05, 0.1],
            'max_depth': [3, 5],
        },
        'neural_network': {
            'hidden_layer_sizes': [(100,), (100, 50)],
            'alpha': [0.0001, 0.001],
        }
    }
    return param_grids

def tune_model(model, X_train, y_train, param_grid, cv=5, quick=False):
    """
    Tune hyperparameters using GridSearchCV.
    
    Args:
        model: The model to tune
        X_train: Training features
        y_train: Training targets
        param_grid: Parameter grid for GridSearchCV
        cv: Number of cross-validation folds
        quick: Use quick mode with fewer parameters
    
    Returns:
        Best estimator from grid search
    """
    logger.info(f"Tuning {type(model).__name__} with {cv}-fold cross-validation...")
    
    # Use quick grid if specified
    if quick and hasattr(model, '__name__'):
        param_grids = get_quick_param_grids()
    else:
        param_grids = get_param_grids()
    
    grid_search = GridSearchCV(
        estimator=model,
        param_grid=param_grid,
        cv=cv,
        scoring='accuracy',
        n_jobs=-1,
        verbose=1
    )
    
    grid_search.fit(X_train, y_train)
    
    logger.info(f"Best parameters: {grid_search.best_params_}")
    logger.info(f"Best CV score: {grid_search.best_score_:.4f}")
    
    return grid_search.best_estimator_

def tune_all_models(models, X_train, y_train, quick=False):
    """
    Tune all models in the dictionary.
    
    Args:
        models: Dictionary of model_name: model
        X_train: Training features
        y_train: Training targets
        quick: Use quick mode with fewer parameters
    
    Returns:
        Dictionary of tuned models
    """
    param_grids = get_quick_param_grids() if quick else get_param_grids()
    tuned_models = {}
    
    for model_name, model in models.items():
        try:
            if model_name in param_grids:
                logger.info(f"\n{'='*60}")
                logger.info(f"Tuning {model_name}...")
                logger.info(f"{'='*60}")
                
                tuned_model = tune_model(
                    model=model,
                    X_train=X_train,
                    y_train=y_train,
                    param_grid=param_grids[model_name],
                    quick=quick
                )
                tuned_models[model_name] = tuned_model
            else:
                logger.warning(f"No parameter grid defined for {model_name}, using default")
                tuned_models[model_name] = model
                
        except Exception as e:
            logger.error(f"Error tuning {model_name}: {str(e)}")
            tuned_models[model_name] = model
    
    return tuned_models

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    logger.info("Hyperparameter Tuning Module Ready")
    param_grids = get_param_grids()
    logger.info(f"Parameter grids defined for {len(param_grids)} models")
