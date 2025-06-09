import unittest
import os
import random
import string
from models.terrain import Terrain
from services.terrain_service import TerrainService

def generate_unique_terrain_name():
    """Gera nome único para terreno de teste"""
    random_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
    return f"test_terrain_{random_suffix}"

class TestTerrainModel(unittest.TestCase):
    """Testes unitários para o modelo Terrain"""
    
    def setUp(self):
        """Configuração antes de cada teste"""
        self.terrain = Terrain("Test Farm", 41.1579, -8.6291, 1)
    
    def test_terrain_creation(self):
        """Teste: criação de terreno"""
        self.assertEqual(self.terrain.name, "Test Farm")
        self.assertEqual(self.terrain.latitude, 41.1579)
        self.assertEqual(self.terrain.longitude, -8.6291)
        self.assertEqual(self.terrain.user_id, 1)
        self.assertIsNone(self.terrain.id)
        self.assertIsNone(self.terrain.crop_type)
        self.assertIsNone(self.terrain.area_hectares)
        self.assertIsNone(self.terrain.notes)
    
    def test_terrain_set_crop_type(self):
        """Teste: definir tipo de cultura"""
        self.terrain.set_crop_type("Wheat")
        self.assertEqual(self.terrain.crop_type, "Wheat")
        
        # Teste com espaços
        self.terrain.set_crop_type("  Corn  ")
        self.assertEqual(self.terrain.crop_type, "Corn")
        
        # Teste com None
        self.terrain.set_crop_type(None)
        self.assertIsNone(self.terrain.crop_type)
    
    def test_terrain_set_area_hectares(self):
        """Teste: definir área em hectares"""
        self.terrain.set_area_hectares(10.5)
        self.assertEqual(self.terrain.area_hectares, 10.5)
        
        # Teste com área inválida
        with self.assertRaises(ValueError):
            self.terrain.set_area_hectares(-5)
    
    def test_terrain_set_notes(self):
        """Teste: definir notas"""
        self.terrain.set_notes("This is a test note")
        self.assertEqual(self.terrain.notes, "This is a test note")
        
        # Teste com espaços
        self.terrain.set_notes("  Note with spaces  ")
        self.assertEqual(self.terrain.notes, "Note with spaces")
    
    def test_update_coordinates(self):
        """Teste: atualizar coordenadas"""
        old_updated_at = self.terrain.updated_at
        
        self.terrain.update_coordinates(40.0, -9.0)
        
        self.assertEqual(self.terrain.latitude, 40.0)
        self.assertEqual(self.terrain.longitude, -9.0)
        self.assertGreater(self.terrain.updated_at, old_updated_at)
    
    def test_update_coordinates_invalid(self):
        """Teste: coordenadas inválidas"""
        with self.assertRaises(ValueError):
            self.terrain.update_coordinates(91, 0)  # Latitude inválida
        
        with self.assertRaises(ValueError):
            self.terrain.update_coordinates(0, 181)  # Longitude inválida
    
    def test_update_name(self):
        """Teste: atualizar nome"""
        old_updated_at = self.terrain.updated_at
        
        self.terrain.update_name("New Farm Name")
        
        self.assertEqual(self.terrain.name, "New Farm Name")
        self.assertGreater(self.terrain.updated_at, old_updated_at)
    
    def test_update_name_invalid(self):
        """Teste: nome inválido"""
        with self.assertRaises(ValueError):
            self.terrain.update_name("")
        
        with self.assertRaises(ValueError):
            self.terrain.update_name("   ")
    
    def test_to_dict(self):
        """Teste: conversão para dicionário"""
        self.terrain.set_id(123)
        self.terrain.set_crop_type("Vegetables")
        self.terrain.set_area_hectares(15.0)
        self.terrain.set_notes("Test notes")
        
        terrain_dict = self.terrain.to_dict()
        
        self.assertEqual(terrain_dict['id'], 123)
        self.assertEqual(terrain_dict['user_id'], 1)
        self.assertEqual(terrain_dict['name'], "Test Farm")
        self.assertEqual(terrain_dict['latitude'], 41.1579)
        self.assertEqual(terrain_dict['longitude'], -8.6291)
        self.assertEqual(terrain_dict['crop_type'], "Vegetables")
        self.assertEqual(terrain_dict['area_hectares'], 15.0)
        self.assertEqual(terrain_dict['notes'], "Test notes")
        self.assertIsNotNone(terrain_dict['created_at'])
        self.assertIsNotNone(terrain_dict['updated_at'])
    
    def test_from_dict(self):
        """Teste: criação a partir de dicionário"""
        data = {
            'id': 456,
            'user_id': 2,
            'name': 'Dict Farm',
            'latitude': 38.7223,
            'longitude': -9.1393,
            'crop_type': 'Rice',
            'area_hectares': 20.5,
            'notes': 'From dict',
            'created_at': '2025-01-01T12:00:00',
            'updated_at': '2025-01-02T12:00:00'
        }
        
        terrain = Terrain.from_dict(data)
        
        self.assertEqual(terrain.id, 456)
        self.assertEqual(terrain.user_id, 2)
        self.assertEqual(terrain.name, 'Dict Farm')
        self.assertEqual(terrain.latitude, 38.7223)
        self.assertEqual(terrain.longitude, -9.1393)
        self.assertEqual(terrain.crop_type, 'Rice')
        self.assertEqual(terrain.area_hectares, 20.5)
        self.assertEqual(terrain.notes, 'From dict')
    
    def test_string_representations(self):
        """Teste: representações em string"""
        self.terrain.set_id(789)
        self.terrain.set_crop_type("Corn")
        
        str_repr = str(self.terrain)
        self.assertIn("Test Farm", str_repr)
        self.assertIn("41.1579", str_repr)
        self.assertIn("-8.6291", str_repr)
        
        repr_str = repr(self.terrain)
        self.assertIn("789", repr_str)
        self.assertIn("Test Farm", repr_str)
        self.assertIn("Corn", repr_str)


class TestTerrainService(unittest.TestCase):
    """Testes unitários para o TerrainService"""
    
    @classmethod
    def setUpClass(cls):
        """Configuração da classe"""
        os.environ['DB_NAME'] = 'farmville_test'
        try:
            cls.terrain_service = TerrainService()
            cls.terrain_service.repository.clear_all_terrains()
        except Exception as e:
            print(f"Warning: Database not available: {e}")
            raise unittest.SkipTest("Database not available for testing")
    
    def setUp(self):
        """Configuração antes de cada teste"""
        self.terrain_service.repository.clear_all_terrains()
        self.test_user_id = 999  # ID de utilizador para testes
    
    def tearDown(self):
        """Limpeza após cada teste"""
        self.terrain_service.repository.clear_all_terrains()
    
    def test_create_terrain_success(self):
        """Teste: criar terreno com sucesso"""
        terrain_name = generate_unique_terrain_name()
        
        result = self.terrain_service.create_terrain(
            user_id=self.test_user_id,
            name=terrain_name,
            latitude=41.1579,
            longitude=-8.6291,
            crop_type="Wheat",
            area_hectares=10.0,
            notes="Test terrain"
        )
        
        self.assertTrue(result["success"])
        self.assertEqual(result["message"], "Terreno criado com sucesso")
        self.assertIn("terrain_id", result)
        self.assertIn("terrain", result)
        
        # Verificar dados do terreno criado
        terrain_data = result["terrain"]
        self.assertEqual(terrain_data["name"], terrain_name)
        self.assertEqual(terrain_data["user_id"], self.test_user_id)
        self.assertEqual(terrain_data["crop_type"], "Wheat")
        self.assertEqual(terrain_data["area_hectares"], 10.0)
    
    def test_create_terrain_invalid_name(self):
        """Teste: criar terreno com nome inválido"""
        result = self.terrain_service.create_terrain(
            user_id=self.test_user_id,
            name="",
            latitude=41.1579,
            longitude=-8.6291
        )
        
        self.assertFalse(result["success"])
        self.assertEqual(result["message"], "Nome do terreno é obrigatório")
    
    def test_create_terrain_invalid_coordinates(self):
        """Teste: criar terreno com coordenadas inválidas"""
        # Latitude inválida
        result = self.terrain_service.create_terrain(
            user_id=self.test_user_id,
            name="Test Farm",
            latitude=91,
            longitude=-8.6291
        )
        
        self.assertFalse(result["success"])
        self.assertIn("Latitude", result["message"])
        
        # Longitude inválida
        result = self.terrain_service.create_terrain(
            user_id=self.test_user_id,
            name="Test Farm",
            latitude=41.1579,
            longitude=181
        )
        
        self.assertFalse(result["success"])
        self.assertIn("Longitude", result["message"])
    
    def test_create_terrain_invalid_area(self):
        """Teste: criar terreno com área inválida"""
        result = self.terrain_service.create_terrain(
            user_id=self.test_user_id,
            name="Test Farm",
            latitude=41.1579,
            longitude=-8.6291,
            area_hectares=-5.0
        )
        
        self.assertFalse(result["success"])
        self.assertIn("Área", result["message"])
    
    def test_get_user_terrains(self):
        """Teste: obter terrenos do utilizador"""
        # Criar alguns terrenos
        terrain1_name = generate_unique_terrain_name()
        terrain2_name = generate_unique_terrain_name()
        
        self.terrain_service.create_terrain(self.test_user_id, terrain1_name, 41.0, -8.0)
        self.terrain_service.create_terrain(self.test_user_id, terrain2_name, 42.0, -9.0)
        
        # Obter terrenos
        result = self.terrain_service.get_user_terrains(self.test_user_id)
        
        self.assertTrue(result["success"])
        self.assertEqual(result["count"], 2)
        self.assertEqual(len(result["terrains"]), 2)
        
        # Verificar nomes dos terrenos
        terrain_names = [t["name"] for t in result["terrains"]]
        self.assertIn(terrain1_name, terrain_names)
        self.assertIn(terrain2_name, terrain_names)
    
    def test_get_terrain_success(self):
        """Teste: obter terreno específico"""
        terrain_name = generate_unique_terrain_name()
        
        # Criar terreno
        create_result = self.terrain_service.create_terrain(
            self.test_user_id, terrain_name, 41.1579, -8.6291
        )
        terrain_id = create_result["terrain_id"]
        
        # Obter terreno
        result = self.terrain_service.get_terrain(terrain_id, self.test_user_id)
        
        self.assertTrue(result["success"])
        self.assertIn("terrain", result)
        self.assertEqual(result["terrain"]["name"], terrain_name)
        self.assertEqual(result["terrain"]["user_id"], self.test_user_id)
    
    def test_get_terrain_not_found(self):
        """Teste: obter terreno inexistente"""
        result = self.terrain_service.get_terrain(99999, self.test_user_id)
        
        self.assertFalse(result["success"])
        self.assertEqual(result["message"], "Terreno não encontrado")
    
    def test_get_terrain_access_denied(self):
        """Teste: acesso negado a terreno de outro utilizador"""
        terrain_name = generate_unique_terrain_name()
        
        # Criar terreno para utilizador 1
        create_result = self.terrain_service.create_terrain(
            self.test_user_id, terrain_name, 41.1579, -8.6291
        )
        terrain_id = create_result["terrain_id"]
        
        # Tentar aceder com utilizador 2
        result = self.terrain_service.get_terrain(terrain_id, self.test_user_id + 1)
        
        self.assertFalse(result["success"])
        self.assertEqual(result["message"], "Acesso negado")
    
    def test_update_terrain_success(self):
        """Teste: atualizar terreno com sucesso"""
        terrain_name = generate_unique_terrain_name()
        new_name = f"{terrain_name}_updated"
        
        # Criar terreno
        create_result = self.terrain_service.create_terrain(
            self.test_user_id, terrain_name, 41.1579, -8.6291
        )
        terrain_id = create_result["terrain_id"]
        
        # Atualizar terreno
        result = self.terrain_service.update_terrain(
            terrain_id, self.test_user_id,
            name=new_name,
            crop_type="Rice",
            area_hectares=15.0
        )
        
        self.assertTrue(result["success"])
        self.assertEqual(result["message"], "Terreno atualizado com sucesso")
        
        # Verificar dados atualizados
        terrain_data = result["terrain"]
        self.assertEqual(terrain_data["name"], new_name)
        self.assertEqual(terrain_data["crop_type"], "Rice")
        self.assertEqual(terrain_data["area_hectares"], 15.0)
    
    def test_delete_terrain_success(self):
        """Teste: remover terreno com sucesso"""
        terrain_name = generate_unique_terrain_name()
        
        # Criar terreno
        create_result = self.terrain_service.create_terrain(
            self.test_user_id, terrain_name, 41.1579, -8.6291
        )
        terrain_id = create_result["terrain_id"]
        
        # Remover terreno
        result = self.terrain_service.delete_terrain(terrain_id, self.test_user_id)
        
        self.assertTrue(result["success"])
        self.assertEqual(result["message"], "Terreno removido com sucesso")
        
        # Verificar que terreno foi removido
        get_result = self.terrain_service.get_terrain(terrain_id, self.test_user_id)
        self.assertFalse(get_result["success"])
    
    def test_get_terrain_stats(self):
        """Teste: obter estatísticas dos terrenos"""
        # Criar terrenos com diferentes culturas e áreas
        self.terrain_service.create_terrain(
            self.test_user_id, "Farm 1", 41.0, -8.0, "Wheat", 10.0
        )
        self.terrain_service.create_terrain(
            self.test_user_id, "Farm 2", 42.0, -9.0, "Corn", 15.0
        )
        self.terrain_service.create_terrain(
            self.test_user_id, "Farm 3", 43.0, -10.0, "Wheat", 20.0
        )
        
        # Obter estatísticas
        result = self.terrain_service.get_terrain_stats(self.test_user_id)
        
        self.assertTrue(result["success"])
        
        stats = result["stats"]
        self.assertEqual(stats["total_terrains"], 3)
        self.assertEqual(stats["total_area_hectares"], 45.0)
        self.assertEqual(stats["avg_area"], 15.0)
        self.assertEqual(len(stats["crop_types"]), 2)  # Wheat e Corn
        self.assertIn("Wheat", stats["crop_types"])
        self.assertIn("Corn", stats["crop_types"])


if __name__ == '__main__':
    unittest.main()