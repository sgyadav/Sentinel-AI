"""Authentication service with enhanced security"""

import logging
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_
from db.models import UserDB
from auth.password import hash_password, verify_password
from auth.jwt_handler import create_access_token
from core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

# Account lockout configuration
MAX_LOGIN_ATTEMPTS = 5
LOCKOUT_DURATION_MINUTES = 30


class AuthService:
    """Authentication service"""
    
    @staticmethod
    def register_user(
        db: Session,
        username: str,
        email: str,
        password: str,
        role: str = "User",
        organization: str = "Sentinel AI"
    ) -> UserDB:
        """
        Register a new user
        
        Args:
            db: Database session
            username: Username
            email: Email address
            password: Password (will be hashed)
            role: User role
            organization: Organization name
            
        Returns:
            Created UserDB object
            
        Raises:
            ValueError: If username or email already exists
        """
        # Check if user exists
        existing = db.query(UserDB).filter(
            (UserDB.username == username) | (UserDB.email == email)
        ).first()
        
        if existing:
            raise ValueError(
                f"Username or email already exists"
            )
        
        # Validate password length (bcrypt has 72-byte limit)
        if len(password) < settings.PASSWORD_MIN_LENGTH:
            raise ValueError(
                f"Password must be at least {settings.PASSWORD_MIN_LENGTH} characters"
            )
        
        if len(password) > 72:
            raise ValueError(
                f"Password must be less than 72 characters"
            )
        
        # Create user
        hashed_password = hash_password(password)
        new_user = UserDB(
            username=username,
            email=email,
            password=hashed_password,
            role=role,
            organization=organization,
            is_active=True,
            is_verified=False
        )
        
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        logger.info(f"New user registered: {username}")
        return new_user
    
    @staticmethod
    def authenticate_user(db: Session, username: str, password: str) -> tuple:
        """
        Authenticate user and return JWT token
        
        Args:
            db: Database session
            username: Username
            password: Password
            
        Returns:
            Tuple of (success, token, user_dict) or (False, None, error_message)
        """
        user = db.query(UserDB).filter(UserDB.username == username).first()
        
        if not user:
            logger.warning(f"Login attempt with unknown username: {username}")
            return False, None, "Invalid credentials"
        
        # Check if account is locked
        if user.locked_until and user.locked_until > datetime.utcnow():
            remaining_minutes = (
                (user.locked_until - datetime.utcnow()).total_seconds() / 60
            )
            logger.warning(
                f"Login attempt on locked account: {username} "
                f"(locked for {remaining_minutes:.1f} more minutes)"
            )
            return False, None, f"Account locked. Try again later."
        
        # Check if account is active
        if not user.is_active:
            logger.warning(f"Login attempt on inactive account: {username}")
            return False, None, "Account is inactive"
        
        # Verify password
        if not verify_password(password, user.password):
            # Increment failed attempts
            user.failed_login_attempts += 1
            
            # Lock account if max attempts exceeded
            if user.failed_login_attempts >= MAX_LOGIN_ATTEMPTS:
                user.locked_until = datetime.utcnow() + timedelta(
                    minutes=LOCKOUT_DURATION_MINUTES
                )
                logger.warning(
                    f"Account locked due to too many failed attempts: {username}"
                )
            
            db.commit()
            logger.warning(f"Failed login attempt for user: {username}")
            return False, None, "Invalid credentials"
        
        # Reset failed attempts on successful login
        user.failed_login_attempts = 0
        user.locked_until = None
        user.last_login = datetime.utcnow()
        db.commit()
        
        # Create JWT token
        token = create_access_token({
            "sub": user.username,
            "role": user.role,
            "organization": user.organization
        })
        
        logger.info(f"Successful login for user: {username}")
        
        return True, token, user.to_dict()
    
    @staticmethod
    def get_user(db: Session, username: str) -> UserDB:
        """Get user by username"""
        return db.query(UserDB).filter(UserDB.username == username).first()
    
    @staticmethod
    def change_password(
        db: Session,
        username: str,
        old_password: str,
        new_password: str
    ) -> bool:
        """
        Change user password
        
        Args:
            db: Database session
            username: Username
            old_password: Current password
            new_password: New password
            
        Returns:
            True if successful, False otherwise
        """
        user = db.query(UserDB).filter(UserDB.username == username).first()
        
        if not user:
            logger.warning(f"Password change attempt for unknown user: {username}")
            return False
        
        # Verify old password
        if not verify_password(old_password, user.password):
            logger.warning(f"Failed password change: incorrect old password for {username}")
            return False
        
        # Validate new password
        if len(new_password) < settings.PASSWORD_MIN_LENGTH:
            logger.warning(f"Password change rejected: password too short for {username}")
            return False
        
        if len(new_password) > 72:
            logger.warning(f"Password change rejected: password too long for {username}")
            return False
        
        # Update password
        user.password = hash_password(new_password)
        db.commit()
        
        logger.info(f"Password changed for user: {username}")
        return True

    @staticmethod
    def update_profile(
        db: Session,
        current_username: str,
        new_username: str,
        email: str,
        current_password: str,
        new_password: str = ""
    ) -> tuple:
        """Update username/email and optionally password."""
        user = db.query(UserDB).filter(UserDB.username == current_username).first()

        if not user:
            return False, "User not found", None

        if not verify_password(current_password, user.password):
            return False, "Current password is incorrect", None

        new_username = new_username.strip()
        email = email.strip()

        if not new_username:
            return False, "Username is required", None

        if not email:
            return False, "Email is required", None

        existing = (
            db.query(UserDB)
            .filter(UserDB.username == new_username)
            .filter(UserDB.id != user.id)
            .first()
        )

        if existing:
            return False, "Username already exists", None

        existing_email = (
            db.query(UserDB)
            .filter(UserDB.email == email)
            .filter(UserDB.id != user.id)
            .first()
        )

        if existing_email:
            return False, "Email already exists", None

        if new_password:
            if len(new_password) < settings.PASSWORD_MIN_LENGTH:
                return False, "New password is too short", None
            user.password = hash_password(new_password)

        user.username = new_username
        user.email = email
        db.commit()
        db.refresh(user)

        token = create_access_token({
            "sub": user.username,
            "role": user.role,
            "organization": user.organization
        })

        logger.info("User profile updated: %s", user.username)

        return True, token, user.to_dict()
