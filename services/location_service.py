import requests
import logging
from typing import Optional, List, Dict
from threading import Lock
import time

from utils.patterns.observer import Subject
from models.location import Location


class LocationEventTypes:
    """Constants for location event types"""
    DISTRICTS_LOADED = "districts_loaded"
    MUNICIPALITIES_LOADED = "municipalities_loaded"
    PARISHES_LOADED = "parishes_loaded"
    LOCATION_SELECTED = "location_selected"
    API_ERROR = "api_error"


class LocationService(Subject):
    """
    Service for managing Portuguese location data using GeoAPI.pt
    """
    
    def __init__(self):
        super().__init__()
        self._cache = {}
        self._cache_lock = Lock()
        self._cache_duration = 3600  # 1 hour in seconds
        self._base_url = "https://json.geoapi.pt"
        
        self.logger = logging.getLogger(self.__class__.__name__)
        
        print("🗺️  LocationService initialized with GeoAPI.pt")
    
    def _is_cache_valid(self, cache_key: str) -> bool:
        """Check if cached data is still valid"""
        with self._cache_lock:
            if cache_key not in self._cache:
                return False
            
            cached_time = self._cache[cache_key]['timestamp']
            current_time = time.time()
            
            return (current_time - cached_time) < self._cache_duration
    
    def _fetch_from_api(self, endpoint: str) -> Optional[List[Dict]]:
        """
        Make API call to GeoAPI.pt
        
        Args:
            endpoint: API endpoint to call
            
        Returns:
            List of location data or None if error
        """
        try:
            url = f"{self._base_url}/{endpoint}"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            return response.json()
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"API request failed: {e}")
            self.notify(LocationEventTypes.API_ERROR, {
                'endpoint': endpoint,
                'error': str(e)
            })
            return None
        except Exception as e:
            self.logger.error(f"Unexpected error: {e}")
            return None
    
    def get_districts(self) -> Optional[List[Dict]]:
        """
        Get all Portuguese districts
        
        Returns:
            List of districts with id and nome, or None if error
        """
        cache_key = "districts"
        
        if self._is_cache_valid(cache_key):
            self.logger.info("Using cached districts data")
            with self._cache_lock:
                return self._cache[cache_key]['data']
        
        self.logger.info("Fetching districts from API...")
        data = self._fetch_from_api("distrito")
        
        if data:
            districts = [{"id": item["id"], "nome": item["nome"]} for item in data]
            
            with self._cache_lock:
                self._cache[cache_key] = {
                    'data': districts,
                    'timestamp': time.time()
                }
            
            self.notify(LocationEventTypes.DISTRICTS_LOADED, {
                'count': len(districts)
            })
            
            print(f"✅ Loaded {len(districts)} districts")
            return districts
        
        return None
    
    def get_municipalities(self, district_id: int) -> Optional[List[Dict]]:
        """
        Get municipalities for a specific district
        
        Args:
            district_id: District ID
            
        Returns:
            List of municipalities with id and nome, or None if error
        """
        cache_key = f"municipalities_{district_id}"
        
        if self._is_cache_valid(cache_key):
            self.logger.info(f"Using cached municipalities for district {district_id}")
            with self._cache_lock:
                return self._cache[cache_key]['data']
        
        self.logger.info(f"Fetching municipalities for district {district_id}...")
        data = self._fetch_from_api(f"municipio?distrito={district_id}")
        
        if data:
            municipalities = [{"id": item["id"], "nome": item["nome"]} for item in data]
            
            with self._cache_lock:
                self._cache[cache_key] = {
                    'data': municipalities,
                    'timestamp': time.time()
                }
            
            self.notify(LocationEventTypes.MUNICIPALITIES_LOADED, {
                'district_id': district_id,
                'count': len(municipalities)
            })
            
            print(f"✅ Loaded {len(municipalities)} municipalities for district {district_id}")
            return municipalities
        
        return None
    
    def get_parishes(self, municipality_id: int) -> Optional[List[Dict]]:
        """
        Get parishes for a specific municipality
        
        Args:
            municipality_id: Municipality ID
            
        Returns:
            List of parishes with id and nome, or None if error
        """
        cache_key = f"parishes_{municipality_id}"
        
        if self._is_cache_valid(cache_key):
            self.logger.info(f"Using cached parishes for municipality {municipality_id}")
            with self._cache_lock:
                return self._cache[cache_key]['data']
        
        self.logger.info(f"Fetching parishes for municipality {municipality_id}...")
        data = self._fetch_from_api(f"freguesia?municipio={municipality_id}")
        
        if data:
            parishes = [{"id": item["id"], "nome": item["nome"]} for item in data]
            
            with self._cache_lock:
                self._cache[cache_key] = {
                    'data': parishes,
                    'timestamp': time.time()
                }
            
            self.notify(LocationEventTypes.PARISHES_LOADED, {
                'municipality_id': municipality_id,
                'count': len(parishes)
            })
            
            print(f"✅ Loaded {len(parishes)} parishes for municipality {municipality_id}")
            return parishes
        
        return None
    
    def get_parish_coordinates(self, parish_id: int) -> Optional[Dict]:
        """
        Get coordinates for a specific parish
        
        Args:
            parish_id: Parish ID
            
        Returns:
            Dict with latitude and longitude, or None if error
        """
        cache_key = f"coordinates_{parish_id}"
        
        if self._is_cache_valid(cache_key):
            self.logger.info(f"Using cached coordinates for parish {parish_id}")
            with self._cache_lock:
                return self._cache[cache_key]['data']
        
        self.logger.info(f"Fetching coordinates for parish {parish_id}...")
        data = self._fetch_from_api(f"freguesia/{parish_id}")
        
        if data and len(data) > 0:
            parish_data = data[0]
            coordinates = {
                'latitude': parish_data.get('latitude'),
                'longitude': parish_data.get('longitude')
            }
            
            if coordinates['latitude'] and coordinates['longitude']:
                with self._cache_lock:
                    self._cache[cache_key] = {
                        'data': coordinates,
                        'timestamp': time.time()
                    }
                
                print(f"✅ Loaded coordinates for parish {parish_id}")
                return coordinates
        
        self.logger.warning(f"No coordinates found for parish {parish_id}")
        return None
    
    def get_location_hierarchy(self, parish_id: int) -> Optional[Dict]:
        """
        Get complete location hierarchy (district, municipality, parish) for a parish
        
        Args:
            parish_id: Parish ID
            
        Returns:
            Dict with complete location info and coordinates, or None if error
        """
        self.logger.info(f"Fetching complete location hierarchy for parish {parish_id}...")
        
        # Get parish details including coordinates
        parish_data = self._fetch_from_api(f"freguesia/{parish_id}")
        if not parish_data or len(parish_data) == 0:
            return None
        
        parish_info = parish_data[0]
        
        result = {
            'parish': {
                'id': parish_info.get('id'),
                'nome': parish_info.get('nome')
            },
            'municipality': {
                'id': parish_info.get('municipio', {}).get('id'),
                'nome': parish_info.get('municipio', {}).get('nome')
            },
            'district': {
                'id': parish_info.get('distrito', {}).get('id'),
                'nome': parish_info.get('distrito', {}).get('nome')
            },
            'coordinates': {
                'latitude': parish_info.get('latitude'),
                'longitude': parish_info.get('longitude')
            }
        }
        
        self.notify(LocationEventTypes.LOCATION_SELECTED, {
            'parish_id': parish_id,
            'location_name': f"{result['parish']['nome']}, {result['municipality']['nome']}, {result['district']['nome']}"
        })
        
        print(f"✅ Complete location hierarchy loaded for {result['parish']['nome']}")
        return result
    
    def get_location_from_parish(self, parish_id: int) -> Optional[Location]:
        """
        Get Location object from parish ID
        
        Args:
            parish_id: Parish ID
            
        Returns:
            Location object or None if error
        """
        hierarchy = self.get_location_hierarchy(parish_id)
        if not hierarchy:
            return None
        
        return Location.from_hierarchy_data(hierarchy)
    
    def clear_cache(self):
        """Clear all cached location data"""
        with self._cache_lock:
            self._cache.clear()
        
        self.logger.info("Location cache cleared")
        print("🗑️  Location cache cleared")
    
    def get_cache_info(self) -> Dict:
        """
        Get information about cached data
        
        Returns:
            Dictionary with cache statistics
        """
        with self._cache_lock:
            cache_keys = list(self._cache.keys())
            return {
                'cached_items': len(cache_keys),
                'cache_keys': cache_keys,
                'cache_duration_seconds': self._cache_duration
            }