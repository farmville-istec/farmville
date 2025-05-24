"""
Models package for FarmVille
"""

from .weather_data import WeatherData

__version__ = "1.0.0"

__all__ = [
    'WeatherData'
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