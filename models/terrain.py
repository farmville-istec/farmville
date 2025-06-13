from datetime import datetime
from typing import Dict, Optional

class Terrain:
    """
    Classe para representar terrenos agrícolas dos utilizadores
    Updated to include Portuguese administrative location fields
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
        
        # New location fields
        self._district_id = None
        self._district_name = None
        self._municipality_id = None
        self._municipality_name = None
        self._parish_id = None
        self._parish_name = None
    
    # Existing properties
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
    
    # New location properties
    @property
    def district_id(self) -> Optional[int]:
        return self._district_id
    
    @property
    def district_name(self) -> Optional[str]:
        return self._district_name
    
    @property
    def municipality_id(self) -> Optional[int]:
        return self._municipality_id
    
    @property
    def municipality_name(self) -> Optional[str]:
        return self._municipality_name
    
    @property
    def parish_id(self) -> Optional[int]:
        return self._parish_id
    
    @property
    def parish_name(self) -> Optional[str]:
        return self._parish_name
    
    # Existing methods
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
    
    # New location methods
    def set_location_info(self, district_id: int, district_name: str, 
                         municipality_id: int, municipality_name: str,
                         parish_id: int, parish_name: str):
        """
        Set complete location information
        
        Args:
            district_id: District ID
            district_name: District name
            municipality_id: Municipality ID  
            municipality_name: Municipality name
            parish_id: Parish ID
            parish_name: Parish name
        """
        self._district_id = district_id
        self._district_name = district_name.strip() if district_name else None
        self._municipality_id = municipality_id
        self._municipality_name = municipality_name.strip() if municipality_name else None
        self._parish_id = parish_id
        self._parish_name = parish_name.strip() if parish_name else None
        self._updated_at = datetime.now()
    
    def set_location_from_location_object(self, location):
        """
        Set location info from Location object
        
        Args:
            location: Location object instance
        """
        self.set_location_info(
            location.district_id, location.district_name,
            location.municipality_id, location.municipality_name,
            location.parish_id, location.parish_name
        )
    
    def get_location_name(self) -> Optional[str]:
        """Get formatted location name"""
        if self._parish_name and self._municipality_name and self._district_name:
            return f"{self._parish_name}, {self._municipality_name}, {self._district_name}"
        return None
    
    def get_short_location_name(self) -> Optional[str]:
        """Get short location name (parish + municipality)"""
        if self._parish_name and self._municipality_name:
            return f"{self._parish_name}, {self._municipality_name}"
        return None
    
    def has_location_info(self) -> bool:
        """Check if terrain has complete location information"""
        return all([
            self._district_id, self._district_name,
            self._municipality_id, self._municipality_name,
            self._parish_id, self._parish_name
        ])
    
    def to_dict(self) -> Dict:
        """Converte para dicionário para JSON - Updated with location fields"""
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
            'updated_at': self._updated_at.isoformat() if self._updated_at else None,
            # Location fields
            'district': {
                'id': self._district_id,
                'name': self._district_name
            } if self._district_id else None,
            'municipality': {
                'id': self._municipality_id,
                'name': self._municipality_name
            } if self._municipality_id else None,
            'parish': {
                'id': self._parish_id,
                'name': self._parish_name
            } if self._parish_id else None,
            'location_name': self.get_location_name(),
            'short_location_name': self.get_short_location_name(),
            'has_location_info': self.has_location_info()
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Terrain':
        """Cria instância a partir de dicionário - Updated with location fields"""
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
        
        # Location fields
        district = data.get('district', {})
        municipality = data.get('municipality', {})
        parish = data.get('parish', {})
        
        if all([district.get('id'), municipality.get('id'), parish.get('id')]):
            terrain.set_location_info(
                district['id'], district['name'],
                municipality['id'], municipality['name'],
                parish['id'], parish['name']
            )
        
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
        location_part = f" in {self.get_location_name()}" if self.has_location_info() else ""
        return f"Terrain '{self._name}'{location_part} at ({self._latitude}, {self._longitude})"
    
    def __repr__(self) -> str:
        return (f"Terrain(id={self._id}, name='{self._name}', "
               f"user_id={self._user_id}, crop='{self._crop_type}', "
               f"location='{self.get_short_location_name()}')")