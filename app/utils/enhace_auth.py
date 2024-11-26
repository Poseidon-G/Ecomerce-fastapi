from __future__ import annotations

import logging
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Type, TypeVar, Union

from fastapi import (
    Depends, FastAPI, HTTPException, Request, Security, status
)
from fastapi.security import (
    HTTPAuthorizationCredentials, 
    HTTPBearer, 
    OAuth2PasswordBearer
)
from jose import ExpiredSignatureError, JWTError, jwt
from pydantic import BaseModel, Field, ValidationError
from sqlalchemy.orm import Session

# Abstract base classes for enhanced type safety and extensibility
class UserRole(str, Enum):
    """
    Centralized enum for user roles
    Provides a single source of truth for role definitions
    """
    ANONYMOUS = "anonymous"
    USER = "user"
    ADMIN = "admin"
    SUPER_ADMIN = "super_admin"

class TokenType(str, Enum):
    """
    Defines different types of tokens
    """
    ACCESS = "access"
    REFRESH = "refresh"
    RESET_PASSWORD = "reset_password"

class UserContextModel(BaseModel):
    """
    Standardized user context model with comprehensive attributes
    """
    id: str = Field(..., description="Unique user identifier")
    username: str = Field(..., description="User's username")
    email: Optional[str] = Field(None, description="User's email address")
    roles: List[UserRole] = Field(
        default=[UserRole.USER], 
        description="User roles"
    )
    is_active: bool = Field(
        default=True, 
        description="User account status"
    )
    permissions: List[str] = Field(
        default_factory=list, 
        description="Granular permissions"
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict, 
        description="Additional user metadata"
    )

    @property
    def is_admin(self) -> bool:
        """Quick check for admin roles"""
        return any(role in [UserRole.ADMIN, UserRole.SUPER_ADMIN] 
                   for role in self.roles)

    def has_role(self, *roles: UserRole) -> bool:
        """
        Check if user has any of the specified roles
        
        :param roles: Roles to check
        :return: Boolean indicating role match
        """
        return any(role in self.roles for role in roles)

    def has_permission(self, *permissions: str) -> bool:
        """
        Check if user has specific permissions
        
        :param permissions: Permissions to check
        :return: Boolean indicating permission
        """
        return any(perm in self.permissions for perm in permissions)

class AuthConfig:
    """
    Centralized configuration for authentication
    """
    SECRET_KEY: str = "your-highly-secure-secret-key"  # Replace with secure method
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days

class TokenService:
    """
    Comprehensive token management service
    """
    @staticmethod
    def create_token(
        data: Dict[str, Any], 
        token_type: TokenType = TokenType.ACCESS,
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """
        Create JWT token with flexible configuration
        
        :param data: Payload data
        :param token_type: Type of token
        :param expires_delta: Token expiration time
        :return: Encoded JWT token
        """
        to_encode = data.copy()
        
        # Set expiration
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(
                minutes=AuthConfig.ACCESS_TOKEN_EXPIRE_MINUTES
            )
        
        to_encode.update({
            "exp": expire,
            "type": token_type.value
        })
        
        return jwt.encode(
            to_encode, 
            AuthConfig.SECRET_KEY, 
            algorithm=AuthConfig.ALGORITHM
        )

    @staticmethod
    def decode_token(token: str) -> Dict[str, Any]:
        """
        Decode and validate JWT token
        
        :param token: JWT token string
        :return: Decoded token payload
        """
        try:
            return jwt.decode(
                token, 
                AuthConfig.SECRET_KEY, 
                algorithms=[AuthConfig.ALGORITHM]
            )
        except ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired"
            )
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials"
            )

class UserContextManager:
    """
    Advanced user context management with dependency injection
    """
    _current_context: Optional[UserContextModel] = None
    
    @classmethod
    def set_context(cls, context: Optional[UserContextModel]) -> None:
        """
        Set the current user context
        
        :param context: User context to set
        """
        cls._current_context = context

    @classmethod
    def get_context(cls) -> Optional[UserContextModel]:
        """
        Retrieve the current user context
        
        :return: Current user context or None
        """
        return cls._current_context

    @classmethod
    def require_context(cls) -> UserContextModel:
        """
        Get context or raise exception if not available
        
        :return: Current user context
        :raises HTTPException: If no context is available
        """
        context = cls.get_context()
        if not context:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required"
            )
        return context

    @classmethod
    def require_roles(cls, *roles: UserRole) -> UserContextModel:
        """
        Require specific roles for access
        
        :param roles: Required roles
        :return: Current user context
        :raises HTTPException: If roles are not met
        """
        context = cls.require_context()
        if not any(context.has_role(role) for role in roles):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions"
            )
        return context

def create_user_context_middleware(security_scheme):
    """
    Create middleware for extracting and setting user context
    
    :param security_scheme: Authentication scheme
    :return: Middleware function
    """
    async def middleware(request: Request, call_next):
        # Reset context for each request
        UserContextManager.set_context(None)
        
        try:
            # Attempt to extract credentials
            credentials = await security_scheme(request)
            
            # Decode token and create context
            payload = TokenService.decode_token(credentials.credentials)
            
            try:
                # Create user context model
                user_context = UserContextModel(
                    id=payload.get('sub'),
                    username=payload.get('username', ''),
                    email=payload.get('email'),
                    roles=[UserRole(role) for role in payload.get('roles', [])],
                    is_active=payload.get('is_active', True),
                    permissions=payload.get('permissions', []),
                    metadata=payload.get('metadata', {})
                )
                
                # Set the context
                UserContextManager.set_context(user_context)
            
            except ValidationError as e:
                # Log validation errors
                logging.error(f"User context validation failed: {e}")
        
        except HTTPException:
            # No valid authentication - remains unauthenticated
            pass
        
        # Continue request processing
        response = await call_next(request)
        return response
    
    return middleware

# FastAPI Application Setup
app = FastAPI()

# Security schemes
security_bearer = HTTPBearer()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Add middleware
app.middleware("http")(create_user_context_middleware(security_bearer))

# Example Services demonstrating context usage
class ProductService:
    def create_product(self, name: str):
        # Automatically access user context
        context = UserContextManager.require_roles(
            UserRole.ADMIN, UserRole.SUPER_ADMIN
        )
        
        return {
            "message": "Product created",
            "name": name,
            "created_by": context.id
        }

class UserService:
    def get_profile(self):
        # Require authenticated context
        context = UserContextManager.require_context()
        
        return {
            "id": context.id,
            "username": context.username,
            "roles": context.roles
        }

# Example Routes
@app.post("/products")
def create_product(product_name: str):
    service = ProductService()
    return service.create_product(product_name)

@app.get("/profile")
def get_profile():
    service = UserService()
    return service.get_profile()

# Token generation example (for demonstration)
@app.post("/token")
def generate_token():
    # In real-world, this would involve user validation
    token = TokenService.create_token(
        {
            "sub": "user123",
            "username": "johndoe",
            "roles": [UserRole.USER],
            "email": "john@example.com"
        }
    )
    return {"access_token": token}