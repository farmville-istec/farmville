"""
Tests for Location Service and related components
"""

import unittest
import os
from unittest.mock import Mock, patch
from models.location import Location
from services.location_service import LocationService
from services.mapbox_client import MapboxClient

class TestLocationModel(unittest.TestCase):
    """Test the Location model"""
    
    def setUp(self):
        self.location = Location("Test Farm", 41.1579, -8.6291)
    
    def test_location_creation(self):
        """Test basic location creation"""
        self.assertEqual(self.location.name, "Test Farm")
        self.assertEqual(self.location.latitude, 41.1579)
        self.assertEqual(self.location.longitude, -8.6291)
        self.assertEqual(self.location.location_type, "point")
        self.assertTrue(self.location.is_complete())
    
    def test_coordinate_validation(self):
        """Test coordinate validation"""
        # Valid coordinates
        valid_location = Location("Valid", 45.0, 90.0)
        self.assertTrue(valid_location._validate_coordinates())
        
        # Invalid coordinates should still create object but fail validation
        invalid_location = Location("Invalid", 95.0, 200.0)
        self.assertFalse(invalid_location._validate_coordinates())
    
    def test_location_with_address(self):
        """Test location with address"""
        self.location.set_address("123 Test Street, Porto, Portugal")
        self.assertEqual(self.location.address, "123 Test Street, Porto, Portugal")
        self.assertEqual(self.location.location_type, "address")
    
    def test_location_with_area(self):
        """Test location with terrain area"""
        geojson_polygon = {
            "type": "Polygon",
            "coordinates": [[
                [-8.6291, 41.1579],
                [-8.6300, 41.1579],
                [-8.6300, 41.1590],
                [-8.6291, 41.1590],
                [-8.6291, 41.1579]
            ]]
        }
        
        self.location.set_terrain_area(geojson_polygon)
        self.assertEqual(self.location.location_type, "area")
        self.assertIsNotNone(self.location.terrain_area)
        self.assertIsNotNone(self.location.get_area_size())
    
    def test_invalid_geojson(self):
        """Test invalid GeoJSON handling"""
        invalid_geojson = {"type": "InvalidType"}
        
        with self.assertRaises(ValueError):
            self.location.set_terrain_area(invalid_geojson)
    
    def test_location_serialization(self):
        """Test location to_dict and from_dict"""
        self.location.set_id(1)
        self.location.set_user_id(100)
        self.location.set_address("Test Address")
        
        location_dict = self.location.to_dict()
        
        self.assertEqual(location_dict['id'], 1)
        self.assertEqual(location_dict['name'], "Test Farm")
        self.assertEqual(location_dict['user_id'], 100)
        
        # Test reconstruction from dict
        new_location = Location.from_dict(location_dict)
        self.assertEqual(new_location.name, self.location.name)
        self.assertEqual(new_location.latitude, self.location.latitude)

class TestMapboxClient(unittest.TestCase):
    """Test Mapbox client functionality"""
    
    def setUp(self):
        # Mock the Mapbox client to avoid real API calls
        self.mock_token = "fake_mapbox_token"
    
    def test_coordinate_validation(self):
        """Test coordinate validation method"""
        with patch.dict(os.environ, {'MAPBOX_ACCESS_TOKEN': self.mock_token}):
            client = MapboxClient()
            
            # Valid coordinates
            self.assertTrue(client.validate_coordinates(41.1579, -8.6291))
            self.assertTrue(client.validate_coordinates(0, 0))
            self.assertTrue(client.validate_coordinates(-90, -180))
            self.assertTrue(client.validate_coordinates(90, 180))
            
            # Invalid coordinates
            self.assertFalse(client.validate_coordinates(91, 0))
            self.assertFalse(client.validate_coordinates(0, 181))
            self.assertFalse(client.validate_coordinates(-91, 0))
            self.assertFalse(client.validate_coordinates(0, -181))
    
    def test_distance_calculation(self):
        """Test distance calculation using Haversine formula"""
        with patch.dict(os.environ, {'MAPBOX_ACCESS_TOKEN': self.mock_token}):
            client = MapboxClient()
            
            # Distance between Porto and Lisboa (approximately 274 km)
            porto_lat, porto_lng = 41.1579, -8.6291
            lisboa_lat, lisboa_lng = 38.7223, -9.1393
            
            distance = client.calculate_distance(porto_lat, porto_lng, lisboa_lat, lisboa_lng)
            
            # Should be approximately 274 km (allow 10% margin)
            self.assertGreater(distance, 250)
            self.assertLess(distance, 300)
    
    @patch('requests.Session.get')
    def test_geocoding_success(self, mock_get):
        """Test successful geocoding"""
        # Mock successful response
        mock_response = Mock()
        mock_response.json.return_value = {
            'features': [{
                'geometry': {'coordinates': [-8.6291, 41.1579]},
                'place_name': 'Porto, Portugal',
                'text': 'Porto',
                'place_type': ['place'],
                'context': []
            }]
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        with patch.dict(os.environ, {'MAPBOX_ACCESS_TOKEN': self.mock_token}):
            client = MapboxClient()
            result = client.geocode_address("Porto, Portugal")
            
            self.assertIsNotNone(result)
            self.assertEqual(result['name'], 'Porto, Portugal')
            self.assertEqual(result['latitude'], 41.1579)
            self.assertEqual(result['longitude'], -8.6291)
    
    @patch('requests.Session.get')
    def test_geocoding_not_found(self, mock_get):
        """Test geocoding when address not found"""
        # Mock empty response
        mock_response = Mock()
        mock_response.json.return_value = {'features': []}
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        with patch.dict(os.environ, {'MAPBOX_ACCESS_TOKEN': self.mock_token}):
            client = MapboxClient()
            result = client.geocode_address("NonExistentPlace12345")
            
            self.assertIsNone(result)

class TestLocationService(unittest.TestCase):
    """Test Location Service functionality"""
    
    @classmethod
    def setUpClass(cls):
        """Set up test environment"""
        os.environ['POSTGRES_HOST'] = 'localhost'
        os.environ['POSTGRES_PORT'] = '5432'
        os.environ['POSTGRES_USER'] = 'farmville'
        os.environ['POSTGRES_PASSWORD'] = 'farmville'
        os.environ['POSTGRES_DB'] = 'farmville_test'
        os.environ['MAPBOX_ACCESS_TOKEN'] = 'fake_token_for_testing'
        
        try:
            cls.location_service = LocationService()
            cls.location_service.clear_test_data()
        except Exception as e:
            print(f"Warning: Database not available: {e}")
            raise unittest.SkipTest("Database not available for testing")
    
    def setUp(self):
        """Clean data before each test"""
        self.location_service.clear_test_data()
    
    def tearDown(self):
        """Clean data after each test"""
        self.location_service.clear_test_data()
    
    def test_create_location_from_coordinates(self):
        """Test creating location from coordinates"""
        result = self.location_service.create_location_from_coordinates(
            latitude=41.1579,
            longitude=-8.6291,
            name="Test Farm",
            user_id=1
        )
        
        self.assertTrue(result['success'])
        self.assertIn('location_id', result)
        self.assertEqual(result['location']['name'], "Test Farm")
    
    def test_invalid_coordinates(self):
        """Test handling of invalid coordinates"""
        result = self.location_service.create_location_from_coordinates(
            latitude=95.0,  # Invalid latitude
            longitude=-8.6291,
            name="Invalid Location",
            user_id=1
        )
        
        self.assertFalse(result['success'])
        self.assertIn("Invalid coordinates", result['message'])
    
    @patch.object(MapboxClient, 'geocode_address')
    def test_create_location_from_address(self, mock_geocode):
        """Test creating location from address"""
        # Mock geocoding response
        mock_geocode.return_value = {
            'name': 'Porto, Portugal',
            'latitude': 41.1579,
            'longitude': -8.6291,
            'address': 'Porto, Portugal',
            'confidence': 1.0
        }
        
        result = self.location_service.create_location_from_address(
            address="Porto, Portugal",
            name="Porto Location",
            user_id=1
        )
        
        self.assertTrue(result['success'])
        self.assertEqual(result['location']['name'], "Porto Location")
        mock_geocode.assert_called_once()
    
    @patch.object(MapboxClient, 'geocode_address')
    def test_address_not_found(self, mock_geocode):
        """Test handling of address not found"""
        mock_geocode.return_value = None
        
        result = self.location_service.create_location_from_address(
            address="NonExistentPlace12345",
            user_id=1
        )
        
        self.assertFalse(result['success'])
        self.assertIn("Address not found", result['message'])
    
    def test_create_location_from_area(self):
        """Test creating location from drawn area"""
        geojson_polygon = {
            "type": "Polygon",
            "coordinates": [[
                [-8.6291, 41.1579],
                [-8.6300, 41.1579],
                [-8.6300, 41.1590],
                [-8.6291, 41.1590],
                [-8.6291, 41.1579]
            ]]
        }
        
        result = self.location_service.create_location_from_area(
            geojson_polygon=geojson_polygon,
            name="Test Area",
            user_id=1
        )
        
        self.assertTrue(result['success'])
        self.assertEqual(result['location']['name'], "Test Area")
        self.assertEqual(result['location']['location_type'], "area")
        self.assertIsNotNone(result['area_size_sqm'])
    
    def test_get_user_locations(self):
        """Test getting all locations for a user"""
        # Create test locations
        self.location_service.create_location_from_coordinates(
            41.1579, -8.6291, "Location 1", user_id=1
        )
        self.location_service.create_location_from_coordinates(
            38.7223, -9.1393, "Location 2", user_id=1
        )
        
        result = self.location_service.get_user_locations(user_id=1)
        
        self.assertTrue(result['success'])
        self.assertEqual(result['count'], 2)
        self.assertEqual(len(result['locations']), 2)
    
    def test_update_location(self):
        """Test updating location"""
        # Create location first
        create_result = self.location_service.create_location_from_coordinates(
            41.1579, -8.6291, "Original Name", user_id=1
        )
        location_id = create_result['location_id']
        
        # Update location
        updates = {
            'name': 'Updated Name',
            'latitude': 41.1600,
            'longitude': -8.6300
        }
        
        result = self.location_service.update_location(
            location_id=location_id,
            updates=updates,
            user_id=1
        )
        
        self.assertTrue(result['success'])
        self.assertEqual(result['location']['name'], 'Updated Name')
    
    def test_delete_location(self):
        """Test deleting location"""
        # Create location first
        create_result = self.location_service.create_location_from_coordinates(
            41.1579, -8.6291, "To Delete", user_id=1
        )
        location_id = create_result['location_id']
        
        # Delete location
        result = self.location_service.delete_location(
            location_id=location_id,
            user_id=1
        )
        
        self.assertTrue(result['success'])
        
        # Verify location is no longer accessible
        get_result = self.location_service.get_location_with_weather(
            location_id=location_id,
            user_id=1
        )
        self.assertFalse(get_result['success'])
    
    def test_user_isolation(self):
        """Test that users can only access their own locations"""
        # Create location for user 1
        create_result = self.location_service.create_location_from_coordinates(
            41.1579, -8.6291, "User 1 Location", user_id=1
        )
        location_id = create_result['location_id']
        
        # Try to access with user 2
        result = self.location_service.get_location_with_weather(
            location_id=location_id,
            user_id=2
        )
        
        self.assertFalse(result['success'])
        self.assertIn("Access denied", result['message'])
    
    def test_cache_functionality(self):
        """Test caching mechanism"""
        # This test verifies that cache methods work without errors
        cache_info = self.location_service.get_cache_info()
        self.assertIsInstance(cache_info, dict)
        self.assertIn('cached_items', cache_info)
        
        # Clear cache should not raise errors
        self.location_service.clear_cache()

if __name__ == '__main__':
    unittest.main()