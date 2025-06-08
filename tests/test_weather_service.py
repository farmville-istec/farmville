import unittest
from services.weather_service import WeatherService
from models.weather_data import WeatherData

class TestWeatherService(unittest.TestCase):
    """Testes unitários para o WeatherService"""
    
    def setUp(self):
        """Configuração antes de cada teste"""
        self.weather_service = WeatherService()
    
    def tearDown(self):
        """Limpeza após cada teste"""
        self.weather_service.clear_cache()
    
    def test_get_weather_data_single_location(self):
        """Teste: obter dados para uma localização"""
        weather = self.weather_service.get_weather_data("Porto", 41.1579, -8.6291)
        
        self.assertIsNotNone(weather)
        self.assertIsInstance(weather, WeatherData)
        self.assertEqual(weather.location, "Porto")
        self.assertTrue(weather.is_complete())
    
    def test_weather_data_validation(self):
        """Teste: validação dos dados meteorológicos"""
        weather = WeatherData("Test Location", 0.0, 0.0)
        
        # Testa temperatura válida
        weather.set_temperature(25.0)
        self.assertEqual(weather.temperature, 25.0)
        
        # Testa temperatura inválida
        with self.assertRaises(ValueError):
            weather.set_temperature(100.0)
        
        # Testa humidade válida
        weather.set_humidity(65.0)
        self.assertEqual(weather.humidity, 65.0)
        
        # Testa humidade inválida
        with self.assertRaises(ValueError):
            weather.set_humidity(150.0)
    
    def test_cache_functionality(self):
        """Teste: funcionalidade de cache"""
        weather1 = self.weather_service.get_weather_data("Lisboa", 38.7223, -9.1393)
        
        weather2 = self.weather_service.get_weather_data("Lisboa", 38.7223, -9.1393)
        
        self.assertEqual(weather1.timestamp, weather2.timestamp)
        
        cache_info = self.weather_service.get_cache_info()
        self.assertEqual(cache_info['cached_locations'], 1)
    
    def test_multiple_locations_concurrent(self):
        """Teste: múltiplas localizações com concorrência (UPDATED METHOD NAME)"""
        locations = [
            ("Porto", 41.1579, -8.6291),
            ("Lisboa", 38.7223, -9.1393),
            ("Braga", 41.5518, -8.4229)
        ]
        
        # Updated method name to match new implementation
        weather_list = self.weather_service.get_multiple_locations_concurrent(locations)
        
        self.assertEqual(len(weather_list), 3)
        for weather in weather_list:
            self.assertIsInstance(weather, WeatherData)
            self.assertTrue(weather.is_complete())
    
    def test_api_connection_test(self):
        """Teste: teste de conexão com API"""
        # Test API connection method (may return False if no API key)
        api_result = self.weather_service.test_api_connection()
        self.assertIsInstance(api_result, bool)
    
    def test_cache_info_enhanced(self):
        """Teste: informações do cache (versão melhorada)"""
        cache_info = self.weather_service.get_cache_info()
        
        # Check new fields from enhanced weather service
        self.assertIn('cached_locations', cache_info)
        self.assertIn('cache_duration_minutes', cache_info)
        self.assertIn('locations', cache_info)
        self.assertIn('api_key_configured', cache_info)
        
        # Check types
        self.assertIsInstance(cache_info['cached_locations'], int)
        self.assertIsInstance(cache_info['api_key_configured'], bool)
    
    def test_thread_safety(self):
        """Teste: segurança de thread no cache"""
        import threading
        import time
        
        results = []
        
        def fetch_weather():
            """Função para executar em thread separada"""
            weather = self.weather_service.get_weather_data("Test Location", 0.0, 0.0)
            results.append(weather)
        
        # Create multiple threads
        threads = []
        for i in range(3):
            thread = threading.Thread(target=fetch_weather)
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # All threads should have completed successfully
        self.assertEqual(len(results), 3)
        for weather in results:
            self.assertIsNotNone(weather)
            self.assertIsInstance(weather, WeatherData)

if __name__ == '__main__':
    unittest.main()