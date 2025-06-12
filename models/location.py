from datetime import datetime
from typing import Dict, Optional, List

class Location:
    """
    Classe para representar dados de localização portuguesa
    """
    
    def __init__(self, district: str, municipality: str, parish: str):
        self._district = district
        self._municipality = municipality
        self._parish = parish
        self._latitude = None
        self._longitude = None
        self._timestamp = datetime.now()
    
    @property
    def district(self) -> str:
        return self._district
    
    @property
    def municipality(self) -> str:
        return self._municipality
    
    @property
    def parish(self) -> str:
        return self._parish
    
    @property
    def latitude(self) -> Optional[float]:
        return self._latitude
    
    @property
    def longitude(self) -> Optional[float]:
        return self._longitude
    
    @property
    def timestamp(self) -> datetime:
        return self._timestamp
    
    def set_coordinates(self, latitude: float, longitude: float):
        """Define coordenadas da localização"""
        if not (-90 <= latitude <= 90):
            raise ValueError("Latitude deve estar entre -90 e 90")
        if not (-180 <= longitude <= 180):
            raise ValueError("Longitude deve estar entre -180 e 180")
        
        self._latitude = latitude
        self._longitude = longitude
    
    def get_full_name(self) -> str:
        """Retorna nome completo da localização"""
        return f"{self._parish}, {self._municipality}, {self._district}"
    
    def is_complete(self) -> bool:
        """Verifica se tem coordenadas definidas"""
        return all([
            self._district,
            self._municipality, 
            self._parish,
            self._latitude is not None,
            self._longitude is not None
        ])
    
    def to_dict(self) -> Dict:
        """Converte para dicionário para JSON"""
        return {
            'district': self._district,
            'municipality': self._municipality,
            'parish': self._parish,
            'latitude': self._latitude,
            'longitude': self._longitude,
            'full_name': self.get_full_name(),
            'timestamp': self._timestamp.isoformat(),
            'is_complete': self.is_complete()
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Location':
        """Cria instância a partir de dicionário"""
        location = cls(
            data['district'],
            data['municipality'], 
            data['parish']
        )
        
        if 'latitude' in data and 'longitude' in data:
            if data['latitude'] is not None and data['longitude'] is not None:
                location.set_coordinates(float(data['latitude']), float(data['longitude']))
        
        return location
    
    def __str__(self) -> str:
        return self.get_full_name()
    
    def __repr__(self) -> str:
        return f"Location(district='{self._district}', municipality='{self._municipality}', parish='{self._parish}')"


class LocationHierarchy:
    """
    Classe para representar hierarquia de localização portuguesa
    """
    
    def __init__(self):
        self._districts = []
    
    @property
    def districts(self) -> List[Dict]:
        return self._districts
    
    def add_district(self, district_data: Dict):
        """Adiciona distrito à hierarquia"""
        self._districts.append(district_data)
    
    def to_dict(self) -> Dict:
        """Converte para dicionário para JSON"""
        return {
            'districts': self._districts,
            'total_districts': len(self._districts)
        }
    
    def __str__(self) -> str:
        return f"LocationHierarchy with {len(self._districts)} districts"