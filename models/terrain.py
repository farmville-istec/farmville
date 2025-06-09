from datetime import datetime
from typing import Dict, Optional

class Terrain:
    """
    Classe para representar terrenos agrícolas dos utilizadores
    """
    
    def __init__(self, name: str, latitude: float, longitude: float, user_id: int):
        self._id = None
        self._user_id = user_id
        self._name = name
        self._latitude = latitude
        self._longitude = longitude
        self._crop_type = None
        self._area_hectares = None
        self._notes = None
        self._created_at = datetime.now()
        self._updated_at = datetime.now()
    
    @property
    def id(self) -> Optional[int]:
        return self._id
    
    @property
    def user_id(self) -> int:
        return self._user_id
    
    @property
    def name(self) -> str:
        return self._name
    
    @property
    def latitude(self) -> float:
        return self._latitude
    
    @property
    def longitude(self) -> float:
        return self._longitude
    
    @property
    def crop_type(self) -> Optional[str]:
        return self._crop_type
    
    @property
    def area_hectares(self) -> Optional[float]:
        return self._area_hectares
    
    @property
    def notes(self) -> Optional[str]:
        return self._notes
    
    @property
    def created_at(self) -> datetime:
        return self._created_at
    
    @property
    def updated_at(self) -> datetime:
        return self._updated_at
    
    def set_id(self, terrain_id: int):
        self._id = terrain_id
    
    def set_crop_type(self, crop_type: str):
        self._crop_type = crop_type.strip() if crop_type else None
        self._updated_at = datetime.now()
    
    def set_area_hectares(self, area: float):
        if area < 0:
            raise ValueError("Área deve ser positiva")
        self._area_hectares = area
        self._updated_at = datetime.now()
    
    def set_notes(self, notes: str):
        self._notes = notes.strip() if notes else None
        self._updated_at = datetime.now()
    
    def update_coordinates(self, latitude: float, longitude: float):
        """Atualiza coordenadas do terreno"""
        if not (-90 <= latitude <= 90):
            raise ValueError("Latitude deve estar entre -90 e 90")
        if not (-180 <= longitude <= 180):
            raise ValueError("Longitude deve estar entre -180 e 180")
        
        self._latitude = latitude
        self._longitude = longitude
        self._updated_at = datetime.now()
    
    def update_name(self, name: str):
        """Atualiza nome do terreno"""
        if not name or not name.strip():
            raise ValueError("Nome não pode estar vazio")
        self._name = name.strip()
        self._updated_at = datetime.now()
    
    def to_dict(self) -> Dict:
        """Converte para dicionário para JSON"""
        return {
            'id': self._id,
            'user_id': self._user_id,
            'name': self._name,
            'latitude': self._latitude,
            'longitude': self._longitude,
            'crop_type': self._crop_type,
            'area_hectares': self._area_hectares,
            'notes': self._notes,
            'created_at': self._created_at.isoformat() if self._created_at else None,
            'updated_at': self._updated_at.isoformat() if self._updated_at else None
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Terrain':
        """Cria instância a partir de dicionário"""
        terrain = cls(
            data['name'],
            float(data['latitude']),
            float(data['longitude']),
            int(data['user_id'])
        )
        
        if 'id' in data:
            terrain.set_id(data['id'])
        
        if 'crop_type' in data and data['crop_type']:
            terrain.set_crop_type(data['crop_type'])
        
        if 'area_hectares' in data and data['area_hectares']:
            terrain.set_area_hectares(float(data['area_hectares']))
        
        if 'notes' in data and data['notes']:
            terrain.set_notes(data['notes'])
        
        if 'created_at' in data and data['created_at']:
            if isinstance(data['created_at'], str):
                terrain._created_at = datetime.fromisoformat(data['created_at'].replace('Z', '+00:00'))
            else:
                terrain._created_at = data['created_at']
        
        if 'updated_at' in data and data['updated_at']:
            if isinstance(data['updated_at'], str):
                terrain._updated_at = datetime.fromisoformat(data['updated_at'].replace('Z', '+00:00'))
            else:
                terrain._updated_at = data['updated_at']
        
        return terrain
    
    def __str__(self) -> str:
        return f"Terrain '{self._name}' at ({self._latitude}, {self._longitude})"
    
    def __repr__(self) -> str:
        return (f"Terrain(id={self._id}, name='{self._name}', "
               f"user_id={self._user_id}, crop='{self._crop_type}')")