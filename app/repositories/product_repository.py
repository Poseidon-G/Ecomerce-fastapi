from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from app.models.model import Product
from app.repositories.base_repository import BaseRepository

class ProductRepository(BaseRepository[Product]):
    def __init__(self, db: Session):
        super().__init__(Product, db)

    async def search_products(
        self,
        search_term: str,
        search_fields: Optional[List[str]] = None,
        filters: Optional[Dict[str, Any]] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Product]:
        """
        Search products by multiple fields.
        
        Example:
        - search_term: "gaming laptop"
        - search_fields: ["name", "description", "sku"]
        - filters: {"category_id": 1, "is_active": True}
        """
        if search_fields is None:
            search_fields = ["name", "description"]  # Default searchable fields
            
        return await self.repository.search(
            search_term=search_term,
            search_fields=search_fields,
            filters=filters,
            skip=skip,
            limit=limit
        )