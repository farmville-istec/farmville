"""
PostgreSQL connection - Updated with Location Support
"""

import pg8000.native
import os
from contextlib import contextmanager
from dotenv import load_dotenv

load_dotenv()

class DatabaseConnection:
    """PostgreSQL connection manager with location support"""
    
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
        """Create required tables with location support"""
        
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
        
        # Updated terrains table with location fields
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
            -- Location fields
            district_id INTEGER,
            district_name VARCHAR(100),
            municipality_id INTEGER,
            municipality_name VARCHAR(100),
            parish_id INTEGER,
            parish_name VARCHAR(100)
        );
        """
        
        try:
            with self.get_connection() as conn:
                conn.run(users_sql)
                conn.run(terrains_sql)
                
                # Create indexes for better performance
                conn.run("CREATE INDEX IF NOT EXISTS idx_terrains_user_id ON terrains(user_id);")
                conn.run("CREATE INDEX IF NOT EXISTS idx_terrains_district_id ON terrains(district_id);")
                conn.run("CREATE INDEX IF NOT EXISTS idx_terrains_municipality_id ON terrains(municipality_id);")
                conn.run("CREATE INDEX IF NOT EXISTS idx_terrains_parish_id ON terrains(parish_id);")
                conn.run("CREATE INDEX IF NOT EXISTS idx_terrains_user_location ON terrains(user_id, district_id, municipality_id);")
                
            print("✅ Database tables created successfully with location support")
            
        except Exception as e:
            print(f"❌ Database init error: {e}")
            pass
    
    def update_existing_tables(self):
        """Update existing terrains table to add location columns"""
        
        location_columns_sql = """
        DO $
        BEGIN
            -- Add location columns if they don't exist
            IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                          WHERE table_name = 'terrains' AND column_name = 'district_id') THEN
                ALTER TABLE terrains 
                ADD COLUMN district_id INTEGER,
                ADD COLUMN district_name VARCHAR(100),
                ADD COLUMN municipality_id INTEGER,
                ADD COLUMN municipality_name VARCHAR(100),
                ADD COLUMN parish_id INTEGER,
                ADD COLUMN parish_name VARCHAR(100);
                
                -- Add indexes
                CREATE INDEX idx_terrains_district_id ON terrains(district_id);
                CREATE INDEX idx_terrains_municipality_id ON terrains(municipality_id);
                CREATE INDEX idx_terrains_parish_id ON terrains(parish_id);
                CREATE INDEX idx_terrains_user_location ON terrains(user_id, district_id, municipality_id);
                
                RAISE NOTICE 'Location columns added to terrains table successfully';
            ELSE
                RAISE NOTICE 'Location columns already exist in terrains table';
            END IF;
        END
        $;
        """
        
        try:
            with self.get_connection() as conn:
                conn.run(location_columns_sql)
                
            print("✅ Database schema updated with location support")
            
        except Exception as e:
            print(f"❌ Database update error: {e}")
            pass