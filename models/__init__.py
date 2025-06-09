"""
Models package for FarmVille
"""

from .weather_data import WeatherData
from .user import User
from .terrain import Terrain
from .agro_data import AgroSuggestion, AgroEventTypes

__version__ = "1.0.0"

__all__ = [
    'WeatherData'
    'User',
    'Terrain',
    'AgroSuggestion',
    'AgroEventTypes'
]

class ModelConstants:
    """Constantes usadas nos modelos"""
    MIN_TEMPERATURE = -100  # °C
    MAX_TEMPERATURE = 60    # °C
    MIN_HUMIDITY = 0        # %
    MAX_HUMIDITY = 100      # %
    MIN_PRESSURE = 800      # hPa
    MAX_PRESSURE = 1200     # hPa
    
    DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
    DATE_FORMAT = "%Y-%m-%d"

    AGRO_PRIORITIES = ["low", "medium", "high", "urgent"]
    MIN_CONFIDENCE = 0.0
    MAX_CONFIDENCE = 1.0

def validate_coordinates(latitude: float, longitude: float) -> bool:
    """
    Valida se as coordenadas são válidas
    
    Args:
        latitude: Latitude (-90 a 90)
        longitude: Longitude (-180 a 180)
        
    Returns:
        bool: True se válidas, False caso contrário
    """
    if not (-90 <= latitude <= 90):
        return False
    if not (-180 <= longitude <= 180):
        return False
    return True

__all__.extend(['ModelConstants', 'validate_coordinates'])