import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.neural_network import MLPClassifier
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score
from sklearn.preprocessing import StandardScaler
import xgboost as xgb
import lightgbm as lgb
import joblib
import logging
from typing import Dict, List, Tuple, Any, Optional
import os

logger = logging.getLogger(__name__)

class MLModelManager:
    """Manages multiple machine learning models for NFL game prediction."""
    
    def __init__(self, model_save_path: str = "data/models"):
        self.model_save_path = model_save_path
        self.models = {}
        self.scalers = {}
        self.performance_history = {}
        
        # Create models directory if it doesn't exist
        os.makedirs(model_save_path, exist_ok=True)
        
        # Initialize models
        self._initialize_models()
    
    def _initialize_models(self):
        """Initialize all available models."""
        self.models = {
            'random_forest': RandomForestClassifier(
                n_estimators=100,
                max_depth=10,
                min_samples_split=5,
                min_samples_leaf=2,
                random_state=42
            ),
            'xgboost': xgb.XGBClassifier(
                n_estimators=100,
                max_depth=6,
                learning_rate=0.1,
                subsample=0.8,
                colsample_bytree=0.8,
                random_state=42
            ),
            'lightgbm': lgb.LGBMClassifier(
                n_estimators=100,
                max_depth=6,
                learning_rate=0.1,
                subsample=0.8,
                colsample_bytree=0.8,
                random_state=42
            ),
            'logistic_regression': LogisticRegression(
                random_state=42,
                max_iter=1000
            ),
            'gradient_boosting': GradientBoostingClassifier(
                n_estimators=100,
                learning_rate=0.1,
                max_depth=6,
                random_state=42
            ),
            'neural_network': MLPClassifier(
                hidden_layer_sizes=(100, 50),
                max_iter=500,
                random_state=42
            )
        }
        
        # Initialize scalers for models that need them
        scaler_models = ['logistic_regression', 'neural_network']
        for model_name in scaler_models:
            self.scalers[model_name] = StandardScaler()
    
    def train_all_models(self, X: pd.DataFrame, y: pd.Series) -> Dict[str, Dict[str, float]]:
        """Train all models and return performance metrics."""
        logger.info("Training all models...")
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        
        results = {}
        
        for model_name, model in self.models.items():
            try:
                logger.info(f"Training {model_name}...")
                
                # Prepare data (scale if necessary)
                X_train_prepared = X_train.copy()
                X_test_prepared = X_test.copy()
                
                if model_name in self.scalers:
                    X_train_prepared = self.scalers[model_name].fit_transform(X_train_prepared)
                    X_test_prepared = self.scalers[model_name].transform(X_test_prepared)
                
                # Train model
                model.fit(X_train_prepared, y_train)
                
                # Make predictions
                y_pred = model.predict(X_test_prepared)
                y_pred_proba = model.predict_proba(X_test_prepared)[:, 1] if hasattr(model, 'predict_proba') else None
                
                # Calculate metrics
                metrics = self._calculate_metrics(y_test, y_pred, y_pred_proba)
                results[model_name] = metrics
                
                # Save model
                self._save_model(model_name, model)
                
                logger.info(f"{model_name} - Accuracy: {metrics['accuracy']:.4f}")
                
            except Exception as e:
                logger.error(f"Error training {model_name}: {e}")
                results[model_name] = {'error': str(e)}
        
        return results
    
    def _calculate_metrics(self, y_true: pd.Series, y_pred: np.ndarray, 
                          y_pred_proba: Optional[np.ndarray] = None) -> Dict[str, float]:
        """Calculate comprehensive performance metrics."""
        metrics = {
            'accuracy': accuracy_score(y_true, y_pred),
            'precision': precision_score(y_true, y_pred, average='weighted'),
            'recall': recall_score(y_true, y_pred, average='weighted'),
            'f1': f1_score(y_true, y_pred, average='weighted')
        }
        
        if y_pred_proba is not None:
            try:
                metrics['roc_auc'] = roc_auc_score(y_true, y_pred_proba)
            except ValueError:
                metrics['roc_auc'] = 0.5  # Default for edge cases
        
        return metrics
    
    def predict_with_all_models(self, X: pd.DataFrame) -> Dict[str, Dict[str, Any]]:
        """Make predictions with all trained models."""
        predictions = {}
        
        for model_name, model in self.models.items():
            try:
                # Prepare data
                X_prepared = X.copy()
                if model_name in self.scalers:
                    X_prepared = self.scalers[model_name].transform(X_prepared)
                
                # Make predictions
                y_pred = model.predict(X_prepared)
                y_pred_proba = model.predict_proba(X_prepared) if hasattr(model, 'predict_proba') else None
                
                predictions[model_name] = {
                    'predictions': y_pred,
                    'probabilities': y_pred_proba
                }
                
            except Exception as e:
                logger.error(f"Error predicting with {model_name}: {e}")
                predictions[model_name] = {'error': str(e)}
        
        return predictions
    
    def get_ensemble_prediction(self, X: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray]:
        """Get ensemble prediction from all models."""
        all_predictions = self.predict_with_all_models(X)
        
        # Collect predictions from successful models
        valid_predictions = []
        valid_probabilities = []
        
        for model_name, result in all_predictions.items():
            if 'error' not in result and result['predictions'] is not None:
                valid_predictions.append(result['predictions'])
                if result['probabilities'] is not None:
                    valid_probabilities.append(result['probabilities'][:, 1])
        
        if not valid_predictions:
            # Fallback: random predictions
            return np.random.randint(0, 2, size=len(X)), np.random.rand(len(X))
        
        # Average predictions
        ensemble_pred = np.round(np.mean(valid_predictions, axis=0)).astype(int)
        
        if valid_probabilities:
            ensemble_prob = np.mean(valid_probabilities, axis=0)
        else:
            ensemble_prob = ensemble_pred.astype(float)
        
        return ensemble_pred, ensemble_prob
    
    def optimize_hyperparameters(self, X: pd.DataFrame, y: pd.Series, 
                                model_name: str) -> Dict[str, Any]:
        """Optimize hyperparameters for a specific model."""
        if model_name not in self.models:
            raise ValueError(f"Model {model_name} not found")
        
        logger.info(f"Optimizing hyperparameters for {model_name}...")
        
        # Define parameter grids
        param_grids = {
            'random_forest': {
                'n_estimators': [50, 100, 200],
                'max_depth': [5, 10, 15, None],
                'min_samples_split': [2, 5, 10]
            },
            'xgboost': {
                'n_estimators': [50, 100, 200],
                'max_depth': [3, 6, 9],
                'learning_rate': [0.01, 0.1, 0.2]
            },
            'logistic_regression': {
                'C': [0.1, 1, 10, 100],
                'penalty': ['l1', 'l2'],
                'solver': ['liblinear', 'saga']
            }
        }
        
        if model_name not in param_grids:
            logger.warning(f"No parameter grid defined for {model_name}")
            return {}
        
        # Prepare data
        X_prepared = X.copy()
        if model_name in self.scalers:
            X_prepared = self.scalers[model_name].fit_transform(X_prepared)
        
        # Perform grid search
        grid_search = GridSearchCV(
            self.models[model_name],
            param_grids[model_name],
            cv=5,
            scoring='accuracy',
            n_jobs=-1
        )
        
        grid_search.fit(X_prepared, y)
        
        # Update model with best parameters
        self.models[model_name] = grid_search.best_estimator_
        
        return {
            'best_params': grid_search.best_params_,
            'best_score': grid_search.best_score_
        }
    
    def _save_model(self, model_name: str, model: Any):
        """Save trained model to disk."""
        try:
            model_path = os.path.join(self.model_save_path, f"{model_name}.joblib")
            joblib.dump(model, model_path)
            
            # Save scaler if exists
            if model_name in self.scalers:
                scaler_path = os.path.join(self.model_save_path, f"{model_name}_scaler.joblib")
                joblib.dump(self.scalers[model_name], scaler_path)
                
        except Exception as e:
            logger.error(f"Error saving {model_name}: {e}")
    
    def load_models(self):
        """Load all saved models from disk."""
        for model_name in self.models.keys():
            try:
                model_path = os.path.join(self.model_save_path, f"{model_name}.joblib")
                if os.path.exists(model_path):
                    self.models[model_name] = joblib.load(model_path)
                    
                    # Load scaler if exists
                    scaler_path = os.path.join(self.model_save_path, f"{model_name}_scaler.joblib")
                    if os.path.exists(scaler_path):
                        self.scalers[model_name] = joblib.load(scaler_path)
                    
                    logger.info(f"Loaded {model_name} successfully")
                    
            except Exception as e:
                logger.error(f"Error loading {model_name}: {e}")
    
    def get_feature_importance(self, model_name: str) -> Optional[pd.DataFrame]:
        """Get feature importance for tree-based models."""
        if model_name not in self.models:
            return None
        
        model = self.models[model_name]
        
        if hasattr(model, 'feature_importances_'):
            return pd.DataFrame({
                'feature': range(len(model.feature_importances_)),
                'importance': model.feature_importances_
            }).sort_values('importance', ascending=False)
        
        return None
    
    def cross_validate_model(self, X: pd.DataFrame, y: pd.Series, 
                           model_name: str, cv: int = 5) -> Dict[str, float]:
        """Perform cross-validation on a specific model."""
        if model_name not in self.models:
            raise ValueError(f"Model {model_name} not found")
        
        # Prepare data
        X_prepared = X.copy()
        if model_name in self.scalers:
            X_prepared = self.scalers[model_name].fit_transform(X_prepared)
        
        # Perform cross-validation
        scores = cross_val_score(
            self.models[model_name], 
            X_prepared, 
            y, 
            cv=cv, 
            scoring='accuracy'
        )
        
        return {
            'mean_score': scores.mean(),
            'std_score': scores.std(),
            'scores': scores.tolist()
        }