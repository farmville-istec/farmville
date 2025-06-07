from datetime import datetime
from typing import Dict, List
from dataclasses import dataclass

@dataclass
class AgroSuggestion:
    """
    Classe para representar sugestões agrícolas
    """
    
    def __init__(self, location: str, weather_context: Dict):
        self._location = location
        self._weather_context = weather_context
        self._suggestions = []
        self._priority = "medium"
        self._confidence = 0.0
        self._timestamp = datetime.now()
        self._reasoning = ""
    
    @property
    def location(self) -> str:
        return self._location
    
    @property
    def suggestions(self) -> List[str]:
        return self._suggestions
    
    @property
    def priority(self) -> str:
        return self._priority
    
    @property
    def confidence(self) -> float:
        return self._confidence
    
    @property
    def reasoning(self) -> str:
        return self._reasoning
    
    @property
    def timestamp(self) -> datetime:
        return self._timestamp
    
    @property
    def weather_context(self) -> Dict:
        return self._weather_context
    
    def add_suggestion(self, suggestion: str):
        """Adiciona uma sugestão à lista"""
        if suggestion and suggestion not in self._suggestions:
            self._suggestions.append(suggestion.strip())
    
    def set_priority(self, priority: str):
        """Define prioridade: low, medium, high, urgent"""
        valid_priorities = ["low", "medium", "high", "urgent"]
        if priority.lower() in valid_priorities:
            self._priority = priority.lower()
        else:
            raise ValueError(f"Priority must be one of: {valid_priorities}")
    
    def set_confidence(self, confidence: float):
        """Define confiança da sugestão (0.0 a 1.0)"""
        if 0.0 <= confidence <= 1.0:
            self._confidence = confidence
        else:
            raise ValueError("Confidence must be between 0.0 and 1.0")
    
    def set_reasoning(self, reasoning: str):
        """Define o raciocínio por trás das sugestões"""
        self._reasoning = reasoning.strip()
    
    def to_dict(self) -> Dict:
        """Converte para dicionário para JSON"""
        return {
            'location': self._location,
            'suggestions': self._suggestions,
            'priority': self._priority,
            'confidence': self._confidence,
            'reasoning': self._reasoning,
            'weather_context': self._weather_context,
            'timestamp': self._timestamp.isoformat(),
            'suggestion_count': len(self._suggestions)
        }
    
    def __str__(self) -> str:
        """String representation"""
        suggestions_text = ", ".join(self._suggestions) if self._suggestions else "No suggestions"
        return f"AgroSuggestion for {self._location}: {suggestions_text} (Priority: {self._priority})"
    
    def __repr__(self) -> str:
        """Debugging representation"""
        return (f"AgroSuggestion(location='{self._location}', "
               f"suggestions={len(self._suggestions)}, priority='{self._priority}', "
               f"confidence={self._confidence:.2f})")


class AgroEventTypes:
    """Constantes para tipos de eventos agrícolas"""
    SUGGESTION_GENERATED = "suggestion_generated"
    SUGGESTION_UPDATED = "suggestion_updated"
    HIGH_PRIORITY_ALERT = "high_priority_alert"
    WEATHER_ANALYSIS_COMPLETE = "weather_analysis_complete"
    AI_ERROR = "ai_error"