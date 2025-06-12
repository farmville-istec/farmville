"""
Terrain Service
"""

from typing import List, Dict, Any, Optional
from models.terrain import Terrain
from database.terrain_repository import TerrainRepository

class TerrainService:
    """
    Serviço de gestão de terrenos com integração de localização
    """
    
    def __init__(self, location_service=None):
        self.repository = TerrainRepository()
        self.location_service = location_service  # Injected dependency
        print("🌱 Terrain Service initialized")
    
    def create_terrain(self, user_id: int, name: str, latitude: float = None, longitude: float = None, 
                      district: str = None, municipality: str = None, parish: str = None,
                      crop_type: str = None, area_hectares: float = None, notes: str = None) -> Dict[str, Any]:
        """
        Cria novo terreno com suporte para localização administrativa
        
        Args:
            user_id: ID do utilizador
            name: Nome do terreno
            latitude: Latitude (opcional se fornecida localização administrativa)
            longitude: Longitude (opcional se fornecida localização administrativa)
            district: Distrito português (opcional)
            municipality: Concelho português (opcional)
            parish: Freguesia portuguesa (opcional)
            crop_type: Tipo de cultura (opcional)
            area_hectares: Área em hectares (opcional)
            notes: Notas (opcional)
            
        Returns:
            Resultado da criação
        """
        try:
            # Validações básicas
            if not name or not name.strip():
                return {"success": False, "message": "Nome do terreno é obrigatório"}
            
            # Determinar coordenadas
            final_lat, final_lon = latitude, longitude
            
            # Se foram fornecidos dados de localização administrativa, usar o location service
            if all([district, municipality, parish]) and self.location_service:
                print(f"🌐 Using location service to get coordinates for {parish}, {municipality}, {district}")
                location = self.location_service.get_coordinates_for_location(district, municipality, parish)
                
                if location and location.is_complete():
                    final_lat, final_lon = location.latitude, location.longitude
                    print(f"✅ Coordinates found: {final_lat}, {final_lon}")
                else:
                    return {"success": False, "message": "Localização não encontrada"}
            
            # Validar coordenadas finais
            if final_lat is None or final_lon is None:
                return {"success": False, "message": "Coordenadas ou localização administrativa são obrigatórias"}
            
            if not (-90 <= final_lat <= 90):
                return {"success": False, "message": "Latitude deve estar entre -90 e 90"}
            
            if not (-180 <= final_lon <= 180):
                return {"success": False, "message": "Longitude deve estar entre -180 e 180"}
            
            if area_hectares is not None and area_hectares <= 0:
                return {"success": False, "message": "Área deve ser positiva"}
            
            # Criar terreno
            terrain = Terrain(name.strip(), final_lat, final_lon, user_id)
            
            # Definir localização administrativa se fornecida
            if all([district, municipality, parish]):
                terrain.set_location(district, municipality, parish)
            
            if crop_type:
                terrain.set_crop_type(crop_type)
            
            if area_hectares:
                terrain.set_area_hectares(area_hectares)
            
            if notes:
                terrain.set_notes(notes)
            
            # Guardar na BD
            terrain_id = self.repository.create_terrain(terrain)
            
            print(f"✅ Terrain '{name}' created for user {user_id}")
            
            return {
                "success": True,
                "message": "Terreno criado com sucesso",
                "terrain_id": terrain_id,
                "terrain": terrain.to_dict()
            }
            
        except Exception as e:
            print(f"❌ Error creating terrain: {e}")
            return {"success": False, "message": f"Erro ao criar terreno: {str(e)}"}
    
    def create_terrain_with_location(self, user_id: int, name: str, district: str, municipality: str, parish: str,
                                   crop_type: str = None, area_hectares: float = None, notes: str = None) -> Dict[str, Any]:
        """
        Cria terreno usando apenas localização administrativa portuguesa
        
        Args:
            user_id: ID do utilizador
            name: Nome do terreno
            district: Distrito
            municipality: Concelho
            parish: Freguesia
            crop_type: Tipo de cultura (opcional)
            area_hectares: Área em hectares (opcional)
            notes: Notas (opcional)
            
        Returns:
            Resultado da criação
        """
        return self.create_terrain(
            user_id=user_id,
            name=name,
            district=district,
            municipality=municipality,
            parish=parish,
            crop_type=crop_type,
            area_hectares=area_hectares,
            notes=notes
        )
    
    def get_user_terrains(self, user_id: int) -> Dict[str, Any]:
        """
        Obtém todos os terrenos de um utilizador
        
        Args:
            user_id: ID do utilizador
            
        Returns:
            Lista de terrenos
        """
        try:
            terrains = self.repository.get_terrains_by_user(user_id)
            
            return {
                "success": True,
                "terrains": [terrain.to_dict() for terrain in terrains],
                "count": len(terrains)
            }
            
        except Exception as e:
            print(f"❌ Error getting user terrains: {e}")
            return {"success": False, "message": f"Erro ao obter terrenos: {str(e)}"}
    
    def get_terrains_by_location(self, district: str = None, municipality: str = None, parish: str = None) -> Dict[str, Any]:
        """
        Obtém terrenos por localização administrativa
        
        Args:
            district: Distrito (opcional)
            municipality: Concelho (opcional)
            parish: Freguesia (opcional)
            
        Returns:
            Lista de terrenos na localização
        """
        try:
            terrains = self.repository.get_terrains_by_location(district, municipality, parish)
            
            return {
                "success": True,
                "terrains": [terrain.to_dict() for terrain in terrains],
                "count": len(terrains),
                "location_filter": {
                    "district": district,
                    "municipality": municipality,
                    "parish": parish
                }
            }
            
        except Exception as e:
            print(f"❌ Error getting terrains by location: {e}")
            return {"success": False, "message": f"Erro ao obter terrenos por localização: {str(e)}"}
    
    def get_terrain(self, terrain_id: int, user_id: int) -> Dict[str, Any]:
        """
        Obtém terreno específico (se pertencer ao utilizador)
        
        Args:
            terrain_id: ID do terreno
            user_id: ID do utilizador
            
        Returns:
            Dados do terreno
        """
        try:
            terrain = self.repository.get_terrain_by_id(terrain_id)
            
            if not terrain:
                return {"success": False, "message": "Terreno não encontrado"}
            
            if terrain.user_id != user_id:
                return {"success": False, "message": "Acesso negado"}
            
            return {
                "success": True,
                "terrain": terrain.to_dict()
            }
            
        except Exception as e:
            print(f"❌ Error getting terrain: {e}")
            return {"success": False, "message": f"Erro ao obter terreno: {str(e)}"}
    
    def update_terrain(self, terrain_id: int, user_id: int, **updates) -> Dict[str, Any]:
        """
        Atualiza terreno
        
        Args:
            terrain_id: ID do terreno
            user_id: ID do utilizador
            **updates: Campos a atualizar
            
        Returns:
            Resultado da atualização
        """
        try:
            
            terrain = self.repository.get_terrain_by_id(terrain_id)
            
            if not terrain:
                return {"success": False, "message": "Terreno não encontrado"}
            
            if terrain.user_id != user_id:
                return {"success": False, "message": "Acesso negado"}
            
            
            if 'name' in updates:
                terrain.update_name(updates['name'])
            
            if all(key in updates for key in ['district', 'municipality', 'parish']):
                district = updates['district']
                municipality = updates['municipality']
                parish = updates['parish']
                
                if all([district, municipality, parish]) and self.location_service:
                    location = self.location_service.get_coordinates_for_location(district, municipality, parish)
                    if location and location.is_complete():
                        terrain.update_coordinates(location.latitude, location.longitude)
                        terrain.set_location(district, municipality, parish)
                else:
                    terrain.set_location(district, municipality, parish)
            
            
            elif 'latitude' in updates and 'longitude' in updates:
                terrain.update_coordinates(updates['latitude'], updates['longitude'])
            
            if 'crop_type' in updates:
                terrain.set_crop_type(updates['crop_type'])
            
            if 'area_hectares' in updates:
                if updates['area_hectares']:
                    terrain.set_area_hectares(updates['area_hectares'])
            
            if 'notes' in updates:
                terrain.set_notes(updates['notes'])
            
            self.repository.update_terrain(terrain)
            
            print(f"✅ Terrain {terrain_id} updated")
            
            return {
                "success": True,
                "message": "Terreno atualizado com sucesso",
                "terrain": terrain.to_dict()
            }
            
        except Exception as e:
            print(f"❌ Error updating terrain: {e}")
            return {"success": False, "message": f"Erro ao atualizar terreno: {str(e)}"}
    
    def delete_terrain(self, terrain_id: int, user_id: int) -> Dict[str, Any]:
        """
        Remove terreno
        
        Args:
            terrain_id: ID do terreno
            user_id: ID do utilizador
            
        Returns:
            Resultado da remoção
        """
        try:
           
            terrain = self.repository.get_terrain_by_id(terrain_id)
            
            if not terrain:
                return {"success": False, "message": "Terreno não encontrado"}
            
            if terrain.user_id != user_id:
                return {"success": False, "message": "Acesso negado"}
            
           
            self.repository.delete_terrain(terrain_id, user_id)
            
            print(f"✅ Terrain {terrain_id} deleted")
            
            return {
                "success": True,
                "message": "Terreno removido com sucesso"
            }
            
        except Exception as e:
            print(f"❌ Error deleting terrain: {e}")
            return {"success": False, "message": f"Erro ao remover terreno: {str(e)}"}
    
    def get_terrain_stats(self, user_id: int) -> Dict[str, Any]:
        """
        Obtém estatísticas dos terrenos do utilizador
        
        Args:
            user_id: ID do utilizador
            
        Returns:
            Estatísticas
        """
        try:
            terrains = self.repository.get_terrains_by_user(user_id)
            location_stats = self.repository.get_location_stats(user_id)
            
            total_area = sum(t.area_hectares for t in terrains if t.area_hectares)
            crops = list(set(t.crop_type for t in terrains if t.crop_type))
        
            terrains_with_location = sum(1 for t in terrains if t.has_administrative_location())
            
            return {
                "success": True,
                "stats": {
                    "total_terrains": len(terrains),
                    "total_area_hectares": total_area,
                    "crop_types": crops,
                    "avg_area": total_area / len(terrains) if terrains and total_area > 0 else 0,
                    "terrains_with_administrative_location": terrains_with_location,
                    "location_coverage_percentage": (terrains_with_location / len(terrains) * 100) if terrains else 0,
                    "location_breakdown": location_stats.get('location_breakdown', [])
                }
            }
            
        except Exception as e:
            print(f"❌ Error getting terrain stats: {e}")
            return {"success": False, "message": f"Erro ao obter estatísticas: {str(e)}"}