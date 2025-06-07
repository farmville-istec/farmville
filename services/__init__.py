"""
Services package for FarmVille
"""

from .weather_service import WeatherService
from .user_service import UserService
from .agro_service import AgroService

__version__ = "1.0.0"

__all__ = [
    'WeatherService',
    'UserService',
    'AgroService'
]

import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

if not logger.handlers:
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    
    formatter = logging.Formatter('[SERVICES] %(levelname)s - %(message)s')
    console_handler.setFormatter(formatter)
    
    logger.addHandler(console_handler)

logger.info("Services package loaded successfully")