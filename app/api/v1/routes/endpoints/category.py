# app/api/v1/endpoints/categories.py
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.services.category_service import CategoryService
from app.schemas.base import PaginatedResponse
from app.schemas.category import (
    CategoryCreate,
    CategoryUpdate,
    CategoryResponse,
)
from app.utils.helpers import paginate, convert_pydantic

router = APIRouter(
    prefix="/categories",
    tags=["categories"],
    responses={404: {"description": "Not found"}}
)

async def get_category_service(db: Session = Depends(get_db)) -> CategoryService:
    return CategoryService(db)

@router.post(
    "/",
    response_model=CategoryResponse,
    status_code=201,
    description="Create a new category"
)
async def create_category(
    category: CategoryCreate,
    service: CategoryService = Depends(get_category_service)
) -> CategoryResponse:
    return await service.create_category(category)

@router.get(
    "/{category_id}",
    response_model=CategoryResponse,
    description="Get a category by ID"
)
async def get_category(
    category_id: int,
    service: CategoryService = Depends(get_category_service)
) -> CategoryResponse:
    return await service.get_category(category_id)

@router.get(
    "/",
    response_model=PaginatedResponse[CategoryResponse],
    description="Get all categories with filtering"
)
async def get_categories(
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(100, ge=1, le=100, description="Page size"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    service: CategoryService = Depends(get_category_service)
) -> PaginatedResponse[CategoryResponse]:
    filters = {"is_active": is_active} if is_active is not None else None
    categories, total = await service.get_categories(page, size, filters)

    return paginate(categories, CategoryResponse, total, page, size)

@router.put(
    "/{category_id}",
    response_model=CategoryResponse,
    description="Update a category"
)
async def update_category(
    category_id: int,
    category: CategoryUpdate,
    service: CategoryService = Depends(get_category_service)
) -> CategoryResponse:
    return await service.update_category(category_id, category)

@router.delete(
    "/{category_id}",
    status_code=204,
    description="Delete a category"
)
async def delete_category(
    category_id: int,
    service: CategoryService = Depends(get_category_service)
):
    result = await service.delete_category(category_id)
    if not result:
        raise HTTPException(status_code=404, detail="Category not found")