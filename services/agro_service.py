import os
import time
import json
from typing import Optional, List
import logging
from openai import OpenAI
from dotenv import load_dotenv

from models.agro_data import AgroSuggestion, AgroEventTypes
from models.weather_data import WeatherData
from utils.patterns.observer import Subject

load_dotenv()

class AgroService(Subject):
    """
    Serviço de inteligência agrícola com integração OpenAI
    """
    
    def __init__(self, api_key: Optional[str] = None):
        super().__init__()
        
        self._api_key = api_key or os.getenv('OPENAI_API_KEY')
        if not self._api_key:
            raise ValueError("OpenAI API key is required. Set OPENAI_API_KEY in .env file")
        
        self.client = OpenAI(api_key=self._api_key)
        
        self._cache = {}
        self._cache_duration = 3600  # 1 hora em segundos
        
        self.logger = logging.getLogger(self.__class__.__name__)
        
        print("🌾 AgroService initialized with OpenAI integration")
    
    def _is_cache_valid(self, location_key: str) -> bool:
        """Verifica se os dados em cache ainda são válidos"""
        if location_key not in self._cache:
            return False
        
        cached_time = self._cache[location_key]['timestamp']
        current_time = time.time()
        
        return (current_time - cached_time) < self._cache_duration
    
    def _create_location_key(self, location: str) -> str:
        """Cria chave única para localização"""
        return f"agro_{location.lower().replace(' ', '_')}"
    
    def _build_weather_prompt(self, weather_data: WeatherData) -> str:
        """Constrói prompt para OpenAI baseado nos dados meteorológicos"""
        
        prompt = f"""
You are an agricultural expert AI assistant. Analyze the following weather data and provide farming recommendations.

Location: {weather_data.location}
Current Conditions:
- Temperature: {weather_data.temperature}°C
- Humidity: {weather_data.humidity}%
- Atmospheric Pressure: {weather_data.pressure} hPa
- Weather Description: {weather_data.description}
- Data Timestamp: {weather_data.timestamp}

Please provide:
1. 3-5 specific agricultural recommendations based on these conditions
2. Priority level (low/medium/high/urgent)
3. Confidence level (0.0 to 1.0)
4. Brief reasoning for your recommendations

Focus on practical actions like irrigation, fertilization, pest control, harvesting timing, or protective measures.

Respond in JSON format:
{{
    "suggestions": ["suggestion 1", "suggestion 2", "suggestion 3"],
    "priority": "medium",
    "confidence": 0.85,
    "reasoning": "Brief explanation of why these suggestions are recommended based on the weather conditions"
}}
"""
        return prompt.strip()
    
    def analyze_weather_for_agriculture(self, weather_data: WeatherData) -> Optional[AgroSuggestion]:
        """
        Analisa dados meteorológicos e gera sugestões agrícolas usando OpenAI
        
        Args:
            weather_data: Dados meteorológicos
            
        Returns:
            AgroSuggestion ou None se erro
        """
        location_key = self._create_location_key(weather_data.location)
        
        if self._is_cache_valid(location_key):
            print(f"🌾 Using cached agro suggestions for {weather_data.location}")
            cached_data = self._cache[location_key]['data']
            return cached_data
        
        print(f"🤖 Analyzing weather data for {weather_data.location} with AI...")
        
        try:
            prompt = self._build_weather_prompt(weather_data)
            
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an expert agricultural advisor. Always respond with valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500,
                temperature=0.7
            )
            
            ai_response = response.choices[0].message.content.strip()
            
            try:
                ai_data = json.loads(ai_response)
            except json.JSONDecodeError:
                import re
                json_match = re.search(r'\{.*\}', ai_response, re.DOTALL)
                if json_match:
                    ai_data = json.loads(json_match.group())
                else:
                    raise ValueError("Could not parse AI response as JSON")
            
            suggestion = AgroSuggestion(
                location=weather_data.location,
                weather_context=weather_data.to_dict()
            )
            
            for sug in ai_data.get('suggestions', []):
                suggestion.add_suggestion(sug)
            
            suggestion.set_priority(ai_data.get('priority', 'medium'))
            suggestion.set_confidence(float(ai_data.get('confidence', 0.5)))
            suggestion.set_reasoning(ai_data.get('reasoning', 'AI analysis of weather conditions'))
            
            self._cache[location_key] = {
                'data': suggestion,
                'timestamp': time.time()
            }
            
            print(f"✅ Generated {len(suggestion.suggestions)} suggestions for {weather_data.location}")
            
            self.notify(AgroEventTypes.SUGGESTION_GENERATED, {
                'location': weather_data.location,
                'suggestion_count': len(suggestion.suggestions),
                'priority': suggestion.priority
            })
            
            if suggestion.priority in ['high', 'urgent']:
                self.notify(AgroEventTypes.HIGH_PRIORITY_ALERT, {
                    'location': weather_data.location,
                    'priority': suggestion.priority,
                    'suggestions': suggestion.suggestions
                })
            
            return suggestion
            
        except Exception as e:
            self.logger.error(f"Error analyzing weather for agriculture: {e}")
            print(f"❌ Error generating agricultural suggestions: {e}")
            
            self.notify(AgroEventTypes.AI_ERROR, {
                'location': weather_data.location,
                'error': str(e)
            })
            
            return None
    
    def get_suggestions_for_locations(self, weather_data_list: List[WeatherData]) -> List[AgroSuggestion]:
        """
        Gera sugestões para múltiplas localizações
        
        Args:
            weather_data_list: Lista de dados meteorológicos
            
        Returns:
            Lista de sugestões agrícolas
        """
        suggestions = []
        
        for weather_data in weather_data_list:
            suggestion = self.analyze_weather_for_agriculture(weather_data)
            if suggestion:
                suggestions.append(suggestion)
        
        print(f"🌾 Generated suggestions for {len(suggestions)} locations")
        return suggestions
    
    def get_simple_suggestions(self, temperature: float, humidity: float, description: str, location: str = "Farm") -> Optional[AgroSuggestion]:
        """
        Versão simplificada para testes rápidos
        """
        # Criar WeatherData temporário
        from models.weather_data import WeatherData
        
        weather = WeatherData(location, 0.0, 0.0)  # lat/lon não importam para sugestões
        weather.set_temperature(temperature)
        weather.set_humidity(humidity)
        weather.set_pressure(1013.0)  # pressão padrão
        weather.set_description(description)
        
        return self.analyze_weather_for_agriculture(weather)
    
    def clear_cache(self):
        """Limpa o cache de sugestões"""
        self._cache.clear()
        print("🗑️ Agro suggestions cache cleared")
    
    def get_cache_info(self) -> dict:
        """Retorna informações sobre o cache"""
        return {
            'cached_locations': len(self._cache),
            'cache_duration_hours': self._cache_duration / 3600,
            'locations': list(self._cache.keys())
        }