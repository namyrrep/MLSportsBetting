#!/usr/bin/env python3
"""Quick script to check predictions in database."""

from src.database import DatabaseManager

db = DatabaseManager()
conn = db.connection()
cursor = conn.cursor()

# Check predictions by model
cursor.execute('''
    SELECT model_name, COUNT(*) as cnt 
    FROM predictions 
    GROUP BY model_name
''')
print("Predictions by model:")
for row in cursor.fetchall():
    print(f"  {row[0]}: {row[1]} predictions")

# Check predictions by season/week
cursor.execute('''
    SELECT g.season, g.week, COUNT(*) as cnt 
    FROM predictions p 
    JOIN games g ON p.game_id = g.game_id 
    WHERE p.model_name = 'ensemble'
    GROUP BY g.season, g.week 
    ORDER BY g.season DESC, g.week DESC 
    LIMIT 10
''')
print("\nEnsemble predictions by week:")
for row in cursor.fetchall():
    print(f"  Season {row[0]} Week {row[1]}: {row[2]} predictions")

# Check games without winners (upcoming games)
cursor.execute('''
    SELECT season, week, COUNT(*) as cnt 
    FROM games 
    WHERE winner IS NULL OR winner = ''
    GROUP BY season, week 
    ORDER BY season DESC, week DESC
''')
print("\nUpcoming games (no winner yet):")
for row in cursor.fetchall():
    print(f"  Season {row[0]} Week {row[1]}: {row[2]} games")

# Check current predictions query
current_preds = db.get_current_predictions()
print(f"\nget_current_predictions() returns: {len(current_preds)} predictions")

# Check past predictions query
past_preds = db.get_past_predictions()
print(f"get_past_predictions() returns: {len(past_preds)} predictions")

conn.close()
