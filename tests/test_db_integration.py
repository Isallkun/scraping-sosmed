"""
Test script for database integration with Flask app.

This script tests that the database module is properly integrated
with the Flask application and that connections work correctly.
"""

import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.database import get_db, get_database_info


def test_database_integration():
    """Test database integration with Flask app"""
    print("=" * 70)
    print("Testing Database Integration with Flask App")
    print("=" * 70)
    
    # Create Flask app
    print("\n1. Creating Flask application...")
    try:
        app = create_app()
        print("   ✓ Flask app created successfully")
    except Exception as e:
        print(f"   ✗ Failed to create Flask app: {e}")
        return False
    
    # Test within app context
    with app.app_context():
        # Get database info
        print("\n2. Getting database connection info...")
        try:
            db_info = get_database_info()
            print(f"   Database: {db_info.get('database', 'unknown')}")
            print(f"   Connected: {db_info.get('connected', False)}")
            print(f"   Pool size: {db_info.get('pool_min', '?')}-{db_info.get('pool_max', '?')} connections")
            
            if not db_info.get('connected'):
                print(f"   ✗ Database not connected: {db_info.get('error', 'unknown error')}")
                return False
            
            print("   ✓ Database connection info retrieved")
        except Exception as e:
            print(f"   ✗ Failed to get database info: {e}")
            return False
        
        # Test database connection
        print("\n3. Testing database connection...")
        try:
            db = get_db()
            if db.test_connection():
                print("   ✓ Database connection test passed")
            else:
                print("   ✗ Database connection test failed")
                return False
        except Exception as e:
            print(f"   ✗ Database connection test failed: {e}")
            return False
        
        # Test query execution
        print("\n4. Testing query execution...")
        try:
            with db.get_cursor() as cursor:
                cursor.execute("SELECT 1 as test")
                result = cursor.fetchone()
                if result and result[0] == 1:
                    print("   ✓ Query execution successful")
                else:
                    print("   ✗ Query returned unexpected result")
                    return False
        except Exception as e:
            print(f"   ✗ Query execution failed: {e}")
            return False
        
        # Test database operations module
        print("\n5. Testing database operations module...")
        try:
            from database import db_operations
            print("   ✓ Database operations module imported successfully")
        except Exception as e:
            print(f"   ✗ Failed to import database operations: {e}")
            return False
        
        # Test checking if posts table exists
        print("\n6. Checking database schema...")
        try:
            with db.get_cursor() as cursor:
                cursor.execute("""
                    SELECT table_name 
                    FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name IN ('posts', 'sentiments', 'execution_logs')
                    ORDER BY table_name;
                """)
                tables = cursor.fetchall()
                
                if tables:
                    print(f"   Found {len(tables)} table(s):")
                    for table in tables:
                        print(f"     - {table[0]}")
                    print("   ✓ Database schema exists")
                else:
                    print("   ⚠ No tables found - database may need to be initialized")
                    print("   Run: python database/scripts/init_database.py")
        except Exception as e:
            print(f"   ✗ Failed to check database schema: {e}")
            return False
    
    print("\n" + "=" * 70)
    print("✓ All database integration tests passed!")
    print("=" * 70)
    return True


if __name__ == "__main__":
    success = test_database_integration()
    sys.exit(0 if success else 1)
