
import logging
from database.db_connection import get_db_connection

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_comments_table():
    try:
        db = get_db_connection()
        with db.get_cursor(commit=True) as cursor:
            # Create comments table
            logger.info("Creating comments table...")
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS comments (
                    id SERIAL PRIMARY KEY,
                    post_id INTEGER REFERENCES posts(id) ON DELETE CASCADE,
                    author VARCHAR(255),
                    content TEXT,
                    timestamp TIMESTAMP,
                    sentiment VARCHAR(50),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    raw_data JSONB
                );
            """)
            
            # Create index
            logger.info("Creating index on comments(post_id)...")
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_comments_post_id ON comments(post_id);
            """)
            
            logger.info("Comments table initialized successfully.")
                
    except Exception as e:
        logger.error(f"Error: {e}")

if __name__ == "__main__":
    init_comments_table()
