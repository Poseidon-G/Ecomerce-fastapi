from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict
from app.schemas.base import PaginationMetadata

class CategoryBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=100, description="Category name")
    description: Optional[str] = Field(None, description="Category description")
    is_active: bool = Field(default=True, description="Category status")
    parent_id: Optional[int] = Field(default=None, description="Parent category ID")

class CategoryCreate(CategoryBase):
    pass

class CategoryUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    description: Optional[str] = None
    is_active: Optional[bool] = None
    parent_id: Optional[str] = None

class CategoryResponse(CategoryBase):
    id: int
    slug: str
    model_config = ConfigDict(from_attributes=True)

    def dict(self, **kwargs):
        return super().model_dump(**kwargs)

class PaginatedCategoryResponse(BaseModel):
    data: List[CategoryResponse]
    metadata: PaginationMetadata
    model_config = ConfigDict(from_attributes=True)