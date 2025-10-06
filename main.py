#!/usr/bin/env python3
"""
Main entry point for NFL Prediction Agent
"""

import sys
import os
import logging
from datetime import datetime

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from agent import NFLPredictionAgent

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('nfl_agent.log'),
        logging.StreamHandler()
    ]
)

def main():
    """Main function demonstrating agent usage."""
    print("🏈 NFL Game Prediction Agent")
    print("=" * 40)
    
    try:
        # Initialize the agent
        print("Initializing NFL Prediction Agent...")
        agent = NFLPredictionAgent()
        
        # Show menu
        while True:
            print("\nWhat would you like to do?")
            print("1. Collect historical data")
            print("2. Train models")
            print("3. Make predictions for current week")
            print("4. Make predictions for specific week")
            print("5. Update results and retrain")
            print("6. Show performance summary")
            print("7. Analyze specific team")
            print("8. Exit")
            
            choice = input("\nEnter your choice (1-8): ").strip()
            
            if choice == '1':
                collect_data(agent)
            elif choice == '2':
                train_models(agent)
            elif choice == '3':
                predict_current_week(agent)
            elif choice == '4':
                predict_specific_week(agent)
            elif choice == '5':
                update_and_retrain(agent)
            elif choice == '6':
                show_performance(agent)
            elif choice == '7':
                analyze_team(agent)
            elif choice == '8':
                print("Goodbye! 🏈")
                break
            else:
                print("Invalid choice. Please try again.")
                
    except KeyboardInterrupt:
        print("\nExiting...")
    except Exception as e:
        print(f"Error: {e}")
        logging.error(f"Main error: {e}")

def collect_data(agent):
    """Collect historical data."""
    try:
        start_year = int(input("Enter start year (e.g., 2018): "))
        end_year = int(input("Enter end year (e.g., 2024): "))
        
        print(f"Collecting data from {start_year} to {end_year}...")
        success = agent.collect_and_store_data(start_year, end_year)
        
        if success:
            print("✅ Data collection completed successfully!")
        else:
            print("❌ Data collection failed!")
            
    except ValueError:
        print("Please enter valid years.")
    except Exception as e:
        print(f"Error collecting data: {e}")

def train_models(agent):
    """Train ML models."""
    try:
        print("Training models... This may take a few minutes.")
        results = agent.train_models()
        
        if 'error' in results:
            print(f"❌ Training failed: {results['error']}")
        else:
            print("✅ Training completed successfully!")
            print(f"Models trained: {results['models_trained']}")
            print(f"Training samples: {results['training_samples']}")
            print(f"Features used: {results['features_used']}")
            
            print("\nModel Performance:")
            for model_name, metrics in results['results'].items():
                if 'error' not in metrics:
                    print(f"  {model_name}: {metrics['accuracy']:.4f}")
                    
    except Exception as e:
        print(f"Error training models: {e}")

def predict_current_week(agent):
    """Make predictions for current week."""
    try:
        print("Making predictions for current week...")
        predictions = agent.predict_current_week()
        
        if not predictions:
            print("No games found for current week.")
            return
            
        if len(predictions) == 1 and 'error' in predictions[0]:
            print(f"❌ Prediction error: {predictions[0]['error']}")
            return
        
        print(f"\n🏈 Predictions for Current Week ({len(predictions)} games):")
        print("-" * 60)
        
        for pred in predictions:
            confidence = pred.get('confidence_score', 0)
            confidence_emoji = "🔥" if confidence > 0.7 else "⚡" if confidence > 0.5 else "🤔"
            
            print(f"{confidence_emoji} {pred['away_team']} @ {pred['home_team']}")
            print(f"   Predicted Winner: {pred['predicted_winner']}")
            print(f"   Confidence: {confidence:.2f}")
            print(f"   Win Probability: {pred.get('win_probability', 0):.2f}")
            print()
            
    except Exception as e:
        print(f"Error making predictions: {e}")

def predict_specific_week(agent):
    """Make predictions for specific week."""
    try:
        season = int(input("Enter season year (e.g., 2024): "))
        week = int(input("Enter week number (1-18): "))
        
        print(f"Making predictions for {season} week {week}...")
        predictions = agent.predict_week(season, week)
        
        if not predictions:
            print("No games found for specified week.")
            return
            
        if len(predictions) == 1 and 'error' in predictions[0]:
            print(f"❌ Prediction error: {predictions[0]['error']}")
            return
        
        print(f"\n🏈 Predictions for {season} Week {week} ({len(predictions)} games):")
        print("-" * 60)
        
        for pred in predictions:
            confidence = pred.get('confidence_score', 0)
            confidence_emoji = "🔥" if confidence > 0.7 else "⚡" if confidence > 0.5 else "🤔"
            
            print(f"{confidence_emoji} {pred['away_team']} @ {pred['home_team']}")
            print(f"   Predicted Winner: {pred['predicted_winner']}")
            print(f"   Confidence: {confidence:.2f}")
            print()
            
    except ValueError:
        print("Please enter valid season and week numbers.")
    except Exception as e:
        print(f"Error making predictions: {e}")

def update_and_retrain(agent):
    """Update results and retrain models."""
    try:
        print("Updating game results and checking for retraining...")
        results = agent.update_results_and_retrain()
        
        if 'error' in results:
            print(f"❌ Update failed: {results['error']}")
            return
        
        print(f"✅ Updated {results['updated_games']} game results")
        
        if results['retrained']:
            print("🔄 Models were retrained with new data")
        else:
            print("ℹ️ No retraining was necessary")
            
    except Exception as e:
        print(f"Error updating: {e}")

def show_performance(agent):
    """Show performance summary."""
    try:
        print("Getting performance summary...")
        summary = agent.get_performance_summary()
        
        if 'error' in summary:
            print(f"❌ Error getting performance: {summary['error']}")
            return
        
        print("\n📊 Agent Performance Summary:")
        print("-" * 40)
        print(f"Overall Accuracy: {summary['overall_accuracy']:.3f}")
        print(f"Total Predictions: {summary['total_predictions']}")
        print(f"Correct Predictions: {summary['correct_predictions']}")
        print(f"Is Trained: {summary['is_trained']}")
        
        if summary['last_training_date']:
            print(f"Last Training: {summary['last_training_date'][:19]}")
        
        print("\nModel Accuracies:")
        for model_name, accuracy in summary['model_accuracies'].items():
            print(f"  {model_name}: {accuracy:.3f}")
            
    except Exception as e:
        print(f"Error getting performance: {e}")

def analyze_team(agent):
    """Analyze specific team."""
    try:
        team = input("Enter team abbreviation (e.g., KC, NE, SF): ").upper()
        season = int(input("Enter season year (e.g., 2024): "))
        
        print(f"Analyzing {team} for {season} season...")
        analysis = agent.get_team_analysis(team, season)
        
        if 'error' in analysis:
            print(f"❌ Analysis error: {analysis['error']}")
            return
        
        print(f"\n📈 {team} Analysis for {season}:")
        print("-" * 40)
        print(f"Record: {analysis['wins']}-{analysis['losses']}")
        print(f"Win Percentage: {analysis['win_percentage']:.3f}")
        print(f"Average Home Score: {analysis['average_home_score']:.1f}")
        print(f"Average Away Score: {analysis['average_away_score']:.1f}")
        print(f"Games Played: {analysis['total_games_played']}")
        
    except ValueError:
        print("Please enter valid inputs.")
    except Exception as e:
        print(f"Error analyzing team: {e}")

if __name__ == "__main__":
    main()