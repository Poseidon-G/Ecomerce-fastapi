# app/schemas/pagination.py
from typing import Generic, TypeVar, List, Optional, Dict
from pydantic import BaseModel, ConfigDict, Field
T = TypeVar("T", bound=BaseModel)

class PaginationMetadata(BaseModel):
    total_items: int = Field(..., description="Total number of items")
    items_per_page: int = Field(..., description="Number of items per page")
    current_page: int = Field(..., description="Current page number")
    total_pages: int = Field(..., description="Total number of pages")
    has_previous: bool = Field(..., description="Whether there is a previous page")
    has_next: bool = Field(..., description="Whether there is a next page")

class PaginatedResponse(BaseModel, Generic[T]):
    items: List[T] = Field(..., description="List of items")
    metadata: PaginationMetadata
    model_config = ConfigDict(from_attributes=True)
