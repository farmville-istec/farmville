import unittest
import os
from unittest.mock import patch, MagicMock
from services.agro_service import AgroService
from services.weather_service import WeatherService
from models.weather_data import WeatherData
from models.agro_data import AgroSuggestion, AgroEventTypes
from utils.observers.agro_observer import AgroAlertObserver, AgroLogObserver

class TestAgroModels(unittest.TestCase):
    """Testes unitários para os modelos agrícolas"""
    
    def setUp(self):
        """Configuração antes de cada teste"""
        self.weather_context = {
            'location': 'Test Farm',
            'temperature': 25.0,
            'humidity': 60.0,
            'pressure': 1013.0
        }
        self.agro_suggestion = AgroSuggestion('Test Farm', self.weather_context)
    
    def test_agro_suggestion_creation(self):
        """Teste: criação de AgroSuggestion"""
        self.assertEqual(self.agro_suggestion.location, 'Test Farm')
        self.assertEqual(self.agro_suggestion.weather_context, self.weather_context)
        self.assertEqual(len(self.agro_suggestion.suggestions), 0)
        self.assertEqual(self.agro_suggestion.priority, 'medium')
        self.assertEqual(self.agro_suggestion.confidence, 0.0)
    
    def test_add_suggestion(self):
        """Teste: adicionar sugestões"""
        self.agro_suggestion.add_suggestion("Irrigate the crops")
        self.agro_suggestion.add_suggestion("Apply fertilizer")
        
        self.assertEqual(len(self.agro_suggestion.suggestions), 2)
        self.assertIn("Irrigate the crops", self.agro_suggestion.suggestions)
        self.assertIn("Apply fertilizer", self.agro_suggestion.suggestions)
        
        # Teste duplicadas
        self.agro_suggestion.add_suggestion("Irrigate the crops")
        self.assertEqual(len(self.agro_suggestion.suggestions), 2)
    
    def test_set_priority_valid(self):
        """Teste: definir prioridade válida"""
        valid_priorities = ["low", "medium", "high", "urgent"]
        
        for priority in valid_priorities:
            self.agro_suggestion.set_priority(priority)
            self.assertEqual(self.agro_suggestion.priority, priority)
    
    def test_set_priority_invalid(self):
        """Teste: definir prioridade inválida"""
        with self.assertRaises(ValueError):
            self.agro_suggestion.set_priority("invalid_priority")
    
    def test_set_confidence_valid(self):
        """Teste: definir confiança válida"""
        self.agro_suggestion.set_confidence(0.85)
        self.assertEqual(self.agro_suggestion.confidence, 0.85)
        
        self.agro_suggestion.set_confidence(0.0)
        self.assertEqual(self.agro_suggestion.confidence, 0.0)
        
        self.agro_suggestion.set_confidence(1.0)
        self.assertEqual(self.agro_suggestion.confidence, 1.0)
    
    def test_set_confidence_invalid(self):
        """Teste: definir confiança inválida"""
        with self.assertRaises(ValueError):
            self.agro_suggestion.set_confidence(-0.1)
        
        with self.assertRaises(ValueError):
            self.agro_suggestion.set_confidence(1.1)
    
    def test_to_dict(self):
        """Teste: conversão para dicionário"""
        self.agro_suggestion.add_suggestion("Test suggestion")
        self.agro_suggestion.set_priority("high")
        self.agro_suggestion.set_confidence(0.9)
        self.agro_suggestion.set_reasoning("Test reasoning")
        
        result_dict = self.agro_suggestion.to_dict()
        
        self.assertEqual(result_dict['location'], 'Test Farm')
        self.assertEqual(result_dict['suggestions'], ["Test suggestion"])
        self.assertEqual(result_dict['priority'], 'high')
        self.assertEqual(result_dict['confidence'], 0.9)
        self.assertEqual(result_dict['reasoning'], 'Test reasoning')
        self.assertEqual(result_dict['suggestion_count'], 1)


class TestAgroObservers(unittest.TestCase):
    """Testes unitários para os observadores agrícolas"""
    
    def setUp(self):
        """Configuração antes de cada teste"""
        self.alert_observer = AgroAlertObserver()
        self.log_observer = AgroLogObserver()
    
    def test_alert_observer_creation(self):
        """Teste: criação do AgroAlertObserver"""
        self.assertIsInstance(self.alert_observer, AgroAlertObserver)
    
    def test_log_observer_creation(self):
        """Teste: criação do AgroLogObserver"""
        self.assertIsInstance(self.log_observer, AgroLogObserver)
        self.assertEqual(self.log_observer.event_count, {})
    
    def test_log_observer_event_counting(self):
        """Teste: contagem de eventos no log observer"""
        # Simular eventos
        self.log_observer.update(None, AgroEventTypes.SUGGESTION_GENERATED, {})
        self.log_observer.update(None, AgroEventTypes.SUGGESTION_GENERATED, {})
        self.log_observer.update(None, AgroEventTypes.HIGH_PRIORITY_ALERT, {})
        
        stats = self.log_observer.get_event_stats()
        
        self.assertEqual(stats['total_events'], 3)
        self.assertEqual(stats['event_breakdown'][AgroEventTypes.SUGGESTION_GENERATED], 2)
        self.assertEqual(stats['event_breakdown'][AgroEventTypes.HIGH_PRIORITY_ALERT], 1)


class TestAgroService(unittest.TestCase):
    """Testes unitários para o AgroService"""
    
    def setUp(self):
        """Configuração antes de cada teste"""
        self.openai_patcher = patch('services.agro_service.OpenAI')
        self.mock_openai = self.openai_patcher.start()
        
        os.environ['OPENAI_API_KEY'] = 'test_api_key'
        
        mock_response = MagicMock()
        mock_response.choices[0].message.content = '''
        {
            "suggestions": ["Monitor soil moisture", "Apply fertilizer", "Check for pests"],
            "priority": "medium",
            "confidence": 0.85,
            "reasoning": "Current conditions are favorable for most crops"
        }
        '''
        
        self.mock_openai.return_value.chat.completions.create.return_value = mock_response
        
        try:
            self.agro_service = AgroService()
        except Exception as e:
            self.skipTest(f"Could not initialize AgroService: {e}")
    
    def tearDown(self):
        """Limpeza após cada teste"""
        self.openai_patcher.stop()
        if hasattr(self, 'agro_service'):
            self.agro_service.clear_cache()
        
        if 'OPENAI_API_KEY' in os.environ:
            del os.environ['OPENAI_API_KEY']
    
    def test_agro_service_initialization(self):
        """Teste: inicialização do AgroService"""
        self.assertIsInstance(self.agro_service, AgroService)
        self.assertEqual(len(self.agro_service._observers), 0)
    
    def test_observer_attachment(self):
        """Teste: anexar observadores"""
        observer = AgroAlertObserver()
        
        self.agro_service.attach(observer)
        self.assertEqual(len(self.agro_service._observers), 1)
        self.assertIn(observer, self.agro_service._observers)
    
    def test_cache_functionality(self):
        """Teste: funcionalidade de cache"""
        weather_data = WeatherData("Test Location", 0.0, 0.0)
        weather_data.set_temperature(25.0)
        weather_data.set_humidity(60.0)
        weather_data.set_pressure(1013.0)
        weather_data.set_description("Clear sky")
        
        suggestion1 = self.agro_service.analyze_weather_for_agriculture(weather_data)
        self.assertIsNotNone(suggestion1)
        
        suggestion2 = self.agro_service.analyze_weather_for_agriculture(weather_data)
        self.assertIsNotNone(suggestion2)
        
        self.assertEqual(suggestion1.timestamp, suggestion2.timestamp)
        
        cache_info = self.agro_service.get_cache_info()
        self.assertEqual(cache_info['cached_locations'], 1)
    
    def test_simple_suggestions(self):
        """Teste: sugestões simples"""
        suggestion = self.agro_service.get_simple_suggestions(
            temperature=25.0,
            humidity=60.0,
            description="Clear sky",
            location="Test Farm"
        )
        
        self.assertIsNotNone(suggestion)
        self.assertIsInstance(suggestion, AgroSuggestion)
        self.assertEqual(suggestion.location, "Test Farm")
        self.assertGreater(len(suggestion.suggestions), 0)
    
    def test_multiple_locations_analysis(self):
        """Teste: análise de múltiplas localizações"""
        weather_data_list = []
        
        for i, location in enumerate(["Farm A", "Farm B", "Farm C"]):
            weather = WeatherData(location, i, i)
            weather.set_temperature(20 + i * 5)
            weather.set_humidity(50 + i * 10)
            weather.set_pressure(1013.0)
            weather.set_description("Test weather")
            weather_data_list.append(weather)
        
        suggestions = self.agro_service.get_suggestions_for_locations(weather_data_list)
        
        self.assertEqual(len(suggestions), 3)
        
        for suggestion in suggestions:
            self.assertIsInstance(suggestion, AgroSuggestion)
            self.assertGreater(len(suggestion.suggestions), 0)
    
    def test_cache_clear(self):
        """Teste: limpeza de cache"""
        weather_data = WeatherData("Test", 0.0, 0.0)
        weather_data.set_temperature(25.0)
        weather_data.set_humidity(60.0)
        weather_data.set_pressure(1013.0)
        weather_data.set_description("Clear")
        
        self.agro_service.analyze_weather_for_agriculture(weather_data)
        
        cache_info_before = self.agro_service.get_cache_info()
        self.assertGreater(cache_info_before['cached_locations'], 0)
        
        self.agro_service.clear_cache()
        
        cache_info_after = self.agro_service.get_cache_info()
        self.assertEqual(cache_info_after['cached_locations'], 0)


class TestAgroServiceError(unittest.TestCase):
    """Testes de tratamento de erros do AgroService"""
    
    def test_missing_api_key(self):
        """Teste: erro quando API key não está definida"""
        if 'OPENAI_API_KEY' in os.environ:
            del os.environ['OPENAI_API_KEY']
        
        with self.assertRaises(ValueError) as context:
            AgroService()
        
        self.assertIn("OpenAI API key is required", str(context.exception))
    
    @patch('services.agro_service.OpenAI')
    def test_openai_api_error(self, mock_openai):
        """Teste: erro na API do OpenAI"""
        os.environ['OPENAI_API_KEY'] = 'test_key'
        
        mock_openai.return_value.chat.completions.create.side_effect = Exception("API Error")
        
        agro_service = AgroService()
        
        weather_data = WeatherData("Test", 0.0, 0.0)
        weather_data.set_temperature(25.0)
        weather_data.set_humidity(60.0)
        weather_data.set_pressure(1013.0)
        weather_data.set_description("Clear")
        
        result = agro_service.analyze_weather_for_agriculture(weather_data)
        self.assertIsNone(result)
        
        del os.environ['OPENAI_API_KEY']


class TestAgroServiceIntegration(unittest.TestCase):
    """Testes de integração do AgroService com outros serviços"""
    
    def setUp(self):
        """Configuração antes de cada teste"""
        self.openai_patcher = patch('services.agro_service.OpenAI')
        self.mock_openai = self.openai_patcher.start()
        
        os.environ['OPENAI_API_KEY'] = 'test_key'
        
        mock_response = MagicMock()
        mock_response.choices[0].message.content = '''
        {
            "suggestions": ["Integration test suggestion"],
            "priority": "low",
            "confidence": 0.7,
            "reasoning": "Integration test reasoning"
        }
        '''
        
        self.mock_openai.return_value.chat.completions.create.return_value = mock_response
        
        try:
            self.weather_service = WeatherService()
            self.agro_service = AgroService()
        except Exception as e:
            self.skipTest(f"Could not initialize services: {e}")
    
    def tearDown(self):
        """Limpeza após cada teste"""
        self.openai_patcher.stop()
        if hasattr(self, 'weather_service'):
            self.weather_service.clear_cache()
        if hasattr(self, 'agro_service'):
            self.agro_service.clear_cache()
        
        if 'OPENAI_API_KEY' in os.environ:
            del os.environ['OPENAI_API_KEY']
    
    def test_weather_agro_integration(self):
        """Teste: integração entre WeatherService e AgroService"""
        weather_data = self.weather_service.get_weather_data("Test Location", 0.0, 0.0)
        self.assertIsNotNone(weather_data)
        self.assertTrue(weather_data.is_complete())
        
        suggestion = self.agro_service.analyze_weather_for_agriculture(weather_data)
        self.assertIsNotNone(suggestion)
        self.assertIsInstance(suggestion, AgroSuggestion)
        self.assertEqual(suggestion.location, "Test Location")
    
    def test_observer_notification_integration(self):
        """Teste: integração com sistema de observadores"""
        log_observer = AgroLogObserver()
        alert_observer = AgroAlertObserver()
        
        self.agro_service.attach(log_observer)
        self.agro_service.attach(alert_observer)
        
        weather_data = self.weather_service.get_weather_data("Test Farm", 0.0, 0.0)
        suggestion = self.agro_service.analyze_weather_for_agriculture(weather_data)
        
        self.assertIsNotNone(suggestion)
        
        stats = log_observer.get_event_stats()
        self.assertGreater(stats['total_events'], 0)


if __name__ == '__main__':
    unittest.main()