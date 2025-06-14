"""
Terrain Repository - Updated with Location Fields
"""

from typing import Optional, List
from models.terrain import Terrain
from .connection import DatabaseConnection

class TerrainRepository:
    """Repository para gestão de dados de terrenos com suporte a localização"""
    
    def __init__(self):
        self.db = DatabaseConnection()
    
    def create_terrain(self, terrain: Terrain) -> int:
        """
        Cria novo terreno na BD - Updated with location fields
        
        Args:
            terrain: Instância de Terrain
            
        Returns:
            int: ID do terreno criado
        """
        sql = """
        INSERT INTO terrains (
            user_id, name, latitude, longitude, crop_type, area_hectares, notes,
            district_id, district_name, municipality_id, municipality_name, 
            parish_id, parish_name
        )
        VALUES (
            :user_id, :name, :latitude, :longitude, :crop_type, :area_hectares, :notes,
            :district_id, :district_name, :municipality_id, :municipality_name,
            :parish_id, :parish_name
        )
        RETURNING id;
        """
        
        with self.db.get_connection() as conn:
            result = conn.run(
                sql,
                user_id=terrain.user_id,
                name=terrain.name,
                latitude=terrain.latitude,
                longitude=terrain.longitude,
                crop_type=terrain.crop_type,
                area_hectares=terrain.area_hectares,
                notes=terrain.notes,
                district_id=terrain.district_id,
                district_name=terrain.district_name,
                municipality_id=terrain.municipality_id,
                municipality_name=terrain.municipality_name,
                parish_id=terrain.parish_id,
                parish_name=terrain.parish_name
            )
            terrain_id = result[0][0]
            terrain.set_id(terrain_id)
            return terrain_id
    
    def get_terrain_by_id(self, terrain_id: int) -> Optional[Terrain]:
        """
        Obtém terreno pelo ID - Updated with location fields
        
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
        Obtém todos os terrenos de um utilizador - Updated with location fields
        
        Args:
            user_id: ID do utilizador
            
        Returns:
            Lista de terrenos
        """
        sql = "SELECT * FROM terrains WHERE user_id = :user_id ORDER BY created_at DESC;"
        
        with self.db.get_connection() as conn:
            result = conn.run(sql, user_id=user_id)
            
            return [self._row_to_terrain(row) for row in result]
    
    def get_terrains_by_location(self, user_id: int, district_id: int = None, 
                                municipality_id: int = None, parish_id: int = None) -> List[Terrain]:
        """
        Get terrains by location filters
        
        Args:
            user_id: User ID
            district_id: District ID (optional)
            municipality_id: Municipality ID (optional)
            parish_id: Parish ID (optional)
            
        Returns:
            List of terrains matching location filters
        """
        conditions = ["user_id = :user_id"]
        params = {"user_id": user_id}
        
        if district_id:
            conditions.append("district_id = :district_id")
            params["district_id"] = district_id
        
        if municipality_id:
            conditions.append("municipality_id = :municipality_id")
            params["municipality_id"] = municipality_id
        
        if parish_id:
            conditions.append("parish_id = :parish_id")
            params["parish_id"] = parish_id
        
        sql = f"SELECT * FROM terrains WHERE {' AND '.join(conditions)} ORDER BY created_at DESC;"
        
        with self.db.get_connection() as conn:
            result = conn.run(sql, **params)
            
            return [self._row_to_terrain(row) for row in result]
    
    def get_location_stats(self, user_id: int) -> dict:
        """
        Get location statistics for user terrains
        
        Args:
            user_id: User ID
            
        Returns:
            Dictionary with location statistics
        """
        sql = """
        SELECT 
            COUNT(*) as total_terrains,
            COUNT(DISTINCT district_id) as unique_districts,
            COUNT(DISTINCT municipality_id) as unique_municipalities,
            COUNT(DISTINCT parish_id) as unique_parishes,
            SUM(area_hectares) as total_area,
            district_name,
            COUNT(*) as terrains_per_district
        FROM terrains 
        WHERE user_id = :user_id AND district_id IS NOT NULL
        GROUP BY district_id, district_name
        ORDER BY terrains_per_district DESC;
        """
        
        with self.db.get_connection() as conn:
            result = conn.run(sql, user_id=user_id)
            
            if not result:
                return {
                    'total_terrains': 0,
                    'unique_districts': 0,
                    'unique_municipalities': 0,
                    'unique_parishes': 0,
                    'total_area': 0,
                    'districts_breakdown': []
                }
            
            first_row = result[0]
            districts_breakdown = [
                {
                    'district_name': row['district_name'],
                    'terrain_count': row['terrains_per_district']
                }
                for row in result if row['district_name']
            ]
            
            return {
                'total_terrains': first_row['total_terrains'],
                'unique_districts': first_row['unique_districts'],
                'unique_municipalities': first_row['unique_municipalities'],
                'unique_parishes': first_row['unique_parishes'],
                'total_area': float(first_row['total_area']) if first_row['total_area'] else 0,
                'districts_breakdown': districts_breakdown
            }
    
    def update_terrain(self, terrain: Terrain):
        """
        Atualiza terreno na BD - Updated with location fields
        
        Args:
            terrain: Instância de Terrain atualizada
        """
        sql = """
        UPDATE terrains SET 
            name = :name, 
            latitude = :latitude, 
            longitude = :longitude,
            crop_type = :crop_type, 
            area_hectares = :area_hectares, 
            notes = :notes,
            district_id = :district_id,
            district_name = :district_name,
            municipality_id = :municipality_id,
            municipality_name = :municipality_name,
            parish_id = :parish_id,
            parish_name = :parish_name,
            updated_at = CURRENT_TIMESTAMP
        WHERE id = :terrain_id;
        """
        
        with self.db.get_connection() as conn:
            conn.run(
                sql,
                terrain_id=terrain.id,
                name=terrain.name,
                latitude=terrain.latitude,
                longitude=terrain.longitude,
                crop_type=terrain.crop_type,
                area_hectares=terrain.area_hectares,
                notes=terrain.notes,
                district_id=terrain.district_id,
                district_name=terrain.district_name,
                municipality_id=terrain.municipality_id,
                municipality_name=terrain.municipality_name,
                parish_id=terrain.parish_id,
                parish_name=terrain.parish_name
            )
    
    def delete_terrain(self, terrain_id: int, user_id: int):
        """
        Remove terreno da BD
        
        Args:
            terrain_id: ID do terreno
            user_id: ID do utilizador (para segurança)
        """
        sql = "DELETE FROM terrains WHERE id = :terrain_id AND user_id = :user_id;"
        
        with self.db.get_connection() as conn:
            conn.run(sql, terrain_id=terrain_id, user_id=user_id)
    
    def clear_all_terrains(self):
        """Remove todos os terrenos (para testes)"""
        sql = "DELETE FROM terrains;"
        
        with self.db.get_connection() as conn:
            conn.run(sql)
    
    def _row_to_terrain(self, row) -> Terrain:
        """
        Converte linha da BD para objeto Terrain - Updated with location fields
        
        Args:
            row: Linha da base de dados
            
        Returns:
            Instância de Terrain
        """
        terrain = Terrain(
            name=row['name'],
            latitude=float(row['latitude']),
            longitude=float(row['longitude']),
            user_id=row['user_id']
        )
        
        terrain.set_id(row['id'])
        
        if row['crop_type']:
            terrain.set_crop_type(row['crop_type'])
        
        if row['area_hectares']:
            terrain.set_area_hectares(float(row['area_hectares']))
        
        if row['notes']:
            terrain.set_notes(row['notes'])
        
        # Set location info if available
        if all([row.get('district_id'), row.get('municipality_id'), row.get('parish_id')]):
            terrain.set_location_info(
                row['district_id'], row['district_name'],
                row['municipality_id'], row['municipality_name'],
                row['parish_id'], row['parish_name']
            )
        
        # Set timestamps
        if row['created_at']:
            terrain._created_at = row['created_at']
        if row['updated_at']:
            terrain._updated_at = row['updated_at']
        
        return terrain