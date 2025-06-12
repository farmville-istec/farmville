import time
import requests
import logging
from typing import Optional, Dict, Any, List
from threading import Lock
from dotenv import load_dotenv

from models.location import Location, LocationHierarchy

load_dotenv()

class LocationService:
    """
    Serviço para gestão de dados de localização portuguesa usando GeoAPI.pt
    """
    
    def __init__(self):
        self._cache = {}
        self._cache_lock = Lock()
        self._cache_duration = 86400  
        self._base_url = "https://geoapi.pt"
        
        self.logger = logging.getLogger(self.__class__.__name__)
        
        print("📍 LocationService initialized with GeoAPI.pt")
    
    def _is_cache_valid(self, cache_key: str) -> bool:
        """Verifica se os dados em cache ainda são válidos"""
        with self._cache_lock:
            if cache_key not in self._cache:
                return False
            
            cached_time = self._cache[cache_key]['timestamp']
            current_time = time.time()
            
            return (current_time - cached_time) < self._cache_duration
    
    def _fetch_from_api(self, endpoint: str) -> Optional[List[Dict]]:
        """
        Faz chamada para GeoAPI.pt
        
        Args:
            endpoint: Endpoint da API
            
        Returns:
            Dados da API ou None se erro
        """
        try:
            url = f"{self._base_url}/{endpoint}"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            return response.json()
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"GeoAPI.pt error: {e}")
            print(f"❌ API Error: {e}")
            return None
        except Exception as e:
            self.logger.error(f"Unexpected error fetching location data: {e}")
            print(f"❌ Unexpected Error: {e}")
            return None
    
    def get_location_hierarchy(self) -> Optional[LocationHierarchy]:
        """
        Obtém hierarquia completa de localização (distritos -> concelhos -> freguesias)
        
        Returns:
            LocationHierarchy com dados completos ou None se erro
        """
        cache_key = "full_hierarchy"
        
        if self._is_cache_valid(cache_key):
            print("📋 Using cached location hierarchy")
            with self._cache_lock:
                cached_data = self._cache[cache_key]['data']
            return cached_data
        
        print("🌐 Fetching location hierarchy from GeoAPI.pt...")
        
        try:
           
            districts_data = self._fetch_from_api("distrito")
            if not districts_data:
                return None
            
            hierarchy = LocationHierarchy()
            
            for district in districts_data:
                district_info = {
                    'id': district['id'],
                    'name': district['nome'],
                    'municipalities': []
                }
                
               
                municipalities_data = self._fetch_from_api(f"distrito/{district['id']}/concelhos")
                if municipalities_data:
                    for municipality in municipalities_data:
                        municipality_info = {
                            'id': municipality['id'],
                            'name': municipality['nome'],
                            'parishes': []
                        }
                        
                        
                        parishes_data = self._fetch_from_api(f"concelho/{municipality['id']}/freguesias")
                        if parishes_data:
                            for parish in parishes_data:
                                parish_info = {
                                    'id': parish['id'],
                                    'name': parish['nome']
                                }
                                municipality_info['parishes'].append(parish_info)
                        
                        district_info['municipalities'].append(municipality_info)
                
                hierarchy.add_district(district_info)
            
            
            with self._cache_lock:
                self._cache[cache_key] = {
                    'data': hierarchy,
                    'timestamp': time.time()
                }
            
            print(f"✅ Location hierarchy fetched: {len(hierarchy.districts)} districts")
            return hierarchy
            
        except Exception as e:
            self.logger.error(f"Error building location hierarchy: {e}")
            print(f"❌ Error building hierarchy: {e}")
            return None
    
    def get_coordinates_for_location(self, district: str, municipality: str, parish: str) -> Optional[Location]:
        """
        Obtém coordenadas para uma localização específica
        
        Args:
            district: Nome do distrito
            municipality: Nome do concelho
            parish: Nome da freguesia
            
        Returns:
            Location com coordenadas ou None se erro
        """
        cache_key = f"coords_{district}_{municipality}_{parish}".lower().replace(" ", "_")
        
        if self._is_cache_valid(cache_key):
            print(f"📋 Using cached coordinates for {parish}, {municipality}, {district}")
            with self._cache_lock:
                cached_data = self._cache[cache_key]['data']
            return cached_data
        
        print(f"🌐 Fetching coordinates for {parish}, {municipality}, {district}...")
        
        try:
            
            parishes_data = self._fetch_from_api("freguesia")
            if not parishes_data:
                return None
            
            target_parish = None
            for parish_data in parishes_data:
                if (parish_data['nome'].lower() == parish.lower() and 
                    parish_data['concelho']['nome'].lower() == municipality.lower() and
                    parish_data['distrito']['nome'].lower() == district.lower()):
                    target_parish = parish_data
                    break
            
            if not target_parish:
                print(f"❌ Location not found: {parish}, {municipality}, {district}")
                return None
            
            location = Location(district, municipality, parish)
            
            if 'centro' in target_parish and target_parish['centro']:
                centro = target_parish['centro']
                if 'latitude' in centro and 'longitude' in centro:
                    location.set_coordinates(
                        float(centro['latitude']), 
                        float(centro['longitude'])
                    )
                else:
                    
                    location.set_coordinates(39.3999, -8.2245)  # Coordenadas padrão para Portugal
            else:
                
                location.set_coordinates(39.3999, -8.2245)
            
           
            with self._cache_lock:
                self._cache[cache_key] = {
                    'data': location,
                    'timestamp': time.time()
                }
            
            print(f"✅ Coordinates found for {location.get_full_name()}")
            return location
            
        except Exception as e:
            self.logger.error(f"Error getting coordinates: {e}")
            print(f"❌ Error getting coordinates: {e}")
            return None
    
    def search_locations(self, query: str) -> List[Dict]:
        """
        Busca localizações por nome (simplificado)
        
        Args:
            query: Termo de busca
            
        Returns:
            Lista de localizações encontradas
        """
       
        hierarchy = self.get_location_hierarchy()
        if not hierarchy:
            return []
        
        results = []
        query_lower = query.lower()
        
        for district in hierarchy.districts:
            for municipality in district['municipalities']:
                for parish in municipality['parishes']:
                    if (query_lower in parish['name'].lower() or 
                        query_lower in municipality['name'].lower() or
                        query_lower in district['name'].lower()):
                        results.append({
                            'district': district['name'],
                            'municipality': municipality['name'],
                            'parish': parish['name'],
                            'full_name': f"{parish['name']}, {municipality['name']}, {district['name']}"
                        })
        
        return results[:20]  
    
    def clear_cache(self):
        """Limpa o cache"""
        with self._cache_lock:
            self._cache.clear()
        
        print("🗑️ Location cache cleared")
    
    def get_cache_info(self) -> dict:
        """Retorna informações sobre o cache"""
        with self._cache_lock:
            return {
                'cached_items': len(self._cache),
                'cache_duration_hours': self._cache_duration / 3600,
                'items': list(self._cache.keys())
            }
    
    def test_api_connection(self) -> bool:
        """
        Testa conexão com GeoAPI.pt
        
        Returns:
            True se API está funcionando, False caso contrário
        """
        test_data = self._fetch_from_api("distrito")
        return test_data is not None and len(test_data) > 0