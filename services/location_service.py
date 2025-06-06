"""
Location Service
Central service for location management and integration
Implements the Facade Pattern to provide a unified interface for location operations
"""

from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime
import time
from models.location import Location
from database.location_repository import LocationRepository
from services.mapbox_client import MapboxClient
from services.weather_service import WeatherService

class LocationService:
    """
    Central service for location management
    Implements Facade Pattern to coordinate between location storage, 
    geocoding services, and weather integration
    """
    
    def __init__(self, mapbox_token: str = None):
        self.repository = LocationRepository()
        self.mapbox_client = MapboxClient(mapbox_token)
        self.weather_service = WeatherService()
        
        # Cache for location operations
        self._cache = {}
        self._cache_duration = 3600  # 1 hour in seconds
        
        print("Location Service initialized")
    
    def _is_cache_valid(self, cache_key: str) -> bool:
        """Check if cached data is still valid"""
        if cache_key not in self._cache:
            return False
        
        cached_time = self._cache[cache_key]['timestamp']
        current_time = time.time()
        
        return (current_time - cached_time) < self._cache_duration
    
    def _cache_location_data(self, cache_key: str, data: Any):
        """Cache location data with timestamp"""
        self._cache[cache_key] = {
            'data': data,
            'timestamp': time.time()
        }
    
    def create_location_from_address(self, address: str, name: str = None, 
                                   user_id: int = None, country: str = None) -> Dict[str, Any]:
        """
        Create location from address using geocoding
        
        Args:
            address: Address to geocode
            name: Optional custom name for location
            user_id: User ID who owns this location
            country: Optional country code for better results
            
        Returns:
            Result dictionary with success status and location data
        """
        try:
            # Try cache first
            cache_key = f"geocode_{address}_{country}"
            if self._is_cache_valid(cache_key):
                geocode_result = self._cache[cache_key]['data']
            else:
                # Geocode the address
                geocode_result = self.mapbox_client.geocode_address(address, country)
                if geocode_result:
                    self._cache_location_data(cache_key, geocode_result)
            
            if not geocode_result:
                return {
                    "success": False,
                    "message": "Address not found",
                    "address_searched": address
                }
            
            # Create location object
            location_name = name or geocode_result['name']
            location = Location(
                location_name,
                geocode_result['latitude'],
                geocode_result['longitude']
            )
            
            location.set_address(geocode_result['address'])
            location.set_location_type("address")
            
            if user_id:
                location.set_user_id(user_id)
            
            # Save to database
            location_id = self.repository.create_location(location)
            
            return {
                "success": True,
                "message": "Location created from address",
                "location": location.to_dict_safe(),
                "location_id": location_id,
                "geocoding_confidence": geocode_result.get('confidence', 1.0)
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"Error creating location from address: {str(e)}",
                "address_searched": address
            }
    
    def create_location_from_coordinates(self, latitude: float, longitude: float,
                                       name: str = None, user_id: int = None) -> Dict[str, Any]:
        """
        Create location from coordinates with reverse geocoding
        
        Args:
            latitude: Latitude coordinate
            longitude: Longitude coordinate
            name: Optional custom name
            user_id: User ID who owns this location
            
        Returns:
            Result dictionary with success status and location data
        """
        try:
            # Validate coordinates
            if not self.mapbox_client.validate_coordinates(latitude, longitude):
                return {
                    "success": False,
                    "message": "Invalid coordinates provided"
                }
            
            # Try reverse geocoding for address
            cache_key = f"reverse_{latitude}_{longitude}"
            if self._is_cache_valid(cache_key):
                reverse_result = self._cache[cache_key]['data']
            else:
                reverse_result = self.mapbox_client.reverse_geocode(latitude, longitude)
                if reverse_result:
                    self._cache_location_data(cache_key, reverse_result)
            
            # Create location object
            location_name = name or (reverse_result['address'] if reverse_result else f"Location at {latitude}, {longitude}")
            location = Location(location_name, latitude, longitude)
            
            if reverse_result:
                location.set_address(reverse_result['address'])
            
            location.set_location_type("point")
            
            if user_id:
                location.set_user_id(user_id)
            
            # Save to database
            location_id = self.repository.create_location(location)
            
            return {
                "success": True,
                "message": "Location created from coordinates",
                "location": location.to_dict_safe(),
                "location_id": location_id,
                "reverse_geocoded": bool(reverse_result)
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"Error creating location from coordinates: {str(e)}"
            }
    
    def create_location_from_area(self, geojson_polygon: Dict, name: str,
                                user_id: int = None) -> Dict[str, Any]:
        """
        Create location from drawn terrain area
        
        Args:
            geojson_polygon: GeoJSON polygon representing the drawn area
            name: Name for the area
            user_id: User ID who owns this location
            
        Returns:
            Result dictionary with success status and location data
        """
        try:
            # Calculate center point from polygon
            center_lat, center_lng = self._calculate_polygon_center(geojson_polygon)
            
            # Create location object
            location = Location(name, center_lat, center_lng)
            location.set_terrain_area(geojson_polygon)
            location.set_location_type("area")
            
            if user_id:
                location.set_user_id(user_id)
            
            # Try to get address for center point
            reverse_result = self.mapbox_client.reverse_geocode(center_lat, center_lng)
            if reverse_result:
                location.set_address(reverse_result['address'])
            
            # Save to database
            location_id = self.repository.create_location(location)
            
            return {
                "success": True,
                "message": "Location created from drawn area",
                "location": location.to_dict_safe(),
                "location_id": location_id,
                "area_size_sqm": location.get_area_size()
            }
            
        except ValueError as e:
            return {
                "success": False,
                "message": f"Invalid area data: {str(e)}"
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Error creating location from area: {str(e)}"
            }
    
    def search_locations(self, query: str, user_id: int = None, 
                        proximity: Tuple[float, float] = None) -> Dict[str, Any]:
        """
        Search for locations using multiple sources
        Combines database search with external geocoding
        
        Args:
            query: Search query
            user_id: Optional user ID to search user's locations
            proximity: Optional (lat, lng) tuple for proximity bias
            
        Returns:
            Combined search results
        """
        try:
            results = {
                "user_locations": [],
                "mapbox_places": [],
                "total_results": 0
            }
            
            # Search user's saved locations if user_id provided
            if user_id:
                user_locations = self.repository.search_locations_by_name(query, user_id)
                results["user_locations"] = [loc.to_dict_safe() for loc in user_locations]
            
            # Search external places via Mapbox
            cache_key = f"search_{query}_{proximity}"
            if self._is_cache_valid(cache_key):
                mapbox_places = self._cache[cache_key]['data']
            else:
                mapbox_places = self.mapbox_client.search_places(
                    query, proximity=proximity, limit=5
                )
                self._cache_location_data(cache_key, mapbox_places)
            
            results["mapbox_places"] = mapbox_places
            results["total_results"] = len(results["user_locations"]) + len(mapbox_places)
            
            return {
                "success": True,
                "message": f"Found {results['total_results']} results",
                "results": results
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"Search error: {str(e)}",
                "results": {"user_locations": [], "mapbox_places": [], "total_results": 0}
            }
    
    def get_location_with_weather(self, location_id: int, user_id: int = None) -> Dict[str, Any]:
        """
        Get location data combined with current weather information
        Implements the coordination between location and weather services
        
        Args:
            location_id: Location ID
            user_id: Optional user ID for security check
            
        Returns:
            Location data with weather information
        """
        try:
            # Get location from database
            location = self.repository.get_location_by_id(location_id)
            
            if not location:
                return {
                    "success": False,
                    "message": "Location not found"
                }
            
            # Security check - ensure user owns location if user_id provided
            if user_id and location.user_id != user_id:
                return {
                    "success": False,
                    "message": "Access denied to this location"
                }
            
            # Get center coordinates for weather
            center_lat, center_lng = location.get_center_point()
            
            # Get weather data
            weather_data = self.weather_service.get_weather_data(
                location.name, center_lat, center_lng
            )
            
            result = {
                "success": True,
                "location": location.to_dict_safe(),
                "weather": weather_data.to_dict() if weather_data else None
            }
            
            return result
            
        except Exception as e:
            return {
                "success": False,
                "message": f"Error getting location with weather: {str(e)}"
            }
    
    def get_user_locations(self, user_id: int, include_weather: bool = False) -> Dict[str, Any]:
        """
        Get all locations for a user, optionally with weather data
        
        Args:
            user_id: User ID
            include_weather: Whether to include weather data for each location
            
        Returns:
            List of user locations with optional weather data
        """
        try:
            locations = self.repository.get_locations_by_user(user_id)
            
            if not include_weather:
                return {
                    "success": True,
                    "locations": [loc.to_dict_safe() for loc in locations],
                    "count": len(locations)
                }
            
            # Include weather data for each location
            locations_with_weather = []
            for location in locations:
                center_lat, center_lng = location.get_center_point()
                weather_data = self.weather_service.get_weather_data(
                    location.name, center_lat, center_lng
                )
                
                location_dict = location.to_dict_safe()
                location_dict['weather'] = weather_data.to_dict() if weather_data else None
                locations_with_weather.append(location_dict)
            
            return {
                "success": True,
                "locations": locations_with_weather,
                "count": len(locations_with_weather)
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"Error getting user locations: {str(e)}",
                "locations": [],
                "count": 0
            }
    
    def update_location(self, location_id: int, updates: Dict, user_id: int = None) -> Dict[str, Any]:
        """
        Update existing location
        
        Args:
            location_id: Location ID to update
            updates: Dictionary with fields to update
            user_id: Optional user ID for security check
            
        Returns:
            Update result
        """
        try:
            # Get existing location
            location = self.repository.get_location_by_id(location_id)
            
            if not location:
                return {
                    "success": False,
                    "message": "Location not found"
                }
            
            # Security check
            if user_id and location.user_id != user_id:
                return {
                    "success": False,
                    "message": "Access denied to this location"
                }
            
            # Apply updates
            if 'name' in updates:
                location._name = updates['name'].strip()
            
            if 'latitude' in updates and 'longitude' in updates:
                if self.mapbox_client.validate_coordinates(updates['latitude'], updates['longitude']):
                    location._latitude = updates['latitude']
                    location._longitude = updates['longitude']
                else:
                    return {
                        "success": False,
                        "message": "Invalid coordinates provided"
                    }
            
            if 'address' in updates:
                location.set_address(updates['address'])
            
            if 'terrain_area' in updates:
                location.set_terrain_area(updates['terrain_area'])
            
            # Save changes
            self.repository.update_location(location)
            
            return {
                "success": True,
                "message": "Location updated successfully",
                "location": location.to_dict_safe()
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"Error updating location: {str(e)}"
            }
    
    def delete_location(self, location_id: int, user_id: int = None) -> Dict[str, Any]:
        """
        Delete location (soft delete)
        
        Args:
            location_id: Location ID to delete
            user_id: Optional user ID for security check
            
        Returns:
            Delete result
        """
        try:
            # Security check by getting location first
            if user_id:
                location = self.repository.get_location_by_id(location_id)
                if not location:
                    return {
                        "success": False,
                        "message": "Location not found"
                    }
                
                if location.user_id != user_id:
                    return {
                        "success": False,
                        "message": "Access denied to this location"
                    }
            
            # Perform soft delete
            self.repository.delete_location(location_id, user_id)
            
            return {
                "success": True,
                "message": "Location deleted successfully"
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"Error deleting location: {str(e)}"
            }
    
    def get_nearby_locations(self, latitude: float, longitude: float, 
                           radius_km: float = 10.0, user_id: int = None) -> Dict[str, Any]:
        """
        Get locations within radius of a point
        
        Args:
            latitude: Center latitude
            longitude: Center longitude
            radius_km: Search radius in kilometers
            user_id: Optional user ID filter
            
        Returns:
            List of nearby locations
        """
        try:
            if not self.mapbox_client.validate_coordinates(latitude, longitude):
                return {
                    "success": False,
                    "message": "Invalid coordinates provided"
                }
            
            locations = self.repository.get_locations_near_point(
                latitude, longitude, radius_km, user_id
            )
            
            # Calculate actual distances
            locations_with_distance = []
            for location in locations:
                distance = self.mapbox_client.calculate_distance(
                    latitude, longitude,
                    location.latitude, location.longitude
                )
                
                location_dict = location.to_dict_safe()
                location_dict['distance_km'] = round(distance, 2)
                locations_with_distance.append(location_dict)
            
            # Sort by distance
            locations_with_distance.sort(key=lambda x: x['distance_km'])
            
            return {
                "success": True,
                "locations": locations_with_distance,
                "count": len(locations_with_distance),
                "search_radius_km": radius_km
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"Error finding nearby locations: {str(e)}",
                "locations": [],
                "count": 0
            }
    
    def _calculate_polygon_center(self, geojson_polygon: Dict) -> Tuple[float, float]:
        """
        Calculate center point of GeoJSON polygon
        
        Args:
            geojson_polygon: GeoJSON polygon
            
        Returns:
            Tuple of (latitude, longitude)
        """
        coordinates = geojson_polygon["coordinates"][0]  # First ring
        
        # Simple centroid calculation
        lat_sum = sum(coord[1] for coord in coordinates)
        lng_sum = sum(coord[0] for coord in coordinates)
        count = len(coordinates)
        
        return (lat_sum / count, lng_sum / count)
    
    def clear_cache(self):
        """Clear location service cache"""
        self._cache.clear()
        print("Location cache cleared")
    
    def get_cache_info(self) -> Dict:
        """Get cache information for debugging"""
        return {
            'cached_items': len(self._cache),
            'cache_duration_hours': self._cache_duration / 3600,
            'cache_keys': list(self._cache.keys())
        }
    
    def clear_test_data(self):
        """Clear test data (for testing only)"""
        try:
            self.repository.clear_all_locations()
            self.clear_cache()
            print("Location test data cleared")
        except Exception as e:
            print(f"Warning: Could not clear location test data: {e}")