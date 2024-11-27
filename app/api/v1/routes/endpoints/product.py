# app/api/v1/endpoints/categories.py
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.models.model import User
from app.schemas.base import PaginatedResponse
from app.services.product_service import ProductService
from app.schemas.product import ProductCreate, ProductUpdate, ProductResponse
from app.utils.helpers import paginate
from app.utils.auth import auth_utils

router = APIRouter(
    prefix="/products",
    tags=["products"],
    responses={404: {"description": "Not found"}}
)

async def get_product_service(db: Session = Depends(get_db)) -> ProductService:
    return ProductService(db)

@router.post(
    "/",
    response_model=ProductResponse,
    status_code=201,
    description="Create a new product"
)
async def create_product(
    product: ProductCreate,
    current_user: User = Depends(auth_utils.require_roles(["admin"])),
    service: ProductService = Depends(get_product_service)
) -> ProductResponse:
    return await service.create_product(product)


@router.get(
    "/",
    response_model=PaginatedResponse[ProductResponse],
    description="Get all products with filtering"
)
async def get_products(
    skip: int = Query(0, ge=0, description="Skip N items"),
    limit: int = Query(100, ge=1, le=100, description="Limit the results"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    current_user: User = Depends(auth_utils.require_roles(["admin"])),
    service: ProductService = Depends(get_product_service)
) -> PaginatedResponse[ProductResponse]:
    filters = {"is_active": is_active} if is_active is not None else None
    products, total = await service.get_products(skip, limit, filters)
    return paginate(products, ProductResponse, total, skip, limit)

@router.get(
    "/{product_id}",
    response_model=ProductResponse,
    description="Get a product by ID"
)
async def get_product(
    product_id: int,
    service: ProductService = Depends(get_product_service)
) -> ProductResponse:
    return await service.get_product(product_id)


@router.put(
    "/{product_id}",
    response_model=ProductResponse,
    description="Update a product"
)
async def update_product(
    product_id: int,
    product: ProductUpdate,
    current_user: User = Depends(auth_utils.require_roles(["admin"])),
    service: ProductService = Depends(get_product_service)
) -> ProductResponse:
    return await service.update_product(product_id, product)

@router.delete(
    "/{product_id}",
    status_code=204,
    description="Delete a product"
)
async def delete_product(
    product_id: int,
    current_user: User = Depends(auth_utils.require_roles(["admin"])),
    service: ProductService = Depends(get_product_service)
) -> None:
    await service.delete_product(product_id)

@router.get(
    "/search",
    response_model=List[ProductResponse],
    description="Search products"
)
async def search_products(
    search_term: str,
    current_user: User = Depends(auth_utils.require_roles(["admin"])),
    service: ProductService = Depends(get_product_service)
) -> List[ProductResponse]:
    return await service.search_products(search_term)