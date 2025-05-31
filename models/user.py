from datetime import datetime
from typing import Dict, Optional
import hashlib

class User:
    """
    User representation class
    """
    
    def __init__(self, username: str, email: str = None):
        self._id = None
        self._username = username
        self._email = email
        self._password_hash = None
        self._created_at = datetime.now()
        self._last_login = None
        self._is_active = True
    
    @property
    def id(self) -> Optional[int]:
        return self._id
    
    @property
    def username(self) -> str:
        return self._username
    
    @property
    def email(self) -> Optional[str]:
        return self._email
    
    @property
    def password_hash(self) -> Optional[str]:
        return self._password_hash
    
    @property
    def created_at(self) -> datetime:
        return self._created_at
    
    @property
    def last_login(self) -> Optional[datetime]:
        return self._last_login
    
    @property
    def is_active(self) -> bool:
        return self._is_active
    
    def set_id(self, user_id: int):
        self._id = user_id
    
    def set_password(self, password: str):
        if len(password) < 6:
            raise ValueError("Password deve ter pelo menos 6 caracteres")
        
        salt = "farmville_salt"
        self._password_hash = hashlib.sha256((password + salt).encode()).hexdigest()
    
    def verify_password(self, password: str) -> bool:
        if not self._password_hash:
            return False
        
        salt = "farmville_salt"
        password_hash = hashlib.sha256((password + salt).encode()).hexdigest()
        return password_hash == self._password_hash
    
    def set_password_hash(self, password_hash: str):
        self._password_hash = password_hash
    
    def set_last_login(self, last_login: datetime = None):
        self._last_login = last_login or datetime.now()
    
    def set_created_at(self, created_at: datetime):
        self._created_at = created_at
    
    def set_email(self, email: str):
        self._email = email.strip() if email else None
    
    def is_complete(self) -> bool:
        return all([
            self._username,
            self._password_hash,
            self._created_at
        ])
    
    def to_dict(self) -> Dict:
        return {
            'id': self._id,
            'username': self._username,
            'email': self._email,
            'created_at': self._created_at.isoformat() if self._created_at else None,
            'last_login': self._last_login.isoformat() if self._last_login else None,
            'is_active': self._is_active,
            'is_complete': self.is_complete()
        }
    
    def to_dict_safe(self) -> Dict:
        return {
            'id': self._id,
            'username': self._username,
            'email': self._email,
            'last_login': self._last_login.isoformat() if self._last_login else None
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'User':
        user = cls(data['username'], data.get('email'))
        
        if 'id' in data:
            user.set_id(data['id'])
        
        if 'password_hash' in data:
            user.set_password_hash(data['password_hash'])
        
        if 'created_at' in data and data['created_at']:
            if isinstance(data['created_at'], str):
                user.set_created_at(datetime.fromisoformat(data['created_at'].replace('Z', '+00:00')))
            else:
                user.set_created_at(data['created_at'])
        
        if 'last_login' in data and data['last_login']:
            if isinstance(data['last_login'], str):
                user.set_last_login(datetime.fromisoformat(data['last_login'].replace('Z', '+00:00')))
            else:
                user.set_last_login(data['last_login'])
        
        return user
    
    def __str__(self) -> str:
        status = "ativo" if self._is_active else "inativo"
        return f"User {self._username} ({status})"
    
    def __repr__(self) -> str:
        return (f"User(id={self._id}, username='{self._username}', "
               f"email='{self._email}', complete={self.is_complete()})")