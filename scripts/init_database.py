#!/usr/bin/env python3
"""
Initialize the NFL Prediction Database
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from database import DatabaseManager
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    """Initialize the database with required tables."""
    try:
        logger.info("Initializing NFL Prediction database...")
        
        # Create data directory if it doesn't exist
        os.makedirs("data", exist_ok=True)
        
        # Initialize database
        db = DatabaseManager("data/nfl_games.db")
        
        logger.info("Database initialized successfully!")
        logger.info("You can now run data collection and training scripts.")
        
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()