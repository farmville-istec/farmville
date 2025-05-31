import unittest
from services.user_service import UserService
from models.user import User
import os
import random
import string

def generate_unique_username():
    random_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
    return f"test_user_{random_suffix}"

class TestUserModel(unittest.TestCase):    
    def setUp(self):
        self.user = User("test_user", "test@farmville.com")
    
    def test_user_creation(self):
        self.assertEqual(self.user.username, "test_user")
        self.assertEqual(self.user.email, "test@farmville.com")
        self.assertIsNone(self.user.id)
        self.assertFalse(self.user.is_complete())
    
    def test_user_password_setting(self):
        self.user.set_password("password123")
        
        self.assertIsNotNone(self.user.password_hash)
        self.assertTrue(self.user.verify_password("password123"))
        self.assertFalse(self.user.verify_password("wrong_password"))
        self.assertTrue(self.user.is_complete())
    
    def test_user_password_validation(self):
        with self.assertRaises(ValueError):
            self.user.set_password("123")
    
    def test_user_to_dict(self):
        self.user.set_password("password123")
        self.user.set_id(1)
        
        user_dict = self.user.to_dict()
        
        self.assertEqual(user_dict['id'], 1)
        self.assertEqual(user_dict['username'], "test_user")
        self.assertEqual(user_dict['email'], "test@farmville.com")
        self.assertTrue(user_dict['is_complete'])
    
    def test_user_from_dict(self):
        data = {
            'id': 1,
            'username': 'dict_user',
            'email': 'dict@test.com',
            'password_hash': 'hash123',
            'created_at': '2025-05-31T12:00:00',
            'last_login': None
        }
        
        user = User.from_dict(data)
        
        self.assertEqual(user.id, 1)
        self.assertEqual(user.username, 'dict_user')
        self.assertEqual(user.email, 'dict@test.com')

class TestUserService(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        os.environ['DB_NAME'] = 'farmville_test'
        try:
            cls.user_service = UserService()
            cls.user_service.clear_test_data()
        except Exception as e:
            print(f"Warning: Database not available: {e}")
            raise unittest.SkipTest("Database not available for testing")
    
    def setUp(self):
        self.user_service.clear_test_data()
    
    def tearDown(self):
        self.user_service.clear_test_data()
    
    def test_register_user_success(self):
        username = generate_unique_username()
        result = self.user_service.register_user(username, "password123", "test1@farm.com")
        
        print(f"Registration result: {result}")
        
        self.assertTrue(result["success"])
        self.assertEqual(result["message"], "User registered successfully")
        self.assertIn("user_id", result)
    
    def test_register_user_duplicate_username(self):
        username = generate_unique_username()
        
        self.user_service.register_user(username, "pass123", "dup1@farm.com")
        
        result = self.user_service.register_user(username, "different_pass", "dup2@farm.com")
        
        self.assertFalse(result["success"])
        self.assertEqual(result["message"], "Username already exists")
    
    def test_register_user_invalid_password(self):
        username = generate_unique_username()
        result = self.user_service.register_user(username, "123", "test2@farm.com")
        
        self.assertFalse(result["success"])
        self.assertEqual(result["message"], "Password must be at least 6 characters")
    
    def test_login_user_success(self):
        self.user_service.register_user("login_user", "password123", "login@farm.com")
        
        result = self.user_service.login_user("login_user", "password123")
        
        self.assertTrue(result["success"])
        self.assertEqual(result["message"], "Login successful")
        self.assertIn("token", result)
        self.assertIn("user", result)
        self.assertEqual(result["user"]["username"], "login_user")
    
    def test_login_user_invalid_credentials(self):
        self.user_service.register_user("valid_user", "password123", "valid@farm.com")
        
        result = self.user_service.login_user("valid_user", "wrong_password")
        
        self.assertFalse(result["success"])
        self.assertEqual(result["message"], "Invalid credentials")
    
    def test_token_verification_valid(self):
        self.user_service.register_user("token_user", "password123", "token@farm.com")
        login_result = self.user_service.login_user("token_user", "password123")
        
        self.assertTrue(login_result["success"])
        
        token = login_result["token"]
        user_info = self.user_service.get_user_from_token(token)
        
        self.assertIsNotNone(user_info)
        self.assertEqual(user_info["username"], "token_user")
    
    def test_token_verification_invalid(self):
        invalid_token = "invalid.token.here"
        user_info = self.user_service.get_user_from_token(invalid_token)
        
        self.assertIsNone(user_info)
    
    def test_cache_functionality(self):
        self.user_service.register_user("cache_user", "password123", "cache@farm.com")
        login_result = self.user_service.login_user("cache_user", "password123")
        
        token = login_result["token"]
        
        user1 = self.user_service.get_user_from_token(token)
        
        user2 = self.user_service.get_user_from_token(token)
        
        self.assertEqual(user1["username"], user2["username"])
        
        cache_info = self.user_service.get_cache_info()
        self.assertGreater(cache_info['cached_users'], 0)

if __name__ == '__main__':
    unittest.main()