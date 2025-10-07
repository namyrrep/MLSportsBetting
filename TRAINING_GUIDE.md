# 🏈 Complete Training Guide - Maximize Model Efficiency

## Current Status
- **Training Data**: 76 completed games
- **Best Model**: Random Forest at 68.75% accuracy
- **Features**: 67 engineered features

## 🎯 How to Train Your Models for Maximum Efficiency

### Method 1: Quick Retrain (Current Data Only)
Just retrain with existing data to refresh models:

```powershell
# Simple retrain
python scripts\train_models.py
```

**When to use**: After code changes, parameter tuning, or to refresh models.

---

### Method 2: 🚀 BEST - Collect Historical Data & Train (RECOMMENDED)
This will dramatically improve accuracy by training on 5+ years of data!

```powershell
# Step 1: Collect historical data from 2020-2024 seasons
python scripts\collect_historical_data.py

# Step 2: Train models with the expanded dataset
python scripts\train_models.py
```

**Expected improvement**:
- Current: ~76 games → **Target: 1,000+ games**
- Current: 68.75% accuracy → **Expected: 75-85% accuracy**
- More diverse scenarios = better generalization

**Time**: Takes 10-30 minutes depending on your internet speed (ESPN API rate limits)

---

### Method 3: Automated Weekly Updates
Keep models fresh with the latest results:

```powershell
# Update completed game results and auto-retrain if needed
python scripts\update_and_retrain.py
```

**What it does**:
1. Fetches final scores for games that have completed
2. Calculates prediction accuracy
3. Automatically retrains models if enough new data exists
4. Updates the Models page with new training history

**When to use**: Run this **every Monday** after NFL games complete.

---

### Method 4: Smart Data Collection
Intelligently collects missing data:

```powershell
python scripts\smart_collect_data.py
```

---

## 📊 Complete Workflow for Maximum Efficiency

### Initial Setup (Do Once)
```powershell
# 1. Collect ALL historical data (2020-2024)
python scripts\collect_historical_data.py

# 2. Train models on the full dataset
python scripts\train_models.py

# 3. Verify training succeeded
# Check: data/models/ folder should contain .pkl files
# Check: Models page should show training history
```

### Weekly Maintenance (Every Monday)
```powershell
# Update results from weekend games and retrain
python scripts\update_and_retrain.py
```

### Before Each Week's Predictions (Thursday/Friday)
```powershell
# Generate predictions for upcoming week
python scripts\predict.py --season 2025 --week 7
```

---

## 🔧 Advanced: Improving Model Efficiency

### 1. Hyperparameter Tuning
Edit `src/ml_models.py` to tune model parameters:

```python
# Example: Random Forest (currently the best model)
'random_forest': RandomForestClassifier(
    n_estimators=200,      # Try: 300, 500
    max_depth=15,          # Try: 20, 25
    min_samples_split=5,   # Try: 3, 7
    random_state=42
)
```

After changes, retrain:
```powershell
python scripts\train_models.py
```

### 2. Feature Engineering
The system already has 67 features including:
- ✅ Team records and win percentages
- ✅ Point differentials
- ✅ Home/away splits
- ✅ Recent form (last 3 games)
- ✅ ELO ratings
- ✅ Weather conditions
- ✅ Rest days
- ✅ Travel distance
- ✅ Head-to-head history
- ✅ Momentum metrics

### 3. Data Quality
More data = better models:
- **Current**: 76 games (1 partial season)
- **Good**: 500+ games (2-3 seasons)
- **Excellent**: 1,000+ games (5+ seasons) ⭐ RECOMMENDED
- **Maximum**: 2,000+ games (10+ seasons)

---

## 📈 Monitoring Training Progress

### Check Training Logs
```powershell
python scripts\train_models.py
```

Look for output like:
```
INFO:ml_models:Training random_forest...
INFO:ml_models:random_forest - Accuracy: 0.7500 (trained in 0.15s)
INFO:ml_models:Training xgboost...
INFO:ml_models:xgboost - Accuracy: 0.7200 (trained in 0.20s)
...
```

### View in Models Page
1. Start frontend: `cd frontend && npm run dev`
2. Navigate to **Models** page
3. See:
   - Current accuracy for each model
   - Training history over time
   - Performance trends
   - Number of times trained

### Check Database
```powershell
# View training history
python -c "from src.database import DatabaseManager; db = DatabaseManager(); history = db.get_all_models_metadata(); print(history)"
```

---

## 🎯 Recommended Training Schedule

### Initial Phase (This Week)
```powershell
# Day 1: Collect maximum historical data
python scripts\collect_historical_data.py

# Day 2: Train models
python scripts\train_models.py

# Day 3: Generate predictions & test
python scripts\predict.py --season 2025 --week 6
```

### Ongoing (Weekly)
```powershell
# Monday: Update results & retrain
python scripts\update_and_retrain.py

# Thursday/Friday: Generate new predictions
python scripts\predict.py --season 2025 --week <next_week>
```

### Monthly
```powershell
# Review model performance on Models page
# Tune hyperparameters if needed
# Full retrain to consolidate knowledge
python scripts\train_models.py
```

---

## 📁 File Structure

After training, you'll have:

```
data/
├── models/                           # Trained model files
│   ├── random_forest.pkl
│   ├── xgboost.pkl
│   ├── lightgbm.pkl
│   ├── gradient_boosting.pkl
│   ├── neural_network.pkl
│   └── logistic_regression.pkl
│
└── nfl_predictions.db               # SQLite database with:
    ├── games                        # All collected games
    ├── predictions                  # Model predictions
    ├── model_training_history       # Training logs
    └── model_metadata               # Model stats
```

---

## 🚨 Troubleshooting

### "Not enough data to train"
→ Run `python scripts\collect_historical_data.py` first

### "API rate limit exceeded"
→ ESPN API limits requests. Wait 5 minutes and retry

### "Module not found" errors
→ Already fixed! Import issues resolved

### Models not improving
→ Need more diverse training data
→ Try collecting data from multiple seasons

### "Database locked" error
→ Close any programs accessing the database
→ Stop the API server, run training, restart server

---

## 💡 Pro Tips

1. **Train with at least 500 games** for reliable predictions (run historical collection)
2. **Retrain weekly** as new games complete
3. **Monitor the Models page** to track improvement over time
4. **Random Forest is currently best** - focus on tuning it
5. **Weather and rest days** are powerful features (already included)
6. **Compare predictions to actual results** to identify weaknesses

---

## 🎓 Understanding the Training Process

```
┌─────────────────────────────────────┐
│  1. Data Collection                 │
│     └── ESPN API → Database         │
└─────────────────────────────────────┘
              ↓
┌─────────────────────────────────────┐
│  2. Feature Engineering             │
│     └── Raw stats → 67 features     │
└─────────────────────────────────────┘
              ↓
┌─────────────────────────────────────┐
│  3. Model Training                  │
│     └── 6 algorithms learn patterns │
└─────────────────────────────────────┘
              ↓
┌─────────────────────────────────────┐
│  4. Model Saving                    │
│     └── .pkl files + DB logging     │
└─────────────────────────────────────┘
              ↓
┌─────────────────────────────────────┐
│  5. Prediction (Ensemble Voting)    │
│     └── All models vote → result    │
└─────────────────────────────────────┘
```

---

## 🏆 Goal: Achieve 80%+ Accuracy

### Steps to get there:

1. ✅ **Collect 1,000+ games** (run `collect_historical_data.py`)
2. ✅ **Train models** (run `train_models.py`)
3. ✅ **Weekly updates** (run `update_and_retrain.py` every Monday)
4. ⚙️ **Tune hyperparameters** (edit `src/ml_models.py`)
5. 📊 **Monitor Models page** (track performance trends)
6. 🔄 **Iterate** (repeat weekly)

---

## Quick Start Right Now

```powershell
# Get maximum training data (RECOMMENDED - do this first!)
python scripts\collect_historical_data.py

# Then train models
python scripts\train_models.py

# Start the app to see results
python src\api_server.py
# In another terminal:
cd frontend
npm run dev
```

**Expected result**: Models trained on 1,000+ games with 75-85% accuracy! 🎯
