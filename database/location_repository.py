"""
Location Repository
Handles database operations for locations
Follows the same pattern as UserRepository
"""

from typing import Optional, List
import json
from models.location import Location
from database.connection import DatabaseConnection

class LocationRepository:
    """
    Repository for location data management
    Implements the Repository Pattern for data access abstraction
    """
    
    def __init__(self):
        self.db = DatabaseConnection()
        self._init_tables()
    
    def _init_tables(self):
        """Create locations table if it doesn't exist"""
        sql = """
        CREATE TABLE IF NOT EXISTS locations (
            id SERIAL PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            latitude DECIMAL(10, 8) NOT NULL,
            longitude DECIMAL(11, 8) NOT NULL,
            address TEXT,
            terrain_area JSONB,
            location_type VARCHAR(50) DEFAULT 'point',
            user_id INTEGER,
            created_at TIMESTAMP DEFAULT NOW(),
            is_active BOOLEAN DEFAULT TRUE,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        );
        
        CREATE INDEX IF NOT EXISTS idx_locations_user_id ON locations(user_id);
        CREATE INDEX IF NOT EXISTS idx_locations_coordinates ON locations(latitude, longitude);
        CREATE INDEX IF NOT EXISTS idx_locations_type ON locations(location_type);
        """
        
        try:
            with self.db.get_connection() as conn:
                conn.run(sql)
        except Exception as e:
            print(f"Warning: Could not create locations table: {e}")
    
    def create_location(self, location: Location) -> int:
        """
        Create new location in database
        
        Args:
            location: Location instance
            
        Returns:
            int: ID of created location
        """
        sql = """
        INSERT INTO locations (name, latitude, longitude, address, terrain_area, 
                             location_type, user_id)
        VALUES (:name, :latitude, :longitude, :address, :terrain_area, 
                :location_type, :user_id)
        RETURNING id;
        """
        
        # Convert terrain_area to JSON string if it exists
        terrain_area_json = None
        if location.terrain_area:
            terrain_area_json = json.dumps(location.terrain_area)
        
        with self.db.get_connection() as conn:
            result = conn.run(
                sql,
                name=location.name,
                latitude=location.latitude,
                longitude=location.longitude,
                address=location.address,
                terrain_area=terrain_area_json,
                location_type=location.location_type,
                user_id=location.user_id
            )
            location_id = result[0][0]
            location.set_id(location_id)
            return location_id
    
    def get_location_by_id(self, location_id: int) -> Optional[Location]:
        """
        Get location by ID
        
        Args:
            location_id: Location ID
            
        Returns:
            Location or None if not found
        """
        sql = "SELECT * FROM locations WHERE id = :location_id AND is_active = TRUE;"
        
        with self.db.get_connection() as conn:
            result = conn.run(sql, location_id=location_id)
            
            if not result:
                return None
            
            return self._row_to_location(result[0])
    
    def get_locations_by_user(self, user_id: int) -> List[Location]:
        """
        Get all locations for a specific user
        
        Args:
            user_id: User ID
            
        Returns:
            List of locations
        """
        sql = """
        SELECT * FROM locations 
        WHERE user_id = :user_id AND is_active = TRUE 
        ORDER BY created_at DESC;
        """
        
        with self.db.get_connection() as conn:
            result = conn.run(sql, user_id=user_id)
            
            return [self._row_to_location(row) for row in result]
    
    def get_locations_by_type(self, location_type: str, user_id: int = None) -> List[Location]:
        """
        Get locations by type, optionally filtered by user
        
        Args:
            location_type: Type of location (point, area, address)
            user_id: Optional user ID filter
            
        Returns:
            List of locations
        """
        if user_id:
            sql = """
            SELECT * FROM locations 
            WHERE location_type = :location_type AND user_id = :user_id AND is_active = TRUE 
            ORDER BY created_at DESC;
            """
            params = {'location_type': location_type, 'user_id': user_id}
        else:
            sql = """
            SELECT * FROM locations 
            WHERE location_type = :location_type AND is_active = TRUE 
            ORDER BY created_at DESC;
            """
            params = {'location_type': location_type}
        
        with self.db.get_connection() as conn:
            result = conn.run(sql, **params)
            
            return [self._row_to_location(row) for row in result]
    
    def get_locations_near_point(self, latitude: float, longitude: float, 
                                radius_km: float = 10.0, user_id: int = None) -> List[Location]:
        """
        Get locations within radius of a point
        Uses simple bounding box calculation for performance
        
        Args:
            latitude: Center latitude
            longitude: Center longitude
            radius_km: Radius in kilometers
            user_id: Optional user ID filter
            
        Returns:
            List of locations within radius
        """
        # Simple bounding box calculation
        # 1 degree latitude ≈ 111 km
        lat_delta = radius_km / 111.0
        lng_delta = radius_km / (111.0 * abs(cos(radians(latitude))))
        
        min_lat = latitude - lat_delta
        max_lat = latitude + lat_delta
        min_lng = longitude - lng_delta
        max_lng = longitude + lng_delta
        
        if user_id:
            sql = """
            SELECT * FROM locations 
            WHERE latitude BETWEEN :min_lat AND :max_lat 
            AND longitude BETWEEN :min_lng AND :max_lng
            AND user_id = :user_id AND is_active = TRUE
            ORDER BY created_at DESC;
            """
            params = {
                'min_lat': min_lat, 'max_lat': max_lat,
                'min_lng': min_lng, 'max_lng': max_lng,
                'user_id': user_id
            }
        else:
            sql = """
            SELECT * FROM locations 
            WHERE latitude BETWEEN :min_lat AND :max_lat 
            AND longitude BETWEEN :min_lng AND :max_lng
            AND is_active = TRUE
            ORDER BY created_at DESC;
            """
            params = {
                'min_lat': min_lat, 'max_lat': max_lat,
                'min_lng': min_lng, 'max_lng': max_lng
            }
        
        with self.db.get_connection() as conn:
            result = conn.run(sql, **params)
            
            return [self._row_to_location(row) for row in result]
    
    def update_location(self, location: Location) -> bool:
        """
        Update existing location
        
        Args:
            location: Location instance with updated data
            
        Returns:
            bool: True if updated successfully
        """
        sql = """
        UPDATE locations SET 
            name = :name,
            latitude = :latitude,
            longitude = :longitude,
            address = :address,
            terrain_area = :terrain_area,
            location_type = :location_type
        WHERE id = :location_id AND is_active = TRUE;
        """
        
        terrain_area_json = None
        if location.terrain_area:
            terrain_area_json = json.dumps(location.terrain_area)
        
        with self.db.get_connection() as conn:
            conn.run(
                sql,
                name=location.name,
                latitude=location.latitude,
                longitude=location.longitude,
                address=location.address,
                terrain_area=terrain_area_json,
                location_type=location.location_type,
                location_id=location.id
            )
            return True
    
    def delete_location(self, location_id: int, user_id: int = None) -> bool:
        """
        Soft delete location (set is_active = FALSE)
        
        Args:
            location_id: Location ID
            user_id: Optional user ID for security
            
        Returns:
            bool: True if deleted successfully
        """
        if user_id:
            sql = """
            UPDATE locations SET is_active = FALSE 
            WHERE id = :location_id AND user_id = :user_id;
            """
            params = {'location_id': location_id, 'user_id': user_id}
        else:
            sql = "UPDATE locations SET is_active = FALSE WHERE id = :location_id;"
            params = {'location_id': location_id}
        
        with self.db.get_connection() as conn:
            conn.run(sql, **params)
            return True
    
    def search_locations_by_name(self, search_term: str, user_id: int = None) -> List[Location]:
        """
        Search locations by name using ILIKE for case-insensitive search
        
        Args:
            search_term: Search term
            user_id: Optional user ID filter
            
        Returns:
            List of matching locations
        """
        search_pattern = f"%{search_term}%"
        
        if user_id:
            sql = """
            SELECT * FROM locations 
            WHERE name ILIKE :search_pattern AND user_id = :user_id AND is_active = TRUE
            ORDER BY created_at DESC;
            """
            params = {'search_pattern': search_pattern, 'user_id': user_id}
        else:
            sql = """
            SELECT * FROM locations 
            WHERE name ILIKE :search_pattern AND is_active = TRUE
            ORDER BY created_at DESC;
            """
            params = {'search_pattern': search_pattern}
        
        with self.db.get_connection() as conn:
            result = conn.run(sql, **params)
            
            return [self._row_to_location(row) for row in result]
    
    def clear_all_locations(self):
        """Remove all locations (for testing)"""
        sql = "DELETE FROM locations;"
        
        with self.db.get_connection() as conn:
            conn.run(sql)
    
    def _row_to_location(self, row) -> Location:
        """
        Convert database row to Location object
        
        Args:
            row: Database row
            
        Returns:
            Location instance
        """
        columns = ['id', 'name', 'latitude', 'longitude', 'address', 
                  'terrain_area', 'location_type', 'user_id', 'created_at', 'is_active']
        data = dict(zip(columns, row))
        
        # Parse terrain_area JSON if it exists
        if data['terrain_area']:
            try:
                data['terrain_area'] = json.loads(data['terrain_area'])
            except (json.JSONDecodeError, TypeError):
                data['terrain_area'] = None
        
        return Location.from_dict(data)

# Import for radius calculation
from math import cos, radians