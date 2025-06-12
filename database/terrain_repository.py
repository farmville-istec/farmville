"""
Terrain Repository
"""

from typing import Optional, List, Dict, Any
from models.terrain import Terrain
from .connection import DatabaseConnection

class TerrainRepository:
    """Repository para gestão de dados de terrenos"""
    
    def __init__(self):
        self.db = DatabaseConnection()
    
    def create_terrain(self, terrain: Terrain) -> int:
        """
        Cria novo terreno na BD
        
        Args:
            terrain: Instância de Terrain
            
        Returns:
            int: ID do terreno criado
        """
        sql = """
        INSERT INTO terrains (user_id, name, latitude, longitude, district, municipality, parish, crop_type, area_hectares, notes)
        VALUES (:user_id, :name, :latitude, :longitude, :district, :municipality, :parish, :crop_type, :area_hectares, :notes)
        RETURNING id;
        """
        
        with self.db.get_connection() as conn:
            result = conn.run(
                sql,
                user_id=terrain.user_id,
                name=terrain.name,
                latitude=terrain.latitude,
                longitude=terrain.longitude,
                district=terrain.district,
                municipality=terrain.municipality,
                parish=terrain.parish,
                crop_type=terrain.crop_type,
                area_hectares=terrain.area_hectares,
                notes=terrain.notes
            )
            terrain_id = result[0][0]
            terrain.set_id(terrain_id)
            return terrain_id
    
    def get_terrain_by_id(self, terrain_id: int) -> Optional[Terrain]:
        """
        Obtém terreno pelo ID
        
        Args:
            terrain_id: ID do terreno
            
        Returns:
            Terrain ou None se não encontrado
        """
        sql = "SELECT * FROM terrains WHERE id = :terrain_id;"
        
        with self.db.get_connection() as conn:
            result = conn.run(sql, terrain_id=terrain_id)
            
            if not result:
                return None
            
            return self._row_to_terrain(result[0])
    
    def get_terrains_by_user(self, user_id: int) -> List[Terrain]:
        """
        Obtém todos os terrenos de um utilizador
        
        Args:
            user_id: ID do utilizador
            
        Returns:
            Lista de terrenos
        """
        sql = "SELECT * FROM terrains WHERE user_id = :user_id ORDER BY created_at DESC;"
        
        with self.db.get_connection() as conn:
            result = conn.run(sql, user_id=user_id)
            
            return [self._row_to_terrain(row) for row in result]
    
    def get_terrains_by_location(self, district: str = None, municipality: str = None, parish: str = None) -> List[Terrain]:
        """
        Obtém terrenos por localização administrativa
        
        Args:
            district: Nome do distrito (opcional)
            municipality: Nome do concelho (opcional)  
            parish: Nome da freguesia (opcional)
            
        Returns:
            Lista de terrenos
        """
        conditions = []
        params = {}
        
        if district:
            conditions.append("district = :district")
            params['district'] = district
        
        if municipality:
            conditions.append("municipality = :municipality")
            params['municipality'] = municipality
        
        if parish:
            conditions.append("parish = :parish")
            params['parish'] = parish
        
        if not conditions:
            return []
        
        sql = f"SELECT * FROM terrains WHERE {' AND '.join(conditions)} ORDER BY created_at DESC;"
        
        with self.db.get_connection() as conn:
            result = conn.run(sql, **params)
            
            return [self._row_to_terrain(row) for row in result]
    
    def update_terrain(self, terrain: Terrain) -> bool:
        """
        Atualiza terreno na BD
        
        Args:
            terrain: Instância de Terrain
            
        Returns:
            bool: True se atualizado com sucesso
        """
        sql = """
        UPDATE terrains 
        SET name = :name, 
            latitude = :latitude, 
            longitude = :longitude,
            district = :district,
            municipality = :municipality,
            parish = :parish,
            crop_type = :crop_type,
            area_hectares = :area_hectares,
            notes = :notes,
            updated_at = NOW()
        WHERE id = :terrain_id AND user_id = :user_id;
        """
        
        with self.db.get_connection() as conn:
            conn.run(
                sql,
                terrain_id=terrain.id,
                user_id=terrain.user_id,
                name=terrain.name,
                latitude=terrain.latitude,
                longitude=terrain.longitude,
                district=terrain.district,
                municipality=terrain.municipality,
                parish=terrain.parish,
                crop_type=terrain.crop_type,
                area_hectares=terrain.area_hectares,
                notes=terrain.notes
            )
            return True
    
    def delete_terrain(self, terrain_id: int, user_id: int) -> bool:
        """
        Remove terreno da BD (apenas se pertencer ao utilizador)
        
        Args:
            terrain_id: ID do terreno
            user_id: ID do utilizador (para segurança)
            
        Returns:
            bool: True se removido com sucesso
        """
        sql = "DELETE FROM terrains WHERE id = :terrain_id AND user_id = :user_id;"
        
        with self.db.get_connection() as conn:
            conn.run(sql, terrain_id=terrain_id, user_id=user_id)
            return True
    
    def get_terrain_count_by_user(self, user_id: int) -> int:
        """
        Obtém número total de terrenos de um utilizador
        
        Args:
            user_id: ID do utilizador
            
        Returns:
            int: Número de terrenos
        """
        sql = "SELECT COUNT(*) FROM terrains WHERE user_id = :user_id;"
        
        with self.db.get_connection() as conn:
            result = conn.run(sql, user_id=user_id)
            return result[0][0]
    
    def get_location_stats(self, user_id: int = None) -> dict:
        """
        Obtém estatísticas de localização dos terrenos
        
        Args:
            user_id: ID do utilizador (opcional, None para todos)
            
        Returns:
            Estatísticas de localização
        """
        base_sql = """
        SELECT 
            district,
            municipality,
            COUNT(*) as terrain_count,
            AVG(area_hectares) as avg_area
        FROM terrains 
        WHERE district IS NOT NULL AND municipality IS NOT NULL
        """
        
        if user_id:
            sql = base_sql + " AND user_id = :user_id GROUP BY district, municipality ORDER BY terrain_count DESC;"
            params = {'user_id': user_id}
        else:
            sql = base_sql + " GROUP BY district, municipality ORDER BY terrain_count DESC;"
            params = {}
        
        with self.db.get_connection() as conn:
            result = conn.run(sql, **params)
            
            stats = []
            for row in result:
                stats.append({
                    'district': row[0],
                    'municipality': row[1], 
                    'terrain_count': row[2],
                    'avg_area': float(row[3]) if row[3] else 0
                })
            
            return {
                'location_breakdown': stats,
                'total_locations': len(stats)
            }
    
    def get_all_terrains(self) -> List[Terrain]:
        """
        Obtém todos os terrenos (admin)
        
        Returns:
            Lista de todos os terrenos
        """
        sql = "SELECT * FROM terrains ORDER BY created_at DESC;"
        
        with self.db.get_connection() as conn:
            result = conn.run(sql)
            
            return [self._row_to_terrain(row) for row in result]
    
    def clear_all_terrains(self):
        """Remove todos os terrenos (para testes)"""
        sql = "DELETE FROM terrains;"
        
        with self.db.get_connection() as conn:
            conn.run(sql)
    
    def _row_to_terrain(self, row) -> Terrain:
        """
        Converte linha da BD em objeto Terrain
        
        Args:
            row: Linha da base de dados
            
        Returns:
            Terrain: Instância de Terrain
        """
        # pg8000 returns rows as tuples, map to column names
        columns = ['id', 'user_id', 'name', 'latitude', 'longitude', 
                  'district', 'municipality', 'parish', 'crop_type', 'area_hectares', 'notes', 'created_at', 'updated_at']
        data = dict(zip(columns, row))
        
        return Terrain.from_dict(data)