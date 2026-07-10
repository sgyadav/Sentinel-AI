"""Authentication routes with JWT and comprehensive security"""

import logging
from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel, Field, EmailStr, validator
from sqlalchemy.orm import Session
from db.database import get_db
from db.models import UserDB
from services.auth_service import AuthService
from core.security import get_current_user
from core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


# ===========================
# Request/Response Models
# ===========================

class LoginRequest(BaseModel):
    """Login request model"""
    username: str = Field(..., min_length=3, max_length=255)
    password: str = Field(..., min_length=6)


class SignupRequest(BaseModel):
    """User registration request model"""
    username: str = Field(..., min_length=3, max_length=255)
    email: EmailStr
    password: str = Field(..., min_length=8)
    role: str = Field(default="User")


class ChangePasswordRequest(BaseModel):
    """Change password request model"""
    old_password: str = Field(..., min_length=6)
    new_password: str = Field(..., min_length=8)


class UpdateProfileRequest(BaseModel):
    """Update username/email/password request."""
    username: str = Field(..., min_length=3, max_length=255)
    email: EmailStr
    current_password: str = Field(..., min_length=6)
    new_password: str = Field(default="", max_length=128)


class TokenResponse(BaseModel):
    """Token response model"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int


class UserResponse(BaseModel):
    """User response model"""
    username: str
    email: str
    role: str
    organization: str


# ===========================
# Authentication Endpoints
# ===========================

@router.get("/status", tags=["Health"])
def auth_status():
    """Check authentication service status"""
    return {
        "status": "operational",
        "authentication_enabled": True,
        "jwt_enabled": True,
        "version": settings.APP_VERSION
    }


@router.post("/login", response_model=dict)
def login(request: LoginRequest, db: Session = Depends(get_db)):
    """
    Authenticate user and return JWT token
    
    Args:
        request: Login credentials
        db: Database session
        
    Returns:
        JWT token and user info on success
        
    Raises:
        HTTPException: If credentials are invalid
    """
    try:
        success, token, result = AuthService.authenticate_user(
            db,
            request.username,
            request.password
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=result  # Error message
            )
        
        return {
            "success": True,
            "access_token": token,
            "token_type": "bearer",
            "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            "user": result
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Authentication service error"
        )


@router.post("/signup", response_model=dict)
def signup(request: SignupRequest, db: Session = Depends(get_db)):
    """
    Register a new user account
    
    Args:
        request: Registration details
        db: Database session
        
    Returns:
        Confirmation message with user info
        
    Raises:
        HTTPException: If registration fails
    """
    try:
        user = AuthService.register_user(
            db,
            username=request.username,
            email=request.email,
            password=request.password,
            role=request.role
        )
        
        return {
            "success": True,
            "message": "User registered successfully",
            "user": {
                "username": user.username,
                "email": user.email,
                "role": user.role
            }
        }
        
    except ValueError as e:
        logger.warning(f"Signup validation error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Signup error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed"
        )


@router.post("/change-password", response_model=dict)
def change_password(
    request: ChangePasswordRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Change user password (requires authentication)
    
    Args:
        request: Old and new passwords
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Success message
        
    Raises:
        HTTPException: If password change fails
    """
    try:
        success = AuthService.change_password(
            db,
            current_user["sub"],
            request.old_password,
            request.new_password
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid old password or password change failed"
            )
        
        return {
            "success": True,
            "message": "Password changed successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Password change error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Password change failed"
        )


@router.put("/profile", response_model=dict)
def update_profile(
    request: UpdateProfileRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update the current admin/user account username, email, and password."""
    try:
        success, token_or_message, user = AuthService.update_profile(
            db,
            current_user["sub"],
            request.username,
            request.email,
            request.current_password,
            request.new_password
        )

        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=token_or_message
            )

        return {
            "success": True,
            "message": "Account updated successfully",
            "access_token": token_or_message,
            "token_type": "bearer",
            "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            "user": user
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Profile update error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Profile update failed"
        )


@router.get("/me", response_model=dict)
def get_current_user_info(current_user: dict = Depends(get_current_user)):
    """
    Get current authenticated user info
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        User information
    """
    return {
        "username": current_user.get("sub"),
        "role": current_user.get("role"),
        "organization": current_user.get("organization")
    }


@router.post("/logout", response_model=dict)
def logout(current_user: dict = Depends(get_current_user)):
    """
    Logout user (token is invalidated client-side)
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        Logout confirmation
    """
    logger.info(f"User logged out: {current_user.get('sub')}")
    return {
        "success": True,
        "message": "Logged out successfully"
    }


@router.post("/verify-token", response_model=dict)
def verify_token(current_user: dict = Depends(get_current_user)):
    """
    Verify JWT token is valid
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        Token validation result
    """
    return {
        "valid": True,
        "username": current_user.get("sub"),
        "role": current_user.get("role")
    }
