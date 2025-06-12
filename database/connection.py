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
            'host': os.getenv('POSTGRES_HOST', 'localhost'),
            'port': int(os.getenv('POSTGRES_PORT', 5432)),
            'database': os.getenv('POSTGRES_DB', 'farmville'),
            'user': os.getenv('POSTGRES_USER', 'farmville'),
            'password': os.getenv('POSTGRES_PASSWORD', 'farmville')
        }
    
    @contextmanager
    def get_connection(self):
        """Get database connection"""
        conn = None
        try:
            conn = pg8000.native.Connection(**self.config)
            yield conn
        except Exception as e:
            print(f"Database error: {e}")
            raise e
        finally:
            if conn:
                conn.close()
    
    def test_connection(self) -> bool:
        """Testa conexão à base de dados"""
        try:
            with self.get_connection() as conn:
                result = conn.run("SELECT 1;")
                return len(result) > 0
        except Exception as e:
            print(f"Connection test failed: {e}")
            return False
    
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
            district VARCHAR(100),
            municipality VARCHAR(100),
            parish VARCHAR(100),
            crop_type VARCHAR(50),
            area_hectares DECIMAL(8, 2),
            notes TEXT,
            created_at TIMESTAMP DEFAULT NOW(),
            updated_at TIMESTAMP DEFAULT NOW()
        );
        """
        
        try:
            with self.get_connection() as conn:
                conn.run(users_sql)
                conn.run(terrains_sql)
                
                conn.run("CREATE INDEX IF NOT EXISTS idx_terrains_user_id ON terrains(user_id);")
                conn.run("CREATE INDEX IF NOT EXISTS idx_terrains_location ON terrains(district, municipality, parish);")
                
            print("✅ Database tables created successfully")
            
        except Exception as e:
            print(f"❌ Database init error: {e}")
            pass
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
            updated_at TIMESTAMP DEFAULT NOW()
        );
        """
        
        try:
            with self.get_connection() as conn:
                conn.run(users_sql)
                conn.run(terrains_sql)
                
                conn.run("CREATE INDEX IF NOT EXISTS idx_terrains_user_id ON terrains(user_id);")
                
            print("✅ Database tables created successfully")
            
        except Exception as e:
            print(f"❌ Database init error: {e}")
            pass