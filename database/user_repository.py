"""
User Repository
"""

from typing import Optional, List
from models.user import User
from .connection import DatabaseConnection

class UserRepository:
    """Repository para gestão de dados de utilizadores"""
    
    def __init__(self):
        self.db = DatabaseConnection()
    
    def create_user(self, user: User) -> int:
        """
        Cria novo utilizador na BD
        
        Args:
            user: Instância de User
            
        Returns:
            int: ID do utilizador criado
        """
        sql = """
        INSERT INTO users (username, email, password_hash)
        VALUES (:username, :email, :password_hash)
        RETURNING id;
        """
        
        with self.db.get_connection() as conn:
            result = conn.run(
                sql, 
                username=user.username,
                email=user.email,
                password_hash=user.password_hash
            )
            user_id = result[0][0]
            user.set_id(user_id)
            return user_id
    
    def get_user_by_username(self, username: str) -> Optional[User]:
        """
        Obtém utilizador pelo username
        
        Args:
            username: Nome do utilizador
            
        Returns:
            User ou None se não encontrado
        """
        sql = "SELECT * FROM users WHERE username = :username;"
        
        with self.db.get_connection() as conn:
            result = conn.run(sql, username=username)
            
            if not result:
                return None
            
            return self._row_to_user(result[0])
    
    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """
        Obtém utilizador pelo ID
        
        Args:
            user_id: ID do utilizador
            
        Returns:
            User ou None se não encontrado
        """
        sql = "SELECT * FROM users WHERE id = :user_id;"
        
        with self.db.get_connection() as conn:
            result = conn.run(sql, user_id=user_id)
            
            if not result:
                return None
            
            return self._row_to_user(result[0])
    
    def update_last_login(self, user: User):
        """
        Atualiza último login do utilizador
        
        Args:
            user: Instância de User
        """
        sql = "UPDATE users SET last_login = NOW() WHERE id = :user_id;"
        
        with self.db.get_connection() as conn:
            conn.run(sql, user_id=user.id)
        
        # Update local object
        user.set_last_login()
    
    def username_exists(self, username: str) -> bool:
        """
        Verifica se username já existe
        
        Args:
            username: Nome do utilizador
            
        Returns:
            bool: True se existe, False caso contrário
        """
        sql = "SELECT 1 FROM users WHERE username = :username;"
        
        with self.db.get_connection() as conn:
            result = conn.run(sql, username=username)
            return len(result) > 0
    
    def get_all_users(self) -> List[User]:
        """
        Obtém todos os utilizadores
        
        Returns:
            Lista de utilizadores
        """
        sql = "SELECT * FROM users ORDER BY created_at DESC;"
        
        with self.db.get_connection() as conn:
            result = conn.run(sql)
            
            return [self._row_to_user(row) for row in result]
    
    def delete_user_by_username(self, username: str) -> bool:
        """
        Remove utilizador pelo username
        
        Args:
            username: Nome do utilizador
            
        Returns:
            bool: True se removido, False se não encontrado
        """
        sql = "DELETE FROM users WHERE username = :username;"
        
        with self.db.get_connection() as conn:
            conn.run(sql, username=username)
            return True  # pg8000 doesn't return rowcount easily
    
    def clear_all_users(self):
        """Remove todos os utilizadores (para testes)"""
        sql = "DELETE FROM users;"
        
        with self.db.get_connection() as conn:
            conn.run(sql)
    
    def delete_user(self, user_id: int) -> bool:
        """
        Remove utilizador da BD
        
        Args:
            user_id: ID do utilizador
            
        Returns:
            bool: True se removido, False se não encontrado
        """
        sql = "DELETE FROM users WHERE id = :user_id;"
        
        with self.db.get_connection() as conn:
            result = conn.run(sql, user_id=user_id)
            return conn.rowcount > 0
    
    def _row_to_user(self, row) -> User:
        """
        Converte linha da BD em objeto User
        
        Args:
            row: Linha da base de dados
            
        Returns:
            User: Instância de User
        """
        # pg8000 returns rows as tuples, map to column names
        columns = ['id', 'username', 'email', 'password_hash', 'created_at', 'last_login']
        data = dict(zip(columns, row))
        
        return User.from_dict(data)