from typing import Any, Dict, List, Optional, Tuple
from fastapi import HTTPException
from app.repositories.order_repository import OrderRepository
from app.repositories.order_item_repository import OrderItemRepository
from app.schemas.order import OrderCreate, OrderResponse, OrderAdminUpdate
from app.models.model import Product
from sqlalchemy.orm import Session


class OrderService:
    def __init__(self, db: Session):
        self.repository = OrderRepository(db)
        self.order_item_repository = OrderItemRepository(db)

    async def create_order(self, order_data: OrderCreate, user_id: int) -> OrderResponse:
        """Create a new order."""
        # Calculate total from items
        total = sum(item.price * item.quantity for item in order_data.items)
        
        # Create order first
        order_dump = {
            "user_id": user_id,
            "total": total,
            "is_paid": False,
            "is_shipped": False
        }
        
        order = await self.repository.create(order_dump)

        items = []
        # Create order items with proper relationships
        for item in order_data.items:
            order_item_data = {
                "order_id": order.id,
                "product_id": item.product_id,
                "quantity": item.quantity,
                "price": item.price
            }
            order_item = await self.order_item_repository.create(order_item_data)
            items.append(order_item)
        
        order = await self.repository.get(order.id)
        return {
                    "id": order.id,
                    "user_id": order.user_id,
                    "total": order.total,
                    "is_paid": order.is_paid,
                    "is_shipped": order.is_shipped,
                    "created_at": order.created_at,
                    "updated_at": order.updated_at,
                    "items": [{
                        "id": item.id,
                        "order_id": item.order_id,
                        "product_id": item.product_id,
                        "quantity": item.quantity,
                        "price": item.price,
                        "created_at": item.created_at,
                        "updated_at": item.updated_at
                    } for item in items]
                }
    async def get_orders(
        self,
        page: int = 1,
        size: int = 100,
        filters: Optional[Dict[str, Any]] = None
    ) -> Tuple[List[OrderResponse], int]:
        """Get all orders."""
        skip = (page - 1) * size
        limit = size
        orders, total = await self.repository.get_all(
            filters=filters,
            skip=skip,
            limit=limit
        ), await self.repository.count(filters=filters)

        return orders, total
    
    async def get_order(self, order_id: int) -> Optional[OrderResponse]:
        """Get order by ID."""
        order = await self.repository.get(order_id)
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")
        return order    
    

    async def update_order(self, order_id: int, order_data: OrderAdminUpdate) -> OrderResponse:
        """Update order."""
        order = await self.repository.get(order_id)
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")
        return await self.repository.update(order, order_data.model_dump())
    
    async def delete_order(self, order_id: int) -> bool:
        """Delete order."""
        order = await self.repository.get(order_id)
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")
        return await self.repository.delete(order)
    
    async def search_orders(self, search_term: str) -> List[OrderResponse]:
        """Search orders."""
        return await self.repository.search_orders(search_term)
