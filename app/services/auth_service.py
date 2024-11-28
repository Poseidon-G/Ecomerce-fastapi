# app/services/auth_service.py
from datetime import datetime, timedelta
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.repositories.user_repository import UserRepository
from app.schemas.auth import LoginBody, TokenResponse
from app.utils.auth import auth_utils

class AuthService:
    def __init__(self, db: Session):
        self.repository = UserRepository(db)
        self.auth_utils = auth_utils

    async def login(self, login_data: LoginBody) -> TokenResponse:
        """Handle user login and token generation"""
        # Get user and verify credentials
        user = await self.repository.get_by_email(login_data.email)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        if not self.auth_utils.verify_password(login_data.password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect password"
            )

        # Generate tokens
        access_token = self.auth_utils.create_access_token(
            subject=user.id,
            extra_claims={"email": user.email, "role": user.role, "id": user.id}
        )
        
        refresh_token = self.auth_utils.create_refresh_token(
            subject=user.id
        )

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer"
        )

    async def refresh(self, refresh_token: str) -> TokenResponse:
        """Handle access token refresh"""
        try:
            # Verify refresh token
            payload = self.auth_utils.decode_token(refresh_token, verify_type="refresh")
            user_id = payload["sub"]
            
            # Get user
            user = await self.repository.get(user_id)
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found"
                )

            # Generate new access token
            access_token = self.auth_utils.create_access_token(
                subject=user.id,
                extra_claims={"email": user.email, "role": user.role, "id": user.id}
            )

            return TokenResponse(
                access_token=access_token,
                token_type="bearer"
            )
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Error refreshing token: {str(e)}"
            )

    async def logout(self, token: str) -> dict:
        """Handle user logout"""
        try:
            # Verify and blacklist both tokens
            self.auth_utils.blacklist_token(token)
            return {"message": "Successfully logged out"}
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Error during logout: {str(e)}"
            )

    async def validate_token(self, token: str) -> dict:
        """Validate access token and return payload"""
        return self.auth_utils.decode_token(token, verify_type="access")