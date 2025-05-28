from datetime import datetime
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import json
import uuid

class LocationType(Enum):
    """Tipos de Forma de "Desenhar" a localização"""
    PONTO = "PONTO"
    POLÍGONO = "POLÍGONO"
    RETANGULO = "RETANGULO"


@dataclass
class Coordinate:
    
    latitude: float
    longitude: float
    
    """Valida as coordenadas"""
    def __post_init__(self):
        if not (-90 <= self.latitude <= 90):
            raise ValueError(f"Latitude deve estar entre -90 and 90, got {self.latitude}")
        if not (-180 <= self.longitude <= 180):
            raise ValueError(f"Longitude deve estar entre -180 and 180, got {self.longitude}")
    
    def to_dict(self) -> Dict:
        return {"lat": self.latitude, "lng": self.longitude}
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Coordinate':
        return cls(data['lat'], data['lng'])

class FieldLocation:
    """
    Classe para representar a localização de um campo agrícola
    """
    
    def __init__(self, name: str, location_type: LocationType, user_id: str):
        self._id = str(uuid.uuid4())
        self._name = name
        self._location_type = location_type
        self._user_id = user_id
        self._coordinates: List[Coordinate] = []
        self._center_PONTO: Optional[Coordinate] = None
        self._area_hectares: Optional[float] = None
        self._description: Optional[str] = None
        self._created_at = datetime.now()
        self._updated_at = datetime.now()
        self._is_active = True
    
    # Properties
    @property
    def id(self) -> str:
        return self._id
    
    @property
    def name(self) -> str:
        return self._name
    
    @property
    def location_type(self) -> LocationType:
        return self._location_type
    
    @property
    def user_id(self) -> str:
        return self._user_id
    
    @property
    def coordinates(self) -> List[Coordinate]:
        return self._coordinates.copy()
    
    @property
    def center_PONTO(self) -> Optional[Coordinate]:
        return self._center_PONTO
    
    @property
    def area_hectares(self) -> Optional[float]:
        return self._area_hectares
    
    
    @property
    def description(self) -> Optional[str]:
        return self._description
    
    @property
    def created_at(self) -> datetime:
        return self._created_at
    
    @property
    def updated_at(self) -> datetime:
        return self._updated_at
    
    @property
    def is_active(self) -> bool:
        return self._is_active
    
    # Setters
    def set_name(self, name: str):
        """Define o nome do campo agrícola"""
        if not name or not name.strip():
            raise ValueError("Nome do campo não pode ser vazio")
        self._name = name.strip()
        self._update_timestamp()
    
    def set_coordinates(self, coordinates: List[Coordinate]):
        """Define as coordenadas do campo"""
        if not coordinates:
            raise ValueError("Lista de coordenadas não pode ser vazia")
        
        # Validação baseada no tipo de localização
        if self._location_type == LocationType.PONTO and len(coordinates) != 1:
            raise ValueError("Tipo PONTO deve ter exatamente 1 coordenada")
        elif self._location_type == LocationType.RETANGULO and len(coordinates) != 2:
            raise ValueError("Tipo RETANGULO deve ter exatamente 2 coordenadas (diagonal)")
        elif self._location_type == LocationType.POLÍGONO and len(coordinates) < 3:
            raise ValueError("Tipo POLÍGONO deve ter pelo menos 3 coordenadas")
        
        self._coordinates = coordinates.copy()
        self._calculate_center_PONTO()
        self._calculate_area()
        self._update_timestamp()
    
    def add_coordinate(self, coordinate: Coordinate):
        """Adiciona uma coordenada"""
        self._coordinates.append(coordinate)
        self._calculate_center_PONTO()
        self._calculate_area()
        self._update_timestamp()
    
    
    def set_description(self, description: str):
        """Define a descrição do campo"""
        self._description = description.strip() if description else None
        self._update_timestamp()
    
    def deactivate(self):
        """Desativa o campo"""
        self._is_active = False
        self._update_timestamp()
    
    def activate(self):
        """Ativa o campo"""
        self._is_active = True
        self._update_timestamp()
    
    # Métodos privados
    def _update_timestamp(self):
        """Atualiza o timestamp de modificação"""
        self._updated_at = datetime.now()
    
    def _calculate_center_PONTO(self):
        """Calcula o ponto central das coordenadas"""
        if not self._coordinates:
            self._center_PONTO = None
            return
        
        if self._location_type == LocationType.PONTO:
            self._center_PONTO = self._coordinates[0]
        else:
            # Calcula a média das coordenadas
            avg_lat = sum(coord.latitude for coord in self._coordinates) / len(self._coordinates)
            avg_lng = sum(coord.longitude for coord in self._coordinates) / len(self._coordinates)
            self._center_PONTO = Coordinate(avg_lat, avg_lng)
    
    def _calculate_area(self):
        """Calcula a área aproximada em hectares"""
        if self._location_type == LocationType.PONTO:
            self._area_hectares = 0.0
            return
        
        if self._location_type == LocationType.RETANGULO and len(self._coordinates) == 2:
            # Cálculo simples para retângulo
            coord1, coord2 = self._coordinates[0], self._coordinates[1]
            lat_diff = abs(coord2.latitude - coord1.latitude)
            lng_diff = abs(coord2.longitude - coord1.longitude)
            
            # Conversão aproximada (1 grau ≈ 111 km)
            area_km2 = (lat_diff * 111) * (lng_diff * 111 * abs(coord1.latitude) / 90)
            self._area_hectares = area_km2 * 100  # km² para hectares
        
        elif self._location_type == LocationType.POLÍGONO and len(self._coordinates) >= 3:
            # Usar fórmula Shoelace para polígonos
            self._area_hectares = self._calculate_POLÍGONO_area()
    
    def _calculate_POLÍGONO_area(self) -> float:
        """Calcula área de polígono usando fórmula Shoelace"""
        if len(self._coordinates) < 3:
            return 0.0
        
        # Fórmula Shoelace
        area = 0.0
        n = len(self._coordinates)
        
        for i in range(n):
            j = (i + 1) % n
            area += self._coordinates[i].latitude * self._coordinates[j].longitude
            area -= self._coordinates[j].latitude * self._coordinates[i].longitude
        
        area = abs(area) / 2.0
        
        # Conversão aproximada para hectares (muito simplificada)
        # Para cálculo real, seria necessário considerar projeção cartográfica
        area_km2 = area * (111 * 111)  # graus² para km²
        return area_km2 * 100  # km² para hectares
    
    # Métodos de validação
    def is_valid(self) -> bool:
        """Verifica se o campo tem dados válidos"""
        return (
            bool(self._name and self._name.strip()) and
            bool(self._coordinates) and
            self._center_PONTO is not None
        )
    
    def get_validation_errors(self) -> List[str]:
        """Retorna lista de erros de validação"""
        errors = []
        
        if not self._name or not self._name.strip():
            errors.append("Nome do campo é obrigatório")
        
        if not self._coordinates:
            errors.append("Coordenadas são obrigatórias")
        
        if self._location_type == LocationType.PONTO and len(self._coordinates) != 1:
            errors.append("Tipo PONTO deve ter exatamente 1 coordenada")
        elif self._location_type == LocationType.RETANGULO and len(self._coordinates) != 2:
            errors.append("Tipo RETANGULO deve ter exatamente 2 coordenadas")
        elif self._location_type == LocationType.POLÍGONO and len(self._coordinates) < 3:
            errors.append("Tipo POLÍGONO deve ter pelo menos 3 coordenadas")
        
        return errors
    
    # Serialização
    def to_dict(self) -> Dict:
        """Converte para dicionário"""
        return {
            'id': self._id,
            'name': self._name,
            'location_type': self._location_type.value,
            'user_id': self._user_id,
            'coordinates': [coord.to_dict() for coord in self._coordinates],
            'center_PONTO': self._center_PONTO.to_dict() if self._center_PONTO else None,
            'area_hectares': self._area_hectares,
            'crop_type': self._crop_type.value if self._crop_type else None,
            'description': self._description,
            'created_at': self._created_at.isoformat(),
            'updated_at': self._updated_at.isoformat(),
            'is_active': self._is_active,
            'is_valid': self.is_valid()
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'FieldLocation':
        """Cria instância a partir de dicionário"""
        field = cls(
            name=data['name'],
            location_type=LocationType(data['location_type']),
            user_id=data['user_id']
        )
        
        field._id = data['id']
        field._coordinates = [Coordinate.from_dict(coord) for coord in data['coordinates']]
        field._center_PONTO = Coordinate.from_dict(data['center_PONTO']) if data['center_PONTO'] else None
        field._area_hectares = data.get('area_hectares')
        field._description = data.get('description')
        field._created_at = datetime.fromisoformat(data['created_at'])
        field._updated_at = datetime.fromisoformat(data['updated_at'])
        field._is_active = data.get('is_active', True)
        
        return field
    
    def __str__(self) -> str:
        """Printar em String"""
        return f"FieldLocation('{self._name}', {self._location_type.value}, {len(self._coordinates)} coords)"
    
    def __repr__(self) -> str:
        """Printar para Test"""
        return (f"FieldLocation(id='{self._id}', name='{self._name}', "
               f"type={self._location_type.value}, valid={self.is_valid()})")