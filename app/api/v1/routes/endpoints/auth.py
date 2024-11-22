# app/api/v1/endpoints/categories.py
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.services.auth_service import AuthService
from app.schemas.auth import TokenPayload, TokenResponse, LoginBody

router = APIRouter(
    prefix="/auth",
    tags=["authentications"],
    responses={404: {"description": "Not found"}}
)

async def get_auth_service(db: Session = Depends(get_db)) -> AuthService:
    return AuthService(db)

@router.post(
    "/login",
    response_model=TokenResponse,
    description="User login and token generation"
)
async def login(
    login_data: LoginBody,
    service: AuthService = Depends(get_auth_service)
) -> TokenResponse:
    return await service.login(login_data)

@router.post(
    "/refresh",
    response_model=TokenResponse,
    description="Access token refresh"
)
async def refresh(
    payload: TokenPayload,
    service: AuthService = Depends(get_auth_service)
) -> TokenResponse:
    return await service.refresh(payload.refresh_token)


@router.post(
    "/logout",
    description="User logout"
)
async def logout(
    payload: TokenPayload,
    service: AuthService = Depends(get_auth_service)
):
    return await service.logout(payload.refresh_token)
