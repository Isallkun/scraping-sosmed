"""
Clear Database Script

This script clears all data from the database tables.
Use this when you want to start fresh with new data.

Usage:
    python clear_database.py

WARNING: This will delete ALL data from the database!
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from database.db_operations import clear_all_data, DatabaseOperationError


def main():
    """Clear all data from database with confirmation."""
    
    print("=" * 70)
    print("DATABASE CLEAR UTILITY")
    print("=" * 70)
    print()
    print("WARNING: This will delete ALL data from the following tables:")
    print("  - posts")
    print("  - sentiments")
    print("  - comments")
    print("  - execution_logs")
    print()
    print("This operation CANNOT be undone!")
    print()
    
    # Ask for confirmation
    confirmation = input("Are you sure you want to continue? (yes/no): ").strip().lower()
    
    if confirmation not in ['yes', 'y']:
        print()
        print("Operation cancelled.")
        print()
        return
    
    # Double confirmation for safety
    print()
    print("Please type 'DELETE ALL DATA' to confirm:")
    final_confirm = input("> ").strip()
    
    if final_confirm != 'DELETE ALL DATA':
        print()
        print("Operation cancelled.")
        print()
        return
    
    print()
    print("Clearing database...")
    print()
    
    try:
        # Clear all data
        counts = clear_all_data()
        
        print("=" * 70)
        print("DATABASE CLEARED SUCCESSFULLY")
        print("=" * 70)
        print()
        print("Records deleted:")
        print(f"  - Posts:          {counts['posts']:,}")
        print(f"  - Sentiments:     {counts['sentiments']:,}")
        print(f"  - Comments:       {counts['comments']:,}")
        print(f"  - Execution Logs: {counts['execution_logs']:,}")
        print()
        print("Database is now empty and ready for new data.")
        print()
        
    except DatabaseOperationError as e:
        print()
        print("=" * 70)
        print("ERROR: Failed to clear database")
        print("=" * 70)
        print()
        print(f"Error: {e}")
        print()
        print("Please check:")
        print("  - Database connection is working")
        print("  - PostgreSQL is running")
        print("  - Database credentials in .env are correct")
        print()
        sys.exit(1)
    except Exception as e:
        print()
        print("=" * 70)
        print("UNEXPECTED ERROR")
        print("=" * 70)
        print()
        print(f"Error: {e}")
        print()
        import traceback
        traceback.print_exc()
        print()
        sys.exit(1)


if __name__ == "__main__":
    main()
