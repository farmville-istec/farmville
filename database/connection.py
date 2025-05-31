"""
PostgreSQL connection
"""

import pg8000.native
import os
from contextlib import contextmanager
from dotenv import load_dotenv

load_dotenv()

class DatabaseConnection:
    """PostgreSQL connection manager"""
    
    def __init__(self):
        self.config = {
            'host': os.getenv('POSTGRES_HOST'),
            'port': int(os.getenv('POSTGRES_PORT')),
            'database': os.getenv('POSTGRES_DB'),
            'user': os.getenv('POSTGRES_USER'),
            'password': os.getenv('POSTGRES_PASSWORD')
        }
    
    @contextmanager
    def get_connection(self):
        """Get database connection"""
        conn = None
        try:
            conn = pg8000.native.Connection(**self.config)
            yield conn
        except Exception as e:
            if conn:
                conn.rollback()
            raise e
        finally:
            if conn:
                conn.close()
    
    def init_tables(self):
        """Create required tables"""
        sql = """
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            username VARCHAR(50) UNIQUE NOT NULL,
            email VARCHAR(100),
            password_hash VARCHAR(64) NOT NULL,
            created_at TIMESTAMP DEFAULT NOW(),
            last_login TIMESTAMP
        );
        """
        
        try:
            with self.get_connection() as conn:
                conn.run(sql)
            print("✅ Database tables created")
        except Exception as e:
            print(f"❌ Database init error: {e}")
            raise