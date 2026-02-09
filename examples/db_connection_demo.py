"""
Database Connection Module Demo

This script demonstrates how to use the database connection module
for connecting to PostgreSQL with connection pooling and retry logic.

Prerequisites:
- PostgreSQL server running
- Environment variables configured in .env file
- Database schema created (run migrations first)
"""

import sys
import os

# Add parent directory to path to import modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from database.db_connection import (
    DatabaseConnection,
    DatabaseConnectionError,
    get_db_connection,
    close_db_connection
)


def demo_basic_connection():
    """Demo: Basic connection and query"""
    print("\n=== Demo 1: Basic Connection ===")
    
    try:
        # Create database connection
        db = DatabaseConnection()
        
        # Test the connection
        if db.test_connection():
            print("✓ Database connection successful!")
        else:
            print("✗ Database connection failed!")
            return
        
        # Execute a simple query
        with db.get_cursor() as cursor:
            cursor.execute("SELECT version()")
            version = cursor.fetchone()
            print(f"✓ PostgreSQL version: {version[0]}")
        
        # Close connections
        db.close_all_connections()
        print("✓ Connections closed")
        
    except DatabaseConnectionError as e:
        print(f"✗ Database error: {e}")
    except Exception as e:
        print(f"✗ Unexpected error: {e}")


def demo_context_manager():
    """Demo: Using context manager for automatic cleanup"""
    print("\n=== Demo 2: Context Manager ===")
    
    try:
        # Use context manager for automatic cleanup
        with DatabaseConnection() as db:
            print("✓ Database connection opened")
            
            # Execute query
            with db.get_cursor() as cursor:
                cursor.execute("SELECT COUNT(*) FROM information_schema.tables")
                count = cursor.fetchone()
                print(f"✓ Number of tables in database: {count[0]}")
        
        print("✓ Connections automatically closed")
        
    except DatabaseConnectionError as e:
        print(f"✗ Database error: {e}")
    except Exception as e:
        print(f"✗ Unexpected error: {e}")


def demo_transaction_with_commit():
    """Demo: Transaction with commit"""
    print("\n=== Demo 3: Transaction with Commit ===")
    
    try:
        with DatabaseConnection() as db:
            # Create a test table
            with db.get_cursor(commit=True) as cursor:
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS demo_test (
                        id SERIAL PRIMARY KEY,
                        message TEXT NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                print("✓ Test table created")
            
            # Insert data with commit
            with db.get_cursor(commit=True) as cursor:
                cursor.execute(
                    "INSERT INTO demo_test (message) VALUES (%s)",
                    ("Hello from database connection demo!",)
                )
                print("✓ Data inserted")
            
            # Query the data
            with db.get_cursor() as cursor:
                cursor.execute("SELECT * FROM demo_test ORDER BY id DESC LIMIT 1")
                row = cursor.fetchone()
                print(f"✓ Latest record: ID={row[0]}, Message='{row[1]}'")
            
            # Clean up test table
            with db.get_cursor(commit=True) as cursor:
                cursor.execute("DROP TABLE IF EXISTS demo_test")
                print("✓ Test table dropped")
        
    except DatabaseConnectionError as e:
        print(f"✗ Database error: {e}")
    except Exception as e:
        print(f"✗ Unexpected error: {e}")


def demo_error_handling():
    """Demo: Error handling and rollback"""
    print("\n=== Demo 4: Error Handling and Rollback ===")
    
    try:
        with DatabaseConnection() as db:
            # Try to execute invalid SQL
            try:
                with db.get_cursor(commit=True) as cursor:
                    cursor.execute("SELECT * FROM nonexistent_table")
            except Exception as e:
                print(f"✓ Error caught and handled: {type(e).__name__}")
                print("✓ Transaction automatically rolled back")
            
            # Connection should still work after error
            if db.test_connection():
                print("✓ Connection still healthy after error")
        
    except DatabaseConnectionError as e:
        print(f"✗ Database error: {e}")
    except Exception as e:
        print(f"✗ Unexpected error: {e}")


def demo_singleton_pattern():
    """Demo: Global singleton instance"""
    print("\n=== Demo 5: Singleton Pattern ===")
    
    try:
        # Get global instance
        db1 = get_db_connection()
        print("✓ Got first database instance")
        
        # Get global instance again - should be same object
        db2 = get_db_connection()
        print("✓ Got second database instance")
        
        if db1 is db2:
            print("✓ Both instances are the same object (singleton)")
        else:
            print("✗ Instances are different (not singleton)")
        
        # Test connection
        if db1.test_connection():
            print("✓ Singleton instance works correctly")
        
        # Close global instance
        close_db_connection()
        print("✓ Global instance closed")
        
    except DatabaseConnectionError as e:
        print(f"✗ Database error: {e}")
    except Exception as e:
        print(f"✗ Unexpected error: {e}")


def demo_connection_pool():
    """Demo: Connection pooling"""
    print("\n=== Demo 6: Connection Pooling ===")
    
    try:
        # Create connection with custom pool size
        with DatabaseConnection(min_conn=2, max_conn=5) as db:
            print("✓ Connection pool created (min=2, max=5)")
            
            # Get multiple connections
            connections = []
            for i in range(3):
                conn = db.get_connection()
                connections.append(conn)
                print(f"✓ Acquired connection {i+1}")
            
            # Return connections to pool
            for i, conn in enumerate(connections):
                db.return_connection(conn)
                print(f"✓ Returned connection {i+1} to pool")
            
            print("✓ All connections returned to pool")
        
    except DatabaseConnectionError as e:
        print(f"✗ Database error: {e}")
    except Exception as e:
        print(f"✗ Unexpected error: {e}")


def main():
    """Run all demos"""
    print("=" * 60)
    print("Database Connection Module Demo")
    print("=" * 60)
    
    # Check if database configuration is available
    if not os.getenv('DATABASE_URL') and not os.getenv('DB_HOST'):
        print("\n⚠ Warning: Database configuration not found!")
        print("Please set DATABASE_URL or DB_* environment variables in .env file")
        print("\nExample .env configuration:")
        print("DATABASE_URL=postgresql://user:password@localhost:5432/dbname")
        print("\nOr:")
        print("DB_HOST=localhost")
        print("DB_PORT=5432")
        print("DB_NAME=dbname")
        print("DB_USER=user")
        print("DB_PASSWORD=password")
        return
    
    # Run demos
    try:
        demo_basic_connection()
        demo_context_manager()
        demo_transaction_with_commit()
        demo_error_handling()
        demo_singleton_pattern()
        demo_connection_pool()
        
        print("\n" + "=" * 60)
        print("All demos completed!")
        print("=" * 60)
        
    except KeyboardInterrupt:
        print("\n\nDemo interrupted by user")
    except Exception as e:
        print(f"\n\n✗ Demo failed with error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
