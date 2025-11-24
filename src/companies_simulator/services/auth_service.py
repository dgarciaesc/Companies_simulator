"""
Authentication service - handles user login and registration
"""
import hashlib
from typing import Optional
from companies_simulator.domain.models import User
from companies_simulator.domain.ports import RepositoryPort


class AuthService:
    """Service for handling authentication operations."""
    
    def __init__(self, repository: RepositoryPort):
        self.repository = repository
    
    def hash_password(self, password: str) -> str:
        """Hash a password using SHA256."""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def verify_password(self, password: str, password_hash: str) -> bool:
        """Verify a password against its hash."""
        return self.hash_password(password) == password_hash
    
    def login(self, email: str, password: str) -> Optional[User]:
        """
        Authenticate a user by email and password.
        Returns User if credentials are valid, None otherwise.
        """
        user = self.repository.get_user_by_email(email)
        if not user:
            return None
        
        if not self.verify_password(password, user.password_hash):
            return None
        
        return user
    
    def register(self, email: str, password: str, company_id: Optional[int] = None) -> Optional[User]:
        """
        Register a new user.
        Returns User if registration successful, None if email already exists.
        """
        # Check if user already exists
        existing_user = self.repository.get_user_by_email(email)
        if existing_user:
            return None
        
        # Hash password and create user
        password_hash = self.hash_password(password)
        return self.repository.create_user(email, password_hash, company_id)
