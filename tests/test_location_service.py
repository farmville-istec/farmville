import unittest
from unittest.mock import patch, Mock
from services.location_service import LocationService
from services.terrain_service import TerrainService
from models.location import Location, LocationHierarchy
from models.terrain import Terrain


class TestLocationService(unittest.TestCase):
    """Unit tests for LocationService"""
    
    def setUp(self):
        """Setup before each test"""
        self.location_service = LocationService()
    
    def tearDown(self):
        """Cleanup after each test"""
        self.location_service.clear_cache()
    
    @patch('services.location_service.requests.get')
    def test_get_districts(self, mock_get):
        """Test: get all districts"""
        mock_response = Mock()
        mock_response.json.return_value = [
            {"id": 1, "nome": "Aveiro"},
            {"id": 2, "nome": "Beja"}
        ]
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        districts = self.location_service.get_districts()
        
        self.assertIsNotNone(districts)
        self.assertEqual(len(districts), 2)
        self.assertEqual(districts[0]['nome'], "Aveiro")
        self.assertEqual(districts[1]['nome'], "Beja")
    
    @patch('services.location_service.requests.get')
    def test_get_location_hierarchy(self, mock_get):
        """Test: get complete location hierarchy"""
        mock_response = Mock()
        mock_response.json.return_value = [
            {
                "id": 1,
                "nome": "Águeda",
                "latitude": 40.5649,
                "longitude": -8.4459,
                "municipio": {"id": 1, "nome": "Águeda"},
                "distrito": {"id": 1, "nome": "Aveiro"}
            }
        ]
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        hierarchy = self.location_service.get_location_hierarchy(1)
        
        self.assertIsNotNone(hierarchy)
        self.assertEqual(hierarchy['parish']['nome'], "Águeda")
        self.assertEqual(hierarchy['municipality']['nome'], "Águeda")
        self.assertEqual(hierarchy['district']['nome'], "Aveiro")
        self.assertEqual(hierarchy['coordinates']['latitude'], 40.5649)
    
    def test_cache_functionality(self):
        """Test: cache functionality"""
        with patch('services.location_service.requests.get') as mock_get:
            mock_response = Mock()
            mock_response.json.return_value = [{"id": 1, "nome": "Aveiro"}]
            mock_response.raise_for_status.return_value = None
            mock_get.return_value = mock_response
            
            districts1 = self.location_service.get_districts()
            districts2 = self.location_service.get_districts()
            
            # Should only call API once due to caching
            self.assertEqual(mock_get.call_count, 1)
            self.assertEqual(districts1, districts2)


class TestLocationModel(unittest.TestCase):
    """Unit tests for Location model"""
    
    def test_location_creation(self):
        """Test: create location instance"""
        location = Location(
            parish_id=1,
            parish_name="Águeda",
            municipality_id=1,
            municipality_name="Águeda",
            district_id=1,
            district_name="Aveiro"
        )
        
        self.assertEqual(location.parish_name, "Águeda")
        self.assertEqual(location.municipality_name, "Águeda")
        self.assertEqual(location.district_name, "Aveiro")
        self.assertTrue(location.is_complete())
        self.assertFalse(location.has_coordinates())
    
    def test_location_coordinates(self):
        """Test: location coordinates validation"""
        location = Location(1, "Test", 1, "Test", 1, "Test")
        
        # Valid coordinates
        location.set_coordinates(40.5649, -8.4459)
        self.assertTrue(location.has_coordinates())
        self.assertEqual(location.latitude, 40.5649)
        self.assertEqual(location.longitude, -8.4459)
        
        # Invalid coordinates
        with self.assertRaises(ValueError):
            location.set_coordinates(91.0, 0.0)  # Invalid latitude
        
        with self.assertRaises(ValueError):
            location.set_coordinates(0.0, 181.0)  # Invalid longitude
    
    def test_location_names(self):
        """Test: location name methods"""
        location = Location(
            parish_id=1,
            parish_name="Águeda",
            municipality_id=1,
            municipality_name="Águeda",
            district_id=1,
            district_name="Aveiro"
        )
        
        full_name = location.get_full_name()
        short_name = location.get_short_name()
        
        self.assertEqual(full_name, "Águeda, Águeda, Aveiro")
        self.assertEqual(short_name, "Águeda, Águeda")


class TestLocationHierarchy(unittest.TestCase):
    """Unit tests for LocationHierarchy helper"""
    
    def test_hierarchy_flow(self):
        """Test: complete hierarchy selection flow"""
        hierarchy = LocationHierarchy()
        
        # Initial state
        self.assertFalse(hierarchy.is_complete())
        
        # Set district
        district = {"id": 1, "nome": "Aveiro"}
        municipalities = [{"id": 1, "nome": "Águeda"}]
        hierarchy.set_district(district, municipalities)
        
        self.assertEqual(hierarchy.selected_district, district)
        self.assertEqual(len(hierarchy.available_municipalities), 1)
        self.assertFalse(hierarchy.is_complete())
        
        # Set municipality
        municipality = {"id": 1, "nome": "Águeda"}
        parishes = [{"id": 1, "nome": "Águeda"}]
        hierarchy.set_municipality(municipality, parishes)
        
        self.assertEqual(hierarchy.selected_municipality, municipality)
        self.assertEqual(len(hierarchy.available_parishes), 1)
        self.assertFalse(hierarchy.is_complete())
        
        # Set parish
        parish = {"id": 1, "nome": "Águeda"}
        hierarchy.set_parish(parish)
        
        self.assertEqual(hierarchy.selected_parish, parish)
        self.assertTrue(hierarchy.is_complete())
        
        # Get location
        location = hierarchy.get_location()
        self.assertIsNotNone(location)
        self.assertEqual(location.parish_name, "Águeda")


class TestUpdatedTerrainModel(unittest.TestCase):
    """Unit tests for updated Terrain model with location fields"""
    
    def test_terrain_with_location(self):
        """Test: terrain with location information"""
        terrain = Terrain("Test Farm", 40.5649, -8.4459, 1)
        
        # Initially no location info
        self.assertFalse(terrain.has_location_info())
        self.assertIsNone(terrain.get_location_name())
        
        # Set location info
        terrain.set_location_info(
            district_id=1, district_name="Aveiro",
            municipality_id=1, municipality_name="Águeda",
            parish_id=1, parish_name="Águeda"
        )
        
        self.assertTrue(terrain.has_location_info())
        self.assertEqual(terrain.get_location_name(), "Águeda, Águeda, Aveiro")
        self.assertEqual(terrain.get_short_location_name(), "Águeda, Águeda")
        
        # Test to_dict includes location data
        terrain_dict = terrain.to_dict()
        self.assertIsNotNone(terrain_dict['district'])
        self.assertIsNotNone(terrain_dict['municipality'])
        self.assertIsNotNone(terrain_dict['parish'])
        self.assertEqual(terrain_dict['location_name'], "Águeda, Águeda, Aveiro")
    
    def test_terrain_from_location_object(self):
        """Test: set terrain location from Location object"""
        terrain = Terrain("Test Farm", 40.5649, -8.4459, 1)
        
        location = Location(
            parish_id=1, parish_name="Águeda",
            municipality_id=1, municipality_name="Águeda", 
            district_id=1, district_name="Aveiro"
        )
        
        terrain.set_location_from_location_object(location)
        
        self.assertTrue(terrain.has_location_info())
        self.assertEqual(terrain.district_name, "Aveiro")
        self.assertEqual(terrain.municipality_name, "Águeda")
        self.assertEqual(terrain.parish_name, "Águeda")


class TestTerrainLocationIntegration(unittest.TestCase):
    """Integration tests for terrain and location services"""
    
    def setUp(self):
        """Setup services for integration testing"""
        self.location_service = LocationService()
        self.terrain_service = TerrainService(location_service=self.location_service)
    
    @patch('services.location_service.requests.get')
    def test_create_terrain_with_location(self, mock_get):
        """Test: create terrain using parish ID"""
        # Mock location API response
        mock_response = Mock()
        mock_response.json.return_value = [
            {
                "id": 1,
                "nome": "Águeda",
                "latitude": 40.5649,
                "longitude": -8.4459,
                "municipio": {"id": 1, "nome": "Águeda"},
                "distrito": {"id": 1, "nome": "Aveiro"}
            }
        ]
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        # Mock repository to avoid database calls in tests
        with patch.object(self.terrain_service.repository, 'create_terrain') as mock_create:
            mock_create.return_value = 1
            
            result = self.terrain_service.create_terrain_with_location(
                user_id=1,
                name="Test Farm",
                parish_id=1,
                crop_type="Wheat",
                area_hectares=10.0
            )
            
            self.assertTrue(result['success'])
            self.assertIn('terrain', result)
            
            # Verify terrain has location info
            terrain_data = result['terrain']
            self.assertIsNotNone(terrain_data['district'])
            self.assertIsNotNone(terrain_data['municipality']) 
            self.assertIsNotNone(terrain_data['parish'])
            self.assertEqual(terrain_data['location_name'], "Águeda, Águeda, Aveiro")


if __name__ == '__main__':
    unittest.main()