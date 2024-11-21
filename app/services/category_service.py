from typing import List, Optional, Dict, Any
from fastapi import HTTPException
from app.repositories.category_repository import CategoryRepository
from app.schemas.category import CategoryCreate, CategoryUpdate, CategoryResponse
from app.models.model import Category
from sqlalchemy.orm import Session

class CategoryService:
    def __init__(self, db: Session):
        self.repository = CategoryRepository(db)

    async def create_category(self, category_data: CategoryCreate) -> Category:
        """Create a new category."""
        if category_data.parent_id:
            parent = await self.repository.get(category_data.parent_id)
            if not parent:
                raise HTTPException(status_code=404, detail="Parent category not found")
        
        return await self.repository.create(category_data.model_dump())

    async def get_category(self, category_id: int) -> Optional[Category]:
        """Get category by ID."""
        category = await self.repository.get(category_id)
        if not category:
            raise HTTPException(status_code=404, detail="Category not found")
        return category

    async def get_by_slug(self, slug: str) -> Optional[Category]:
        """Get category by slug."""
        category = await self.repository.get_by_slug(slug)
        if not category:
            raise HTTPException(status_code=404, detail="Category not found")
        return category

    async def get_categories(
        self,
        skip: int = 0,
        limit: int = 100,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Category]:
        """Get all categories with filtering."""
        return await self.repository.get_all(
            filters=filters,
            skip=skip,
            limit=limit
        )

    async def update_category(
        self,
        category_id: int,
        category_data: CategoryUpdate
    ) -> Category:
        """Update category."""
        category = await self.repository.get(category_id)
        if not category:
            raise HTTPException(status_code=404, detail="Category not found")
        
        if category_data.parent_id and category_data.parent_id != category.parent_id:
            if category_data.parent_id == category_id:
                raise HTTPException(
                    status_code=400,
                    detail="Category cannot be its own parent"
                )
            parent = await self.repository.get(category_data.parent_id)
            if not parent:
                raise HTTPException(status_code=404, detail="Parent category not found")

        return await self.repository.update(
            category_id,
            category_data.model_dump(exclude_unset=True)
        )

    async def delete_category(self, category_id: int) -> bool:
        """Delete category and its children."""
        category = await self.repository.get(category_id)
        if not category:
            raise HTTPException(status_code=404, detail="Category not found")
        
        children = await self.repository.get_children(category_id)
        if children:
            raise HTTPException(
                status_code=400,
                detail="Cannot delete category with children"
            )
            
        return await self.repository.delete(category_id)

    async def get_category_tree(self, category_id: Optional[int] = None) -> List[Category]:
        """Get category tree starting from given category or root."""
        if category_id:
            return await self.repository.get_with_children(category_id)
        return await self.repository.get_root_categories()