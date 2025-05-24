from datetime import datetime
from typing import Dict, Optional

class WeatherData:
    """
    Classe para representar dados meteorológicos
   
    """
    
    def __init__(self, location: str, latitude: float, longitude: float):
        self._location = location
        self._latitude = latitude
        self._longitude = longitude
        self._temperature = None
        self._humidity = None
        self._pressure = None
        self._description = None
        self._timestamp = datetime.now()
    
    
    @property
    def location(self) -> str:
        return self._location
    
    @property
    def latitude(self) -> float:
        return self._latitude
    
    @property
    def longitude(self) -> float:
        return self._longitude
    
    @property
    def temperature(self) -> Optional[float]:
        return self._temperature
    
    @property
    def humidity(self) -> Optional[float]:
        return self._humidity
    
    @property
    def pressure(self) -> Optional[float]:
        return self._pressure
    
    @property
    def description(self) -> Optional[str]:
        return self._description
    
    @property
    def timestamp(self) -> datetime:
        return self._timestamp
    
    
    def set_temperature(self, temp: float):
        """Define temperatura em Celsius"""
        if temp < -100 or temp > 60:
            raise ValueError("Temperatura fora do range válido (-100 a 60°C)")
        self._temperature = temp
    
    def set_humidity(self, humidity: float):
        """Define humidade em percentagem"""
        if humidity < 0 or humidity > 100:
            raise ValueError("Humidade deve estar entre 0 e 100%")
        self._humidity = humidity
    
    def set_pressure(self, pressure: float):
        """Define pressão atmosférica em hPa"""
        if pressure < 800 or pressure > 1200:
            raise ValueError("Pressão fora do range válido (800-1200 hPa)")
        self._pressure = pressure
    
    def set_description(self, description: str):
        """Define descrição do tempo"""
        self._description = description.strip()
    
    def is_complete(self) -> bool:
        """Verifica se todos os dados essenciais estão preenchidos"""
        return all([
            self._temperature is not None,
            self._humidity is not None,
            self._pressure is not None,
            self._description is not None
        ])
    
    def to_dict(self) -> Dict:
        """Converte para dicionário para JSON"""
        return {
            'location': self._location,
            'latitude': self._latitude,
            'longitude': self._longitude,
            'temperature': self._temperature,
            'humidity': self._humidity,
            'pressure': self._pressure,
            'description': self._description,
            'timestamp': self._timestamp.isoformat(),
            'is_complete': self.is_complete()
        }
    
    def __str__(self) -> str:
        """Printagem em string"""
        if self.is_complete():
            return (f"Weather in {self._location}: {self._temperature}°C, "
                   f"{self._humidity}% humidity, {self._description}")
        else:
            return f"Incomplete weather data for {self._location}"
    
    def __repr__(self) -> str:
        """Representação em string para debugging"""
        return (f"WeatherData(location='{self._location}', "
               f"lat={self._latitude}, lon={self._longitude}, "
               f"complete={self.is_complete()})")