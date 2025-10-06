"""
Example usage of the NFL Prediction Agent
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from agent import NFLPredictionAgent
import json

def example_usage():
    """Demonstrate basic usage of the NFL Prediction Agent."""
    
    print("NFL Prediction Agent - Example Usage")
    print("=" * 50)
    
    # Initialize the agent
    agent = NFLPredictionAgent()
    
    # Example 1: Collect some historical data (small sample for demo)
    print("\n1. Collecting historical data...")
    success = agent.collect_and_store_data(2023, 2023)  # Just 2023 season
    print(f"Data collection success: {success}")
    
    # Example 2: Train models
    print("\n2. Training models...")
    training_results = agent.train_models()
    if 'error' not in training_results:
        print(f"Training completed! Models trained: {training_results['models_trained']}")
        print(f"Training samples: {training_results['training_samples']}")
    else:
        print(f"Training error: {training_results['error']}")
    
    # Example 3: Make predictions for current week
    print("\n3. Making predictions for current week...")
    predictions = agent.predict_current_week()
    
    if predictions and 'error' not in predictions[0]:
        print(f"Generated {len(predictions)} predictions:")
        for pred in predictions[:3]:  # Show first 3
            print(f"  {pred['away_team']} @ {pred['home_team']}: {pred['predicted_winner']} "
                  f"(Confidence: {pred['confidence_score']:.2f})")
    else:
        print("No predictions available or error occurred")
    
    # Example 4: Get performance summary
    print("\n4. Performance summary...")
    summary = agent.get_performance_summary()
    if 'error' not in summary:
        print(f"Overall accuracy: {summary['overall_accuracy']:.3f}")
        print(f"Total predictions: {summary['total_predictions']}")
    else:
        print(f"Performance error: {summary['error']}")
    
    # Example 5: Analyze a team
    print("\n5. Team analysis example (Kansas City Chiefs)...")
    team_analysis = agent.get_team_analysis('KC', 2023)
    if 'error' not in team_analysis:
        print(f"KC 2023 Record: {team_analysis['wins']}-{team_analysis['losses']}")
        print(f"Win percentage: {team_analysis['win_percentage']:.3f}")
    else:
        print(f"Team analysis error: {team_analysis['error']}")

def advanced_example():
    """Demonstrate advanced features."""
    
    print("\nAdvanced Example - Custom Workflow")
    print("=" * 50)
    
    agent = NFLPredictionAgent()
    
    # Create custom game data for prediction
    custom_games = [
        {
            'game_id': 'test_game_1',
            'season': 2024,
            'week': 1,
            'game_date': '2024-09-08',
            'home_team': 'KC',
            'away_team': 'BAL',
            'home_score': None,
            'away_score': None,
            'winner': None,
            'home_spread': -3.0,
            'total_points': 47.5
        },
        {
            'game_id': 'test_game_2',
            'season': 2024,
            'week': 1,
            'game_date': '2024-09-08',
            'home_team': 'BUF',
            'away_team': 'NYJ',
            'home_score': None,
            'away_score': None,
            'winner': None,
            'home_spread': -6.5,
            'total_points': 45.0
        }
    ]
    
    # Make predictions for custom games
    print("Making predictions for custom games...")
    predictions = agent.predict_games(custom_games)
    
    for pred in predictions:
        if 'error' not in pred:
            print(f"\nGame: {pred['away_team']} @ {pred['home_team']}")
            print(f"Predicted Winner: {pred['predicted_winner']}")
            print(f"Win Probability: {pred['win_probability']:.3f}")
            print(f"Confidence: {pred['confidence_score']:.3f}")
        else:
            print(f"Prediction error: {pred['error']}")

def save_predictions_example():
    """Example of saving predictions to file."""
    
    print("\nSaving Predictions Example")
    print("=" * 50)
    
    agent = NFLPredictionAgent()
    
    # Get predictions
    predictions = agent.predict_current_week()
    
    if predictions and 'error' not in predictions[0]:
        # Save to JSON file
        output_file = "predictions_output.json"
        with open(output_file, 'w') as f:
            json.dump(predictions, f, indent=2)
        
        print(f"Predictions saved to {output_file}")
        
        # Also create a readable text format
        readable_file = "predictions_readable.txt"
        with open(readable_file, 'w') as f:
            f.write("NFL Game Predictions\n")
            f.write("=" * 30 + "\n\n")
            
            for pred in predictions:
                f.write(f"{pred['away_team']} @ {pred['home_team']}\n")
                f.write(f"Predicted Winner: {pred['predicted_winner']}\n")
                f.write(f"Confidence: {pred['confidence_score']:.2f}\n")
                f.write(f"Win Probability: {pred['win_probability']:.2f}\n")
                f.write("-" * 30 + "\n")
        
        print(f"Readable predictions saved to {readable_file}")
    else:
        print("No predictions to save")

if __name__ == "__main__":
    print("Choose an example to run:")
    print("1. Basic usage example")
    print("2. Advanced example")
    print("3. Save predictions example")
    
    choice = input("Enter choice (1-3): ").strip()
    
    if choice == '1':
        example_usage()
    elif choice == '2':
        advanced_example()
    elif choice == '3':
        save_predictions_example()
    else:
        print("Running basic example...")
        example_usage()