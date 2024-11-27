from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict

class OrderItemBase(BaseModel):
    product_id: int = Field(..., description="Product ID")
    quantity: int = Field(..., description="Product quantity")
    price: float = Field(..., description="Product price")


class OrderItemCreate(OrderItemBase):
    order_id: int = Field(..., description="Order ID")


class OrderItemUpdate(BaseModel):
    quantity: Optional[int] = Field(None, description="Product quantity")
    price: Optional[float] = Field(None, description="Product price")

class OrderItemResponse(OrderItemBase):
    id: int
    order_id: int
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)

    def dict(self, **kwargs):
        return super().model_dump(**kwargs)
