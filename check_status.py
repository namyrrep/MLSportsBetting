#!/usr/bin/env python3
"""Quick database status check"""

from src.database import DatabaseManager

def main():
    db = DatabaseManager()
    summary = db.get_data_coverage_summary()
    
    print("📊 Final Database Status:")
    print("Available keys:", list(summary.keys()))
    print(summary)

if __name__ == "__main__":
    main()