import os
import time
import requests
import logging
from typing import Optional, List
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock
from dotenv import load_dotenv

from models.weather_data import WeatherData
from utils.patterns.observer import Subject, WeatherEventTypes

load_dotenv()

class WeatherService(Subject):
    """
    Serviço para gestão de dados meteorológicos com OpenWeatherMap API
    """
    
    def __init__(self, api_key: Optional[str] = None):
        super().__init__()
        self._api_key = api_key or os.getenv('OPENWEATHERMAP_API_KEY')
        if not self._api_key:
            print("⚠️  Warning: No OpenWeatherMap API key found. Using fallback mode.")
        
        self._cache = {} 
        self._cache_lock = Lock()
        self._cache_duration = 1800  # 30 minutos em segundos
        self._base_url = "https://api.openweathermap.org/data/2.5/weather"
        
        self._max_workers = 5
        self.logger = logging.getLogger(self.__class__.__name__)
        
        print("🌤️  WeatherService initialized with OpenWeatherMap API")
    
    def _is_cache_valid(self, location_key: str) -> bool:
        """Verifica se os dados em cache ainda são válidos"""
        with self._cache_lock:
            if location_key not in self._cache:
                return False
            
            cached_time = self._cache[location_key]['timestamp']
            current_time = time.time()
            
            return (current_time - cached_time) < self._cache_duration
    
    def _create_location_key(self, latitude: float, longitude: float) -> str:
        """Cria chave única para localização"""
        return f"{latitude:.4f},{longitude:.4f}"
    
    def _fetch_weather_from_api(self, latitude: float, longitude: float) -> Optional[dict]:
        """
        Faz chamada para OpenWeatherMap API
        
        Args:
            latitude: Latitude da localização
            longitude: Longitude da localização
            
        Returns:
            Dados meteorológicos da API ou None se erro
        """
        if not self._api_key:
            return None
        
        try:
            params = {
                'lat': latitude,
                'lon': longitude,
                'appid': self._api_key,
                'units': 'metric'  # Celsius
            }
            
            response = requests.get(self._base_url, params=params, timeout=10)
            response.raise_for_status()
            
            return response.json()
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"OpenWeatherMap API error: {e}")
            print(f"❌ API Error: {e}")
            return None
        except Exception as e:
            self.logger.error(f"Unexpected error fetching weather: {e}")
            print(f"❌ Unexpected Error: {e}")
            return None
    
    def _parse_api_response(self, api_data: dict, location: str, latitude: float, longitude: float) -> WeatherData:
        """
        Converte resposta da API para WeatherData
        
        Args:
            api_data: Dados da API OpenWeatherMap
            location: Nome da localização
            latitude: Latitude
            longitude: Longitude
            
        Returns:
            WeatherData object
        """
        weather = WeatherData(location, latitude, longitude)
        
        # Parse temperature
        weather.set_temperature(api_data['main']['temp'])
        
        # Parse humidity
        weather.set_humidity(api_data['main']['humidity'])
        
        # Parse pressure
        weather.set_pressure(api_data['main']['pressure'])
        
        # Parse description
        description = api_data['weather'][0]['description'].title()
        weather.set_description(description)
        
        return weather
    
    def _simulate_weather_data(self, location: str, latitude: float, longitude: float) -> WeatherData:
        """
        Fallback: Simula dados meteorológicos quando API não está disponível
        """
        import random
        
        weather = WeatherData(location, latitude, longitude)
        
        base_temp = 20 - (abs(latitude) * 0.5) 
        
        weather.set_temperature(base_temp + random.uniform(-5, 10))
        weather.set_humidity(random.uniform(30, 80))
        weather.set_pressure(random.uniform(1000, 1025))
        
        descriptions = ["Clear sky", "Few clouds", "Scattered clouds", "Light rain", "Overcast"]
        weather.set_description(random.choice(descriptions))
        
        print(f"🔄 Using simulated weather data for {location}")
        return weather
    
    def get_weather_data(self, location: str, latitude: float, longitude: float) -> Optional[WeatherData]:
        """
        Obtém dados meteorológicos
        
        Args:
            location: Nome da localização
            latitude: Latitude
            longitude: Longitude
            
        Returns:
            WeatherData ou None se erro
        """
        location_key = self._create_location_key(latitude, longitude)
        
        if self._is_cache_valid(location_key):
            print(f"📋 Using cached weather data for {location}")
            with self._cache_lock:
                cached_data = self._cache[location_key]['data']
            return cached_data
        
        print(f"🌐 Fetching real weather data for {location}...")
        
        api_data = self._fetch_weather_from_api(latitude, longitude)
        
        if api_data:
            try:
                weather_data = self._parse_api_response(api_data, location, latitude, longitude)
                print(f"✅ Real weather data fetched for {location}")
                
                with self._cache_lock:
                    self._cache[location_key] = {
                        'data': weather_data,
                        'timestamp': time.time()
                    }
                
                self.notify(WeatherEventTypes.WEATHER_UPDATED, {
                    'location': location,
                    'source': 'openweathermap'
                })
                
                return weather_data
                
            except Exception as e:
                self.logger.error(f"Error parsing API response: {e}")
                print(f"❌ Error parsing weather data: {e}")
        
        weather_data = self._simulate_weather_data(location, latitude, longitude)
        
        with self._cache_lock:
            self._cache[location_key] = {
                'data': weather_data,
                'timestamp': time.time()
            }
        
        self.notify(WeatherEventTypes.WEATHER_UPDATED, {
            'location': location,
            'source': 'simulated'
        })
        
        return weather_data
    
    def get_multiple_locations_concurrent(self, locations: List[tuple]) -> List[WeatherData]:
        """
        Obtém dados para múltiplas localizações usando threading
        
        Args:
            locations: Lista de tuplas (nome, latitude, longitude)
            
        Returns:
            Lista de WeatherData
        """
        print(f"🚀 Starting concurrent weather fetch for {len(locations)} locations...")
        
        results = []
        
        def fetch_single_location(location_data):
            """Função para buscar dados de uma localização"""
            name, lat, lon = location_data
            try:
                weather_data = self.get_weather_data(name, lat, lon)
                return weather_data
            except Exception as e:
                self.logger.error(f"Error fetching weather for {name}: {e}")
                return None
        
        with ThreadPoolExecutor(max_workers=self._max_workers) as executor:
            future_to_location = {
                executor.submit(fetch_single_location, location): location 
                for location in locations
            }
            
            for future in as_completed(future_to_location):
                location = future_to_location[future]
                try:
                    weather_data = future.result()
                    if weather_data:
                        results.append(weather_data)
                        print(f"✅ Completed: {location[0]}")
                except Exception as e:
                    self.logger.error(f"Exception in thread for {location[0]}: {e}")
                    print(f"❌ Failed: {location[0]} - {e}")
        
        print(f"🎯 Concurrent fetch completed: {len(results)}/{len(locations)} successful")
        
        self.notify(WeatherEventTypes.WEATHER_UPDATED, {
            'bulk_update': True,
            'locations_count': len(results),
            'total_requested': len(locations)
        })
        
        return results
    
    def clear_cache(self):
        """Limpa o cache"""
        with self._cache_lock:
            self._cache.clear()
        
        print("🗑️ Weather cache cleared")
        
        self.notify(WeatherEventTypes.CACHE_CLEARED, {
            'timestamp': time.time()
        })
    
    def get_cache_info(self) -> dict:
        """Retorna informações sobre o cache"""
        with self._cache_lock:
            return {
                'cached_locations': len(self._cache),
                'cache_duration_minutes': self._cache_duration / 60,
                'locations': list(self._cache.keys()),
                'api_key_configured': bool(self._api_key)
            }
    
    def test_api_connection(self) -> bool:
        """
        Testa conexão com OpenWeatherMap API
        
        Returns:
            True se API está funcionando, False caso contrário
        """
        if not self._api_key:
            return False
        
        test_data = self._fetch_weather_from_api(41.1579, -8.6291)
        return test_data is not None