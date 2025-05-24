from typing import Optional, List
from models.weather_data import WeatherData
import time

class WeatherService:
    """
    Serviço para gestão de dados meteorológicos
    """
    
    def __init__(self, api_key: Optional[str] = None):
        self._api_key = api_key
        self._cache = {}  # Cache simples para evitar chamadas desnecessárias
        self._cache_duration = 1800  # 30 minutos em segundos
    
    def _is_cache_valid(self, location_key: str) -> bool:
        """Verifica se os dados em cache ainda são válidos"""
        if location_key not in self._cache:
            return False
        
        cached_time = self._cache[location_key]['timestamp']
        current_time = time.time()
        
        return (current_time - cached_time) < self._cache_duration
    
    def _create_location_key(self, latitude: float, longitude: float) -> str:
        """Cria chave única para localização"""
        return f"{latitude:.4f},{longitude:.4f}"
    
    def get_weather_data(self, location: str, latitude: float, longitude: float) -> Optional[WeatherData]:
        """
        Obtém dados meteorológicos para uma localização (mock por agora)
        """
        location_key = self._create_location_key(latitude, longitude)
        
        if self._is_cache_valid(location_key):
            print(f"📋 Using cached data for {location}")
            cached_data = self._cache[location_key]['data']
            return cached_data
        
        print(f"🌐 Fetching weather data for {location}...")
        
        # Por agora simula
        weather_data = self._simulate_weather_data(location, latitude, longitude)
        
        self._cache[location_key] = {
            'data': weather_data,
            'timestamp': time.time()
        }
        
        return weather_data
    
    def _simulate_weather_data(self, location: str, latitude: float, longitude: float) -> WeatherData:
        """
        Simula dados meteorológicos para teste
        """
        import random
        
        weather = WeatherData(location, latitude, longitude)
        
        base_temp = 20 - (abs(latitude) * 0.5) 
        
        weather.set_temperature(base_temp + random.uniform(-5, 10))
        weather.set_humidity(random.uniform(30, 80))
        weather.set_pressure(random.uniform(1000, 1025))
        
        descriptions = ["Clear sky", "Few clouds", "Scattered clouds", "Light rain", "Overcast"]
        weather.set_description(random.choice(descriptions))
        
        print(f"✅ Weather data generated for {location}")
        return weather
    
    def get_multiple_locations(self, locations: List[tuple]) -> List[WeatherData]:
        """
        Obtém dados para múltiplas localizações
        locations: Lista de tuplas (nome, latitude, longitude)
        """
        results = []
        
        for location_name, lat, lon in locations:
            weather_data = self.get_weather_data(location_name, lat, lon)
            if weather_data:
                results.append(weather_data)
        
        return results
    
    def clear_cache(self):
        """Limpa o cache"""
        self._cache.clear()
        print("🗑️ Weather cache cleared")
    
    def get_cache_info(self) -> dict:
        """Retorna informações sobre o cache"""
        return {
            'cached_locations': len(self._cache),
            'cache_duration_minutes': self._cache_duration / 60,
            'locations': list(self._cache.keys())
        }