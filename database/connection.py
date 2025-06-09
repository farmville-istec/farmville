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
        
        users_sql = """
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            username VARCHAR(50) UNIQUE NOT NULL,
            email VARCHAR(100),
            password_hash VARCHAR(64) NOT NULL,
            created_at TIMESTAMP DEFAULT NOW(),
            last_login TIMESTAMP
        );
        """
        
        terrains_sql = """
        CREATE TABLE IF NOT EXISTS terrains (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            name VARCHAR(100) NOT NULL,
            latitude DECIMAL(10, 8) NOT NULL,
            longitude DECIMAL(11, 8) NOT NULL,
            crop_type VARCHAR(50),
            area_hectares DECIMAL(8, 2),
            notes TEXT,
            created_at TIMESTAMP DEFAULT NOW(),
            updated_at TIMESTAMP DEFAULT NOW(),
            
            -- Constraints
            CONSTRAINT check_latitude CHECK (latitude >= -90 AND latitude <= 90),
            CONSTRAINT check_longitude CHECK (longitude >= -180 AND longitude <= 180),
            CONSTRAINT check_area_positive CHECK (area_hectares IS NULL OR area_hectares > 0),
            CONSTRAINT check_name_not_empty CHECK (LENGTH(TRIM(name)) > 0)
        );
        """
        
        indices_sql = """
        CREATE INDEX IF NOT EXISTS idx_terrains_user_id ON terrains(user_id);
        CREATE INDEX IF NOT EXISTS idx_terrains_coordinates ON terrains(latitude, longitude);
        CREATE INDEX IF NOT EXISTS idx_terrains_created_at ON terrains(created_at DESC);
        """
        
        try:
            with self.get_connection() as conn:
                conn.run(users_sql)
                conn.run(terrains_sql)
                conn.run(indices_sql)
                
            print("✅ Database tables created successfully")
            
        except Exception as e:
            print(f"❌ Database init error: {e}")
            raise