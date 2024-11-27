# app/api/v1/endpoints/categories.py
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.models.model import User
from app.schemas.base import PaginatedResponse
from app.services.user_service import UserService
from app.schemas.user import UserCreate, UserUpdate, UserResponse, UserPasswordUpdate
from app.utils.auth import auth_utils
from app.models.model import UserRole
from app.utils.helpers import paginate

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
    current_user: User = Depends(auth_utils.require_roles(["admin"])),
    service: UserService = Depends(get_user_service)
) -> UserResponse:
    return await service.create_user(user)

@router.get(
    "/",
    response_model=PaginatedResponse[UserResponse],
    description="Get all users"
)
async def get_users(
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(100, ge=1, le=100, description="Page size"),
    current_user: User = Depends(auth_utils.require_roles(["admin"])),
    service: UserService = Depends(get_user_service)
) -> PaginatedResponse[UserResponse]:
    users, total = await service.get_users(page, size)
    return paginate(users, UserResponse, total, page, size)

@router.get(
    "/{user_id}",
    response_model=UserResponse,
    description="Get a user by ID"
)
async def get_user(
    user_id: int,
    current_user: User = Depends(auth_utils.require_roles(["admin"])),
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
    current_user: User = Depends(auth_utils.require_roles(["admin"])),
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
    current_user: User = Depends(auth_utils.require_roles(["admin"])),
    service: UserService = Depends(get_user_service)
):
    return await service.deactivate_user(user_id)

@router.get(
    "/me",
    response_model=UserResponse,
    description="Get current user profile",
    dependencies=[Depends(auth_utils.get_current_user)]
)
async def get_current_user(
    service: UserService = Depends(get_user_service)
) -> UserResponse:
    return await service.get_current_user()

@router.put(
    "/me/password",
    response_model=UserResponse,
    description="Update password",
    dependencies=[Depends(auth_utils.get_current_user)]
)

async def update_password(
    user: UserPasswordUpdate,
    service: UserService = Depends(get_user_service)
) -> UserResponse:
    return await service.update_password(user)
