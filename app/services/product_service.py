from typing import Any, Dict, List, Optional, Tuple
from fastapi import HTTPException
from app.repositories.product_repository import ProductRepository
from app.schemas.product import ProductCreate, ProductUpdate, ProductResponse
from app.models.model import Product
from sqlalchemy.orm import Session


class ProductService:
    def __init__(self, db: Session):
        self.repository = ProductRepository(db)

    async def create_product(self, product_data: ProductCreate) -> Product:
        """Create a new product."""
        return await self.repository.create(product_data.model_dump())

    async def get_products(
        self,
        page: int = 1,
        size: int = 100,
        filters: Optional[Dict[str, Any]] = None
    ) -> Tuple[List[Product], int]:
        """Get all products with filtering."""
        skip = (page - 1) * size
        limit = size
        products, total = await self.repository.get_all(
            filters=filters,
            skip=skip,
            limit=limit
        ), await self.repository.count(filters=filters)

        return products, total

    async def get_product(self, product_id: int) -> Optional[Product]:
        """Get product by ID."""
        product = await self.repository.get(product_id)
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        return product

    async def update_product(self, product_id: int, product_data: ProductUpdate) -> Product:
        """Update product."""
        product = await self.repository.get(product_id)
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        return await self.repository.update(product, product_data.model_dump())

    async def delete_product(self, product_id: int) -> bool:
        """Delete product."""
        product = await self.repository.get(product_id)
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        return await self.repository.delete(product)

    async def search_products(self, search_term: str) -> List[Product]:
        """Search products."""
        return await self.repository.search_products(search_term)

    async def get_product_reviews(self, product_id: int) -> List[ProductResponse]:
        """Get product reviews."""
        pass