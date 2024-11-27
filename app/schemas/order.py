from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict
from app.schemas.order_item import OrderItemBase

class OrderBase(BaseModel):
    total: float = Field(..., description="Total order amount")
    items: List[OrderItemBase] = Field(..., description="Order items")
   
class OrderCreate(OrderBase):
    pass

class OrderAdminUpdate(BaseModel):
    total: Optional[float] = Field(None, description="Total order amount")
    items: Optional[List[OrderItemBase]] = Field(None, description="Order items")
    is_active: Optional[bool] = Field(None, description="Order status")
    is_shipped: Optional[bool] = Field(None, description="Order shipped status")
    is_paid: Optional[bool] = Field(None, description="Order paid status")


class OrderResponse(OrderBase):
    id: int
    user_id: int
    is_active: bool
    is_shipped: bool
    is_paid: bool
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)

    def dict(self, **kwargs):
        return super().model_dump(**kwargs)