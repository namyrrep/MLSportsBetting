# 🏈 NFL Game Prediction ML Agent - Project Overview

## What This Project Does

This is a complete machine learning system that predicts the winning team of NFL football games. The agent:

- **Learns from History**: Collects and stores historical NFL game data
- **Smart Features**: Creates intelligent features like team momentum, head-to-head records, and ELO ratings
- **Multiple Models**: Uses various ML algorithms (Random Forest, XGBoost, Neural Networks, etc.)
- **Self-Improving**: Automatically retrains with new game results
- **Easy to Use**: Simple command-line interface and interactive mode

## Key Features

### 🔍 Data Collection
- Automatically fetches NFL game data from ESPN API
- Stores historical games, scores, and statistics
- Handles multiple seasons of data

### 🧠 Machine Learning
- **6 Different Models**: Random Forest, XGBoost, LightGBM, Logistic Regression, Gradient Boosting, Neural Networks
- **Ensemble Predictions**: Combines multiple models for better accuracy
- **Feature Engineering**: Creates 20+ features from raw game data
- **Performance Tracking**: Monitors and reports prediction accuracy

### 📊 Features Used for Predictions
- Recent team performance (wins/losses in last 5 games)
- Historical head-to-head matchups
- Home field advantage
- Team momentum and win streaks
- ELO ratings
- Scoring averages and defensive performance
- Game context (playoffs, division games, etc.)

### 💾 Database Management
- SQLite database for reliable data storage
- Tracks games, predictions, and model performance
- Automatic data updates and result validation

## Quick Start Guide

1. **Install**: Run `setup.bat` (Windows) or install requirements manually
2. **Collect Data**: Gather historical game data (2018-2024 recommended)
3. **Train Models**: Train the ML models on historical data
4. **Predict**: Make predictions for upcoming games

## Usage Examples

### Interactive Mode (Recommended for Beginners)
```bash
python main.py
```
Follow the menu to collect data, train models, and make predictions.

### Command Line Mode
```bash
# Collect data
python scripts/collect_data.py --start-year 2020 --end-year 2024

# Train models
python scripts/train_models.py

# Make predictions
python scripts/predict.py --current
```

### Programmatic Usage
```python
from src.agent import NFLPredictionAgent

agent = NFLPredictionAgent()
agent.collect_and_store_data(2020, 2024)
agent.train_models()
predictions = agent.predict_current_week()
```

## Project Structure

```
MLSportsBetting/
├── 📁 src/                    # Core source code
│   ├── agent.py              # Main prediction agent
│   ├── database.py           # Database management
│   ├── data_collector.py     # Data fetching from APIs
│   ├── feature_engineering.py # Feature creation
│   └── ml_models.py          # Machine learning models
│
├── 📁 scripts/               # Execution scripts
│   ├── init_database.py      # Setup database
│   ├── collect_data.py       # Collect historical data
│   ├── train_models.py       # Train ML models
│   └── predict.py            # Make predictions
│
├── 📁 config/                # Configuration files
├── 📁 data/                  # Data storage
│   ├── nfl_games.db         # SQLite database
│   └── models/              # Trained model files
│
├── main.py                   # Interactive main program
├── example_usage.py          # Usage examples
├── requirements.txt          # Python dependencies
└── README.md                # Documentation
```

## Model Performance

The agent tracks its performance and typically achieves:
- **Accuracy**: 55-65% (better than random 50%)
- **Best Models**: XGBoost and Random Forest usually perform best
- **Improvement**: Accuracy improves with more historical data

## Technical Details

### Models Used
1. **Random Forest**: Ensemble of decision trees
2. **XGBoost**: Gradient boosting with advanced optimizations
3. **LightGBM**: Fast gradient boosting
4. **Logistic Regression**: Linear probability model
5. **Gradient Boosting**: Sequential ensemble learning
6. **Neural Network**: Multi-layer perceptron

### Features Engineered
- Recent performance metrics (5-game windows)
- Head-to-head historical records
- Home/away performance splits
- Team momentum indicators
- ELO rating system
- Situational features (playoffs, primetime, etc.)

### Data Sources
- ESPN API for game data and scores
- Automatic data collection and updates
- Historical data back to 2018 (customizable)

## Important Notes

⚠️ **Educational Purpose Only**: This is for learning and testing machine learning concepts, not for actual gambling.

📈 **Performance Reality**: NFL games are inherently difficult to predict due to many variables (injuries, weather, motivation, etc.). Even professional analysts struggle to exceed 60% accuracy.

🔄 **Continuous Learning**: The agent improves over time as it learns from new game results.

## Getting Help

1. **Setup Issues**: Check `SETUP.md` for detailed installation guide
2. **Usage Questions**: Run `python main.py` for interactive help
3. **Examples**: See `example_usage.py` for code examples
4. **Errors**: Check logs in the console output

## Future Enhancements

Potential improvements you could add:
- Weather data integration
- Injury reports
- Betting odds incorporation
- Player statistics
- Advanced team chemistry metrics
- Web interface for easier use

This project provides a solid foundation for sports prediction and can be extended with additional features as needed!