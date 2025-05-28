from typing import List, Dict, Optional, Tuple
import json
import logging
from datetime import datetime
import os
from models.location_data import FieldLocation, LocationType, Coordinate

class LocationService:
    """
    Serviço para gestão de localizações de campos agrícolas
    """
    
    def __init__(self, storage_path: str = "data/fields.json"):
        self._storage_path = storage_path
        self._fields: Dict[str, FieldLocation] = {}
        self._logger = logging.getLogger(__name__)
        
        os.makedirs(os.path.dirname(storage_path), exist_ok=True)
        
        self._load_from_storage()

    """CRUD"""

    def create_field(self, name: str, location_type: LocationType, user_id: str,
                    coordinates: List[Coordinate], description: Optional[str] = None) -> FieldLocation:
        
        try:
            # Cria o campo
            field = FieldLocation(name, location_type, user_id)
            field.set_coordinates(coordinates)
            
            if description:
                field.set_description(description)
            
            # Valida
            if not field.is_valid():
                errors = field.get_validation_errors()
                raise ValueError(f"Campo inválido: {', '.join(errors)}")
            
            # Armazena
            self._fields[field.id] = field
            self._save_to_storage()
            
            self._logger.info(f"Campo criado: {field.name} (ID: {field.id})")
            return field
            
        except Exception as e:
            self._logger.error(f"Erro ao criar campo {name}: {e}")
            raise

    def get_field(self, field_id: str) -> Optional[FieldLocation]:
        return self._fields.get(field_id)

    def get_fields_by_user(self, user_id: str, active_only: bool = True) -> List[FieldLocation]:
        fields = []
        for field in self._fields.values():
            if field.user_id == user_id:
                if not active_only or field.is_active:
                    fields.append(field)
        return sorted(fields, key=lambda f: f.created_at, reverse=True)

    def update_field(self, field_id: str, **updates) -> Optional[FieldLocation]:
        field = self._fields.get(field_id)
        if not field:
            return None
        
        try:
            if 'name' in updates:
                field.set_name(updates['name'])
            
            if 'coordinates' in updates:
                field.set_coordinates(updates['coordinates'])
            
            if 'description' in updates:
                field.set_description(updates['description'])
            
            if not field.is_valid():
                errors = field.get_validation_errors()
                raise ValueError(f"Dados inválidos: {', '.join(errors)}")
            
            self._save_to_storage()
            self._logger.info(f"Campo atualizado: {field.name} (ID: {field_id})")
            return field
        
        except Exception as e:
            self._logger.error(f"Erro ao atualizar campo {field_id}: {e}")
            raise

    def delete_field(self, field_id: str, soft_delete: bool = True) -> bool:
        field = self._fields.get(field_id)
        if not field:
            return False
        
        if soft_delete:
            field.deactivate()
            self._logger.info(f"Campo desativado: {field.name} (ID: {field_id})")
        else:
            del self._fields[field_id]
            self._logger.info(f"Campo removido: {field.name} (ID: {field_id})")
        
        self._save_to_storage()
        return True

    # === OPERAÇÕES DE PESQUISA ===

    def search_fields(self, user_id: str, **filters) -> List[FieldLocation]:
        fields = self.get_fields_by_user(user_id, active_only=filters.get('active_only', True))

        if 'name' in filters:
            name_filter = filters['name'].lower()
            fields = [f for f in fields if name_filter in f.name.lower()]

        if 'location_type' in filters:
            fields = [f for f in fields if f.location_type == filters['location_type']]

        if 'min_area' in filters and filters['min_area'] is not None:
            fields = [f for f in fields if f.area_hectares and f.area_hectares >= filters['min_area']]

        if 'max_area' in filters and filters['max_area'] is not None:
            fields = [f for f in fields if f.area_hectares and f.area_hectares <= filters['max_area']]

        return fields

    def get_fields_near_location(self, center: Coordinate, radius_km: float, 
                               user_id: Optional[str] = None) -> List[Tuple[FieldLocation, float]]:
        nearby_fields = []
        
        for field in self._fields.values():
            if user_id and field.user_id != user_id:
                continue
            
            if not field.is_active or not field.center_point:
                continue
            
            distance = self._calculate_distance(center, field.center_point)
            if distance <= radius_km:
                nearby_fields.append((field, distance))
        
        nearby_fields.sort(key=lambda x: x[1])
        return nearby_fields

    # === OPERAÇÕES DE GEOMETRIA ===

    def create_point_field(self, name: str, user_id: str, latitude: float, longitude: float,
                          description: Optional[str] = None) -> FieldLocation:
        coordinate = Coordinate(latitude, longitude)
        return self.create_field(name, LocationType.POINT, user_id, [coordinate], description)

    def create_rectangle_field(self, name: str, user_id: str, 
                              corner1: Tuple[float, float], corner2: Tuple[float, float],
                              description: Optional[str] = None) -> FieldLocation:
        coord1 = Coordinate(corner1[0], corner1[1])
        coord2 = Coordinate(corner2[0], corner2[1])
        return self.create_field(name, LocationType.RECTANGLE, user_id, [coord1, coord2], description)

    def create_polygon_field(self, name: str, user_id: str, vertices: List[Tuple[float, float]],
                           description: Optional[str] = None) -> FieldLocation:
        coordinates = [Coordinate(lat, lng) for lat, lng in vertices]
        return self.create_field(name, LocationType.POLYGON, user_id, coordinates, description)

    # === ESTATÍSTICAS ===

    def get_user_statistics(self, user_id: str) -> Dict:
        fields = self.get_fields_by_user(user_id)
        
        if not fields:
            return {
                'total_fields': 0,
                'total_area_hectares': 0,
                'location_types': {},
                'active_fields': 0
            }

        total_area = sum(f.area_hectares or 0 for f in fields)
        active_fields = sum(1 for f in fields if f.is_active)

        location_counts = {}
        for field in fields:
            loc_type = field.location_type.value
            location_counts[loc_type] = location_counts.get(loc_type, 0) + 1

        return {
            'total_fields': len(fields),
            'total_area_hectares': round(total_area, 2),
            'location_types': location_counts,
            'active_fields': active_fields,
            'average_field_size': round(total_area / len(fields), 2) if fields else 0
        }

    def _calculate_distance(self, coord1: Coordinate, coord2: Coordinate) -> float:
        import math
        
        lat1, lon1 = math.radians(coord1.latitude), math.radians(coord1.longitude)
        lat2, lon2 = math.radians(coord2.latitude), math.radians(coord2.longitude)
        
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        
        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
        c = 2 * math.asin(math.sqrt(a))
        
        earth_radius_km = 6371.0
        
        return earth_radius_km * c

    def _load_from_storage(self):
        try:
            if os.path.exists(self._storage_path):
                with open(self._storage_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                for field_data in data.get('fields', []):
                    field = FieldLocation.from_dict(field_data)
                    self._fields[field.id] = field
                
                self._logger.info(f"Carregados {len(self._fields)} campos do armazenamento")
        except Exception as e:
            self._logger.error(f"Erro ao carregar dados: {e}")

    def _save_to_storage(self):
        try:
            data = {
                'version': '1.0',
                'updated_at': datetime.now().isoformat(),
                'fields': [field.to_dict() for field in self._fields.values()]
            }
            
            with open(self._storage_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            self._logger.error(f"Erro ao guardar dados: {e}")
            raise

    def get_all_location_types(self) -> List[str]:
        return [loc.value for loc in LocationType]

    def get_service_info(self) -> Dict:
        return {
            'total_fields': len(self._fields),
            'active_fields': sum(1 for f in self._fields.values() if f.is_active),
            'storage_path': self._storage_path,
            'supported_location_types': self.get_all_location_types()
        }

    def export_user_data(self, user_id: str) -> Dict:
        fields = self.get_fields_by_user(user_id, active_only=False)
        
        return {
            'user_id': user_id,
            'export_date': datetime.now().isoformat(),
            'fields': [field.to_dict() for field in fields],
            'statistics': self.get_user_statistics(user_id)
        }
