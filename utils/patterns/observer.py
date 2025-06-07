from abc import ABC, abstractmethod
from typing import List, Any
import logging

class Observer(ABC):
    """Interface para observadores"""
    
    @abstractmethod
    def update(self, subject: 'Subject', event_type: str, data: Any):
        """
        Método chamado quando o subject notifica mudanças
        
        Args:
            subject: O objeto que está a notificar
            event_type: Tipo de evento (ex: 'weather_updated')
            data: Dados relacionados ao evento
        """
        pass

class Subject(ABC):
    """Interface para subjects (observáveis)"""
    
    def __init__(self):
        self._observers: List[Observer] = []
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def attach(self, observer: Observer):
        """Adiciona um observador"""
        if observer not in self._observers:
            self._observers.append(observer)
            self.logger.info(f"Observer {observer.__class__.__name__} attached")
    
    def detach(self, observer: Observer):
        """Remove um observador"""
        if observer in self._observers:
            self._observers.remove(observer)
            self.logger.info(f"Observer {observer.__class__.__name__} detached")
    
    def notify(self, event_type: str, data: Any = None):
        """
        Notifica todos os observadores
        
        Args:
            event_type: Tipo de evento
            data: Dados do evento
        """
        self.logger.info(f"Notifying {len(self._observers)} observers about '{event_type}'")
        
        for observer in self._observers:
            try:
                observer.update(self, event_type, data)
            except Exception as e:
                self.logger.error(f"Error notifying observer {observer.__class__.__name__}: {e}")

class WeatherEventTypes:
    """Constantes para tipos de eventos meteorológicos"""
    WEATHER_UPDATED = "weather_updated"
    WEATHER_ALERT = "weather_alert"
    CACHE_CLEARED = "cache_cleared"
    API_ERROR = "api_error"