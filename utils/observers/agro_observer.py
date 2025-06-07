from utils.patterns.observer import Observer
from models.agro_data import AgroEventTypes
import logging

class AgroAlertObserver(Observer):
    """
    Observador para alertas agrícolas
    """
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        print("🔔 AgroAlertObserver initialized")
    
    def update(self, subject, event_type: str, data):
        """
        Processa eventos agrícolas
        """
        if event_type == AgroEventTypes.SUGGESTION_GENERATED:
            self._handle_suggestion_generated(data)
        
        elif event_type == AgroEventTypes.HIGH_PRIORITY_ALERT:
            self._handle_high_priority_alert(data)
        
        elif event_type == AgroEventTypes.AI_ERROR:
            self._handle_ai_error(data)
        
        elif event_type == AgroEventTypes.WEATHER_ANALYSIS_COMPLETE:
            self._handle_analysis_complete(data)
    
    def _handle_suggestion_generated(self, data):
        """Processa sugestões geradas"""
        location = data.get('location', 'Unknown')
        count = data.get('suggestion_count', 0)
        priority = data.get('priority', 'medium')
        
        print(f"🌾 New suggestions for {location}: {count} suggestions (Priority: {priority})")
        self.logger.info(f"Agricultural suggestions generated for {location}")
    
    def _handle_high_priority_alert(self, data):
        """Processa alertas de alta prioridade"""
        location = data.get('location', 'Unknown')
        priority = data.get('priority', 'high')
        suggestions = data.get('suggestions', [])
        
        print(f"⚠️  HIGH PRIORITY ALERT for {location}!")
        print(f"   Priority: {priority.upper()}")
        for i, suggestion in enumerate(suggestions, 1):
            print(f"   {i}. {suggestion}")
        
        self.logger.warning(f"High priority agricultural alert for {location}: {priority}")
    
    def _handle_ai_error(self, data):
        """Processa erros da AI"""
        location = data.get('location', 'Unknown')
        error = data.get('error', 'Unknown error')
        
        print(f"❌ AI Error for {location}: {error}")
        self.logger.error(f"AI analysis failed for {location}: {error}")
    
    def _handle_analysis_complete(self, data):
        """Processa conclusão de análise"""
        location = data.get('location', 'Unknown')
        print(f"✅ Weather analysis complete for {location}")
        self.logger.info(f"Weather analysis completed for {location}")


class AgroLogObserver(Observer):
    """
    Observador para logging detalhado de eventos agrícolas
    """
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.event_count = {}
        print("📝 AgroLogObserver initialized")
    
    def update(self, subject, event_type: str, data):
        """
        Regista todos os eventos agrícolas
        """
        self.event_count[event_type] = self.event_count.get(event_type, 0) + 1
        
        # Log event details
        self.logger.info(f"Agro Event: {event_type}")
        self.logger.debug(f"Event data: {data}")
        
        if event_type in [AgroEventTypes.SUGGESTION_GENERATED, AgroEventTypes.HIGH_PRIORITY_ALERT]:
            print(f"📊 Event #{self.event_count[event_type]}: {event_type}")
    
    def get_event_stats(self):
        """Retorna estatísticas dos eventos"""
        return {
            'total_events': sum(self.event_count.values()),
            'event_breakdown': self.event_count.copy()
        }