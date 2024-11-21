from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from app.models.model import Category
from app.schemas.category import CategoryCreate, CategoryUpdate
from app.repositories.base_repository import BaseRepository

class CategoryRepository(BaseRepository[Category]):
    def __init__(self, db: Session):
        super().__init__(Category, db)

    async def get_by_slug(self, slug: str) -> Optional[Category]:
        """Get category by slug."""
        return self.db.query(self.model).filter(self.model.slug == slug).first()

    async def get_with_children(self, category_id: int) -> Optional[Category]:
        """Get category with all children."""
        return (
            self.db.query(self.model)
            .filter(self.model.id == category_id)
            .first()
        )

    async def get_root_categories(self) -> List[Category]:
        """Get all root categories (no parent)."""
        return (
            self.db.query(self.model)
            .filter(self.model.parent_id.is_(None))
            .all()
        )

    async def get_children(self, category_id: int) -> List[Category]:
        """Get all children of a category."""
        return (
            self.db.query(self.model)
            .filter(self.model.parent_id == category_id)
            .all()
        )

    async def move_to_category(self, category_id: int, new_parent_id: Optional[int]) -> bool:
        """Move category to a new parent."""
        try:
            category = await self.get(category_id)
            if category:
                category.parent_id = new_parent_id
                await self.commit()
                return True
            return False
        except Exception:
            await self.rollback()
            return False