"""
Authentication Manager
Handles user registration, login, and token validation
"""

from typing import Optional, Dict
from datetime import timedelta

from utils.security import hash_password, verify_password, create_access_token, verify_token
from database.db_manager import DatabaseManager
from database.models import User


class AuthManager:
    """Authentication manager"""

    def __init__(self, db_manager: DatabaseManager):
        """Initialize auth manager"""
        self.db = db_manager

    def register_user(self, email: str, username: str, password: str) -> Dict:
        """
        Register a new user

        Args:
            email: User email
            username: Username
            password: Plain text password

        Returns:
            Dictionary with user info and token

        Raises:
            ValueError: If user already exists or validation fails
        """
        # Validate input
        if not email or not username or not password:
            raise ValueError("Email, username, and password are required")

        if len(password) < 6:
            raise ValueError("Password must be at least 6 characters long")

        # Check if user already exists
        if self.db.get_user_by_email(email):
            raise ValueError("Email already registered")

        if self.db.get_user_by_username(username):
            raise ValueError("Username already taken")

        # Hash password and create user
        password_hash = hash_password(password)
        user = self.db.create_user(email=email, username=username, password_hash=password_hash)

        # Generate access token
        access_token = create_access_token({"sub": user.id})

        return {
            "user": {
                "id": user.id,
                "email": user.email,
                "username": user.username,
                "created_at": user.created_at.isoformat() if user.created_at else None
            },
            "access_token": access_token,
            "token_type": "bearer"
        }

    def login(self, identifier: str, password: str) -> Dict:
        """
        Login user with email/username and password

        Args:
            identifier: Email or username
            password: Plain text password

        Returns:
            Dictionary with user info and token

        Raises:
            ValueError: If credentials are invalid
        """
        # Try to find user by email or username
        user = self.db.get_user_by_email(identifier)
        if not user:
            user = self.db.get_user_by_username(identifier)

        if not user:
            raise ValueError("Invalid credentials")

        # Verify password
        if not verify_password(password, user.password_hash):
            raise ValueError("Invalid credentials")

        # Check if user is active
        if not user.is_active:
            raise ValueError("User account is inactive")

        # Generate access token
        access_token = create_access_token({"sub": user.id})

        return {
            "user": {
                "id": user.id,
                "email": user.email,
                "username": user.username
            },
            "access_token": access_token,
            "token_type": "bearer"
        }

    def validate_token(self, token: str) -> Optional[User]:
        """
        Validate token and return user

        Args:
            token: JWT token

        Returns:
            User object or None if invalid
        """
        payload = verify_token(token)
        if not payload:
            return None

        user_id = payload.get("sub")
        if not user_id:
            return None

        user = self.db.get_user_by_id(user_id)
        if not user or not user.is_active:
            return None

        return user

    def get_current_user(self, token: str) -> Dict:
        """
        Get current user from token

        Args:
            token: JWT token

        Returns:
            Dictionary with user info

        Raises:
            ValueError: If token is invalid
        """
        user = self.validate_token(token)
        if not user:
            raise ValueError("Invalid or expired token")

        return {
            "id": user.id,
            "email": user.email,
            "username": user.username,
            "created_at": user.created_at.isoformat() if user.created_at else None
        }

    def change_password(self, user_id: int, old_password: str, new_password: str) -> bool:
        """
        Change user password

        Args:
            user_id: User ID
            old_password: Current password
            new_password: New password

        Returns:
            True if successful

        Raises:
            ValueError: If validation fails
        """
        user = self.db.get_user_by_id(user_id)
        if not user:
            raise ValueError("User not found")

        # Verify old password
        if not verify_password(old_password, user.password_hash):
            raise ValueError("Current password is incorrect")

        # Validate new password
        if len(new_password) < 6:
            raise ValueError("New password must be at least 6 characters long")

        # Update password
        new_hash = hash_password(new_password)
        with self.db.get_session() as session:
            user = session.query(User).filter(User.id == user_id).first()
            if user:
                user.password_hash = new_hash
                session.commit()
                return True

        return False
