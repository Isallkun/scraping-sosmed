"""
Quick Clear Database Script (No Confirmation)

This script clears all data from the database WITHOUT confirmation.
Use this for automation or when you're absolutely sure.

Usage:
    python clear_database_quick.py

WARNING: This will delete ALL data immediately!
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from database.db_operations import clear_all_data, DatabaseOperationError


def main():
    """Clear all data from database without confirmation."""
    
    print("Clearing database...")
    
    try:
        # Clear all data
        counts = clear_all_data()
        
        print(f"Database cleared: {counts['posts']} posts, {counts['sentiments']} sentiments, {counts['comments']} comments deleted")
        
    except DatabaseOperationError as e:
        print(f"ERROR: Failed to clear database: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"UNEXPECTED ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
