# Setup and Installation Guide

## Quick Setup (Recommended)

1. **Install Python Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Initialize Database**:
   ```bash
   python scripts/init_database.py
   ```

3. **Collect Historical Data** (This may take 10-15 minutes):
   ```bash
   python scripts/collect_data.py --start-year 2020 --end-year 2024
   ```

4. **Train Models** (This may take 5-10 minutes):
   ```bash
   python scripts/train_models.py
   ```

5. **Make Predictions**:
   ```bash
   python scripts/predict.py --current
   ```

## Alternative: Interactive Mode

Run the main interactive application:
```bash
python main.py
```

## Manual Setup Steps

If you prefer to set up manually or encounter issues:

### 1. Install Required Libraries

Make sure you have Python 3.8+ installed, then:

```bash
# Install core data science libraries
pip install pandas numpy scikit-learn

# Install ML libraries
pip install xgboost lightgbm

# Install utilities
pip install requests beautifulsoup4 joblib tqdm

# Install visualization (optional)
pip install matplotlib seaborn plotly
```

### 2. Create Directory Structure

The project should have this structure:
```
MLSportsBetting/
├── data/
│   ├── models/
│   └── nfl_games.db (created automatically)
├── src/
│   ├── agent.py
│   ├── database.py
│   ├── data_collector.py
│   ├── feature_engineering.py
│   └── ml_models.py
├── scripts/
├── config/
└── main.py
```

### 3. Test Installation

Run this to test if everything is working:

```python
from src.agent import NFLPredictionAgent
agent = NFLPredictionAgent()
print("✅ Installation successful!")
```

## Common Issues and Solutions

### Import Errors
If you get import errors, make sure you're running scripts from the project root directory:
```bash
cd MLSportsBetting
python main.py
```

### Database Issues
If you encounter database errors:
```bash
python scripts/init_database.py
```

### Missing Dependencies
Install any missing dependencies:
```bash
pip install <missing-library-name>
```

### Data Collection Issues
If data collection fails, it might be due to:
- Network connectivity
- API rate limiting
- Changed API endpoints

Try reducing the date range or running collection in smaller batches.

## Usage Examples

### Basic Usage
```python
from src.agent import NFLPredictionAgent

# Initialize agent
agent = NFLPredictionAgent()

# Collect data (one-time setup)
agent.collect_and_store_data(2020, 2024)

# Train models
agent.train_models()

# Make predictions
predictions = agent.predict_current_week()
for pred in predictions:
    print(f"{pred['away_team']} @ {pred['home_team']}: {pred['predicted_winner']}")
```

### Performance Monitoring
```python
# Check agent performance
summary = agent.get_performance_summary()
print(f"Accuracy: {summary['overall_accuracy']:.3f}")
```

### Team Analysis
```python
# Analyze specific team
analysis = agent.get_team_analysis('KC', 2024)
print(f"KC Record: {analysis['wins']}-{analysis['losses']}")
```

## Advanced Configuration

Edit `config/config.json` to customize:
- Data collection parameters
- Model training settings
- Feature engineering options
- Logging configuration

## Troubleshooting

1. **Low Accuracy**: Collect more historical data and retrain models
2. **Slow Performance**: Reduce the number of models or use fewer features
3. **Memory Issues**: Process data in smaller batches
4. **API Errors**: Add delays between API calls or use cached data

## Notes

- This is for educational/testing purposes only
- Models need regular retraining with new data
- Prediction accuracy will improve with more historical data
- The agent automatically saves and loads trained models