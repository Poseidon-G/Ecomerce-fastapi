from datetime import datetime, timedelta, timezone
from typing import Annotated, List, Optional, Union, Dict, Any, Set
from fastapi.security import HTTPBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status, Request
from pydantic import ValidationError
from app.core.config import settings
from app.repositories.user_repository import UserRepository
from app.schemas.auth import TokenPayload
from collections import defaultdict
import time
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.models.model import User

bearerSchema = HTTPBearer()
class AuthUtils:
    """Authentication utility class for token management and password hashing."""
    
    def __init__(self, db: Session = Depends(get_db)):
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        self.algorithm = settings.ALGORITHM
        self.secret_key = settings.SECRET_KEY
        self.access_token_expire = settings.ACCESS_TOKEN_EXPIRE_MINUTES
        self.refresh_token_expire = 60 * 24 * 7  # 7 days
        self.token_blacklist: Dict[str, float] = {}  # token -> expiry timestamp
        self.rate_limit_data: Dict[str, List[float]] = defaultdict(list)
        self.rate_limit = 100  # requests per minute
        self._clean_blacklist_interval = 3600  # 1 hour
        self._last_cleanup = time.time()
        self.user_repository = UserRepository(db)

    def _clean_blacklist(self) -> None:
        """Remove expired tokens from blacklist."""
        now = time.time()
        if now - self._last_cleanup > self._clean_blacklist_interval:
            self.token_blacklist = {
                token: exp for token, exp in self.token_blacklist.items()
                if exp > now
            }
            self._last_cleanup = now

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash."""
        return self.pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str) -> str:
        """Generate password hash."""
        return self.pwd_context.hash(password)

    def create_token(
        self,
        subject: Union[str, Any],
        token_type: str,
        expires_delta: Optional[timedelta] = None,
        extra_claims: Optional[Dict[str, Any]] = None
    ) -> str:
        """Create JWT token with common logic."""
        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            minutes = (
                self.refresh_token_expire 
                if token_type == "refresh" 
                else self.access_token_expire
            )
            expire = datetime.now(timezone.utc) + timedelta(minutes=minutes)
            
        to_encode = {
            "exp": expire,
            "sub": str(subject),
            "type": token_type,
            "iat": datetime.utcnow(),
            "jti": f"{token_type}-{time.time()}"
        }
        
        if extra_claims:
            to_encode.update(extra_claims)
            
        return jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)

    def create_access_token(
        self,
        subject: Union[str, Any],
        expires_delta: Optional[timedelta] = None,
        extra_claims: Optional[Dict[str, Any]] = None
    ) -> str:
        """Create JWT access token."""
        return self.create_token(subject, "access", expires_delta, extra_claims)

    def create_refresh_token(
        self,
        subject: Union[str, Any],
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """Create JWT refresh token."""
        return self.create_token(subject, "refresh", expires_delta)

    def decode_token(self, token: str, verify_type: Optional[str] = None) -> Dict[str, Any]:
        """
        Decode and validate JWT token.
        
        Args:
            token: JWT token to decode
            verify_type: Optional token type to verify ("access" or "refresh")
        
        Raises:
            HTTPException: If token is invalid or expired
        """
        try:
            self._clean_blacklist()

            token_str = token.credentials if hasattr(token, 'credentials') else token
            print("token_str", token_str)
            if token_str in self.token_blacklist:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token has been blacklisted"
                )
            
            payload = jwt.decode(
                token_str,
                self.secret_key,
                algorithms=[self.algorithm]
            )
            
            token_data = TokenPayload(**payload)

            print("token_data", token_data)
            
            if verify_type and payload.get("type") != verify_type:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail=f"Invalid token type. Expected {verify_type}"
                )
            
            if token_data.exp < datetime.utcnow().timestamp():
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token has expired"
                )
                
            return payload
            
        except (JWTError, ValidationError) as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Could not validate credentials: {str(e)}"
            )

    def blacklist_token(self, token: str) -> None:
        """Add token to blacklist with expiry."""
        try:
            payload = self.decode_token(token)
            self.token_blacklist[token] = payload["exp"]
        except HTTPException:
            pass

    async def check_rate_limit(self, request: Request) -> None:
        """Check rate limiting for the request."""
        now = time.time()
        ip = request.client.host
        
        # Remove old requests
        self.rate_limit_data[ip] = [
            t for t in self.rate_limit_data[ip]
            if now - t < 60
        ]
        
        if len(self.rate_limit_data[ip]) >= self.rate_limit:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Too many requests"
            )
            
        self.rate_limit_data[ip].append(now)

    def get_security_headers(self) -> Dict[str, str]:
        """Get security headers for API responses."""
        return {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "X-XSS-Protection": "1; mode=block",
            "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
            "Content-Security-Policy": "default-src 'self'",
            "Referrer-Policy": "strict-origin-when-cross-origin",
            "Permissions-Policy": "geolocation=(), microphone=()"
        } 
    async def get_current_user(
        self,
        token: Annotated[str, Depends(bearerSchema)],
        db: Session = Depends(get_db),
    ) -> User:

        try:
            # Decode and validate the token
            payload = self.decode_token(token, verify_type="access")
            token_data = TokenPayload(**payload)
            
            if not token_data.sub:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Could not validate credentials"
                )

            # Get user from database
            user_repository = UserRepository(db)
            user = await user_repository.get_by_field("id", token_data.sub)
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="User not found"
                )
                
            # Check if user is active
            if not user.is_active:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Inactive user"
                )
                    
            return user
            
        except (JWTError, ValidationError) as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Could not validate credentials: {str(e)}"
            )

    # Helper decorator for role-based access control
    def require_roles(self, allowed_roles: Set[str]):
        async def role_checker(
            current_user: User = Depends(self.get_current_user)
        ) -> User:
            if current_user.role not in allowed_roles:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Insufficient permissions"
                )
            return current_user
        return role_checker
    
# Create global instance
auth_utils = AuthUtils()