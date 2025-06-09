"""
Terrain Service
"""

from typing import List, Dict, Any, Optional
from models.terrain import Terrain
from database.terrain_repository import TerrainRepository

class TerrainService:
    """
    Serviço de gestão de terrenos
    """
    
    def __init__(self):
        self.repository = TerrainRepository()
        print("🌱 Terrain Service initialized")
    
    def create_terrain(self, user_id: int, name: str, latitude: float, longitude: float, 
                      crop_type: str = None, area_hectares: float = None, notes: str = None) -> Dict[str, Any]:
        """
        Cria novo terreno
        
        Args:
            user_id: ID do utilizador
            name: Nome do terreno
            latitude: Latitude
            longitude: Longitude
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
            
            if not (-90 <= latitude <= 90):
                return {"success": False, "message": "Latitude deve estar entre -90 e 90"}
            
            if not (-180 <= longitude <= 180):
                return {"success": False, "message": "Longitude deve estar entre -180 e 180"}
            
            if area_hectares is not None and area_hectares <= 0:
                return {"success": False, "message": "Área deve ser positiva"}
            
            # Criar terreno
            terrain = Terrain(name.strip(), latitude, longitude, user_id)
            
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
            # Obter terreno atual
            terrain = self.repository.get_terrain_by_id(terrain_id)
            
            if not terrain:
                return {"success": False, "message": "Terreno não encontrado"}
            
            if terrain.user_id != user_id:
                return {"success": False, "message": "Acesso negado"}
            
            # Aplicar atualizações
            if 'name' in updates:
                terrain.update_name(updates['name'])
            
            if 'latitude' in updates and 'longitude' in updates:
                terrain.update_coordinates(updates['latitude'], updates['longitude'])
            
            if 'crop_type' in updates:
                terrain.set_crop_type(updates['crop_type'])
            
            if 'area_hectares' in updates:
                if updates['area_hectares']:
                    terrain.set_area_hectares(updates['area_hectares'])
            
            if 'notes' in updates:
                terrain.set_notes(updates['notes'])
            
            # Guardar na BD
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
            # Verificar se terreno existe e pertence ao utilizador
            terrain = self.repository.get_terrain_by_id(terrain_id)
            
            if not terrain:
                return {"success": False, "message": "Terreno não encontrado"}
            
            if terrain.user_id != user_id:
                return {"success": False, "message": "Acesso negado"}
            
            # Remover da BD
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
            
            total_area = sum(t.area_hectares for t in terrains if t.area_hectares)
            crops = list(set(t.crop_type for t in terrains if t.crop_type))
            
            return {
                "success": True,
                "stats": {
                    "total_terrains": len(terrains),
                    "total_area_hectares": total_area,
                    "crop_types": crops,
                    "avg_area": total_area / len(terrains) if terrains and total_area > 0 else 0
                }
            }
            
        except Exception as e:
            print(f"❌ Error getting terrain stats: {e}")
            return {"success": False, "message": f"Erro ao obter estatísticas: {str(e)}"}