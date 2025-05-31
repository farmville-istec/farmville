"""
User Service
"""

from typing import Optional, Dict, Any, List
import jwt
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv
from models.user import User
from database.user_repository import UserRepository

# Load environment variables from .env file
load_dotenv()

class UserService:
    """
    Serviço de gestão de utilizadores
    Segue o padrão dos outros serviços do projeto
    """
    
    def __init__(self):
        self.repository = UserRepository()
        self.secret_key = os.getenv('JWT_SECRET', 'farmville-secret-2025')
        self.token_expiry_hours = 24
        
        # Cache para utilizadores (seguindo padrão do weather_service)
        self._cache = {}
        self._cache_duration = 1800  # 30 minutos em segundos
        
        # Initialize database
        self._init_service()
    
    def _init_service(self):
        """Inicializa o serviço"""
        try:
            self.repository.db.init_tables()
            print("🔐 User Service initialized")
        except Exception as e:
            print(f"❌ User Service init error: {e}")
    
    def _create_token(self, user: User) -> str:
        """
        Cria token JWT para utilizador
        
        Args:
            user: Instância de User
            
        Returns:
            str: Token JWT
        """
        payload = {
            'user_id': user.id,
            'username': user.username,
            'exp': datetime.now() + timedelta(hours=self.token_expiry_hours)
        }
        return jwt.encode(payload, self.secret_key, algorithm='HS256')
    
    def _verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """
        Verifica token JWT
        
        Args:
            token: Token JWT
            
        Returns:
            Payload se válido, None se inválido
        """
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=['HS256'])
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
    
    def _is_cache_valid(self, cache_key: str) -> bool:
        """Verifica se os dados em cache ainda são válidos"""
        if cache_key not in self._cache:
            return False
        
        cached_time = self._cache[cache_key]['timestamp']
        current_time = datetime.now().timestamp()
        
        return (current_time - cached_time) < self._cache_duration
    
    def register_user(self, username: str, password: str, email: str = None) -> Dict[str, Any]:
        """
        Regista novo utilizador
        
        Args:
            username: Nome do utilizador
            password: Password em texto
            email: Email (opcional)
            
        Returns:
            Resultado do registo
        """
        # Validation
        if not username or not password:
            return {"success": False, "message": "Username and password required"}
        
        if len(password) < 6:
            return {"success": False, "message": "Password must be at least 6 characters"}
        
        if self.repository.username_exists(username):
            return {"success": False, "message": "Username already exists"}
        
        try:
            # Create User model
            user = User(username, email)
            user.set_password(password)
            
            # Save to database
            user_id = self.repository.create_user(user)
            
            print(f"✅ User {username} registered successfully")
            
            return {
                "success": True,
                "message": "User registered successfully",
                "user_id": user_id
            }
            
        except ValueError as e:
            return {"success": False, "message": str(e)}
        except Exception as e:
            return {"success": False, "message": f"Erro no registo: {str(e)}"}
    
    def login_user(self, username: str, password: str) -> Dict[str, Any]:
        """
        Autentica utilizador
        
        Args:
            username: Nome do utilizador
            password: Password em texto
            
        Returns:
            Resultado do login com token
        """
        user = self.repository.get_user_by_username(username)
        
        if not user:
            return {"success": False, "message": "Invalid credentials"}
        
        if not user.verify_password(password):
            return {"success": False, "message": "Invalid credentials"}
        
        # Update last login
        self.repository.update_last_login(user)
        
        # Create token
        token = self._create_token(user)
        
        # Cache user info
        cache_key = f"user_{user.id}"
        self._cache[cache_key] = {
            'data': user,
            'timestamp': datetime.now().timestamp()
        }
        
        print(f"✅ User {username} logged in successfully")
        
        return {
            "success": True,
            "message": "Login successful",
            "token": token,
            "user": user.to_dict_safe()
        }
    
    def get_user_from_token(self, token: str) -> Optional[Dict[str, Any]]:
        """
        Obtém informação do utilizador a partir do token
        
        Args:
            token: Token JWT
            
        Returns:
            Informação do utilizador ou None
        """
        payload = self._verify_token(token)
        if not payload:
            return None
        
        user_id = payload.get('user_id')
        cache_key = f"user_{user_id}"
        
        # Check cache first
        if self._is_cache_valid(cache_key):
            user = self._cache[cache_key]['data']
            return user.to_dict_safe()
        
        # Get from database
        user = self.repository.get_user_by_id(user_id)
        if not user:
            return None
        
        # Update cache
        self._cache[cache_key] = {
            'data': user,
            'timestamp': datetime.now().timestamp()
        }
        
        return user.to_dict_safe()
    
    def verify_token(self, token: str) -> bool:
        """
        Verifica se token é válido
        
        Args:
            token: Token JWT
            
        Returns:
            bool: True se válido
        """
        return self._verify_token(token) is not None
    
    def get_all_users(self) -> List[Dict[str, Any]]:
        """
        Obtém todos os utilizadores (admin)
        
        Returns:
            Lista de utilizadores
        """
        users = self.repository.get_all_users()
        return [user.to_dict_safe() for user in users]
    
    def clear_cache(self):
        """Limpa o cache de utilizadores"""
        self._cache.clear()
        print("🗑️ User cache cleared")
    
    def clear_test_data(self):
        """Limpa dados de teste (apenas para testes)"""
        try:
            self.repository.clear_all_users()
            self.clear_cache()
            print("🧹 Test data cleared")
        except Exception as e:
            print(f"Warning: Could not clear test data: {e}")
    
    def get_cache_info(self) -> dict:
        """Retorna informações sobre o cache"""
        return {
            'cached_users': len(self._cache),
            'cache_duration_minutes': self._cache_duration / 60,
            'users': list(self._cache.keys())
        }