# app/api/v1/endpoints/categories.py
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.models.model import User
from app.schemas.base import PaginatedResponse
from app.services.order.order_service import OrderService
from app.schemas.order import OrderCreate, OrderAdminUpdate, OrderResponse
from app.utils.helpers import paginate
from app.utils.auth import auth_utils

router = APIRouter(
    prefix="/orders",
    tags=["orders"],
    responses={404: {"description": "Not found"}}
)

async def get_order_service(db: Session = Depends(get_db)) -> OrderService:
    return OrderService(db)

@router.post(
    "/",
    response_model=OrderResponse,
    status_code=201,
    description="Create a new order"
)
async def create_order(
    product: OrderCreate,
    current_user: User = Depends(auth_utils.require_roles(["admin"])),
    service: OrderService = Depends(get_order_service)
) -> OrderResponse:
    return await service.create_order(product)


@router.get(
    "/",
    response_model=PaginatedResponse[OrderResponse],
    description="Get all products with filtering"
)
async def get_orders(
    skip: int = Query(0, ge=0, description="Skip N items"),
    limit: int = Query(100, ge=1, le=100, description="Limit the results"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    current_user: User = Depends(auth_utils.require_roles(["admin"])),
    service: OrderService = Depends(get_order_service)
) -> PaginatedResponse[OrderResponse]:
    filters = {"is_active": is_active} if is_active is not None else None
    orders, total = await service.get_orders(skip, limit, filters)
    return paginate(orders, OrderResponse, total, skip, limit)

@router.get(
    "/{order_id}",
    response_model=OrderResponse,
    description="Get a order by ID"
)
async def get_order(
    order_id: int,
    current_user: User = Depends(auth_utils.require_roles(["admin"])),
    service: OrderService = Depends(get_order_service)
) -> OrderResponse:
    return await service.get_order(order_id)

@router.put(
    "/{order_id}",
    response_model=OrderResponse,
    description="Update a order by ID"
)
async def update_order(
    order_id: int,
    order: OrderAdminUpdate,
    current_user: User = Depends(auth_utils.require_roles(["admin"])),
    service: OrderService = Depends(get_order_service)
) -> OrderResponse:
    return await service.update_order(order_id, order)

@router.delete(
    "/{order_id}",
    status_code=204,
    description="Delete a order by ID"
)
async def delete_order(
    order_id: int,
    current_user: User = Depends(auth_utils.require_roles(["admin"])),
    service: OrderService = Depends(get_order_service)
) -> None:
    await service.delete_order(order_id)

@router.get(
    "/search",
    response_model=List[OrderResponse],
    description="Search orders"
)
async def search_orders(
    search_term: str,
    current_user: User = Depends(auth_utils.require_roles(["admin"])),
    service: OrderService = Depends(get_order_service)
) -> List[OrderResponse]:
    return await service.search_orders(search_term)
