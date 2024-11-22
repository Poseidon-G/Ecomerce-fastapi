# app/api/v1/endpoints/categories.py
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.models.model import User
from app.services.user_service import UserService
from app.schemas.user import UserCreate, UserUpdate, UserResponse, UserPasswordUpdate
from app.utils.auth import auth_utils

router = APIRouter(
    prefix="/users",
    tags=["users"],
    responses={404: {"description": "Not found"}}
)

async def get_user_service(db: Session = Depends(get_db)) -> UserService:
    return UserService(db)

@router.post(
    "/",
    response_model=UserResponse,
    status_code=201,
    description="Create a new user",
)
async def create_user(
    user: UserCreate,
    current_user: User = Depends(auth_utils.get_current_user),
    service: UserService = Depends(get_user_service)
) -> UserResponse:
    return await service.create_user(user)

@router.get(
    "/",
    response_model=List[UserResponse],
    description="Get all users"
)
async def get_users(
    skip: int = Query(0, ge=0, description="Skip N items"),
    limit: int = Query(100, ge=1, le=100, description="Limit the results"),
    service: UserService = Depends(get_user_service)
) -> List[UserResponse]:
    return await service.get_users(skip=skip, limit=limit)

@router.get(
    "/{user_id}",
    response_model=UserResponse,
    description="Get a user by ID"
)
async def get_user(
    user_id: int,
    service: UserService = Depends(get_user_service)
) -> UserResponse:
    return await service.get_user(user_id)

@router.put(
    "/{user_id}",
    response_model=UserResponse,
    description="Update a user"
)
async def update_user(
    user_id: int,
    user: UserUpdate,
    service: UserService = Depends(get_user_service)
) -> UserResponse:
    return await service.update_user(user_id, user)

@router.delete(
    "/{user_id}",
    status_code=204,
    description="Deactivate a user"
)
async def deactivate_user(
    user_id: int,
    service: UserService = Depends(get_user_service)
):
    return await service.deactivate_user(user_id)

@router.get(
    "/me",
    response_model=UserResponse,
    description="Get current user profile"
)
async def get_current_user(
    service: UserService = Depends(get_user_service)
) -> UserResponse:
    return await service.get_current_user()

@router.put(
    "/me/password",
    response_model=UserResponse,
    description="Update password"
)

async def update_password(
    user: UserPasswordUpdate,
    service: UserService = Depends(get_user_service)
) -> UserResponse:
    return await service.update_password(user)
