from .auth_routes import auth_bp
from .weather_routes import weather_bp
from .agro_routes import agro_bp
from .terrain_routes import terrain_bp
from .system_routes import system_bp
from .location_routes import location_bp  

__all__ = [
    'auth_bp',
    'weather_bp',
    'agro_bp',
    'terrain_bp',
    'system_bp',
    'location_bp'  
]