"""
Mapbox Client
Handles integration with Mapbox APIs
Implements the Adapter Pattern to abstract external API details
"""

import requests
import os
from typing import Dict, List, Optional, Tuple
from dotenv import load_dotenv

load_dotenv()

class MapboxClient:
    """
    Client for Mapbox API integration
    Implements Adapter Pattern to provide a unified interface for location services
    """
    
    def __init__(self, access_token: str = None):
        self.access_token = access_token or os.getenv('MAPBOX_ACCESS_TOKEN')
        if not self.access_token:
            raise ValueError("Mapbox access token is required")
        
        self.base_url = "https://api.mapbox.com"
        self.geocoding_url = f"{self.base_url}/geocoding/v5/mapbox.places"
        
        # Session for connection pooling and better performance
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'FarmVille/1.0'
        })
    
    def geocode_address(self, address: str, country: str = None) -> Optional[Dict]:
        """
        Convert address to coordinates using Mapbox Geocoding API
        
        Args:
            address: Address to geocode
            country: Optional country code to limit search (e.g., 'pt', 'us')
            
        Returns:
            Dict with location data or None if not found
        """
        try:
            params = {
                'access_token': self.access_token,
                'limit': 1,
                'types': 'address,place,locality'
            }
            
            if country:
                params['country'] = country
            
            url = f"{self.geocoding_url}/{requests.utils.quote(address)}.json"
            
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get('features'):
                feature = data['features'][0]
                coordinates = feature['geometry']['coordinates']
                
                return {
                    'name': address,
                    'longitude': coordinates[0],
                    'latitude': coordinates[1],
                    'address': feature.get('place_name', address),
                    'confidence': 1.0,  # Mapbox doesn't provide confidence scores
                    'place_type': feature.get('place_type', ['unknown'])[0],
                    'context': self._extract_context(feature)
                }
            
            return None
            
        except requests.RequestException as e:
            print(f"Geocoding error: {e}")
            return None
        except (KeyError, IndexError, ValueError) as e:
            print(f"Response parsing error: {e}")
            return None
    
    def reverse_geocode(self, latitude: float, longitude: float) -> Optional[Dict]:
        """
        Convert coordinates to address using Mapbox Reverse Geocoding
        
        Args:
            latitude: Latitude coordinate
            longitude: Longitude coordinate
            
        Returns:
            Dict with address data or None if not found
        """
        try:
            params = {
                'access_token': self.access_token,
                'limit': 1,
                'types': 'address,place,locality'
            }
            
            url = f"{self.geocoding_url}/{longitude},{latitude}.json"
            
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get('features'):
                feature = data['features'][0]
                
                return {
                    'latitude': latitude,
                    'longitude': longitude,
                    'address': feature.get('place_name', 'Unknown location'),
                    'place_type': feature.get('place_type', ['unknown'])[0],
                    'context': self._extract_context(feature)
                }
            
            return None
            
        except requests.RequestException as e:
            print(f"Reverse geocoding error: {e}")
            return None
        except (KeyError, IndexError, ValueError) as e:
            print(f"Response parsing error: {e}")
            return None
    
    def search_places(self, query: str, proximity: Tuple[float, float] = None, 
                     country: str = None, limit: int = 5) -> List[Dict]:
        """
        Search for places using Mapbox Places API
        
        Args:
            query: Search query
            proximity: Optional (lat, lng) tuple to bias results
            country: Optional country code
            limit: Maximum number of results
            
        Returns:
            List of place dictionaries
        """
        try:
            params = {
                'access_token': self.access_token,
                'limit': min(limit, 10),  # Mapbox limit
                'types': 'address,place,locality,poi'
            }
            
            if proximity:
                params['proximity'] = f"{proximity[1]},{proximity[0]}"  # lng,lat format
            
            if country:
                params['country'] = country
            
            url = f"{self.geocoding_url}/{requests.utils.quote(query)}.json"
            
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            places = []
            
            for feature in data.get('features', []):
                coordinates = feature['geometry']['coordinates']
                
                place = {
                    'name': feature.get('text', query),
                    'longitude': coordinates[0],
                    'latitude': coordinates[1],
                    'address': feature.get('place_name', ''),
                    'place_type': feature.get('place_type', ['unknown'])[0],
                    'context': self._extract_context(feature),
                    'relevance': feature.get('relevance', 0.0)
                }
                places.append(place)
            
            # Sort by relevance (highest first)
            places.sort(key=lambda x: x['relevance'], reverse=True)
            
            return places
            
        except requests.RequestException as e:
            print(f"Places search error: {e}")
            return []
        except (KeyError, IndexError, ValueError) as e:
            print(f"Response parsing error: {e}")
            return []
    
    def get_map_style_url(self, style: str = "satellite-v9") -> str:
        """
        Get Mapbox map style URL for frontend integration
        
        Args:
            style: Map style (satellite-v9, streets-v11, outdoors-v11, etc.)
            
        Returns:
            Style URL
        """
        return f"mapbox://styles/mapbox/{style}"
    
    def validate_coordinates(self, latitude: float, longitude: float) -> bool:
        """
        Validate coordinate ranges
        
        Args:
            latitude: Latitude value
            longitude: Longitude value
            
        Returns:
            bool: True if coordinates are valid
        """
        return (-90 <= latitude <= 90) and (-180 <= longitude <= 180)
    
    def calculate_distance(self, lat1: float, lng1: float, 
                          lat2: float, lng2: float) -> float:
        """
        Calculate distance between two points using Haversine formula
        
        Args:
            lat1, lng1: First point coordinates
            lat2, lng2: Second point coordinates
            
        Returns:
            Distance in kilometers
        """
        from math import radians, sin, cos, sqrt, atan2
        
        # Convert to radians
        lat1, lng1, lat2, lng2 = map(radians, [lat1, lng1, lat2, lng2])
        
        # Haversine formula
        dlat = lat2 - lat1
        dlng = lng2 - lng1
        
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlng/2)**2
        c = 2 * atan2(sqrt(a), sqrt(1-a))
        
        # Earth radius in kilometers
        earth_radius = 6371.0
        
        return earth_radius * c
    
    def _extract_context(self, feature: Dict) -> Dict:
        """
        Extract contextual information from Mapbox feature
        
        Args:
            feature: Mapbox feature object
            
        Returns:
            Dict with extracted context information
        """
        context = {}
        
        # Extract context hierarchy (country, region, district, etc.)
        for item in feature.get('context', []):
            context_id = item.get('id', '')
            text = item.get('text', '')
            
            if context_id.startswith('country'):
                context['country'] = text
            elif context_id.startswith('region'):
                context['region'] = text
            elif context_id.startswith('district'):
                context['district'] = text
            elif context_id.startswith('place'):
                context['place'] = text
            elif context_id.startswith('locality'):
                context['locality'] = text
        
        # Add place type and properties
        context['place_type'] = feature.get('place_type', [])
        context['properties'] = feature.get('properties', {})
        
        return context
    
    def __del__(self):
        """Clean up session on object destruction"""
        if hasattr(self, 'session'):
            self.session.close()

class MapboxError(Exception):
    """Custom exception for Mapbox-related errors"""
    pass