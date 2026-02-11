
import logging
from database.db_connection import get_db_connection

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_schema():
    try:
        db = get_db_connection()
        with db.get_cursor() as cursor:
            # Check tables
            cursor.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
            """)
            tables = cursor.fetchall()
            print("Tables:", [t[0] for t in tables])
            
            # Check columns of posts
            cursor.execute("""
                SELECT column_name, data_type 
                FROM information_schema.columns 
                WHERE table_name = 'posts'
            """)
            columns = cursor.fetchall()
            print("\nPosts Columns:")
            for col in columns:
                print(f"- {col[0]}: {col[1]}")
                
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_schema()
