"""
Location Model for FarmVille
Represents geographical locations and terrain areas
"""

from datetime import datetime
from typing import Dict, List, Optional, Tuple
import json

class Location:
    """
    Location representation class
    Follows the same pattern as User and WeatherData models
    """
    
    def __init__(self, name: str, latitude: float, longitude: float):
        self._id = None
        self._name = name.strip()
        self._latitude = latitude
        self._longitude = longitude
        self._address = None
        self._terrain_area = None  # GeoJSON polygon for drawn areas
        self._location_type = "point"  # "point", "area", "address"
        self._created_at = datetime.now()
        self._user_id = None
        self._is_active = True
    
    # Properties following the established pattern
    @property
    def id(self) -> Optional[int]:
        return self._id
    
    @property
    def name(self) -> str:
        return self._name
    
    @property
    def latitude(self) -> float:
        return self._latitude
    
    @property
    def longitude(self) -> float:
        return self._longitude
    
    @property
    def address(self) -> Optional[str]:
        return self._address
    
    @property
    def terrain_area(self) -> Optional[Dict]:
        return self._terrain_area
    
    @property
    def location_type(self) -> str:
        return self._location_type
    
    @property
    def created_at(self) -> datetime:
        return self._created_at
    
    @property
    def user_id(self) -> Optional[int]:
        return self._user_id
    
    @property
    def is_active(self) -> bool:
        return self._is_active
    
    # Setters with validation
    def set_id(self, location_id: int):
        self._id = location_id
    
    def set_address(self, address: str):
        """Set the full address for this location"""
        self._address = address.strip() if address else None
        if self._address:
            self._location_type = "address"
    
    def set_terrain_area(self, geojson_polygon: Dict):
        """
        Set terrain area as GeoJSON polygon
        
        Args:
            geojson_polygon: GeoJSON polygon representing the drawn area
        """
        if self._validate_geojson_polygon(geojson_polygon):
            self._terrain_area = geojson_polygon
            self._location_type = "area"
        else:
            raise ValueError("Invalid GeoJSON polygon format")
    
    def set_user_id(self, user_id: int):
        self._user_id = user_id
    
    def set_location_type(self, location_type: str):
        """Set location type: point, area, or address"""
        valid_types = ["point", "area", "address"]
        if location_type in valid_types:
            self._location_type = location_type
        else:
            raise ValueError(f"Location type must be one of: {valid_types}")
    
    def _validate_coordinates(self) -> bool:
        """Validate latitude and longitude ranges"""
        return (-90 <= self._latitude <= 90) and (-180 <= self._longitude <= 180)
    
    def _validate_geojson_polygon(self, geojson: Dict) -> bool:
        """
        Validate GeoJSON polygon structure
        Simple validation - checks basic structure
        """
        if not isinstance(geojson, dict):
            return False
        
        required_fields = ["type", "coordinates"]
        if not all(field in geojson for field in required_fields):
            return False
        
        if geojson["type"] != "Polygon":
            return False
        
        # Check if coordinates is a list of coordinate rings
        coordinates = geojson["coordinates"]
        if not isinstance(coordinates, list) or len(coordinates) == 0:
            return False
        
        return True
    
    def get_center_point(self) -> Tuple[float, float]:
        """
        Get center point of the location
        For areas, calculates centroid; for points, returns the point
        """
        if self._location_type == "area" and self._terrain_area:
            return self._calculate_polygon_centroid()
        return (self._latitude, self._longitude)
    
    def _calculate_polygon_centroid(self) -> Tuple[float, float]:
        """Calculate centroid of polygon area"""
        if not self._terrain_area:
            return (self._latitude, self._longitude)
        
        coordinates = self._terrain_area["coordinates"][0]  # First ring
        
        # Simple centroid calculation
        lat_sum = sum(coord[1] for coord in coordinates)
        lng_sum = sum(coord[0] for coord in coordinates)
        count = len(coordinates)
        
        return (lat_sum / count, lng_sum / count)
    
    def get_area_size(self) -> Optional[float]:
        """
        Calculate approximate area in square meters
        Returns None for point locations
        """
        if self._location_type != "area" or not self._terrain_area:
            return None
        
        # Simplified area calculation using shoelace formula
        coordinates = self._terrain_area["coordinates"][0]
        
        area = 0.0
        j = len(coordinates) - 1
        
        for i in range(len(coordinates)):
            area += (coordinates[j][0] + coordinates[i][0]) * (coordinates[j][1] - coordinates[i][1])
            j = i
        
        # Convert to approximate square meters (rough calculation)
        # This is a simplified calculation - for precise areas, use proper geodetic libraries
        return abs(area) * 111000 * 111000 / 2  # Rough conversion
    
    def is_complete(self) -> bool:
        """Check if location has all required data"""
        has_coordinates = self._validate_coordinates()
        has_name = bool(self._name)
        
        if self._location_type == "area":
            return has_coordinates and has_name and self._terrain_area is not None
        
        return has_coordinates and has_name
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization"""
        return {
            'id': self._id,
            'name': self._name,
            'latitude': self._latitude,
            'longitude': self._longitude,
            'address': self._address,
            'terrain_area': self._terrain_area,
            'location_type': self._location_type,
            'created_at': self._created_at.isoformat() if self._created_at else None,
            'user_id': self._user_id,
            'is_active': self._is_active,
            'is_complete': self.is_complete(),
            'area_size': self.get_area_size()
        }
    
    def to_dict_safe(self) -> Dict:
        """Safe dictionary without sensitive data"""
        center_lat, center_lng = self.get_center_point()
        
        return {
            'id': self._id,
            'name': self._name,
            'latitude': self._latitude,
            'longitude': self._longitude,
            'center_latitude': center_lat,
            'center_longitude': center_lng,
            'address': self._address,
            'location_type': self._location_type,
            'area_size': self.get_area_size()
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Location':
        """Create Location instance from dictionary"""
        location = cls(
            data['name'],
            data['latitude'],
            data['longitude']
        )
        
        if 'id' in data:
            location.set_id(data['id'])
        
        if 'address' in data and data['address']:
            location.set_address(data['address'])
        
        if 'terrain_area' in data and data['terrain_area']:
            location.set_terrain_area(data['terrain_area'])
        
        if 'location_type' in data:
            location.set_location_type(data['location_type'])
        
        if 'user_id' in data:
            location.set_user_id(data['user_id'])
        
        if 'created_at' in data and data['created_at']:
            if isinstance(data['created_at'], str):
                location._created_at = datetime.fromisoformat(data['created_at'].replace('Z', '+00:00'))
            else:
                location._created_at = data['created_at']
        
        return location
    
    def __str__(self) -> str:
        return f"Location {self._name} ({self._location_type})"
    
    def __repr__(self) -> str:
        return (f"Location(id={self._id}, name='{self._name}', "
               f"type='{self._location_type}', complete={self.is_complete()})")